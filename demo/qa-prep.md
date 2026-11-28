# Q&A preparation

Grounded answers for the likely questions. Each answer says where it comes from. Rules for the call:

- Say **verified live**, **tested with mocks** or **not run**. Never round up.
- Free-tier numbers below are marked **unverified** unless a primary page was checked on the day. If asked,
  say "the figures in my notes are from a dated search; check the provider's page for today's numbers."
- Do not guess about competitors. Compare on design properties, not on claims about products you did not test.
- If you do not know: "I have not measured that. I would find out by X."

Abbreviations: Spec = `axon-architecture.md`; C = Appendix C item; STATE = `axon-STATE.md`.

---

## A. The big one

### Why is Axon a "personal agent"? Isn't it just a cron job running Python?

**Short, honest answer.** "Partly, yes. The scheduled digest is a workflow: a cron trigger runs fixed Python.
Calling that an autonomous agent would overstate it. What makes Axon agent-*facing* is the A2A and MCP surface:
other agents can discover it from an Agent Card, call it, poll a task, and cancel it. And it is *personal*
because it acts on one person's profile, one person's key and one person's history."

**The distinction, in one line.** Anthropic's "Building effective agents" separates *workflows*, where code
paths are predefined, from *agents*, where the model dynamically directs its own process and tool use. By that
definition, the digest is a workflow. I use "personalised, agent-callable digest service" because it is accurate.

**What the cron job does not give you** (so it is more than `0 2 * * *`):
- A discoverable contract (Agent Card, MCP tools, JSON schemas) so a machine can use it without reading docs.
- Per-caller authorisation: tokens that are scoped, labelled, expiring, revocable and stored only as hashes,
  with identity proved through GitHub OIDC rather than a shared secret.
- An asynchronous task model (submitted, working, completed, rejected, failed, canceled) over a stateless gateway.
- Owner policy that an inbound agent cannot override (`allow_inbound_agents`, `allowed_modes`, a daily cap).
- Validation of model output and a hostile-input defence, because both inputs and outputs are untrusted.

**What would make it a real agent**: a model choosing sources, deciding what to read in full and when to
re-query, with a budget and a stop condition. The spec defers natural-language Tier 3 (C 102) because it
would need an LLM on the owner's key. I would add that only if the workflow proves too rigid.

**If pressed: "so why call it an agent at all?"** "I do not, in the sense of autonomy. I describe it as a
digest service that agents can call, and that a person can use directly."

---

## B. What and why

### What problem does it solve?
Too many sources, too little time, and a risk of both information overload and missing something relevant.
It reduces a large daily flow to a short ranked digest in your own channel. (Observed: 652 candidates to
10 items in one run.)

### Why the name Axon?
An axon carries a signal from a neuron's cell body to other cells; Axon relays signal from many sources to a
person and to agents. *This is the rationale offered for the demo; the spec does not record one. State it as your idea.*

### How much time does it save?
Only claim what you measured. Observed: hundreds of candidates per run reduced to ten, no repeats, one
message at a set time. Time saved depends on your habits; "I have not timed it rigorously" is a fine answer.
To measure: time yourself reading the same sources for a week, then time the digest for a week.

### Why these sources and not others?
Verified stable feeds, plus an authority score per source (spec 5.3, `authority.yaml`). Reddit is excluded
because robots.txt disallows our User-Agent (probe 2026-10-16). Anthropic, Meta, Mistral, Qwen and DeepSeek
blogs are on a research list with no verified feed, and the rule is never to add a guessed URL.

### Can I add my own sources?
Yes, per user: `sources.extra_rss` in `profile.yaml`, fetched through the SSRF guard. For the shared feed,
a source must be probed and given an authority score; a new one starts at 0.50 and is capped at 0.60 for 30 days.

### Can it cover topics other than AI?
Not without work. The taxonomy (16 topics, about 29 entities) and the source list are AI-specific. The
architecture is not, but the sources, taxonomy and prompt would change.

### How does it keep me updated without more noise?
It runs on your schedule, never repeats an item (delivered ids are kept), ranks by your interests, filters
by your exclusions, and optionally learns from thumbs votes. It is not real time: the feed refreshes every 3 hours.

---

## C. Cost, platforms and limits

### What does it cost?
GitHub, Cloudflare and the shared feed are free-plan only; no card was needed on Cloudflare in the maintainer's setup (C 117).
The only variable cost is your own LLM key. Observed: **under 0.01 USD for two digest runs** with DeepSeek `deepseek-flash`
(C 112). A longer digest or a pricier model costs more. Watch cost and latency before raising `max_items`.

### What do the free tiers cap?
All **unverified for today**; from the spec, Appendix B item 47 (2026-10-25), third-party summaries:

