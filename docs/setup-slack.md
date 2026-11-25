# Slack delivery

Spec: Appendix C 89. Nothing here has run against real Slack (first-push check 1).

## What you need
An **incoming webhook** for one channel: Slack app settings > Incoming Webhooks > activate > "Add New
Webhook to Workspace". The URL looks like `https://hooks.slack.com/services/T.../B.../<secret>`. It is a
secret: anyone holding it can post to the channel. Do not commit it or paste it in an Issue.

## Set it up
1. `profile.yaml`: `delivery.channel: slack`.
2. Repository secret `SLACK_WEBHOOK_URL` (and `LLM_API_KEY`).
3. Dry run: `python -m digest.cli run --dry-run --outbox .local\outbox` writes `.txt` files.
4. Run the `digest` workflow by hand once.

## Rules the code enforces
- Only `https://hooks.slack.com/services/T<id>/B<id>/<secret>` is accepted (no GovSlack, no query, no
  extra path, ASCII only).
- Untrusted item text becomes one line; `&`, `<`, `>` are escaped, so an item cannot form `<!channel>`,
  `<@user>` or a link. `*`, `~` and a backtick are swapped for look-alikes (mrkdwn has no escape).
- Messages are at most 3500 UTF-16 units; a long digest is split at item boundaries.
- A revoked webhook (404 or 410) gives a "no longer exists" message; the URL is never printed.

Not verified: whether Slack unfurls links in webhook posts, and its real size limit for webhooks.
