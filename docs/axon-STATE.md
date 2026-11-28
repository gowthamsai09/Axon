# Axon: project state (handoff file)

Updated: 2026-11-28. Phase 6 is built and its live walkthrough (Task A of `axon-END-OF-PHASE6-BRIEF.md`)
is largely done: Telegram, Slack, email, the onboarding form, feedback links, the Atom channel, keepalive and
the `state` branch are **verified live**; **the gateway is deployed to Cloudflare Workers** with Tier 1, 2 and
**Tier 3** verified live (sections 3b and 3c).
Spec: `axon-architecture.md` **v1.7** plus Appendix C items **106 to 127** (draft items, to be folded in
when the spec becomes v1.8; the 2026-11-27 and 11-28 items are in `phase6-live-appendix-c-part2.md` and
`phase6-live-appendix-c-part3.md`). Items 1 to 105 are in the spec. Rules for working: `axon-GUIDELINES.md`. Owner: gowthamsai09.

Words used in this file: **verified live** = seen on real services by the maintainer; **mocked only** =
tests with fakes; **not run** = nothing executed; **derived** = computed, not observed.

## 1. Where things stand

| Item | State |
|---|---|
| Phases 0 to 6 (code) | DONE. Phase 6 built 2026-11-26 in stages 1, 23, 45 |
| Code repos on GitHub | All four pushed, public, CI green: hub (`Axon`), `axon-feed`, `axon-template`, `axon-gateway`. Private: `axon-digest` (user repo made from the template) |
| Licence | Apache-2.0, "Copyright 2026 gowthamsai09", all four repos (item 106) |
| Feed (plane 1) | **Verified live**: `collect.yml` runs, feed served by Pages |
| User pipeline (plane 2) | **Verified live** in `axon-digest`: Telegram, Slack, email, onboarding form |
| Gateway (plane 3) | **Deployed 2026-11-27**: `https://axon-gateway.gowthamsaiyadlapalli1234.workers.dev`. Tier 1 and 2 **verified live**; **Tier 3 verified live over A2A on 2026-11-28** (GitHub App `5953758`, key stored as a Cloudflare Secret, register, token, start, poll, cancel, revoke). Tier 3 over MCP not yet run |
| Public feed repo (Task B) | **Deferred by decision 2026-11-27** (item 114); revisit if an RSS reader feed is wanted |
| Next work | A demo of the whole project; then the housekeeping in section 7 (Tier 3 over MCP, measurements, docs fixes, token narrowing, Dependabot) |

Folder layout on the laptop (siblings): `Axon/` (hub), `axon-feed/`, `axon-template/`, `axon-gateway/`,
`feed-out/` (generated, currently `<path-to>\Axon\Axon\feed-out`). Live repos: `gowthamsai09/Axon` (the hub;
GitHub ignores case), `gowthamsai09/axon-feed`, `gowthamsai09/axon-template`, `gowthamsai09/axon-gateway`,
private `gowthamsai09/axon-digest`.
User environment: company Windows laptop, PowerShell, conda env `axon` (Python 3.12), Node 22, behind a
corporate proxy with DNS restrictions (section 8). Commits use the GitHub noreply address.

## 2. Phase status (spec section 12)

| Phase | Status |
|---|---|
| 0 Foundations | DONE |
| 1 Shared feed | DONE. Live data 2026-10-20 (665 items). **First Actions run verified live 2026-11-26** (item 112) |
| 2 User pipeline MVP | DONE 2026-10-23. Real email **verified live 2026-11-26** |
| 3 Gateway Tier 1 and 2 | DONE 2026-10-28 (mocks); **deployed and verified live 2026-11-27** (section 3b), including one real Tier 2 call |
| 4 Tier 3 | DONE 2026-10-29, user-confirmed green 2026-10-31. **Verified live over A2A 2026-11-28** (section 3c); MCP route and measurements still open |
| 5 Hardening | DONE 2026-11-22. Mostly mocked only (section 5) |
| 6 Polish | BUILT 2026-11-26; stage 45 user-confirmed green 2026-11-25. Live walkthrough: see section 3 |

## 3. Live walkthrough record (2026-11-26)

**Verified live**
- Hub, feed and template CI green on GitHub; Dependabot opened PRs (item 108).
- `axon-feed`: `collect.yml` ran; Pages serves the feed under `/feed/`, so `FEED_BASE` is
  `https://gowthamsai09.github.io/axon-feed/feed` and `meta.json` is at `.../axon-feed/feed/meta.json`
  (`.../axon-feed/meta.json` and the site root return 404, as expected). `meta.json` at 2026-11-26 16:45
  UTC: 1270 items, 150 in `latest`, 16 tags, 20 entities, all 9 sources `ok`, none stale; only expected
  extract warnings (403 and 429 from other sites, the 30-page-fetch cap).
- `axon-digest` (private, from the template): secrets `LLM_API_KEY`, `TELEGRAM_BOT_TOKEN`,
  `TELEGRAM_CHAT_ID`, `SLACK_WEBHOOK_URL`, `SMTP_*`, `MAIL_TO`; variable `FEED_BASE` set by the
  maintainer, never seen by the assistant.
