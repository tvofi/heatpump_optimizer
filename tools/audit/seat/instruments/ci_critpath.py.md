# `ci_critpath.py`

- `ci_critpath.py` — one workflow run's critical path from its job and step
  timestamps (each job's queue, duration and longest step), its `needs:` read
  from the run's own head, and a counterfactual holding every queue and
  duration fixed: `--drop-edge NEED:JOB`, `--delete-job JOB`, `--charge
  JOB=SECONDS` (the bare cost, stated by the caller). `--workflow F --last N`
  prints median and p90 over the last N runs. The CI design archive's phase-2
  method generalised (tag `archive/probe/design-ci-rev4`), and
  `dev/audit/harnesses/r10_critpath_archive_parity.py` holds it to that
  method's V1 numbers run for run. When: a job-graph change states the wall
  it buys before it is built. Refusal: an edge the workflow does not have, a
  needs cycle, or a run past `--max-reads` API reads; jobs and needs are
  cached per run id and head, so a re-run reads only `--last`'s run list.
