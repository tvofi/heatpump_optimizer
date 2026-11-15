`tools/pr/ci_predict.py` replayed each touched instrument-self-tests step at the head under a fixed 180 s bound and turned a timeout into rc 124; `step_replay_preds` read rc 124 at the head and 0 at the base as a predicted red, so `prepr.sh` refused clean branches on a loaded host (#3598's update and the owner-criteria opener, 2026-11-15, CI green for those steps). A timeout measures the host, not the head. Now `replay_step` returns `TIMED_OUT` (-124, never a bash rc), a head timeout is reported as the info line `UNMEASURED <step>: timed out at <s> s on this host` and is not replayed at the base or predicted. The bound is `HPO_STEP_REPLAY_TIMEOUT_S` (default 180, unparseable or non-positive falls back to 180). A real non-timeout red is predicted exactly as before. A base timeout keeps its existing path (non-zero at the base: a note left to CI).

Alternative not taken: replaying once more, base first. It doubles the cost on exactly the hosts that are slow, and a second timeout would still need this info path.

Closes: none

## Head

d77e2f91896ea4541f244f3b2967c4f1cef34203

## Mutation proof

Mutated the predicate in `step_replay_preds`: `if rc and rc != TIMED_OUT` to `if rc` (timeout mapped back to a red), ran `python3 tools/pr/ci_predict.py --self-test`: `FAIL a step that outlives the bound at the head is UNMEASURED, not a red`, `ci_predict self-test: 1 failed`. Restored; the same command at the head: `ci_predict self-test: 0 failed`.

## Null control

At the merge base the new arm's step (sleeps past a 0.5 s bound at the head, passes at the base) is predicted red, since rc 124 there is truthy. In the tree, the null control arm `rc 1 at the head and 0 at the base is still predicted` passes under the same 0.5 s bound, with no UNMEASURED note.

## Figures

- `python3 tools/pr/ci_predict.py --self-test` (instrument): 0 failed at the head, 1 failed under the mutant.

## Red checks

none

## Forward-carry

none

## Friction

none
