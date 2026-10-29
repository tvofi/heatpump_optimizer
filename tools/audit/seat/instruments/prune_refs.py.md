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
  the ordering offline (22 checks).
