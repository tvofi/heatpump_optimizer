# recut-3835: result

Seat: cloud fixer, fourth-round re-cut of PR #3835 (R11-SEAM-learners), 2026-11-25.

- Code head: `bdaf324c4b3bb069d0dc2f76f668a68aaf0da37d` on `handoff/r11-seam-learners-pr` (fast-forward from 0291a7d9a5 via ee7df28bf3 and a4a600a4ef). Merge base: origin/main `d3d66c40408e76351ffc528686353cadf815a05c`.
- Body: `handoff-body/r11-seam-learners-pr` at `126a75a3cbc835ff8b0e2e9262d46456d97d8b63` (BODY.md, under `## Re-cut`). `policy_lint.mjs --pr-body --head bdaf324c4b --base d3d66c4040`: 0 errors. `carry_audit.py check`: 3 routed, 0 unrouted, 0 bad destinations. `body_push.sh` passed its predictor at bdaf324c4b.
- Delta range for the reviewer: `fab2d371ede00e9168843c18f6c47dc2425046f9..bdaf324c4b3bb069d0dc2f76f668a68aaf0da37d`. Of this pass's own work, a4a600a4ef is a test docstring and bdaf324c4b merges main. The repair of fab2d371's block is bd7e21777b (2026-11-22), which was already on the branch.

## The three blocks

| verdict | block | resolution | evidence |
|---|---|---|---|
| 877d152270 (c6c11df0) | mutation-vacuous, `coordinator.py:1121` (tank read never reaches the meter) and `draw_range.py:788` (`floor > 0.0` dropped) | killed at ee7df28bf3 and at bdaf324c4b. T1 (`None`) fails 2 of 28 learner-block checks, and D788 fails 1 | `evidence/mut_T1.log`, `evidence/mut_D788.log`, `evidence/m2/T1.log`, `evidence/m2/D788.log` |
| c06d450a7f (3d8679b7) | mutation-vacuous, `coordinator.py:1121` (`tank.ok` gate dropped) | killed at both heads. T2 (`tank.value`) fails 1 of 28: "a stale first tank read is no evidence ..." | `evidence/mut_T2.log`, `evidence/m2/T2.log` |
| 414fe919eb (fab2d371) | class-open, `coordinator.py:6134` `room_record.House` reads the plan split, E3 | fixed, not dispositioned by exclusion. bd7e21777b gives `room_history.House` a `space_alone` field that `HeatEnergyMeter.served_space_alone` answers on the settled interval's split, and runs the step before `_record_accuracy`. E3 reads 15 at the merge base and 14 at the head, and the removed line is exactly that site. Main adds no E line between bb6377b4 and d3d66c40. Mutant R1 fails 2. The review's findings O and P (per-cycle evidence asks) fail 1 each. No Carry is needed, because the site is built | `evidence/E*_*.txt`, `evidence/mut_R1.log`, `evidence/mut_O.log`, `evidence/mut_P.log`, `evidence/m2/` |

Driver for every mutant: `tools/audit/seat/features_block.py` with an `--emit-prelude` prelude on `R.section("R11-SEAM-learners: the one freeze predicate")`, the finder's harness. The unmutated block reads `ALL 28 FEATURES BLOCK PASSED` at both heads (`evidence/block_clean.log`, `evidence/block_clean2.log`). The 17-row mutation table is in the body. Every row is killed, with equal counts at both heads.

## What this pass found and repaired

- The scoped gate at ee7df28bf3 was red: `tests/entities.py` read `1 of 2763` on the #1218 selection-cost note. `learning_freeze.py` lifts env_drift.py/manual_plan.py and golden.py/manual_plan.py from 0.798 to 0.800, so the census reads 182 at the merge base and 184 at the head (`evidence/pairs.py`, `evidence/gate.log`). a4a600a4ef updates `tests/deployment_shape.py`'s note. With it, `tests/entities.py` reads ALL 2763 PASSED, and deployment_shape and doc_claims pass (`evidence/post_*.log`). This is probably the CI `tests / fast (3.14)` red at e4d40de37b (run 45574795779), whose log does not name the failing script.
- `body_push.sh`'s predictor refused a4a600a4ef: a plain merge into the new main d3d66c4040 conflicted (wave-script AGREEMENT UNMERGED). bdaf324c4b merges origin/main. The ledger driver resolved `tests/structure_budgets.json`, and no budget was raised.
- At bdaf324c4b the scoped gate (`GOLDEN_REF=d3d66c4040`) passes: `MODE: SCOPED -- 32 script(s) run`, `34 TEST SCRIPT(S) PASSED; 1 SCOPED OUT AND NOT RUN` (`evidence/gate2.log`). `tests/structure.py` passes, `brief_lint.mjs` exits rc 0, and archscore reads `dS +3.1822 WORSENS (inadmissible: coord_footprint 2531->2534)`, answered in the body's `## Architecture score` as before.
- Finder harnesses ran at both ends twice (bb6377b4/ee7df28b in `evidence/h/`, d3d66c40/bdaf324c in `evidence/h2/`, comparison in `evidence/compare2.txt`). The RESULT lines are identical except two counter_spans counts that depend on the wall-clock hour and are not body figures.

## Not stopped on

No second class-open block on the same axis was found. The E1-E3 re-run at both merge bases names no line outside the design tables and this diff's own readers.

## Notes for the orchestrator

- `body_push.sh` printed `could not delete the kept body handoff-wip/r11-seam-learners-pr-body`. That ref (95c36ec563) holds a refused earlier body of this pass and can be deleted.
- `body_push.sh`: `no Prepr: trailer`, so the open runs the full `prepr.sh` at bdaf324c4b. This seat did not run prepr.
- The design §5 plan-flag-off arm (`booked_kwh_unplanned_max` 3.0160 kWh at both ends) is still unbuilt and carried to #3769. As the verdict at 414fe919eb noted, whether an unbuilt design row needs the design reviewer's acceptance is the orchestrator's decision.
- Comms: seat_comms init, heartbeat and checkpoints ran. No inbox command arrived.
