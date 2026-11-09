# Review packet #3358
head: 64d4e7dbc6b0231c5ff4c9919b2b4052647e2698
base: fdc8d21adaa50a7feee534f08ee5edde9bda81ed

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=129011323485 neutral
arch-score / arch-score id=129010967635 success
arm id=129010791772 skipped
budget-raise-gate / budget-raise-gate id=129010967790 success
cancel-superseded id=129010770299 success
codeql id=129010946750 skipped
codeql / Analyze (actions) id=129010967778 success
codeql / Analyze (javascript-typescript) id=129010967744 success
codeql / Analyze (python) id=129010967856 in_progress
gate id=129011201915 failure
governance id=129010946746 skipped
governance / delivery-status id=129010967839 failure
governance / delivery-status-publish id=129010968892 skipped
governance / env-matrix id=129010967706 success
governance / instrument-self-tests id=129010967737 in_progress
governance / policy-docs id=129010967718 success
governance / record id=129010969766 skipped
governance / wave-script id=129010967689 success
hassfest id=129010946060 skipped
hassfest / hassfest id=129010967759 success
kernel-points id=129010969268 skipped
pr-contract id=129011203411 skipped
prelude id=129010770154 success
refresh id=129010770354 success
tests id=129010946431 skipped
tests / arch-instrument id=129011161115 success
tests / briefs id=129010967746 success
tests / browser id=129011161104 success
tests / closure-scope id=129010967791 success
tests / closures id=129011160976 in_progress
tests / coverage id=129011161024 in_progress
tests / fast (3.14) id=129011161134 in_progress
tests / mutation id=129010967812 in_progress
tests / nightly-ha id=129011163081 skipped
tests / nightly-status id=129010967914 success
tests / replay id=129011161006 in_progress
tests / typing id=129011161070 success
validate id=129010946486 skipped
validate / validate-hacs id=129010967900 success

## Refusals
required-red: required context `gate` concluded failure at 64d4e7dbc6b0231c5ff4c9919b2b4052647e2698

## Advisories
none

## carry_audit at the head
NOTE body item 7907dbfa: R10-COMBI-TANK: R10-COMBI-TANK resolved on origin/handoff/audit-r10-roster
NOTE body item cc665630: R10-COMBI-TANK: R10-COMBI-TANK resolved on origin/handoff/audit-r10-roster
NOTE body item c45c9022: R10-COMBI-TANK: R10-COMBI-TANK resolved on origin/handoff/audit-r10-roster
NOTE body item 54ed3e93: R10-COMBI-TANK: R10-COMBI-TANK resolved on origin/handoff/audit-r10-roster
CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/features.py
             `tests/features.py` is in the tree at this head
  unverified git diff --stat 09199e9e8 HEAD -- custom_components tests/features.py
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/guard_pins.py
             `tests/guard_pins.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         tools/audit/seat/mutant_run.py --spec <the 24 mutants> --cmd '<the combi block, as under ## Mutation proof>'
             `tools/audit/seat/mutant_run.py` is in the tree at this head
  ok         dev/audit/harnesses/r10_combi_tank.py
             `dev/audit/harnesses/r10_combi_tank.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_combi_tank.py equiv
             `dev/audit/harnesses/r10_combi_tank.py` is in the tree at this head
  unverified git diff --shortstat $(git merge-base origin/main HEAD) HEAD -- custom_components
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git diff --shortstat 74df96f104dfd8630894e8b52a11563b80803377 HEAD -- custom_components
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift bash tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/stress.py
             `tests/stress.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_combi_tank.py
             `dev/audit/harnesses/r10_combi_tank.py` is in the tree at this head
  ok         tests/features.py
             `tests/features.py` is in the tree at this head

FIGURES: 16 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/battery.py/build.BOOLOP.d0e56937.json b/tests/mutation_ledger/killed_by/battery.py/build.BOOLOP.d0e56937.json
new file mode 100644
index 000000000..3b0ee15b4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/battery.py/build.BOOLOP.d0e56937.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/battery.py:build BOOLOP d0e56937",
+  "killed_by": "tests/features.py",
+  "old": "    if params.dhw_enabled and not store.combi:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if params.dhw_enabled or not store.combi:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/battery.py/build.GUARD_OFF.19bc981b.json b/tests/mutation_ledger/killed_by/battery.py/build.GUARD_OFF.19bc981b.json
deleted file mode 100644
index f4780a13f..000000000
--- a/tests/mutation_ledger/killed_by/battery.py/build.GUARD_OFF.19bc981b.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/battery.py:build GUARD_OFF 19bc981b",
-  "killed_by": "tests/features.py",
-  "old": "    if params.dhw_enabled:",
-  "reason": "arrived with origin/main, commit d62195ade (fix(D12): guard the battery buffer/DHW stores on the config signal). `if params.dhw_enabled:` -> `if False:` raises the driver's `FAILED` count to 2 against a 0 baseline. Measured at the post-main head, 2026-09-22."
-}
diff --git a/tests/mutation_ledger/killed_by/battery.py/build.GUARD_OFF.d0e56937.json b/tests/mutation_ledger/killed_by/battery.py/build.GUARD_OFF.d0e56937.json
new file mode 100644
index 000000000..67d62d2c5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/battery.py/build.GUARD_OFF.d0e56937.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/battery.py:build GUARD_OFF d0e56937",
+  "killed_by": "tests/features.py",
+  "old": "    if params.dhw_enabled and not store.combi:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_legionella_ceilings.CLAMP_DROP.ab570bf1.json b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_legionella_ceilings.CLAMP_DROP.ab570bf1.json
new file mode 100644
index 000000000..e4abe0ef7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_legionella_ceilings.CLAMP_DROP.ab570bf1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._dhw_legionella_ceilings CLAMP_DROP ab570bf1",
+  "killed_by": "tests/manual_plan.py",
+  "old": "        boost_top = min(70.0, float(store.rating_max_temp))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`boost_top = (70.0)`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_legionella_ceilings.CMP_BOUND.456b4bfb.json b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_legionella_ceilings.CMP_BOUND.456b4bfb.json
new file mode 100644
index 000000000..147a0a4b7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_legionella_ceilings.CMP_BOUND.456b4bfb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._dhw_legionella_ceilings CMP_BOUND 456b4bfb",
+  "killed_by": "tests/features.py",
+  "old": "            boost_top > float(store.charge_max_temp)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`boost_top >= float(store.charge_max_temp)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_window_floors.CLAMP_DROP.6523b9c6.json b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_window_floors.CLAMP_DROP.6523b9c6.json
new file mode 100644
index 000000000..0dae9f381
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_window_floors.CLAMP_DROP.6523b9c6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._dhw_window_floors CLAMP_DROP 6523b9c6",
+  "killed_by": "tests/features.py",
+  "old": "        idle_min_temp = min(store.store_temp_for_tap(params.dhw_idle_min_temp), dhw_min_temp)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`idle_min_temp = (store.store_temp_for_tap(params.dhw_idle_min_temp))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._plan_dhw_min_cost.CLAMP_DROP.41cffe03.json b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._plan_dhw_min_cost.CLAMP_DROP.41cffe03.json
new file mode 100644
index 000000000..927e3ae70
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._plan_dhw_min_cost.CLAMP_DROP.41cffe03.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._plan_dhw_min_cost CLAMP_DROP 41cffe03",
+  "killed_by": "tests/features.py",
+  "old": "            np.maximum(requirement, ctx.store.store_temp_for_tap(params.dhw_min_temp)), humidity",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`(requirement), humidity`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/_DhwPlanContext.c_dhw.RETURN_DEL.e37bb5f4.json b/tests/mutation_ledger/killed_by/dhw_planner.py/_DhwPlanContext.c_dhw.RETURN_DEL.e37bb5f4.json
new file mode 100644
index 000000000..04ca1faa5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/_DhwPlanContext.c_dhw.RETURN_DEL.e37bb5f4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:_DhwPlanContext.c_dhw RETURN_DEL e37bb5f4",
+  "killed_by": "tests/manual_plan.py",
+  "old": "        return self.store.capacity_kwh_per_c",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/_DhwPlanContext.tank_decay.RETURN_DEL.22d7e1e8.json b/tests/mutation_ledger/killed_by/dhw_planner.py/_DhwPlanContext.tank_decay.RETURN_DEL.22d7e1e8.json
new file mode 100644
index 000000000..b08441fc8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/_DhwPlanContext.tank_decay.RETURN_DEL.22d7e1e8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:_DhwPlanContext.tank_decay RETURN_DEL 22d7e1e8",
+  "killed_by": "tests/manual_plan.py",
+  "old": "        return _tank_decay(self.store.ua_kw_per_c, self.dt, self.c_dhw)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/_exo_at.RETURN_DEL.1768b4d1.json b/tests/mutation_ledger/killed_by/dhw_planner.py/_exo_at.RETURN_DEL.1768b4d1.json
new file mode 100644
index 000000000..deff03e1f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/_exo_at.RETURN_DEL.1768b4d1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:_exo_at RETURN_DEL 1768b4d1",
+  "killed_by": "tests/manual_plan.py",
+  "old": "    return 0.0 if exo_kw is None else float(exo_kw[i])",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/@module.CONST.ff7e3dcd.json b/tests/mutation_ledger/killed_by/optimizer.py/@module.CONST.ff7e3dcd.json
new file mode 100644
index 000000000..e4ccc7244
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/@module.CONST.ff7e3dcd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:<module> CONST ff7e3dcd",
+  "killed_by": "tests/features.py",
+  "old": "_COMBI_EXCHANGE_ROUNDS = 4",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`_COMBI_EXCHANGE_ROUNDS = 8`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._co_optimize.BOOLOP.91c5b887.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._co_optimize.BOOLOP.91c5b887.json
new file mode 100644
index 000000000..5de21c02b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._co_optimize.BOOLOP.91c5b887.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._co_optimize BOOLOP 91c5b887",
+  "killed_by": "tests/features.py",
+  "old": "            if draw_rates is not None and self.model.params.dhw_store.combi:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if draw_rates is not None or self.model.params.dhw_store.combi:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._co_optimize.GUARD_OFF.91c5b887.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._co_optimize.GUARD_OFF.91c5b887.json
new file mode 100644
index 000000000..ecf998731
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._co_optimize.GUARD_OFF.91c5b887.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._co_optimize GUARD_OFF 91c5b887",
+  "killed_by": "tests/features.py",
+  "old": "            if draw_rates is not None and self.model.params.dhw_store.combi:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._deferred_energy_cost.GUARD_OFF.f5c46daf.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._deferred_energy_cost.GUARD_OFF.f5c46daf.json
new file mode 100644
index 000000000..8f113392d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._deferred_energy_cost.GUARD_OFF.f5c46daf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._deferred_energy_cost GUARD_OFF f5c46daf",
+  "killed_by": "tests/features.py",
+  "old": "        if include_dhw and not (p.dhw_store.combi and p.two_zone_enabled):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._stored_thermal_energy.GUARD_OFF.f5c46daf.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._stored_thermal_energy.GUARD_OFF.f5c46daf.json
new file mode 100644
index 000000000..60b806ee1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._stored_thermal_energy.GUARD_OFF.f5c46daf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._stored_thermal_energy GUARD_OFF f5c46daf",
+  "killed_by": "tests/features.py",
+  "old": "        if include_dhw and not (p.dhw_store.combi and p.two_zone_enabled):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_combi_dhw_exo.GUARD_OFF.f195744f.json b/tests/mutation_ledger/killed_by/optimizer.py/_combi_dhw_exo.GUARD_OFF.f195744f.json
new file mode 100644
index 000000000..17d973890
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_combi_dhw_exo.GUARD_OFF.f195744f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_dhw_exo GUARD_OFF f195744f",
+  "killed_by": "tests/features.py",
+  "old": "    if not p.combi_tank_active:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_combi_dhw_exo.RETURN_DEL.371740dd.json b/tests/mutation_ledger/killed_by/optimizer.py/_combi_dhw_exo.RETURN_DEL.371740dd.json
new file mode 100644
index 000000000..89825d92f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_combi_dhw_exo.RETURN_DEL.371740dd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_dhw_exo RETURN_DEL 371740dd",
+  "killed_by": "tests/features.py",
+  "old": "    return combi_dhw_net_series(model, temps, schedule, draw_rates, h.outdoor_temps, h.humidity)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.GUARD_OFF.ba727eb5.json b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.GUARD_OFF.ba727eb5.json
new file mode 100644
index 000000000..a532a51c9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.GUARD_OFF.ba727eb5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_flux_exchange GUARD_OFF ba727eb5",
+  "killed_by": "tests/features.py",
+  "old": "        if np.allclose(plan.schedule, dhw_power, atol=1e-4):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.RETURN_DEL.d235e41f.json b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.RETURN_DEL.d235e41f.json
new file mode 100644
index 000000000..b2cba6274
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.RETURN_DEL.d235e41f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_flux_exchange RETURN_DEL d235e41f",
+  "killed_by": "tests/features.py",
+  "old": "    return dhw_power",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_with_buffer_exo.RETURN_DEL.f71de30b.json b/tests/mutation_ledger/killed_by/optimizer.py/_with_buffer_exo.RETURN_DEL.f71de30b.json
new file mode 100644
index 000000000..98aecc5a7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_with_buffer_exo.RETURN_DEL.f71de30b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_with_buffer_exo RETURN_DEL f71de30b",
+  "killed_by": "tests/plan_view.py",
+  "old": "    return weather if buffer_exo_kw is None else replace(weather, buffer_exo_kw=buffer_exo_kw)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.space_flux.RETURN_DEL.9de167ed.json b/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.space_flux.RETURN_DEL.9de167ed.json
new file mode 100644
index 000000000..fe4fd6ae6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.space_flux.RETURN_DEL.9de167ed.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:DhwStore.space_flux RETURN_DEL 9de167ed",
+  "killed_by": "tests/features.py",
+  "old": "        return space_net_kw if self.combi else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.store_temp_for_tap.GUARD_OFF.95502b11.json b/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.store_temp_for_tap.GUARD_OFF.95502b11.json
new file mode 100644
index 000000000..b19cb31ee
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.store_temp_for_tap.GUARD_OFF.95502b11.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:DhwStore.store_temp_for_tap GUARD_OFF 95502b11",
+  "killed_by": "tests/features.py",
+  "old": "        if not self.combi:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.store_temp_for_tap.RETURN_DEL.f06db824.json b/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.store_temp_for_tap.RETURN_DEL.f06db824.json
new file mode 100644
index 000000000..902ad5017
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.store_temp_for_tap.RETURN_DEL.f06db824.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:DhwStore.store_temp_for_tap RETURN_DEL f06db824",
+  "killed_by": "tests/features.py",
+  "old": "        return self.inlet_c + (tap_c - self.inlet_c) / self.effectiveness",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.tap_temp_for_store.GUARD_OFF.95502b11.json b/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.tap_temp_for_store.GUARD_OFF.95502b11.json
new file mode 100644
index 000000000..55bc722c4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.tap_temp_for_store.GUARD_OFF.95502b11.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:DhwStore.tap_temp_for_store GUARD_OFF 95502b11",
+  "killed_by": "tests/features.py",
+  "old": "        if not self.combi:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.tap_temp_for_store.RETURN_DEL.3fab1e26.json b/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.tap_temp_for_store.RETURN_DEL.3fab1e26.json
new file mode 100644
index 000000000..1ffc90b82
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.tap_temp_for_store.RETURN_DEL.3fab1e26.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:DhwStore.tap_temp_for_store RETURN_DEL 3fab1e26",
+  "killed_by": "tests/features.py",
+  "old": "        return self.inlet_c + self.effectiveness * (store_c - self.inlet_c)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._simulate_step_two_zone.BOOLOP.2fe6a11c.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._simulate_step_two_zone.BOOLOP.2fe6a11c.json
new file mode 100644
index 000000000..42f642994
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._simulate_step_two_zone.BOOLOP.2fe6a11c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalModel._simulate_step_two_zone BOOLOP 2fe6a11c",
+  "killed_by": "tests/features.py",
+  "old": "        if throttled and buffer_exo_kw:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if throttled or buffer_exo_kw:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._simulate_step_two_zone.GUARD_OFF.2fe6a11c.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._simulate_step_two_zone.GUARD_OFF.2fe6a11c.json
new file mode 100644
index 000000000..d15e0ca88
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._simulate_step_two_zone.GUARD_OFF.2fe6a11c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalModel._simulate_step_two_zone GUARD_OFF 2fe6a11c",
+  "killed_by": "tests/features.py",
+  "old": "        if throttled and buffer_exo_kw:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.dhw_hold_hours.CLAMP_DROP.24cf749e.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.dhw_hold_hours.CLAMP_DROP.24cf749e.json
new file mode 100644
index 000000000..36e0d471a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.dhw_hold_hours.CLAMP_DROP.24cf749e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalModel.dhw_hold_hours CLAMP_DROP 24cf749e",
+  "killed_by": "tests/features.py",
+  "old": "        top = max(store.charge_max_temp, floor + 1.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`top = (store.charge_max_temp)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.simulate_dhw_step.CLAMP_DROP.6d5b3ca5.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.simulate_dhw_step.CLAMP_DROP.6d5b3ca5.json
deleted file mode 100644
index 97b244bfd..000000000
--- a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.simulate_dhw_step.CLAMP_DROP.6d5b3ca5.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalModel.simulate_dhw_step CLAMP_DROP 6d5b3ca5",
-  "killed_by": "tests/features.py",
-  "old": "        floor = min(p.dhw_inlet_reference, ambient_temp)",
-  "reason": "arrived with origin/main, commit 7eeea4d90 (D2-02: clamp the DHW inlet floor to the tank surroundings). Dropping the `min` clamp raises the driver's `FAILED` count to 2 against a 0 baseline. Measured at the post-main head, 2026-09-22, and re-pinned 1894 -> 1897 by PR #1488, whose D2-01 fix adds three comment lines above this site."
-}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.simulate_trajectory_batch.BOOLOP.89cf64f9.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.simulate_trajectory_batch.BOOLOP.89cf64f9.json
new file mode 100644
index 000000000..858a3cbff
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.simulate_trajectory_batch.BOOLOP.89cf64f9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalModel.simulate_trajectory_batch BOOLOP 89cf64f9",
+  "killed_by": "tests/features.py",
+  "old": "                    if throttled and exo_i:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if throttled or exo_i:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.simulate_trajectory_batch.GUARD_OFF.89cf64f9.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.simulate_trajectory_batch.GUARD_OFF.89cf64f9.json
new file mode 100644
index 000000000..f54f70f77
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.simulate_trajectory_batch.GUARD_OFF.89cf64f9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalModel.simulate_trajectory_batch GUARD_OFF 89cf64f9",
+  "killed_by": "tests/features.py",
+  "old": "                    if throttled and exo_i:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.simulate_trajectory_with_dhw.GUARD_OFF.d84dbbe9.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.simulate_trajectory_with_dhw.GUARD_OFF.d84dbbe9.json
new file mode 100644
index 000000000..544847d09
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.simulate_trajectory_with_dhw.GUARD_OFF.d84dbbe9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalModel.simulate_trajectory_with_dhw GUARD_OFF d84dbbe9",
+  "killed_by": "tests/features.py",
+  "old": "            if store is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.buffer_store_volume.GUARD_OFF.5946724e.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.buffer_store_volume.GUARD_OFF.5946724e.json
new file mode 100644
index 000000000..0acfe8bfb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.buffer_store_volume.GUARD_OFF.5946724e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalParameters.buffer_store_volume GUARD_OFF 5946724e",
+  "killed_by": "tests/features.py",
+  "old": "        if self.combi_tank_active:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.buffer_store_volume.RETURN_DEL.9314a0a4.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.buffer_store_volume.RETURN_DEL.9314a0a4.json
new file mode 100644
index 000000000..2cb01a718
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.buffer_store_volume.RETURN_DEL.9314a0a4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalParameters.buffer_store_volume RETURN_DEL 9314a0a4",
+  "killed_by": "tests/features.py",
+  "old": "        return self.buffer_tank_volume",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.buffer_tank_thermal_mass.RETURN_DEL.c22e3681.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.buffer_tank_thermal_mass.RETURN_DEL.c22e3681.json
deleted file mode 100644
index 866161160..000000000
--- a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.buffer_tank_thermal_mass.RETURN_DEL.c22e3681.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalParameters.buffer_tank_thermal_mass RETURN_DEL c22e3681",
-  "killed_by": "tests/features.py",
-  "old": "        return self.buffer_tank_volume * WATER_SPECIFIC_HEAT",
-  "reason": "Recorded by `mutation_table.py --drain` against 9061fbd3d710d5894b7083d8a58b8203f9e7aa97: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
-}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.buffer_tank_thermal_mass.RETURN_DEL.da341731.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.buffer_tank_thermal_mass.RETURN_DEL.da341731.json
new file mode 100644
index 000000000..de0cfcb85
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.buffer_tank_thermal_mass.RETURN_DEL.da341731.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalParameters.buffer_tank_thermal_mass RETURN_DEL da341731",
+  "killed_by": "tests/features.py",
+  "old": "        return self.buffer_store_volume * WATER_SPECIFIC_HEAT",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.dhw_store.RETURN_DEL.c401cdfe.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.dhw_store.RETURN_DEL.c401cdfe.json
new file mode 100644
index 000000000..0775f7d89
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.dhw_store.RETURN_DEL.c401cdfe.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalParameters.dhw_store RETURN_DEL c401cdfe",
+  "killed_by": "tests/guard_pins.py",
+  "old": "        return dhw_store_of(self)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/combi_space_net_kw.CLAMP_DROP.b47686bf.json b/tests/mutation_ledger/killed_by/thermal_model.py/combi_space_net_kw.CLAMP_DROP.b47686bf.json
new file mode 100644
index 000000000..f4f6e2f96
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/combi_space_net_kw.CLAMP_DROP.b47686bf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:combi_space_net_kw CLAMP_DROP b47686bf",
+  "killed_by": "tests/features.py",
+  "old": "    gained = store.capacity_kwh_per_c * np.diff(temps) / max(dt_hours, 1e-6)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`gained = store.capacity_kwh_per_c * np.diff(temps) / (dt_hours)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/combi_space_net_kw.RETURN_DEL.ed3f9304.json b/tests/mutation_ledger/killed_by/thermal_model.py/combi_space_net_kw.RETURN_DEL.ed3f9304.json
new file mode 100644
index 000000000..4b3115561
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/combi_space_net_kw.RETURN_DEL.ed3f9304.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:combi_space_net_kw RETURN_DEL ed3f9304",
+  "killed_by": "tests/features.py",
+  "old": "    return gained + loss - np.asarray(dhw_net_kw, dtype=float)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/combi_store_of.GUARD_OFF.f195744f.json b/tests/mutation_ledger/killed_by/thermal_model.py/combi_store_of.GUARD_OFF.f195744f.json
new file mode 100644
index 000000000..a29b2c015
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/combi_store_of.GUARD_OFF.f195744f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:combi_store_of GUARD_OFF f195744f",
+  "killed_by": "tests/features.py",
+  "old": "    if not p.combi_tank_active:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=24."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/combi_store_of.RETURN_DEL.8b8f9e7e.json b/tests/mutation_ledger/killed_by/thermal_model.py/combi_store_of.RETURN_DEL.8b8f9e7e.json
new file mode 100644
index 000000000..49b05e2f6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/combi_store_of.RETURN_DEL.8b8f9e7e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:combi_store_of RETURN_DEL 8b8f9e7e",
+  "killed_by": "tests/features.py",
+  "old": "    return dhw_store_of(p)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/dhw_charge_kw.RETURN_DEL.57a921d7.json b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_charge_kw.RETURN_DEL.57a921d7.json
new file mode 100644
index 000000000..61d4f9897
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_charge_kw.RETURN_DEL.57a921d7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_charge_kw RETURN_DEL 57a921d7",
+  "killed_by": "tests/features.py",
+  "old": "    return float(cop * heat_per_cop_kw(model.params, dhw_power_kw))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/dhw_mixed_litres.CLAMP_DROP.36b456aa.json b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_mixed_litres.CLAMP_DROP.36b456aa.json
new file mode 100644
index 000000000..f25f2099b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_mixed_litres.CLAMP_DROP.36b456aa.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_mixed_litres CLAMP_DROP 36b456aa",
+  "killed_by": "tests/features.py",
+  "old": "        return p.dhw_tank_volume * max(0.0, tank_c - store.inlet_c) / (mixed_c - store.inlet_c)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return p.dhw_tank_volume * (0.0) / (mixed_c - store.inlet_c)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/dhw_mixed_litres.CLAMP_DROP.a416a8fd.json b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_mixed_litres.CLAMP_DROP.a416a8fd.json
new file mode 100644
index 000000000..95dbaaa6c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_mixed_litres.CLAMP_DROP.a416a8fd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_mixed_litres CLAMP_DROP a416a8fd",
+  "killed_by": "tests/features.py",
+  "old": "    usable_kwh = store.capacity_kwh_per_c * max(0.0, tank_c - store.store_temp_for_tap(mixed_c))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`usable_kwh = store.capacity_kwh_per_c * (0.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/dhw_mixed_litres.GUARD_OFF.f078337e.json b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_mixed_litres.GUARD_OFF.f078337e.json
new file mode 100644
index 000000000..bdd598bd6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_mixed_litres.GUARD_OFF.f078337e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_mixed_litres GUARD_OFF f078337e",
+  "killed_by": "tests/features.py",
+  "old": "    if not store.combi:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/dhw_mixed_litres.RETURN_DEL.700dd13c.json b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_mixed_litres.RETURN_DEL.700dd13c.json
new file mode 100644
index 000000000..f6dc53264
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_mixed_litres.RETURN_DEL.700dd13c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_mixed_litres RETURN_DEL 700dd13c",
+  "killed_by": "tests/features.py",
+  "old": "    return usable_kwh / (WATER_SPECIFIC_HEAT * (mixed_c - store.inlet_c))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/dhw_store_of.CLAMP_DROP.15ca99bb.json b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_store_of.CLAMP_DROP.15ca99bb.json
new file mode 100644
index 000000000..54b150a91
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_store_of.CLAMP_DROP.15ca99bb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_store_of CLAMP_DROP 15ca99bb",
+  "killed_by": "tests/features.py",
+  "old": "        p.buffer_store_volume, min(p.dhw_max_temp, p.buffer_max_temp),",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`p.buffer_store_volume, (p.dhw_max_temp),`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/dhw_store_of.CLAMP_DROP.48a1fc65.json b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_store_of.CLAMP_DROP.48a1fc65.json
new file mode 100644
index 000000000..bd63ef2eb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_store_of.CLAMP_DROP.48a1fc65.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_store_of CLAMP_DROP 48a1fc65",
+  "killed_by": "tests/features.py",
+  "old": "    eps = min(1.0, eps) if eps >= COMBI_DHW_EFFECTIVENESS_FLOOR else COMBI_DHW_EFFECTIVENESS_FLOOR",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`eps = (1.0) if eps >= COMBI_DHW_EFFECTIVENESS_FLOOR else COMBI_DHW_EFFECTIVENESS_FLOOR`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/dhw_store_of.CLAMP_DROP.7e6f8a91.json b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_store_of.CLAMP_DROP.7e6f8a91.json
new file mode 100644
index 000000000..fdea895c6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_store_of.CLAMP_DROP.7e6f8a91.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_store_of CLAMP_DROP 7e6f8a91",
+  "killed_by": "tests/features.py",
+  "old": "        min(p.dhw_hard_max_temp, p.buffer_max_temp), eps,",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`(p.dhw_hard_max_temp), eps,`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/dhw_store_of.GUARD_OFF.f195744f.json b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_store_of.GUARD_OFF.f195744f.json
new file mode 100644
index 000000000..5c4e5ad58
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_store_of.GUARD_OFF.f195744f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_store_of GUARD_OFF f195744f",
+  "killed_by": "tests/features.py",
+  "old": "    if not p.combi_tank_active:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=88."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/store_step.CLAMP_DROP.c2b1e48b.json b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.CLAMP_DROP.c2b1e48b.json
new file mode 100644
index 000000000..755ac5b0a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.CLAMP_DROP.c2b1e48b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:store_step CLAMP_DROP c2b1e48b",
+  "killed_by": "tests/features.py",
+  "old": "        injected, new_temp = (floor - new_temp) * capacity / max(dt_hours, 1e-6), floor",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`injected, new_temp = (floor - new_temp) * capacity / (dt_hours), floor`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/store_step.CLAMP_DROP.dc05794e.json b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.CLAMP_DROP.dc05794e.json
new file mode 100644
index 000000000..121631d8f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.CLAMP_DROP.dc05794e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:store_step CLAMP_DROP dc05794e",
+  "killed_by": "tests/features.py",
+  "old": "    floor = min(store.inlet_c, ambient_temp)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`floor = (store.inlet_c)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/store_step.CLAMP_DROP.e56c36b8.json b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.CLAMP_DROP.e56c36b8.json
new file mode 100644
index 000000000..e905d8af6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.CLAMP_DROP.e56c36b8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:store_step CLAMP_DROP e56c36b8",
+  "killed_by": "tests/features.py",
+  "old": "    cap = max(0.0, store.rating_max_temp - temp) / max(dt_hours, 1e-6)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`cap = (0.0) / max(dt_hours, 1e-6)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=43. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/store_step.CMP_BOUND.7b7f231d.json b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.CMP_BOUND.7b7f231d.json
new file mode 100644
index 000000000..427389393
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.CMP_BOUND.7b7f231d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:store_step CMP_BOUND 7b7f231d",
+  "killed_by": "tests/features.py",
+  "old": "    if capacity <= 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if capacity < 0.0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/store_step.GUARD_OFF.09c88e0c.json b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.GUARD_OFF.09c88e0c.json
new file mode 100644
index 000000000..1b3a08c3d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.GUARD_OFF.09c88e0c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:store_step GUARD_OFF 09c88e0c",
+  "killed_by": "tests/features.py",
+  "old": "    if new_temp < floor:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/store_step.GUARD_OFF.7b7f231d.json b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.GUARD_OFF.7b7f231d.json
new file mode 100644
index 000000000..231636e65
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.GUARD_OFF.7b7f231d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:store_step GUARD_OFF 7b7f231d",
+  "killed_by": "tests/features.py",
+  "old": "    if capacity <= 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/store_step.GUARD_OFF.955429e2.json b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.GUARD_OFF.955429e2.json
new file mode 100644
index 000000000..7adc56af4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.GUARD_OFF.955429e2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:store_step GUARD_OFF 955429e2",
+  "killed_by": "tests/features.py",
+  "old": "    if d_temp > cap:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/store_step.RETURN_DEL.ceab1f1e.json b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.RETURN_DEL.ceab1f1e.json
new file mode 100644
index 000000000..dbfea5ddf
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.RETURN_DEL.ceab1f1e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:store_step RETURN_DEL ceab1f1e",
+  "killed_by": "tests/features.py",
+  "old": "    return new_temp, refused, injected, draw",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._dhw_legionella_ceilings.CLAMP_DROP.725a61cf.json b/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._dhw_legionella_ceilings.CLAMP_DROP.725a61cf.json
new file mode 100644
index 000000000..c48717940
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._dhw_legionella_ceilings.CLAMP_DROP.725a61cf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._dhw_legionella_ceilings CLAMP_DROP 725a61cf",
+  "old": "        max_temp = np.full(max(n_steps, 0), float(store.charge_max_temp))",
+  "reason": "Equivalent on every reachable input (CLAMP_DROP, `max(n_steps, 0)` -> `(n_steps)`): the two differ only for a negative `n_steps`, where `np.full` raises and the head returns an empty array, and no horizon carries one. `_dhw_legionella_ceilings` reads `h.n_steps`, which `HeatPumpOptimizer.optimize` sets to `min(len(prices), len(outdoor_temps), self.config.n_steps)`, two lengths and `OptimizationConfig.n_steps`'s `int(horizon_hours * 60 / time_step_minutes)` over a positive horizon; the other `_Horizon` builders carry a series length. The line beside it, `runup_temps = np.zeros(max(n_steps, 0))`, is the same idiom and unpinned at the merge base. Survival measured by the R10-COMBI-TANK repair fixer's mutant_run.py drive against tests/features.py's R10-COMBI-TANK blocks, and named unpinned by tests / mutation (job 128944437769) at 74df96f1, the mutation-autofix pin drive's own commit, so no driver of that drive killed it.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/thermal_model.py/dhw_store_of.CMP_BOUND.48a1fc65.json b/tests/mutation_ledger/survivor_triage/thermal_model.py/dhw_store_of.CMP_BOUND.48a1fc65.json
new file mode 100644
index 000000000..ea8751eca
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/thermal_model.py/dhw_store_of.CMP_BOUND.48a1fc65.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_store_of CMP_BOUND 48a1fc65",
+  "old": "    eps = min(1.0, eps) if eps >= COMBI_DHW_EFFECTIVENESS_FLOOR else COMBI_DHW_EFFECTIVENESS_FLOOR",
+  "reason": "Equivalent (CMP_BOUND, `eps >=` -> `eps >` COMBI_DHW_EFFECTIVENESS_FLOOR): the arms differ only at eps == the floor, where the head's `min(1.0, eps)` and the mutant's else arm are both the floor (0.1, below the 1.0 cap); NaN fails both comparisons alike. Measured by ``: the operator's own text compiled over `dhw_store_of`, against the head, over 11 effectiveness values holding the tie, NaN, inf and both of the floor's float neighbours: equiv_eps_differ=0. The tie-only control (`(min(1.0, eps) if eps != FLOOR else 0.5)` in the first arm) differs on the 1 tie and on 0 of the 10 others, so the grid reaches the tie.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/thermal_model.py/store_step.CMP_BOUND.09c88e0c.json b/tests/mutation_ledger/survivor_triage/thermal_model.py/store_step.CMP_BOUND.09c88e0c.json
new file mode 100644
index 000000000..162ce4c63
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/thermal_model.py/store_step.CMP_BOUND.09c88e0c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:store_step CMP_BOUND 09c88e0c",
+  "old": "    if new_temp < floor:",
+  "reason": "Equivalent (CMP_BOUND, `new_temp < floor` -> `new_temp <= floor`): the arms differ only at new_temp == floor, where the mutant's branch books `(floor - new_temp) * capacity / max(dt_hours, 1e-6)` = 0.0 injected and sets new_temp to the floor it already equals, so `store_step` returns the head's tuple bitwise. Measured by `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_combi_tank.py equiv`: the operator's own text compiled over `store_step`, against the head, over 56 steps of which 3 land exactly on the floor (C = 1, no loss or draw, ambient 8 below the inlet, an exact binary heat over dt): equiv_floor_differ=0. The tie-only control (`if new_temp == floor: injected += 1.0` ahead of the floor branch) differs on all 3 ties and 0 of the 53 others. `mutation_table.py --pin-killed` at this site cut tests/features.py's run as an exclusive tail (skip-budget-tail), so no driver verdict was read; the equivalence is the disposition.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/thermal_model.py/store_step.CMP_BOUND.955429e2.json b/tests/mutation_ledger/survivor_triage/thermal_model.py/store_step.CMP_BOUND.955429e2.json
new file mode 100644
index 000000000..7bee199e6
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/thermal_model.py/store_step.CMP_BOUND.955429e2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:store_step CMP_BOUND 955429e2",
+  "old": "    if d_temp > cap:",
+  "reason": "Equivalent (CMP_BOUND, `d_temp > cap` -> `d_temp >= cap`): the arms differ only at d_temp == cap, where the mutant's branch books `(d_temp - cap) * capacity` = 0.0 refused and sets d_temp to cap, which it already is, so `store_step` returns the head's tuple bitwise. Measured by ``: the operator's own text compiled over `store_step`, against the head, over 53 steps of which 3 are exact ties (C = 1, no loss or draw, the rating's distance over dt an exact binary fraction): equiv_step_differ=0. The tie-only control (`if d_temp == cap: refused += 1.0` ahead of the clamp) differs on all 3 ties and 0 of the 50 others.",
+  "verdict": "equivalent"
+}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/battery.py b/custom_components/heatpump_optimizer/battery.py
index 516320016..66b533806 100644
--- a/custom_components/heatpump_optimizer/battery.py
+++ b/custom_components/heatpump_optimizer/battery.py
@@ -320,15 +320,18 @@ def build(
         )
     )
 
