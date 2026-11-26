# Axon: project state (handoff file)

Updated: 2026-11-26. Phase 6 is built and its live walkthrough (Task A of `axon-END-OF-PHASE6-BRIEF.md`)
is mostly done: Telegram, Slack, email, the onboarding form and the `state` branch are **verified live**.
Spec: `axon-architecture.md` **v1.7** plus the draft Appendix C items **106 to 113** (file
`phase6-live-appendix-c.md`, to be merged when the spec becomes v1.8). Appendix C items 1 to 105 are in
the spec. Rules for working: `axon-GUIDELINES.md`. Owner: gowthamsai09.

Words used in this file: **verified live** = seen on real services by the maintainer; **mocked only** =
tests with fakes; **not run** = nothing executed; **derived** = computed, not observed.

## 1. Where things stand

| Item | State |
|---|---|
| Phases 0 to 6 (code) | DONE. Phase 6 built 2026-11-26 in stages 1, 23, 45 |
| Four code repos on GitHub | `axon` (the "Axon" repo), `axon-feed`, `axon-template`: pushed, public, CI green. `axon-gateway`: repo exists, **not pushed** |
| Licence | Apache-2.0, "Copyright 2026 gowthamsai09", all four repos (item 106) |
| Feed (plane 1) | **Verified live**: `collect.yml` runs, `meta.json` served by Pages |
| User pipeline (plane 2) | **Verified live** in the private repo `axon-digest` (created from the template): Telegram, Slack, email, onboarding form |
| Gateway (plane 3) | Built and mock-tested only; not deployed |
| Next work | Close the remaining Task A checks; Task B (public feed repo design); Task C remainder (push gateway, hardening) |

Folder layout on the laptop (siblings): `Axon/` (hub), `axon-feed/`, `axon-template/`, `axon-gateway/`,
`feed-out/` (generated, currently `<path-to>\Axon\Axon\feed-out`). Live repos: `gowthamsai09/axon`
is the hub repo named "Axon" (check the exact name before scripting), `gowthamsai09/axon-feed`,
`gowthamsai09/axon-template`, `gowthamsai09/axon-gateway`, private `gowthamsai09/axon-digest`.
User environment: company Windows laptop, PowerShell, conda env `axon` (Python 3.12), Node 22, behind a
corporate proxy with DNS restrictions (section 8). Commits use the GitHub noreply address.

## 2. Phase status (spec section 12)

| Phase | Status |
|---|---|
| 0 Foundations | DONE |
| 1 Shared feed | DONE. Live data 2026-10-20 (665 items). **First Actions run verified live 2026-11-26** (item 112) |
| 2 User pipeline MVP | DONE 2026-10-23. Real email **verified live 2026-11-26** |
| 3 Gateway Tier 1 and 2 | DONE 2026-10-28 (laptop-tested with mocks). Not deployed; no live LLM call |
| 4 Tier 3 | DONE 2026-10-29, user-confirmed green 2026-10-31. Nothing against real GitHub, KV or a deployed Worker |
| 5 Hardening | DONE 2026-11-22. Mostly mocked only (section 5) |
| 6 Polish | BUILT 2026-11-26; stage 45 user-confirmed green 2026-11-25. Live walkthrough: see section 3 |

## 3. Live walkthrough record (2026-11-26)

**Verified live**
- Hub, feed and template CI green on GitHub; Dependabot opened PRs (item 108).
- `axon-feed`: `collect.yml` ran; `https://gowthamsai09.github.io/axon-feed/meta.json` is served (the
  site root returns 404, expected: there is no index page). Counts were checked with PowerShell.
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

**Mocked only so far**
- Atom (`rss`) channel, embeddings, trends, feedback Issues and links, `keepalive.yml`, stale-source
  Issues, `evals live`, deploy workflow, gateway, Tier 3, the second email-failure path.

