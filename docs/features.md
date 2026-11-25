# Optional features (all off by default)

Every section below is optional in `profile.yaml`. A profile without it stays valid.
Nothing here has run against a real service; the checks are in `first-push-phase6.md`.

## Atom feed (`delivery.channel: rss`), Appendix C 95
Each run adds one entry to `rss/feed.xml` on the `state` branch (at most 50 entries; a rerun replaces its
own entry). No GitHub Pages is used: on GitHub Free, Pages is available for public repositories only.
The file is readable by people with read access to your private repository, and an ordinary feed reader
cannot sign in to it. Use it if you can fetch it with a token or copy it elsewhere.

## Semantic matching (`embeddings`), Appendix C 96
```yaml
embeddings:
  enabled: true
  provider: huggingface        # or openai_compatible (then set base_url, https, no query)
  model: thenlper/gte-large
  weight: 0.25
```
Secret: `EMBED_API_KEY` (a Hugging Face token with Inference Providers access, or your provider's key).
DeepSeek has no embeddings endpoint. Cost is bounded: at most `max_items` candidates (default 50, max 200),
batches of 16, 1500 characters per text. If anything fails the run falls back to keyword matching and says
so in a fixed warning. Vectors are cached in `state/embeddings/` for 7 days.

## Weekly trends (`trends`), Appendix C 97
```yaml
trends:
  enabled: true
  llm_labels: false            # true adds a one-line AI label per trend (uses your summarizer key)
```
Only weekly digests show a Trends section. Clusters come from the last 7 days of the shared feed by
entity first, tag second, at least 3 stories each. Labels, when on, go through the same injection rules
and validation as summaries, and a flagged or failed label is simply left out.

## Feedback weights (`feedback`), Appendix C 98
```yaml
feedback:
  enabled: true
```
The HTML e-mail gets thumbs links that open a prefilled Issue (`item:<id> vote:up`). The `digest`
workflow reads open Issues from you or a collaborator, counts strict vote lines only, closes them and
moves per-topic weights by a small bounded amount that halves every 30 days. Other Issues are ignored.
Needs `issues: write` on the workflow (already set in `digest.yml`).
