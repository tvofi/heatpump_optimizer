Fix review: merge a9ba0b8874092db8780f93fa290b282b5ce200b5

bus-nonce: e3f91bfe68c9b9db63e48cf97fc3ed3e
seat: review-2070, round 3. I reviewed the delta b731ef6b3..3ecb86adaf247f182679a175bd619fd363a5e35c (one commit, 3ecb86ada) from detached worktrees at the head and on one mutant.

## Head move: a bot ledger commit, nothing else

Measured at 3ecb86adaf247f182679a175bd619fd363a5e35c. The head then moved to a9ba0b8874092db8780f93fa290b282b5ce200b5, one commit by github-actions[bot] ("ci: pin killed mutants"). It adds 4 files under tests/mutation_ledger/killed_by/ only:
- coordinator.py:_tail_freeze GUARD_OFF, killed by features.py;
- early_cutoff.py:allow_on CMP_BOUND, killed by features.py;
- early_cutoff.py:on_room_event GUARD_OFF, killed by structure.py;
- early_cutoff.py:threshold RETURN_DEL, killed by structure.py.
It changes no production, test or harness line, so every number below holds at a9ba0b8874092db8780f93fa290b282b5ce200b5 (evidence-r3/bot-pin-delta.txt). The other 42 of the 46 added sites are still unpinned: they are the autofix's to pin, and the train's CI gate waits for mutation to go green.

## Round-2 blockers: resolved

1. **The ledger pin is re-keyed.** `killed_by/coordinator.py/_on_off_service.RETURN_DEL.dac85d34.json` was renamed to `pump_arbiter.py/on_off_service...`. The old line and the digest are the same, because the function moved unchanged. Results:
   - CI `mutation` at this head no longer prints "ledger disagrees". It refuses only the 49 ADDED UNPINNED entries, which dedupe to 46 sites, set-equal to the body's list (evidence-r3/ci-sites.txt, body-sites.txt). That is autofix's path.
   - `tests/entities.py` locally: ALL 2227 PASSED (evidence-r3/entities.txt).
   - CI `fast (3.14)` is green (check-run 113691279940).
2. **D12-s2 surfaces.py is retargeted to `pump_arbiter.on_off_service`.** At the head the baseline gives failing_surface_cells=0 (switch, input_boolean and climate all have calls=2 and misrouted=0), and `--perturb` gives 0 -> 2 (input_boolean, climate). That is the same as round 2's `f74924e` and my retargeted copy. The docstrings in surfaces.py and mode_domain.py now name the new owner (evidence-r3/surfaces*.txt).

## The round-2 gap is now pinned (the coordinator's allow_on wiring)

The new check drives the real `_apply_action` twice: the cycle that arms, then an early refresh with a cut on record.
- At the head: "inside MIN_OFF of a cut does not turn the switch on" passes, and its null control, "past MIN_OFF turns it on as the plan says", passes.
- Mutant M17 is my own run (cda10f0df, local only), reverting the coordinator line to `bool(self._current_action.get("heat_pump_on", False))`. The first check FAILS with `[('switch', 'turn_on')]` and the null control still passes, so the null control proves the cycle does reach the switch write (evidence-r3/features-{r3,mut3}.txt).
- One feature check also fails at the head locally on macOS: `R9-F2.1 P3`, a solver-optimality float comparison (110.4366 vs 110.1297). This diff does not touch the optimizer, and the check is BLAS-dependent. CI's Linux `fast (3.14)` at this head is green, so it is not this PR's.

## Body and records

- The Head section names 3ecb86adaf247f182679a175bd619fd363a5e35c. Red checks answers round 2's `mutation` and `entities` reds with their cheaper detector (`mutation_table.py` reads the ledger in seconds). It names the instrument gap (nothing in CI runs a harness's perturbation arms) for the root-cause seat rather than building a check here.
- **Merge.** `git merge-tree` against origin/main 47b083b03 is clean; the claimnotes/ledger driver resolved tests/closures.json as a set.
- **Carried from round 2, unchanged by this commit** (the commit touches no production line):
  - the plan-write null control on surfaces.py;
  - the `switch_supply` fence, equivalent to the removed try/except;
  - archscore coord_footprint 2587 -> 2589, attributed and admitted;
  - structure ratchet passing at max_class_loc 8810;
  - dst_checks killing the wall-clock mutant;
  - the inert plan-aware rule reproducing the body's closed-loop table;
  - #2065 and #2066 conflicts limited to count and row files, with coordinator.py merging cleanly.

## CI at 3ecb86adaf247f182679a175bd619fd363a5e35c

`fast (3.14)`, `typing`, `env-matrix`, `browser` and `instrument-self-tests` are green. `mutation` is red only on the 46 listed sites, pending mutation-autofix. `nightly-status` is red and is main's. Final settle state: evidence-r3/check-runs.txt.

RESULT mutation refusal: ledger-disagreement 1 -> 0; added-unpinned 46 sites = body list
RESULT entities 2227/2227 pass
RESULT surfaces baseline 0, --perturb 2 (committed arm)
RESULT M17 (coordinator reads raw plan value): "inside MIN_OFF ... does not turn the switch on" FAIL; null control ok
