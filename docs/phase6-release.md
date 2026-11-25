# Phase 6 release notes: commit messages and bundle repack

## Commit messages (one per repo, imperative, no secrets)
**axon-template**
```
Phase 6: Telegram, Slack and Atom delivery, optional embeddings, trends, feedback, onboarding

- delivery/telegram.py, slack.py, rss.py with shared common.py (fixed hosts, no redirects, fixed errors)
- optional embeddings (Hugging Face, OpenAI-compatible), weekly trends, feedback weights from Issues
- onboarding issue form, digest/onboarding.py, `digest.cli onboard`, onboard.yml (owner only, env-only)
- DeepSeek default deepseek-flash; digest.yml gets issues: write and the feedback step
- tests: 3 new channel suites, embeddings, trends, feedback, onboarding, hostile-text corpus replay;
  mutation sanity now 94 mutations
```
**Axon (hub)**
```
Phase 6: spec v1.7, hostile-text corpus, docs

- axon-architecture.md v1.7: Appendix C items 76 to 105 folded in, profile and onboarding sections updated
- corpus/hostile-text (onboarding, feedback, chat) with generator and drift test
- docs: setup-telegram, setup-slack, features, onboarding, first-push-phase6, phase6-release
- STATE and GUIDELINES updated; schemas regenerated; onboarding prompt (13.2) updated
```
**axon-gateway**
```
Default DeepSeek model is deepseek-flash

- src/env.ts, retirement warning text; summarize and providers tests updated
```
**axon-feed:** no changes in Phase 6.
Each message ends with:
```
Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01WR5ps91WdDmgHNHnFEwDPT
```

## Repack the project bundles (after you apply the final zips)
`axon_bundle.py` was not in this session's project files, so the exact `pack` options are not written
here (never invented). Use it the same way as after Phase 5: pack `axon-template`, the hub folder `Axon`
and `axon-gateway` (the feed is unchanged), upload the new `.bundle.partN.md` files to the project, and
remove the obsolete project files: `phase56-appendix-c-draft.md`, `phase6-appendix-c-draft.md` (hub
only) and `state-phase5-update.md`. The new spec, STATE and GUIDELINES are in the hub zip under `docs/`;
replace the project copies `axon-architecture.md`, `axon-STATE.md` and `axon-GUIDELINES.md` with them.
