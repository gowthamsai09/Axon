# Pinned GitHub Actions (resolved 2026-11-01)

All third-party actions are pinned to commit SHAs in every repo (spec 10.1, Appendix C 76).
Method: `git ls-remote --tags https://github.com/<action>.git` (peeled `^{}` entries), because
`api.github.com` rate-limited the unauthenticated sandbox. Commit dates read from shallow clones.
The checkout and setup-python SHAs equal the pins already in `axon-feed`, which cross-checks the method.
Not the newest majors on purpose (v7 exists); Dependabot (grouped, weekly) proposes updates.

| Action | Tag | Commit SHA | Commit date |
|---|---|---|---|
| actions/checkout | v6.1.0 | d23441a48e516b6c34aea4fa41551a30e30af803 | 2026-07-16 |
| actions/setup-python | v6.3.0 | ece7cb06caefa5fff74198d8649806c4678c61a1 | 2026-06-23 |
| actions/setup-node | v6.5.0 | 249970729cb0ef3589644e2896645e5dc5ba9c38 | 2026-07-13 |

Every pin is more than 14 days old on the resolution date. To re-resolve or bump, run
`python scripts/pin_actions.py --check <repo>/.github/workflows` (read-only: reports unpinned lines and
SHAs that no longer match the table) or edit `PINS` in the script and run it with `--apply`.