-    if params.dhw_enabled:
+    # A combi store is the `buffer_tank` component below (combi implies
+    # `buffer_is_store`), so a `dhw_tank` beside it would count it twice.
+    store = params.dhw_store
+    if params.dhw_enabled and not store.combi:
         components.append(
             StorageComponent(
                 name="dhw_tank",
-                capacity_kwh_per_c=params.dhw_tank_thermal_mass,
+                capacity_kwh_per_c=store.capacity_kwh_per_c,
                 temperature=state.dhw_temperature,
                 min_temperature=dhw_min,
                 max_temperature=dhw_max,
-                loss_kw_per_c=params.dhw_tank_heat_loss_coefficient,
+                loss_kw_per_c=store.ua_kw_per_c,
                 ambient_temperature=20.0,
             )
         )
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index 3d34ee24a..2345eef0c 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -336,6 +336,7 @@ from .thermal_model import (
     ThermalParameters,
     ThermalState,
     channel_heating_steps,
+    dhw_mixed_litres,
     is_sunlit_interval,
     heat_loss_anchor_pair,
     heat_loss_basis,
@@ -4427,9 +4428,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         inlet = params.dhw_inlet_reference
         if 40.0 - inlet < 1.0:
             return {}
-        litres = (
-            params.dhw_tank_volume * max(0.0, float(tank) - inlet) / (40.0 - inlet)
-        )
+        litres = dhw_mixed_litres(params, float(tank), 40.0)
         flow = ctx._config.shower_flow_lpm
         out: DhwMixed = {"litres_40c": round(litres, 1), "tank_temperature": round(float(tank), 1)}
         if flow > 0:
@@ -4454,7 +4453,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         params = ctx._thermal_params
         if not params.dhw_enabled or not self._prices:
             return {}
-        c_dhw = params.dhw_tank_thermal_mass
+        c_dhw = params.dhw_store.capacity_kwh_per_c
         outdoor = float(ctx._current_state.outdoor_temperature)
         mean_price = _sweep_price(kwh_price, self._prices)
         # The heaviest ready energy any window needs, learned where
@@ -4490,7 +4489,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         for setpoint in range(48, 61, 2):
             t = float(setpoint)
             standby_kwh = (
-                params.dhw_tank_heat_loss_coefficient
+                params.dhw_store.ua_kw_per_c
                 * max(0.5 * (t + params.dhw_min_temp) - TANK_ROOM_AMBIENT_TEMP, 0.0)
                 * 24.0
             )
@@ -5141,7 +5140,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         )
         thermal_kw = params.max_electrical_power * max(cop, 1.0)
         if tank == "dhw":
-            capacity = params.dhw_tank_thermal_mass
+            capacity = params.dhw_store.capacity_kwh_per_c
         else:
             capacity = params.buffer_tank_thermal_mass
         if capacity <= 1e-6:
diff --git a/custom_components/heatpump_optimizer/dhw_learning.py b/custom_components/heatpump_optimizer/dhw_learning.py
index f6082202d..ef7e0bbf7 100644
--- a/custom_components/heatpump_optimizer/dhw_learning.py
+++ b/custom_components/heatpump_optimizer/dhw_learning.py
@@ -418,7 +418,7 @@ class DhwProfileLearner:
             / DHW_COOLING_REFERENCE_DELTA
         )
         intensity = max(0.0, temp_drop / dt_h - standby_rate)  # °C/h beyond standby
-        energy_kwh = intensity * dt_h * params.dhw_tank_thermal_mass
+        energy_kwh = intensity * dt_h * params.dhw_store.capacity_kwh_per_c
         windows = params.dhw_demand_windows
         label = draw_window_label(
             now.hour + now.minute / 60.0, windows
diff --git a/custom_components/heatpump_optimizer/dhw_planner.py b/custom_components/heatpump_optimizer/dhw_planner.py
index 97bee8dc7..c1972ac76 100644
--- a/custom_components/heatpump_optimizer/dhw_planner.py
+++ b/custom_components/heatpump_optimizer/dhw_planner.py
@@ -40,6 +40,7 @@ from .dhw_schedule import (
 from .manual_plan import _pin_is_free
 from .thermal_model import (
     TANK_ROOM_AMBIENT_TEMP,
+    DhwStore,
     ThermalModel,
     ThermalParameters,
     ThermalState,
@@ -101,6 +102,11 @@ def _tank_decay(ua: float, dt: float, c_dhw: float) -> tuple[float, float]:
     return float(np.clip(1.0 - ua * dt / c_dhw, 0.0, 1.0)), ua * TANK_ROOM_AMBIENT_TEMP * dt / c_dhw
 
 
+def _exo_at(exo_kw: np.ndarray | None, i: int) -> float:
+    """Step ``i`` of a combi store's space-side flux (``_DhwPlanContext.tank_exo_kw``), 0 off combi."""
+    return 0.0 if exo_kw is None else float(exo_kw[i])
+
+
 def _within_ceiling(requirement: Any, max_temp: Any) -> tuple[np.ndarray, np.ndarray]:
     """The requirement held to each step's own ceiling, and the ceiling, as float arrays.
 
@@ -244,10 +250,23 @@ class _DhwPlanContext:
     humidity: np.ndarray | None
     n_steps: int
     dt: float
-    c_dhw: float
+    store: DhwStore
     p_dhw_max: float
     min_run_power: float
     max_lead_steps: int
+    #: Combi: the space side's net flux into the shared store, kW per step,
+    #: which every recursion adds where it subtracts the draw; None off combi.
+    tank_exo_kw: np.ndarray | None = None
+
+    @property
+    def c_dhw(self) -> float:
+        """The store's capacity, kWh/K: the one value the planners divide by."""
+        return self.store.capacity_kwh_per_c
+
+    @property
+    def tank_decay(self) -> tuple[float, float]:
+        """The store's per-step ``_tank_decay`` (share kept, standby gain), for a positive capacity."""
+        return _tank_decay(self.store.ua_kw_per_c, self.dt, self.c_dhw)
 
 
 class _Horizon(Protocol):
@@ -370,7 +389,7 @@ class DhwPlanner:
             ),
             1e-3,
         )
-        standby_loss = p.dhw_tank_heat_loss_coefficient * max(
+        standby_loss = p.dhw_store.ua_kw_per_c * max(
             dhw_setpoint - TANK_ROOM_AMBIENT_TEMP, 0.0
         )
         # The reference house has no wood side, so no refill coil: whatever the
@@ -437,6 +456,7 @@ class DhwPlanner:
         p_dhw_run: float,
         dhw_prices: np.ndarray,
         off_steps: np.ndarray | None = None,
+        exo_kw: np.ndarray | None = None,
     ) -> tuple[bool, float | None, int | None]:
         """Whether the anti-legionella cycle is due, and which step it lands on.
 
@@ -481,15 +501,10 @@ class DhwPlanner:
             # and never retried. This is the same simulation every later
             # stage runs, so the two cannot disagree about what is reachable.
             off = _legionella_off_mask(off_steps, n_steps)
-            ramp = np.asarray(
-                self.model.simulate_dhw_only(
-                    initial_temp=float(initial_state.dhw_temperature),
-                    dhw_power_schedule=_legionella_charge(n_steps, p_dhw_run, off),
-                    outdoor_temps=outdoor_temps,
-                    draw_rates=draw_rates,
-                    dt_hours=dt,
-                    humidity=humidity,
-                )
+            ramp = self._dhw_plan_temps(
+                _legionella_charge(n_steps, p_dhw_run, off),
+                float(initial_state.dhw_temperature), outdoor_temps, draw_rates, dt,
+                humidity, exo_kw,
             )
             hot = np.where(ramp[1:] >= params.dhw_legionella_temp - 1e-6)[0]
             reach_step = int(hot[0]) if hot.size else n_steps
@@ -580,13 +595,13 @@ class DhwPlanner:
         h: _Horizon,
         *,
         params: ThermalParameters,
-        c_dhw: float,
         draw_rates: np.ndarray,
         floor_temps: np.ndarray,
         p_dhw_run: float,
         legionella_due: bool,
         legionella_hour: float | None,
         legionella_step: int | None,
+        exo_kw: np.ndarray | None = None,
     ) -> _DhwLegionellaPlan:
         """The tank ceilings and run-up floor the cycle needs, verbatim.
 
@@ -598,20 +613,21 @@ class DhwPlanner:
         dt = h.dt
         outdoor_temps = h.outdoor_temps
         humidity = h.humidity
-        max_temp = np.full(max(n_steps, 0), float(params.dhw_max_temp))
+        store = params.dhw_store
+        max_temp = np.full(max(n_steps, 0), float(store.charge_max_temp))
         lp_max_temp = max_temp
         # The run-up the cycle needs, as a per-step FLOOR. Folded into
         # ``requirement`` below rather than into ``ready_temps``, so the step
         # reason codes and the published "required now" keep meaning what
         # they meant.
         runup_temps = np.zeros(max(n_steps, 0))
-        boost_top = min(70.0, float(params.dhw_hard_max_temp))
+        boost_top = min(70.0, float(store.rating_max_temp))
+        c_dhw = store.capacity_kwh_per_c
         if c_dhw > 0.0 and legionella_step is not None and n_steps > 0 and (
-            boost_top > float(params.dhw_max_temp)
+            boost_top > float(store.charge_max_temp)
         ):
-            ua = params.dhw_tank_heat_loss_coefficient
-            decay, gain = _tank_decay(ua, dt, c_dhw)
-            everyday = float(params.dhw_max_temp)
+            decay, gain = _tank_decay(store.ua_kw_per_c, dt, c_dhw)
+            everyday = float(store.charge_max_temp)
             max_temp[legionella_step] = boost_top
 
             # Run-up: walk backwards along the fastest charge the pump can
@@ -646,7 +662,7 @@ class DhwPlanner:
                     0.5,
                 )
                 rise = delivered_heat_kw(params, cop, p_dhw_run) * dt / c_dhw
-                drawn = float(draw_rates[nxt]) * dt / c_dhw
+                drawn = (float(draw_rates[nxt]) - _exo_at(exo_kw, nxt)) * dt / c_dhw
                 need = (need + drawn - gain - rise) / max(decay, 1e-6)
                 if need > boost_top:
                     # Even starting AT the disinfection temperature the pump
@@ -688,7 +704,6 @@ class DhwPlanner:
         h: _Horizon,
         *,
         params: ThermalParameters,
-        c_dhw: float,
         hours_mod: np.ndarray,
         draw_rates: np.ndarray,
         ready_temps: np.ndarray,
@@ -696,6 +711,7 @@ class DhwPlanner:
         p_dhw_run: float,
         dhw_prices: np.ndarray,
         off_steps: np.ndarray | None = None,
+        exo_kw: np.ndarray | None = None,
     ) -> "_DhwLegionellaPlan":
         """The anti-legionella stage: when the cycle runs, and its ceilings.
 
@@ -713,17 +729,18 @@ class DhwPlanner:
             p_dhw_run=p_dhw_run,
             dhw_prices=dhw_prices,
             off_steps=off_steps,
+            exo_kw=exo_kw,
         )
         return self._dhw_legionella_ceilings(
             h,
             params=params,
-            c_dhw=c_dhw,
             draw_rates=draw_rates,
             floor_temps=floor_temps,
             p_dhw_run=p_dhw_run,
             legionella_due=legionella_due,
             legionella_hour=legionella_hour,
             legionella_step=legionella_step,
+            exo_kw=exo_kw,
         )
 
     def _dhw_coil_wood_forecast(
@@ -805,16 +822,17 @@ class DhwPlanner:
         wood_temps: np.ndarray | None,
         holiday_flags: np.ndarray | None = None,
     ) -> tuple[
-        float, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray
+        DhwStore, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray
     ]:
-        """Window mask, floors, ready temps, and the planner draw series."""
-        dhw_min_temp = params.dhw_min_temp
-        dhw_setpoint = params.dhw_setpoint
-        idle_min_temp = min(params.dhw_idle_min_temp, dhw_min_temp)
-        # The tank's own capacity, unfloored: the three planners this is
+        """The store, mask, store-frame floors and ready temps, and the draw series."""
+        # The store's own capacity, unfloored: the three planners this is
         # threaded into and the legionella run-up all read this one value
         # (D2-03, the class D2-01 closed in thermal_model.py).
-        c_dhw = params.dhw_tank_thermal_mass
+        store = params.dhw_store
+        c_dhw = store.capacity_kwh_per_c
+        dhw_min_temp = store.store_temp_for_tap(params.dhw_min_temp)
+        dhw_setpoint = params.dhw_setpoint
+        idle_min_temp = min(store.store_temp_for_tap(params.dhw_idle_min_temp), dhw_min_temp)
 
         hours_mod = np.asarray(step_hours, dtype=float) % 24.0
         # Weekly windows (#3): when the configured spec names days, the
@@ -902,7 +920,7 @@ class DhwPlanner:
                             0.0, p90
                         )
             standby_energy = (
-                params.dhw_tank_heat_loss_coefficient
+                store.ua_kw_per_c
                 * max(0.5 * (dhw_setpoint + dhw_min_temp) - TANK_ROOM_AMBIENT_TEMP, 0.0)
                 * window_hours
             )
@@ -921,7 +939,7 @@ class DhwPlanner:
             ready_idx = max(0, start_idx - 1)
             ready_temps[ready_idx] = max(ready_temps[ready_idx], required_ready)
         return (
-            c_dhw,
+            store,
             hours_mod,
             in_window,
             raw_draw_rates,
@@ -940,6 +958,7 @@ class DhwPlanner:
         blocked: bool = False,
         off_steps: np.ndarray | None = None,
         wood_temps: np.ndarray | None = None,
+        tank_exo_kw: np.ndarray | None = None,
     ) -> tuple[DhwPlan, np.ndarray]:
         """Build the DHW availability requirements and a cheapest-first plan.
 
@@ -969,7 +988,7 @@ class DhwPlanner:
         params = self.model.params
         windows, learned_windows = self._effective_dhw_windows()
         (
-            c_dhw,
+            store,
             hours_mod,
             in_window,
             raw_draw_rates,
@@ -986,6 +1005,7 @@ class DhwPlanner:
             wood_temps,
             holiday_flags,
         )
+        tank_exo_kw = store.space_flux(tank_exo_kw)
 
         # The pump serves DHW as an on/off block, not a trickle, so the planner
         # allocates at a realistic run power and never below the level at which
@@ -1019,7 +1039,6 @@ class DhwPlanner:
         ) = self._dhw_legionella_plan(
             h,
             params=params,
-            c_dhw=c_dhw,
             hours_mod=hours_mod,
             draw_rates=draw_rates,
             ready_temps=ready_temps,
@@ -1027,6 +1046,7 @@ class DhwPlanner:
             p_dhw_run=p_dhw_run,
             dhw_prices=dhw_prices,
             off_steps=off_steps,
+            exo_kw=tank_exo_kw,
         )
 
         # How long stored heat actually survives in this tank. The learned
@@ -1083,10 +1103,11 @@ class DhwPlanner:
             humidity=humidity,
             n_steps=n_steps,
             dt=dt,
-            c_dhw=c_dhw,
+            store=store,
             p_dhw_max=p_dhw_run,
             min_run_power=min_run_power,
             max_lead_steps=max_lead_steps,
+            tank_exo_kw=tank_exo_kw,
         )
 
         # Stage 1: a linear program over the whole horizon finds the truly
@@ -1124,6 +1145,7 @@ class DhwPlanner:
             min_run_power=min_run_power,
             max_temp=max_temp,
             humidity=humidity,
+            exo_kw=tank_exo_kw,
         )
 
         # Rounding weak slots down leaves energy the tank was counting on
@@ -1152,6 +1174,7 @@ class DhwPlanner:
             dt=dt,
             max_temp=max_temp,
             humidity=humidity,
+            exo_kw=tank_exo_kw,
         )
         schedule = np.where(schedule < min_run_power - 1e-9, 0.0, schedule)
 
@@ -1197,13 +1220,9 @@ class DhwPlanner:
         if getattr(initial_state, "external_heat_active", False) or getattr(
             initial_state, "peak_guard_active", False
         ):
-            free_temps = self.model.simulate_dhw_only(
-                initial_temp=initial_state.dhw_temperature,
-                dhw_power_schedule=np.zeros(n_steps),
-                outdoor_temps=outdoor_temps,
-                draw_rates=draw_rates,
-                dt_hours=dt,
-                humidity=humidity,
+            free_temps = self._dhw_plan_temps(
+                np.zeros(n_steps), initial_state.dhw_temperature, outdoor_temps,
+                draw_rates, dt, humidity, tank_exo_kw,
             )
             # Only suppress while coasting still meets the requirement. Running
             # out of hot water because a fire was assumed to keep burning is
@@ -1238,6 +1257,7 @@ class DhwPlanner:
                 dt=dt,
                 max_temp=max_temp,
                 humidity=humidity,
+                exo_kw=tank_exo_kw,
             )
             # Same hygiene as the automatic path: a step the rating truncated
             # below the pump's minimum cannot actually run, even a pinned one.
@@ -1370,15 +1390,15 @@ class DhwPlanner:
 
         requirement, max_temp = _within_ceiling(requirement, max_temp)
         params = self.model.params
-        ua = params.dhw_tank_heat_loss_coefficient
-        decay, gain = _tank_decay(ua, dt, c_dhw)
+        decay, gain = ctx.tank_decay
 
-        # Free trajectory: what the tank does with no heating at all.
+        # Free trajectory: the tank with no heating (in combi, under the space side's flux).
         free = np.zeros(n_steps + 1)
         free[0] = initial_temp
         for i in range(n_steps):
             free[i + 1] = (
-                decay * free[i] - float(draw_rates[i]) * dt / c_dhw + gain
+                decay * free[i]
+                - (float(draw_rates[i]) - _exo_at(ctx.tank_exo_kw, i)) * dt / c_dhw + gain
             )
 
         # Influence matrix: A[m, j] = degrees at step m+1 per thermal kWh at j.
@@ -1389,7 +1409,8 @@ class DhwPlanner:
         # COP is temperature dependent; solve once against the requirement
         # level, then re-solve against the trajectory the first pass produced.
         cop = self._dhw_cop_profile(
-            outdoor_temps, np.maximum(requirement, params.dhw_min_temp), humidity
+            outdoor_temps,
+            np.maximum(requirement, ctx.store.store_temp_for_tap(params.dhw_min_temp)), humidity
         )
 
         # --- Capacity contention with space heating -------------------------
@@ -1498,13 +1519,9 @@ class DhwPlanner:
 
             # Refine the COP estimate against the tank temperatures this plan
             # actually produces, so the cost ranking reflects reality.
-            temps = self.model.simulate_dhw_only(
-                initial_temp=initial_temp,
-                dhw_power_schedule=best,
-                outdoor_temps=outdoor_temps,
-                draw_rates=draw_rates,
-                dt_hours=dt,
-                humidity=humidity,
+            temps = self._dhw_plan_temps(
+                best, initial_temp, outdoor_temps, draw_rates, dt, humidity,
+                ctx.tank_exo_kw,
             )
             refined = self._dhw_cop_profile(outdoor_temps, temps[:-1], humidity)
             if np.allclose(refined, cop, rtol=0.02):
@@ -1546,6 +1563,7 @@ class DhwPlanner:
         humidity: np.ndarray | None,
         requirement: np.ndarray,
         unreachable: set[int],
+        exo_kw: np.ndarray | None = None,
     ) -> tuple[np.ndarray, np.ndarray, int | None]:
         """One round of a planner that fills breaches in time order: the tank
         trajectory under ``plan`` (re-simulated when ``temps`` is ``None``), the
@@ -1554,7 +1572,7 @@ class DhwPlanner:
         when there is none). The greedy planner and the floor repair share it."""
         if temps is None:
             temps = self._dhw_plan_temps(
-                plan, initial_temp, outdoor_temps, draw_rates, dt, humidity
+                plan, initial_temp, outdoor_temps, draw_rates, dt, humidity, exo_kw
             )
         gaps = requirement - temps[1 : plan.size + 1]
         for i in np.where(gaps > 0.05)[0]:
@@ -1570,6 +1588,7 @@ class DhwPlanner:
         draw_rates: np.ndarray,
         dt: float,
         humidity: np.ndarray | None = None,
+        exo_kw: np.ndarray | None = None,
     ) -> np.ndarray:
         return np.asarray(
             self.model.simulate_dhw_only(
@@ -1579,6 +1598,7 @@ class DhwPlanner:
                 draw_rates=draw_rates,
                 dt_hours=dt,
                 humidity=humidity,
+                exo_kw=exo_kw,
             )
         )
 
@@ -1637,7 +1657,7 @@ class DhwPlanner:
         # uses: heat added now is worth less later, so the ceiling bound
         # below can price how much of a top-up still survives at each step.
         params = self.model.params
-        decay, _ = _tank_decay(params.dhw_tank_heat_loss_coefficient, dt, c_dhw)
+        decay, _ = ctx.tank_decay
         # Breaches no ceiling-legal top-up can close. Skipped rather than
         # returned on: a demand window later in the day is not helped by
         # giving up at the first step the tank cannot quite reach, and a
@@ -1651,7 +1671,7 @@ class DhwPlanner:
         for _ in range(48):
             temps, deficit, b = self._dhw_shortfall(
                 temps, plan, initial_temp, outdoor_temps, draw_rates, dt,
-                humidity, req, unreachable,
+                humidity, req, unreachable, ctx.tank_exo_kw,
             )
             if b is None:
                 return plan
@@ -1756,6 +1776,7 @@ class DhwPlanner:
                     dt=dt,
                     max_temp=ceiling,
                     humidity=humidity,
+                    exo_kw=ctx.tank_exo_kw,
                 )
                 plan = np.where(plan < min_run_power - 1e-9, 0.0, plan)
                 if np.array_equal(plan, before):
@@ -1766,7 +1787,8 @@ class DhwPlanner:
                     unreachable.add(b)
                 else:
                     temps = self._dhw_plan_temps(
-                        plan, initial_temp, outdoor_temps, draw_rates, dt, humidity
+                        plan, initial_temp, outdoor_temps, draw_rates, dt, humidity,
+                        ctx.tank_exo_kw,
                     )
             else:
                 # Nothing ceiling-legal can fix this step; move on rather than
