# `carry_fold.py`

- `carry_fold.py` — the orchestrator's pre-merge writer for a body's `Carry: <GROUP>` items. It takes
  the items `carry_audit.py landed` reports missing from their destination group's brief, appends each
  through `roster_edit.py append-carry --push` (the one write path), re-reads the roster branch, and
  asserts after the fold that every item id is now in its group's brief or carries; an op that exited
  0 and left an id out is rc 1 naming it. A destination that is no valid group refuses before any
  write. When: after `body_push.sh` refuses `CARRY-LANDED` for a seat that cannot write the roster,
  before the merge; `roster_sync.py` writes the same items at the merge and `roster_edit.py` refuses
  an exact repeat. `--self-test` drives it over injected `load` and `apply` callables.
