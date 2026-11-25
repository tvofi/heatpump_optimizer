Fix review: blocked 3f8fb54ffcf92146097881fe4762866340446fe8 mutation-vacuous: dhw_planner.py:1197 flag read replaced by True (M1), dhw_planner.py:1205 charge_running unbound (M8), dhw_start.py:126 charge_running dropped (M9) survive

bus-nonce: 1c75229b3e205a3251865e3aad055401

Round 1 (first review of this pull request; no prior verdict).

## Block

The fix's production effect runs coordinator -> `ThermalState.dhw_charge_under_way` -> `DhwPlanner` (`dhw_planner.py:1197` reads the flag, `:1205` binds it into `_repair_dhw_floor` and hands it to `place_startable`) -> `dhw_start.py`. The two ends are pinned: the coordinator call by the new features check (M7 killed) and the `dhw_start.py`/`pump_signals.py` helpers by `tests/block_duty.py` calling them with `charge_running=False` directly (M2-M6 killed). The middle link is pinned by nothing: no test hands `DhwPlanner` a state with `dhw_charge_under_way=False` (the only test references to the field or keyword are `tests/block_duty.py:1013`, `tests/features.py:41036` (a stand-in default `True`) and `tests/features.py:97154` (reads the coordinator's state, runs no planner)).

- M1 (`dhw_planner.py:1197`: `initial_state.dhw_charge_under_way` -> `True`, i.e. the planner behaves exactly as at the base): survives `tests/block_duty.py` (158 passed), the features block, and every closure script run: `manual_plan.py`, `edge.py`, `cycle_lane.py`, `finite_boundary.py`, `stress.py`, `guard_pins.py`, `optimality.py`, `solar_alignment.py`, `plan_view.py`, and the full `tests/features.py` (`ALL 6117 FEATURE CHECKS PASSED`, rc=0, 983 s).
- M8 (`dhw_planner.py:1205`: `charge_running=running` removed from the repair's binding): survives `block_duty.py`, the features block, `manual_plan.py`, `guard_pins.py`, `edge.py`.
- M9 (`dhw_start.py:126`: final `drop_unstartable(...)` without `charge_running`): survives the same five. (The ledger's `place_startable.RETURN_DEL.474cf0a0` kills deleting the return, not dropping the argument.)

With M1 applied the defect #3848 fixes is back in production (a step-0 hot-water run is kept while the pump heats or is stopped) and the suite is green, so the claimed fix is not pinned end to end. CI's `tests / mutation` lane was GREEN because no mutation operator draws a mutant on the attribute read or the keyword argument, so the six pinned sites do not cover these lines. Owed: a check driving `DhwPlanner` (or the scheduled solve) with `dhw_charge_under_way=False` on a warm tank with a step-0 charge and asserting the run is dropped, failing under M1, M8 and M9.

## Findings

- Note: harness: the finder's harness (`dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py`) predates the flag and cannot see this change; the PR body names no enumeration rule for the step-0 exemption sites. My own enumeration (builder's, a locator over `custom_components/heatpump_optimizer/*.py` for start-condition and "under way" terms plus every caller of the four helpers) returns exactly two exemption sites, `dhw_start.py` `startable_steps` and `drop_unstartable`, both in the diff: a closed class at this head. Carry: dismissed: evidence of a closed class, not a defect
- Note: arch-score: `score.py --diff` prints `dS -0.0006 WORSENS (inadmissible: coord_footprint 2521->2522)` at this head while the `arch-score` check is success; the body answers the +1 under `## Architecture score`. Carry: dismissed: answered in the body, CI check green

## Evidence

- Head reviewed: `3f8fb54ffcf92146097881fe4762866340446fe8` (`ev/HEAD.txt`), equal to the PR head read live. Merge base `5594a34a49404109b8e0f18bd5be18ddbb667cdf`. Role files unchanged between merge base and origin/main.
- `git merge-tree --write-tree origin/main 3f8fb54ffcf92146097881fe4762866340446fe8`: rc=0, no conflict (`ev/merge-tree.txt`).
- CI: `merge_train.py classify 3f8fb54ffcf92146097881fe4762866340446fe8 --pr 3863` -> `GREEN 3f8fb54ffcf92146097881fe4762866340446fe8 pending: none red: none` at 05:14:19Z (`ev/classify.log`). Owed reds at earlier heads (`tests / fast (3.14)`, `tests / mutation`, `gate`, `arch-score`, `tests / closures` UNDER-SCOPED) are answered under the body's `## Red checks` / `## Head`.
- Targeted mutants (`ev/mutants.txt`, `ev/mutant_M1_closure.txt`, `ev/mutant_M8_M9_closure.txt`, `ev/M1_features_full.tail.txt`): killed M2 (flag always True), M3 (drop exempts step 0), M4 (startable ignores flag), M5 (flag ignores mode), M6 (combined mode ignores action), M7 (coordinator skips `with_dhw_under_way`, killed by the features block only); survived M1, M8, M9; NULL comment-only change survived both drivers.
- Moved code: `dhw_start.py` against the deleted `dhw_planner.py` block differs only in the `charge_running` parameter, its uses and docstrings (verified by diff).
- `tests/structure.py`: `STRUCTURE RATCHET PASSED`, `module_excess_loc=21672` (body's 21672 against main's 21775 re-derived); `class_excess_loc 17301`, `max_class_loc 7844` at budget.
- `closure.py select --diff <merge-base>`: `MODE: SCOPED -- 29 script(s) run, 5 scoped out` at this head (body's 28 was at `859dda1c38` against `0f63320c`; not re-derived at that pair).
- `deployment_shape.py`: `ALL DEPLOYMENT SHAPE CHECKS PASSED`. `VERSION`, manifest, `RELEASE_NOTES.md` and both claim files untouched three-dot (`ev/cheap_checks.txt`). Architecture score `ev/archscore.txt`.
- Not re-derived: the body's patch-id equality, the finder's-harness counts (42/43 KILLED) and the `claims.py` RESULT lines.