@@ -1783,6 +1805,7 @@ class DhwPlanner:
         dt: float,
         max_temp: np.ndarray,
         humidity: np.ndarray | None = None,
+        exo_kw: np.ndarray | None = None,
     ) -> np.ndarray:
         """Never deliver more heat than the tank has room for.
 
@@ -1814,9 +1837,8 @@ class DhwPlanner:
 
         ceiling = np.asarray(max_temp, dtype=float)
         params = self.model.params
-        capacity = params.dhw_tank_thermal_mass
-        ua = params.dhw_tank_heat_loss_coefficient
-        inlet = params.dhw_inlet_reference
+        store = params.dhw_store
+        capacity, ua, inlet = store.capacity_kwh_per_c, store.ua_kw_per_c, store.inlet_c
         temp = float(initial_temp)
 
         for i in range(len(plan)):
@@ -1856,11 +1878,12 @@ class DhwPlanner:
             # be heated — `allowed` comes out negative and floors at zero,
             # so the hours after a disinfection cycle stay closed to
             # re-heating exactly as before.
-            q_draw = float(draw_rates[i]) * dhw_draw_scale(temp, inlet)
+            q_draw = float(draw_rates[i]) * dhw_draw_scale(store.tap_temp_for_store(temp), inlet)
             q_loss = ua * (temp - TANK_ROOM_AMBIENT_TEMP)
             headroom_c = float(ceiling[i]) - temp
+            exo_i = _exo_at(exo_kw, i)
             allowed = power_for_heat_per_cop_kw(
-                params, (headroom_c * capacity / dt + q_draw + q_loss) / cop
+                params, (headroom_c * capacity / dt + q_draw + q_loss - exo_i) / cop
             )
             plan[i] = float(np.clip(plan[i], 0.0, max(0.0, allowed)))
 
@@ -1873,6 +1896,8 @@ class DhwPlanner:
                     hour_of_day=0.0,
                     dt_hours=dt,
                     draw_power=float(draw_rates[i]),
+                    exo_kw=exo_i,
+                    store=store,
                 )
             )
 
@@ -1889,6 +1914,7 @@ class DhwPlanner:
         min_run_power: float,
         max_temp: np.ndarray,
         humidity: np.ndarray | None = None,
+        exo_kw: np.ndarray | None = None,
     ) -> np.ndarray:
         """Round sub-minimum runs up to a power the pump can actually deliver.
 
@@ -1928,23 +1954,13 @@ class DhwPlanner:
         ceiling = np.asarray(max_temp, dtype=float)
         ceiling = np.concatenate([ceiling[:1], ceiling]) + 0.5
 
-        def trajectory(schedule: np.ndarray) -> np.ndarray:
-            return np.asarray(
-                self.model.simulate_dhw_only(
-                    initial_temp=initial_temp,
-                    dhw_power_schedule=schedule,
-                    outdoor_temps=outdoor_temps,
-                    draw_rates=draw_rates,
-                    dt_hours=dt,
-                    humidity=humidity,
-                )
-            )
-
         run_power = min(min_run_power, p_dhw_max)
-        base = trajectory(plan)
+        base = self._dhw_plan_temps(
+            plan, initial_temp, outdoor_temps, draw_rates, dt, humidity, exo_kw)
         joint = plan.copy()
         joint[weak] = run_power
-        joint_temps = trajectory(joint)
+        joint_temps = self._dhw_plan_temps(
+            joint, initial_temp, outdoor_temps, draw_rates, dt, humidity, exo_kw)
         joint_limit = np.maximum(
             ceiling[: joint_temps.size], base[: joint_temps.size]
         )
@@ -1966,7 +1982,7 @@ class DhwPlanner:
             candidate = base.copy()
             if self._dhw_raise_fits(
                 candidate, base, ceiling, slot, plan, outdoor_temps,
-                draw_rates, dt, humidity,
+                draw_rates, dt, humidity, exo_kw,
             ):
                 base = candidate
             else:
@@ -1977,7 +1993,7 @@ class DhwPlanner:
                 # reason as the check itself.
                 self.model.extend_dhw_temps(
                     base, slot, plan, outdoor_temps, draw_rates, dt_hours=dt,
-                    humidity=humidity,
+                    humidity=humidity, exo_kw=exo_kw,
                 )
         repaired: np.ndarray = np.clip(plan, 0.0, p_dhw_max)
         return repaired
@@ -1993,6 +2009,7 @@ class DhwPlanner:
         draw_rates: np.ndarray,
         dt: float,
         humidity: np.ndarray | None,
+        exo_kw: np.ndarray | None = None,
     ) -> bool:
         """Extend ``candidate`` from ``slot`` and say whether it stays in bounds.
 
@@ -2009,7 +2026,7 @@ class DhwPlanner:
             end = pos + _DHW_MIN_RUN_CHUNK
             self.model.extend_dhw_temps(
                 candidate, pos, plan[:end], outdoor_temps, draw_rates,
-                dt_hours=dt, humidity=humidity,
+                dt_hours=dt, humidity=humidity, exo_kw=exo_kw,
             )
             limit = np.maximum(ceiling[pos + 1: end + 1], base[pos + 1: end + 1])
             if not bool(np.all(candidate[pos + 1: end + 1] <= limit + 1e-9)):
@@ -2074,14 +2091,14 @@ class DhwPlanner:
         # Fraction of stored heat lost per hour of storage: raising the tank by
         # ΔT stores C·ΔT kWh but adds U·ΔT kW of standby loss.
         params = self.model.params
-        loss_rate_per_hour = params.dhw_tank_heat_loss_coefficient / c_dhw
+        loss_rate_per_hour = ctx.store.ua_kw_per_c / c_dhw
 
         unreachable: set[int] = set()
         temps: np.ndarray | None = None
         for _ in range(400):
             temps, gaps, k = self._dhw_shortfall(
                 temps, plan, initial_temp, outdoor_temps, draw_rates, dt,
-                humidity, requirement, unreachable,
+                humidity, requirement, unreachable, ctx.tank_exo_kw,
             )
             if k is None:
                 break
@@ -2171,6 +2188,7 @@ class DhwPlanner:
                     draw_rates,
                     dt_hours=dt,
                     humidity=humidity,
+                    exo_kw=ctx.tank_exo_kw,
                 )
                 break
 
diff --git a/custom_components/heatpump_optimizer/optimizer.py b/custom_components/heatpump_optimizer/optimizer.py
index a87b313cb..c6954961a 100644
--- a/custom_components/heatpump_optimizer/optimizer.py
+++ b/custom_components/heatpump_optimizer/optimizer.py
@@ -99,6 +99,8 @@ from .thermal_model import (
     _step_humidity,
     channel_heating_draw,
     channel_heating_steps,
+    combi_dhw_net_series,
+    combi_space_net_kw,
     levels_clamped,
     plan_step_runs,
     planned_draw_runs,
@@ -1379,6 +1381,72 @@ def _multi_start_minimize(
 PRICE_MEAN_GUESS_EPS = 1e-3
 
 
+def _with_buffer_exo(weather: WeatherSeries, buffer_exo_kw: np.ndarray | None) -> WeatherSeries:
+    """``weather`` carrying a combi store's hot-water flux, or as it is when there is none."""
+    return weather if buffer_exo_kw is None else replace(weather, buffer_exo_kw=buffer_exo_kw)
+
+
+def _combi_dhw_exo(
+    model: ThermalModel, h: _Horizon, schedule: np.ndarray, draw_rates: np.ndarray,
+    tank_exo_kw: np.ndarray | None = None,
+) -> np.ndarray | None:
+    """The hot-water side's net flux into a combi store along ``schedule``'s
+    own store walk (``combi_dhw_net_series``), the series the space solve
+    takes as ``buffer_exo_kw``; ``None`` off combi (R10-COMBI-TANK, Solver)."""
+    p = model.params
+    if not p.combi_tank_active:
+        return None
+    temps = model.simulate_dhw_only(
+        initial_temp=float(h.initial_state.dhw_temperature), dhw_power_schedule=schedule,
+        outdoor_temps=h.outdoor_temps, draw_rates=draw_rates, dt_hours=h.dt,
+        humidity=h.humidity, exo_kw=tank_exo_kw,
+    )
+    return combi_dhw_net_series(model, temps, schedule, draw_rates, h.outdoor_temps, h.humidity)
+
+
+#: Cap on the combi flux exchange's rounds, each a DHW plan build: each
+#: re-plans hot water against the space side's net flux under the previous
+#: round's plan, and a plan still moving at the cap is published as it stands
+#: (the `exchange` harness arm in dev/audit/harnesses/r10_combi_tank.py
+#: prints the rounds a plan takes).
+_COMBI_EXCHANGE_ROUNDS = 4
+
+
+def _combi_flux_exchange(
+    opt: HeatPumpOptimizer, h: _Horizon, planner: DhwPlanner, space_power: np.ndarray,
+    dhw_power: np.ndarray, draw_rates: np.ndarray, p_max: float,
+) -> np.ndarray:
+    """The hot-water plan for a combi store, re-planned against the fixed
+    space plan's net flux into it until it stops moving (R10-COMBI-TANK,
+    Solver): the space step takes the DHW side's flux as ``buffer_exo_kw``,
+    the DHW recursions take the space side's as ``tank_exo_kw``, so the heat
+    either side moves, and the standing loss, is counted once.
+
+    A feasibility repair, never a scored candidate: the first plan's store
+    breaches the hot-water floor the space side drains, so its score bounds
+    nothing, and a space re-solve would draw the repair straight back out.
+    """
+    model, store = opt.model, opt.model.params.dhw_store
+    weather = WeatherSeries.from_horizon(h)
+    space_net = None
+    for _ in range(_COMBI_EXCHANGE_ROUNDS):
+        dhw_exo = _combi_dhw_exo(model, h, dhw_power, draw_rates, space_net)
+        buffer_temps = model.simulate_trajectory(
+            initial_state=h.initial_state, power_schedule=space_power,
+            weather=_with_buffer_exo(weather, dhw_exo), dt_hours=h.dt,
+            valve_targets=h.valve_targets, start_hour=float(h.step_hours[0]))[4]
+        space_net = combi_space_net_kw(store, buffer_temps, dhw_exo, h.dt)
+        plan, opt._dhw_requirement = planner._build_dhw_requirements(
+            h, p_max=p_max, space_demand=space_power,
+            p_run_cap=None if h.power_caps_extra is None else float(np.min(h.power_caps_extra)),
+            blocked=h.dhw_blocked, off_steps=h.off_steps, tank_exo_kw=space_net,
+        )
+        if np.allclose(plan.schedule, dhw_power, atol=1e-4):
+            break
+        dhw_power = plan.schedule
+    return dhw_power
+
+
 def _price_guess_weights(prices: np.ndarray) -> np.ndarray:
     """Per-step initial-guess weight in [0.2, 1.0], high where cheap.
 
@@ -3193,6 +3261,7 @@ class HeatPumpOptimizer:
         solve_space: Callable[..., Any],
         p_max: float,
         planner: DhwPlanner,
+        draw_rates: np.ndarray | None = None,
     ) -> tuple[np.ndarray, np.ndarray, str]:
         """Re-plan hot water against the space heating it competes with.
 