**Findings fixed during the walkthrough** (all have tests): pydantic mypy plugin in the hub (108); token-
shaped fixture flagged by secret scanning (109); tests read the editable profile (110); `None` dropdown
value (111). **Limitation:** a repo made from the template is a snapshot, so later template fixes do not
reach existing user repos; the owner copies changed files by hand (item 110).

## 4. Test status (observed by the user on Windows unless marked)

| Repo | Tests | Notes |
|---|---|---|
| axon-template | Last observed 2026-11-25 after stage 45 (with `HUB_DIR` set): **1397 collected, 1352 passed, 45 skipped**. After the live fixes (baseline profile, `None` dropdown): **expected 1402 collected, 1357 passed, 45 skipped (derived; confirm on the laptop)** | Test files by stage: stage 1 `test_chat_common`, `test_telegram`, `test_slack`, `test_chat_delivery`; stage 23 `test_rss`, `test_embeddings`, `test_trends`, `test_weights`, `test_feedback`, `test_cli_phase6`, `test_pipeline_phase6`, `test_stage23_misc`; stage 45 `test_onboarding`, `test_onboard_cli`, `test_onboard_workflow`, `test_text_corpus` (139 tests when the hub copy is found through `HUB_DIR` or `..\Axon`, else 6 skips) |
| axon-feed | user reported green; exact count not reported (about 446, derived) | Record the real number at the next run |
| Axon hub | 30 passed + 1 skipped (observed after stage 45); CI green on GitHub | corpus, prompt id, schema, hostile-text tests |
| axon-gateway | **888 passed in 29 files** (observed after stage 45) | typecheck, lint, tests, `prompt:check` (`p-56a22986b1`) green |

Checks everywhere: `ruff format .; ruff check .; mypy .; pytest` (Python); `npm run typecheck; npm run
lint; npm test; npm run prompt:check` (gateway).

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

### Plane 3: axon-gateway (Phase 3 and 4; not deployed)
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

### A. Close the live walkthrough (Task A, step 6 and 7)
1. Merge Appendix C items 106 to 113 into the spec (v1.8) and commit this STATE to the hub (replace the
   hub copy; the project copy is the source).
2. Confirm: the secret-scanning alert is closed as "Used in tests"; template CI green after the `None`
   fix (expected counts in section 4); the 95 mutations run on the laptop.
3. Live checks still open (follow `docs/first-push-phase5.md` and `docs/first-push-phase6.md`): Atom
   (`rss`) channel, embeddings, trends, feedback Issues and links, `keepalive.yml`, stale-source Issues
   after a few feed runs, `evals live --limit 3`, failure notice with a broken SMTP secret (use a scratch
   repo, never the real secret).
4. Docs fixes: wording of `<pin-to-commit-sha>` in docs and the checklist (pins are SHAs already);
   `docs/repo-hardening.md` and checklist 5(k) say "public repos" (item 107); `docs/onboarding.md` says a
   template fix does not reach existing repos (item 110); feed `docs/go-live.md` loose end (section 6).

### B. Task B: public feed repository
Keep the main digest repo private and publish only the digest feed from a separate small public repo.
This is a deliberate deviation from "one private repo per user" and becomes its own Appendix C item
(next number 114). Review the exposures first: `profile.yaml` (interests, schedule, language), the
`state` branch and digests, Actions logs, tokenized `extra_rss` URLs, `base_url` values, open Issues and
pull requests. Propose the smallest mechanism (what is copied, token scope, trigger), list what becomes
public, write the Appendix C item and tests, then wait. Free facts: Pages is for public repos on GitHub
Free (item 107). `delivered.json` already shows that state carries item ids, timestamps and tags, which
reveal reading interests.

### C. Task C: remaining publishing work
Push `axon-gateway`. Branch ruleset and secret scanning with push protection on each public repo (free for
public repos only). Dependabot PRs: merge each bump together with the `scripts/pin_actions.py` table
update, or `pin_actions.py --check` fails. Pin the feed's unpinned dev requirements. Note the `tld`
dependency is MPL (kept as a dependency). Then the gateway first-push items below.

