Fix review: blocked b537cfe9100801c1316c42ca25d2c9494ddedf92 class-open: coordinator._plan_slots and sensor DHWScheduleSensor fallback still count a step the plan declares off

bus-nonce: fa774a635f7c258b92251dee804b0bd8

Round 1 (no earlier verdict on #2819). Measured head `b537cfe9100801c1316c42ca25d2c9494ddedf92`, merge base `bc52ad2af1d0cfe95896119b649fa56e14c74b5b`, on Linux x86_64 with load1 below 2. The finder harnesses ran from `git archive` exports of both ends.

## Block

D8-s1-01 names three seams that read the channel draw against 0.05 kW instead of the plan's running rule: `_build_plan_views` `active_now`, the `_plan_slots` merge, and the `DHWScheduleSensor` fallback (`dev/audit/rounds/round10/D8/s1/REPORT.md`: "Its 'N slots planned' count therefore includes steps the plan declares off"). Its fix scope is: "the plan views and the plan sensors take the plan's running rule (`planned_draws_run` / `heat_pump_on_schedule`), not a literal 0.05". This diff routes only `active_now` through the new owner `optimizer.channel_heating_steps`. The other two changed only their spelling:

- `coordinator.py` `_plan_slots(..., threshold: float = CHANNEL_ACTIVE_KW, ...)` still merges every step with `powers[i] > threshold`, whatever `planned_draws_run` says.
- `sensor.py:1211` still counts `s.get("dhw_power", 0) > CHANNEL_ACTIVE_KW`.

The body says the threshold and the fallback "read them", meaning the constant and `channel_heating_steps`. They read the constant only.

Measured:

- `f1_active_now.py`: `slot_steps_declared_off=5` at base and **5 at head**. The body says 0 at both; the finder's report says 4. The `--perturb` arm leaves the count unchanged by design ("the slot threshold is a separate literal"), so the head did not move the finder's secondary metric.
- Reviewer probe `ev/drivers/slot_probe.py` at head: two 0.07 kW steps give `channel_heating_steps=[False, False, False, False]`, but `_plan_slots` publishes **1 slot** for them. The new owner and the slot list disagree on the same input.
- The class rule hides these sites instead of closing them. The `channel_active_kw` P2 entry in `tests/entities.py` matches only a `Compare` against the literal `0.05`. Renaming the literal to `CHANNEL_ACTIVE_KW` takes both sites out of the rule's reach, so the registry reads zero undispositioned sites while the behaviour is unchanged (fix-review step 14: a spelling move on the instrument).

To unblock: `_plan_slots`, the slot merge's `shared_kwh` test and the sensor fallback decide on `channel_heating_steps` (or `heat_pump_on_schedule`), and the matcher follows the named constant as well as the literal. Otherwise each site is dispositioned with a reason and the owner's agreement, and the body's `slot_steps_declared_off` figure is corrected.

## Findings

- Finite-float class beyond the census rule: `tests/finite_boundary.py::_finite_float_coercers` reads only module-level functions with a `float` / `float | None` return annotation. `accuracy.py` `AccuracySample.from_dict.num` is a nested coercer (`float()` under `except (TypeError, ValueError, OverflowError)` plus `np.isfinite`) with its own bool policy, so `True` reads 1.0. It is the shape `const.finite_float` now owns, outside the rule and outside any disposition. I widened the rule (`ev/drivers/ff_census.py --wide`: nested functions, no annotation filter) and it returns 16 candidates at head. I judged only `num` to be a real twin; the rest are predicates or formatters. The body should route `num` to the owner or disposition it, and say how far the rule reaches. Carry: R10-ARCH-SHAPES
- The disposition of the 63 unpinned sites, "pinned by mutation-autofix (custom_components/ site)", is a relabel for survivors. `ci-autofix.md`'s `mutation-autofix` pins only killed mutants (`ci: pin killed mutants`), and survivor triage is never automated. I sampled three listed sites and all three survived the scripts that exercise them:
  - `sensor.py:1211` CMP_BOUND (`>` to `>=`) against `tests/entities.py` and `tests/features.py`;
  - `dhw_schedule.py:151` CMP_BOUND (`>= 3` to `> 3`) against `tests/features.py` and `tests/entities.py`;
  - `wood_fuel.py:134` CMP_BOUND (`<` to `<=`) against `tests/wood_advisor.py` and `tests/features.py`.

  The FAIL sets equal the unmutated archive's. A script outside those I ran could still kill them, and CI's mutation lane has not run at this head, so this is a sample, not the table. The `## Red checks` `mutation` line owes the survivors their own answer. Carry: R10-ARCH-SHAPES
- The finite-float figure's driver (13 to 1) and the mutation driver are named in the body by machine paths under a user home directory, and neither landed. `fixer.md` step 18 requires a driver that a body figure needs reproduced to land in the PR, and `tools/audit/seat/tmp_paths.py` refuses machine paths. I rebuilt the census driver as `ev/drivers/ff_census.py` (my own instrument, disclosed) and it reproduces 13 to 1. The body's machine paths should go, and the census driver should land, or the body should state the figure as `_finite_float_coercers` applied to the base tree by a named landed command. Carry: R10-ARCH-SHAPES

## Evidence

Every figure below is my own RESULT at the measured head against the merge base (files under `ev/`):

- D7-s2-61, `probe_coercion_reach.py` (`ev/harness_*.txt`):
  - base: `1e6`, `1e400` and `inf` give `silent_cap_kw=6.0`, `inf_changes_decision=1`;
  - head: all three give 4.2, `inf_changes_decision=0`;
  - `unknown` reads 4.2 and `3` reads 3.6 at both ends (the null control holds);
  - `perturbed_1e400_equals_unknown=1` at both ends;
  - `_step_kw(nan|inf)` is nan/inf at base and None at head; `nan_reaches_flow=0` at both.

  This matches the body's 6.0 to 4.2.
- D8-s1-01, `f1_active_now.py`: `heating_now_while_off` 2 at base, 0 at head; `--perturb` gives 0 at both; `snapshots=36`. The body says 1 to 0. The harness header says the count is exact per machine (BLAS), so the direction holds and the absolute base value differs on this box. The secondary metric is under `## Block`.
- D7-s2-01 `pump_offline` arm, `learner_gates.py`: `freq_map` is INGEST at base and frozen at head; `pump_offline.learners_ingesting` 1 to 0; `freq_map_clean_folds=8` and `freq_map_defrost_folds=0` at both ends. This matches the body.
- Weekday twins (`PYTHONPATH=tests/hastub:custom_components`): normal/perturb/identity read 0/49/0 at both ends (`ev/weekday_twins.txt`). The perturbation moves the count, so the finding is live. This matches the body.
- Hour-clock grep: 5 at base, 2 at head, the same sites the body lists (`ev/hour_clock.txt`).
- Finite-float census: head's `_finite_float_coercers` returns 13 at base (the body's list exactly) and 1 at head (`const.py::finite_float`), via my `ev/drivers/ff_census.py` (`ev/ff_census.txt`).
- `finite_float` behaviour: `True` gives None, `b'3'` None, `'3.5'` 3.5, nan None, `10**400` None, `'1e400'` None, `2` 2.0 (`ev/finite_float_probe.txt`). The bool and bytes behaviour change is as the body states.
- Archscore: `score.py --diff bc52ad2af b537cfe9`: `Architecture score: dS +1.2702 IMPROVES`; `coord_footprint` 2445 to 2435, `duplication_copies` 39 to 37, `layer_violations` 17 to 13, `private_cross_module` 12 to 10. This matches the body's coord_footprint and dS (`ev/archscore.txt`).
- `tests/entities.py` in detached worktrees: 2 of 2445 FAIL at base and 2 of 2448 at head, with identical FAIL-name sets (`gate-sweep.yml` U0c, `graders-head-copy` delivery_status, and nested harness self-test lines). In archive copies the FAIL sets are identical at base and head. The body's 4 is this box's 2; the failures are the base's, not this diff's.
- Mutation proof, my own mutants in archive copies of the head (`ev/mut_*.txt`), all killed:
  - `_within_nameplate` to `return kw`: `manual_plan.py` 2 of 132;
  - `finite_float` bool policy dropped: `finite_boundary.py` 1 of 108;
  - `state_power_kw` isfinite dropped: `features.py`, "a power state parses to finite kW...";
  - `_freq_fold_blocked` narrowed to cooling: `features.py`, "an offline, faulted or cooling pump's interval...".

  The `features.py` #363 failure of an archive copy is excluded, as in the body.
