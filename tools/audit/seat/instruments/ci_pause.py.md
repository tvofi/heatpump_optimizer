# `ci_pause.py`

- `ci_pause.py` — the merge train's CI pause: when a check-run at the head the
  train waits on (or main's tip) has been queued `pause_queued_min` minutes,
  cancel the active runs of the worst-ranked pausable pull request (never a
  `never_pause` tier, the train head, a PR in the train's batches or spool, one
  seen with a verdict, or one holding a `Fix review: merge` comment), record it
  in `paused.json` beside the train's state, and re-run its failed jobs when the
  head and main have nothing queued, on every train exit and at every train
  start; a moved head drops the record. Called from `merge_train.py`'s
  `wait_ci` (`pause_poll`), `unwind` and the train starts (`pause_resume`).
  Not switched by `priority_cancel`, which governs only the sweep's cancels of
  queued runs. `hold(<sha>)` names a queued priority run while the pull request
  at `<sha>` is not a priority tier (main's tip never is): the train waits on it
  before each re-run it starts (`HOLD`, carry 6 (ii)). Log lines: `PAUSE #<n> at <head8>: runs <ids> for <head8>`,
  `RESUME #<n> at <head8>: runs <ids> (<why>)`. When: only through the train.
  Refusal: an unreadable roster, setting or comments pause nothing.
