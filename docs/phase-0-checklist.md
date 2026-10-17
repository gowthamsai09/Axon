# Phase 0 done checklist

## Repos and settings (manual)
- [ ] `axon-feed`, `axon-template`, `axon-gateway` exist and are public; `Axon` hub is **public** (CI checks out `schemas/`)
- [ ] `axon-template`: Settings -> General -> **Template repository** ticked
- [ ] All four repos: Settings -> Code security -> **Secret scanning** and **Push protection** enabled
- [ ] All four repos: **Private vulnerability reporting** enabled; fill in `<security-contact-email>` in SECURITY.md
- [ ] All four repos: **Dependabot alerts** and **security updates** enabled (`dependabot.yml` is in the repo)
- [ ] Files copied in (zip), `docs/axon-architecture.md` is the project-knowledge spec verbatim
- [ ] `<pin-to-commit-sha>` replaced everywhere (docs/pinning-actions.md)
- [ ] LICENSE chosen and added to each repo

## Local verification
- [ ] `axon-feed`: ruff, mypy, pytest green; `python -m scripts.validate_config` exits 0
- [ ] `axon-template`: ruff, mypy, pytest green; `python -m digest.cli validate-profile profile.yaml` OK
- [ ] `axon-gateway`: eslint, tsc, vitest green
- [ ] `Axon`: ruff, mypy, pytest green; `python scripts/check_schemas.py` OK
- [ ] Schema checks: `python -m scripts.export_schemas --check ../Axon/schemas` OK in feed and template
- [ ] `python -m scripts.validate_sources` run locally and the output pasted back for review

## CI and protection (after the first push)
- [ ] CI green on `main` in all four repos
- [ ] Branch ruleset on `main`: require PR, require status checks (`checks`, `schema-consistency`), block force-push
- [ ] Review `needs_research` list and the "proposed additions" entities; delete what you do not want
- [ ] Reddit sources: terms of service reviewed (Appendix B #11) before enabling in Phase 1
