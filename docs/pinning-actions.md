# Pinning GitHub Actions to commit SHAs (spec section 10)

Every third-party `uses:` line ships as `actions/NAME@<pin-to-commit-sha>`. CI cannot go green
until each placeholder is replaced with a real 40-character commit SHA. Do this **before your
first push** to each repo.

## 1. Resolve the SHAs (needs `gh`, logged in; run in Git Bash / WSL / macOS / Linux)

```bash
for a in actions/checkout actions/setup-python actions/setup-node; do
  tag=$(gh api "repos/$a/releases/latest" --jq .tag_name)
  sha=$(gh api "repos/$a/commits/$tag" --jq .sha)
  echo "$a $tag $sha"
done
```

Without `gh`: `git ls-remote https://github.com/actions/checkout 'refs/tags/v*'`, pick a release tag
you trust (check the releases page, prefer one at least a couple of weeks old), and for annotated
tags use the line ending in `^{}`.

## 2. Replace the placeholders (repeat per action; SHA and TAG from step 1)

```bash
SHA=<40-char sha>; TAG=<tag>
sed -i -E "s|(uses: actions/checkout)@<pin-to-commit-sha>.*|\1@${SHA}  # ${TAG}|" .github/workflows/*.yml
```
(macOS: `sed -i ''`.) Do the same for `actions/setup-python` and `actions/setup-node`.
The `# TAG` comment lets Dependabot (github-actions ecosystem) keep the pins current.

## 3. Verify

```bash
grep -rn "pin-to-commit-sha" .github || echo "all pinned"
```
The workflow-lint test (`tests/test_workflows.py` / `test/workflows.test.ts`) accepts either
the placeholder or a 40-hex SHA and rejects floating tags such as `@v4`.
