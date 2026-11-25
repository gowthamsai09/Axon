# Telegram delivery

Spec: Appendix C 88. Nothing here has run against the real Telegram API (first-push check 1).

## What you need
- A bot from BotFather (open a chat with `@BotFather`, send `/newbot`, follow the prompts). BotFather gives
  you a token that looks like `123456789:AA...`. Treat it as a password.
- The chat id. Send any message to your bot, then open
  `https://api.telegram.org/bot<token>/getUpdates` in a browser **on your own machine** and read
  `message.chat.id`. For a public channel use `@channelname` (the bot must be an admin there).
  Never paste the token into an Issue, a chat or `profile.yaml`.

## Set it up
1. In `profile.yaml` set `delivery.channel: telegram`. Keep `delivery.depth` and `max_items` modest:
   long digests are split into several messages (at most 4000 UTF-16 units each, one second apart).
2. In the repository: Settings > Secrets and variables > Actions > New repository secret:
   `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` (and `LLM_API_KEY`).
3. Try it locally without sending: `python -m digest.cli run --dry-run --outbox .local\outbox` writes the
   messages to `.local\outbox` as `.md` files.
4. Run the `digest` workflow by hand once.

## What can go wrong (messages never show the token)
| Message names | Meaning |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Telegram answered 401 or 404: the token is wrong or revoked |
| the bot may not post | 403: you never started the chat, or the bot was removed or blocked |
| `TELEGRAM_CHAT_ID` | 400: wrong chat id |
| a wait | 429: the run waits for the time Telegram asks for (at most 30 s), then retries |

If message 2 of 3 fails, message 1 is already delivered; the items are not marked seen and the next run
sends the digest again (the error says how many were sent).