@@ -3206,6 +3275,8 @@ class HeatPumpOptimizer:
         makes a single extra iteration safe rather than something that needs to
         run to convergence. The wood-tank coil (#400) re-plans here against
         the solved space heating's wood trajectory; no compressor pin required.
+        A combi store re-plans against the solved space side's net flux into
+        it (``combi_space_net_kw``, R10-COMBI-TANK), the flux exchange.
         """
         try:
             headroom = np.maximum(0.0, p_max - dhw_power)
@@ -3220,6 +3291,10 @@ class HeatPumpOptimizer:
                 raw = self.model.dhw_draw_rates(hours)
                 credited = planner._dhw_planner_draws(raw, wood_temps)
                 coil_replan = not np.allclose(credited, raw, atol=1e-9)
+            if draw_rates is not None and self.model.params.dhw_store.combi:
+                # A feasibility repair, not a scored candidate (its docstring).
+                return space_power, _combi_flux_exchange(
+                    self, h, planner, space_power, dhw_power, draw_rates, p_max), status
             if not bool(np.any(pinned)) and not coil_replan:
                 return space_power, dhw_power, status
 
@@ -4637,11 +4712,11 @@ class HeatPumpOptimizer:
         )
         energy_cost_of = self._energy_cost_fn(prices, dt)
 
-        def _space_traj(power_schedule: np.ndarray) -> Any:
+        def _space_traj(power_schedule: np.ndarray, buffer_exo_kw: Any = None) -> Any:
             return self.model.simulate_trajectory(
                 initial_state=initial_state,
                 power_schedule=power_schedule,
-                weather=weather,
+                weather=_with_buffer_exo(weather, buffer_exo_kw),
                 dt_hours=dt,
                 valve_targets=h.valve_targets,
                 start_hour=float(h.step_hours[0]),
@@ -4650,6 +4725,7 @@ class HeatPumpOptimizer:
         def objective(
             space_power: np.ndarray,
             dhw_plan_power: np.ndarray | None = None,
+            buffer_exo_kw: np.ndarray | None = None,
         ) -> float:
             """Compute the total cost with predictive weather anticipation."""
             space_power, dhw_plan_power = _realize_draw(
@@ -4657,7 +4733,7 @@ class HeatPumpOptimizer:
                 self.model.params.min_electrical_power, self.model.params.max_electrical_power,
             )
             room_temps, slab_temps, upper_temps, lower_temps, buffer_temps, _, _ = (
-                _space_traj(space_power)
+                _space_traj(space_power, buffer_exo_kw)
             )
 
             # The compressor is one machine: the grid sees the *combined*
@@ -4703,6 +4779,7 @@ class HeatPumpOptimizer:
         def objective_batch(
             space_matrix: np.ndarray,
             dhw_plan_power: np.ndarray | None = None,
+            buffer_exo_kw: np.ndarray | None = None,
         ) -> np.ndarray:
             """The same objective, for B schedules at once (issue #97).
 
@@ -4721,7 +4798,7 @@ class HeatPumpOptimizer:
             traj = self.model.simulate_trajectory_batch(
                 initial_state=initial_state,
                 power_matrix=space_matrix,
-                weather=weather,
+                weather=_with_buffer_exo(weather, buffer_exo_kw),
                 dt_hours=dt,
                 valve_targets=h.valve_targets,
                 start_hour=float(h.step_hours[0]),
@@ -5106,8 +5183,11 @@ class HeatPumpOptimizer:
         init_base = np.clip(init_base, p_min * 0.5, p_max * 0.8)
 
         def solve_space(
-            dhw_plan: np.ndarray, warm_start: np.ndarray | None
+            dhw_plan: np.ndarray, warm_start: np.ndarray | None,
+            tank_exo_kw: np.ndarray | None = None,
         ) -> tuple[np.ndarray, str, float]:
+            # Combi: the space solve sees this DHW plan's flux into the store.
+            exo = _combi_dhw_exo(self.model, h, dhw_plan, dhw_draw_rates, tank_exo_kw)
             return self._solve_space(
                 dhw_plan,
                 warm_start,
@@ -5117,8 +5197,9 @@ class HeatPumpOptimizer:
                 dt,
                 prices,
                 init_base,
-                objective,
-                objective_batch,
+                objective if exo is None else partial(objective, buffer_exo_kw=exo),
+                objective_batch if exo is None
+                else partial(objective_batch, buffer_exo_kw=exo),
             )
 
         # The seam between the DHW LP stage above and the gradient space
@@ -5137,6 +5218,7 @@ class HeatPumpOptimizer:
             solve_space=solve_space,
             p_max=p_max,
             planner=planner,
+            draw_rates=dhw_draw_rates,
         )
         optimal_space, optimal_dhw = _realize_joint(
             self.config.clamp_planned_levels, optimal_space, optimal_dhw,
@@ -5165,8 +5247,13 @@ class HeatPumpOptimizer:
             end_state=published_end,
         )
         # The achieved objective, for candidate comparison across valve
-        # schedules.
-        achieved_objective = float(objective(optimal_space, optimal_dhw))
+        # schedules; in combi, at the hot-water flux of the published walk.
+        achieved_objective = float(objective(
+            optimal_space, optimal_dhw,
+            combi_dhw_net_series(
+                self.model, buffer_temps, optimal_dhw, dhw_draw_rates, outdoor_temps, h.humidity)
+            if self.model.params.dhw_store.combi else None,
+        ))
 
         # Baseline cost. The reference holds the comfort schedule, not the comfort the plan
         # delivered (#2255): the baseline must not move with the plan's start.
@@ -5465,15 +5552,16 @@ class HeatPumpOptimizer:
             cap = caps.get(cap_key)
             return min(value, cap) if cap is not None else value
 
-        # (store, mass, COP-read temperature, reference end, plan end)
+        # (store, mass, COP-read temperature, reference end, plan end); a combi
+        # store already counted as the buffer is not counted again as DHW.
         tanks: list[tuple[str, float, float | None, float, float]] = []
         if p.two_zone_enabled:
             tanks.append(("buffer", p.buffer_tank_thermal_mass, caps.get("buffer"),
                           baseline_end.buffer_tank_temperature,
                           optimized_end.buffer_tank_temperature))
-        if include_dhw:
+        if include_dhw and not (p.dhw_store.combi and p.two_zone_enabled):
             dhw_cap = caps.get("dhw")
-            tanks.append(("dhw", p.dhw_tank_thermal_mass,
+            tanks.append(("dhw", p.dhw_store.capacity_kwh_per_c,
                           dhw_cap if dhw_cap is not None else p.dhw_setpoint,
                           baseline_end.dhw_temperature, optimized_end.dhw_temperature))
         for store, mass, cop_temp, ref_end, plan_end in tanks:
@@ -5706,8 +5794,8 @@ class HeatPumpOptimizer:
                 p.slab_thermal_mass * _t(state.slab_temperature, "slab")
                 + p.room_thermal_mass * _t(state.room_temperature, "room")
             )
-        if include_dhw:
-            stored += p.dhw_tank_thermal_mass * _t(state.dhw_temperature, "dhw")
+        if include_dhw and not (p.dhw_store.combi and p.two_zone_enabled):
+            stored += p.dhw_store.capacity_kwh_per_c * _t(state.dhw_temperature, "dhw")
         return float(stored)
 
     def _replay_end_state(
diff --git a/custom_components/heatpump_optimizer/thermal_model.py b/custom_components/heatpump_optimizer/thermal_model.py
index 7e3e08232..ff0358897 100644
--- a/custom_components/heatpump_optimizer/thermal_model.py
+++ b/custom_components/heatpump_optimizer/thermal_model.py
@@ -156,6 +156,16 @@ THERMAL_MASS_FLOOR: float = 0.1
 # it ``simulate_step`` subdivides only an extreme configuration.
 EULER_MONOTONE_MAX_RATIO: float = 1.0
 
+# Combi tank (#3225, R10-COMBI-TANK): one store of heating water serves the
+# space circuit and hot water through an exchanger whose effectiveness is
+# eps = (T_tap - T_in) / (T_store - T_in). The defaults are the design's
+# internal-coil preset (eps 0.85, 30 l of potable water in the coil); a value
+# below the floor is no real exchanger, and the floor keeps the tap-to-store
+# transform's divisor finite.
+COMBI_DHW_EFFECTIVENESS_DEFAULT: float = 0.85
+COMBI_DHW_EFFECTIVENESS_FLOOR: float = 0.1
+COMBI_POTABLE_VOLUME_DEFAULT_L: float = 30.0
+
 
 def _holiday_dhw_windows(config: Mapping[str, Any]) -> list[Window] | None:
     spec = config.get(const.CONF_HOLIDAY_DHW_WINDOWS)
@@ -299,6 +309,31 @@ class ThermalParameters:
     # optimizer it must become a hard constraint, because comfort and tank
     # limits there are soft penalties and the solver would plan to boil it.
     buffer_max_temp: float = 70.0  # °C
+    # Combi tank (#3225): hot water is drawn from the buffer store through an
+    # exchanger of effectiveness eps holding `combi_potable_volume_l` litres.
+    dhw_combi_tank_enabled: bool = False
+    combi_dhw_effectiveness: float = COMBI_DHW_EFFECTIVENESS_DEFAULT
+    combi_potable_volume_l: float = COMBI_POTABLE_VOLUME_DEFAULT_L
+
+    @property
+    def combi_tank_active(self) -> bool:
+        """Whether the DHW tank is the buffer store (R10-COMBI-TANK)."""
+        return (
+            self.dhw_combi_tank_enabled and self.dhw_enabled
+            and self.buffer_is_store and not self.dhw_coil_active
+        )
+
+    @property
+    def buffer_store_volume(self) -> float:
+        """The store's water in litres: in combi, the potable water inside it too."""
+        if self.combi_tank_active:
+            return self.buffer_tank_volume + self.combi_potable_volume_l
+        return self.buffer_tank_volume
+
+    @property
+    def dhw_store(self) -> DhwStore:
+        """The store every DHW recursion integrates: ``dhw_store_of``."""
+        return dhw_store_of(self)
 
     # --- Two-tank topology (issue #40) --------------------------------------
     #
@@ -598,7 +633,7 @@ class ThermalParameters:
     @property
     def buffer_tank_thermal_mass(self) -> float:
         """Thermal mass of buffer tank in kWh/°C."""
-        return self.buffer_tank_volume * WATER_SPECIFIC_HEAT
+        return self.buffer_store_volume * WATER_SPECIFIC_HEAT
 
     @property
     def buffer_tank_heat_loss_coefficient(self) -> float:
@@ -620,14 +655,15 @@ class ThermalParameters:
         # volume^(2/3), while the rate is UA/C and so falls as volume^(-1/3).
         # Clamping every size against a 35 L tank's numbers is what floored a
         # large accumulator an order of magnitude above its real standby loss.
-        key = (self.buffer_tank_volume, self.buffer_cooling_rate)
+        volume = self.buffer_store_volume
+        key = (volume, self.buffer_cooling_rate)
         cached = self._buffer_ua_cache
         if cached is not None and cached[0] == key:
             return cached[1]
-        low, high = buffer_cooling_rate_bounds(self.buffer_tank_volume)
+        low, high = buffer_cooling_rate_bounds(volume)
         rate = self.buffer_cooling_rate
         if rate <= 0.0:
-            rate = default_buffer_cooling_rate(self.buffer_tank_volume)
+            rate = default_buffer_cooling_rate(volume)
         # min/max rather than np.clip: this is a scalar, and np.clip on a
         # Python float costs about six microseconds, which at a few million
         # calls per solve is seconds for nothing.
@@ -1846,6 +1882,194 @@ def _buffer_capacity(p: ThermalParameters) -> float:
     return 0.04 if c_buf < 1e-6 else c_buf
 
 
+@dataclass(frozen=True, slots=True)
+class DhwStore:
+    """The store the hot-water recursions integrate (R10-COMBI-TANK design, Shape).
+
+    Off combi: the separate DHW tank's own values, and both transforms are the
+    identity (they return their argument, so every plan is byte-identical).
+    In combi: the buffer store, one mixed node, seen through the exchanger. A
+    limit stated at the tap enters the store frame through
+    ``store_temp_for_tap``; a store temperature reaches the tap through
+    ``tap_temp_for_store``. The legionella target is a store temperature
+    (standing water reaches the store's own), so it never passes through either.
+    """
+
+    capacity_kwh_per_c: float
+    ua_kw_per_c: float
+    volume_l: float
+    charge_max_temp: float
+    rating_max_temp: float
+    effectiveness: float
+    inlet_c: float
+    combi: bool
+
+    def store_temp_for_tap(self, tap_c: float) -> float:
+        """The store temperature at which the tap delivers ``tap_c``."""
+        if not self.combi:
+            return tap_c
+        return self.inlet_c + (tap_c - self.inlet_c) / self.effectiveness
+
+    def tap_temp_for_store(self, store_c: float) -> float:
+        """The tap temperature a store at ``store_c`` delivers."""
+        if not self.combi:
+            return store_c
+        return self.inlet_c + self.effectiveness * (store_c - self.inlet_c)
+
+    def space_flux(self, space_net_kw: np.ndarray | None) -> np.ndarray | None:
+        """The space side's net flux as this store sees it: a separate tank
+        shares no water with the space side, so for it the series is dead."""
+        return space_net_kw if self.combi else None
+
+
+def combi_store_of(p: ThermalParameters) -> DhwStore | None:
+    """The combi store, or None off combi: read once per walk, never per step."""
+    if not p.combi_tank_active:
+        return None
+    return dhw_store_of(p)
+
+
+def dhw_store_of(p: ThermalParameters) -> DhwStore:
+    """``ThermalParameters.dhw_store``: the separate tank, or the combi store.
+
+    In combi the capacity and loss are the buffer's (over the store volume,
+    potable water included), the charge limit and rating are the tighter of
+    the DHW and buffer ones, and an effectiveness that is not a number above
+    the floor reads as the floor, the guard ``ThermalParameters.clamp`` gives
+    every divisor.
+    """
+    if not p.combi_tank_active:
+        return DhwStore(
+            p.dhw_tank_thermal_mass, p.dhw_tank_heat_loss_coefficient,
+            p.dhw_tank_volume, p.dhw_max_temp, p.dhw_hard_max_temp, 1.0,
+            p.dhw_inlet_reference, False,
+        )
+    eps = float(p.combi_dhw_effectiveness)
+    eps = min(1.0, eps) if eps >= COMBI_DHW_EFFECTIVENESS_FLOOR else COMBI_DHW_EFFECTIVENESS_FLOOR
+    return DhwStore(
+        _buffer_capacity(p), p.buffer_tank_heat_loss_coefficient,
+        p.buffer_store_volume, min(p.dhw_max_temp, p.buffer_max_temp),
+        min(p.dhw_hard_max_temp, p.buffer_max_temp), eps,
+        p.dhw_inlet_reference, True,
+    )
+
+
+def store_step(
+    store: DhwStore, temp: float, heat_in_kw: float, draw_nominal_kw: float,
+    ambient_temp: float, dt_hours: float,
+) -> tuple[float, float, float, float]:
+    """One step of a hot-water store, the separate tank and the combi store
+    alike: ``(new temp, refused kW, floor-injected kW, draw kW)``.
+
+    ``heat_in_kw`` is everything entering the node but the draw and the
+    standing loss: the pump's DHW charge, plus in combi the space side's net
+    flux. The three rules, each booked so the step balances exactly,
+    ``C * dT = (heat_in - draw - loss - refused + injected) * dt``:
+
+    * The draw is the NOMINAL demand (volume heated from the inlet to the
+      setpoint) debited at the TAP temperature through ``dhw_draw_scale``. At
+      or above the 40 °C mixed-use temperature the tap mixes, so the enthalpy
+      removed stays nominal (the ``MixedHotWater`` convention); below it the
+      store delivers only the rise it holds. Referencing the setpoint instead
+      under-debited the 40..setpoint band by up to a third and booked the
+      deleted demand as savings (v4.0.5 review). Demand-side quantities (the
+      planner's ready-energy targets, the always-hot baseline) stay nominal.
+    * The rating clamps only the charging direction, and the refused heat is
+      booked, never deleted: the published trajectory replays pinned plans
+      and legionella boosts that no planner pre-clamped. The rating, not the
+      everyday charge limit, or a disinfection boost would silently fall short.
+    * The floor is the inlet or the surroundings, whichever is lower: an inlet
+      above ambient would make the floor a heat source with no physical
+      origin (R6-D2-02). With the scaled draw it is a no-op safety bound, and
+      any heat it does fabricate is booked.
+    """
+    capacity = store.capacity_kwh_per_c
+    if capacity <= 0.0:
+        return temp, 0.0, 0.0, 0.0
+    draw = draw_nominal_kw * dhw_draw_scale(store.tap_temp_for_store(temp), store.inlet_c)
+    d_temp = (heat_in_kw - draw - store.ua_kw_per_c * (temp - ambient_temp)) / capacity
+    cap = max(0.0, store.rating_max_temp - temp) / max(dt_hours, 1e-6)
+    refused = 0.0
+    if d_temp > cap:
+        refused, d_temp = (d_temp - cap) * capacity, cap
+    new_temp = temp + d_temp * dt_hours
+    floor = min(store.inlet_c, ambient_temp)
+    injected = 0.0
+    if new_temp < floor:
+        injected, new_temp = (floor - new_temp) * capacity / max(dt_hours, 1e-6), floor
+    return new_temp, refused, injected, draw
+
+
+def dhw_mixed_litres(p: ThermalParameters, tank_c: float, mixed_c: float) -> float:
+    """Litres of ``mixed_c`` water the hot-water store at ``tank_c`` holds (#28).
+
+    The separate tank: its volume delivered by displacement and mixed down,
+    ``V * (T - T_in) / (T_mix - T_in)``. A combi store, one mixed node: the
+    heat above the store temperature at which the tap stops reaching
+    ``mixed_c``, over what a litre of it takes from the inlet. The caller
+    refuses ``mixed_c`` within a kelvin of the inlet.
+    """
+    store = p.dhw_store
+    if not store.combi:
+        return p.dhw_tank_volume * max(0.0, tank_c - store.inlet_c) / (mixed_c - store.inlet_c)
+    usable_kwh = store.capacity_kwh_per_c * max(0.0, tank_c - store.store_temp_for_tap(mixed_c))
+    return usable_kwh / (WATER_SPECIFIC_HEAT * (mixed_c - store.inlet_c))
+
+
+def combi_dhw_net_kw(
+    model: ThermalModel, store: DhwStore, temp: float, dhw_power_kw: float,
+    draw_nominal_kw: float, outdoor_temp: float, humidity: float | None = None,
+) -> float:
+    """The hot-water side's net flux into a combi store at ``temp``, kW: the
+    pump's DHW charge at its COP less the draw debited at the tap
+    (``store_step``'s two terms). What the space step sees as
+    ``buffer_exo_kw``."""
+    return (
+        dhw_charge_kw(model, temp, dhw_power_kw, outdoor_temp, humidity)
+        - draw_nominal_kw * dhw_draw_scale(store.tap_temp_for_store(temp), store.inlet_c)
+    )
+
+
+def dhw_charge_kw(
+    model: ThermalModel, temp: float, dhw_power_kw: float, outdoor_temp: float,
+    humidity: float | None = None,
+) -> float:
+    """The heat a DHW draw of ``dhw_power_kw`` puts into a store at ``temp``,
+    at the DHW COP: the charge term of the separate tank and the combi store."""
+    cop = model.compute_cop_dhw(outdoor_temp, temp, humidity=humidity)
+    return float(cop * heat_per_cop_kw(model.params, dhw_power_kw))
+
+
+def combi_dhw_net_series(
+    model: ThermalModel, temps: Any, dhw_power: Any, draw_rates: Any,
+    outdoor_temps: Any, humidity: Any = None,
+) -> np.ndarray:
+    """``combi_dhw_net_kw`` per step along a DHW plan's own store trajectory
+    ``temps`` (length n + 1): the series the space solve takes as
+    ``WeatherSeries.buffer_exo_kw``."""
+    store = model.params.dhw_store
+    return np.array([
+        combi_dhw_net_kw(
+            model, store, float(temps[i]), float(dhw_power[i]), float(draw_rates[i]),
+            float(outdoor_temps[i]), None if humidity is None else float(humidity[i]))
+        for i in range(len(dhw_power))
+    ])
+
+
+def combi_space_net_kw(
+    store: DhwStore, buffer_temps: Any, dhw_net_kw: Any, dt_hours: float,
+) -> np.ndarray:
+    """The space side's net flux into a combi store, kW per step: what the
+    store gained along a space trajectory, plus its standing loss, less the
+    hot-water flux that trajectory was simulated with. The series the DHW
+    planner's recursions take as ``tank_exo_kw``, so heat moved by either side
+    is counted once and the loss once (R10-COMBI-TANK design, Solver)."""
+    temps = np.asarray(buffer_temps, dtype=float)
+    gained = store.capacity_kwh_per_c * np.diff(temps) / max(dt_hours, 1e-6)
+    loss = store.ua_kw_per_c * (temps[:-1] - TANK_ROOM_AMBIENT_TEMP)
+    return gained + loss - np.asarray(dhw_net_kw, dtype=float)
+
+
 def _valve_ua(p: ThermalParameters) -> float:
     """Every emitter's conductance behind a valve, kW/K, backed out of the
     nameplate output at the design flow-to-zone difference."""
@@ -2734,6 +2958,10 @@ class WeatherSeries:
     solar_radiation: np.ndarray | None = None
     humidity: np.ndarray | None = None
     external_heat_kw: np.ndarray | None = None
+    #: Combi store (R10-COMBI-TANK): the hot-water side's net flux into the
+    #: buffer, kW per step, signed; ``None`` off combi. Not weather, but like
+    #: ``external_heat_kw`` an exogenous flux the space physics consumes.
+    buffer_exo_kw: np.ndarray | None = None
 
     @classmethod
     def from_horizon(cls, h: Any) -> "WeatherSeries":
@@ -2755,21 +2983,13 @@ class ThermalModel:
 
     #: Per-step scratch for buffer cap refusal, written by the step function.
     _step_buffer_refused: float = 0.0
-    #: DHW analogue of the buffer's refused-heat ledger (v4.0.5). The DHW
-    #: step now clamps charging at the tank rating instead of trusting every
-    #: caller to pre-clamp, and heat the rating refuses is booked here (kW)
-    #: rather than silently deleted — the same reasoning as the buffer: a
-    #: trajectory that pays for deleted heat is merely wasteful in the model
-    #: but boils the tank on the real system.
+    #: The DHW step's three booked terms, kW (``store_step`` states the rules):
+    #: heat the rating refused (v4.0.5: a trajectory paying for deleted heat
+    #: boils the real tank), heat the inlet floor fabricated (non-zero is a
+    #: conservation bug, and the tests assert it), and the draw actually
+    #: debited, so accounting outside the model balances the step exactly.
     _step_dhw_refused: float = 0.0
-    #: Heat the inlet floor would have had to fabricate this step (kW). With
-    #: the temperature-dependent draw the floor is a genuine no-op safety
-    #: bound — the draw vanishes as the tank approaches the inlet — so any
-    #: non-zero value here is a conservation bug, and the tests assert it.
     _step_dhw_floor_injected: float = 0.0
-    #: The draw the DHW step actually debited (kW), after tank-temperature
-    #: scaling. Recorded so energy accounting outside the model can balance
-    #: the step exactly instead of assuming the nominal demand was met.
     _step_dhw_draw_kw: float = 0.0
     #: Wood-tank analogue of the buffer/DHW refused-heat ledgers (R5-D2-01).
     #: The 95 °C ceiling clamps the external-heat forecast's charge rate, and
@@ -3148,8 +3368,9 @@ class ThermalModel:
         # disinfection cycle is a few hours a week, and sizing the pre-heat
         # horizon off a temperature the tank only sees during one would
         # over-state how far ahead ordinary hot water may be bought.
-        top = max(p.dhw_max_temp, p.dhw_min_temp + 1.0)
-        floor = p.dhw_min_temp
+        store = p.dhw_store
+        floor = store.store_temp_for_tap(p.dhw_min_temp)
+        top = max(store.charge_max_temp, floor + 1.0)
         return self.dhw_coast_hours(top, floor)
 
     def dhw_coast_hours(
@@ -3173,8 +3394,8 @@ class ThermalModel:
         # One store, read twice (D2-01): `ua` is built from this same mass, so
         # `C/ua` is `delta/rate` by construction -- a floor on *either* is a
         # disagreement, not a guard. A zero coefficient is the only guard left.
-        c_dhw = p.dhw_tank_thermal_mass
-        ua = p.dhw_tank_heat_loss_coefficient
+        store = p.dhw_store
+        c_dhw, ua = store.capacity_kwh_per_c, store.ua_kw_per_c
         hot = from_temp - ambient_temp
         cold = to_temp - ambient_temp
         if hot <= 0.0:
@@ -3192,8 +3413,10 @@ class ThermalModel:
         ambient_temp: float = TANK_ROOM_AMBIENT_TEMP,
         dt_hours: float = 0.25,
         draw_power: float | None = None,
+        exo_kw: float = 0.0,
+        store: DhwStore | None = None,
     ) -> float:
-        """Simulate one time step of DHW tank dynamics.
+        """Simulate one time step of DHW tank dynamics (``store_step``).
 
         Args:
             dhw_temp: Current DHW tank temperature (°C)
@@ -3201,93 +3424,22 @@ class ThermalModel:
             hour_of_day: Current hour (0-24) for draw pattern
             ambient_temp: Ambient temperature near the tank (°C)
             dt_hours: Time step (hours)
-            draw_power: Pre-computed draw power (kW); avoids recomputing the
-                hourly pattern inside hot optimization loops.
+            draw_power: Pre-computed nominal draw power (kW); avoids recomputing
+                the hourly pattern inside hot optimization loops.
+            exo_kw: In combi, the space side's net flux into the shared store.
+            store: The parameters' ``dhw_store``, hoisted by a walk; None reads it.
 
         Returns:
-            New DHW tank temperature (°C)
+            New DHW tank temperature (°C); the refused, floor-injected and
+            debited heat of the step are booked on the ``_step_dhw_*`` ledgers.
         """
-        p = self.params
-        self._step_dhw_refused = 0.0
-        self._step_dhw_floor_injected = 0.0
-        self._step_dhw_draw_kw = 0.0
-        C_dhw = p.dhw_tank_thermal_mass
-        if C_dhw <= 0.0:
-            return dhw_temp
-
-        # Heat input from heat pump
-        q_in = dhw_power_thermal
-
-        # Heat drawn by consumption. The passed/pattern value is the NOMINAL
-        # demand — volume heated from the inlet to the setpoint — and that is
-        # what a tank at or above the setpoint genuinely supplies: mixing at
-        # the tap shrinks the drawn volume so the enthalpy removed stays
-        # exactly nominal (the `MixedHotWater` convention,
-        # coordinator._dhw_mixed_water). A colder tank cannot be debited
-        # energy referenced to a rise it does not hold, so the debit scales
-        # with the rise it can actually deliver:
-        #
-        #     q_eff = q_nominal · min(1, (T − inlet) / (T_use − inlet))
-        #
-        # with T_use the 40 °C mixed-water temperature: the tap draws MORE
-        # volume from a cooler tank to make the same mixed water, so the
-        # enthalpy removed stays exactly nominal all the way down to T_use,
-        # and only below it does the service itself degrade. Referencing the
-        # setpoint instead under-debited the 40..setpoint band — the very
-        # band cost optimization rides — by up to a third, and booked the
-        # deleted demand as savings (v4.0.5 review, blocker). Unscaled, a
-        # 30 °C tank was charged the full (setpoint − inlet) per litre and
-        # the inlet floor below silently refunded the fabricated deficit.
-        # Demand-side quantities (planner ready-energy targets, the
-        # always-hot baseline) stay nominal on purpose: what the user wants
-        # delivered does not shrink because the tank is cold.
-        q_draw = (
-            self.dhw_draw_rate(hour_of_day) if draw_power is None else draw_power
+        q_draw = self.dhw_draw_rate(hour_of_day) if draw_power is None else draw_power
+        (new_temp, self._step_dhw_refused, self._step_dhw_floor_injected,
+         self._step_dhw_draw_kw) = store_step(
+            self.params.dhw_store if store is None else store, dhw_temp,
+            dhw_power_thermal + exo_kw if exo_kw else dhw_power_thermal,
+            q_draw, ambient_temp, dt_hours,
         )
-        q_draw = q_draw * dhw_draw_scale(dhw_temp, p.dhw_inlet_reference)
-        self._step_dhw_draw_kw = q_draw
-
-        # Standby heat loss to ambient
-        q_loss = p.dhw_tank_heat_loss_coefficient * (dhw_temp - ambient_temp)
-
-        # Temperature change
-        dT = (q_in - q_draw - q_loss) / C_dhw
-
-        # The tank rating, enforced in the model itself rather than trusted
-        # to every caller's pre-clamp: the DHW planner's `_clamp_dhw_to_capacity`
-        # protects planned schedules, but the published trajectory also
-        # replays pinned plans and legionella boosts, and those paths could
-        # exceed the rating with no accounting. Same shape as the buffer
-        # clamp: only the charging direction is limited (a tank read above
-        # the rating cools at its physical rate, it is not snapped down),
-        # and the refused heat is booked, never deleted.
-        # The *rating*, not the everyday charge limit: a disinfection boost is
-        # meant to go above the user's charge limit, and clamping it here
-        # would make the cycle silently fail to reach temperature. The
-        # everyday limit is enforced per step by the planner instead.
-        dT_cap = max(0.0, p.dhw_hard_max_temp - dhw_temp) / max(dt_hours, 1e-6)
-        if dT > dT_cap:
-            self._step_dhw_refused = (dT - dT_cap) * C_dhw
-            dT = dT_cap
-        new_temp = dhw_temp + dT * dt_hours
-
-        # Physical bound: the tank cannot fall below its surroundings, which
-        # sit at `ambient_temp` (20 °C indoors), nor below the cold-water inlet
-        # it refills at — whichever is lower. With the scaled draw the floor is
-        # a genuine no-op safety bound: the draw vanishes as the tank
-        # approaches the inlet, and an inlet below ambient is warmed by its own
-        # standby "loss". The bound is clamped to ambient because an inlet
-        # above ambient would otherwise pin the tank there and turn the floor
-        # into a heat source with no physical origin (R6-D2-02). Any heat the
-        # bound does have to fabricate is booked so the energy balance stays
-        # honest instead of silently created.
-        floor = min(p.dhw_inlet_reference, ambient_temp)
-        if new_temp < floor:
-            self._step_dhw_floor_injected = (
-                (floor - new_temp) * C_dhw / max(dt_hours, 1e-6)
-            )
-            new_temp = floor
-
         return new_temp
 
     def simulate_dhw_only(
@@ -3298,11 +3450,13 @@ class ThermalModel:
         draw_rates: np.ndarray,
         dt_hours: float = 0.25,
         humidity: np.ndarray | None = None,
+        exo_kw: np.ndarray | None = None,
     ) -> np.ndarray:
         """Simulate the DHW tank alone (used for fast schedule planning).
 
         Returns an array of length ``n_steps + 1`` starting at ``initial_temp``.
-        ``humidity`` is the forecast series the published trajectory uses (#1520).
+        ``humidity`` is the forecast series the published trajectory uses (#1520);
+        ``exo_kw`` the combi store's space-side flux, per step (``simulate_dhw_step``).
         """
         schedule = np.asarray(dhw_power_schedule, dtype=float)
         n_steps = schedule.size
@@ -3316,6 +3470,7 @@ class ThermalModel:
             draw_rates,
             dt_hours=dt_hours,
             humidity=humidity,
+            exo_kw=exo_kw,
         )
 
     def extend_dhw_temps(
@@ -3327,6 +3482,7 @@ class ThermalModel:
         draw_rates: np.ndarray,
         dt_hours: float = 0.25,
         humidity: np.ndarray | None = None,
+        exo_kw: np.ndarray | None = None,
     ) -> np.ndarray:
         """Refresh ``temps[from_step + 1:]`` after the schedule changed there."""
         heat_per_cop = heat_per_cop_kw(self.params, np.asarray(dhw_power_schedule, dtype=float))
@@ -3335,6 +3491,7 @@ class ThermalModel:
         temp = float(temps[from_step])
         compute_cop = self.compute_cop_dhw
         simulate_step = self.simulate_dhw_step
+        store = self.params.dhw_store
         for i in range(from_step, heat_per_cop.size):
             cop = compute_cop(
                 outdoor[i], temp, humidity=None if humidity is None else humidity[i]
@@ -3345,6 +3502,8 @@ class ThermalModel:
                 hour_of_day=0.0,
                 dt_hours=dt_hours,
                 draw_power=draws[i],
+                exo_kw=0.0 if exo_kw is None else float(exo_kw[i]),
+                store=store,
             )
             temps[i + 1] = temp
         return temps
@@ -3367,6 +3526,7 @@ class ThermalModel:
         hour_of_day: float | None = None,
         measured_heat_kw: float | None = None,
         valve_target: float | None = None,
+        buffer_exo_kw: float = 0.0,
         _cop: float | None = None,
         _u_eff: float | None = None,
         _q_solar: float | None = None,
@@ -3432,7 +3592,7 @@ class ThermalModel:
         new_buf = state.buffer_tank_temperature
         if throttled:
             q_slab, dT_buf, refused = _single_valve_rates(
-                p, new_buf, state.slab_temperature, thermal_power,
+                p, new_buf, state.slab_temperature, thermal_power + buffer_exo_kw,
                 outdoor_temp, u_eff, valve_target, dt_hours,
             )
             thermal_power, new_buf = float(q_slab), float(new_buf + dT_buf * dt_hours)
@@ -3479,6 +3639,7 @@ class ThermalModel:
         humidity: float | None = None,
         hour_of_day: float | None = None,
         measured_heat_kw: float | None = None,
+        buffer_exo_kw: float = 0.0,
         _loss: tuple[float, float] | None = None,
     ) -> ThermalState:
         """Simulate one step with the two-zone model including buffer tank.
@@ -3528,6 +3689,8 @@ class ThermalModel:
             else measured_heat_kw
         )
         thermal_power = pump_heat_kw + (0.0 if two_tank else ext)
+        if throttled and buffer_exo_kw:
+            thermal_power += buffer_exo_kw
 
         u_upper, u_lower = (
             self._zone_loss(wind_speed, precipitation) if _loss is None else _loss
@@ -3656,6 +3819,7 @@ class ThermalModel:
         humidity: float | None = None,
         hour_of_day: float | None = None,
         measured_heat_kw: float | None = None,
+        buffer_exo_kw: float = 0.0,
     ) -> ThermalState:
         """Simulate one time step (dispatches to single or two-zone).
 
@@ -3676,7 +3840,8 @@ class ThermalModel:
         (``flow_meter.read_heat_output_kw``) refuses a reading that is stale,
         negative, of an unknown unit or no warmer than the return, and only
         the two interval learners, which replay one elapsed step, ever have
-        one to pass.
+        one to pass. ``buffer_exo_kw`` is ``WeatherSeries.buffer_exo_kw``'s
+        step, which joins the tank's input behind the valve.
         """
         # Only a throttled step books the buffer cap, so the scratch would
         # otherwise carry a stale value from an earlier step. The wood
@@ -3703,7 +3868,7 @@ class ThermalModel:
                     state, electrical_power, outdoor_temp,
                     wind_speed, precipitation, solar_radiation, dt_hours,
                     external_heat_kw, valve_target, humidity, hour_of_day,
-                    measured_heat_kw=measured_heat_kw,
+                    measured_heat_kw=measured_heat_kw, buffer_exo_kw=buffer_exo_kw,
                     _loss=(u_first, u_second),
                 )
             refused = 0.0
@@ -3714,7 +3879,7 @@ class ThermalModel:
                     wind_speed, precipitation, solar_radiation,
                     dt_hours / n_sub,
                     external_heat_kw, valve_target, humidity, hour_of_day,
-                    measured_heat_kw=measured_heat_kw,
+                    measured_heat_kw=measured_heat_kw, buffer_exo_kw=buffer_exo_kw,
                     _loss=(u_first, u_second),
                 )
                 refused += self._step_buffer_refused
@@ -3730,6 +3895,7 @@ class ThermalModel:
                 wind_speed, precipitation, solar_radiation, dt_hours,
                 external_heat_kw, humidity, hour_of_day,
                 measured_heat_kw=measured_heat_kw, valve_target=valve_target,
+                buffer_exo_kw=buffer_exo_kw,
                 _u_eff=u_first,
             )
         # Every sub-step below re-enters with the same outdoor, wind, rain,
@@ -3748,6 +3914,7 @@ class ThermalModel:
                 wind_speed, precipitation, solar_radiation, dt_hours / n_sub,
                 external_heat_kw, humidity, hour_of_day,
                 measured_heat_kw=measured_heat_kw, valve_target=valve_target,
+                buffer_exo_kw=buffer_exo_kw,
                 _cop=cop, _u_eff=u_first, _q_solar=q_solar,
             )
             refused += self._step_buffer_refused
@@ -3943,6 +4110,7 @@ class ThermalModel:
         solar_radiation = weather.solar_radiation
         humidity = weather.humidity
         external_heat_kw = weather.external_heat_kw
+        buffer_exo = weather.buffer_exo_kw
         n_steps = len(power_schedule)
 
         wind_speeds, precipitation, solar_radiation = weather_or_calm(
@@ -3989,6 +4157,7 @@ class ThermalModel:
                     if start_hour is not None and hours_matter
                     else None
                 ),
+                buffer_exo_kw=0.0 if buffer_exo is None else float(buffer_exo[i]),
             )
             room_temps[i + 1] = state.room_temperature
             slab_temps[i + 1] = state.slab_temperature
@@ -4120,6 +4289,7 @@ class ThermalModel:
         solar_radiation = weather.solar_radiation
         humidity = weather.humidity
         external_heat_kw = weather.external_heat_kw
+        buffer_exo = weather.buffer_exo_kw
         n_steps = heat_per_cop.shape[1]
         wind_speeds, precipitation, solar_radiation = weather_or_calm(
             n_steps, wind_speeds, precipitation, solar_radiation
@@ -4201,6 +4371,7 @@ class ThermalModel:
                 else 0.0
             )
             ext = np.maximum(0.0, ext_i)
+            exo_i = 0.0 if buffer_exo is None else float(buffer_exo[i])
             hum_i = float(humidity[i]) if humidity is not None else None
             hour_i = (
                 (start_hour + i * dt_hours) % 24.0
@@ -4232,6 +4403,8 @@ class ThermalModel:
                     thermal_power = (
                         cop * heat_per_cop_i + (0.0 if two_tank else ext)
                     )
+                    if throttled and exo_i:
+                        thermal_power = thermal_power + exo_i
                     if throttled:
                         target = (
                             vt if vt is not None
@@ -4369,8 +4542,8 @@ class ThermalModel:
                         # the store itself (#2500), the growth the
                         # production-call channel exempts.
                         q_slab, dT_sub, refused_sub = _single_valve_rates(
-                            p, T_buf, T_slab, thermal_power, out_i, u_first,
-                            vt, dt,
+                            p, T_buf, T_slab, thermal_power + exo_i, out_i,
+                            u_first, vt, dt,
                         )
                         refused_acc = refused_acc + refused_sub
                         thermal_power = q_slab
@@ -4434,10 +4607,8 @@ class ThermalModel:
         """Simulate full trajectory with coordinated space + DHW heating.
 
         Args:
-            dhw_draw_rates: Optional pre-computed per-step DHW draw power (kW).
-                Passing it avoids re-deriving the hourly pattern on every call,
-                which matters because the optimizer evaluates this thousands of
-                times per solve.
+            dhw_draw_rates: Optional pre-computed per-step DHW draw power (kW),
+                the planner's own series; None derives it from the pattern.
             coil_wood_read: Optional length-``n_steps`` array, filled with the
                 wood temperature each step's coil reduction reads: after that
                 step's space update, before the coil's drain -- a temperature
@@ -4448,11 +4619,12 @@ class ThermalModel:
 
         Returns:
             Tuple of (room_temps, slab_temps, upper_temps, lower_temps,
-                       dhw_temps, buffer_temps, wood_temps or None)
+                       dhw_temps, buffer_temps, wood_temps or None); a combi
+                       store is one node, so its dhw_temps are its buffer_temps.
         """
         # astuple: the arrays by reference, in the record's field order.
         (outdoor_temps, wind_speeds, precipitation, solar_radiation,
-         humidity, external_heat_kw) = astuple(weather)
+         humidity, external_heat_kw, _) = astuple(weather)
         n_steps = len(space_power_schedule)
 
         wind_speeds, precipitation, solar_radiation = weather_or_calm(
@@ -4476,8 +4648,14 @@ class ThermalModel:
         # #53: the space step needs its hour only when a learned gains
         # profile exists — hoisted for the same reason as the coil flag.
         gains_hours_matter = self.params.internal_gains_profile is not None
+        # Combi: one node. The hot-water side's net flux joins the space
+        # step's tank input, so the two trajectories are one (R10-COMBI-TANK).
+        store = combi_store_of(self.params)
 
         for i in range(n_steps):
+            exo_i = 0.0 if store is None else combi_dhw_net_kw(
+                self, store, state.buffer_tank_temperature, dhw_power_schedule[i],
+                float(dhw_draw_rates[i]), outdoor_temps[i], _step_humidity(humidity, i))
             # Space heating simulation
             state = self.simulate_step(
                 state=state,
@@ -4497,12 +4675,11 @@ class ThermalModel:
                     if valve_targets is not None
                     else None
                 ),
-                humidity=(
-                    float(humidity[i]) if humidity is not None else None
-                ),
+                humidity=_step_humidity(humidity, i),
                 hour_of_day=(
                     current_hour % 24.0 if gains_hours_matter else None
                 ),
+                buffer_exo_kw=exo_i,
             )
 
             draw_i = float(dhw_draw_rates[i])
@@ -4516,24 +4693,20 @@ class ThermalModel:
                     state, draw_i, state.dhw_temperature, dt_hours
                 )
 
-            # DHW simulation (runs in parallel with space heating)
-            cop_dhw = self.compute_cop_dhw(
-                outdoor_temps[i],
-                state.dhw_temperature,
-                humidity=(
-                    float(humidity[i]) if humidity is not None else None
-                ),
-            )
-            dhw_thermal_power = cop_dhw * heat_per_cop_kw(self.params, dhw_power_schedule[i])
-
-            new_dhw = self.simulate_dhw_step(
-                dhw_temp=state.dhw_temperature,
-                dhw_power_thermal=dhw_thermal_power,
-                hour_of_day=current_hour % 24.0,
-                ambient_temp=TANK_ROOM_AMBIENT_TEMP,
-                dt_hours=dt_hours,
-                draw_power=draw_i,
-            )
+            if store is not None:
+                new_dhw = state.buffer_tank_temperature
+            else:
+                # DHW simulation (runs in parallel with space heating)
+                new_dhw = self.simulate_dhw_step(
+                    dhw_temp=state.dhw_temperature,
+                    dhw_power_thermal=dhw_charge_kw(
+                        self, state.dhw_temperature, dhw_power_schedule[i],
+                        outdoor_temps[i], _step_humidity(humidity, i)),
+                    hour_of_day=current_hour % 24.0,
+                    ambient_temp=TANK_ROOM_AMBIENT_TEMP,
+                    dt_hours=dt_hours,
+                    draw_power=draw_i,
+                )
             state.dhw_temperature = new_dhw
 
             room_temps[i + 1] = state.room_temperature
