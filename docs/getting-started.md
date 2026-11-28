# Getting started with Axon

From zero to your first personal digest. About 20 to 30 minutes, free platforms only. No credit card
is needed for GitHub, Cloudflare (only for agent access) or the Axon feed. Your LLM provider (DeepSeek
or Hugging Face) is the one place that may ask for billing: **a digest of 10 items cost under 0.01 USD
for two runs** in the maintainer's live test (observed, DeepSeek `deepseek-flash`).

![Overview](img/overview.png)

## What you will have at the end

- A **private** GitHub repository that you own, created from the Axon template.
- A scheduled GitHub Actions job that reads the shared Axon feed, ranks it by your interests,
  summarises the top items with **your** key and sends you the digest (email, Telegram, Slack or an
  Atom file).
- Optionally, a way for other agents to ask for your digest (Tier 3).

Nobody, including the Axon maintainer, ever holds your keys. They live in your repository's secrets.

## Before you start

| Need | Notes |
|---|---|
| GitHub account | A personal account is simplest. The onboarding form only works for personal-account repos |
| An LLM key | DeepSeek, Hugging Face or any OpenAI-compatible endpoint |
| A delivery channel | Email (SMTP, for example a Gmail app password), Telegram bot, Slack incoming webhook, or none (Atom file) |

Never paste a key, token or password into an Issue, a form, a chat or `profile.yaml`.

## Step 1: Create your repo from the template

1. Open `https://github.com/gowthamsai09/axon-template`.
2. **Use this template** > **Create a new repository**.
3. Owner: you. Visibility: **Private**. Name: for example `axon-digest`.

This is a template copy, not a fork, so your history and state stay private. Because it is a snapshot,
later template fixes do not reach your repo automatically; copy changed files by hand when you want them
(Appendix C 110).

## Step 2: Tell Axon what you care about

Pick **one** of three ways.

**A. Issue form (no terminal).** In your repo: Issues > New issue > **Onboarding**. Create the label
`onboarding` first if it is missing. Fill the form, tick the "no keys" box and submit. The `onboard`
workflow either lists fields to fix or commits `profile.yaml`, closes the Issue and replies with a cron
line and the secret names to add. Paste the cron line into `.github/workflows/digest.yml` under
`schedule:` yourself (a workflow cannot edit workflow files).

**B. Command line.**
```powershell
git clone https://github.com/<you>/axon-digest; cd axon-digest
pip install -r requirements.txt
python -m digest.cli init
```

**C. Edit `profile.yaml` by hand.** The part you will touch most:

```yaml
interests:
  topics: [open-source-llms, agents-tooling, rag, research-papers]
  follow_entities: ["Qwen", "LangChain", "github:ollama/ollama"]
  keywords_include: ["quantization", "local inference"]
  keywords_exclude: ["crypto", "funding round"]
delivery:
  channel: email            # email | telegram | slack | rss
  frequency: daily          # daily | weekly
  send_time_local: "07:30"
  timezone: "Asia/Kolkata"
  depth: brief              # headlines | brief | detailed
  max_items: 10
summarizer:
  provider: deepseek        # deepseek | huggingface | openai_compatible
  model: deepseek-flash
```

Validate it: `python -m digest.cli validate-profile`.

The 16 topic slugs are listed in [call-the-agent.md](call-the-agent.md). Schedule times are in UTC in
GitHub cron: `0 2 * * *` is 07:30 in India.

## Step 3: Add secrets and a variable

Repository > Settings > Secrets and variables > Actions.

| Name | Type | Used for |
|---|---|---|
| `LLM_API_KEY` | secret | Your summariser key |
| `SMTP_USER`, `SMTP_PASS`, `MAIL_TO` | secrets | Email |
| `SMTP_HOST`, `SMTP_PORT` | **variables** | Email server (465 worked for Gmail) |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | secrets | Telegram ([setup guide](setup-telegram.md)) |
| `SLACK_WEBHOOK_URL` | secret | Slack ([setup guide](setup-slack.md)) |
| `FEED_BASE` | **variable** | `https://gowthamsai09.github.io/axon-feed/feed` |

Note the `/feed` at the end: the shared feed is served under that path.

The template README has the full list (including the optional `LLM_API_KEY_FALLBACK` and `EMBED_API_KEY`). If a
name is wrong the run fails with a clear, secret-free message that names the setting.

## Step 4: Dry run on your machine (optional)

```powershell
python -m digest.cli run --profile profile.yaml --feed <path-to-feed-out> `
  --state-dir .local\state --outbox .local\outbox --dry-run --no-llm
