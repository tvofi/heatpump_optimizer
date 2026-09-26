# D7 verification, lens V2 (independent), round 9, box G4-V2

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`. Evidence tree: `/home/claude/ev` (branch `handoff/audit-r9-verify-g4-v2`). Python 3.14 at `/home/claude/venv`, run with `PYTHONPATH=tests/hastub`. nproc is 4. Every harness pins BLAS to 1 thread and printed thread_factor 1.000–1.007. load1 was between 0.4 and 3.7 while I measured, and it is quoted beside each number. Every number here is a count or a ratio, so box load does not change it. I made no on-disk production or test edits. The perturbations are all in memory, and `git status` shows only my `tools/audit/round9/D7/verify-v2/` directory.

## D7-s1-01: the structural ratchet does not price `_helper(self, ...)` state
- **Step 1, finder's harness re-run** (`s1/helper_escape.py`): reproduced exactly. helpers=11, state_refs=30, coord_method_calls=8, inline `_fold_flow_lift` rows_up=4, cut_delta=8. The rows that rise are cross_seam_edges, cut_grid, cut_learning and internal_call_edges. load1 0.43.
- **Step 2, my own measurement** (`verify-v2/extract_reward.py`). I ran the refused move in the other direction. On the AST, I moved each plain coordinator method out of the class as a module-level `_m(coord, ...)` and rewrote each `self.m(...)` call to `_m(self, ...)`. Then I scored the result with production `structure.seam_metrics`.
  - Metric: the change in sum(cut_*) + cross_seam_edges per extraction.
  - Result: of 184 eligible methods, the metric fell for 139 and rose for 1. The total drop was 1139, against a baseline score of 930. The largest single drop was 37 (`_async_watch_learning_drift`).
  - Null control: a synthetic pure method that nothing calls moved nothing (1 cell, 0 nonzero).
  - load1 3.72.
- **Step 3, attacks**:
  - Contention: none applies; these are AST counts.
  - Documented as accepted? `docs/HANDOVER.md` records this shape as refused. The `state_root_bindings` docstring guards only the `_ctx`-handoff variant, and nothing in `seam_metrics` enforces the refusal for `self`.
  - Cause and effect in the tree: `_fold_flow_lift`'s docstring (coordinator.py:708–710) gives avoiding `coordinator_methods` and a seam edge as its reason for being module-level.
  - Grid artefact: my 184-cell grid points the same way as the finder's 10-cell leave-one-out.
  - Severity: an instrument blind spot that shapes how code is laid out; no user effect.
- **Vote: verify, low.**

## D7-s1-02: the drift-gate comparison and the stress per-scenario verdict can be deleted with every check green
- **Step 1**: I did not re-run the finder's mutation train (`train_mutations.py`). tvofi's 2026-09-26T11:37Z rule rules out mutation pools and re-runs, so I cite the finder's recorded mutants `drift`, `stress` and `drift_leaf`.
- **Step 2, my own measurement** (`verify-v2/verdict_lines.py`). I ran the recorded driver `tests/entities.py` with sys.monitoring LINE counting and counted how often each verdict line actually executes. A line that runs 0 times means no mutant on it can be killed by that driver.
  - `drift_callsite` (env_drift.py:2452, `_diff_leaves(baseline[name], branch[name], ...)` in `main`): **0** executions.
  - Lines of `env_drift.main` hit at all: 0.
  - `stress_verdict` (stress.py:3664, `if ratio > allowed:`): **0** executions.
  - Control `drift_leaf` (the `elif a != b:` line in `_diff_leaves`): 1622 executions.
  - driver exit=1 (entities.py is red in this environment as well). load1 1.83.
  - The stress verdict sits inside stress.py's `if __name__ == "__main__":` block (starting at :2736), so no importing driver can ever reach it.
  - A second control, `scenario_budget`, also ran 0 times under entities.py. So this run does not confirm the finder's statement that `scenario_budget` is pinned; that pin must live in another driver, and I did not verify it.
- **Mutations the suite misses** (these are instrument files, not production files):
  - `tests/env_drift.py:2452` `_diff_leaves(...)` → `pass`
  - `tests/stress.py:3664` `if ratio > allowed:` → `if False:`
- **Step 3, attacks**:
  - Is the stress deletion covered by the global `slow` ceiling? Only weakly. The global ceiling is `live_solve_budget_ratio()` = 1630.2, and for 48 of 51 scenarios the scenario's own budget is tighter than that. Deleting the per-scenario branch therefore leaves a ceiling about 8x looser at the median (median recorded ratio 59.5 × 3.5 ≈ 208).
  - Severity: at this baseline both gates behave correctly; the gap is latent. Both files are CODEOWNERS `@tvofi` (`.github/CODEOWNERS` lines 102 and 110), so any edit that deleted either verdict would need tvofi's approving review. That review is a working mitigation. On consequence, this is low, not medium.
- **Vote: weaken, low.** The mechanism holds (executed count 0 of 2 verdict lines reached, against 1622 for the control). The medium severity is not earned while an owner review stands in front of both sites.

## D7-s2-01: the sysid fit is biased by a coarse Euler rollout
- **Step 1** (`s2/sysid_plant.py`): reproduced exactly.
  - Bias on the 30-substep truth: light_new −0.16823, heavy_old −0.25461, typical_slab refused.
  - continuous_presets_bias_gt5pct=3, adopted=0.
  - Truth integrated at the fit's own step (sub1): heavy_old +0.00000 adopted, typical_slab +0.00000 adopted.
  - load1 3.12.
- **Step 2, my own measurement** (`verify-v2/sysid_openloop.py`). This removes the state machine, the step sizer and the adoption gate:
  - an open-loop power step (6 h hold, 8 h step, 8 h hold);
  - the truth is the same candidate family (`_simulate_slab_path`) at the preset's true parameters, integrated with 1 or 30 substeps;
  - I fitted UA, C_r and G freely with scipy least squares, without the production G ridge.
  - Metric: presets whose fit with the production 0.5 h rollout, on the 30-substep truth, is more than 5 % off in UA.
  - **Result: 2 of 3.** light_new +0.038, heavy_old +0.381, typical_slab +0.369.
  - Null control (truth at 1 substep): |bias| ≤ 1e-5 on all three.
  - Perturbation (fine rollout at dt/30): |bias| ≤ 1e-5 on all three.
  - load1 2.28.
- **My definition versus the finder's**: my bias has the opposite sign and a different size, because without the ridge G trades off against UA. Both measurements isolate the same mechanism: the bias exists only when the rollout step is coarser than the truth's, and disappears when the rollout is refined. The judge decides whether the two definitions are comparable.
- **Step 3, attacks**:
  - Reachable in real Home Assistant: the fit runs through production `identify_slab`, armed by the button.
  - Harm is bounded: the #1410 gate refuses the biased fit (the finder's adopted_biased=0). The real effect is that the feature is inert and it publishes a biased `heat_loss_kw_per_c` with a reason that blames the measurement window.
- **Vote: verify, medium.**

## D7-s2-02: the defrost-derate fallback folds intervals that `_cop_fold_blocked` refuses
- **Step 1** (`s2/learner_gates.py`): reproduced exactly. derate_ingests_distorted=3. Derate factor after 24 intervals: 0.8738 with the immersion latch and with the backup heater, 0.9769 capacity-capped, 1.0000 clean. load1 0.83.
- **Step 2, my own measurement** (`verify-v2/derate_latch_grid.py`). The finder set `_immersion_active` directly. I let the production detector `_detect_immersion` set the latch instead, through two real `_update_current_state` reads of a FakeHass meter at 3 kW commanded plus the element, on a 6 kW-nameplate pump. Then one `_record_accuracy`.
  - Grid: element 4/5/6 kW × outdoor 0.5/2.5/4.5 °C = 9 cells.
  - **Result:** the detector latched in 9 of 9 cells, and the derate folded while `_cop_fold_blocked` was True in **9 of 9**.
  - Null (outdoor 7 °C, outside the frost band): 0 of 3 fold.
  - Published `factor()` after 24 latched intervals: 0.8088.
  - Perturbation `--gate-derate`: 9 → 0, and the factor stays at 1.0000.
  - load1 0.90.
- **Step 3, attacks**:
  - Reachable through the real read path (the detector is production code) — yes.
  - Is this the fallback's intended behaviour? No. `_space_measured_power` at coordinator.py:3479–3490 already refuses meter readings while the latch or resistive heat is active, so folding them in the derate is inconsistent with the rest of the coordinator.
  - Bounded by `DERATE_MIN` and the frost band, so medium rather than high.
- **Vote: verify, medium.**

## D7-s3-01: 10 class members are reached by no production code
- **Step 1**:
  - `s3/reach.py --list`: dead_reachability_total=9 (1 method, 8 properties), with the same 9 names as the finding. load1 0.58.
  - `s3/sentinel.py`: dead_members_called_from_production=0, live_controls_called=6 of 6, update_cycles_completed=12. load1 0.91.
- **Step 2, my own measurement** (`verify-v2/member_callers.py`). I used a different driver: the whole of `tests/entities.py`, which runs every platform through `async_setup_entry` and reads the Home Assistant surface. sys.monitoring counted each entry into the 10 members' code objects and classified the immediate caller frame as production or test.
  - **Result: production callers 0 of 10**, test callers 0 of 10.
  - Live controls with a production caller: 4 of 6. `mode` 4, `optimization_running` 1, `stale_keys` 142, `factor` 496. `IrradianceSeries.end` and `_Horizon.timestamps` are not driven by entities.py, so for those two classes my driver is weaker than the finder's sentinel, which does reach them.
  - load1 0.79.
- **Step 3, attacks**:
  - Dynamic access: I grepped for `getattr` string literals on these names, the `_hub` facade, diagnostics' `getattr` loop and the package `__getattr__`. None reaches the 10.
  - The string hits are `data` dict keys such as `"next_optimization"`, which entities read from `coordinator.data` rather than through the property.
  - Severity: hygiene.
- **Vote: verify, low.**

## D7-s3-02: `structure.py` dead_methods reads 0 while members are dead
- **Step 1** (`s3/screen.py`): baseline 0; `--no-property-exclusion` 5; `--attribute-only` 1; both 11. Reproduced.
- **Step 2, my own measurement** (`verify-v2/member_screen.py`). I wrote my own attribute-reference screen over methods and properties: a member counts as referenced only by an `ast.Attribute` or a getattr/hasattr/setattr literal. HA convention names are excluded using structure's own lists.
  - `structure_dead_methods` = 0 versus **my_dead_members = 11**: 10 properties and 1 plain method. Two of the 11 are false positives (climate `hvac_mode` and `preset_mode`), so 9 are genuinely dead.
  - Which of structure's rules hides each member: property rule only 5; bare-name rule only 1 (`DefrostDerate.measured`); both 5.
  - Null: an injected unread member adds +1; injecting one read of it brings the count back (+0).
  - load1 0.58.
- **Step 3, attacks**:
  - Scope: `is_property_getter`'s docstring and the comment at structure.py:1095–1108 exclude `@property` by design and call the name screen "coarse". Part of the gap is therefore a documented scope boundary, not a counting error.
  - But the bare-name rule misses `DefrostDerate.measured`, a plain method. Catching exactly that kind of method is the screen's stated purpose (#1395), so that part is a real defect in the instrument.
  - The claim as written ("two rules hide them") is accurate.
  - Severity: hygiene.
- **Vote: verify, low.**

## Harnesses
All under `/home/claude/ev/tools/audit/round9/D7/verify-v2/`: `extract_reward.py`, `verdict_lines.py`, `sysid_openloop.py`, `derate_latch_grid.py`, `member_callers.py`, `member_screen.py`. Each header states how to run it and what it prints.
