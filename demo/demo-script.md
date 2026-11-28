# Axon demo script (30 minutes, screen-share)

Format: Teams call, screen-share, no slide deck. The diagrams in `docs/img/` are the visuals.
Budget: about 24 minutes of talk and demo, about 6 minutes of questions.

Words to use consistently: **verified live** = I saw it on real services; **tested with mocks** = covered
by tests with fakes; **not run** = not done yet. Do not blur these on the call.

## Run of show

| Min | Block | Screen | Goal |
|---|---|---|---|
| 0 to 3 | 1. The problem and what Axon does | `ARCHITECTURE.md` hub page, top | Everyone knows what it is in one sentence |
| 3 to 5 | 2. The name | Same page | A memorable hook |
| 5 to 10 | 3. Architecture | `overview.png`, then `state-model.png` | Three planes, three tiers, where keys live |
| 10 to 13 | 4. Why these sources | `axon-feed/ARCHITECTURE.md` sources table | Trust and restraint |
| 13 to 19 | 5. Demo A: my personal digest | Telegram or email, GitHub Actions, `profile.yaml` | See value, then see how it was made |
| 19 to 24 | 6. Demo B: an agent calls Axon | PowerShell | A2A and MCP in practice |
| 24 to 27 | 7. Security and quality | Hub `ARCHITECTURE.md` security list, test counts | Why it is safe to run |
| 27 to 30 | 8. How to start, roadmap, questions | `docs/getting-started.md` | A clear next step |

If you run late, cut in this order: Demo B Tier 2, the second half of block 7, the `state-model` image.
Never cut the "verified live vs not" statement.

---

## Before the call (do 30 minutes earlier)

**Tabs, in this order**
1. Hub `ARCHITECTURE.md` on GitHub (rendered, images visible).
2. `axon-feed/ARCHITECTURE.md`.
3. Your private `axon-digest` repo > Actions > the last green `digest` run.
4. Telegram (or your inbox) showing the latest digest. Blur or close other chats.
5. `profile.yaml` in `axon-digest` (check it holds no secrets).
6. PowerShell window, font size large, in a scratch folder.
7. `docs/getting-started.md`.

**Environment checks**
- Close notifications, other tabs, the password manager and Slack. A secret on screen cannot be taken back.
- `Invoke-RestMethod "$base/healthz"` returns `ok`.
- The last scheduled `digest` run is green, and the digest message is fresh.
- You have a **fresh Tier 3 token** ready to copy (issue one 10 minutes before; the token shows once in the job
  summary; delete that run afterwards). Keep the token **off screen**.
- The company proxy: Node `fetch` may fail on `workers.dev` here; PowerShell worked. Use PowerShell only.

**Pre-load PowerShell** (paste once before sharing the screen, then `cls`):

```powershell
$base = "https://axon-gateway.gowthamsaiyadlapalli1234.workers.dev"
function Send-A2A($payload, $headers = @{}) {
  Invoke-RestMethod -Method Post -Uri "$base/a2a" -Headers $headers -ContentType "application/json" -Body ($payload | ConvertTo-Json -Depth 10)
}
function Msg($data) {
  @{ jsonrpc="2.0"; id=1; method="message/send"
     params=@{ message=@{ kind="message"; role="user"; messageId=[guid]::NewGuid().ToString()
       parts=@(@{ kind="data"; data=$data }) } } }
}
```

**Backups (screenshots in a folder)**: the digest message, the green Actions run, the Agent Card output, a
Tier 1 result, a Tier 3 `completed` result. Name them `fallback-1.png` and so on.

---

## Block 1 (0 to 3): the problem and what Axon does

**Say**
- "The AI field produces hundreds of papers, releases and announcements a day. Reading all of it is
  impossible; reading none of it means missing the thing that matters for your work."
- "Axon is a small system that watches a fixed set of trusted sources, throws away duplicates, ranks what is
  left against **your** interests, summarises the top few with **your own** LLM key and sends you a short
  digest where you already read: email, Telegram or Slack."
- "The same capability is available to other agents over two standard protocols, A2A and MCP. So your
  agent can ask Axon what happened in AI this week."
- "It runs entirely on free platforms. The only cost is your own LLM usage: two real digests cost under
  one US cent. Nobody, including me, ever holds your keys."

**Show**: the intro of the hub `ARCHITECTURE.md`.

**Time saved: what you can honestly say.** Do not quote hours you did not measure. Use observed numbers and your own:
- Observed in my run: **652 candidate items were reduced to a 10-item digest**, summarised in 17 model calls.
- The shared feed on 2026-11-26 held 1270 items in its window (150 in `latest`).
- Then add one sentence from your own life, for example "I used to check these sources by hand; now I read
  one message in about N minutes." Fill N yourself after timing it this week. If you have not timed it,
  say "I have not measured it rigorously; the reduction from hundreds of candidates to ten is the part I can show."

**Keeps you updated in a busy world**: it arrives on schedule (default 07:30 IST), it never repeats an item
(delivered ids are remembered), and it adapts through optional thumbs feedback.