- Delivery by Actions: Telegram (2 messages of 5 items, readable links, footer as designed), Slack
  (10 items), email (Gmail SMTP, port 465). The maintainer approved each.
- DeepSeek `deepseek-flash` summaries: 17 LLM calls for 10 items (the validator retries or repairs
  over-length one-liners and key points); cost under 0.01 USD for two runs.
- `state` branch: written by the first run, read back by the next. The first run showed a soft error
  on the `state` checkout (the branch did not exist; `continue-on-error`); gone from the second run.
- `delivered.json` (on `state`): a map from item id to `{"at": ISO timestamp, "tags": [tag slugs]}`.
  Four runs left 40 distinct ids, 10 per run (timestamps 13:23, 13:35, 13:43, 13:59 UTC), so **no item
  was delivered twice**. It holds no address, key or chat id. A `summaries/` file holds item fields
  such as `title` and `why_it_matters`. `last_run.json` holds counts and usage only.
- Secret hygiene: in a green run the secrets print as `***`; log searches for key fragments, the
  Telegram token, the chat id and `hooks.slack.com` returned nothing; `state/` and `last_run.json` clean.
- Onboarding form (Issue #3): body shape `### label`, `_No response_`, `- [x]`/`- [ ]` confirmed;
  an unset optional dropdown arrives as `None` (fixed, item 111); bot reply, `profile.yaml` commit
  (cron `"0 2 * * *"`, unchanged) and Issue close all worked. An Issue edit that changes nothing fires
  no `edited` event.
- Template CI in a user repo is green after the baseline-profile fix (item 110).

**Not run**
- Breaking `SMTP_PASS` to see the failure notice (the old value cannot be read back, so a mistake would
  force a new app password). The failure-notice path stays mocked only.

**Verified live later:** feedback links, the Atom channel, keepalive and Tier 3 (section 3c).

**Mocked only so far**
- Embeddings, trends, stale-source
  Issues, `evals live`, the second email-failure path.

**Findings fixed during the walkthrough** (all have tests): pydantic mypy plugin in the hub (108); token-
shaped fixture flagged by secret scanning (109); tests read the editable profile (110); `None` dropdown
value (111). **Limitation:** a repo made from the template is a snapshot, so later template fixes do not
reach existing user repos; the owner copies changed files by hand (item 110).

### 3b. Gateway deploy and live record (2026-11-27)

**Deploy path.** Pushed to `axon-gateway` (CI green: lint, typecheck, 888 tests, `prompt:check`, hub contract
tests, `wrangler deploy --dry-run`). The `deploy` workflow failed on its first runs by design (the guard
refuses placeholder config). The maintainer then created, by hand and never in chat: a Cloudflare account
(Free plan; the account `workers.dev` subdomain is `gowthamsaiyadlapalli1234`, auto-assigned and accepted as
public), the KV namespace `axon-gateway-tokens` (id in `wrangler.toml`, public), an account API token from the
"Edit Cloudflare Workers" template (no expiry, maintainer's choice; rotation is manual) and the GitHub
environment `production` (required reviewer: the maintainer; secrets `CLOUDFLARE_API_TOKEN`,
`CLOUDFLARE_ACCOUNT_ID`). `PUBLIC_URL` and the KV id were set in `wrangler.toml`; one existing test had to be
changed deliberately (item 116). Deploy #4 waited for approval, then succeeded.

**Verified live**
- Deploy: upload 1166.27 KiB (215.79 KiB gzip), Worker startup 23 ms, version `dd9b9a55-7dba-47dc-906e-35f0f99596dd`,
  bindings accepted by Cloudflare including the three `[[ratelimits]]` (60, 10 and 30 per 60 s).
- `/healthz` `ok`; Agent Card: `url` equals `PUBLIC_URL/a2a`, protocol 0.3.0, skills `get_ai_updates` and
  `summarize_ai_updates`, scheme `callerLlmKey`, no Tier 3.
- A2A Tier 1 (`topics: ["rag"]`, limit 3): `completed`, 3 items, `feed_stale` false, `fallback` null,
  `missing_shards` empty.
- MCP: `server/discover` lists 2026-07-28 and 2025-11-25; legacy `tools/list` returns `get_ai_updates` and
  `summarize_items`; `tools/call get_ai_updates` returns 3 items, not stale, no fallback.
- Hygiene: `GET /a2a` 405, `text/plain` 415, `GET /` 404; Tier 2 without a key `input-required`.
- Rate limit: 70 POSTs in a row gave 61 `200` and 9 `429` (the limit is per location and approximate).
- **Tier 2 with a real key**: two feed items summarized by `deepseek` / `deepseek-flash`, state `completed`,
  both items `ok`; the key did not come back in the response. The test key was deleted afterwards.
- Cloudflare Metrics (last 24 h, after about 83 requests): 83 invocations, 133 subrequests, 0 errors,
  CPU time 2 ms (panel) and median CPU 4.62 ms (active deployment), wall time 7 ms, request duration 7 ms.
  Free plan CPU limit is 10 ms; only medians were read, not p99.

**Not verified / open**
- No real MCP or A2A client yet (everything came from PowerShell).
- `Retry-After` on a real 429 (the check printed nothing because the window had reset).
- `wrangler tail` not run (Cloudflare edge log checked, section 3c).
- CPU p99 and Tier 2 CPU and subrequests per request (Tier 3: section 3c).
- The company proxy may inspect HTTPS: the Tier 2 test key crossed it. It was a dedicated key and is deleted.

### 3c. Digest extras and Tier 3 live record (2026-11-27 and 2026-11-28)

**Verified live (observed)**
- **Feedback links:** the thumbs links in the email opened prefilled Issues; the "Apply feedback votes" step
  read, counted and closed 2 Issues: `feedback: applied 2 vote(s) from 2 issue(s); 0 ignored, 0 for unknown
  items, 2 closed`. `weights.json` on `state` then held `ai-hardware +0.1`, `small-local-models +0.1`,
  `research-papers -0.1`. The first empty run after enabling feedback stamps the 6-day wait (`MIN_INTERVAL_DAYS`),
  so a vote the same day was skipped until `weights.json` was deleted on `state` (item 122). Not verified: a
  stranger's vote being ignored; the effect of the weights on ranking.
- **Atom (`rss`) channel:** two runs wrote `rss/feed.xml` and `rss/entries.json` on `state`; the second file
  held 2 entries, newest first, 20 distinct item links, well-formed Atom (PowerShell and a second parser). Text is
  plain, the `self` link is the raw URL (needs a sign-in for a private repo). Item 6 of one digest was the
  designed extractive fallback.
- **`keepalive.yml`:** one manual run, green; `digest.yml` still shown as enabled.
- **Cloudflare Logs (HTTP requests):** stores edge metadata only (ray, time, method, path, host, IP, country,
  status, cache); the expanded row had no request headers or body.
- **Tier 3 setup:** GitHub App created on the personal account (webhook "Active" unticked, Actions read and
  write, Contents read-only, Metadata read-only), installed on `axon-digest` only. The private key was first
  saved as a Cloudflare variable of type Text (visible), removed by the next deploy, the key rotated, and stored
  again as type **Secret** (item 123). With the real `GITHUB_APP_ID` in `wrangler.toml` the Agent Card lists
  `run_personal_digest` and `ownerBearer`.
- **register:** green with GitHub's real OIDC token. **issue-token:** the token showed as `***` in the job summary;
  the workflow no longer masks it (item 123), then the token was readable once and the run was deleted.
- **A2A flow:** the first run failed because the gateway rejected the `null` the template writes for the unused
  `summary` / `fallback_snippet` (item 124). After the fix: `submitted`, `working` at 16 s, `completed` at 32 s,
  3 items, `deepseek/deepseek-flash`, 1 warning (`summary rejected (schema violation in: notable_figures)`),
  `untrusted: True`. A cancel sent at once returned -32002 (the run is not listed yet); after 12 s it returned
  `canceled`. After the `revoke-token` workflow the same token gave `401` (delay not measured).

**Not verified / open**
- Tier 3 over MCP (`start_digest`, `get_digest_status`); a real MCP or A2A client; subrequests, CPU and KV usage
  per Tier 3 request; the delay until a revoked token stops working.
- `scripts/integration-real.js` fails behind the company proxy (`ENOTFOUND`: Node 22.14 `fetch` does not use the
  proxy); the same steps were run from PowerShell (item 127).

## 4. Test status (observed by the user on Windows unless marked)

| Repo | Tests | Notes |
|---|---|---|
| axon-template | Last observed 2026-11-25 after stage 45 (with `HUB_DIR` set): **1397 collected, 1352 passed, 45 skipped**. After the live fixes, with the real hub path (observed 2026-11-27): **1400 collected, 1355 passed, 45 skipped** (44 need POSIX bash, 1 empty parameter set) | Test files by stage: stage 1 `test_chat_common`, `test_telegram`, `test_slack`, `test_chat_delivery`; stage 23 `test_rss`, `test_embeddings`, `test_trends`, `test_weights`, `test_feedback`, `test_cli_phase6`, `test_pipeline_phase6`, `test_stage23_misc`; stage 45 `test_onboarding`, `test_onboard_cli`, `test_onboard_workflow`, `test_text_corpus` (139 tests when the hub copy is found through `HUB_DIR` or `..\Axon`, else 6 skips) |
| axon-feed | user reported green; exact count not reported (about 446, derived) | Record the real number at the next run |
| Axon hub | 30 passed + 1 skipped (observed after stage 45); CI green on GitHub | corpus, prompt id, schema, hostile-text tests |
| axon-gateway | **992 passed** (observed 2026-11-28 after the null fix; 888 observed before it; my derived 892 was 100 low and the reason is not established, probably suites that read the hub) | typecheck, lint, tests, `prompt:check` (`p-56a22986b1`) green; `test/deploy-config.test.ts` now asserts that the repo's own `wrangler.toml` passes the guard |

Checks everywhere: `ruff format .; ruff check .; mypy .; pytest` (Python); `npm run typecheck; npm run
lint; npm test; npm run prompt:check` (gateway).

Template change 2026-11-28 (`issue-token.yml` no longer masks the token, item 123): counts unchanged (derived); in my
sandbox `tests/test_phase4.py` gave 74 passed and the new mutation `wf-issue-token-echo` was killed. The project
bundle holds 94 mutations before that change (the 95th named below is not in it), 95 after.

Mutation sanity: template `scripts/mutation_sanity.py` has **95 mutations** (27 before Phase 6, 49 in
stages 1 and 23, 18 in stage 45, 1 new: `onb-none-choice`). 94 of 94 observed on the laptop on
2026-11-25; the 95th is derived until the maintainer runs it. Gateway: Phase 3 (11 breaks) and Phase 4
(14 breaks) all caught after one extra test each.

Template tests read the frozen baseline `tests/fixtures/profile_base.yaml` (`tests.conftest.BASE_PROFILE`),
not the user's `profile.yaml`; only the cron-match test reads the real profile on purpose (item 110).
Fake secrets in tests are built by string concatenation so scanners do not flag them (item 109).

## 5. What exists

### Plane 1: axon-feed (Phase 1, unchanged except live results)
Order in `pipeline/run.py`: load store, collect, window, merge with store, resolve_redirects, enrich
(extract), process (canonicalize, dedupe, tag, score), publish, save store. Modules: `collectors/` (arxiv,
rss, github_releases, hf, hn, http with Throttle/Robots/Fetcher incl. `resolve`, registry incl.
`host_limits`), `pipeline/` (window, canonicalize, redirects, extract, dedupe, tag, score, publish, store,
run, health), `scripts/` (validate_config, validate_sources, capture_samples, export_schemas,
inspect_feed, publish_data, sync_issues). Published layout (spec 5.4): `meta.json`, `latest.json`,
`tags/<tag>.json`, `entities/<slug>.json`, `items/<id>.json`, `archive/`, `store.json`, on the `data`
branch served by Pages.
Run: `python -m pipeline.run --out ..\Axon\feed-out [--window-hours 72] [--no-store]` (production 168 via
`collect.yml`, cron `7 */3 * * *`, `contents: write`, `issues: write`, actions pinned to SHAs). Inspect:
`python -m scripts.inspect_feed <feed-out> [--top 15] [--untagged 25] [--tag <slug>] [--entity <name>]
[--save PATH]`. `docs/go-live.md` is the repo's checklist.

### Plane 2: axon-template (Phase 2 to 6)
Flow (`digest/pipeline.py`): `load_feed` -> extra_rss -> drop seen -> `rank` -> text for the top N ->
summary cache -> router (primary, circuit breaker, fallback, extractive last resort) -> validated
`Summary`. `digest/cli.py` renders, delivers, marks seen, writes `last_run.json` and, for Tier 3,
`state/tasks/<id>.json`.
CLI: `python -m digest.cli run|init|onboard|feedback|notify-failure|validate-profile`. Local secrets:
`.env` (git-ignored). Delivery channels: `email`, `telegram`, `slack`, `rss` (Atom file
`rss/feed.xml` on the `state` branch). Optional embeddings (Hugging Face, OpenAI-compatible), weekly
trends, feedback weights from Issues, onboarding form with `onboard.yml`. Real workflows: `ci.yml`,
`digest.yml` (cron `0 2 * * *` UTC = 07:30 Asia/Kolkata; `continue-on-error` state checkout; failure
notice step `if: failure()`; commit state `if: always()`), `onboard.yml` (issues opened or edited, label
`onboarding`, owner only, personal-account repos only: item 101), `keepalive.yml`, `register.yml`,
`issue-token.yml`, `revoke-token.yml`. All acting workflows have the template-repo guard
(`github.repository != 'gowthamsai09/axon-template'`), least-privilege `permissions:`, inputs through
`env:` only, SHA-pinned actions.
Local run (PowerShell): `python -m digest.cli run --profile profile.yaml --feed <path-to>\Axon\Axon\feed-out
--state-dir .local\state --outbox .local\outbox --dry-run` (add `--no-llm` for no key).

### Plane 3: axon-gateway (Phase 3 and 4; deployed 2026-11-27, Tier 3 off)
Hono app, `createApp(deps)` (injected fetch, clock, sleep, rng, nonce). Layout: `src/index.ts` (routes,
405/404, no CORS), `a2a.ts` and `mcp.ts` (thin adapters over the core), `agentcard.ts`,
`core/{updates,summarize,feed,deps,digest}.ts` (the one contract), `providers.ts` (fixed provider URLs,
key in a private field, `redirect: "manual"`), `summarizer/{prompting,validation,llm,types}.ts` (port of
the template), `prompts/summarizer.generated.ts` (generated from `prompts/summarizer_system.txt`),
`budget.ts` (45-subrequest budget, concurrency pool), `ratelimit.ts`, `security.ts` (key and `axn_` token
detection), `env.ts`, `errors.ts`, `http.ts`, `util.ts`, `tokens.ts` (KV: registration, `axn_` tokens as
SHA-256, revoke, cap 10), `tier3.ts`, `register.ts` (`/register`, `/tokens`, `/tokens/:id` behind OIDC),
`github/{http,app,oidc,runs}.ts` (REST client, App JWT PKCS#1/#8, down-scoped installation tokens, jose
OIDC verification, dispatch, list, read, cancel).
Behaviour: Tier 1 reads `tags/` and `entities/` shards (or `latest.json`) with edge caching (5 min),
merges, filters, sorts, returns items without excerpts plus freshness metadata. Tier 2 takes provider,
key and model from headers, reads `items/<id>.json`, builds the 13.1 prompt like the template, validates
strictly, retries once, repairs key points, degrades per item to `not_summarized`, fails fast on key or
quota errors, runs 3 items at a time inside a 45-subrequest budget. Tier 3 starts the owner's workflow
through the GitHub App and maps run state to A2A task state. A2A speaks 0.3.0; MCP speaks 2026-07-28
(stateless, `server/discover`) and 2025-11-25. Rate limits per IP: 60/min public, 10/min Tier 2,
30/min per token for Tier 3. Scripts: `npm run prompt:generate|prompt:check|prompt:compare -- <template
prompt path>`, `npm run bench`, `npm run dev`; `scripts/{dev-setup,mock-github,mint-oidc,integration-real}.js`
(`integration-real.js` NOT RUN). Docs: `docs/local-run.md`, `docs/github-app-setup.md`,
`docs/local-run-tier3.md` (merge into `local-run.md`).

### Hub (`Axon`)
Spec, schemas, canonical prompts (`prompts/`, summarizer id `p-56a22986b1`), corpora (hostile documents,
SSRF cases), docs, `scripts/pin_actions.py` (SHA table and `--check`), tests, STATE, GUIDELINES. Dev
requirements pinned in `requirements-dev.txt` (mypy, pytest, PyYAML, ruff, types-PyYAML).

## 6. Verification history (be exact)

### Phase 3 (laptop, 2026-10-28)
Observed: typecheck and lint clean; 442 tests passed (17 files); `prompt:check` current; `prompt:compare`
against the template file identical (`p-56a22986b1`); `npm run bench` median 0.98 to 1.38 ms, p95 up to
2.14 ms; `wrangler dev` started; smoke tests against the real `feed-out` served by `python -m http.server`:
health ok, Agent Card 0.3.0 with both skills, A2A Tier 1 completed with 5 items (`feed_stale` true, correct
for the old local feed), MCP `server/discover` and `tools/list`, 405, 415, key in body rejected, Tier 2
without a key `input-required`. `GET /` is 404 by design.
Sandbox (2026-10-26): clean `npm ci`, 442 tests, `wrangler deploy --dry-run` bundle 887 KiB (152 KiB
gzip; free limit 3 MB compressed), real workerd smoke tests; the dummy key appeared in neither the
response nor the Worker log. Tier 1 CPU measured only in Node (median 0.8 to 1.4 ms, p95 up to 3.3 ms
against the 10 ms free-plan budget); real workerd CPU unmeasured.
Not verified: a real Tier 2 call with a dedicated, spend-limited key; `npm audit` shows 3 dev-tooling
findings bundled with wrangler (production dependencies 0); real Cloudflare behaviour (rate limit
binding, cache TTL, CPU, subrequests).

### Phase 4 (sandbox 2026-10-29; laptop 2026-10-31)
Observed in the sandbox: typecheck, lint, `prompt:check`, 219 new tests; bundle 1165.98 KiB / 215.69 KiB
gzip; the full Tier 3 flow under workerd against `scripts/mock-github.js` (card, register, issue, start,
poll, cancel, MCP, revoke, refusal after revoke; tokens absent from the Worker log); template strict
mypy clean, 74 new tests; workflow scripts run under bash with a fake curl and a real jq.
Found and fixed: workerd rejects `redirect: "error"` (item 74); a newline slipped through the workflow
label check (item 64); a wrong test premise about the token cache.
Not run: anything against real GitHub (OIDC, App JWT, installation tokens, dispatch, run list latency,
`display_title`, contents API, cancel), real KV, a deployed Worker, a live Tier 2 call. The mock cannot
prove GitHub agrees.
Existing tests deliberately updated after the laptop run: gateway `test/providers.test.ts` (redirect
`manual`, plus `t3-providers-redirect.test.ts`), `test/security.test.ts`; template `tests/test_cli.py`,
`tests/test_workflows.py`; `tests/test_phase4.py` skips the bash tests on Windows.

### Phase 5 (mocked or offline only)
Shared injection corpus (38 hostile documents, 1 metadata case, 19 hostile model outputs); SSRF corpus
(88 URL cases) and fixes; secret-echo guard; `keepalive.yml`; gateway `deploy.yml` with
`scripts/check-deploy-config.js`; Actions pinned to SHAs (checkout v6.1.0, setup-python v6.3.0,
setup-node v6.5.0); hub canonical prompts with byte checks; stale-source Issues in the feed; eval harness
`evals/` (12 seed cases; stored answers are hand-written reference answers, not model output); failure
notice review (`safe_run_url`); docs `repo-hardening.md`, `notices-review.md`, `npm-audit.md`,
`first-push-phase5.md`. **Never run against real services:** keepalive, deploy workflow, Cloudflare token
scope, `evals live`, rulesets. Known hand-edit risk: hub `schemas/sources.schema.json`; if
`python -m scripts.export_schemas --check ..\axon\schemas` reports drift in `axon-feed`, regenerate with
`--out`. Loose end: the feed's `docs/go-live.md` still says stale-source Issues "belong to Phase 5";
replace that bullet with "Stale-source Issues (spec 11.1) are built: `collect.yml` has `issues: write`
for the `sync_issues` step; after a few runs check that Issues open only for sources empty 3 days in a
row (arXiv is exempt at weekends), close on recovery, and that the step never fails the run."

### Phase 6 (built with mocks; live results in section 3)
Telegram (88), Slack (89), shared chat helpers (90), Atom channel (95), embeddings (96), trends (97),
feedback weights (98), `digest.yml` (99), `deepseek-flash` default in template (94) and gateway (103),
onboarding form and `onboard.yml` (101), hostile-text corpus (104), docs (105). Natural-language Tier 3
deferred (102). Decisions: D1 and D2 deferred; D3 Atom on the `state` branch, no Pages; D4 daily cron
only; D5 no DeepSeek embeddings; D7 and D8 as built (91). Prompt sync: summarizer prompt unchanged
(`p-56a22986b1`); onboarding prompt (spec 13.2) equals the template file and the hub copy.
Found and fixed while building: `delivery.common.number()` overflow on huge JSON integers; thumbs links
shown with feedback off; `http_url` accepted whitespace; `\d` and `isdigit()` accept non-ASCII digits.
Mutation survivor found and fixed: `onb-choice-allowlist`.
Deliberate edits to existing tests: template `tests/test_cli.py`, `tests/test_phase4.py`,
`tests/test_openai_compat.py`, `tests/test_workflows.py`; gateway `test/summarize.test.ts`,
`test/providers.test.ts`; after the live fixes also template `tests/test_telegram.py`,
`tests/test_chat_delivery.py`, `tests/test_phase4.py`, `tests/test_stage23_misc.py`,
`tests/test_profile.py`, `tests/conftest.py`, `tests/test_onboarding.py`.

## 7. What is left

### A. Records
1. Paste Appendix C items 122 to 127 (`phase6-live-appendix-c-part3.md`) into the spec and commit STATE and the
   spec to the hub. Items 106 to 121 are in the spec already. Optionally call the result v1.8.
2. Docs fixes: `docs/github-app-setup.md` (gateway): untick Webhook Active, use type Secret in the dashboard,
   the token is shown unmasked, run the test from PowerShell behind the proxy, replace the "artifact" sentence;
   the `<pin-to-commit-sha>` wording (pins are SHAs already); `docs/repo-hardening.md` says "public repos" (item
   107); `docs/onboarding.md` on the template snapshot (item 110); the feed's `docs/go-live.md` loose end and its
   `/feed/` URL. Copy the changed `issue-token.yml` into existing user repos by hand (item 110).

### B. Digest live checks still open
Weekly trends (needs a weekly digest), embeddings (optional), stale-source Issues (needs a few days of feed
runs), `evals live --limit 3` (spend-limited key), failure notice with a broken SMTP secret in a scratch repo
(never the real secret). Optional fix, not built: start the 6-day feedback wait only when a run counted a vote.

### C. Gateway and Tier 3 remaining
Tier 3 over MCP; measurements (subrequests, CPU, KV reads and writes, start-to-completed latency, revoke
propagation); `Retry-After` on a real 429; CPU p99; a real MCP and A2A client; `npm run prompt:compare` once
more; the misleading cancel message "can no longer be canceled" for a run not yet listed; narrow the Cloudflare
deploy token (no expiry, broad template) and record what it needs; optionally declare
`GITHUB_APP_PRIVATE_KEY` as a required secret in `wrangler.toml` so a deploy cannot silently lose it; a
proxy-aware version of `scripts/integration-real.js`. Keep `[observability] enabled = false`.

### D. Housekeeping
Dependabot: gateway PR #1 (actions bump) waits for the `scripts/pin_actions.py` table; the npm group PR (minor
and patch only) may be merged after CI. Pin the feed's dev requirements. `tld` is MPL (kept). Branch rulesets on
the public repos.

### E. Deferred by decision (do not build unless asked)
Task B, the public feed repository (item 114); natural-language Tier 3 (item 102); A2A v1.0 (item 71); MCP OAuth
metadata (item 72).

### F. Next: the demo
The maintainer asked for help to demonstrate the whole project. Audience and format are to be decided.

## 8. Environment constraints (company laptop)
- `*.workers.dev` resolves and answers from the laptop (observed 2026-11-27: all gateway smoke tests ran
  from it). In the classic PowerShell window Ctrl+V does not paste into `Read-Host -AsSecureString` (one
  control character arrives); copy the key and read it with `Get-Clipboard`, validate its length and
  characters without printing it, then clear the clipboard.
- Node's built-in `fetch` (Node 22.14) does not use the company proxy and fails with `ENOTFOUND` for
  `workers.dev`, while PowerShell `Invoke-RestMethod` reaches it; run live checks from PowerShell (item 127).
  The Cloudflare dashboard "Add variable" form defaults to type Text; choose Secret for keys (item 123).
- Outbound DNS is restricted: `smtp.gmail.com`, `api.telegram.org` and `hooks.slack.com` do not resolve
  (observed 2026-11-26), and `api.deepseek.com` did not resolve on 2026-10-28. SMTP, Telegram and Slack
  therefore cannot be tested locally; all live channel tests ran in Actions. Do not work around IT policy
  (no DNS changes, tunnels or hotspots on the company laptop).
- The company pip index answers 401 (`pip install` of new packages fails); use no-install scripts that
  read installed metadata and `package-lock.json`. DeepSeek calls from Python worked without extra
  settings. `github.com` and `github.io` are reachable.
- The Slack CLI fails with 403 (`apps.hosted.generateAuthTicket`). Create the Slack app and incoming
  webhook in a browser on a personal device at api.slack.com/apps; the maintainer enters secrets there or
  in GitHub, never in chat.
- Web traffic goes through a proxy; TLS may be inspected. Python/httpx: `SSL_CERT_FILE`; pip:
  `PIP_CERT`. Node and `wrangler`: expect `npm config set proxy` and `https-proxy`, `NODE_EXTRA_CA_CERTS`.
  `wrangler dev` runs locally without a Cloudflare login; `wrangler login`, `deploy` and `kv` need
  Cloudflare reachable and are deferred. If the proxy intercepts `localhost`, set
  `[System.Net.WebRequest]::DefaultWebProxy = $null` before `Invoke-RestMethod`.
- `wrangler dev` runs the Worker on the laptop; workerd does not read `HTTPS_PROXY`, so a Tier 2 smoke
  test needs the provider hosts reachable; otherwise test Tier 2 only after deploy.
- Windows: read and write files with explicit UTF-8; the gateway `.gitattributes` forces LF for prompt files.

## 9. Decisions index (spec Appendix C)
**Live walkthrough (draft items, 2026-11-26): 106 licence (Apache-2.0); 107 repo visibility and GitHub
Free facts; 108 hub CI fixes; 109 fake secrets in tests; 110 frozen baseline profile and the
template-snapshot limitation; 111 issue-form body shape and `None` for an unset dropdown; 112 live
results; 113 environment facts.**
**Gateway deploy (draft items, 2026-11-27): 114 Task B deferred; 115 gateway push, Dependabot grouping and the
TypeScript 7 conflict, deploy guard on first pushes; 116 deploy-config test changed deliberately; 117
Cloudflare setup and deploy facts; 118 gateway live smoke results; 119 live Tier 2 call and key handling; 120
rate limit and metrics observed; 121 corrections (feed URL, hub name, stale checklist item); 122 template totals, Cloudflare edge log,
feedback live result and throttle; 123 Tier 3 setup facts and the unmasked token; 124 the `null` result-file
bug; 125 Atom and keepalive live; 126 Tier 3 live results; 127 environment facts. Next number: 128.**
**Phase 6 (in the spec): 88 Telegram; 89 Slack; 90 shared chat helpers and hardening fixes; 91 decisions
D1 to D8; 92 model name question (closed by 94); 93 facts for later stages; 94 `deepseek-flash` default;
95 Atom delivery; 96 embeddings; 97 trends; 98 feedback weights; 99 `digest.yml`; 100 maintainer decisions
and the end-of-phase reminder; 101 onboarding form and `onboard.yml`; 102 natural-language Tier 3
deferred; 103 gateway default model; 104 hostile-text corpus; 105 documentation.**
**Phase 5: 76 action pinning; 77 shared injection corpus; 78 secret-echo guard (closes 58); 79 hub ruff
excludes markdown; 80 keepalive and verified GitHub facts; 81 gateway deploy workflow and the workflow-test
change; 82 canonical prompts in the hub (closes the open part of 45); 83 stale-source Issues; 84 SSRF
suite; 85 eval harness; 86 failure notices review; 87 repo hardening docs and npm audit (not run).**
**Phase 4: 62 `allow_owner_channel`; 63 App key formats and installation scoping; 64 template workflows;
65 tokens and KV; 66 dev-only overrides; 67 OIDC claims; 68 UUIDv7 task ids and run lookup; 69 status
mapping and results; 70 policy pre-check; 71 A2A v1.0 decision and Tier 3 errors; 72 MCP Tier 3 and
authorization; 73 conditional exposure; 74 workerd `redirect` bug; 75 rate limits.**
**Phase 3: 45 prompt sync and pin; 46 Tier 2 model selection; 47 Appendix B verification (A2A 0.3.0, MCP
2026-07-28, Workers limits, rate limit syntax); 48 edge cache through `fetch`; 49 Tier 1 fallback keeps
filters; 50 subrequest budget and failure semantics; 51 response metadata and per-item statuses; 52 HTTP
conventions, no CORS, batches rejected; 53 no intent parsing; 54 MCP transport; 55 A2A details; 56 rate
limiting; 57 tooling; 58 secret-echo guard; 59 differences from the template port; 60 config validation
and error codes; 61 route behaviour.**
1 to 14 Phase 0. 15 to 20 collector findings. 21 to 28 Phase 1. 29 to 44 Phase 2 (29 cache key with
language; 30 summarizer contract and router; 31 derived `prompt_version`; 32 DeepSeek V4 ids, HF router;
33 new modules; 34 feed reading; 35 ranking; 36 Tier 3 behaviour; 37 CLI; 38 delivery; 39 digest.yml;
40 text extraction; 41 dependencies; 42 tests; 43 key-point repair; 44 local `.env`).

## 10. Assumptions to revisit (spec Appendix B)
**Phase 4 (none verified live):** installation token reuse until 2 minutes before expiry; App JWT `iat`
-60 s and `exp` +9 min; OIDC tolerance 30 s and max token age 15 minutes; JWKS edge cache 300 s; token cap
10 per repo; default lifetime 90 days; Tier 3 limiter 30/min per token; submitted grace 2 minutes; result
grace 90 seconds; retention 7 days; result cap 256 KiB; profile cap 64 KiB; run list `per_page=50` with a
one-day `created` margin; API version header `2022-11-28`; KV 60-second propagation; MCP static bearer
without OAuth metadata.
**Template:** interest weights 0.5/0.3/0.2, `EXTRA_RSS_MATCH` 0.5, thin text 200 characters, document
cap 24,000 characters, `max_tokens` 1500, breaker threshold 3, 10 page fetches per run, retention 30/30/7
days, stale feed 30 hours, SMTP default smtp.gmail.com:465, validator limits one-liner 200 and key point
160.
**Feed:** `MIN_BODY_HITS` 2, `MIN_ENTITY_MENTIONS` 2, `MAX_STORE_ITEMS` 6000, `MAX_EXTRACT_ATTEMPTS` 2,
`SQUASH_AFTER` 56, `REDIRECT_HOSTS`, Algolia HN params.
**Gateway (none verified live):** subrequest budget 45, Tier 2 concurrency 3, two transient failures stop
a request, provider retries 3 with `Retry-After` capped at 5 s, body cap 16 KB, edge cache 300 s, stale
feed 30 hours, fallback limits 60/10 per minute with `Retry-After: 60`, gateway version `1.0.0`, MCP error
data shape for `-32022`, strict `Mcp-Method` and `Mcp-Name` enforcement for 2026-07-28 requests, model id
charset, key charset `[A-Za-z0-9._~+/=:-]{8,512}`.
**Appendix B status:** items 1 to 4 verified 2026-10-25 (item 47). Pages (12) works in practice for the
feed; limits seen in docs on 2026-11-26: 1 GB site, 100 GB/month soft, 10 branch builds per hour. Gmail
SMTP (10) worked on port 465 with an app password. Still unverified: Actions limits (5). Verified live 2026-11-28: GitHub App permissions Actions
read and write, Contents read-only, Metadata read-only are enough to dispatch, list runs and read the result file (6);
the OIDC token was accepted by the gateway for register and issue-token (7). Re-check A2A v1.0 status before Phase 4 work resumes (labelled
draft or release candidate on the official page; one third-party page claimed a March 2026 release).

## 11. Open items
1. Section 7.B digest live checks; 7.C gateway and Tier 3 remaining (MCP route, measurements).
2. Dependabot PRs with the pin table; branch rulesets; feed dev requirements unpinned.
3. Entity matching misses new version names (Qwen4); sources under `needs_research:`.
4. Taxonomy schema export (`name_ambiguous`) and hub tests: confirm after the last feed change.
5. `onboard.yml` works for personal-account repositories only (item 101).
6. Template fixes do not reach existing user repos (item 110); document the manual copy.
7. Dev-only `npm audit` findings (`docs/npm-audit.md`); the eval set of 30 to 50 human-checked cases;
   `deepseek-flash` schema-violation retries (watch cost before raising `max_items`).
8. Deploy token has no expiry (maintainer's choice); narrow it.
9. The mutation count in STATE (95) was 94 in the project bundle; confirm on the laptop.
10. Task B deferred (item 114); A2A v1.0, MCP OAuth metadata, natural-language Tier 3 deferred.

## 12. Working conventions
- The user runs every test suite and every real-service step on the laptop; the assistant writes code,
  tests and docs, compile-checks at most, and gives exact PowerShell commands. Zero key custody: the
  assistant never asks for, sees or stores a key, token, password or webhook URL; if one appears in chat,
  rotate it.
- Work in small stages. After each, ship cumulative zips (only new and changed files; changed existing
  tests as full files), commands, expected counts (labelled derived), what is built and pending, then
  stop and wait. Zips are named `axon-<repo>-<topic>.zip`; the user unzips over the repo and runs
  `pip install -r requirements.txt -r requirements-dev.txt` (or `npm ci`) when dependencies changed.
- Hard rules: no `# type: ignore` and no `any` or `@ts-ignore`; do not hand-edit generated or exported
  models (`src/prompts/summarizer.generated.ts` is generated); run the formatter before the checks; keep
  secrets out of logs, files and chat; untrusted text never becomes instructions, URLs, commands or
  workflow inputs without validation; Summarizer prompt `p-56a22986b1` stays byte-identical in template,
  gateway and hub unless a deliberate, recorded change; the onboarding prompt (13.2) equals the template
  file, the hub copy and the spec text.
- Repository facts: the four code repos are public (secret scanning, push protection, rulesets and Pages
  need public repos on GitHub Free); the user's digest repo is private. Code reaches the assistant as text
  bundles in project knowledge (`<repo>.bundle.part1.md`, ...): rebuild with `python
  /mnt/project/axon_bundle.py unpack <parts> --out <dir>`; any PROBLEM line means stop.
- STATE and Appendix C are updated at the end of every phase and whenever something important is
  learned; "verified live" and "mocked only" stay separate claims.