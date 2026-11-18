# `prepare_baseline.sh`

- `prepare_baseline.sh` — builds a round's audit baseline: a git-archive
  export finders work in, one worktree per mutating finder, briefs copied in.
  When: starting a round. Refusal: an archive run from a `git archive` copy
  fails the `recorded_at` check on every mutant, baseline included — the M0
  null run attributes that to the runner, not the findings.