diff --git a/dev/audit/harnesses/r10_combi_tank.py b/dev/audit/harnesses/r10_combi_tank.py
index 47deb5d88..d89d602d9 100644
--- a/dev/audit/harnesses/r10_combi_tank.py
+++ b/dev/audit/harnesses/r10_combi_tank.py
@@ -1,196 +1,318 @@
-"""R10-COMBI-TANK: the combi-tank group's harness; PR 0 (R10-BUFFER-OPENLOOP) arms.
+"""R10-COMBI-TANK-STORE (#3225): one store for space heating and hot water.
 
     PYTHONPATH=tests/hastub:custom_components:tests \\
-        python3 dev/audit/harnesses/r10_combi_tank.py [no_probe|wood_seed|solve|all]
-
-Synthetic installs only; no private data. Every arm drives the production
-``HeatPumpOptimizerCoordinator._update_current_state`` (which runs the
-external-heat detection) and reads the published state and the detector's
-observation; run it at the merge base and at the head to read the defect
-(D12-s1-01: the no-probe buffer is never advanced) at one end only.
-
-``no_probe``: a 500 L buffer behind a manual (throttling) valve and no buffer
-probe; a prior plan whose ``buffer_temp_trajectory`` moves 40 -> 47 degC in
-15-minute steps; two cycles at +20 and +50 minutes (covering steps 1 and 3).
-Printed per arm: the buffer level after each cycle and the observation's rise
-inputs (buffer_temp, dhw_temp). Arms: ``seed`` (no probe), ``probe`` (a probe
-reading 36.5 degC: the reading must win, the null control), ``empty`` (an
-empty trajectory, which is what a plan without a throttling valve publishes:
-the level must stay where it was, never fabricated).
-
-``wood_seed``: the same install plus a wood furnace (wood tank top 70, bottom
-60, valve outlet 55 degC, 1000 L, stove override on so the detector is
-active). The throttling valve is what makes the plan publish a buffer
-trajectory (optimizer.py, ``buffer_temp_trajectory``); without it this arm
-collapses into its own ``empty`` control. Printed: ``hp_tank_temp`` per
-cycle, and the detector's ``wood_energy_kwh`` and ``displacement``. Arms
-``seed``, ``probe`` (38 degC) and ``empty``.
-
-``solve``: four hourly ``async_refresh`` cycles with the real solver, no buffer
-probe, a 500 L buffer, valve ``manual`` against valve ``none``. Printed: the
-buffer level each solve started from, and whether the previous plan
-published a buffer trajectory. Under ``none`` the plan publishes none, so the
-level is never fabricated.
-
-RESULT lines are printed for the head; at the merge base ``no_probe_seed``
-reads 40.0,40.0 and ``wood_seed_hp`` reads 40.0,40.0.
-
-EXPECTED RESULT no_probe_seed=41.0,43.0
-EXPECTED RESULT no_probe_probe=36.5,36.5
-EXPECTED RESULT no_probe_empty=40.0,40.0
-EXPECTED RESULT no_probe_rise=None,None
-EXPECTED RESULT wood_seed_hp=41.0,43.0
-EXPECTED RESULT wood_seed_probe_hp=38.0,38.0
-EXPECTED RESULT wood_seed_empty_hp=40.0,40.0
+        python3 dev/audit/harnesses/r10_combi_tank.py [ARM ...]
+
+Synthetic installs only; no private data. The install is the issue's shape:
+a 504 l store behind a smart-write valve with a 40 l potable coil and the
+manual's 111 W standing loss at 65 degC (UA 111/45 W/K), eps 0.85 unless an
+arm says otherwise. Every arm prints ``RESULT name=value`` lines;
+no arm asserts, tests/features.py's R10-COMBI-TANK-STORE block does that.
+
+``issue``: the battery's components and stored kWh at 55 degC for the
+workaround base offers (a 504 l "DHW tank" beside the 504 l buffer, both on
+one probe) against the combi store: the workaround counts the water twice.
+
+``off_identity``: the store view with the option off, field for field
+against the separate tank's own properties (1 when bitwise equal).
+
+``balance`` / ``ua_zero`` / ``eps_null``: ``store_step`` over a 48-step day;
+the kWh residual of ``C * dT`` against its booked terms, the same with UA 0,
+and the end temperatures at eps 0.6 and 1.0 of a store cooling from 64.5 degC
+with the tap kept above 40 degC (a 65 degC setpoint keeps the rating above it).
+
+``legionella_eps``: the cycle's (due, step, hour) at eps 0.6 and 1.0.
+
+``lp_flux``: kWh the DHW planner buys with no space flux and with a 2 kW
+valve draw over the four hours before a 19-21 window, combi and separate.
+
+``exchange``: a joint solve at a two-tier price day: the rounds the flux
+exchange took, the worst shortfall below the hot-water requirement, and the
+same solve with zero exchange rounds (the null), plus the solve's seconds.
+
+``equiv``: the two comparison mutants the mutation ledger triages as
+equivalent, each the operator's own text compiled over the head's function
+(``dhw_store_of``'s ``eps >=`` to ``>``, ``store_step``'s ``d_temp >`` to
+``>=`` and ``new_temp <`` to ``<=``), against the head over a grid holding
+each comparison's tie; the
+cases that differ, the ties the grid reaches, and a tie-only control that
+moves only the tied result (it must differ on every tie, or the grid does not
+reach one).
 """
 from __future__ import annotations
 
-import asyncio
+import math
 import sys
-from datetime import datetime, timedelta, timezone
-from types import SimpleNamespace
-
-from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
-from homeassistant.util import dt as dt_util  # noqa: E402
-
-from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
-
-T0 = datetime(2026, 3, 2, 6, 0, tzinfo=timezone.utc)
-TRAJ = [40.0 + i for i in range(8)]
-AT = (T0 + timedelta(minutes=20), T0 + timedelta(minutes=50))
-BASE_CFG = {
-    "tibber_token": "x",
-    "weather_entity": "weather.home",
-    "indoor_temp_entity": "sensor.indoor",
-    "outdoor_temp_entity": "sensor.outdoor",
-    "buffer_tank_volume": 500.0,
-    "dhw_tank_volume": 200.0,
-    "mixing_valve_mode": "manual",
-}
-WOOD_CFG = {
-    "wood_furnace_enabled": True,
-    "external_heat_detection_enabled": True,
-    "external_heat_entity": "input_boolean.stove",
-    "wood_tank_top_entity": "sensor.wood_top",
-    "wood_tank_bottom_entity": "sensor.wood_bottom",
-    "valve_outlet_temp_entity": "sensor.outlet",
-    "wood_tank_volume": 1000.0,
-}
+import time
+from dataclasses import replace
+from datetime import datetime
+
+import numpy as np
+
+from heatpump_optimizer import battery, mixing_valve
+from heatpump_optimizer import optimizer as optmod
+from heatpump_optimizer import thermal_model as tm
+from heatpump_optimizer.dhw_planner import DhwPlanner
+from heatpump_optimizer.dhw_schedule import parse_windows
+from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig, _Horizon
+from profiles import solve_inputs
+
+
+#: The MFS 600 S's ErP standing loss, 111 W at 65 degC (carry 4, item 1), as
+#: the cooling rate its UA of 111/45 W/K gives at 25 K over 544 l.
+RATE = 0.111 / 45.0 * 25.0 / (tm.WATER_SPECIFIC_HEAT * 544.0)
+
+
+def params(combi=True, eps=0.85, **kw):
+    base = dict(buffer_tank_volume=504.0, mixing_valve_mode=mixing_valve.MODE_SMART_WRITE,
+                dhw_enabled=True, dhw_tank_volume=200.0, combi_potable_volume_l=40.0,
+                buffer_cooling_rate=RATE)
+    base.update(kw)
+    return tm.ThermalParameters(dhw_combi_tank_enabled=combi, combi_dhw_effectiveness=eps, **base)
+
+
+def state(t=50.0, since=1.0):
+    return tm.ThermalState(room_temperature=21.0, slab_temperature=23.0,
+                           buffer_tank_temperature=t, dhw_temperature=t,
+                           outdoor_temperature=0.0, dhw_hours_since_legionella=since)
+
+
+def horizon(st, n=96, dt=0.25):
+    return _Horizon(
+        initial_state=st, prices=np.full(n, 1.0), outdoor_temps=np.full(n, 0.0),
+        wind_speeds=np.zeros(n), precipitation=np.zeros(n), solar_radiation=np.zeros(n),
+        start_time=None, n_steps=n, dt=dt, comfort_targets=np.full(n, 21.0),
+        temp_min_bounds=np.full(n, 17.0), temp_max_bounds=np.full(n, 23.0),
+        step_hours=np.arange(n) * dt, solar_gains=np.zeros(n), heat_loss_factors=np.ones(n),
+        forecast={}, t_start=0.0)
+
+
+def opt_for(p):
+    return HeatPumpOptimizer(tm.ThermalModel(p), OptimizationConfig(
+        horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=19.0, max_temp=23.0))
+
+
+def planner(p):
+    o = opt_for(p)
+    return DhwPlanner(o.model, o.config, o._pv_surplus, o._price_known)
+
+
+def arm_issue():
+    for label, p in (("workaround", params(combi=False, dhw_tank_volume=504.0)),
+                     ("combi", params())):
+        b = battery.build(p, state(55.0), comfort_min=20.0, comfort_max=23.0,
+                          dhw_min=45.0, dhw_max=60.0, cop=3.0)
+        tanks = [c for c in b.components if c.name in ("buffer_tank", "dhw_tank")]
+        print(f"RESULT {label}_tank_components={len(tanks)}")
+        print(f"RESULT {label}_tank_kwh_per_c={sum(c.capacity_kwh_per_c for c in tanks):.4f}")
+    print(f"RESULT combi_store_ua_w_per_k={params().dhw_store.ua_kw_per_c * 1000.0:.4f}")
 
 
-def _fmt(values):
-    return ",".join("None" if v is None else f"{v:.1f}" for v in values)
-
-
-def cycles(*, probe=None, trajectory=TRAJ, wood=False):
-    """Two ``_update_current_state`` cycles over an injected prior plan."""
-    cfg = dict(BASE_CFG)
-    if probe is not None:
-        cfg["buffer_tank_temp_entity"] = "sensor.buffer"
-    if wood:
-        cfg.update(WOOD_CFG)
-    coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
-    coord._snapshots_loaded = True
-    coord._optimization_result = SimpleNamespace(
-        buffer_temp_trajectory=list(trajectory),
-        dhw_temp_trajectory=[],
-        timestamps=[T0 + timedelta(minutes=15 * i) for i in range(8)],
-    )
-    seen = []
-    real = coord._external_heat.update
-    coord._external_heat.update = lambda obs: (seen.append(obs), real(obs))[1]
-    levels = []
-    try:
-        for now in AT:
-            dt_util.freeze(now)
-            states = [("sensor.indoor", "21.0"), ("sensor.outdoor", "5.0")]
-            if probe is not None:
-                states.append(("sensor.buffer", f"{probe}"))
-            if wood:
-                states += [("sensor.wood_top", "70.0"), ("sensor.wood_bottom", "60.0"),
-                           ("sensor.outlet", "55.0")]
-                coord.hass.states.set("input_boolean.stove", FakeState("on", last_updated=now))
-            for entity, value in states:
-                coord.hass.states.set(entity, FakeState(value, last_updated=now, unit="°C"))
-            asyncio.run(coord._update_current_state())
-            levels.append(getattr(coord, "_ctx", coord)._current_state.buffer_tank_temperature)
-    finally:
-        dt_util.freeze(None)
-    return levels, seen, coord._external_heat.state
-
-
-def arm_no_probe() -> None:
-    for name, kw in (("seed", {}), ("probe", {"probe": 36.5}), ("empty", {"trajectory": ()})):
-        levels, seen, _ = cycles(**kw)
-        rise = [(o.buffer_temp, o.dhw_temp) for o in seen]
-        print(f"no_probe {name:5}: buffer levels {_fmt(levels)}  rise inputs {rise}")
-        print(f"RESULT no_probe_{name}={_fmt(levels)}")
-        if name == "seed":
-            print(f"RESULT no_probe_rise={_fmt(o.buffer_temp for o in seen)}")
-
-
-def arm_wood_seed() -> None:
-    for name, kw in (("seed", {}), ("probe", {"probe": 38.0}), ("empty", {"trajectory": ()})):
-        _, seen, st = cycles(wood=True, **kw)
-        hp = [o.hp_tank_temp for o in seen]
-        energy = "None" if st.wood_energy_kwh is None else f"{st.wood_energy_kwh:.4f}"
-        print(f"wood_seed {name:5}: hp_tank_temp {_fmt(hp)}  wood_energy_kwh {energy}"
-              f"  displacement {st.displacement:.4f}")
-        key = "wood_seed_hp" if name == "seed" else f"wood_seed_{name}_hp"
-        print(f"RESULT {key}={_fmt(hp)}")
-
-
-def _prices(hass, now):
-    now = now.replace(minute=0, second=0, microsecond=0)
-    hass.states.set("sensor.prices", FakeState("0.5", attributes={"raw_today": [
-        {"start": (now + timedelta(hours=h)).isoformat(), "value": round(0.5 + 0.1 * (h % 4), 3)}
-        for h in range(48)]}))
-
-
-def arm_solve() -> None:
-    import heatpump_optimizer as integ
-
-    for valve in ("manual", "none"):
-        cfg = {k: v for k, v in BASE_CFG.items() if k != "tibber_token"}
-        cfg.update({"price_source": "entity", "price_entity": "sensor.prices",
-                    "mixing_valve_mode": valve, "dhw_enabled": False})
-        dt_util.freeze(T0)
-        hass = FakeHass()
-        hass.states.set("sensor.indoor", FakeState("21.0", unit="°C"))
-        hass.states.set("sensor.outdoor", FakeState("-3.0", unit="°C"))
-        _prices(hass, T0)
-        entry = FakeEntry(data=cfg, entry_id=f"r10ct_solve_{valve}")
-        seeds, published = [], []
+def arm_off_identity():
+    p = params(combi=False)
+    s = p.dhw_store
+    same = (s.capacity_kwh_per_c == p.dhw_tank_thermal_mass
+            and s.ua_kw_per_c == p.dhw_tank_heat_loss_coefficient
+            and s.charge_max_temp == p.dhw_max_temp and s.rating_max_temp == p.dhw_hard_max_temp
+            and s.inlet_c == p.dhw_inlet_reference and not s.combi)
+    print(f"RESULT off_store_bitwise={int(same)}")
+
+
+def walk(store, t0, heat, draw, dt=0.5):
+    temps, terms = [t0], []
+    for q_in, q_draw in zip(heat, draw):
+        t = temps[-1]
+        new, refused, injected, debited = tm.store_step(store, t, q_in, q_draw, 20.0, dt)
+        terms.append((q_in - debited - store.ua_kw_per_c * (t - 20.0) - refused + injected) * dt)
+        temps.append(new)
+    return temps, terms
+
+
+def arm_balance(ua_zero=False):
+    store = params().dhw_store
+    if ua_zero:
+        store = replace(store, ua_kw_per_c=0.0)
+    heat = [3.0 * math.sin(i / 5.0) - 1.0 for i in range(48)]
+    draw = [0.0 if i % 7 else 6.0 for i in range(48)]
+    temps, terms = walk(store, 58.0, heat, draw)
+    gap = store.capacity_kwh_per_c * (temps[-1] - temps[0]) - math.fsum(terms)
+    print(f"RESULT {'ua_zero' if ua_zero else 'balance'}_residual_kwh={gap:.3e}")
+
+
+def arm_eps_null():
+    for eps in (0.6, 1.0):
+        temps, _ = walk(params(eps=eps, dhw_setpoint=65.0).dhw_store, 64.5, [1.6] * 6, [2.0] * 6)
+        print(f"RESULT eps_{eps}_end_c={temps[-1]:.12f}")
+
+
+def arm_legionella_eps():
+    for eps in (0.6, 1.0):
+        p = params(eps=eps, dhw_legionella_enabled=True, dhw_legionella_temp=60.0,
+                   dhw_legionella_interval_days=7.0, dhw_daily_consumption=0.0,
+                   dhw_min_temp=30.0, dhw_schedule_enabled=True,
+                   dhw_windows=parse_windows("18:00-19:00"))
+        plan, _ = planner(p)._build_dhw_requirements(
+            horizon(state(50.0, since=7 * 24.0 - 6.0)), p_max=4.0)
+        print(f"RESULT legionella_eps_{eps}=({plan.legionella_due},{plan.legionella_step},"
+              f"{plan.legionella_hour})")
+
+
+def arm_lp_flux():
+    exo = np.zeros(96)
+    exo[60:76] = -2.0
+    for combi in (True, False):
+        for label, series in (("none", np.zeros(96)), ("draw", exo)):
+            p = params(combi=combi, dhw_schedule_enabled=True,
+                       dhw_windows=parse_windows("19:00-21:00"), dhw_min_temp=40.0)
+            plan, _ = planner(p)._build_dhw_requirements(
+                horizon(state(50.0)), p_max=4.0, tank_exo_kw=series)
+            kind = "combi" if combi else "separate"
+            print(f"RESULT lp_flux_{kind}_{label}_kwh={float(np.sum(plan.schedule)) * 0.25:.4f}")
+
+
+def arm_exchange():
+    prices = np.full(96, 1.5)
+    prices[:20] = 0.8
+    prices[64:80] = 4.0
+    rounds_taken = []
+    real = optmod._combi_flux_exchange
+
+    def counted(opt, h, planner_, space, dhw, draws, p_max):
+        calls = {"n": 0}
+        build = planner_._build_dhw_requirements
+
+        def wrapped(*a, **k):
+            calls["n"] += 1
+            return build(*a, **k)
+
+        planner_._build_dhw_requirements = wrapped
         try:
-            asyncio.run(integ.async_setup_entry(hass, entry))
-            coord = entry.runtime_data
-            real = coord._solve_record
-
-            def snap(*a, **k):
-                record = real(*a, **k)
-                seeds.append(record.inputs.state.buffer_tank_temperature)
-                return record
-
-            coord._solve_record = snap
-            for hour in range(4):
-                published.append(bool(getattr(coord._optimization_result, "buffer_temp_trajectory", None)))
-                dt_util.freeze(T0 + timedelta(hours=hour))
-                _prices(hass, T0 + timedelta(hours=hour))
-                asyncio.run(coord.async_refresh())
+            return real(opt, h, planner_, space, dhw, draws, p_max)
         finally:
-            dt_util.freeze(None)
-        print(f"solve valve={valve:6}: solver buffer seeds {_fmt(seeds)}  "
-              f"previous plan published a buffer trajectory {published}")
+            rounds_taken.append(calls["n"])
+
+    for label, rounds in (("exchange", None), ("null", 0)):
+        o = opt_for(params())
+        saved = optmod._COMBI_EXCHANGE_ROUNDS
+        optmod._combi_flux_exchange = counted
+        if rounds is not None:
+            optmod._COMBI_EXCHANGE_ROUNDS = rounds
+        try:
+            t0 = time.perf_counter()
+            r = o.optimize(inputs=solve_inputs(
+                initial_state=state(50.0), prices=prices, outdoor_temps=np.full(96, 0.0),
+                wind_speeds=np.zeros(96), precipitation=np.zeros(96),
+                solar_radiation=np.zeros(96), start_time=datetime(2026, 1, 15)))
+            secs = time.perf_counter() - t0
+        finally:
+            optmod._combi_flux_exchange = real
+            optmod._COMBI_EXCHANGE_ROUNDS = saved
+        req = np.asarray(o._dhw_requirement)
+        gap = float(np.max(req - np.asarray(r.dhw_temp_trajectory)[1:req.size + 1]))
+        print(f"RESULT {label}_rounds={rounds_taken[-1] if rounds_taken else 0}")
+        print(f"RESULT {label}_worst_shortfall_c={gap:.3f}")
+        print(f"RESULT {label}_dhw_kwh={float(np.sum(r.dhw_power_schedule)) * 0.25:.3f}")
+        print(f"RESULT {label}_solve_s={secs:.2f}")
+
+
+def _swapped(fn, old, new):
+    """``fn`` recompiled with ``old`` replaced once in its source, over its globals."""
+    import inspect
+    import textwrap
+    src = textwrap.dedent(inspect.getsource(fn))
+    assert src.count(old) == 1, (fn.__name__, old)
+    ns: dict = {}
+    exec(compile(src.replace(old, new), f"<{fn.__name__} mutant>", "exec"), fn.__globals__, ns)
+    return ns[fn.__name__]
 
 
-def main(argv: list[str]) -> int:
-    which = argv[1] if len(argv) > 1 else "all"
-    arms = {"no_probe": arm_no_probe, "wood_seed": arm_wood_seed, "solve": arm_solve}
-    for name, fn in arms.items():
-        if which in (name, "all"):
-            fn()
-    return 0
+def _same(a, b):
+    return all(x == y or (x != x and y != y) for x, y in zip(a, b))
 
 
+def arm_equiv():
+    floor = tm.COMBI_DHW_EFFECTIVENESS_FLOOR
+    cond = "eps = min(1.0, eps) if eps >= COMBI_DHW_EFFECTIVENESS_FLOOR else COMBI_DHW_EFFECTIVENESS_FLOOR"
+    mut = _swapped(tm.dhw_store_of, cond, cond.replace(" >= ", " > ", 1))
+    tie = _swapped(tm.dhw_store_of, cond, cond.replace(
+        "min(1.0, eps) if", "(min(1.0, eps) if eps != COMBI_DHW_EFFECTIVENESS_FLOOR else 0.5) if", 1))
+    grid = [0.0, -1.0, math.nextafter(floor, 0.0), floor, math.nextafter(floor, 1.0), 0.5, 0.85,
+            1.0, 1.5, math.inf, math.nan]
+    rows = [(tm.dhw_store_of(params(eps=e)).effectiveness, mut(params(eps=e)).effectiveness,
+             tie(params(eps=e)).effectiveness, e == floor) for e in grid]
+    print(f"RESULT equiv_eps_cases={len(rows)}")
+    print(f"RESULT equiv_eps_ties={sum(r[3] for r in rows)}")
+    print(f"RESULT equiv_eps_differ={sum(not _same((r[0],), (r[1],)) for r in rows)}")
+    print(f"RESULT equiv_eps_tie_control_differ_on_ties="
+          f"{sum(not _same((r[0],), (r[2],)) for r in rows if r[3])}")
+    print(f"RESULT equiv_eps_tie_control_differ_off_ties="
+          f"{sum(not _same((r[0],), (r[2],)) for r in rows if not r[3])}")
+
+    step = "    if d_temp > cap:\n        refused, d_temp = (d_temp - cap) * capacity, cap"
+    smut = _swapped(tm.store_step, step, step.replace("d_temp > cap", "d_temp >= cap", 1))
+    stie = _swapped(tm.store_step, step, "    if d_temp == cap:\n        refused += 1.0\n" + step)
+    base = replace(params().dhw_store, capacity_kwh_per_c=1.0, ua_kw_per_c=0.0)
+    cases = []
+    # Ties: C = 1, no loss and no draw make d_temp the heat in, and the
+    # rating's distance over dt an exact binary fraction, so heat == cap exactly.
+    for below, dt in ((10.0, 0.5), (4.0, 0.25), (1.0, 1.0)):
+        cases.append((base, base.rating_max_temp - below, below / dt, 0.0, 20.0, dt))
+    store = params().dhw_store
+    for temp in (10.0, 45.0, 60.0, store.rating_max_temp, store.rating_max_temp + 3.0):
+        for heat in (-2.0, 0.0, 1.5, 6.0, 40.0):
+            for draw in (0.0, 2.0):
+                cases.append((store, temp, heat, draw, 15.0, 0.25))
+    ties = differ = tie_hit = tie_off = 0
+    for c in cases:
+        head = tm.store_step(*c)
+        d_temp = ((c[2] - c[3] * tm.dhw_draw_scale(c[0].tap_temp_for_store(c[1]), c[0].inlet_c)
+                   - c[0].ua_kw_per_c * (c[1] - c[4])) / c[0].capacity_kwh_per_c)
+        is_tie = d_temp == max(0.0, c[0].rating_max_temp - c[1]) / max(c[5], 1e-6)
+        ties += is_tie
+        differ += not _same(head, smut(*c))
+        moved = not _same(head, stie(*c))
+        tie_hit += moved and is_tie
+        tie_off += moved and not is_tie
+    print(f"RESULT equiv_step_cases={len(cases)}")
+    print(f"RESULT equiv_step_ties={ties}")
+    print(f"RESULT equiv_step_differ={differ}")
+    print(f"RESULT equiv_step_tie_control_differ_on_ties={tie_hit}")
+    print(f"RESULT equiv_step_tie_control_differ_off_ties={tie_off}")
+
+    fl = "    if new_temp < floor:\n        injected, new_temp ="
+    fmut = _swapped(tm.store_step, fl, fl.replace("new_temp < floor", "new_temp <= floor", 1))
+    ftie = _swapped(tm.store_step, fl, "    if new_temp == floor:\n        injected += 1.0\n" + fl)
+    # Floor ties: ambient 8 below the inlet makes the floor 8, and an exact
+    # binary heat over dt lands the step on it.
+    fcases = [(base, temp, (8.0 - temp) / dt, 0.0, 8.0, dt)
+              for temp, dt in ((12.0, 0.5), (9.0, 0.25), (16.0, 1.0))]
+    fcases += cases
+    fties = fdiffer = fhit = foff = 0
+    for c in fcases:
+        head = tm.store_step(*c)
+        pre = c[1] + min((c[2] - c[3] * tm.dhw_draw_scale(c[0].tap_temp_for_store(c[1]), c[0].inlet_c)
+                          - c[0].ua_kw_per_c * (c[1] - c[4])) / c[0].capacity_kwh_per_c,
+                         max(0.0, c[0].rating_max_temp - c[1]) / max(c[5], 1e-6)) * c[5]
+        is_tie = pre == min(c[0].inlet_c, c[4])
+        fties += is_tie
+        fdiffer += not _same(head, fmut(*c))
+        moved = not _same(head, ftie(*c))
+        fhit += moved and is_tie
+        foff += moved and not is_tie
+    print(f"RESULT equiv_floor_cases={len(fcases)}")
+    print(f"RESULT equiv_floor_ties={fties}")
+    print(f"RESULT equiv_floor_differ={fdiffer}")
+    print(f"RESULT equiv_floor_tie_control_differ_on_ties={fhit}")
+    print(f"RESULT equiv_floor_tie_control_differ_off_ties={foff}")
+
+
+ARMS = {
+    "issue": arm_issue, "off_identity": arm_off_identity, "balance": arm_balance,
+    "ua_zero": lambda: arm_balance(ua_zero=True), "eps_null": arm_eps_null,
+    "legionella_eps": arm_legionella_eps, "lp_flux": arm_lp_flux, "exchange": arm_exchange,
+    "equiv": arm_equiv,
+}
+
 if __name__ == "__main__":
-    sys.exit(main(sys.argv))
+    for name in sys.argv[1:] or list(ARMS):
+        ARMS[name]()
diff --git a/dev/programme/delivery/3358.md b/dev/programme/delivery/3358.md
new file mode 100644
index 000000000..ba9d3bdaf
--- /dev/null
+++ b/dev/programme/delivery/3358.md
@@ -0,0 +1 @@
+- [#3358](https://github.com/tvofi/heatpump_optimizer/pull/3358) — **open**, R10-COMBI-TANK: design for a combi tank where space heating and DHW share the same water (#3225) (R10-COMBI-TANK)
diff --git a/tests/entities.py b/tests/entities.py
index 4a8c8a9d8..44065430f 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -4197,6 +4197,14 @@ def _p2_registry(sources):
 #: Facts no AST shape holds, each held by a census in another script that
 #: asserts its own reach. A registry entry here is the census's check text.
 _P2_CENSUSES = {
+    # R10-COMBI-TANK-STORE (#3225): the hot-water store is one view, its two
+    # sides exchange their flux, and only tap-stated limits pass through eps.
+    "combi_store_view": (
+        "tests/features.py", "combi_store_view census: outside thermal_model.py nothing reads"),
+    "combi_flux_live": (
+        "tests/features.py", "combi_flux_live census: every DHW walk the planner runs"),
+    "combi_tap_limit": (
+        "tests/features.py", "combi_tap_limit census: every tap-stated minimum the planner"),
     # #1747: the DHW mode block reached the first DHW build and not the
     # co-optimisation replan's (R9-RCA-1747); EG-B8's census holds it.
     "dhw_mode_blocked_at_every_build": (
diff --git a/tests/features.py b/tests/features.py
index f74104846..1565c12f8 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -173,17 +173,22 @@ def _dhw_horizon(*, prices, outdoor, n, dt, step_hours=None, state=None,
     )
 
 
-def _dhw_ctx(*, prices, outdoor, n, dt, c_dhw, p_dhw_max,
+from dataclasses import replace as _dhw_store_with  # noqa: E402
+
+
+def _dhw_ctx(*, prices, outdoor, n, dt, c_dhw, p_dhw_max, params,
              min_run_power=0.1, max_lead_steps=24, humidity=None,
-             import_prices=None):
+             import_prices=None, tank_exo_kw=None):
     """The DHW planners' shared record for direct calls (#1776). The floor
-    repair ranks at ``import_prices``, defaulting to the same series."""
+    repair ranks at ``import_prices``, defaulting to the same series. The
+    store is ``params``' own (its UA and limits) at capacity ``c_dhw``."""
     return _DhwPlanContext(
         prices=prices, import_prices=prices if import_prices is None
         else import_prices,
         outdoor_temps=outdoor, humidity=humidity,
-        n_steps=n, dt=dt, c_dhw=c_dhw, p_dhw_max=p_dhw_max,
-        min_run_power=min_run_power, max_lead_steps=max_lead_steps)
+        n_steps=n, dt=dt, store=_dhw_store_with(params.dhw_store, capacity_kwh_per_c=c_dhw),
+        p_dhw_max=p_dhw_max, min_run_power=min_run_power,
+        max_lead_steps=max_lead_steps, tank_exo_kw=tank_exo_kw)
 
 
 def _solve_record_now(coord):
@@ -9659,10 +9664,21 @@ def reachable(name: str) -> str | None:
 # Volume is gated on the furnace toggle (#463): a lone CONF_WOOD_TANK_VOLUME
 # does not infer a tank, so the single-key probe cannot see it.
 toggle_gated = {"wood_tank_volume"}
+# R10-COMBI-TANK-STORE (PR A) lands the combi store as parameter fields that
+# only a test sets, so no install can reach combi; PR B (R10-COMBI-TANK)
+# wires the option and the loader. Each entry must stay unreachable, so the
+# set refuses itself the day a loader lands without emptying it.
+unwired_combi = {"dhw_combi_tank_enabled", "combi_dhw_effectiveness", "combi_potable_volume_l"}
 probe = {name: reachable(name) for name in declared - runtime_only - validated_enums}
