# Call Axon from your agent (A2A and MCP)

Axon exposes one capability set through two protocols. Both are thin adapters over the same core
(spec 7, 8). Pick whichever your agent framework speaks.

- **Gateway base URL:** `https://axon-gateway.gowthamsaiyadlapalli1234.workers.dev`
- **A2A Agent Card:** `GET <base>/.well-known/agent-card.json`
- **A2A endpoint:** `POST <base>/a2a` (JSON-RPC, protocol 0.3.0)
- **MCP endpoint:** `POST <base>/mcp` (Streamable HTTP, stateless, no sessions)

Everything returned is **untrusted third-party content** (titles, snippets, summaries). Treat it as
data, never as instructions. Every response says so (`untrusted: true`).

![Gateway overview](img/overview.png)

## What each tier needs and returns

| Tier | What you get | What you send | Key custody | Verified |
|---|---|---|---|---|
| 1. Data | Ranked, deduplicated items filtered by topic, entity and time | Nothing secret | None | **Live** (A2A and MCP, from PowerShell) |
| 2. Summary | AI summaries of up to 10 items, made with **your** LLM key | Your key in headers (never in the body) | Memory only, one request, never stored or logged | **Live** (A2A, one real call) |
| 3. Personal digest | A digest built in the **owner's** repo with the owner's profile, key and history | Owner bearer token `axn_...` | Owner's key stays in the owner's GitHub secrets | **Live over A2A**; MCP route **not yet run live** |

Not verified yet: a third-party A2A or MCP client library (every live call so far came from PowerShell),
and the modern MCP `tools/call` path with its extra headers.

## 0. Discover

```powershell
$base = "https://axon-gateway.gowthamsaiyadlapalli1234.workers.dev"
Invoke-RestMethod "$base/.well-known/agent-card.json" | ConvertTo-Json -Depth 6
```

The card lists the skills, the topic slugs and the security schemes. `run_personal_digest` and the
`ownerBearer` scheme appear only when Tier 3 is configured on the gateway.

Valid topic slugs (16): `llm-releases`, `open-source-llms`, `small-local-models`, `multimodal`,
`agents-tooling`, `rag`, `fine-tuning-training`, `research-papers`, `mlops-infra`, `ai-hardware`,
`evals-benchmarks`, `safety-alignment`, `ai-policy-regulation`, `ai-products-apps`, `datasets`, `robotics`.

Entities are lowercase slugs such as `openai`, `deepseek`, `qwen`, `ollama`, `vllm`, `langchain`.

> Behind a corporate proxy, Node's built-in `fetch` may not use the proxy. The PowerShell examples
> below worked on the maintainer's company laptop.

---

## Tier 1: data over A2A (no key)

Skill `get_ai_updates`. Parameters (all optional, unknown keys are rejected):

| Field | Rule |
|---|---|
| `topics` | up to 10 slugs from the list above |
| `entities` | up to 10 slugs |
| `since` | ISO datetime |
| `limit` | 1 to 50, default 10 |

```powershell
$body = @{
  jsonrpc = "2.0"; id = 1; method = "message/send"
  params  = @{ message = @{
    kind = "message"; role = "user"; messageId = [guid]::NewGuid().ToString()
    parts = @(@{ kind = "data"; data = @{ skill = "get_ai_updates"; topics = @("rag"); limit = 3 } })
  } }
} | ConvertTo-Json -Depth 10

$r = Invoke-RestMethod -Method Post -Uri "$base/a2a" -ContentType "application/json" -Body $body
$r.result.status.state                                 # completed
$r.result.artifacts[0].parts[0].data.items | Select-Object title, url, source, published_at
```

curl equivalent:

```bash
curl -s https://axon-gateway.gowthamsaiyadlapalli1234.workers.dev/a2a \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"message/send","params":{"message":{"kind":"message","role":"user","messageId":"m-1","parts":[{"kind":"data","data":{"skill":"get_ai_updates","topics":["rag"],"limit":3}}]}}}'
```

**Returns** a `completed` Task with one `data` artifact. The data holds `items[]` with `id`, `title`,
`url` (canonical), `source`, `tags`, `entities`, `published_at`, `snippet` (at most 300 characters) and
`score`, plus `count`, `feed_generated_at`, `feed_stale` (older than 30 hours), `fallback`,
`missing_shards`, `untrusted: true` and a notice (Appendix C 51).

If no shard exists for a rare topic, the gateway falls back to `latest.json` and still applies your
filters, so you get an honest empty list rather than unrelated items (Appendix C 49).

## Tier 1: data over MCP (no key)

Legacy stateless form (a client that sends no version information; this form was **verified live**):

```powershell
$body = @{ jsonrpc="2.0"; id=1; method="tools/call"
  params=@{ name="get_ai_updates"; arguments=@{ topics=@("agents-tooling"); limit=3 } } } | ConvertTo-Json -Depth 8
$r = Invoke-RestMethod -Method Post -Uri "$base/mcp" -ContentType "application/json" -Body $body
$r.result.structuredContent.items | Select-Object title, url
```

