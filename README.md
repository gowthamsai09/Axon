# Axon (hub)

The shared repository of [Axon](https://github.com/gowthamsai09/Axon): the specification, JSON schemas,
canonical prompts, shared test corpora and operational docs. It has no runtime code of its own.

- `docs/axon-architecture.md`: the specification and single source of truth (v1.7).
- `docs/axon-STATE.md`, `docs/axon-GUIDELINES.md`: handoff state and engineering rules.
- `docs/`: setup and first-push guides (`setup-telegram.md`, `setup-slack.md`, `features.md`,
  `onboarding.md`, `first-push-phase5.md`, `first-push-phase6.md`, `go-live.md`, `repo-hardening.md`).
- `schemas/`: JSON schemas exported from the code (`python scripts/check_schemas.py`).
- `prompts/`: canonical summarizer and onboarding prompts (`python scripts/prompt_id.py`).
- `corpus/`: shared hostile-input corpora: `injection/`, `ssrf/`, `hostile-text/` (see `corpus/README.md`).
- `scripts/`: generators for the corpora, the prompt id and the Action pin checker.

```powershell
pip install -r requirements-dev.txt
ruff format .; ruff check .; mypy .; pytest
```