### D. Gateway and Tier 3 first-push checklist (not started)
5. axon-gateway: (a) resolve `<pin-to-commit-sha>` in `ci.yml`; CI green including `prompt:check` and the
   hub schema contract tests (`REQUIRE_HUB_SCHEMAS=1` also needs `feed-item.schema.json`); (b) Cloudflare
   account, `wrangler login`, set `PUBLIC_URL` in `wrangler.toml` to the real `workers.dev` URL (a
   placeholder makes the Agent Card answer 500 on purpose); confirm `FEED_BASE` is the Pages feed
   (https only); (c) check `compatibility_date` against the deployed workerd; (d) `deploy.yml` exists
   (item 81); (e) deploy; `/healthz`, Agent Card URL, then the PowerShell smoke tests from
   `docs/local-run.md` against the deployed URL; (f) an MCP client smoke test with a real client; (g) a
   real Tier 2 call with a dedicated, spend-limited key: confirm the key appears nowhere (response,
   `wrangler tail`, dashboard logs); (h) verify the rate limit binding on the free plan and note the real
   429 behaviour; (i) record real numbers (CPU per request for Tier 1 on the largest shard and Tier 2,
   subrequests, requests per day); (j) keep `[observability] enabled = false`; (k) secret scanning and
   push protection on every public repo (spec 10.2); (l) `npm run prompt:compare` against the template
   copy once more.
6. Tier 3 (`docs/github-app-setup.md`): (n) create the GitHub App (Actions write, Contents read, Metadata
   read, no webhook) and install it on the one private digest repo (`axon-digest`); (o) `wrangler kv
   namespace create TOKENS`, put the id and `GITHUB_APP_ID` in `wrangler.toml`, `wrangler secret put
   GITHUB_APP_PRIVATE_KEY` from the `.pem`; do not set `ENVIRONMENT` or any `GITHUB_*` override; (p)
   repository variable `GATEWAY_URL` = `PUBLIC_URL`; (q) run `register`, `issue-token` (check whether the
   job summary shows the token or `***`: item 64), `revoke-token`; (r) `node scripts/integration-real.js`;
   (s) measure subrequests per start and poll, CPU per request, KV reads and writes per day, `message/send`
   to `completed` latency, run-title lookup lag, revoke propagation; (t) a real Tier 2 call under workerd
   (item 74); (u) confirm the owner policy pre-check and an `owner_policy` result file both map to
   `rejected`.
7. Record real numbers (latency, CPU time, quotas) in this file.

### E. Deferred by decision (do not build unless asked)
Natural-language Tier 3 (item 102, five mitigation rules), A2A v1.0 (item 71), MCP OAuth metadata
(item 72).

## 8. Environment constraints (company laptop)
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
results; 113 environment facts. Next number: 114.**
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
SMTP (10) worked on port 465 with an app password. Still unverified: Actions limits (5), GitHub App
permission details (6), OIDC claims (7). Re-check A2A v1.0 status before Phase 4 work resumes (labelled
draft or release candidate on the official page; one third-party page claimed a March 2026 release).

## 11. Open items
1. Live checks listed in 7.A.3; failure-notice live test.
2. Task B (public feed repo) and Task C (push gateway, rulesets, Dependabot with the pin table).
3. Everything in 7.D (gateway deploy, Tier 3 against real GitHub and KV, live Tier 2).
4. Entity matching misses new version names (Qwen4); sources under `needs_research:`.
5. Taxonomy schema export (`name_ambiguous`) and hub tests: confirm after the last feed change.
6. `onboard.yml` works for personal-account repositories only (item 101).
7. Template fixes do not reach existing user repos (item 110); document the manual copy.
8. Real-runtime numbers for the gateway; dev-only `npm audit` findings (`docs/npm-audit.md`).
9. The eval set of 30 to 50 human-checked cases (yours to write); `deepseek-flash` length-limit retries
   (watch cost before raising `max_items`; the prompt stays locked).
10. A2A v1.0, MCP OAuth metadata, natural-language Tier 3: deferred (section 7.E).

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