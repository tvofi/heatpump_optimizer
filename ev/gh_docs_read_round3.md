# GitHub docs read by the round-3 seat, 2026-10-18

## REST: workflow jobs (docs.github.com/en/rest/actions/workflow-jobs)
- `filter`: default `latest`; values `latest`, `all`. "latest returns jobs from the most
  recent execution of the workflow run."; "all returns all jobs for a workflow run,
  including from old executions of the workflow run."
- The job `status` enum includes `queued`, `waiting`, `requested` and `pending`.
- The page does NOT say whether a job still waiting on its `needs` is listed. So
  "the jobs API lists a job only once it is queued" (DESIGN-P2 4.1, R-7, the premise of
  `gate_model.judging`) is undocumented: a platform fact to measure, not a cited one.
- Nothing on re-running a job while its run is in progress.

## Re-running workflows and jobs (docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs)
- "A workflow run can be re-run a maximum of 50 times." (full and partial re-runs count);
  re-runs are available "up to 30 days after its initial run".
- "Re-runs use the privileges of the actor who initially triggered the workflow"; a
  re-run uses the same commit SHA and git ref as the original event.
- Nothing on concurrency, nothing on dependents of a re-run job, nothing on re-running
  an in-progress run.
