# GitHub documentation read by the round-5 seat (2026-10-19)

Read through a page fetch of
`https://docs.github.com/en/rest/code-scanning/code-scanning`; quotations as returned.

- Get a code scanning analysis, `application/sarif+json`: "Instead of returning a
  summary of the analysis, this endpoint returns a subset of the analysis data that
  was uploaded", which includes "additional data such as the github/alertNumber and
  github/alertUrl properties."
- The page states no size limit, no restriction on which analyses, and nothing on
  deleted analyses for that endpoint.
- List code scanning alerts: "The response includes a most_recent_instance object",
  which "provides details of the most recent instance of this alert for the default
  branch (or for the specified Git reference if you used ref in the request)."
- The `ref` parameter is documented as affecting `most_recent_instance`; nothing on
  the page says an alert's `state` depends on `ref` (N5-2).

The round-4 seat's `ev/gh_docs_read_round4.md` (workflow_run default-branch rule,
three-level chain limit, GITHUB_TOKEN events) is relied on as read there.