+R.check(
+    "the combi store's fields are reachable from no config key until PR B wires them",
+    all(probe.get(n, "absent") is None for n in unwired_combi),
+    f"{ {n: probe.get(n, 'absent') for n in unwired_combi} } -- a wired field leaves the set",
+)
 
 unreachable = sorted(
-    n for n, k in probe.items() if k is None and n not in toggle_gated
+    n for n, k in probe.items()
+    if k is None and n not in toggle_gated and n not in unwired_combi
 )
 R.check(
     "every configurable parameter is reachable from a config key",
@@ -11311,6 +11327,664 @@ R.check(
     f"tank peaked at {_cap_peak:.4f} C",
 )
 
+# R10-COMBI-TANK-STORE (#3225; design/r10-combi-tank a605014b): one body of
+# heating water serves the space circuit and hot water through an exchanger.
+# Every arm builds its parameters through `_ct_params`, which returns None
+# where the combi fields do not exist (the base), so each arm fails there by
+# construction rather than crashing the script.
+import ast as _ct_ast  # noqa: E402
+import math as _ct_math  # noqa: E402
+from dataclasses import replace as _ct_replace  # noqa: E402
+from pathlib import Path as _ct_Path  # noqa: E402
+from heatpump_optimizer import thermal_model as _ct_tm  # noqa: E402
+from heatpump_optimizer.dhw_schedule import parse_windows as _ct_windows  # noqa: E402
+
+R.section("R10-COMBI-TANK-STORE: the combi store, one node for space and hot water")
+_CT_CP = _ct_tm.WATER_SPECIFIC_HEAT
+_CT_MIX = _ct_tm.DHW_MIXED_USE_TEMP
+
+
+# The issue's MFS 600 S, per the manufacturer manual (carry 4, item 1): 504 l of
+# heating water, a 40 l coil, and an ErP standing loss of 111 W at 65 C, so a
+# UA of 111/45 W/K, entered as the cooling rate it gives at the code's 25 K.
+_CT_UA_KW = 0.111 / 45.0
+_CT_RATE = _CT_UA_KW * 25.0 / (_ct_tm.WATER_SPECIFIC_HEAT * 544.0)
+
+
+def _ct_params(combi=True, eps=0.85, potable=40.0, **kw):
+    base = dict(buffer_tank_volume=504.0, mixing_valve_mode=_mv.MODE_SMART_WRITE,
+                dhw_enabled=True, dhw_tank_volume=200.0, buffer_cooling_rate=_CT_RATE)
+    base.update(kw)
+    try:
+        return ThermalParameters(dhw_combi_tank_enabled=combi, combi_dhw_effectiveness=eps,
+                                 combi_potable_volume_l=potable, **base)
+    except TypeError:
+        return None
+
+
+def _ct_store(p):
+    return getattr(p, "dhw_store", None) if p is not None else None
+
+
+# The issue's install (#3225): 504 l of heating water and a 40 l potable coil
+# in ONE vessel. The only configuration base offers counts it twice.
+_ct_p = _ct_params()
+_ct_off = _ct_params(combi=False)
+_ct_s = _ct_store(_ct_p)
+R.check(
+    "combi: the DHW store is the buffer store, potable water included: one capacity, one loss",
+    _ct_s is not None and _ct_s.combi
+    and abs(_ct_s.capacity_kwh_per_c - _CT_CP * 544.0) < 1e-12
+    and _ct_s.capacity_kwh_per_c == _ct_p.buffer_tank_thermal_mass
+    and _ct_s.ua_kw_per_c == _ct_p.buffer_tank_heat_loss_coefficient
+    and abs(_ct_s.ua_kw_per_c / _CT_UA_KW - 1.0) < 1e-12
+    and _ct_p.buffer_store_volume == 544.0
+    and _ct_s.rating_max_temp == min(_ct_p.dhw_hard_max_temp, _ct_p.buffer_max_temp)
+    and _ct_s.charge_max_temp == min(_ct_p.dhw_max_temp, _ct_p.buffer_max_temp),
+    f"store {_ct_s}",
+)
+_ct_so = _ct_store(_ct_off)
+R.check(
+    "combi off: the store is the separate tank's own values, bitwise, and the "
+    "transforms return their argument itself",
+    _ct_so is not None and not _ct_so.combi
+    and _ct_so.capacity_kwh_per_c == _ct_off.dhw_tank_thermal_mass
+    and _ct_so.ua_kw_per_c == _ct_off.dhw_tank_heat_loss_coefficient
+    and _ct_so.rating_max_temp == _ct_off.dhw_hard_max_temp
+    and _ct_so.charge_max_temp == _ct_off.dhw_max_temp
+    and _ct_so.inlet_c == _ct_off.dhw_inlet_reference
+    and _ct_off.buffer_store_volume is _ct_off.buffer_tank_volume
+    and all(_ct_so.store_temp_for_tap(t) is t and _ct_so.tap_temp_for_store(t) is t
+            for t in (40.0, 45.123456789, 61.7)),
+    f"store {_ct_so}",
+)
+R.check(
+    "combi needs the store: no valve, a small tank, no hot water or the wood coil "
+    "each leave the separate tank in force",
+    all(_ct_store(q) is not None and not _ct_store(q).combi for q in (
+        _ct_params(mixing_valve_mode=_mv.MODE_NONE),
+        _ct_params(buffer_tank_volume=50.0),
+        _ct_params(dhw_enabled=False),
+    )),
+    "a combi predicate reached without its preconditions",
+)
+R.check(
+    "the effectiveness is floored and capped, never a divisor of zero or a gain",
+    _ct_params(eps=0.0) is not None
+    and _ct_store(_ct_params(eps=0.0)).effectiveness == _ct_tm.COMBI_DHW_EFFECTIVENESS_FLOOR
+    and _ct_store(_ct_params(eps=float("nan"))).effectiveness
+    == _ct_tm.COMBI_DHW_EFFECTIVENESS_FLOOR
+    and _ct_store(_ct_params(eps=1.5)).effectiveness == 1.0,
+    "eps 0 / nan / 1.5",
+)
+
+# The battery and the settlement count the one store once (invariant 2).
+_ct_state = ThermalState(room_temperature=21.0, slab_temperature=23.0,
+                         buffer_tank_temperature=55.0, dhw_temperature=55.0,
+                         outdoor_temperature=0.0)
+
+
+def _ct_battery(p):
+    return battery_view.build(p, _ct_state, comfort_min=20.0, comfort_max=23.0,
+                              dhw_min=45.0, dhw_max=60.0, cop=3.0)
+
+
+_ct_bat = _ct_battery(_ct_p) if _ct_p is not None else None
+_ct_bat_off = _ct_battery(_ct_off) if _ct_off is not None else None
+_ct_names = [c.name for c in _ct_bat.components] if _ct_bat else []
+_ct_buf = [c for c in (_ct_bat.components if _ct_bat else []) if c.name == "buffer_tank"]
+R.check(
+    "combi battery: no dhw_tank beside the buffer_tank, whose capacity is the store's",
+    _ct_bat is not None and "dhw_tank" not in _ct_names and len(_ct_buf) == 1
+    and _ct_buf[0].capacity_kwh_per_c == _ct_s.capacity_kwh_per_c,
+    f"components {_ct_names}",
+)
+R.check(
+    "combi battery null control: off, the separate tank is its own dhw_tank component",
+    _ct_bat_off is not None
+    and [c.capacity_kwh_per_c for c in _ct_bat_off.components if c.name == "dhw_tank"]
+    == [_ct_off.dhw_tank_thermal_mass],
+    f"components {[c.name for c in _ct_bat_off.components] if _ct_bat_off else None}",
+)
+
+
+def _ct_stored(p):
+    opt = _StoreOpt(ThermalModel(p), _StoreCfg(horizon_hours=24, time_step_minutes=15))
+    return (opt._stored_thermal_energy(_ct_state, include_dhw=True)
+            - opt._stored_thermal_energy(_ct_state, include_dhw=False))
+
+
+_ct_two = _ct_params(two_zone_enabled=True)
+_ct_two_off = _ct_params(combi=False, two_zone_enabled=True)
+_ct_terms_st = (
+    (_ct_stored(_ct_two), _ct_stored(_ct_p), _ct_stored(_ct_off), _ct_stored(_ct_two_off))
+    if _ct_two is not None else None)
+R.check(
+    "combi settlement: two-zone counts the store once, as the buffer; single-zone "
+    "counts it as the DHW term at the store's capacity; off, the separate tank's",
+    _ct_terms_st is not None and _ct_terms_st[0] == 0.0 and _ct_terms_st[2] > 0.0
+    and _ct_terms_st[3] == _ct_terms_st[2]
+    and abs(_ct_terms_st[1] * _ct_off.dhw_tank_thermal_mass
+            - _ct_terms_st[2] * _ct_s.capacity_kwh_per_c) < 1e-12,
+    f"the DHW term (two-zone combi, combi, off, two-zone off): {_ct_terms_st}",
+)
+
+# The store step balances to the kWh (invariant 2's trajectory form, design T.3):
+# a 48-step day of charge, valve draw (negative heat in) and hot-water draw,
+# with a cold stretch below the mixer threshold.
+_ct_heat = [3.0 * _ct_math.sin(i / 5.0) - 1.0 for i in range(48)]
+_ct_draw = [0.0 if i % 7 else 6.0 for i in range(48)]
+
+
+def _ct_walk(store, t0=58.0, heat=_ct_heat, draw=_ct_draw, dt=0.5):
+    temps, terms = [t0], []
+    for q_in, q_draw in zip(heat, draw):
+        t = temps[-1]
+        new, refused, injected, debited = _ct_tm.store_step(store, t, q_in, q_draw, 20.0, dt)
+        terms.append((q_in - debited - store.ua_kw_per_c * (t - 20.0) - refused + injected) * dt)
+        temps.append(new)
+    return temps, terms
+
+
+if _ct_s is not None:
+    _ct_t, _ct_terms = _ct_walk(_ct_s)
+    _ct_gap = abs(_ct_s.capacity_kwh_per_c * (_ct_t[-1] - _ct_t[0]) - _ct_math.fsum(_ct_terms))
+    _ct_zero = _ct_replace(_ct_s, ua_kw_per_c=0.0)
+    _ct_t0, _ct_terms0 = _ct_walk(_ct_zero)
+    _ct_rhs0 = _ct_math.fsum(_ct_terms0)
+    _ct_rel0 = abs(_ct_zero.capacity_kwh_per_c * (_ct_t0[-1] - _ct_t0[0]) - _ct_rhs0) / max(
+        abs(_ct_rhs0), 1.0)
+else:
+    _ct_t, _ct_gap, _ct_rel0 = [], float("inf"), float("inf")
+R.check(
+    "combi_energy_balance: C * dT equals charge + space flux - draw - loss over a day, to 1e-9 kWh",
+    _ct_gap <= 1e-9 and min(_ct_t or [0.0]) < 51.0,
+    f"gap {_ct_gap:.3e} kWh; coldest {min(_ct_t or [0.0]):.2f} C (the debit's scaled band)",
+)
+R.check(
+    "combi_energy_balance null control: with UA = 0 the store conserves its fluxes to 1e-12",
+    _ct_rel0 <= 1e-12,
+    f"relative residual {_ct_rel0:.3e}",
+)
+# Above the mixer the debit is nominal, so eps cannot move the trajectory; below
+# it the debit is read at the tap, so eps must (the liveness leg).
+# A 65 C setpoint puts the rating above the 60 C store that gives 40 C at the
+# tap at eps 0.6, so the walk cools freely inside the mixed band.
+_ct_hot_heat = [1.6] * 6
+_ct_hot_draw = [2.0] * 6
+_ct_e6, _ct_e10 = _ct_params(eps=0.6, dhw_setpoint=65.0), _ct_params(eps=1.0, dhw_setpoint=65.0)
+_ct_hot6 = _ct_walk(_ct_store(_ct_e6), 64.5, _ct_hot_heat, _ct_hot_draw)[0] if _ct_e6 else None
+_ct_hot10 = _ct_walk(_ct_store(_ct_e10), 64.5, _ct_hot_heat, _ct_hot_draw)[0] if _ct_e10 else None
+_ct_cold6 = _ct_walk(_ct_store(_ct_e6), 45.0, [0.0] * 4, [3.0] * 4)[0] if _ct_e6 else None
+_ct_cold10 = _ct_walk(_ct_store(_ct_e10), 45.0, [0.0] * 4, [3.0] * 4)[0] if _ct_e10 else None
+R.check(
+    "combi eps null control: with the tap above the mixer, eps 0.6 and 1.0 walk the same "
+    "store; below it, the colder tap debits less",
+    _ct_hot6 is not None and _ct_hot6 == _ct_hot10 and _ct_hot6[-1] < _ct_hot6[0] - 1.0
+    and min(_ct_hot6) > _ct_store(_ct_e6).store_temp_for_tap(_CT_MIX)
+    and _ct_cold6[-1] > _ct_cold10[-1],
+    f"hot {(_ct_hot6 or [None])[-1]} vs {(_ct_hot10 or [None])[-1]}; "
+    f"cold {(_ct_cold6 or [None])[-1]} vs {(_ct_cold10 or [None])[-1]}",
+)
+
+# One node: the published walk's hot-water trajectory IS its buffer trajectory.
+_CT_N = 96
+
+
+def _ct_published(p):
+    m = ThermalModel(p)
+    out = np.full(_CT_N, 0.0)
+    space = np.full(_CT_N, 1.5)
+    dhw = np.zeros(_CT_N)
+    dhw[8:12] = 3.0
+    *_, dhw_t, buf_t, _ = m.simulate_trajectory_with_dhw(
+        initial_state=ThermalState(room_temperature=21.0, slab_temperature=23.0,
+                                   buffer_tank_temperature=55.0, dhw_temperature=55.0,
+                                   outdoor_temperature=0.0),
+        space_power_schedule=space, dhw_power_schedule=dhw, weather=_WS(out))
+    return dhw_t, buf_t
+
+
+_ct_pub = _ct_published(_ct_p) if _ct_p is not None else None
+_ct_pub_off = _ct_published(_ct_off) if _ct_off is not None else None
+R.check(
+    "combi: the published hot-water trajectory is the buffer trajectory, step for step; "
+    "null control: off, the two tanks part",
+    _ct_pub is not None and np.array_equal(_ct_pub[0], _ct_pub[1])
+    and not np.array_equal(_ct_pub_off[0], _ct_pub_off[1]),
+    "dhw_temps vs buffer_temps",
+)
+
+# Tap-stated minimums enter the store frame; the legionella target never does.
+_ct_tap = _ct_params(eps=0.85, dhw_min_temp=45.0, dhw_idle_min_temp=30.0)
+if _ct_tap is not None:
+    _ct_fl = _dhw_planner(_StoreOpt(ThermalModel(_ct_tap), _StoreCfg()))._dhw_window_floors(
+        _ct_tap, [(0.0, 24.0)], np.arange(24) * 1.0, None, 1.0, 24, None)
+    _ct_floor = float(_ct_fl[5][3])
+    _ct_hold = ThermalModel(_ct_tap).dhw_hold_hours()
+    _ct_need = 10.0 + 35.0 / 0.85
+    _ct_hold_ref = ThermalModel(_ct_tap).dhw_coast_hours(
+        max(_ct_store(_ct_tap).charge_max_temp, _ct_need + 1.0), _ct_need)
+else:
+    _ct_floor = _ct_hold = _ct_need = _ct_hold_ref = None
+R.check(
+    "combi: a 45 C tap minimum is a 51.18 C store floor at eps 0.85 (inlet 10 C), "
+    "in the planner's floors and the hold horizon alike",
+    _ct_floor is not None and abs(_ct_floor - _ct_need) < 1e-9 and abs(_ct_need - 51.176) < 1e-3
+    and _ct_hold == _ct_hold_ref,
+    f"floor {_ct_floor}, need {_ct_need}, hold {_ct_hold} vs {_ct_hold_ref}",
+)
+R.check(
+    "combi litres_40c: the heat above the store temperature that gives 40 C at the tap; "
+    "off, the separate tank's displacement rule",
+    _ct_p is not None
+    and abs(_ct_tm.dhw_mixed_litres(_ct_p, 60.0, 40.0)
+            - _ct_s.capacity_kwh_per_c * (60.0 - (10.0 + 30.0 / 0.85)) / (_CT_CP * 30.0)) < 1e-9
+    and _ct_tm.dhw_mixed_litres(_ct_off, 60.0, 40.0) == 200.0 * 50.0 / 30.0,
+    "litres at 60 C",
+)
+
+# The legionella target is a store temperature (standing water reaches the
+# store's own), so eps cannot move the cycle (legionella_eps, design T.2a).
+_CT_LEG = dict(dhw_legionella_enabled=True, dhw_legionella_temp=60.0,
+               dhw_legionella_interval_days=7.0, dhw_daily_consumption=0.0,
+               dhw_min_temp=30.0, dhw_idle_min_temp=20.0, dhw_schedule_enabled=True,
+               dhw_windows=_ct_windows("18:00-19:00"))
+
+
+def _ct_cycle(eps):
+    p = _ct_params(eps=eps, **_CT_LEG)
+    if p is None:
+        return None
+    opt = _StoreOpt(ThermalModel(p), _StoreCfg(horizon_hours=24, time_step_minutes=15))
+    plan, _ = _dhw_planner(opt)._build_dhw_requirements(
+        _dhw_horizon(prices=np.full(96, 1.0), outdoor=np.full(96, 0.0), n=96, dt=0.25,
+                     state=ThermalState(room_temperature=21.0, slab_temperature=22.0,
+                                        outdoor_temperature=0.0, dhw_temperature=50.0,
+                                        buffer_tank_temperature=50.0,
+                                        dhw_hours_since_legionella=7 * 24.0 - 6.0)),
+        p_max=4.0)
+    step = plan.legionella_step
+    return (plan.legionella_due, step, plan.legionella_hour,
+            None if step is None else float(np.max(plan.ready_temps)))
+
+
+_ct_leg6, _ct_leg10 = _ct_cycle(0.6), _ct_cycle(1.0)
+R.check(
+    "legionella_eps: the cycle's step, hour and target are the same at eps 0.6 and 1.0",
+    _ct_leg6 is not None and _ct_leg6 == _ct_leg10 and _ct_leg6[0] and _ct_leg6[3] == 60.0,
+    f"eps 0.6 {_ct_leg6}, eps 1.0 {_ct_leg10}",
+)
+
+# lp_flux: the planner buys hot water against the space side's draw on the
+# shared store, and a separate tank ignores the series (it is dead off).
+_CT_FLUX = dict(dhw_schedule_enabled=True, dhw_windows=_ct_windows("19:00-21:00"),
+                dhw_min_temp=40.0, dhw_idle_min_temp=20.0)
+_ct_exo = np.zeros(96)
+_ct_exo[60:76] = -2.0  # a 2 kW valve draw over the four hours before the window
+
+
+def _ct_flux_plan(combi, exo):
+    p = _ct_params(combi=combi, **_CT_FLUX)
+    if p is None:
+        return None, None, None
+    opt = _StoreOpt(ThermalModel(p), _StoreCfg(horizon_hours=24, time_step_minutes=15))
+    h = _dhw_horizon(prices=np.full(96, 1.0), outdoor=np.full(96, 0.0), n=96, dt=0.25,
+                     state=ThermalState(room_temperature=21.0, slab_temperature=22.0,
+                                        outdoor_temperature=0.0, dhw_temperature=50.0,
+                                        buffer_tank_temperature=50.0,
+                                        dhw_hours_since_legionella=1.0))
+    plan, _ = _dhw_planner(opt)._build_dhw_requirements(h, p_max=4.0, tank_exo_kw=exo)
+    temps = opt.model.simulate_dhw_only(
+        initial_temp=50.0, dhw_power_schedule=plan.schedule, outdoor_temps=np.full(96, 0.0),
+        draw_rates=plan.draw_rates, dt_hours=0.25,
+        exo_kw=exo if _ct_store(p).combi else None)
+    gap = float(np.max(np.maximum(plan.floor_temps, plan.ready_temps) - temps[1:]))
+    return float(np.sum(plan.schedule)) * 0.25, gap, plan.schedule
+
+
+_ct_f0 = _ct_flux_plan(True, np.zeros(96))
+_ct_f2 = _ct_flux_plan(True, _ct_exo)
+_ct_o0 = _ct_flux_plan(False, None)
+_ct_o2 = _ct_flux_plan(False, _ct_exo)
+R.check(
+    "lp_flux: a 2 kW valve draw before the window raises the hot water the plan buys, "
+    "and the store still meets every floor and the window's ready temperature",
+    _ct_f0[0] is not None and _ct_f2[0] > _ct_f0[0] + 1.0 and _ct_f2[1] <= 0.05,
+    f"kWh {_ct_f0[0]} -> {_ct_f2[0]}, worst shortfall {_ct_f2[1]}",
+)
+R.check(
+    "lp_flux null control: a separate tank's plan is unchanged by the same series",
+    _ct_o0[2] is not None and np.array_equal(_ct_o0[2], _ct_o2[2]),
+    f"kWh {_ct_o0[0]} vs {_ct_o2[0]}",
+)
+
+# The flux exchange, end to end: the joint solve's store meets the hot-water
+# requirement the space side drains; with no exchange rounds it does not.
+_CT_PRICES = np.full(96, 1.5)
+_CT_PRICES[:20] = 0.8
+_CT_PRICES[64:80] = 4.0
+
+
+def _ct_solve(rounds=None):
+    p = _ct_params()
+    if p is None:
+        return None, None
+    opt = _StoreOpt(ThermalModel(p), _StoreCfg(horizon_hours=24, time_step_minutes=15,
+                                               target_temp=21.0, min_temp=19.0, max_temp=23.0))
+    saved = getattr(_optmod, "_COMBI_EXCHANGE_ROUNDS", None)
+    if rounds is not None:
+        _optmod._COMBI_EXCHANGE_ROUNDS = rounds
+    try:
+        r = opt.optimize(inputs=solve_inputs(
+            initial_state=ThermalState(room_temperature=21.0, slab_temperature=23.0,
+                                       buffer_tank_temperature=50.0, dhw_temperature=50.0,
+                                       outdoor_temperature=0.0),
+            prices=_CT_PRICES, outdoor_temps=np.full(96, 0.0), wind_speeds=np.zeros(96),
+            precipitation=np.zeros(96), solar_radiation=np.zeros(96),
+            start_time=datetime(2026, 1, 15)))
+    finally:
+        if rounds is not None:
+            _optmod._COMBI_EXCHANGE_ROUNDS = saved
+    req = np.asarray(opt._dhw_requirement)
+    traj = np.asarray(r.dhw_temp_trajectory)[1:req.size + 1]
+    return float(np.max(req - traj)), r
+
+
+_ct_gap_x, _ct_res = _ct_solve()
+_ct_gap_0, _ = _ct_solve(rounds=0)
+R.check(
+    "combi flux exchange: the joint plan's store meets the hot-water requirement the "
+    "space side drains, and its published DHW and buffer trajectories are one",
+    _ct_gap_x is not None and _ct_gap_x <= 0.05
+    and list(_ct_res.dhw_temp_trajectory) == list(_ct_res.buffer_temp_trajectory),
+    f"worst shortfall {_ct_gap_x}",
+)
+R.check(
+    "combi flux exchange null control: with no exchange round the space side drains "
+    "the store below the requirement",
+    _ct_gap_0 is not None and _ct_gap_0 > 1.0,
+    f"worst shortfall without the exchange {_ct_gap_0}",
+)
+
+# Censuses (P2, _P2_CENSUSES in tests/entities.py). Each asserts its own reach.
+_CT_PKG = _ct_Path(_ct_tm.__file__).parent
+_ct_sources = {f.name: f.read_text() for f in sorted(_CT_PKG.glob("*.py"))}
+_ct_view = sorted(
+    f"{name}:{i}" for name, src in _ct_sources.items() if name != "thermal_model.py"
+    for i, line in enumerate(src.splitlines(), 1)
+    if "dhw_tank_thermal_mass" in line or "dhw_tank_heat_loss_coefficient" in line
+)
+R.check(
+    "combi_store_view census: outside thermal_model.py nothing reads the separate tank's "
+    "capacity or loss; every reader takes the store view",
+    len(_ct_sources) > 20 and "dhw_tank_heat_loss_coefficient" in _ct_sources["thermal_model.py"]
+    and not _ct_view,
+    f"readers {_ct_view} over {len(_ct_sources)} modules",
+)
+_ct_plan_tree = _ct_ast.parse(_ct_sources["dhw_planner.py"])
+_CT_WALKS = {"simulate_dhw_only", "extend_dhw_temps", "simulate_dhw_step", "_dhw_plan_temps"}
+_ct_walk_calls = [n for n in _ct_ast.walk(_ct_plan_tree) if isinstance(n, _ct_ast.Call)
+                  and isinstance(n.func, _ct_ast.Attribute) and n.func.attr in _CT_WALKS]
+_ct_blind = [n.lineno for n in _ct_walk_calls
+             if not any(k.arg == "exo_kw" for k in n.keywords)
+             and not (n.func.attr == "_dhw_plan_temps"
+                      and (len(n.args) == 7 or any(isinstance(a, _ct_ast.Starred) for a in n.args)))]
+_ct_fns = {n.name: _ct_ast.get_source_segment(_ct_sources["dhw_planner.py"], n)
+           for n in _ct_ast.walk(_ct_plan_tree) if isinstance(n, _ct_ast.FunctionDef)}
+_ct_affine = [f for f in ("_plan_dhw_min_cost", "_dhw_legionella_ceilings", "_clamp_dhw_to_capacity")
+              if "_exo_at(" not in _ct_fns.get(f, "")]
+_ct_space = [f for f in ("def simulate_trajectory(", "def simulate_trajectory_batch(")
+             if f not in _ct_sources["thermal_model.py"]
+             or "buffer_exo = weather.buffer_exo_kw" not in _ct_sources["thermal_model.py"].split(f)[1][:4000]]
+R.check(
+    "combi_flux_live census: every DHW walk the planner runs, and each of its three affine "
+    "recursions, carries the space side's flux, and both space walks read the DHW side's",
+    len(_ct_walk_calls) >= 10 and not _ct_blind and not _ct_affine and not _ct_space,
+    f"{len(_ct_walk_calls)} walks, blind at {_ct_blind}, affine without flux {_ct_affine}, "
+    f"space walks without it {_ct_space}",
+)
+_ct_tap_reads, _ct_tap_raw, _ct_leg_routed = 0, [], []
+for _ct_name, _ct_src in (("dhw_planner.py", _ct_sources["dhw_planner.py"]),
+                          ("thermal_model.py", _ct_sources["thermal_model.py"])):
+    _ct_tree = _ct_ast.parse(_ct_src)
+    _ct_routed = set()
+    for _ct_n in _ct_ast.walk(_ct_tree):
+        if isinstance(_ct_n, _ct_ast.Call) and isinstance(_ct_n.func, _ct_ast.Attribute) \
+                and _ct_n.func.attr == "store_temp_for_tap":
+            for _ct_a in _ct_ast.walk(_ct_n):
+                if isinstance(_ct_a, _ct_ast.Attribute):
+                    _ct_routed.add(id(_ct_a))
+                    if _ct_a.attr == "dhw_legionella_temp":
+                        _ct_leg_routed.append(f"{_ct_name}:{_ct_a.lineno}")
+    _ct_scope = _ct_tree if _ct_name == "dhw_planner.py" else next(
+        n for n in _ct_ast.walk(_ct_tree)
+        if isinstance(n, _ct_ast.FunctionDef) and n.name == "dhw_hold_hours")
+    for _ct_n in _ct_ast.walk(_ct_scope):
+        if isinstance(_ct_n, _ct_ast.Attribute) and _ct_n.attr in ("dhw_min_temp", "dhw_idle_min_temp") \
+                and isinstance(_ct_n.value, _ct_ast.Name) and _ct_n.value.id in ("params", "p"):
+            _ct_tap_reads += 1
+            if id(_ct_n) not in _ct_routed:
+                _ct_tap_raw.append(f"{_ct_name}:{_ct_n.lineno}")
+R.check(
+    "combi_tap_limit census: every tap-stated minimum the planner and the hold horizon read "
+    "enters the store frame, and the legionella target never does",
+    _ct_tap_reads >= 4 and not _ct_tap_raw and not _ct_leg_routed,
+    f"{_ct_tap_reads} reads; raw {_ct_tap_raw}; legionella routed {_ct_leg_routed}",
+)
+
+# R10-COMBI-TANK repair (#3358's tests / mutation): each guard and clamp the
+# combi store added, driven at the one input that separates it from its mutant.
+R.section("R10-COMBI-TANK: the combi store's guards and clamps, at the inputs that move them")
+import heatpump_optimizer.dhw_planner as _cg_dp  # noqa: E402
+
+_cg_unmet = [_ct_params(mixing_valve_mode=_mv.MODE_NONE), _ct_params(buffer_tank_volume=50.0),
+             _ct_params(dhw_enabled=False)]
+_cg_h8 = _dhw_horizon(prices=np.full(8, 1.0), outdoor=np.zeros(8), n=8, dt=0.25)
+
+
+def _cg_exo(p):
+    return _optmod._combi_dhw_exo(ThermalModel(p), _cg_h8, np.zeros(8), np.zeros(8))
+
+
+R.check(
+    "combi_store_of and the hot-water flux are None off combi and wherever its preconditions "
+    "fail with the option on; null control: on, the store and an 8-step series",
+    _ct_p is not None and all(q.dhw_combi_tank_enabled for q in _cg_unmet)
+    and all(_ct_tm.combi_store_of(q) is None and _cg_exo(q) is None for q in _cg_unmet + [_ct_off])
+    and _ct_tm.combi_store_of(_ct_p) == _ct_s and np.shape(_cg_exo(_ct_p)) == (8,),
+    "combi_store_of / _combi_dhw_exo off, unmet and on",
+)
+
+# The store's limits are the tighter of the hot-water and buffer ones: a
+# buffer rated below the hot-water setpoint caps both.
+_cg_low = _ct_params(buffer_max_temp=50.0)
+_cg_low_off = _ct_params(combi=False, buffer_max_temp=50.0)
+R.check(
+    "combi: a 50 C buffer rating caps the store's charge limit and rating alike; "
+    "null control: off, the separate tank keeps its own",
+    _cg_low is not None and _ct_store(_cg_low).charge_max_temp == 50.0
+    and _ct_store(_cg_low).rating_max_temp == 50.0
+    and _ct_store(_cg_low_off).charge_max_temp == _cg_low_off.dhw_max_temp > 50.0
+    and _ct_store(_cg_low_off).rating_max_temp == _cg_low_off.dhw_hard_max_temp > 50.0,
+    f"combi {_ct_store(_cg_low)}; off {_ct_store(_cg_low_off)}",
+)
+
+
+def _cg_step(store, temp, heat, dt):
+    try:
+        return _ct_tm.store_step(store, temp, heat, 0.0, 20.0, dt)
+    except ZeroDivisionError as err:
+        return repr(err)
+
+
+_cg_top = _ct_s.rating_max_temp if _ct_s is not None else 0.0
+_cg_empty = _cg_step(_ct_replace(_ct_s, capacity_kwh_per_c=0.0), 55.0, 3.0, 0.25) if _ct_s else None
+_cg_hot = _cg_step(_ct_s, _cg_top + 5.0, 0.0, 0.25) if _ct_s else None
+_cg_dt0 = _cg_step(_ct_s, 5.0, 0.0, 0.0) if _ct_s else None
+_cg_warm = _cg_step(_ct_s, 50.0, 3.0, 0.25) if _ct_s else None
+R.check(
+    "store_step: no capacity holds the temperature and books nothing; a charge below the "
+    "rating warms the store and refuses nothing; a store above its rating cools by its "
+    "loss and refuses nothing; a zero-length step from below the floor returns the floor "
+    "without dividing by zero",
+    _cg_empty == (55.0, 0.0, 0.0, 0.0)
+    and isinstance(_cg_warm, tuple) and _cg_warm[1] == 0.0 and _cg_warm[0] > 50.0
+    and isinstance(_cg_hot, tuple) and _cg_hot[1] == 0.0 and _cg_top < _cg_hot[0] < _cg_top + 5.0
+    and isinstance(_cg_dt0, tuple) and _cg_dt0[0] == min(_ct_s.inlet_c, 20.0) and _cg_dt0[1] == 0.0,
+    f"empty {_cg_empty}; charging {_cg_warm}; above the rating {_cg_hot}; zero step {_cg_dt0}",
+)
+_cg_net = (_ct_tm.combi_space_net_kw(_ct_s, [50.0, 50.0], [0.0], 0.0)
+           if _ct_s is not None else None)
+R.check(
+    "combi_space_net_kw: a zero-length step books the standing loss and no gain, a finite series",
+    _cg_net is not None and bool(np.all(np.isfinite(_cg_net)))
+    and abs(float(_cg_net[0]) - _ct_s.ua_kw_per_c * (50.0 - _ct_tm.TANK_ROOM_AMBIENT_TEMP)) < 1e-12,
+    f"net {_cg_net}",
+)
+
+# A tap minimum whose store floor sits above the charge limit: eps 0.6 puts a
+# 45 C tap at a 68.3 C store, above the 55 C limit, and the hold horizon still
+# coasts the kelvin above the floor.
+_cg_steep = _ct_params(eps=0.6, dhw_min_temp=45.0)
+if _cg_steep is not None:
+    _cg_floor = _ct_store(_cg_steep).store_temp_for_tap(45.0)
+    _cg_hold = ThermalModel(_cg_steep).dhw_hold_hours()
+    _cg_coast = ThermalModel(_cg_steep).dhw_coast_hours(_cg_floor + 1.0, _cg_floor)
+else:
+    _cg_floor = _cg_hold = _cg_coast = None
+R.check(
+    "combi hold horizon: a store floor above the charge limit coasts from a kelvin above "
+    "the floor, a positive horizon",
+    _cg_floor is not None and _cg_floor > _ct_store(_cg_steep).charge_max_temp + 1.0
+    and _cg_hold == _cg_coast and _cg_hold > 0.0,
+    f"floor {_cg_floor}, limit {_ct_store(_cg_steep).charge_max_temp if _cg_steep else None}, "
+    f"hold {_cg_hold} vs {_cg_coast}",
+)
+
+# An idle minimum stated above the window minimum never raises the idle floor
+# past it, in the store frame (combi) and the tank's own (off).
+_cg_idle = []
+for _cg_combi in (True, False):
+    _cg_q = _ct_params(combi=_cg_combi, dhw_min_temp=45.0, dhw_idle_min_temp=50.0)
+    if _cg_q is None:
+        break
+    _cg_fl = _dhw_planner(_StoreOpt(ThermalModel(_cg_q), _StoreCfg()))._dhw_window_floors(
+        _cg_q, [(18.0, 19.0)], np.arange(24) * 1.0, None, 1.0, 24, None)
+    _cg_idle.append((float(_cg_fl[5][3]), _ct_store(_cg_q).store_temp_for_tap(45.0),
+                     _ct_store(_cg_q).store_temp_for_tap(50.0)))
+R.check(
+    "idle floor: a 50 C idle minimum above a 45 C window minimum floors idle steps at the "
+    "window minimum's store temperature, combi and off",
+    len(_cg_idle) == 2 and all(f == lo < hi for f, lo, hi in _cg_idle),
+    f"(idle floor, window minimum, idle minimum) per arm {_cg_idle}",
+)
+
+
+# A rating with no headroom above the charge limit leaves the cycle no boost:
+# the ceilings stay the everyday ones and no run-up floor is set. Null
+# control: a 55 C limit under a 60 C rating runs up to the cycle's step.
+def _cg_ceilings(setpoint):
+    p = ThermalParameters(dhw_enabled=True, dhw_setpoint=setpoint, dhw_legionella_enabled=True,
+                          dhw_legionella_temp=60.0, dhw_legionella_interval_days=7.0)
+    leg = _dhw_planner(_StoreOpt(ThermalModel(p), _StoreCfg()))._dhw_legionella_ceilings(
+        _dhw_horizon(prices=np.full(96, 1.0), outdoor=np.zeros(96), n=96, dt=0.25),
+        params=p, draw_rates=np.zeros(96), floor_temps=np.full(96, 20.0), p_dhw_run=4.0,
+        legionella_due=True, legionella_hour=10.0, legionella_step=40)
+    return p.dhw_store, leg
+
+
+_cg_flat_store, _cg_flat = _cg_ceilings(60.0)
+_cg_room_store, _cg_room = _cg_ceilings(55.0)
+R.check(
+    "legionella ceilings: with the rating at the charge limit no step's ceiling moves and "
+    "no run-up floor is set; null control: below the rating the cycle runs up",
+    _cg_flat_store.rating_max_temp == _cg_flat_store.charge_max_temp == 60.0
+    and not np.any(_cg_flat.runup_temps) and bool(np.all(_cg_flat.lp_max_temp == 60.0))
+    and _cg_room_store.rating_max_temp > _cg_room_store.charge_max_temp
+    and float(np.max(_cg_room.runup_temps[:40])) > 20.0,
+    f"flat run-up max {float(np.max(_cg_flat.runup_temps))}; "
+    f"null run-up max {float(np.max(_cg_room.runup_temps[:40]))}",
+)
+
+# The flux exchange's rounds: a plan that stops moving stops the rounds, and a
+# plan still moving at the cap is published after four DHW plan builds (the
+# cap prices the exchange on a Pi-class host).
+_cg_real_build = _cg_dp.DhwPlanner._build_dhw_requirements
+_cg_real_x = _optmod._combi_flux_exchange
+
+
+def _cg_rounds(moving):
+    runs = []
+
+    def build(self, *a, **k):
+        plan, req = _cg_real_build(self, *a, **k)
+        if runs and k.get("tank_exo_kw") is not None:
+            runs[-1] += 1
+            if moving:
+                plan = _ct_replace(plan, schedule=plan.schedule + 1e-3 * runs[-1])
+        return plan, req
+
+    def exchange(*a, **k):
+        runs.append(0)
+        return _cg_real_x(*a, **k)
+
+    _cg_dp.DhwPlanner._build_dhw_requirements = build
+    _optmod._combi_flux_exchange = exchange
+    try:
+        _ct_solve()
+    finally:
+        _cg_dp.DhwPlanner._build_dhw_requirements = _cg_real_build
+        _optmod._combi_flux_exchange = _cg_real_x
+    return runs
+
+
+_cg_still = _cg_rounds(False) if _ct_p is not None else []
+_cg_moving = _cg_rounds(True) if _ct_p is not None else []
+R.check(
+    "combi flux exchange: a plan that stops moving ends the rounds before the cap; one still "
+    "moving is published after exactly four plan builds",
+    bool(_cg_still) and all(0 < n < 4 for n in _cg_still)
+    and bool(_cg_moving) and all(n == 4 for n in _cg_moving),
+    f"builds per exchange: converging {_cg_still}, moving {_cg_moving}",
+)
+
+
+# Two-zone: the hot-water side's flux enters the store behind a throttling
+# valve, in the scalar walk and its batch twin, and moves nothing without one.
+def _cg_two_zone(p, exo):
+    m = ThermalModel(p)
+    n = 16
+    w = _ct_replace(_WS(np.zeros(n)), buffer_exo_kw=exo)
+    st = ThermalState(room_temperature=21.0, slab_temperature=23.0, upper_floor_temperature=21.0,
+                      lower_floor_temperature=21.0, buffer_tank_temperature=50.0,
+                      dhw_temperature=50.0, outdoor_temperature=0.0)
+    scalar = m.simulate_trajectory(initial_state=st, power_schedule=np.full(n, 1.5), weather=w)
+    batch = m.simulate_trajectory_batch(st, np.full((1, n), 1.5), w)
+    return [np.asarray(a) for a in scalar], {k: np.asarray(v) for k, v in batch.items()}
+
+
+_cg_tz = _ct_params(two_zone_enabled=True)
+_cg_tz_open = _ct_params(combi=False, two_zone_enabled=True, mixing_valve_mode=_mv.MODE_NONE)
+if _cg_tz is not None:
+    _cg_exo16 = np.full(16, 2.0)
+    _cg_on0, _cg_on0b = _cg_two_zone(_cg_tz, None)
+    _cg_on2, _cg_on2b = _cg_two_zone(_cg_tz, _cg_exo16)
+    _cg_op0, _cg_op0b = _cg_two_zone(_cg_tz_open, None)
+    _cg_op2, _cg_op2b = _cg_two_zone(_cg_tz_open, _cg_exo16)
+    _cg_gain = (float(_cg_on2[4][-1] - _cg_on0[4][-1]), float(_cg_on2b["buffer"][0, -1]
+                                                              - _cg_on0b["buffer"][0, -1]))
+    _cg_same = (all(np.array_equal(a, b) for a, b in zip(_cg_op0, _cg_op2))
+                and all(np.array_equal(_cg_op0b[k], _cg_op2b[k]) for k in _cg_op0b))
+else:
+    _cg_gain, _cg_same = (0.0, 0.0), False
+R.check(
+    "two-zone combi: a 2 kW hot-water flux warms the store in the scalar walk and the batch "
+    "twin alike; behind no valve the same series moves no output of either",
+    _cg_gain[0] > 1.0 and _cg_gain[1] > 1.0 and _cg_same,
+    f"store gain scalar {_cg_gain[0]:.4f} C, batch {_cg_gain[1]:.4f} C; unvalved unchanged {_cg_same}",
+)
+
 # R10-BUFFER-STORE review 1: the savings reference sized its power from the
 # emitters' need as if the step delivered it straight to them, so behind a
 # valve its tank climbed to buffer_max_temp and the refused heat was paid for
@@ -38770,7 +39444,7 @@ R.check(
 
 _fr_fixed = _dhw_planner(_fr_opt)._repair_dhw_floor(
     _dhw_ctx(prices=_fr_prices, outdoor=_fr_outdoor,
-             n=_fr_plan.size, dt=_FR_DT, c_dhw=_fr_c, p_dhw_max=_FR_RUN,
+             n=_fr_plan.size, dt=_FR_DT, params=_fr_opt.model.params, c_dhw=_fr_c, p_dhw_max=_FR_RUN,
              min_run_power=_FR_MIN),
     plan=_fr_plan.copy(), initial_temp=52.0,
     draw_rates=_fr_draws, requirement=_fr_req, max_temp=_fr_ceiling,
@@ -41305,6 +41979,7 @@ _g2_saved_extend = _G2Tm.extend_dhw_temps
 
 def _g2_extend_via_full_sim(
     self, temps, from_step, schedule, outdoor, draws, dt_hours=0.25, humidity=None,
+    exo_kw=None,
 ):
     _G2Tm.extend_dhw_temps = _g2_saved_extend
     try:
@@ -41315,6 +41990,7 @@ def _g2_extend_via_full_sim(
             draw_rates=draws,
             dt_hours=dt_hours,
             humidity=humidity,
+            exo_kw=exo_kw,
         )
     finally:
         _G2Tm.extend_dhw_temps = _g2_extend_via_full_sim
@@ -41475,6 +42151,7 @@ _mr_saved_extend = _G2Tm.extend_dhw_temps
 
 def _mr_extend_via_full_sim(
     self, temps, from_step, schedule, outdoor, draws, dt_hours=0.25, humidity=None,
+    exo_kw=None,
 ):
     _G2Tm.extend_dhw_temps = _mr_saved_extend
     try:
@@ -41485,6 +42162,7 @@ def _mr_extend_via_full_sim(
             draw_rates=draws,
             dt_hours=dt_hours,
             humidity=humidity,
+            exo_kw=exo_kw,
         )
     finally:
         _G2Tm.extend_dhw_temps = _mr_extend_via_full_sim
@@ -58880,7 +59558,7 @@ def _r7d203_window_capacity(volume):
     res = _dhw_planner(opt)._dhw_window_floors(
         params, windows, np.arange(96) * 0.25, None, 0.25, 96, None
     )
-    return res[0], params.dhw_tank_thermal_mass
+    return res[0].capacity_kwh_per_c, params.dhw_tank_thermal_mass
 
 
 # The three planners below each took the floored capacity as a whole, so a
@@ -58895,7 +59573,7 @@ def _r7d203_min_cost(c_dhw, n=12, dt=1.0):
     opt, _ = _r7d203_opt(200.0, dhw_cooling_rate=0.3)
     plan = _dhw_planner(opt)._plan_dhw_min_cost(
         _dhw_ctx(prices=np.full(n, 1.0), outdoor=np.full(n, -5.0),
-                 n=n, dt=dt, c_dhw=c_dhw, p_dhw_max=3.0),
+                 n=n, dt=dt, params=opt.model.params, c_dhw=c_dhw, p_dhw_max=3.0),
         45.0, np.full(n, 60.0), np.zeros(n), np.full(n, 60.0),
     )
     return None if plan is None else float(plan.sum())
@@ -58914,7 +59592,7 @@ def _r7d203_greedy_steps(c_dhw, volume=43.1, req=50.0, ceiling=55.0, n=12):
     opt, _ = _r7d203_opt(volume, dhw_cooling_rate=0.3)
     plan = _dhw_planner(opt)._plan_dhw_cheapest_first(
         _dhw_ctx(prices=np.linspace(0.2, 2.0, n), outdoor=np.full(n, -5.0),
-                 n=n, dt=1.0, c_dhw=c_dhw, p_dhw_max=3.0),
+                 n=n, dt=1.0, params=opt.model.params, c_dhw=c_dhw, p_dhw_max=3.0),
         45.0, np.full(n, req), np.zeros(n), np.full(n, ceiling),
     )
     return [i for i, value in enumerate(plan) if value > 0.0]
@@ -58941,7 +59619,7 @@ def _r7d203_repair_steps(c_dhw, ceiling, requirement, volume=17.24, n=12):
     opt, _ = _r7d203_opt(volume, dhw_cooling_rate=3.0)
     plan = _dhw_planner(opt)._repair_dhw_floor(
         _dhw_ctx(prices=np.linspace(0.5, 1.5, n), outdoor=np.full(n, -5.0),
-                 n=n, dt=1.0, c_dhw=c_dhw, p_dhw_max=3.0),
+                 n=n, dt=1.0, params=opt.model.params, c_dhw=c_dhw, p_dhw_max=3.0),
         plan=np.zeros(n), initial_temp=45.0, draw_rates=np.zeros(n),
         requirement=np.asarray(requirement, dtype=float),
         max_temp=np.asarray(ceiling, dtype=float),
@@ -59088,29 +59766,29 @@ def _r7d203_zero_capacity():
     try:
         window = float(_dhw_planner(opt)._dhw_window_floors(
             params, windows, np.arange(24) * 1.0, None, 1.0, 24, None
-        )[0])
+        )[0].capacity_kwh_per_c)
         legionella = _dhw_planner(opt)._dhw_legionella_ceilings(
             _dhw_horizon(prices=np.full(12, 1.0), outdoor=np.full(12, -5.0),
                          n=12, dt=1.0),
-            params=params, c_dhw=0.0,
+            params=params,
             draw_rates=np.zeros(12), floor_temps=np.full(12, 45.0),
             p_dhw_run=3.0,
             legionella_due=True, legionella_hour=6.0, legionella_step=5,
         )
         min_cost = _dhw_planner(opt)._plan_dhw_min_cost(
             _dhw_ctx(prices=np.full(12, 1.0), outdoor=np.full(12, -5.0),
-                     n=12, dt=1.0, c_dhw=0.0, p_dhw_max=3.0),
+                     n=12, dt=1.0, params=opt.model.params, c_dhw=0.0, p_dhw_max=3.0),
             45.0, np.full(12, 55.0), np.zeros(12), np.full(12, 55.0),
         )
         repair = _dhw_planner(opt)._repair_dhw_floor(
             _dhw_ctx(prices=np.full(12, 1.0), outdoor=np.full(12, -5.0),
-                     n=12, dt=1.0, c_dhw=0.0, p_dhw_max=3.0),
+                     n=12, dt=1.0, params=opt.model.params, c_dhw=0.0, p_dhw_max=3.0),
             plan=np.zeros(12), initial_temp=45.0, draw_rates=np.zeros(12),
             requirement=np.full(12, 55.0), max_temp=np.full(12, 55.0),
         )
         greedy = _dhw_planner(opt)._plan_dhw_cheapest_first(
             _dhw_ctx(prices=np.full(12, 1.0), outdoor=np.full(12, -5.0),
-                     n=12, dt=1.0, c_dhw=0.0, p_dhw_max=3.0,
+                     n=12, dt=1.0, params=opt.model.params, c_dhw=0.0, p_dhw_max=3.0,
                      max_lead_steps=6),
             45.0, np.full(12, 55.0), np.zeros(12), np.full(12, 55.0),
         )
