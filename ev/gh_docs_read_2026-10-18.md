# GitHub documentation read by this seat, 2026-10-18 (quoted)

## REST: List code scanning analyses for a repository
GET /repos/{owner}/{repo}/code-scanning/analyses
Query parameters, the complete list: `tool_name`, `tool_guid`, `page`, `per_page`,
`pr` ("The number of the pull request for the results you want to list."),
`ref` ("The Git reference for the analyses you want to list." ... "Pull requests use
refs/pull/<number>/merge"), `sarif_id`, `direction`, `sort`.
There is no `sha` parameter.
Source: https://docs.github.com/en/rest/code-scanning/code-scanning#list-code-scanning-analyses-for-a-repository

## Re-running workflows and jobs
"Re-runs use the privileges of the actor who initially triggered the workflow"; the
re-run uses "the same GITHUB_SHA (commit SHA) and GITHUB_REF (git ref)" of the
original event. The page says nothing about concurrency.
Source: https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs

## Changelog 2026-04-10: Actions workflows are limited to 50 reruns
"Actions workflows are now limited to 50 reruns." "if you attempt to rerun a given
workflow more than 50 times, you will get a failed check suite" "This limit includes
both full re-runs and re-runs of a subset of jobs."
Source: https://github.blog/changelog/2026-04-10-actions-workflows-are-limited-to-50-reruns/

## Concurrency (quoted by round 1: `ev/gh_docs_actions-group-concurrency.md` on `probe/design-ci-review`)
One running and one pending run per group; a newly queued run cancels the pending one.
Whether a RE-RUN attempt re-enters its run's group is not stated in the docs; the
tree measured it (rerun_group_runs_api.json, dev/audit/rca/R9-RC-PRCONTRACT.md:84-86).
