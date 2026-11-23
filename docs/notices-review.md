# Failure notices and observability review (P5.10, Appendix C 86)

Reviewed in the template (`digest/cli.py`, `digest/summarizers/*`, `digest/state.py`) against guidelines section 5.
Evidence is in `axon-template/tests/test_notices.py` (mocked only: no real SMTP or provider was involved).

| Output | What it may contain | Enforced by |
|---|---|---|
| Failure e-mail (`notify-failure`) | A fixed sentence and one run link | `safe_run_url`: https only, host must equal `GITHUB_SERVER_URL` (default github.com), no credentials, no whitespace or control characters, at most 300 characters; otherwise the notice has no link |
| Router notices | Provider name, the secret NAME (`LLM_API_KEY`), a fixed sentence | fixed strings in `summarizers/router.py`; tested with a provider that echoes the key |
| `last_run.json` | Counts, token usage, warnings (100 x 300 chars), notices (20 x 300 chars), a redacted error | caps in `_last_run`, `redact` on every printed or stored error |
| Warnings | Item ids, field names, numbers, fixed phrases | validation messages carry no model text (tested with a hostile model output) |
| Outbox files / digest e-mail | The digest itself (feed titles and AI summaries, labelled AI-generated) | no secrets reach rendering (tested) |

Changed in this review: the old check accepted any `http(s)://...` run link; a hostile `--run-url` could put an
attacker's link into a trusted-looking e-mail. It now follows the table above.

Not verifiable here: the real e-mail path (SMTP is blocked on the development network; first-push item 4), what
GitHub shows in a failed run's log, and whether `::add-mask::` hides every derived value in real Actions.
Gateway: no request, header or body logging exists (`[observability] enabled = false`, `no-console` lint rule);
unchanged by this review.
