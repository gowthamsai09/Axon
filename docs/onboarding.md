# Onboarding with the Issue form

Spec 6.8, Appendix C 101. Never enter an API key, token or password in the form.

## Steps
1. In your private repository (created from the template): Issues > New issue > **Onboarding**.
   Create the label `onboarding` first if the form does not apply it.
2. Fill the form and tick the "no keys" box. Saving an edit re-runs the check.
3. The `onboard` workflow replies on the Issue:
   - problems: a list of form fields to fix, nothing changed;
   - success: `profile.yaml` was committed, the Issue is closed, and the reply gives a cron line and the
     secret names to add.
4. Paste the cron line into `.github/workflows/digest.yml` under `schedule:` (a workflow cannot edit
   workflow files, so this step is yours), add the listed secrets, set the variable `FEED_BASE`, and run
   `digest` once.

## Limits
- Only the repository owner can use it (author and editor must both equal the owner). That works for
  personal-account repositories; for an organisation use `python -m digest.cli init` or edit
  `profile.yaml`.
- Your existing `agent_access` settings are kept when you submit the form again.
- The form never shows what you typed in its reply, on purpose.

## Try the parser locally (PowerShell)
```powershell
$env:ISSUE_BODY = Get-Content .\sample-issue.md -Raw
python -m digest.cli onboard --profile .local\profile.yaml --comment-file .local\comment.md
Get-Content .local\comment.md
```
`sample-issue.md` is the Issue text GitHub produces (`### Delivery channel`, a blank line, the answer).