---

## Block 2 (3 to 5): the name

> Confirm this wording is yours before the call; the spec does not record a reason for the name.

**Suggested line**: "An axon is the part of a neuron that carries a signal from the cell body to other
cells. Axon does the same for AI news: it takes signal from many sources and relays it to you and to your
agents, and, like a neuron, it only passes on what crosses a threshold." The project's working description is
"Signal Relay", which fits this.

If someone asks "is that why?", answer plainly: "That is the idea I chose to describe it."

---

## Block 3 (5 to 10): architecture

**Show** `overview.png`, then zoom into each plane (use the crops you prepared; or open the full-size link).

**Say (about 90 seconds per plane)**
1. **Plane 1, the shared feed.** "Every three hours a GitHub Action collects nine source feeds, removes
   duplicates, tags and scores them, and publishes static JSON on GitHub Pages. **No LLM, no keys, no user
   data.** That keeps the shared part free and safe."
2. **Plane 2, my pipeline.** "I made a private repo from a template. Another Action reads the shared feed, ranks
   it against my profile, summarises the top items with my key, checks each summary, and sends it. It
   remembers what it already sent on a `state` branch."
3. **Plane 3, the gateway.** "A Cloudflare Worker exposes the same things to other agents. Three tiers:
   data with no key; summaries using the caller's own key, in memory for one request; and a personal digest
   that starts **my** pipeline through a GitHub App, only if I issued a token."

**Show** `state-model.png` for 30 seconds: "Here is where each thing lives. The most important row: the
caller's key in Tier 2 lives nowhere. It exists in memory for one request."

**Key sentence**: "Mode A only: one private repo per user, no operator-held keys. That is a decision, not an accident."

**Honest answer ready**: if asked whether this is an "agent" or a cron job, use the answer in `qa-prep.md`.
Short version: "The digest itself is a scheduled workflow, and I say so. What makes it agent-facing is the A2A
and MCP surface, so other agents can discover and call it."

---

## Block 4 (10 to 13): why these sources

**Show** the sources table in `axon-feed/ARCHITECTURE.md`.

**Say**
- "I picked sources by two tests: is there a stable, **verified** feed, and does the source's own
  authority justify trusting its claims. Each gets an authority score from 0 to 1 which is one input to ranking."
- "Primary sources, like the OpenAI and DeepMind blogs, score highest. Hugging Face and GitHub releases are
  platform sources. arXiv and Hacker News are aggregates with the lowest prior, because volume is high and
  claims are unvetted."
- "arXiv gives research; Hugging Face gives the open-model world; GitHub releases cover the tools people
  actually run: ollama, llama.cpp, vllm, langchain, llama_index and transformers; Hacker News gives early signal."
- "What is **not** here matters. Reddit is excluded because its robots.txt disallows our crawler. Anthropic,
  Meta, Mistral, Qwen and DeepSeek are on a research list; I do not add a feed URL until I have verified
  one. I would rather have nine sources I trust than thirty I do not."
- "A new source starts at 0.50 and is capped at 0.60 until it has 30 days of health data."

**If asked "why is X missing?"**: "It is on the list, and the rule is no guessed feed URLs."

---

## Block 5 (13 to 19): demo A, my personal digest

**1. The result first (1 min).** Show the Telegram or email digest. Point at: item titles with links, a short
"why it matters", and the footer naming the model that wrote the summary. "Every item links to its source
and says which model wrote it. Summaries are validated: only the source URL is allowed, and figures must
appear in the source."

**2. How it was made (2 min).** Switch to `axon-digest` > Actions > the last `digest` run. Open it. Point at
the steps (feedback votes, run digest, commit state). Say: "Secrets print as `***` in the log. I searched the
logs for key fragments and found none."

**3. What I control (1 min).** Show `profile.yaml`: topics, entities, keywords to include and exclude,
channel, time, depth, summariser. "This is the only file I normally edit. No keys in it."

**4. Optional live moment (2 min).** Run the workflow by hand: Actions > digest > Run workflow. Do this only
if it has completed in under 2 minutes the last three times. Otherwise say: "A run takes about a minute or two;
here is one I ran earlier" and stay on the finished run. A scheduled digest is the real product, so a manual run is theatre.

**Fallback**: if GitHub is slow or the digest message is missing, show `fallback-1.png` and `fallback-2.png`
and say "this is the run from this morning".

**Verified live**: Telegram, Slack, email, the onboarding form, feedback links, the Atom channel.

---

## Block 6 (19 to 24): demo B, an agent calls Axon

**Setup line**: "Now the other direction. Any agent that speaks A2A or MCP can use Axon. I'll call it
from plain PowerShell, which is what any agent framework does under the hood."

**1. Discover (30 s)**
```powershell
$card = Invoke-RestMethod "$base/.well-known/agent-card.json"
$card.name; $card.protocolVersion; $card.skills.id
```
"The Agent Card says what it can do: two skills for everyone, and a third for token holders."