| Platform | Recorded limit |
|---|---|
| Cloudflare Workers free | 100,000 requests per day; 10 ms CPU per request; 50 subrequests per request; 3 MB compressed bundle |
| Cloudflare KV free | 100,000 reads and 1,000 writes per day; 1 write per second per key; 60 s minimum TTL |
| GitHub Actions on private repos | Free minutes exist but I did **not** re-verify the current number (C 68). Check before quoting |
| GitHub Pages | Free for public repos on GitHub Free; private-repo Pages is paid (C 114) |

Observed here: bundle 1166 KiB (216 KiB gzip); median CPU about 4.6 ms; 83 requests used 133 subrequests.
p99 CPU was **not measured**, and the free CPU limit is 10 ms.

### How does it scale?
- **Shared feed:** reads are static files on Pages and edge-cached, so more readers cost almost nothing.
- **Per-user pipeline:** each user runs in their own repo and minutes. Scaling is horizontal by design.
- **Gateway:** Tier 1 and 2 are stateless. The limits above and per-IP rate limits are the ceiling. Tier 3 is
  one Actions run per call, so the real limit is Actions minutes and the owner's daily cap.
- **Not tested:** load. All real traffic so far is one person. I would say "designed to scale per user, not load-tested."

### What if GitHub or Cloudflare changes its free plan?
That is a real risk of any free-platform design. Each plane is replaceable: static JSON can be hosted
anywhere, and the pipeline is a Python CLI. The decisions record (Appendix C) lists the assumptions to revisit.

### What happens when the free rate limit is hit?
HTTP 429. Observed: 70 POSTs in a row gave 61 successes and 9 limits. The counters are per Cloudflare location and approximate.

---

## D. Privacy and keys

### Who sees my API key?
Nobody but you and your provider. Pipeline: it sits in your repo's GitHub secrets. Gateway Tier 2: header
only, in memory for one request, never stored, logged, cached or returned. The gateway returns an error
rather than process a key found in a request body.

### Is that proven?
Partly. Tests assert it; one real Tier 2 call confirmed the key did not come back; the Cloudflare edge
log shows metadata only. Caveat: my test key crossed a corporate proxy that may inspect HTTPS, so I used a dedicated
key and deleted it. For your own use, create a dedicated key with a spend limit.

### What data does Axon hold about me?
Gateway: a repo registration, and an owner token as a SHA-256 hash with label and expiry. Your repo: your
profile, delivered item ids and caches, in a private repo you own. The shared feed holds no user data.

### Is my digest private?
In a private repo, yes, and delivered to your own channel. The Atom `rss/feed.xml` sits on your private
`state` branch, so a normal feed reader cannot read it (C 95, 114). If you make anything public, items,
summaries and the model name become public.

### Why a GitHub App for Tier 3 and not my personal token?
The App has narrow permissions (Actions read and write, Contents read, Metadata read), is installed on one repo only, and
can start workflows but not push code. Installation tokens are minted per use, scoped to that repo, and kept
in memory only.

---

## E. Quality and trust

### Do the summaries hallucinate?
They can, which is why there are checks: the model sees only the item text; the output must fit a strict schema;
only the source URL may appear; figures in the summary must appear in the source; a suspected injection
produces a snippet instead. Each item links to its source and names the model. Not proven: `evals live`
(scoring on a real model) has not been run, and the human-checked evaluation set is yours to complete (12 seed cases).

### What stops a malicious article from taking over my digest?
Treat scraped text as data. The prompt tells the model to ignore instructions inside the content, the model
reports an `injection_flag`, validation rejects extra links, and a shared injection corpus runs in CI in both
code repos. Honest limit: no filter is perfect. Output cannot execute anything: the pipeline sends text to your channel.

### What if the LLM provider is down?
A router tries the primary, trips a breaker after 3 failures, uses a fallback if you configured one, then falls
back to an extractive snippet, labelled as such. One bad source or item never fails a run.

### Why DeepSeek by default?
It is cheap and OpenAI-compatible, and I tested it live. Hugging Face and any OpenAI-compatible endpoint also work.
The summarizer prompt is fixed and shared, so output style is consistent across providers.

### Did you measure summary quality across models?
No. `deepseek-flash` often exceeds length limits and needs retries (17 calls for 10 items). I have not
compared providers for quality.

---

## F. Architecture choices

### Why GitHub Actions rather than a server?
Free, scheduled, private and auditable; your repo is your deployment. The cost is cold-start latency
(a digest takes about a minute or two) and a platform dependency.

### Why a template, not a fork?
A fork of a public repo cannot be private on the free plan, and would tie your history to mine. A template
copy is private and independent. Trade-off: it is a snapshot, so template fixes do not reach existing repos automatically (C 110).