@@ -59220,7 +59898,7 @@ _r7pin_opt, _ = _r7d203_opt(200.0)
 try:
     _r7pin_plan = _dhw_planner(_r7pin_opt)._plan_dhw_min_cost(
         _dhw_ctx(prices=np.array([0.1] * 4 + [1.0] * 4),
-                 outdoor=np.full(8, -5.0), n=8, dt=1.0, c_dhw=0.232,
+                 outdoor=np.full(8, -5.0), n=8, dt=1.0, params=_r7pin_opt.model.params, c_dhw=0.232,
                  p_dhw_max=3.0),
         45.0, np.array([45.0] * 7 + [55.0]), np.zeros(8), np.full(8, 60.0),
         space_demand=np.array([5.0] * 4 + [0.0] * 4), p_total_max=5.0,
@@ -59272,7 +59950,7 @@ def _r7ua_min_cost(volume):
     n = 12
     plan = _dhw_planner(opt)._plan_dhw_min_cost(
         _dhw_ctx(prices=np.linspace(0.5, 1.5, n), outdoor=np.full(n, -5.0),
-                 n=n, dt=1.0, c_dhw=c, p_dhw_max=50.0 * c),
+                 n=n, dt=1.0, params=opt.model.params, c_dhw=c, p_dhw_max=50.0 * c),
         45.0, np.array([45.0] * 8 + [55.0] * 4), np.zeros(n),
         np.full(n, 60.0),
     )