```

`--no-llm` needs no key and uses the extractive fallback. `--outbox` writes the messages to files so you
can read them instead of sending them.

## Step 5: First real run

Repository > Actions > **digest** > Run workflow. Within a couple of minutes you should receive the
digest. Look at the run log: secrets print as `***`.

What a good first run looks like (maintainer's run, observed): 652 candidates in, 10 items out, 17 LLM
calls (the validator retries over-length one-liners), under 0.01 USD.

If it did not arrive:

| Symptom | Likely cause |
|---|---|
| Run is red with a message naming a secret | That secret is missing or wrong |
| Telegram 403 | You never sent your bot a message first |
| Email fails | Provider needs an app password; check port (465 worked for Gmail) |
| Digest is empty | `keywords_exclude` or topics too narrow, or all items were already sent (`seen`) |
| Soft error on the `state` checkout in the very first run | Expected: the `state` branch did not exist yet |

## Step 6: Let it run daily

The `digest` workflow runs on your cron. GitHub disables scheduled workflows after 60 days without
activity in **public** repositories only (spec Appendix C 80), so your private repo is not affected; the
`keepalive` workflow is a precaution that re-enables `digest` monthly. State (what was already sent, summary caches, feedback weights, the Atom file) lives on an orphan
`state` branch in your repo.

## Optional features (all off by default)

Details in [features.md](features.md).

| Feature | Switch | Note |
|---|---|---|
| Atom channel | `delivery.channel: rss` | Readable only with access to your private repo |
| Semantic matching | `embeddings.enabled: true` | Needs `EMBED_API_KEY`; falls back to keywords if anything fails |
| Weekly trends | `trends.enabled: true` | Only weekly digests show Trends |
| Thumbs feedback | `feedback.enabled: true` | HTML email only; votes arrive as Issues from you or a collaborator |

## Let agents call your digest (Tier 3)

Skip this unless you want other agents to ask for your digest. Everything is optional and under your
control: `agent_access.allow_inbound_agents`, `allowed_modes`, a daily cap
(`max_tier3_runs_per_day`) and `allow_owner_channel` are in `profile.yaml`.

1. **Create a GitHub App** on your account: Settings > Developer settings > GitHub Apps > New.
   Untick **Webhook > Active**. Repository permissions: Actions **read and write**, Contents
   **read-only**, Metadata **read-only**. Installable only on this account. Install it on your digest repo only.
2. Operate your own gateway **or** use the shared one. The shared gateway is
   `https://axon-gateway.gowthamsaiyadlapalli1234.workers.dev`; registration there only works for a repo
   on which the maintainer's GitHub App is installed. To run your own, follow the gateway's
   `docs/github-app-setup.md` (Cloudflare account on the free plan; the App private key is stored as a
   Cloudflare **Secret**, never a plain variable).
3. In your digest repo set the variable `GATEWAY_URL` to the gateway URL, exactly as the gateway's
   `PUBLIC_URL`.
4. Run the **register** workflow. It proves your repo's identity to the gateway with GitHub's OIDC token
   (no secrets). Expect `Registered <repo> as ag_...`.
5. Run **issue-token** with a label and a lifetime (1 to 365 days, default 90). Open the run's job
   summary, copy the `axn_...` token **once**, then delete the run. Only a SHA-256 hash is stored.
6. Give the token to the agent you trust. It calls the gateway as in [call-the-agent.md](call-the-agent.md).
7. To revoke, run **revoke-token** with the `tk_...` id. Revocation is immediate in the location that
   handled the change and may take up to about 60 seconds elsewhere (KV propagation; the figure comes
   from third-party summaries of Cloudflare's docs, not a Cloudflare primary page).

## Security basics you should know

- Keys live in GitHub secrets and in memory during a run. They are not written to `state/`, logs or
  `last_run.json`.
- Scraped content and inbound agent messages are treated as untrusted data in every code path.
- Workflows use least-privilege `permissions:`, pass inputs only through `env:`, pin third-party actions
  to commit SHAs and refuse to act in the template repo itself.
- Summaries link to the source, name the model that wrote them, and are checked: only the source URL is
  allowed and figures must appear in the source text.

## Where to read more

- Architecture: [../ARCHITECTURE.md](../ARCHITECTURE.md)
- Calling Axon from an agent: [call-the-agent.md](call-the-agent.md)
- Optional features: [features.md](features.md)
- Onboarding form details: [onboarding.md](onboarding.md)