- Merge with main: `git merge-tree --write-tree origin/main b537cfe9` exits 0 (with origin/main at `da12aa37d`, `LEDGER-MERGE: resolved tests/structure_budgets.json`), so GitHub's `dirty` is the driver file only. Merged with #2817's head `935a7a6b1fa123b16ba85f3e38756a29527f36ca`, it exits 0 and the same ledger driver resolves. `tests/entities.py` on that merged tree has the head's FAIL set exactly, so no entities disposition clashes. #2817 renames `async_update_thermal_params` dispositions to `_thermal_param_changes`, which is disjoint from this diff's entries.
- `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched; no claim file changed; the diff adds no host, home or temp path.
- CI at the measured head: the only check run is `arm` (skipped). Both CI runs (`CI code`, `CI edit`) are on the earlier head `21d646821` and were in progress, so no gate check on this head has concluded and step 11 has nothing to answer yet.
- Head moved under the review: the branch is now `6feac7eceeff979bfe3692555179565bde565d9b`, a merge of origin/main `da12aa37d` (#2712) on top of the measured head (`ev/HEAD_AT_POST.txt`). It touches `coordinator.py`, `draw_range.py` and `legionella.py` outside the blocking sites. At the new head, `_plan_slots`'s `threshold: float = CHANNEL_ACTIVE_KW` and `sensor.py:1211` are byte-identical, so the block stands there too. I did not re-take the other figures at the new head.