@@ -59285,7 +59963,7 @@ def _r7ua_repair(volume):
     n = 12
     plan = _dhw_planner(opt)._repair_dhw_floor(
         _dhw_ctx(prices=np.linspace(0.5, 1.5, n), outdoor=np.full(n, -5.0),
-                 n=n, dt=1.0, c_dhw=c, p_dhw_max=50.0 * c,
+                 n=n, dt=1.0, params=opt.model.params, c_dhw=c, p_dhw_max=50.0 * c,
                  min_run_power=5.0 * c),
         plan=np.zeros(n), initial_temp=45.0, draw_rates=np.zeros(n),
         requirement=np.array([45.0] * 9 + [60.0] * 3),
@@ -59301,7 +59979,7 @@ def _r7ua_legionella(volume):
     res = _dhw_planner(opt)._dhw_legionella_ceilings(
         _dhw_horizon(prices=np.zeros(n), outdoor=np.full(n, -5.0),
                      n=n, dt=1.0),
-        params=params, c_dhw=c, draw_rates=np.zeros(n),
+        params=params, draw_rates=np.zeros(n),
         floor_temps=np.full(n, 20.0),
         p_dhw_run=2.0 * c, legionella_due=True, legionella_hour=20.0,
         legionella_step=20,
@@ -64289,10 +64967,10 @@ _f22_breach_offsets: list[int] = []
 
 
 def _f22_whole_suffix_fits(
-    self, candidate, base, ceiling, slot, plan, outdoor, draws, dt, humidity
+    self, candidate, base, ceiling, slot, plan, outdoor, draws, dt, humidity, exo_kw=None
 ):
     self.model.extend_dhw_temps(
-        candidate, slot, plan, outdoor, draws, dt_hours=dt, humidity=humidity
+        candidate, slot, plan, outdoor, draws, dt_hours=dt, humidity=humidity, exo_kw=exo_kw
     )
     limit = np.maximum(ceiling[: candidate.size], base)
     bad = np.nonzero(candidate[slot + 1:] > limit[slot + 1:] + 1e-9)[0]
@@ -76005,7 +76683,7 @@ def _pli_lp_end(derate, p_dhw_max=3.0, dt=1.0):
     req[-1] = 58.0
     prices = np.array([5.0] * (n - 1) + [1.0])
     ctx = _dhw_ctx(prices=prices, outdoor=np.full(n, 5.0), n=n, dt=dt,
-                   c_dhw=opt.model.params.dhw_tank_thermal_mass, p_dhw_max=p_dhw_max)
+                   params=opt.model.params, c_dhw=opt.model.params.dhw_tank_thermal_mass, p_dhw_max=p_dhw_max)
     planner = _dhw_planner(opt)
     plan = planner._plan_dhw_min_cost(ctx, 45.0, req, np.zeros(n), np.full(n, 65.0))
     temps = opt.model.simulate_dhw_only(
@@ -76084,7 +76762,7 @@ def _pli_greedy(derate, need=50.0, n=4, dt=0.5, p_dhw_max=3.0):
     req[-1] = need
     plan = _dhw_planner(opt)._plan_dhw_cheapest_first(
         _dhw_ctx(prices=np.linspace(2.0, 1.0, n), outdoor=out, n=n, dt=dt,
-                 c_dhw=opt.model.params.dhw_tank_thermal_mass, p_dhw_max=p_dhw_max),
+                 params=opt.model.params, c_dhw=opt.model.params.dhw_tank_thermal_mass, p_dhw_max=p_dhw_max),
         45.0, req, np.zeros(n), np.full(n, 65.0))
     temps = opt.model.simulate_dhw_only(
         initial_temp=45.0, dhw_power_schedule=plan, outdoor_temps=out,
@@ -76116,7 +76794,7 @@ def _pli_runup(derate):
     n = 24
     res = _dhw_planner(opt)._dhw_legionella_ceilings(
         _dhw_horizon(prices=np.zeros(n), outdoor=np.full(n, -5.0), n=n, dt=1.0),
-        params=params, c_dhw=params.dhw_tank_thermal_mass, draw_rates=np.zeros(n),
+        params=params, draw_rates=np.zeros(n),
         floor_temps=np.full(n, 20.0), p_dhw_run=3.0, legionella_due=True,
         legionella_hour=20.0, legionella_step=20)
     return [round(float(x), 4) for x in res.runup_temps]
@@ -76142,7 +76820,7 @@ def _pli_repair(derate, need=52.0, ceiling=(65.0,) * 4, prices=(2.0, 1.6667, 1.3
     req = np.full(n, 40.0)
     req[-1] = need
     ctx = _dhw_ctx(prices=np.array(prices), outdoor=out, n=n, dt=0.5,
-                   c_dhw=opt.model.params.dhw_tank_thermal_mass, p_dhw_max=5.0)
+                   params=opt.model.params, c_dhw=opt.model.params.dhw_tank_thermal_mass, p_dhw_max=5.0)
     plan = _dhw_planner(opt)._repair_dhw_floor(
         ctx, plan=np.zeros(n), initial_temp=45.0, draw_rates=np.zeros(n),
         requirement=req, max_temp=np.array(ceiling))
diff --git a/tests/guard_pins.py b/tests/guard_pins.py
index 75a8043ea..2d888a0dd 100644
--- a/tests/guard_pins.py
+++ b/tests/guard_pins.py
@@ -163,7 +163,6 @@ def _runup_stops_at_the_ordinary_floor() -> bool:
             heat_loss_factors=np.ones(n_steps), forecast={}, t_start=0.0,
         ),
         params=params,
-        c_dhw=max(params.dhw_tank_thermal_mass, 0.05),
         draw_rates=np.zeros(n_steps),
         floor_temps=floor_temps,
         p_dhw_run=3.0,
diff --git a/tests/mutation_ledger/killed_by/battery.py/build.BOOLOP.d0e56937.json b/tests/mutation_ledger/killed_by/battery.py/build.BOOLOP.d0e56937.json
new file mode 100644
index 000000000..3b0ee15b4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/battery.py/build.BOOLOP.d0e56937.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/battery.py:build BOOLOP d0e56937",
+  "killed_by": "tests/features.py",
+  "old": "    if params.dhw_enabled and not store.combi:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if params.dhw_enabled or not store.combi:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/battery.py/build.GUARD_OFF.19bc981b.json b/tests/mutation_ledger/killed_by/battery.py/build.GUARD_OFF.19bc981b.json
deleted file mode 100644
index f4780a13f..000000000
--- a/tests/mutation_ledger/killed_by/battery.py/build.GUARD_OFF.19bc981b.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/battery.py:build GUARD_OFF 19bc981b",
-  "killed_by": "tests/features.py",
-  "old": "    if params.dhw_enabled:",
-  "reason": "arrived with origin/main, commit d62195ade (fix(D12): guard the battery buffer/DHW stores on the config signal). `if params.dhw_enabled:` -> `if False:` raises the driver's `FAILED` count to 2 against a 0 baseline. Measured at the post-main head, 2026-09-22."
-}
diff --git a/tests/mutation_ledger/killed_by/battery.py/build.GUARD_OFF.d0e56937.json b/tests/mutation_ledger/killed_by/battery.py/build.GUARD_OFF.d0e56937.json
new file mode 100644
index 000000000..67d62d2c5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/battery.py/build.GUARD_OFF.d0e56937.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/battery.py:build GUARD_OFF d0e56937",
+  "killed_by": "tests/features.py",
+  "old": "    if params.dhw_enabled and not store.combi:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_legionella_ceilings.CLAMP_DROP.ab570bf1.json b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_legionella_ceilings.CLAMP_DROP.ab570bf1.json
new file mode 100644
index 000000000..e4abe0ef7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_legionella_ceilings.CLAMP_DROP.ab570bf1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._dhw_legionella_ceilings CLAMP_DROP ab570bf1",
+  "killed_by": "tests/manual_plan.py",
+  "old": "        boost_top = min(70.0, float(store.rating_max_temp))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`boost_top = (70.0)`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_legionella_ceilings.CMP_BOUND.456b4bfb.json b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_legionella_ceilings.CMP_BOUND.456b4bfb.json
new file mode 100644
index 000000000..147a0a4b7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_legionella_ceilings.CMP_BOUND.456b4bfb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._dhw_legionella_ceilings CMP_BOUND 456b4bfb",
+  "killed_by": "tests/features.py",
+  "old": "            boost_top > float(store.charge_max_temp)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`boost_top >= float(store.charge_max_temp)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_window_floors.CLAMP_DROP.6523b9c6.json b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_window_floors.CLAMP_DROP.6523b9c6.json
new file mode 100644
index 000000000..0dae9f381
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_window_floors.CLAMP_DROP.6523b9c6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._dhw_window_floors CLAMP_DROP 6523b9c6",
+  "killed_by": "tests/features.py",
+  "old": "        idle_min_temp = min(store.store_temp_for_tap(params.dhw_idle_min_temp), dhw_min_temp)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`idle_min_temp = (store.store_temp_for_tap(params.dhw_idle_min_temp))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._plan_dhw_min_cost.CLAMP_DROP.41cffe03.json b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._plan_dhw_min_cost.CLAMP_DROP.41cffe03.json
new file mode 100644
index 000000000..927e3ae70
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._plan_dhw_min_cost.CLAMP_DROP.41cffe03.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._plan_dhw_min_cost CLAMP_DROP 41cffe03",
+  "killed_by": "tests/features.py",
+  "old": "            np.maximum(requirement, ctx.store.store_temp_for_tap(params.dhw_min_temp)), humidity",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`(requirement), humidity`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/_DhwPlanContext.c_dhw.RETURN_DEL.e37bb5f4.json b/tests/mutation_ledger/killed_by/dhw_planner.py/_DhwPlanContext.c_dhw.RETURN_DEL.e37bb5f4.json
new file mode 100644
index 000000000..04ca1faa5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/_DhwPlanContext.c_dhw.RETURN_DEL.e37bb5f4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:_DhwPlanContext.c_dhw RETURN_DEL e37bb5f4",
+  "killed_by": "tests/manual_plan.py",
+  "old": "        return self.store.capacity_kwh_per_c",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/_DhwPlanContext.tank_decay.RETURN_DEL.22d7e1e8.json b/tests/mutation_ledger/killed_by/dhw_planner.py/_DhwPlanContext.tank_decay.RETURN_DEL.22d7e1e8.json
new file mode 100644
index 000000000..b08441fc8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/_DhwPlanContext.tank_decay.RETURN_DEL.22d7e1e8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:_DhwPlanContext.tank_decay RETURN_DEL 22d7e1e8",
+  "killed_by": "tests/manual_plan.py",
+  "old": "        return _tank_decay(self.store.ua_kw_per_c, self.dt, self.c_dhw)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/_exo_at.RETURN_DEL.1768b4d1.json b/tests/mutation_ledger/killed_by/dhw_planner.py/_exo_at.RETURN_DEL.1768b4d1.json
new file mode 100644
index 000000000..deff03e1f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/_exo_at.RETURN_DEL.1768b4d1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:_exo_at RETURN_DEL 1768b4d1",
+  "killed_by": "tests/manual_plan.py",
+  "old": "    return 0.0 if exo_kw is None else float(exo_kw[i])",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/@module.CONST.ff7e3dcd.json b/tests/mutation_ledger/killed_by/optimizer.py/@module.CONST.ff7e3dcd.json
new file mode 100644
index 000000000..e4ccc7244
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/@module.CONST.ff7e3dcd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:<module> CONST ff7e3dcd",
+  "killed_by": "tests/features.py",
+  "old": "_COMBI_EXCHANGE_ROUNDS = 4",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`_COMBI_EXCHANGE_ROUNDS = 8`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._co_optimize.BOOLOP.91c5b887.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._co_optimize.BOOLOP.91c5b887.json
new file mode 100644
index 000000000..5de21c02b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._co_optimize.BOOLOP.91c5b887.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._co_optimize BOOLOP 91c5b887",
+  "killed_by": "tests/features.py",
+  "old": "            if draw_rates is not None and self.model.params.dhw_store.combi:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if draw_rates is not None or self.model.params.dhw_store.combi:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._co_optimize.GUARD_OFF.91c5b887.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._co_optimize.GUARD_OFF.91c5b887.json
new file mode 100644
index 000000000..ecf998731
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._co_optimize.GUARD_OFF.91c5b887.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._co_optimize GUARD_OFF 91c5b887",
+  "killed_by": "tests/features.py",
+  "old": "            if draw_rates is not None and self.model.params.dhw_store.combi:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._deferred_energy_cost.GUARD_OFF.f5c46daf.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._deferred_energy_cost.GUARD_OFF.f5c46daf.json
new file mode 100644
index 000000000..8f113392d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._deferred_energy_cost.GUARD_OFF.f5c46daf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._deferred_energy_cost GUARD_OFF f5c46daf",
+  "killed_by": "tests/features.py",
+  "old": "        if include_dhw and not (p.dhw_store.combi and p.two_zone_enabled):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._stored_thermal_energy.GUARD_OFF.f5c46daf.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._stored_thermal_energy.GUARD_OFF.f5c46daf.json
new file mode 100644
index 000000000..60b806ee1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._stored_thermal_energy.GUARD_OFF.f5c46daf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._stored_thermal_energy GUARD_OFF f5c46daf",
+  "killed_by": "tests/features.py",
+  "old": "        if include_dhw and not (p.dhw_store.combi and p.two_zone_enabled):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_combi_dhw_exo.GUARD_OFF.f195744f.json b/tests/mutation_ledger/killed_by/optimizer.py/_combi_dhw_exo.GUARD_OFF.f195744f.json
new file mode 100644
index 000000000..17d973890
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_combi_dhw_exo.GUARD_OFF.f195744f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_dhw_exo GUARD_OFF f195744f",
+  "killed_by": "tests/features.py",
+  "old": "    if not p.combi_tank_active:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_combi_dhw_exo.RETURN_DEL.371740dd.json b/tests/mutation_ledger/killed_by/optimizer.py/_combi_dhw_exo.RETURN_DEL.371740dd.json
new file mode 100644
index 000000000..89825d92f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_combi_dhw_exo.RETURN_DEL.371740dd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_dhw_exo RETURN_DEL 371740dd",
+  "killed_by": "tests/features.py",
+  "old": "    return combi_dhw_net_series(model, temps, schedule, draw_rates, h.outdoor_temps, h.humidity)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.GUARD_OFF.ba727eb5.json b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.GUARD_OFF.ba727eb5.json
new file mode 100644
index 000000000..a532a51c9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.GUARD_OFF.ba727eb5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_flux_exchange GUARD_OFF ba727eb5",
+  "killed_by": "tests/features.py",
+  "old": "        if np.allclose(plan.schedule, dhw_power, atol=1e-4):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.RETURN_DEL.d235e41f.json b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.RETURN_DEL.d235e41f.json
new file mode 100644
index 000000000..b2cba6274
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.RETURN_DEL.d235e41f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_flux_exchange RETURN_DEL d235e41f",
+  "killed_by": "tests/features.py",
+  "old": "    return dhw_power",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_with_buffer_exo.RETURN_DEL.f71de30b.json b/tests/mutation_ledger/killed_by/optimizer.py/_with_buffer_exo.RETURN_DEL.f71de30b.json
new file mode 100644
index 000000000..98aecc5a7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_with_buffer_exo.RETURN_DEL.f71de30b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_with_buffer_exo RETURN_DEL f71de30b",
+  "killed_by": "tests/plan_view.py",
+  "old": "    return weather if buffer_exo_kw is None else replace(weather, buffer_exo_kw=buffer_exo_kw)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.space_flux.RETURN_DEL.9de167ed.json b/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.space_flux.RETURN_DEL.9de167ed.json
new file mode 100644
index 000000000..fe4fd6ae6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.space_flux.RETURN_DEL.9de167ed.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:DhwStore.space_flux RETURN_DEL 9de167ed",
+  "killed_by": "tests/features.py",
+  "old": "        return space_net_kw if self.combi else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.store_temp_for_tap.GUARD_OFF.95502b11.json b/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.store_temp_for_tap.GUARD_OFF.95502b11.json
new file mode 100644
index 000000000..b19cb31ee
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.store_temp_for_tap.GUARD_OFF.95502b11.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:DhwStore.store_temp_for_tap GUARD_OFF 95502b11",
+  "killed_by": "tests/features.py",
+  "old": "        if not self.combi:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.store_temp_for_tap.RETURN_DEL.f06db824.json b/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.store_temp_for_tap.RETURN_DEL.f06db824.json
new file mode 100644
index 000000000..902ad5017
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.store_temp_for_tap.RETURN_DEL.f06db824.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:DhwStore.store_temp_for_tap RETURN_DEL f06db824",
+  "killed_by": "tests/features.py",
+  "old": "        return self.inlet_c + (tap_c - self.inlet_c) / self.effectiveness",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.tap_temp_for_store.GUARD_OFF.95502b11.json b/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.tap_temp_for_store.GUARD_OFF.95502b11.json
new file mode 100644
index 000000000..55bc722c4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.tap_temp_for_store.GUARD_OFF.95502b11.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:DhwStore.tap_temp_for_store GUARD_OFF 95502b11",
+  "killed_by": "tests/features.py",
+  "old": "        if not self.combi:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.tap_temp_for_store.RETURN_DEL.3fab1e26.json b/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.tap_temp_for_store.RETURN_DEL.3fab1e26.json
new file mode 100644
index 000000000..1ffc90b82
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/DhwStore.tap_temp_for_store.RETURN_DEL.3fab1e26.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:DhwStore.tap_temp_for_store RETURN_DEL 3fab1e26",
+  "killed_by": "tests/features.py",
+  "old": "        return self.inlet_c + self.effectiveness * (store_c - self.inlet_c)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._simulate_step_two_zone.BOOLOP.2fe6a11c.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._simulate_step_two_zone.BOOLOP.2fe6a11c.json
new file mode 100644
index 000000000..42f642994
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._simulate_step_two_zone.BOOLOP.2fe6a11c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalModel._simulate_step_two_zone BOOLOP 2fe6a11c",
+  "killed_by": "tests/features.py",
+  "old": "        if throttled and buffer_exo_kw:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if throttled or buffer_exo_kw:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._simulate_step_two_zone.GUARD_OFF.2fe6a11c.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._simulate_step_two_zone.GUARD_OFF.2fe6a11c.json
new file mode 100644
index 000000000..d15e0ca88
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._simulate_step_two_zone.GUARD_OFF.2fe6a11c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalModel._simulate_step_two_zone GUARD_OFF 2fe6a11c",
+  "killed_by": "tests/features.py",
+  "old": "        if throttled and buffer_exo_kw:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.dhw_hold_hours.CLAMP_DROP.24cf749e.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.dhw_hold_hours.CLAMP_DROP.24cf749e.json
new file mode 100644
index 000000000..36e0d471a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.dhw_hold_hours.CLAMP_DROP.24cf749e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalModel.dhw_hold_hours CLAMP_DROP 24cf749e",
+  "killed_by": "tests/features.py",
+  "old": "        top = max(store.charge_max_temp, floor + 1.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`top = (store.charge_max_temp)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.simulate_dhw_step.CLAMP_DROP.6d5b3ca5.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.simulate_dhw_step.CLAMP_DROP.6d5b3ca5.json
deleted file mode 100644
index 97b244bfd..000000000
--- a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.simulate_dhw_step.CLAMP_DROP.6d5b3ca5.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalModel.simulate_dhw_step CLAMP_DROP 6d5b3ca5",
-  "killed_by": "tests/features.py",
-  "old": "        floor = min(p.dhw_inlet_reference, ambient_temp)",
-  "reason": "arrived with origin/main, commit 7eeea4d90 (D2-02: clamp the DHW inlet floor to the tank surroundings). Dropping the `min` clamp raises the driver's `FAILED` count to 2 against a 0 baseline. Measured at the post-main head, 2026-09-22, and re-pinned 1894 -> 1897 by PR #1488, whose D2-01 fix adds three comment lines above this site."
-}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.simulate_trajectory_batch.BOOLOP.89cf64f9.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.simulate_trajectory_batch.BOOLOP.89cf64f9.json
new file mode 100644
index 000000000..858a3cbff
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.simulate_trajectory_batch.BOOLOP.89cf64f9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalModel.simulate_trajectory_batch BOOLOP 89cf64f9",
+  "killed_by": "tests/features.py",
+  "old": "                    if throttled and exo_i:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if throttled or exo_i:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.simulate_trajectory_batch.GUARD_OFF.89cf64f9.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.simulate_trajectory_batch.GUARD_OFF.89cf64f9.json
new file mode 100644
index 000000000..f54f70f77
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.simulate_trajectory_batch.GUARD_OFF.89cf64f9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalModel.simulate_trajectory_batch GUARD_OFF 89cf64f9",
+  "killed_by": "tests/features.py",
+  "old": "                    if throttled and exo_i:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.simulate_trajectory_with_dhw.GUARD_OFF.d84dbbe9.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.simulate_trajectory_with_dhw.GUARD_OFF.d84dbbe9.json
new file mode 100644
index 000000000..544847d09
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.simulate_trajectory_with_dhw.GUARD_OFF.d84dbbe9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalModel.simulate_trajectory_with_dhw GUARD_OFF d84dbbe9",
+  "killed_by": "tests/features.py",
+  "old": "            if store is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.buffer_store_volume.GUARD_OFF.5946724e.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.buffer_store_volume.GUARD_OFF.5946724e.json
new file mode 100644
index 000000000..0acfe8bfb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.buffer_store_volume.GUARD_OFF.5946724e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalParameters.buffer_store_volume GUARD_OFF 5946724e",
+  "killed_by": "tests/features.py",
+  "old": "        if self.combi_tank_active:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.buffer_store_volume.RETURN_DEL.9314a0a4.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.buffer_store_volume.RETURN_DEL.9314a0a4.json
new file mode 100644
index 000000000..2cb01a718
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.buffer_store_volume.RETURN_DEL.9314a0a4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalParameters.buffer_store_volume RETURN_DEL 9314a0a4",
+  "killed_by": "tests/features.py",
+  "old": "        return self.buffer_tank_volume",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.buffer_tank_thermal_mass.RETURN_DEL.c22e3681.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.buffer_tank_thermal_mass.RETURN_DEL.c22e3681.json
deleted file mode 100644
index 866161160..000000000
--- a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.buffer_tank_thermal_mass.RETURN_DEL.c22e3681.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalParameters.buffer_tank_thermal_mass RETURN_DEL c22e3681",
-  "killed_by": "tests/features.py",
-  "old": "        return self.buffer_tank_volume * WATER_SPECIFIC_HEAT",
-  "reason": "Recorded by `mutation_table.py --drain` against 9061fbd3d710d5894b7083d8a58b8203f9e7aa97: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
-}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.buffer_tank_thermal_mass.RETURN_DEL.da341731.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.buffer_tank_thermal_mass.RETURN_DEL.da341731.json
new file mode 100644
index 000000000..de0cfcb85
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.buffer_tank_thermal_mass.RETURN_DEL.da341731.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalParameters.buffer_tank_thermal_mass RETURN_DEL da341731",
+  "killed_by": "tests/features.py",
+  "old": "        return self.buffer_store_volume * WATER_SPECIFIC_HEAT",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.dhw_store.RETURN_DEL.c401cdfe.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.dhw_store.RETURN_DEL.c401cdfe.json
new file mode 100644
index 000000000..0775f7d89
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.dhw_store.RETURN_DEL.c401cdfe.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalParameters.dhw_store RETURN_DEL c401cdfe",
+  "killed_by": "tests/guard_pins.py",
+  "old": "        return dhw_store_of(self)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/combi_space_net_kw.CLAMP_DROP.b47686bf.json b/tests/mutation_ledger/killed_by/thermal_model.py/combi_space_net_kw.CLAMP_DROP.b47686bf.json
new file mode 100644
index 000000000..f4f6e2f96
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/combi_space_net_kw.CLAMP_DROP.b47686bf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:combi_space_net_kw CLAMP_DROP b47686bf",
+  "killed_by": "tests/features.py",
+  "old": "    gained = store.capacity_kwh_per_c * np.diff(temps) / max(dt_hours, 1e-6)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`gained = store.capacity_kwh_per_c * np.diff(temps) / (dt_hours)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/combi_space_net_kw.RETURN_DEL.ed3f9304.json b/tests/mutation_ledger/killed_by/thermal_model.py/combi_space_net_kw.RETURN_DEL.ed3f9304.json
new file mode 100644
index 000000000..4b3115561
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/combi_space_net_kw.RETURN_DEL.ed3f9304.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:combi_space_net_kw RETURN_DEL ed3f9304",
+  "killed_by": "tests/features.py",
+  "old": "    return gained + loss - np.asarray(dhw_net_kw, dtype=float)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/combi_store_of.GUARD_OFF.f195744f.json b/tests/mutation_ledger/killed_by/thermal_model.py/combi_store_of.GUARD_OFF.f195744f.json
new file mode 100644
index 000000000..a29b2c015
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/combi_store_of.GUARD_OFF.f195744f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:combi_store_of GUARD_OFF f195744f",
+  "killed_by": "tests/features.py",
+  "old": "    if not p.combi_tank_active:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=24."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/combi_store_of.RETURN_DEL.8b8f9e7e.json b/tests/mutation_ledger/killed_by/thermal_model.py/combi_store_of.RETURN_DEL.8b8f9e7e.json
new file mode 100644
index 000000000..49b05e2f6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/combi_store_of.RETURN_DEL.8b8f9e7e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:combi_store_of RETURN_DEL 8b8f9e7e",
+  "killed_by": "tests/features.py",
+  "old": "    return dhw_store_of(p)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/dhw_charge_kw.RETURN_DEL.57a921d7.json b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_charge_kw.RETURN_DEL.57a921d7.json
new file mode 100644
index 000000000..61d4f9897
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_charge_kw.RETURN_DEL.57a921d7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_charge_kw RETURN_DEL 57a921d7",
+  "killed_by": "tests/features.py",
+  "old": "    return float(cop * heat_per_cop_kw(model.params, dhw_power_kw))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/dhw_mixed_litres.CLAMP_DROP.36b456aa.json b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_mixed_litres.CLAMP_DROP.36b456aa.json
new file mode 100644
index 000000000..f25f2099b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_mixed_litres.CLAMP_DROP.36b456aa.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_mixed_litres CLAMP_DROP 36b456aa",
+  "killed_by": "tests/features.py",
+  "old": "        return p.dhw_tank_volume * max(0.0, tank_c - store.inlet_c) / (mixed_c - store.inlet_c)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return p.dhw_tank_volume * (0.0) / (mixed_c - store.inlet_c)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/dhw_mixed_litres.CLAMP_DROP.a416a8fd.json b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_mixed_litres.CLAMP_DROP.a416a8fd.json
new file mode 100644
index 000000000..95dbaaa6c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_mixed_litres.CLAMP_DROP.a416a8fd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_mixed_litres CLAMP_DROP a416a8fd",
+  "killed_by": "tests/features.py",
+  "old": "    usable_kwh = store.capacity_kwh_per_c * max(0.0, tank_c - store.store_temp_for_tap(mixed_c))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`usable_kwh = store.capacity_kwh_per_c * (0.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/dhw_mixed_litres.GUARD_OFF.f078337e.json b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_mixed_litres.GUARD_OFF.f078337e.json
new file mode 100644
index 000000000..bdd598bd6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_mixed_litres.GUARD_OFF.f078337e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_mixed_litres GUARD_OFF f078337e",
+  "killed_by": "tests/features.py",
+  "old": "    if not store.combi:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/dhw_mixed_litres.RETURN_DEL.700dd13c.json b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_mixed_litres.RETURN_DEL.700dd13c.json
new file mode 100644
index 000000000..f6dc53264
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_mixed_litres.RETURN_DEL.700dd13c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_mixed_litres RETURN_DEL 700dd13c",
+  "killed_by": "tests/features.py",
+  "old": "    return usable_kwh / (WATER_SPECIFIC_HEAT * (mixed_c - store.inlet_c))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/dhw_store_of.CLAMP_DROP.15ca99bb.json b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_store_of.CLAMP_DROP.15ca99bb.json
new file mode 100644
index 000000000..54b150a91
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_store_of.CLAMP_DROP.15ca99bb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_store_of CLAMP_DROP 15ca99bb",
+  "killed_by": "tests/features.py",
+  "old": "        p.buffer_store_volume, min(p.dhw_max_temp, p.buffer_max_temp),",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`p.buffer_store_volume, (p.dhw_max_temp),`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/dhw_store_of.CLAMP_DROP.48a1fc65.json b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_store_of.CLAMP_DROP.48a1fc65.json
new file mode 100644
index 000000000..bd63ef2eb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_store_of.CLAMP_DROP.48a1fc65.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_store_of CLAMP_DROP 48a1fc65",
+  "killed_by": "tests/features.py",
+  "old": "    eps = min(1.0, eps) if eps >= COMBI_DHW_EFFECTIVENESS_FLOOR else COMBI_DHW_EFFECTIVENESS_FLOOR",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`eps = (1.0) if eps >= COMBI_DHW_EFFECTIVENESS_FLOOR else COMBI_DHW_EFFECTIVENESS_FLOOR`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/dhw_store_of.CLAMP_DROP.7e6f8a91.json b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_store_of.CLAMP_DROP.7e6f8a91.json
new file mode 100644
index 000000000..fdea895c6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_store_of.CLAMP_DROP.7e6f8a91.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_store_of CLAMP_DROP 7e6f8a91",
+  "killed_by": "tests/features.py",
+  "old": "        min(p.dhw_hard_max_temp, p.buffer_max_temp), eps,",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`(p.dhw_hard_max_temp), eps,`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/dhw_store_of.GUARD_OFF.f195744f.json b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_store_of.GUARD_OFF.f195744f.json
new file mode 100644
index 000000000..5c4e5ad58
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_store_of.GUARD_OFF.f195744f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_store_of GUARD_OFF f195744f",
+  "killed_by": "tests/features.py",
+  "old": "    if not p.combi_tank_active:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=88."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/store_step.CLAMP_DROP.c2b1e48b.json b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.CLAMP_DROP.c2b1e48b.json
new file mode 100644
index 000000000..755ac5b0a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.CLAMP_DROP.c2b1e48b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:store_step CLAMP_DROP c2b1e48b",
+  "killed_by": "tests/features.py",
+  "old": "        injected, new_temp = (floor - new_temp) * capacity / max(dt_hours, 1e-6), floor",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`injected, new_temp = (floor - new_temp) * capacity / (dt_hours), floor`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/store_step.CLAMP_DROP.dc05794e.json b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.CLAMP_DROP.dc05794e.json
new file mode 100644
index 000000000..121631d8f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.CLAMP_DROP.dc05794e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:store_step CLAMP_DROP dc05794e",
+  "killed_by": "tests/features.py",
+  "old": "    floor = min(store.inlet_c, ambient_temp)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`floor = (store.inlet_c)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/store_step.CLAMP_DROP.e56c36b8.json b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.CLAMP_DROP.e56c36b8.json
new file mode 100644
index 000000000..e905d8af6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.CLAMP_DROP.e56c36b8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:store_step CLAMP_DROP e56c36b8",
+  "killed_by": "tests/features.py",
+  "old": "    cap = max(0.0, store.rating_max_temp - temp) / max(dt_hours, 1e-6)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`cap = (0.0) / max(dt_hours, 1e-6)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=43. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/store_step.CMP_BOUND.7b7f231d.json b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.CMP_BOUND.7b7f231d.json
new file mode 100644
index 000000000..427389393
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.CMP_BOUND.7b7f231d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:store_step CMP_BOUND 7b7f231d",
+  "killed_by": "tests/features.py",
+  "old": "    if capacity <= 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if capacity < 0.0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/store_step.GUARD_OFF.09c88e0c.json b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.GUARD_OFF.09c88e0c.json
new file mode 100644
index 000000000..1b3a08c3d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.GUARD_OFF.09c88e0c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:store_step GUARD_OFF 09c88e0c",
+  "killed_by": "tests/features.py",
+  "old": "    if new_temp < floor:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/store_step.GUARD_OFF.7b7f231d.json b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.GUARD_OFF.7b7f231d.json
new file mode 100644
index 000000000..231636e65
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.GUARD_OFF.7b7f231d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:store_step GUARD_OFF 7b7f231d",
+  "killed_by": "tests/features.py",
+  "old": "    if capacity <= 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/store_step.GUARD_OFF.955429e2.json b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.GUARD_OFF.955429e2.json
new file mode 100644
index 000000000..7adc56af4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.GUARD_OFF.955429e2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:store_step GUARD_OFF 955429e2",
+  "killed_by": "tests/features.py",
+  "old": "    if d_temp > cap:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/store_step.RETURN_DEL.ceab1f1e.json b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.RETURN_DEL.ceab1f1e.json
new file mode 100644
index 000000000..dbfea5ddf
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/store_step.RETURN_DEL.ceab1f1e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:store_step RETURN_DEL ceab1f1e",
+  "killed_by": "tests/features.py",
+  "old": "    return new_temp, refused, injected, draw",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._dhw_legionella_ceilings.CLAMP_DROP.725a61cf.json b/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._dhw_legionella_ceilings.CLAMP_DROP.725a61cf.json
new file mode 100644
index 000000000..c48717940
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._dhw_legionella_ceilings.CLAMP_DROP.725a61cf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._dhw_legionella_ceilings CLAMP_DROP 725a61cf",
+  "old": "        max_temp = np.full(max(n_steps, 0), float(store.charge_max_temp))",
+  "reason": "Equivalent on every reachable input (CLAMP_DROP, `max(n_steps, 0)` -> `(n_steps)`): the two differ only for a negative `n_steps`, where `np.full` raises and the head returns an empty array, and no horizon carries one. `_dhw_legionella_ceilings` reads `h.n_steps`, which `HeatPumpOptimizer.optimize` sets to `min(len(prices), len(outdoor_temps), self.config.n_steps)`, two lengths and `OptimizationConfig.n_steps`'s `int(horizon_hours * 60 / time_step_minutes)` over a positive horizon; the other `_Horizon` builders carry a series length. The line beside it, `runup_temps = np.zeros(max(n_steps, 0))`, is the same idiom and unpinned at the merge base. Survival measured by the R10-COMBI-TANK repair fixer's mutant_run.py drive against tests/features.py's R10-COMBI-TANK blocks, and named unpinned by tests / mutation (job 128944437769) at 74df96f1, the mutation-autofix pin drive's own commit, so no driver of that drive killed it.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/thermal_model.py/dhw_store_of.CMP_BOUND.48a1fc65.json b/tests/mutation_ledger/survivor_triage/thermal_model.py/dhw_store_of.CMP_BOUND.48a1fc65.json
new file mode 100644
index 000000000..ea8751eca
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/thermal_model.py/dhw_store_of.CMP_BOUND.48a1fc65.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_store_of CMP_BOUND 48a1fc65",
+  "old": "    eps = min(1.0, eps) if eps >= COMBI_DHW_EFFECTIVENESS_FLOOR else COMBI_DHW_EFFECTIVENESS_FLOOR",
+  "reason": "Equivalent (CMP_BOUND, `eps >=` -> `eps >` COMBI_DHW_EFFECTIVENESS_FLOOR): the arms differ only at eps == the floor, where the head's `min(1.0, eps)` and the mutant's else arm are both the floor (0.1, below the 1.0 cap); NaN fails both comparisons alike. Measured by ``: the operator's own text compiled over `dhw_store_of`, against the head, over 11 effectiveness values holding the tie, NaN, inf and both of the floor's float neighbours: equiv_eps_differ=0. The tie-only control (`(min(1.0, eps) if eps != FLOOR else 0.5)` in the first arm) differs on the 1 tie and on 0 of the 10 others, so the grid reaches the tie.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/thermal_model.py/store_step.CMP_BOUND.09c88e0c.json b/tests/mutation_ledger/survivor_triage/thermal_model.py/store_step.CMP_BOUND.09c88e0c.json
new file mode 100644
index 000000000..162ce4c63
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/thermal_model.py/store_step.CMP_BOUND.09c88e0c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:store_step CMP_BOUND 09c88e0c",
+  "old": "    if new_temp < floor:",
+  "reason": "Equivalent (CMP_BOUND, `new_temp < floor` -> `new_temp <= floor`): the arms differ only at new_temp == floor, where the mutant's branch books `(floor - new_temp) * capacity / max(dt_hours, 1e-6)` = 0.0 injected and sets new_temp to the floor it already equals, so `store_step` returns the head's tuple bitwise. Measured by `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_combi_tank.py equiv`: the operator's own text compiled over `store_step`, against the head, over 56 steps of which 3 land exactly on the floor (C = 1, no loss or draw, ambient 8 below the inlet, an exact binary heat over dt): equiv_floor_differ=0. The tie-only control (`if new_temp == floor: injected += 1.0` ahead of the floor branch) differs on all 3 ties and 0 of the 53 others. `mutation_table.py --pin-killed` at this site cut tests/features.py's run as an exclusive tail (skip-budget-tail), so no driver verdict was read; the equivalence is the disposition.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/thermal_model.py/store_step.CMP_BOUND.955429e2.json b/tests/mutation_ledger/survivor_triage/thermal_model.py/store_step.CMP_BOUND.955429e2.json
new file mode 100644
index 000000000..7bee199e6
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/thermal_model.py/store_step.CMP_BOUND.955429e2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:store_step CMP_BOUND 955429e2",
+  "old": "    if d_temp > cap:",
+  "reason": "Equivalent (CMP_BOUND, `d_temp > cap` -> `d_temp >= cap`): the arms differ only at d_temp == cap, where the mutant's branch books `(d_temp - cap) * capacity` = 0.0 refused and sets d_temp to cap, which it already is, so `store_step` returns the head's tuple bitwise. Measured by ``: the operator's own text compiled over `store_step`, against the head, over 53 steps of which 3 are exact ties (C = 1, no loss or draw, the rating's distance over dt an exact binary fraction): equiv_step_differ=0. The tie-only control (`if d_temp == cap: refused += 1.0` ahead of the clamp) differs on all 3 ties and 0 of the 50 others.",
+  "verdict": "equivalent"
+}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 0c48efaa2..5a61d5cf7 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17558,
+ "class_excess_loc": 17546,
  "const_modules_over_50": 3,
  "coordinator_attrs": 141,
  "coordinator_multiassigned_attrs": 108,
@@ -11,11 +11,11 @@
  "functions_cc_over_25": 8,
  "import_cycle_modules": 0,
  "max_cc": 44,
- "max_class_loc": 7933,
+ "max_class_loc": 7931,
  "max_method_loc": 373,
  "methods_over_150": 15,
  "methods_over_200": 8,
  "name_kept_members": 38,
- "recorded_at": "dee8b413fd7da7b07f13e28a93d7d49b4a9e978a",
+ "recorded_at": "17e621f08c4feec724478573741fbd8b596ceaba",
  "seam_cut_total": 423
 }

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
