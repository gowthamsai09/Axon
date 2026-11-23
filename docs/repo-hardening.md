# Repository hardening (P5.11) — NOT RUN

Nothing here has been executed: it needs your real GitHub repositories (first push). Plan-dependent items are marked
**check your plan**; availability on private repositories was read from GitHub's public documentation and is not
verified against your account. Replace `OWNER` and run from a shell where `gh auth status` is green. Repos:
`Axon`, `axon-feed`, `axon-template`, `axon-gateway` (your private digest repo is covered in section 6).

## 1. Order of the first push
Hub, axon-feed, axon-template, axon-gateway (STATE first-push checklist). Do sections 2 and 3 before the first
real run of any workflow.

## 2. Secret scanning and push protection
- Public repositories: both are free. Enable under Settings > Code security.
- Private repositories (your digest repo): push protection needs GitHub Secret Protection (a paid add-on on Team or
  Enterprise plans). **Check your plan.** Without it the guard is the `axon_bundle.py` scan and `.gitignore`.
```powershell
gh api -X PATCH repos/OWNER/axon-feed -f "security_and_analysis[secret_scanning][status]=enabled" -f "security_and_analysis[secret_scanning_push_protection][status]=enabled"
```
Repeat for each repo. If it answers 422, the feature is not available on that repo and plan.

## 3. Branch ruleset on `main` (all four repos)
Required status checks: hub `checks`; feed and template `checks` and `schema-consistency`; gateway `checks`.
```powershell
$body = @'
{ "name": "main protection", "target": "branch", "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "rules": [ { "type": "deletion" }, { "type": "non_fast_forward" },
    { "type": "pull_request", "parameters": { "required_approving_review_count": 0, "dismiss_stale_reviews_on_push": true,
      "require_code_owner_review": false, "require_last_push_approval": false, "required_review_thread_resolution": false } },
    { "type": "required_status_checks", "parameters": { "strict_required_status_checks_policy": true,
      "required_status_checks": [ { "context": "checks" } ] } } ] }
'@
$body | gh api -X POST repos/OWNER/Axon/rulesets --input -
```
Add `{ "context": "schema-consistency" }` for feed and template. With one maintainer, 0 required approvals keeps you
unblocked while still forcing every change through CI. **Check your plan** (rulesets on private repos need a paid plan).
Exception: `axon-feed` pushes the `data` branch with `GITHUB_TOKEN`; the ruleset above only targets the default branch.

## 4. Dependabot
`.github/dependabot.yml` ships in every repo (weekly, grouped, pip or npm plus github-actions). Turn on alerts and
security updates: Settings > Code security. Review the grouped PRs; Actions pins keep their `# vX.Y.Z` comments so
Dependabot can update the SHAs (`scripts/pin_actions.py --check` verifies pins stay full SHAs).

## 5. Deploy environment (gateway)
Settings > Environments > `production`: required reviewer = you, deployment branches = `main` only, and put
`CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` in **environment** secrets, not repository secrets.
Cloudflare token: custom token, Account > Workers Scripts > Edit (add Workers KV Storage > Edit only if the deploy
step manages KV), scoped to this one account, with an expiry date. Environment protection on private repos is
plan-dependent: **check your plan**.

## 6. Your private digest repo
Secrets: `LLM_API_KEY` (dedicated, spend-limited), `SMTP_USER`, `SMTP_PASS` (app password), `MAIL_TO`, optional
fallback key. Do not install the GitHub App on any other repo. Keep Actions permissions at "read" by default
(Settings > Actions > General); each workflow asks for its own `permissions:`.

## 7. Rotation and incident response
| Secret | Where created | Rotate when | How |
|---|---|---|---|
| LLM keys | provider console | on any suspicion; every 90 days | create new key, update the Secret, revoke the old one |
| SMTP app password | Google account | same | new app password, update `SMTP_PASS`, revoke old |
| GitHub App private key | App settings | same | generate a second key, `wrangler secret put GITHUB_APP_PRIVATE_KEY`, delete the old key |
| Cloudflare API token | Cloudflare | same | roll the token, update the environment secret |
| Owner tokens (`axn_`) | `issue-token` workflow | when an agent is retired | run `revoke-token` with the `tk_` id |
If a secret appears in a chat, log or commit: revoke first, then clean up. Pasted in chat means rotate.

## 8. Verify (after setup)
Open a PR that fails CI: merging is blocked. Push a fake secret string to a branch of a test repo: push is refused
where push protection is on. Run `deploy` with no reviewer approval: it waits.
