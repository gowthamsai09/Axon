# Axon: engineering guidelines (production-grade development)

Audience: the assistant and the maintainer, in every chat. Read this together with `axon-architecture.md` (the spec) and `axon-STATE.md` (where we are). Order of authority when they disagree: **spec > STATE > this file > the phase brief**. If code or a guideline contradicts the spec, stop and flag it; do not deviate silently. A justified deviation becomes a numbered item in spec Appendix C. The spec itself can contain mistakes (example: the v1.3 `digest.yml` state-commit snippet fails on the first run): verify before copying.

## 1. How a phase is run (working agreement)
1. Read the spec, STATE, this file, the phase brief and the attached snapshots. Check the attachments really are there before saying something is missing.
2. Verify the spec's Appendix B items the phase depends on with a web search (versions, limits, API shapes) **before** coding. Record the date and result.
3. Build the whole phase in one go, in the order the brief gives. Decide small details yourself and state the assumptions. Ask at most one question, and only when truly blocked.
4. Run everything you can in the sandbox: formatter, linter, strict type check, the full test suite. Say plainly what was **observed** and what was **derived**, and what could not be run (the real network, the user's Windows machine, GitHub, Cloudflare, live providers). Never present an unrun check as passed.
5. Ship new and changed files as a zip of only those files. Give the expected test count, the exact commands for the user, and any file the user must delete (a zip cannot delete).
6. At the end of the phase: update `axon-STATE.md`, fold deltas into the spec as Appendix C items (numbering continues, next is 76), and give short commit messages.
7. After the user reports results, fix what failed, re-verify, and ship a small patch zip. Do not re-open finished work unless asked or a problem is found.

## 2. Engineering standards

### 2.1 Python (axon-feed, axon-template)
- Python 3.12, `from __future__ import annotations`, strict mypy with the pydantic plugin, ruff (`E F I UP B SIM`, line length 100), `ruff format`. **No `# type: ignore`.** If a library has no types (feedparser), wrap its output into our own typed models and use a per-module mypy override in `pyproject.toml`.
- Pydantic models are strict (`extra="forbid"`) for data we **write** and for config; readers of published JSON from another plane are **tolerant** (`extra="ignore"`, skip invalid items with a warning). Never copy another plane's schema into your repo; read the published JSON. Schemas are exported to the hub and checked for drift in CI.
- Inject every side effect: clock (`now`), HTTP client, resolver, SMTP factory, sleep, randomness. Code that calls `datetime.now()` or opens a socket inside logic is not testable offline.
- Small modules, one responsibility, typed signatures, no global mutable state. Files are written atomically (temp file plus `os.replace`). Always pass `encoding="utf-8"` to text I/O (Windows).
- Errors: raise specific exceptions with messages that are safe to print (no keys, headers, model text or user content). The CLI maps them to exit codes (0 ok, 1 runtime failure, 2 configuration error).
- Dependencies: few, pinned to exact versions, one purpose each, justified in an Appendix C item. Typed libraries preferred.

### 2.2 TypeScript (axon-gateway, Cloudflare Workers)
- `strict` TypeScript, no `any`, no `@ts-ignore` / `@ts-expect-error` to silence real problems. ESLint clean. Hono for routing; `zod` at **every** boundary (request bodies, headers, upstream responses, KV records); `jose` for JWTs. Avoid dependencies that need Node APIs; check Workers compatibility before adding one. Keep the bundle small.
- Pure core (`core/*`) with injected `fetch`, clock and crypto; protocol adapters (`a2a.ts`, `mcp.ts`) stay thin and only translate. One contract, many adapters (spec principle 4).
- Never `console.log` headers, request bodies or caller keys. Observability stays disabled for request/header logging (spec 7.2).
- Every Worker request has a CPU and subrequest budget: shard small files, avoid parsing large JSON needlessly, use the Cache API, cap concurrency (see 6).

### 2.3 Contracts shared across repos
- Topic slugs exist in three codebases (feed models, template profile, gateway zod). The hub parity check keeps them equal. Adding a slug means changing all three plus the prompts that list them (13.1 allowed tags come from code, 13.2 and 13.3 list slugs literally).
- The summarizer prompt (13.1) must be byte-identical in the template and the gateway. The template derives `prompt_version()` = `p-` + first 10 hex of the file's sha256. The gateway computes the same and a test pins it; any edit changes the cache key automatically. The canonical copy lives in the template; the sync mechanism is a Phase 3 deliverable.
- Versioned things: `schema_version` (feed), `prompt_version`, A2A and MCP protocol versions, `profile.version`. Changing a published shape means a new version, a note in Appendix C, and readers that tolerate both for a transition.

## 3. Testing standards
- **Offline always.** Tests never touch the real network, LLM providers, SMTP, GitHub or Cloudflare. Mock at the boundary: `httpx.MockTransport` and fake clients (Python); a fetch mock or Workers test pool (TypeScript).
- **Real data, sanitized.** Fixtures are trimmed copies of real captures (`tests/fixtures/feed-out/`), never invented shapes, never raw captures with secrets or emails. Collectors and consumers are tested against them.
- **Table-driven and one behaviour per test.** Name tests by behaviour. Cover the failure and abuse cases at least as well as the happy path.
- **Security tests are first-class:** keys never appear in responses, errors, logs or state files (assert on the absence of a unique key string); SSRF (private IPs, redirects to metadata, DNS to private ranges); prompt-injection documents (delimiter breakout, fake system text, hidden Unicode); header and path injection; oversized inputs; wrong methods and content types.
- **Contract tests:** responses are validated against the zod or pydantic schema and the exported JSON Schema; A2A and MCP handlers get a client-style smoke test.
- **Determinism:** inject `now`, `rng`, `sleep`. No sleeps in tests, no ordering luck, no dependence on the machine's time zone or locale.
- **Counts:** STATE records the expected count per repo. State whether a number was observed or derived. A drop in count without a reason is a bug.
- **Mutation sanity:** when a test seems too easy, break the code on purpose once and see it fail.

## 4. Security rules (non-negotiable; spec sections 1 and 10)
1. **Zero key custody.** The operator never stores user LLM or email keys. Tier 2 caller keys: header only, one request, memory only, never in KV, cache, logs, state, errors or URLs. Tier 3 runs on the owner's repo secrets.
2. **Untrusted stays untrusted.** Scraped text, feed content, model output and inbound agent messages are data. They never become instructions, URLs to fetch, commands, or tool arguments without validation. Model output is validated before use (shape, caps, URL allow-list, figures grounded in the source).
3. **SSRF.** http(s) only, public addresses only, every redirect hop re-checked, size and time caps. The gateway never fetches arbitrary URLs: only feed item ids and fixed provider hosts.
4. **Secrets in logs and files.** Print variable **names**, never values. Redact known secret values from anything printed. `.env` and similar are git-ignored; snapshots and zips are scanned for secrets before they leave the machine (`makesnapshot.py` does; also exclude `.dev.vars`). If a secret was pasted into a chat, rotate it.
5. **Workflows.** Explicit least-privilege `permissions:`; third-party actions pinned to commit SHAs; untrusted inputs reach code through `env:` only, never inside `run:` scripts; no secret-bearing jobs on forked pull requests; `persist-credentials: false`.
6. **Auth.** Tokens are 256-bit random, shown once, stored only as SHA-256, with expiry and revoke. OIDC: verify signature, issuer, audience and repository claims. One token maps to one repo; no caller-controlled repo, branch or workflow.
7. **Least privilege and blast radius.** The GitHub App has the narrowest permissions that work (Actions write, Contents read, Metadata). The App private key is the one high-value credential the operator holds; treat it accordingly.
8. **Privacy.** Collect only what the schema needs. Do not log user content. Retention is bounded (state 30/30/7 days, feed 7 days).

## 5. Error handling and observability
- Stable machine-readable error codes (spec 8.5 and 13.3: `policy_violation`, `owner_policy`, `key_in_body`, `missing_parameter`, `unsupported_skill`, `rate_limited`, `auth_required`, `llm_key_invalid`, `llm_quota`, `upstream_unavailable`) plus one short human sentence. Never echo inputs, headers or upstream bodies.
- Failures are isolated: one bad source, item or provider never fails a whole run; collect `warnings` (cap and truncate). Fatal conditions exit non-zero with an actionable message (names the secret, not its value).
- Correlation: `run_id` and `task_id` in logs and state. `last_run.json` is the run's receipt (status, counts, usage, warnings, notices). The digest footer states the model, token counts and that summaries are AI-generated.
- Gateway: Cloudflare analytics only, no request or header logging; an optional uptime ping on `/healthz`.

## 6. Reliability and performance
- Idempotency: `seen.json`, content-hash cache keys and `task_id` make re-runs safe. Workflows use `concurrency` groups.
- Retries: exponential backoff with jitter, honor `Retry-After` (capped), a circuit breaker per provider per run, a hard attempt cap. Timeouts on every outbound call.
- Gateway budgets (verify the current numbers from Appendix B item 3 before designing): per-request CPU time, subrequests per request, request and KV quotas, bundle size. Design rules that follow regardless: shard files are small; fetch only the shards needed; cache upstream reads (Cache API, TTL about 5 minutes); bound concurrency of upstream calls; never loop over unbounded input; cap body sizes and item counts.
- Cron is UTC and best effort; say "around" a time, never "at".

## 7. Documentation and change control
- Every deviation, decision or discovered fact that changes behaviour becomes an **Appendix C item** (numbered, dated, with the reason and how to revert if cheap). The spec text is edited where the old text would now mislead.
- STATE is updated at the end of every phase and whenever something important is learned (environment limits, live results). It must let a fresh chat start without guessing.
- Commit messages: Conventional Commits (`feat(scope):`, `fix(scope):`, `test:`, `docs:`, `chore:`), imperative, one logical change each. Hub commits for spec, schemas and STATE.
- Docs say what is verified and what is not. "Mocked only" and "verified live" are different claims; keep them separate.

## 8. Definition of done
**For a change:** formatter, linter and strict type check clean; all tests pass; new behaviour has tests including failure and abuse cases; no secret, header or user content can reach logs or errors; docs and Appendix C updated; commit messages written.
**For a phase:** everything in the phase brief's acceptance criteria; expected test counts recorded; the user's local run reproduced the sandbox results; STATE and spec updated; what remains unverified is listed explicitly with how to verify it; the zip contains only what changed and says what to delete.

## 9. Review checklist (use before shipping)
- Spec: does behaviour match the spec or is the deviation documented?
- Security: any new input? validated, bounded, untrusted? any new log line or error message that could contain a secret or user text? any new outbound request? guarded?
- Failure modes: what happens on timeout, 429, 5xx, bad JSON, empty result, huge result, missing config?
- Tests: failure and abuse paths covered? deterministic? no real network?
- Types and lint: clean without suppressions?
- Compatibility: did a published shape change? versions bumped and readers tolerant?
- Windows: UTF-8 explicit, no POSIX-only assumptions in the local developer path, paths built with `Path`.
- Docs: STATE, Appendix C, README, `.env.example` and workflow comments still true?

## 10. Release and go-live
- Local only until all phases are done (spec 12.1). First push order: hub, axon-feed, axon-template, axon-gateway. Checklist in STATE.
- At the first push: branch rulesets and required CI, Dependabot, secret scanning and push protection on every repo, pin Actions to SHAs, enable Pages for the feed, create the private user repo from the template, set Secrets and Variables, run workflows by hand once, verify email, caching and state-branch behaviour, then deploy the Worker.
- Rollback: Worker versions can be rolled back (keep the previous deployment); the feed `data` branch history is squashed weekly, so keep a manual snapshot of `meta.json` before risky changes; template changes only affect repos created afterwards (users update by hand), so keep changes backward compatible with existing `profile.yaml` files.
- After go-live: watch source health (`meta.json`), failure notices, Cloudflare analytics and quota use for a week; record real numbers in STATE; rotate keys on any suspicion.

## 11. Environment constraints and troubleshooting (company laptop)
- Outbound DNS is restricted (SMTP hosts do not resolve). SMTP is tested with mocks and verified from GitHub Actions at the first push. Do not circumvent IT policy.
- Proxy and TLS inspection: Python (httpx) honors `HTTPS_PROXY` and `SSL_CERT_FILE`; pip uses `PIP_CERT`; Node uses `NODE_EXTRA_CA_CERTS` and npm proxy settings. Certificate errors in logs come from the proxy, not the code.
- `wrangler dev` works locally without login; anything that talks to Cloudflare (login, deploy, KV) may be blocked: defer to the first push.
- After unzipping new code: `pip install -r requirements.txt -r requirements-dev.txt` (Python) or `npm ci` (gateway), **then** the checks. A green mypy does not prove packages are installed (missing-import overrides are in place for untyped libraries).
- PowerShell: set secrets for a session with `$env:NAME = Read-Host "NAME"` or use the git-ignored `.env`; use `;` to chain commands.

## 12. Handoff package for a new chat
Project knowledge holds the text documents (spec with Appendix C folded in, STATE, this file, the current phase brief, the exported schemas) **and the code as text bundles**, one set per repo, made with `axon_bundle.py` (no zip files: they were unreliable to upload). Files in project knowledge sit on disk under `/mnt/project/`, so the assistant reads them with tools and they do not fill the chat context unless printed.
```powershell
cd C:\Users\DGY3KOR\Desktop\Axon
python axon_bundle.py pack .\axon-gateway --out .\bundles\axon-gateway.bundle.md
python axon_bundle.py pack .\axon-template --out .\bundles\axon-template.bundle.md
python axon_bundle.py pack .\axon-feed --out .\bundles\axon-feed.bundle.md --exclude tests/fixtures
python axon_bundle.py pack .\Axon --out .\bundles\axon-hub.bundle.md
```
Each command writes `*.part1.md`, `part2.md`, ... (each at most about 350 KB); upload every part plus `axon_bundle.py` itself. The bundle includes tests and the small fixtures they need, honours `.gitignore`, skips locks, binaries, `.env*`, `.dev.vars`, keys and anything secret-like (reported, never written; use `--allow <path>` only for a file you reviewed). The assistant rebuilds a repo with `python axon_bundle.py unpack <parts> --out <dir>`, which verifies every file's sha256, the file count and that all parts are present. STATE records the **observed baseline test counts** per repo; the assistant compares its sandbox baseline with them, so a missing file shows up as a different count. Re-pack after every phase and delete superseded bundles. Large captured fixtures (axon-feed) may be excluded: say so in STATE and run that suite locally.

## 13. Lessons from Phases 1 to 6 (do not repeat)
- Check that attached files exist before claiming they are missing. Documents in the conversation are not always on disk.
- Never put `# type: ignore` in a draft "to fix later". Type the test helpers properly.
- Models miscount characters. Tell them the exact limit and the offending length on the retry; as a last resort delete over-long items (never edit text). Validate everything again after a repair.
- Vendors retire model ids. Verify names and base URLs with a web search at the time of coding (DeepSeek `deepseek-chat` was retired 2026-07-24).
- A green type check can hide missing packages; install requirements first.
- Real fixtures catch real problems (HN precision, entity ambiguity, empty arXiv feeds, thin pages). Tune on real output, not guesses; keep tuning in config, record it in Appendix C.
- Spec snippets can be wrong in practice (state-branch creation on the first run). Test the snippet's assumptions.
- Keep derived and observed numbers separate (test counts, quotas, latencies).
- Do not claim "done" for something that needs an environment you do not have; write the verification into the first-push checklist instead.
- **Mocked `fetch` cannot find runtime option rejections.** workerd rejects `redirect: "error"`; the Phase 3 mocks accepted it and Tier 2 would have failed on every real call (Appendix C 74). Run each new outbound request shape once under `wrangler dev` (use a local mock server) and assert in a test that banned option values never reappear.
- **Tests must not pass by accident.** A rejection test that passes because the code never ran (here: the WSL `bash` launcher failing) proves nothing. Make negative tests prove the code was reached, run mutation sanity on every security rule, and skip platform-specific tests explicitly with a reason (bash script tests skip on Windows and run on Linux CI).
- **Validate whole strings, not lines.** `grep -E '^...$'` is line-based and let a newline through a label check; use bash `[[ =~ ]]` or an anchored regex on the whole value, and test newline, NUL and unicode cases.
- **Ship changed existing tests as full files** when the repos are available; never ask the maintainer to hand-edit tests. List every existing test that was deliberately changed, with the reason.
- **The sandbox loses background processes between tool calls.** Start servers and run the client in the same command. Record only what was actually observed.
- **Test counts on the maintainer's machine can differ from the sandbox** (skips, platform tests); record the observed numbers from the maintainer's run in STATE, not the expected ones.
- **Write long docstrings and comments under 100 characters from the start.** `ruff format` wraps code but cannot fix E501 in strings and comments (Phase 5: 18 errors).
- **Stored answers written by hand are reference answers, never "model output".** Label them so a green replay is not read as a quality result; only a live run measures a model.
- **Any value that ends up in a notification is an injection channel,** not only feed text: the failure e-mail's run link needed scheme, host and character validation.
- **Do not trust names written from memory.** Test files that import helpers (`tests/test_redirects.py`, `test/helpers.ts` exports) must be checked against the repo before shipping; a stage that imports an unverified name is reported as a risk.
- **Record "not run" with the reason** when a tool fails for reasons unrelated to the code (the sandbox npm lockfile); never substitute an older result.
- **Stage zips are cumulative and byte-compared** against the previous bundle so only changed files ship; a zip that contains a file the user cannot find in the repo (a doc for another repo) is a defect.
- **Working agreement:** the user runs the suites on Windows and reports back; the assistant states expected counts as derived and records the observed ones in STATE.
- **Write tests against the real validators, not against what you think the rules are.** Phase 6 test mistakes came from guessing: a weekly profile needs `weekday` (the model requires it), `httpx` refuses a non-ASCII header given as `str` (pass bytes), and a `headlines` summary allows zero key points. Read the model or function before writing the fixture.
- **When a refactor changes a line, update every mutation pattern that quotes it.** `fb-decay` went stale after a typing fix and reported BROKEN; run `python scripts/mutation_sanity.py --check` after every edit that touches a mutated file.
- **Run `ruff check`, `ruff format --check` and `mypy` on tests and scripts too, before shipping.** The Phase 6 lint failures (SIM905, `no-any-return`, import order, long lines in comments) were all in code the assistant had not linted.
- **A second validation layer needs its own test.** `onb-choice-allowlist` survived because the profile model also rejects a bad choice; assert the first layer's own message so the mutation is killed.
- **Replies built from untrusted text are an injection channel.** The onboarding reply names only fixed form labels and validated values; test it with a unique marker and assert the marker is absent from stdout, stderr, the reply and the error list.
- **Never echo a model's or library's validation text for untrusted input.** Map each error location to a fixed message ("<field>: is missing or not valid").
- **`GITHUB_TOKEN` cannot edit workflow files and its events do not start new runs.** Design flows that need a schedule change as "comment the line, the owner pastes it".
- **Gate optional output on its own switch.** Thumbs links appeared whenever the repository URL was known; they now need `feedback.enabled`. Every new profile field is optional, default off, exported to the hub schema, in `init` and in the onboarding prompt.
- **Record the source of every external format.** The issue-form body shape is third-party knowledge, not on GitHub's pages: label it "not verified" and put the check in the first-push list.
- **A hostile-input corpus belongs in the hub when two repos or two code paths read the same class of text,** with a generator, a drift test and a replay in the consuming repo.
- **Deferred scope gets an item with its mitigation rules,** so a later build starts from the safety conditions (Appendix C 102).
