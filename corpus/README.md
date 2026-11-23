# Shared test corpora

`injection/` is consumed by BOTH axon-template (`tests/test_injection_corpus.py`) and axon-gateway
(`test/injection-corpus.test.ts`) against the real sanitize, prompt-assembly and validation code (no LLM).
Edit `scripts/make_injection_corpus.py` and regenerate; `tests/test_corpus.py` fails on drift.
In an `output` case with `raw_text`, the token `{JSON}` is replaced by the base good summary as JSON.
