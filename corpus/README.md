# Shared test corpora

`injection/` is consumed by BOTH axon-template (`tests/test_injection_corpus.py`) and axon-gateway
(`test/injection-corpus.test.ts`) against the real sanitize, prompt-assembly and validation code (no LLM).
Edit `scripts/make_injection_corpus.py` and regenerate; `tests/test_corpus.py` fails on drift.
In an `output` case with `raw_text`, the token `{JSON}` is replaced by the base good summary as JSON.

`ssrf/` is consumed by axon-template and axon-feed (`scripts/make_ssrf_corpus.py`).

`hostile-text/` (Phase 6) holds three files made by `scripts/make_text_corpus.py`:
`onboarding.json` (Issue-form answers), `feedback.json` (Issue payloads for the vote reader) and
`chat.json` (item text for Slack and Telegram). axon-template replays them in
`tests/test_text_corpus.py` against the real parser, vote reader and renderers. Each onboarding
case has a unique `marker` that must never appear in any output; a chat case lists the exact
strings that must not survive rendering. `tests/test_text_corpus.py` here fails on drift.