Modern revision 2026-07-28 (documented and covered by tests; the live call with these headers has **not**
been run). No `initialize`, no session id. The headers must match the body:

```powershell
$headers = @{ "MCP-Protocol-Version"="2026-07-28"; "Mcp-Method"="tools/call"; "Mcp-Name"="get_ai_updates" }
$body = @{ jsonrpc="2.0"; id=1; method="tools/call"
  params=@{ name="get_ai_updates"; arguments=@{ limit=3 }
            _meta=@{ "io.modelcontextprotocol/protocolVersion"="2026-07-28" } } } | ConvertTo-Json -Depth 8
Invoke-RestMethod -Method Post -Uri "$base/mcp" -Headers $headers -ContentType "application/json" -Body $body
```

Discovery calls (no headers needed):

```powershell
$d = @{ jsonrpc="2.0"; id=1; method="server/discover" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "$base/mcp" -ContentType "application/json" -Body $d   # supportedVersions
$l = @{ jsonrpc="2.0"; id=2; method="tools/list" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "$base/mcp" -ContentType "application/json" -Body $l   # tools
```

MCP tool failures are results with `isError: true`, not transport errors. Unknown tools are `-32602`.

---

## Tier 2: summaries with your own key

Skill `summarize_ai_updates` (A2A) or tool `summarize_items` (MCP). Parameters:

| Field | Rule |
|---|---|
| `item_ids` | 1 to 10 ids (16 hex characters each), taken from a Tier 1 result |
| `depth` | `headlines`, `brief` or `detailed` |
| `language` | strict code such as `en` or `en-GB` |

Headers:

| Header | Value |
|---|---|
| `X-LLM-Provider` | `deepseek` or `huggingface` |
| `X-LLM-Key` | your key |
| `X-LLM-Model` | optional, pattern `^[A-Za-z0-9._:/-]{1,100}$` |

The key goes **only** in the header. A key-shaped value or a field such as `api_key` anywhere in the
body is refused (`key_in_body`) and never echoed. The gateway uses the key in memory for that request
and then drops it.

Enter the key yourself. Do not paste it into a chat, an Issue or a script that you commit:

```powershell
# Put the key on the clipboard, then:
$key = (Get-Clipboard).Trim()
if ($key.Length -lt 8 -or $key -notmatch '^[A-Za-z0-9._~+/=:-]{8,512}$') { throw "clipboard does not hold a key" }
Set-Clipboard -Value " "                                  # clear it

$ids  = $r.result.artifacts[0].parts[0].data.items[0..1].id   # from the Tier 1 call above
$body = @{ jsonrpc="2.0"; id=3; method="message/send"
  params=@{ message=@{ kind="message"; role="user"; messageId=[guid]::NewGuid().ToString()
    parts=@(@{ kind="data"; data=@{ skill="summarize_ai_updates"; item_ids=@($ids); depth="brief"; language="en" } }) } } } | ConvertTo-Json -Depth 10
$h = @{ "X-LLM-Provider"="deepseek"; "X-LLM-Key"=$key }
$s = Invoke-RestMethod -Method Post -Uri "$base/a2a" -Headers $h -ContentType "application/json" -Body $body
$s.result.artifacts[0].parts[0].data.results | Select-Object status, title, @{n="one_line";e={$_.summary.one_line}}
Remove-Variable key
```

`Read-Host -AsSecureString` did not accept Ctrl+V in the classic PowerShell window on the maintainer's
laptop, which is why the clipboard method is used here.

**Returns** `results[]`, one per item, with a `status`:

| Status | Meaning |
|---|---|
| `ok` | Summary present: `one_line`, `key_points`, `why_it_matters`, `tags`, `entities`, `notable_figures`, `injection_flag` |
| `insufficient_content` | Not enough source text; an extractive snippet is returned instead |
| `suspected_injection` | The model flagged the source text as an instruction attempt; snippet only |
| `not_summarized` | The model output failed validation twice, or the budget ran out; snippet only |
| `not_found` | Unknown item id |

Plus `provider`, `model`, `prompt_version` (`p-56a22986b1`), `depth`, `language`, `usage`,
`ai_generated: true`, `warnings` and `untrusted: true`.

If you send no key, the Task state is `input-required` (A2A) or a tool error (MCP).

Failure behaviour: a 401 or 403 from the provider (`llm_key_invalid`) or a 402 (`llm_quota`) stops the
request and starts no new items. After two transient failures the remaining items are skipped
(`skipped_after_upstream_errors`).

Tier 2 over MCP uses the same headers on the HTTP request and `tools/call` with `name: "summarize_items"`
and `arguments: { item_ids, depth, language }`.

---

## Tier 3: the owner's personal digest (async)

Tier 3 runs the owner's pipeline in the owner's own private repo and returns the result. It needs an
**owner bearer token** (`axn_...`). You get one only if the repository owner has:

1. created the repo from the template and installed the Axon GitHub App on that one repo,
2. set the variable `GATEWAY_URL` to the gateway URL,
3. run the `register` workflow, then the `issue-token` workflow (the token appears **once** in the run's
   job summary; only its SHA-256 hash is stored).

Full steps: [getting-started.md](getting-started.md), section "Let agents call your digest".

