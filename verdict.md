Fix review: merge e099eff6a5238d2e242892e3418f27a7b0ea8466

bus-nonce: dfe07f6263a4950819c2b1740f55cbd6

pending-ci: tests / mutation, tests / typing, validate / validate-hacs (classify prints WAIT at this head; governance / instrument-self-tests is red on main itself until #3474 and is outside owed-reds)

## Evidence

Round 3, a delta review of 0aed6ccbc99c5a3210dcb1caf013ea0d7c5ceed5...e099eff6a5238d2e242892e3418f27a7b0ea8466 (`ev/HEAD.txt`), from detached worktrees at the head, at 0aed6ccb, at 49a45dd8 and at origin/main. The delta is `de817c3a` (`_dhw_write` bounds the cycle's write with `hi=inp.params.dhw_hard_max_temp`, rounded down, in place of `rounding="up"`), `7c004817` (checks, `--grid`), the ledger re-pin and a merge of main. The block (null-control-leak: an off-step everyday set-point at or above the disinfection temperature written a step above itself) is answered.

- RESULT finder's census, `dev/audit/harnesses/r10_disinfection_setpoint.py --grid`, my own run of the head's copy at all four trees (`ev/grid_*.txt`): cycle=1 rows over `dhw_hard_max_temp`: 0 at the head, 407 at 0aed6ccb, 284 at 49a45dd8; cycle=0 rows over it: 104 at all of them (main's, unchanged). The body's figures reproduce.
- RESULT the blocked case, everyday 57 / disinfection 50 / step 5: grid line writes 55 at the head (0aed6ccb: 60), as 49a45dd8 and the no-cycle row do.
- RESULT null control: the `cycle=0` lines of `--grid` and the 80 `null_*` lines of the default mode are IDENTICAL at the head against origin/main, 49a45dd8 and 0aed6ccb (`ev/grid_*.txt`, `ev/harness_*.txt`). Against 49a45dd8, 284 `cycle=1` lines differ and every one is `over=1` at 49a45dd8 (0 not); against 0aed6ccb, 407.
- RESULT `tests/block_duty.py` at the head: rc=0, 66 of 66 (`ev/block_duty_head.log`); the new census check `_cycle_grid_over_hard_max` asserts all three orderings first.
- RESULT mutation proof, the PR's driver at the head exits 0 (`ev/pr_mutants_head.txt`): NULL survived, every named mutant killed, M2 (0aed6ccb's round-up), M11, M12 and M13 among them.
- RESULT credit cost, my own derivation from the grid lines (`ev/credit_figures.txt`, rows with disinfection above the everyday set-point and at most 70): 330 rows, writes below `legionella.py`'s instant threshold (disinfection less 1.0) 34, below the hold-verified threshold (less 0.5) 71. These equal the body's 34 / 71.
- `git merge-tree --write-tree origin/main e099eff6a5238d2e242892e3418f27a7b0ea8466` rc=0, clean (`ev/merge_tree.txt`).
- `VERSION`, the manifest version and the `RELEASE_NOTES.md` heading: untouched against the merge base.
- Forward-carry: both items are in the body's `## Forward-carry` and landed on the roster (body: Carry 1 at 2ad7130319, Carry 2 at ff4fefa44e on origin/handoff/audit-r10-roster); I did not open the roster ref in this delta.
- CI: `merge_train.py classify` printed `WAIT e099eff6a5238d2e242892e3418f27a7b0ea8466 pending: gate red: none` (rc=3), `ev/classify.txt`. Nothing concluded red at this head when read. `tests / fast (3.14)` red (inherited from main, #3466) and `tests / mutation` (state (b), `ci_predict.py`) are answered in the body's `## Red checks`.

## Findings

- Follow-up: bounding a cycle by the hard maximum reverses 49a45dd8's credit behaviour for an off-step disinfection temperature above the everyday set-point on coarse steps. I reproduced 34 of 330 rows under the instant-credit threshold and 71 under the hold-verified one, against 0 at 49a45dd8. On such an install (for example disinfection 62, step 5) the cycle is written at 60 and the legionella guard never credits it; `dhw_gated` also excuses the arbiter's own 60, so the repair does not name it. This is better than origin/main (265 and 286 rows), the body discloses it, and the choice between overshooting the hard maximum and undershooting the target is a ruling on `dhw_hard_max_temp` outside this repair. Carry: R10-OUTSIDE-DISINFECTION-SETPOINT
- Follow-up: the no-cycle write can still exceed `dhw_hard_max_temp` (everyday 58, step 5: 60), 104 of 780 rows, identical at origin/main; reproduced, unchanged by this delta and held by the brief. Carry: R10-OUTSIDE-DISINFECTION-SETPOINT
