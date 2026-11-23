# STATE and GUIDELINES updates after Phase 5 (merge into `axon-STATE.md` and `axon-GUIDELINES.md` at the end of Phase 6)

## STATE: phase table
| 5 Hardening | **DONE (built; user ran every suite on Windows and reported green; exact counts for feed, gateway and hub were not reported)**. Template observed on the user's machine: 640 collected, 596 passed, 44 skipped (bash-only tests). Nothing run against real services. |
| 6 Polish | NEXT |

## STATE: what was added in Phase 5
Hub: `corpus/injection` (38 hostile documents, 1 hostile metadata case, 19 hostile model outputs), `corpus/ssrf` (88 URL cases), `prompts/` (canonical prompts and id), `scripts/pin_actions.py`, `docs/repo-hardening.md`, `docs/notices-review.md`, `docs/npm-audit.md`.
Template: secret-echo guard, `keepalive.yml`, prompt sync check, SSRF hardening, `evals/` (12 cases), `safe_run_url`, tests `test_injection_corpus`, `test_ssrf`, `test_keepalive`, `test_phase5`, `test_prompt_hub`, `test_evals`, `test_notices`.
Feed: stale-source detection and Issues, SSRF hardening. Gateway: `deploy.yml`, `scripts/check-deploy-config.js`, injection corpus and SSRF tests, hub prompt check, FEED_BASE IP-literal refusal.
Appendix C items 76 to 87 (draft: `docs/phase56-appendix-c-draft.md`).

## STATE: changed tests (deliberate)
Gateway `test/workflows.test.ts` now allows `wrangler` only in `deploy.yml`. Template `tests/test_workflows.py` knows `keepalive.yml` as a real workflow. Feed `tests/test_workflows.py` knows the sync step and `issues: write`. Template `tests/test_safe_http.py` helper takes explicit `max_bytes` and `max_redirects`.

## STATE: open items to add
Phase 5 first-push checks (`docs/first-push-phase5.md`); the human-checked eval set of 30 to 50 cases; `npm audit` not reviewed; repo hardening not applied; real Issue creation, keepalive and deploy unverified.

## GUIDELINES: lessons to add to section 13
- Write the long lines the linter cannot wrap (docstrings, comments) under 100 characters from the start; `ruff format` does not fix E501 in strings and comments.
- Seed evaluation answers written by hand are reference answers, never "model output"; label them so a green replay is not read as a quality result.
- A hostile value in a notification (the run link) is as much an injection channel as feed text: validate scheme, host and characters.
- If a sandbox tool fails in a way unrelated to the code (npm lockfile), record "not run" with the reason; do not substitute an older result.
