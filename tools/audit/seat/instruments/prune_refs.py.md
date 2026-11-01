# `prune_refs.py`

- `prune_refs.py` — reconciles the remote branch refs down to main plus a few
  development branches at programme closure, archive-as-tags first. When: the
  R9-CLOSURE-BRANCHES step 4 (prune by rule), and any future round's closure.
  Four rules -- keep `main` and any ref whose pull request is OPEN; delete a
  ref already merged into main, and an unmerged `handoff/*` ref whose pull
  request merged (a same-named PR, or the branch of a roster group the roster
  records `done`); enumerate the residue (no PR, or a closed-unmerged one) for
  an individual disposition, archived-and-deleted by default. Refusals: a plan
  that would act on `main`, and any `verdict/*` deletion while `--verdicts-drained`
  is unset (the bus watcher reads those refs). Every tag is created before any
  deletion, and `--archive-scope none` deletes nothing, so no tip is ever
  dropped unarchived; `--dry-run` (the default) prints the plan and writes
  nothing. `--self-test` drives the classifier, the planner, the precedence and
  the ordering offline, then the push arm and `--topic` against a throwaway bare remote.

  Writes by `--via push` (default): archive tags as `<sha>:refs/tags/archive/<name>`
  refspecs in chunks of 100, a read-back of the remote's tags, then
  `git push --delete` in the same chunks, aborting at the first refusal and
  refusing before any delete when a ref lacks its tag at its own sha; zero API
  calls (`--via api` is the old one-write-per-ref arm, 2N for N refs). Keeps,
  beyond the four rules: `claude/*`; `design/` and `design-verdict/` refs of a
  group `--roster-file` records not done; a tip younger than 6 h, a `dispatch/*`
  tip younger than 24 h, and a tip whose age cannot be read. `--topic T` limits
  the plan to one topic's refs (`handoff/T`, `handoff-body/T`, `-rN`,
  `dispatch/*T*`) and refuses it whole when a `handoff/` tip has a `+` line in
  `git cherry` against main or any of its refs has an open pull request.