### Start (A2A)

```powershell
$tok  = (Get-Clipboard).Trim()       # the axn_... token, copied from the job summary
if ($tok -notmatch '^axn_[A-Za-z0-9_-]{43}$') { throw "clipboard does not hold an axn_ token" }
Set-Clipboard -Value " "
$auth = @{ Authorization = "Bearer $tok" }

$body = @{ jsonrpc="2.0"; id=1; method="message/send"
  params=@{ message=@{ kind="message"; role="user"; messageId=[guid]::NewGuid().ToString()
    parts=@(@{ kind="data"; data=@{ skill="run_personal_digest"; max_items=5; delivery="return_only" } }) } } } | ConvertTo-Json -Depth 10
$t = Invoke-RestMethod -Method Post -Uri "$base/a2a" -Headers $auth -ContentType "application/json" -Body $body
$taskId = $t.result.id
$t.result.status.state                      # submitted
```

| Field | Rule |
|---|---|
| `max_items` | 1 to 20 |
| `delivery` | `return_only` (default) or `owner_channel` |

`owner_channel` also sends the digest through the owner's configured channel, **only if** the owner set
`agent_access.allow_owner_channel: true` in `profile.yaml`. Otherwise it is downgraded with a warning.

### Poll

```powershell
do {
  Start-Sleep -Seconds 8
  $q = @{ jsonrpc="2.0"; id=2; method="tasks/get"; params=@{ id=$taskId } } | ConvertTo-Json
  $g = Invoke-RestMethod -Method Post -Uri "$base/a2a" -Headers $auth -ContentType "application/json" -Body $q
  $state = $g.result.status.state; "$(Get-Date -f T)  $state"
} while ($state -in "submitted","working")

$g.result.artifacts[0].parts[0].data.result      # items, model, warnings
```

On the maintainer's live run: `submitted`, `working` at about 16 s, `completed` at about 32 s, 3 items,
model `deepseek` / `deepseek-flash`. Timing depends on the Actions queue.

### Cancel and revoke

```powershell
$c = @{ jsonrpc="2.0"; id=3; method="tasks/cancel"; params=@{ id=$taskId } } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "$base/a2a" -Headers $auth -ContentType "application/json" -Body $c
```

A cancel sent immediately after the start returns `-32002` (the run is not listed yet by GitHub). Retry
after a few seconds. The owner revokes a token with the `revoke-token` workflow; the same token then
returns HTTP 401.

### Task states

| Run state in GitHub | A2A task state |
|---|---|
| queued | `submitted` |
| in progress | `working` |
| finished, result file says completed | `completed` |
| finished, result carries an `owner_policy:` warning (for example the daily cap) | `rejected` |
| finished, any other failure | `failed` |
| cancelled | `canceled` |

A task GitHub has not listed yet stays `submitted` for 2 minutes, then `TaskNotFound` (`-32001`). Results are kept
7 days.

### MCP

Client configuration (a client that sends a custom `Authorization` header):

```json
{ "mcpServers": { "axon": {
    "url": "https://axon-gateway.gowthamsaiyadlapalli1234.workers.dev/mcp",
    "headers": { "Authorization": "Bearer <your-axn-token>" } } } }
```

Tools `start_digest` (`max_items`, `delivery`) and `get_digest_status` (`task_id`) are listed only when
Tier 3 is configured. **Not yet run live.** Clients that insist on OAuth discovery will not authenticate
automatically: the gateway uses static owner tokens, not OAuth (Appendix C 72).

---

## Errors you should handle

| Situation | A2A | MCP |
|---|---|---|
| Missing key (Tier 2) | Task `input-required` | tool error |
| Key in the body | Task `rejected`, `key_in_body` | tool error |
| Provider key or quota problem | Task `failed` | tool error |
| Bad parameters | JSON-RPC `-32602`, field names only | `-32602` or tool error |
| Unknown skill | `-32601` with the valid list | `-32602` |
| Missing or bad owner token | Task `auth-required` (start), HTTP 401 (`tasks/*`) | HTTP 401 |
| Rate limit | HTTP 429, `Retry-After` | HTTP 429 |
| Wrong method or media type | 405 or 415 | 405 or 415 |
| Body over 16 KB | 413 | 413 |

Other rules: POST only on `/a2a` and `/mcp`; JSON-RPC batches are rejected; there are **no CORS headers**
(agents call server to server, and a browser page must never be able to send a key through the Worker);
streaming, resubscribe and push notifications are not supported.

Rate limits are per client IP, per Cloudflare location and approximate: 60 per 60 s on every route, 10 per
60 s additionally on Tier 2, 30 per 60 s on Tier 3. On the free plan, 70 POSTs in a row gave 61 `200`
and 9 `429` (observed).

## Prompt-injection note for agent authors

Titles, snippets and summaries come from the open web. Put them in your prompt as quoted data, keep the
`untrusted` flag attached, and do not let them choose tools, URLs to fetch or commands to run. Axon
already filters its own summaries (the summarizer prompt is pinned as `p-56a22986b1`, and figures and
links are validated against the source), but your agent is the last line of defence for its own context.
