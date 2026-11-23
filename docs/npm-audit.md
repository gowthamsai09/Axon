# Reviewing `npm audit` findings (P5.12, Appendix C 87)

**Status: not run in Phase 5.** The build sandbox could not create a lockfile (npm failed internally with
`Cannot read properties of null (reading 'edgesOut')`), so there is no fresh result. The last known state (Phase 3 and 4
sandbox, 2026-10-26 and 2026-10-29): 0 production findings, 3 findings (2 moderate, 1 high) in dev tooling bundled with
`wrangler`. At the time of writing the latest `wrangler` on npm was 4.166.0 (the repo pins 4.152.0). That is a fact about
the registry, not a claim that upgrading fixes anything.

## Procedure (run on your laptop, in `axon-gateway`)
```powershell
npm ci
npm audit --omit=dev        # production dependencies: must be 0 findings, otherwise fix first
npm audit                   # everything, to see the dev tooling findings
npm outdated wrangler
```
1. A production finding (hono, jose, yaml, zod) blocks release: upgrade that package alone, run the full checks.
2. Dev-only findings (wrangler and its tooling, vitest, eslint) do not ship in the Worker bundle. Upgrade only if a fixed version
   exists AND all of these pass with it: `npm run typecheck; npm run lint; npm test; npm run prompt:check` and
   `npx wrangler deploy --dry-run` (bundle size stays well under 3 MB compressed; it was 215 KiB gzip).
3. Upgrade `wrangler` and `@cloudflare/workers-types` together (workers-types is tied to the wrangler/workerd version).
   Re-run one `wrangler dev` smoke test, because mocked tests cannot see workerd differences (Appendix C 74).
4. Record the result (counts before and after, versions) in STATE. Do not use `npm audit fix --force`.
5. Dependabot (weekly, grouped) will open the upgrade PRs after the first push; the same checks decide whether to merge.
