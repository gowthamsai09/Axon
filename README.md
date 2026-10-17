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

- **Spec (single source of truth):** [docs/axon-architecture.md](docs/axon-architecture.md)
- **JSON Schemas** exported from the pydantic models: [schemas/](schemas/)
- **Phase 0 checklist:** [docs/phase-0-checklist.md](docs/phase-0-checklist.md)
- **Pinning GitHub Actions:** [docs/pinning-actions.md](docs/pinning-actions.md)
- **Finding feeds for blogs:** [docs/source-discovery.md](docs/source-discovery.md)

Status: Phase 0 (scaffolding). Nothing is deployed.