### Why is the gateway stateless?
Fewer things to leak or keep consistent. It reads GitHub for task state and keeps only registrations and
token hashes in KV. Revocation can lag up to about 60 seconds across Cloudflare locations (the figure is from third-party summaries).

### Why both A2A and MCP?
They solve different adoption paths: A2A is agent-to-agent with task semantics; MCP is how many tool-using
assistants connect to tools. Both are thin adapters over one core, so supporting both costs little.

### Which versions?
A2A 0.3.0. A2A v1.0 has shipped and is a breaking redesign; migrating is a recorded open item (C 71). MCP
2026-07-28 (stateless) and 2025-11-25 for older clients.

### Why static bearer tokens and not OAuth for MCP?
OAuth needs an authorization server, which is out of scope for a free-tier design (C 72). Clients that insist on
OAuth discovery will not authenticate automatically. A client that lets you set an `Authorization` header will.

### Why no CORS?
Agents call server to server. A browser page should never be able to make a call that carries a user key through the Worker.

### Why TypeScript for the gateway and Python for the pipeline?
Workers run JavaScript well; the pipeline benefits from Python's text and data libraries and from pydantic typing.
Both sides share JSON Schemas from the hub and a byte-identical prompt, checked in CI.

### Could someone else run their own gateway?
Yes. Everything is in `axon-gateway`: a Cloudflare account on the free plan, a KV namespace, a GitHub App, a
`wrangler.toml` with your URL, and the deploy workflow. See `docs/github-app-setup.md` and `docs/deploy.md`.

---

## G. Honesty about status

### What is verified, and what is not?
**Verified live:** feed collection and Pages; Telegram, Slack, email; the onboarding form; feedback links and
weights; the Atom channel; keepalive; gateway deploy; Tier 1 and 2; Tier 3 over A2A (register, token, start,
poll, cancel, revoke).
**Not run:** Tier 3 over MCP; the modern MCP `tools/call` with headers; a third-party A2A or MCP client;
p99 CPU and per-request subrequests; revoke delay; `Retry-After` on a real 429.
**Mocked only:** weekly trends, embeddings, stale-source Issues, `evals live`, the failure notice.

### What went wrong while building it?
Three real examples: Cloudflare's runtime rejects `redirect: "error"`, which would have broken every live Tier 2
call, but mocks hid it (C 74); the gateway rejected a `null` the template wrote on the first live Tier 3 run
(C 124); a fake token-shaped test string was flagged by GitHub secret scanning (C 109). All fixed with tests.

### What is deliberately not built?
A public feed repo for RSS readers (C 114); natural-language Tier 3 (C 102); A2A v1.0 (C 71); MCP OAuth metadata (C 72).

### What is next?
Tier 3 over MCP, measurements, a real client test, docs fixes, narrowing the Cloudflare deploy token, and housekeeping (STATE section 7).

---

## H. Awkward ones

### Is this legal? Are you copying other people's content?
The feed stores titles, links, short snippets and capped excerpts; summaries link to the original. It
respects robots.txt (which is why Reddit is out) and rate-limits itself. I am not a lawyer; read each source's terms before
broadening it.

### Why open source?
Apache-2.0 on all four repos (C 106). The design is easier to trust when you can read the security rules and the tests.

### Why should I trust a gateway run by one person?
Do not trust it with your key: Tier 1 needs none, Tier 2 uses a header-only key you can scope and delete, and you
can run your own gateway. Tier 3 only works for a repo you control, and an owner can revoke access.

### Can a bad agent abuse my Tier 3 access?
Only with your token. Controls: scoped label and expiry (up to 365 days, default 90), at most 10 active tokens,
a daily cap (default 5 runs), `allowed_modes`, `allow_inbound_agents`, and you can revoke at any time. A bad agent could still waste a few
Actions minutes and your LLM spend within those caps.

### Would a person need a GitHub account to use it?
Yes, for the pipeline. Tier 1 and 2 over the gateway need only an agent that can send HTTP requests.

### Are there other digest services doing this?
Many exist, and I did not test them, so I will not compare claims. What Axon aims for: free platforms,
**your own key**, your own private repo, an open and testable pipeline, and a machine-callable interface.
If someone else's product fits you better, use it.

### Is it production-ready?
For one person's daily use on free platforms: it has run live. For many users: not load-tested, one Tier 3
path unverified, free-tier assumptions need re-checking. Say exactly that.

---

## Questions to ask the audience (if the room goes quiet)
- Which sources do you read that I should consider, and do they have a verified feed?
- Would you rather get this by Telegram, Slack, email or through your own agent?
- Which of your agents would call it, and with which protocol?
