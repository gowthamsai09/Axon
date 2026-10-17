# Schemas

JSON Schemas exported from the pydantic models. **Do not edit by hand.**

| File                                             | Owner (exports it)  |
|--------------------------------------------------|---------------------|
| feed-item, summary, sources, taxonomy, authority | `axon-feed`         |
| profile, task-result                             | `axon-template`     |

Update flow: in the owning repo run `python -m scripts.export_schemas --out ../Axon/schemas`,
commit the result here, then open the PR. Each code repo's CI runs
`python -m scripts.export_schemas --check hub/schemas` and fails on drift. The gateway's zod
`TaskResult` is contract-tested against `task-result.schema.json`. Hub CI checks that every
topic-slug enum across all schemas is identical.
