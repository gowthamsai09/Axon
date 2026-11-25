# First-push checklist: Phase 6 additions (nothing here has run against real services)

Add these after `first-push-phase5.md`. Order stays: hub, axon-feed, axon-template, axon-gateway.

**axon-template, delivery**
1. Telegram: send a real digest to a test chat. Check formatting, links, link previews off, no repeats.
2. Slack: same for a test channel; check whether links unfurl; revoke the webhook and confirm the next run
   fails with the "no longer exists" message.
3. Force a long digest (many items); every chunk arrives in order. Send a title containing
   `_ * [ ] ( ) ~ \` | & < >` and check both channels show it literally.
4. Open the raw URL of `rss/feed.xml` on the `state` branch in a reader (with access): it parses and a
   rerun does not repeat an entry.

**axon-template, optional features**
5. Hugging Face embeddings: exact feature-extraction URL, whether a list `inputs` is accepted, free
   allowance and limits, and that 402 and 429 are what a spent allowance returns.
6. OpenAI-compatible embeddings: one real batch returns `data[].embedding`.
7. `deepseek-flash` accepts `thinking: disabled`; the gateway default works with a real key.
8. GitHub Issues API: the `X-GitHub-Api-Version: 2022-11-28` header and the `author_association` and
   `user.type` fields; a collaborator's vote counts, a stranger's does not. Thumbs links appear only with
   `feedback.enabled: true` and open a prefilled Issue.
9. The weekly digest shows Trends; a daily one does not.

**axon-template, onboarding**
10. Create the label `onboarding`. Open the form as the owner: confirm the body GitHub produces uses
    `### <label>`, the answer, `_No response_` for empty optional fields and `- [x]` / `- [ ]` for
    checkboxes (if not, fix `digest/onboarding.py` and its tests together).
11. A valid form commits `profile.yaml`, replies with the cron line and closes the Issue; an invalid
    one changes nothing. A form from a non-owner does nothing. Check a branch ruleset does not block the
    push (allow the Actions bot or use a pull request flow).
12. Paste the cron line into `digest.yml` and check the next scheduled run time.

**All**
13. `EMBED_API_KEY`, `GITHUB_TOKEN`, the bot token and the webhook URL appear nowhere in an Actions log,
    in `state/` or in `last_run.json`, also on a failed run.
14. Dependabot opens grouped PRs for the pinned actions (unchanged pins from Phase 5).

**End of Phase 6 (with the maintainer, secrets entered by him):** live setup of the Telegram bot and Slack
webhook, then the separate small public repository for the feed (Appendix C 100 and the exposures list).
