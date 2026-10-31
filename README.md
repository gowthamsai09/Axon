# Axon

Axon is a highly customizable AI-community digest. It is **Git-native and bring-your-own-key**:
a shared, LLM-free feed (collect, dedupe, tag, score) is published as static JSON; each user runs
a private pipeline repo with their own GitHub Secrets to summarize and deliver a personalized
digest; and a small Cloudflare Worker exposes the same core to other agents over A2A and MCP
(Tier 1 data, Tier 2 caller-key summaries, Tier 3 owner digest runs). The operator never stores
user keys.

| Repo | Role |
|---|---|
| [axon-feed](https://github.com/gowthamsai09/axon-feed) | Plane 1: collectors, pipeline, published feed |
| [axon-template](https://github.com/gowthamsai09/axon-template) | Plane 2: per-user digest pipeline (use as template) |
| [axon-gateway](https://github.com/gowthamsai09/axon-gateway) | Plane 3: Cloudflare Worker, A2A + MCP |

## Status

Phases 0 to 4 are built and tested locally (feed, user pipeline, gateway Tier 1 and 2, gateway Tier 3).
Nothing is deployed yet and the first push has not happened: real GitHub Actions, Pages, email delivery,
the GitHub App and a live provider call are still unverified. Next: Phase 5 (hardening), then Phase 6 (polish).
Details and the first-push checklist are in [STATE](docs/axon-STATE.md).

## Documents

- **Spec (single source of truth):** [docs/axon-architecture.md](docs/axon-architecture.md), plus the
  accepted changes in [Appendix C, Phase 3](docs/appendix-c-phase3.md) and [Phase 4](docs/appendix-c-phase4.md)
  (to be folded into the spec)
- **Project state and next steps:** [docs/axon-STATE.md](docs/axon-STATE.md)
- **Engineering guidelines:** [docs/axon-GUIDELINES.md](docs/axon-GUIDELINES.md)
- **JSON Schemas** exported from the pydantic models: [schemas/](schemas/)
- **Pinning GitHub Actions:** [docs/pinning-actions.md](docs/pinning-actions.md)
- **Finding feeds for blogs:** [docs/source-discovery.md](docs/source-discovery.md)
- **Setting up the GitHub App and Tier 3:** `docs/github-app-setup.md` in `axon-gateway`

## Security promise

Zero key custody: the operator never stores user LLM or email keys. Scraped content and inbound agent
messages are treated as untrusted data, never as instructions. See spec sections 1 and 10.