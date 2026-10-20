# Axon: project state (handoff file)

Updated: 2026-10-20 (Phase 1 COMPLETE and verified on live runs; fixes 4 to 11). Spec: `axon-architecture.md` v1.3 (single source of truth; Phase 1 deltas are folded in, Appendix C items 21 to 28). Owner: gowthamsai09.
Working mode: LOCAL ONLY, nothing pushed to GitHub until all phases are done (spec 12.1). `axon-feed/docs/go-live.md` is the first-push checklist.
User environment: Windows, PowerShell, conda env `axon` (Python 3.12), behind a corporate proxy.
Folder layout (siblings): `Axon/` (hub), `axon-feed/`, `axon-template/`, `axon-gateway/`, `feed-out/` (generated, currently under `Axon\Axon\feed-out`).

## Phase status (spec section 12)
| Phase | Status |
|---|---|
| 0 Foundations | DONE |
| 1 Shared feed | DONE. Collectors, window, redirects, extract, dedupe, tag, score, publish, rolling store, per-domain rate limits, real `collect.yml` + `publish_data.py`. Verified locally on live data (2026-10-20: 665 items, store retention confirmed, 16 entities); the first real Actions run happens at the first push |
| 2 User pipeline MVP | NEXT. Not started (template has only profile/task-result models, prompts, workflow stubs) |
| 3-6 | NOT STARTED (gateway has only /healthz and zod schemas) |

## Test status
axon-feed: 255 passed (user-confirmed after fix10); fix11 adds 2 tests, so 257 expected: run `ruff format .; ruff check .; mypy .; pytest` and record the count here.
axon-template: 86. Axon hub: 10 (+1 skipped). axon-gateway: 48 (vitest). (Those three are from before this session; re-run when next touched.)

## Phase 1 as built (axon-feed)
Order in `pipeline/run.py`: load store, collect, window, merge with store, resolve_redirects, enrich (extract), process (canonicalize, dedupe, tag, score), publish, save store.
Modules: `collectors/` (arxiv, rss, github_releases, hf, hn, http with Throttle/Robots/Fetcher incl. `resolve`, registry incl. `host_limits`), `pipeline/` (window, canonicalize, redirects, extract, dedupe, tag, score, publish, store, run), `scripts/` (validate_config, validate_sources, capture_samples, export_schemas, inspect_feed, publish_data).
Run: `python -m pipeline.run --out ..\Axon\feed-out [--window-hours 72] [--no-store] [--store PATH]` (production: 168, via collect.yml).
Inspect (all accept `--save PATH`, UTF-8): `python -m scripts.inspect_feed <feed-out> [--top 15] [--untagged 25] [--examples 2]`; drill-down `--tag <slug>` or `--entity <name>` with `--limit N`.
Fixtures: `tests/fixtures/` = sanitized real captures (2026-10-16). Never commit raw captures.
`collect.yml` (real): cron `7 */3 * * *`, `contents: write`, steps prepare data branch, run pipeline (`--out data/feed --window-hours 168`), push; actions pinned to SHAs (checkout v6.1.0, setup-python v6.3.0; ci.yml too). `scripts/publish_data.py` is tested against a local bare repo (first run, update, unchanged, weekly squash after 56 commits, token only as an HTTP header, errors scrubbed).

## Decisions (all in spec Appendix C 15 to 27)
Reddit not collected. Pre-release tags and arXiv `replace` types skipped. HN gated on whole-word LLM(s). Entities: `name_ambiguous` (21); title hit or 2 body mentions, releases match title only (22). Redirects only for known redirector hosts (23). Rolling store `feed/store.json` (24). No page fetch for video/social hosts, failing pages tried twice (25). Strictest declared limit per host (26). Production workflow and publisher (27).
Rules: no `# type: ignore`, do not hand-edit models, run `ruff format .` before checks.

## Known assumptions to revisit (spec Appendix B)
`MIN_BODY_HITS = 2` (topics), `MIN_ENTITY_MENTIONS = 2` (entities), `MAX_STORE_ITEMS = 6000`, `MAX_EXTRACT_ATTEMPTS = 2`, `SQUASH_AFTER = 56`, `REDIRECT_HOSTS` list. Algolia HN params; GitHub/Cloudflare/Pages limits; source ToS. DeepSeek may still tag a few HN items on incidental body mentions.
Phase 1 precision fixes (fix11, spec item 28): HN gate needs LLM in the title, 2 mentions in the text, or 1 mention plus an AI term in the title; "X-compatible" is not an entity mention. Recheck the next live report: untagged HN share (was 54% of HN items) and the HN items in the top 15 by score.
Observed 2026-10-20: arXiv feeds go empty intermittently per feed (cs.AI empty while cs.CL and cs.LG were full; earlier the reverse); the store plus runs every 3 hours covers it. "robots.txt unreachable (SSL ... CERTIFICATE_VERIFY_FAILED)" warnings are the corporate proxy, not the code.
Open after Phase 1: new version names do not match entities (Qwen4); stale-source Issue (Phase 5); sources under `needs_research:`; arXiv feeds are empty at weekends (expected; recheck on a weekday run).
Housekeeping: confirm `python -m scripts.export_schemas --out ..\Axon\schemas` was run after fix5 (taxonomy schema gained `name_ambiguous`) and that the hub tests pass. Replace the spec in project knowledge with v1.3.

## Starting Phase 2 in a new chat
Project knowledge holds the spec v1.3 and this file. Attach: `axon-template-snapshot.md` (current template code, same format as the axon-feed snapshot) and, for realistic feed data, `feed-out/meta.json`, `feed-out/latest.json` and one `feed-out/tags/<slug>.json`. Phase 2 is built in one go against the local `feed-out` folder, nothing pushed. The feed-item schema is `Axon/schemas/feed-item.schema.json` (owned by axon-feed); the template must not copy it, it reads the published JSON.

## Phase 2 plan (axon-template, spec section 6; build in this order)
1. `digest/` core: `profile.py` (pydantic, spec 6.1 validation rules), `feed_client.py` (reads shards from FEED_BASE or a local folder), `rank.py` (user_score, spec 5.3), `state.py` (seen.json, summary cache, last_run.json).
2. `summarizers/` (spec 6.4, prompt 13.1): base, deepseek, huggingface, openai_compat, router with circuit breaker and extractive fallback; strict output validation (URLs, notable_figures, tags subset); injection corpus later (Phase 5).
3. `render/` (email html/txt, telegram md) and `delivery/email.py` first (Telegram, Slack, RSS are Phase 6).
4. `cli.py` (`run`, `init`, `notify-failure`), `task_result.py` writing for Tier 3, `digest.yml` made real.
5. Local run against the local `feed-out` folder with a mocked or real LLM key and an SMTP dry run.

## Workflow conventions
Assistant ships changed files as a zip (`axon-fixN.zip`) to unzip over the local repos; user runs `ruff format .; ruff check .; mypy .; pytest`. A zip holds only changed files unless it says cumulative (fix10 is cumulative with fix9). Apply in order. Project knowledge should hold: the spec and this file only.
When tuning, the user pastes inspect_feed reports (use `--save`).
