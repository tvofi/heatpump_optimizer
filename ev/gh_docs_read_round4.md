# GitHub documentation read by the round-4 seat (2026-10-19)

Read through a page fetch; the quotations are verbatim as returned.

## Events that trigger workflows
`https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows`

- `workflow_run`: "This event will only trigger a workflow run if the workflow file
  exists on the default branch."
- `workflow_run`: "You can't use `workflow_run` to chain together more than three
  levels of workflows."
- `workflow_dispatch`: "This event will only trigger a workflow run if the workflow
  file exists on the default branch."
- `GITHUB_TOKEN`: "With the exception of `workflow_dispatch` and
  `repository_dispatch`," "other `GITHUB_TOKEN`-triggered events do not create
  workflow runs at all."

The tree says the same about `workflow_run` at `origin/main`
(`.github/workflows/budget-raise-gate-rerun.yml`, header, "WHY ITS OWN FILE"):
"`workflow_run` runs THIS file from the default branch, never the pull request's
copy".

## Code scanning REST API
`https://docs.github.com/en/rest/code-scanning/code-scanning`

- List code scanning alerts for a repository, `ref`: "The Git reference for the
  results you want to list." and "To reference a pull request use
  refs/pull/<number>/merge."
- `state`: "If specified, only code scanning alerts with this state will be
  returned." (`open`, `closed`, `dismissed`, `fixed`).
- `tool_name`: "The name of a code scanning tool. Only results by this tool will be
  listed."
- `pr`: "The number of the pull request for the results you want to list."
- There is no `sha` and no `analysis_id` parameter on the alerts listing.
- Each alert's `most_recent_instance` carries `ref`, `analysis_key`, `category`,
  `commit_sha` and `state`.
- Get a code scanning analysis with `Accept: application/sarif+json`: "Instead of
  returning a summary of the analysis, this endpoint returns a subset of the
  analysis data that was uploaded", with `github/alertNumber` and
  `github/alertUrl` properties.
- List code scanning analyses: `results_count` is a required integer field (not
  defined further on the page).
