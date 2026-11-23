# First-push checklist: Phase 5 additions (nothing here has run against real services)

Add these to the STATE first-push checklist. Order stays: hub, axon-feed, axon-template, axon-gateway.

**All repos**
1. Actions are already pinned (`scripts/pin_actions.py --check` in the hub). After the first push, confirm Dependabot opens grouped update PRs and keeps the `# vX.Y.Z` comments.
2. Apply `docs/repo-hardening.md` sections 2 to 5 (secret scanning, push protection where the plan allows it, branch ruleset, environment). Record which parts your plan does not offer.

**Hub**
3. CI: the shared corpora tests and the prompt id test run (`corpus/injection`, `corpus/ssrf`, `prompts/`). The template and gateway CI check out the hub, so the hub repo must be readable by Actions (public, or a token).

**axon-feed**
4. `collect.yml` now has `issues: write` and a `continue-on-error` step that runs `scripts/sync_issues.py`. After a few runs check: Issues appear only for sources empty for 3 days (arXiv is exempt at weekends), the label `source-stale` is created, an Issue closes when the source recovers, and a manually closed Issue is not reopened for 3 days. If the step cannot create Issues (permissions or plan), the run must still succeed and the log must say so.

**axon-template**
5. `keepalive.yml`: run it once by hand and confirm `gh workflow enable digest.yml` works with the default token. Not verified live. Scheduled workflows are disabled after 60 days of inactivity in PUBLIC repositories only, so for a private digest repo this is a precaution.
6. Failure notice: break `SMTP_PASS` once and confirm the e-mail has the run link and nothing else (link validation is covered by tests, delivery is not).
7. Evals: `python -m evals.run live` with a dedicated spend-limited key on a few cases (`--limit 3`); this is the first time the real model meets the harness.

**axon-gateway**
8. Create the `production` environment with a required reviewer and the Cloudflare secrets (`docs/repo-hardening.md` section 5), replace the placeholders so `scripts/check-deploy-config.js` passes, then watch the first `deploy` run. It must wait for approval, and after CI only.
9. Re-read STATE first-push items 5 and 6 for everything about the Worker and Tier 3 (unchanged).