**2. Tier 1, no key (1 min)**
```powershell
$r = Send-A2A (Msg @{ skill="get_ai_updates"; topics=@("rag"); limit=3 })
$r.result.status.state
$r.result.artifacts[0].parts[0].data.items | Select-Object title, source, url
```
"No key, no account. Ranked, deduplicated, with an `untrusted: true` flag, because the content is third-party."

**3. Tier 2 (skip if short on time)**: only if you are comfortable loading a key from the clipboard without
showing it. Otherwise describe: "Tier 2 takes the caller's key in a header, uses it in memory for that one
request and returns summaries. I tested it live once with a throwaway DeepSeek key and deleted it."

**4. Tier 3, the personal digest (2 min)**
```powershell
$tok = (Get-Clipboard).Trim()
if ($tok -notmatch '^axn_[A-Za-z0-9_-]{43}$') { throw "no token on the clipboard" }
Set-Clipboard -Value " "
$auth = @{ Authorization = "Bearer $tok" }
$t = Send-A2A (Msg @{ skill="run_personal_digest"; max_items=3; delivery="return_only" }) $auth
$id = $t.result.id; $t.result.status.state          # submitted
```
Poll while you talk:
```powershell
1..10 | % { Start-Sleep 6
  $g = Send-A2A @{ jsonrpc="2.0"; id=2; method="tasks/get"; params=@{ id=$id } } $auth
  "$(Get-Date -f T) $($g.result.status.state)"; if ($g.result.status.state -notin "submitted","working") { break } }
$g.result.artifacts[0].parts[0].data.result | ConvertTo-Json -Depth 6 | Select-Object -First 40
```
Talk during the wait: "This started a real GitHub Actions run in **my** private repo through a GitHub App
with only the permissions it needs. The gateway keeps no database; it reads the run state from GitHub. My key
never leaves my repo's secrets. On my live test it moved to `working` at about 16 seconds and `completed` at
about 32."

**5. Revoke (30 s, optional)**: "I can revoke the token with a workflow, and the same token then gets 401."
Do not run it live unless you have a spare token.

**Honest status line**: "Tier 3 over A2A is verified live. Tier 3 over MCP has tests but I have not run it
live yet, and I have not yet tested a third-party client library; everything so far came from PowerShell."

**Fallback**: if Actions queues slowly, show `fallback-5.png` (completed result) and say the timing from the record.

Pointer for the audience: `docs/call-the-agent.md` has copy-paste examples for all three tiers over A2A and MCP.

---

## Block 7 (24 to 27): security and quality

**Say, in this order (three points, not twelve)**
1. **Untrusted by default.** "Everything scraped from the web and every inbound agent message is data.
   It never becomes an instruction, a URL to fetch or a command. We keep a corpus of hostile text and SSRF
   cases and run it in CI in both code repos."
2. **Keys.** "Keys are header-only and memory-only on the gateway, and stay in GitHub secrets for the
   pipeline. A key in a request body is refused. Observability is off on the Worker."
3. **Proven rules.** "For every security rule I wrote a test **and** a mutation: I break the rule on
   purpose and check that a test fails. The template has 95 of those; 94 were observed on my laptop."

**Numbers you can quote**: template 1355 passed, 45 skipped; gateway 992 passed (observed). Feed count is
reported green, exact count not recorded.

**What broke in real life, which is the credible bit**: a mocked test hid that Cloudflare's runtime rejects
`redirect: "error"`, which would have broken every real Tier 2 call; a template null value that the gateway
rejected on the first live Tier 3 run; a secret-shaped test string flagged by GitHub secret scanning. All
fixed, all with tests. "That is why I ran everything live before showing you."

---

## Block 8 (27 to 30): how to start, roadmap, questions

**Say**
- "To start: create a private repo from the template, run the onboarding form or `digest.cli init`, add
  your key and a channel as secrets, set the feed variable, and run `digest` once. About 20 to 30 minutes.
  `docs/getting-started.md` has every step."
- "Not built on purpose: a public RSS feed repo (deferred), natural-language Tier 3, A2A v1.0, MCP OAuth.
  Not yet verified: Tier 3 over MCP, a third-party client, and some measurements."
- "If you try it, tell me what breaks."

**Show** `docs/getting-started.md`. Then open the floor.

---

## If things go wrong

| Problem | What to do |
|---|---|
| Image does not load | Open the PNG directly from `docs/img/` |
| `Invoke-RestMethod` times out | Say "the corporate proxy"; show the fallback screenshot; do not retry more than once |
| 429 from the gateway | "That is the rate limiter working: 60 per minute per location"; wait 60 s or move on |
| Tier 3 returns `auth-required` | Token expired or revoked; show the fallback result and explain |
| Tier 3 stays `submitted` | GitHub's run list can lag a minute or two; say so, show the fallback |
| Digest is not in Telegram | Show the Actions run instead and the screenshot |
| A secret appears on screen | Say so, stop sharing, rotate it after the call. Do not carry on |

## After the call

- Delete the Tier 3 token run's job summary if you did not already, and revoke the demo token.
- Clear the clipboard.
- Note the questions you could not answer and add them to `qa-prep.md`.
