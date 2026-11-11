# D7#3 verifier report (round 10)

Worktree: audit-r10-verify-D7-3 at 9355f107d (handoff/audit-r10-register).
Per the user's instruction for this run, no harness was re-run; votes rest on source reading.
No executed numbers were taken, so no vote is a refute. The judge should re-measure any finding it depends on.

| id | vote | severity | basis |
|---|---|---|---|
| D7-s3-01 | weaken | low | Cusum.reset is defined at drift.py:157. The `.as_dict()` loads at coordinator.py:1719/1730 are on `state`, so a reader must type that receiver before BoostState.as_dict counts as dead. The name-kept blind spot is real in principle, but the 6-member list is not independently re-counted. |
| D7-s3-02 | verify | low | `textWidth(` occurs once in the card, at its definition (:3031), so there are 0 call sites. The comment at :2156-2157 says the chart "already has" a function by that name, "good enough for axis units", which implies the chart uses it. That claim is false. |
| D7-s3-51 | verify (unexecuted) | low | This is about the instrument (archscore census) and is consistent with the patch D7-arch3-01. Not re-measured. |
| D7-s3-52 | verify (unexecuted) | low | C1 reading Optional/alias spellings of Any is plausible as a string-matching blind spot. Not re-measured. Class: new (instrument blind spot), close to N-structure-blind. |
| D7-s3-53 | verify (unexecuted) | low | Instrument gaming of C6. Not re-measured. The class N-name-sort is kept. |
| D7-s3-54 | verify | medium | pump_arbiter.py:353-356 sets `planned_draw_runs.modulation_floor` as module-global function state. thermal_model.py:1229 reads it when no floor is passed, and the decorator at :327 clears it. Any concurrent caller on another thread (the executor fallback) reads or loses the floor. It is reachable in real Home Assistant only when the solve runs in-thread. Class: N-shared-config is confirmed. |
