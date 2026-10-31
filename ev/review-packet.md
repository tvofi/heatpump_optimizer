# Review packet #3006
head: a6be5baa55e41507a7dec1ffec7b88a660167e15
base: 2fc0e95b2f3ccfedc03975a801f0960fbc9bbc84

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=124531405741 neutral
arch-score / arch-score id=124531257077 success
arm id=124531191863 skipped
budget-raise-gate / budget-raise-gate id=124531257194 failure
cancel-superseded id=124531195779 success
codeql / Analyze (actions) id=124531257002 success
codeql / Analyze (javascript-typescript) id=124531256967 success
codeql / Analyze (python) id=124531256995 in_progress
governance / delivery-status id=124531257085 success
governance / delivery-status-publish id=124531258176 skipped
governance / env-matrix id=124531257053 success
governance / instrument-self-tests id=124531257042 in_progress
governance / policy-docs id=124531257062 success
governance / record id=124531258058 skipped
governance / wave-script id=124531257215 success
hassfest / hassfest id=124531256997 success
kernel-points id=124531258079 skipped
prelude id=124531195922 success
refresh id=124531195909 success
tests / arch-instrument id=124531352342 success
tests / briefs id=124531256980 success
tests / browser id=124531352375 success
tests / closure-scope id=124531257074 success
tests / closures id=124531352354 in_progress
tests / coverage id=124531352334 in_progress
tests / fast (3.14) id=124531352316 in_progress
tests / mutation id=124531257007 in_progress
tests / nightly-ha id=124531353735 skipped
tests / nightly-status id=124531257301 success
tests / replay id=124531352353 success
tests / typing id=124531352407 success
validate / validate-hacs id=124531257060 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 997fbfae: R10-COP-PARTLOAD
NOTE body item a92218a5: R10-COP-PARTLOAD
NOTE body item 71a9ea2b: R10-COP-PARTLOAD
NOTE body item cfb9f7e5: dismissed:a session-local plugin, not repository policy
NOTE body item 800abe4c: dismissed:a session-local hook, not repository policy
CARRY-AUDIT: 5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified - `battery.py:charge_rate_kw`: the factor is `charge_heat_per_cop_kw`, which is `heat_per_cop_kw`'s output.
             no segment of this names a program this check knows
  unverified - `thermal_model.py:extend_dhw_temps` (`cop * heat_per_cop[i]`) and `simulate_trajectory_batch` (`cop * heat_per_cop_i`, two hits) are already routed by #2872. The operand is `heat_per_cop_kw`'s output, hoisted once per schedule. That is lexically PLAIN, and routed in fact.
             no segment of this names a program this check knows
  unverified - `coordinator.py:machine_score`, `_observe_cop_health`, and `store.py:<module>` use COP-health constants.
             no segment of this names a program this check knows
  unverified - `coordinator.py:_fold_cop_evidence` (two hits) updates the learned `_cop_scale`.
             no segment of this names a program this check knows
  unverified - `thermal_model.py:_cop_law` (three hits) and `_batch_cop` (four hits) multiply COP factors together.
             no segment of this names a program this check knows
  unverified - `thermal_model.py:partload_factor` is `d * x`, the derate itself.
             no segment of this names a program this check knows
  unverified - `topology.py:outdoor_cop_miss_sek` (two hits) is the sensitivity of cost to a mis-set COP, not a plant conversion.
             no segment of this names a program this check knows
  unverified - `coordinator.py:_fold_capacity_envelope` and `flow_meter.py:cop_evidence` (three hits) read measured power at an observed COP, and the observed COP already contains the real part-load. This is the census's disposition.
             no segment of this names a program this check knows
  unverified - `optimizer.py:_compute_baseline_power`,
             no segment of this names a program this check knows
  unverified - `sysid.py:_held_state`,
             no segment of this names a program this check knows
  unverified - `thermal_model.py:_valve_ua`, `_valve_two_zone_delivery`, `flow_target_for_indoor`, `_substeps_and_loss` (two hits), `simulate_trajectory_batch` (two hits),
             no segment of this names a program this check knows
  unverified - and `heat_energy.py:observe_cycle`'s `max_heat_kw`.
             no segment of this names a program this check knows
  unverified Folding the derate in would count it twice against the UA it calibrates. This is the census's disposition.
             no segment of this names a program this check knows
  unverified - `coordinator.py:_max_pump_rise`.
             no segment of this names a program this check knows
  unverified - `heat_energy.py:span_heat`, the counter-resolution threshold.
             no segment of this names a program this check knows
  unverified - `sysid.py:_size_step_power` (four hits). The census's `sysid._size_step_power` bound, confirmed: the plain quotient sizes a step that delivers at most the `q` its excursion was judged at.
             no segment of this names a program this check knows
  unverified - `sysid.py:_begin_step_phase`, the adoption check on the same step.
             no segment of this names a program this check knows
  unverified - `sysid.py:_valve_drive`, `q / compute_cop`: `q` is the step's nominal heat at the plain law. The plant then prices every COP effect on the resulting draw: the flow lift, which its docstring names, and the part-load derate the same way. Inverting the derate there would exempt one of those effects from the plant.
             no segment of this names a program this check knows
  unverified - `modbus_prefill.py:_plant`, `capacity / cop`: a datasheet rating, whose COP is measured at that capacity and already contains the part-load.
             no segment of this names a program this check knows
  unverified - `dhw_planner.py:_plan_dhw_min_cost`'s displacement row `1.0 / (cop * dt)`: a no-op for every input, argued under Alternatives.
             no segment of this names a program this check knows
  unverified - `dhw_planner.py:_plan_dhw_min_cost` objective, `prices / cop`;
             no segment of this names a program this check knows
  unverified - `optimizer.py:row_cost` (three hits);
             no segment of this names a program this check knows
  unverified - `optimizer.py:_deferred_energy_cost` (three hits);
             no segment of this names a program this check knows
  unverified - `wood_fuel.py:cheaper_hour_count` and `_scan_wood_night`.
             no segment of this names a program this check knows
  ok         python3 dev/audit/harnesses/r10_cop_conversions.py
             `dev/audit/harnesses/r10_cop_conversions.py` is in the tree at this head
  unverified git grep -nE '/ *\(?[A-Za-z_.]*cop' -- 'custom_components/*.py'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/optimality.py
             `tests/optimality.py` is in the tree at this head
  ok         tests/card.mjs
             `tests/card.mjs` is in the tree at this head
  ok         tests/stress.py
             `tests/stress.py` is in the tree at this head
  ok         python3 tests/structure.py --record
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff cf4f6b7a660f5b61e0f2b933bd18647fe3ba90c7 HEAD
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         node tools/policy/rules_sync.mjs --check
             `tools/policy/rules_sync.mjs` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 -u dev/audit/harnesses/r10_cop_partload.py
             `dev/audit/harnesses/r10_cop_partload.py` is in the tree at this head

FIGURES: 14 resolved, 25 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/battery.py/VirtualBattery.charge_rate_kw.RETURN_DEL.b403cdd2.json b/tests/mutation_ledger/killed_by/battery.py/VirtualBattery.charge_rate_kw.RETURN_DEL.b403cdd2.json
new file mode 100644
index 000000000..d43fbc164
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/battery.py/VirtualBattery.charge_rate_kw.RETURN_DEL.b403cdd2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/battery.py:VirtualBattery.charge_rate_kw RETURN_DEL b403cdd2",
+  "killed_by": "tests/features.py",
+  "old": "        return max(self.cop, 0.1) * self.charge_heat_per_cop_kw",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.BOOLOP.a5d8d969.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.BOOLOP.a5d8d969.json
deleted file mode 100644
index 2b6dc5af4..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.BOOLOP.a5d8d969.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._capacity_caps BOOLOP a5d8d969",
-  "killed_by": "tests/features.py",
-  "old": "            has_hum = humidity is not None and i < len(humidity)",
-  "reason": "R8-P3 round 2 (fix review): the capacity envelope's per-step humidity. `and` -> `or` evaluates `len(None)` on every call without a forecast, so tests/features.py dies with `TypeError: object of type 'NoneType' has no len()` at the #17 envelope checks (`_capacity_caps(np.array([-10.0, -10.0, 15.0]))`), measured in a git-less copy of ef45f9ce's production. A crash, not a counted FAIL line: the kill is the uncaught error on the only path every install without a humidity forecast takes."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.BOOLOP.f3835ba8.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.BOOLOP.f3835ba8.json
new file mode 100644
index 000000000..b904337f0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.BOOLOP.f3835ba8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._capacity_caps BOOLOP f3835ba8",
+  "killed_by": "tests/features.py",
+  "old": "            hum = float(humidity[i]) if humidity is not None and i < len(humidity) else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`hum = float(humidity[i]) if humidity is not None or i < len(humidity) else None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CLAMP_DROP.8a6fab44.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CLAMP_DROP.8a6fab44.json
new file mode 100644
index 000000000..a913f9e42
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CLAMP_DROP.8a6fab44.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._capacity_caps CLAMP_DROP 8a6fab44",
+  "killed_by": "tests/features.py",
+  "old": "            cap_i = float(np.clip(power_for_heat_per_cop_kw(model.params, float(entry[0]) / cop_i), floor, p_max))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`cap_i = float((power_for_heat_per_cop_kw(model.params, float(entry[0]) / cop_i)))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CMP_BOUND.a5d8d969.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CMP_BOUND.a5d8d969.json
deleted file mode 100644
index 23fe60e39..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CMP_BOUND.a5d8d969.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._capacity_caps CMP_BOUND a5d8d969",
-  "killed_by": "tests/features.py",
-  "old": "            has_hum = humidity is not None and i < len(humidity)",
-  "reason": "Recorded by `mutation_table.py --drain`: CMP_BOUND (`has_hum = humidity is not None and i <= len(humidity)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CMP_BOUND.f3835ba8.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CMP_BOUND.f3835ba8.json
new file mode 100644
index 000000000..e8771f19c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CMP_BOUND.f3835ba8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._capacity_caps CMP_BOUND f3835ba8",
+  "killed_by": "tests/features.py",
+  "old": "            hum = float(humidity[i]) if humidity is not None and i < len(humidity) else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`hum = float(humidity[i]) if humidity is not None and i <= len(humidity) else None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.CLAMP_DROP.2bd515d1.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.CLAMP_DROP.2bd515d1.json
deleted file mode 100644
index c19a2cffd..000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.CLAMP_DROP.2bd515d1.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._compute_baseline_power CLAMP_DROP 2bd515d1",
-  "killed_by": "tests/features.py",
-  "old": "            power = min(required_thermal / cop, p.max_electrical_power)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 5c0ee109305fc4f377c9326c712156b9ceb0e638: CLAMP_DROP (`power = (required_thermal / cop)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.CLAMP_DROP.67fa09c5.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.CLAMP_DROP.67fa09c5.json
new file mode 100644
index 000000000..4439bdeb9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.CLAMP_DROP.67fa09c5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._compute_baseline_power CLAMP_DROP 67fa09c5",
+  "killed_by": "tests/features.py",
+  "old": "            power = min(power_for_heat_per_cop_kw(p, required_thermal / cop), p.max_electrical_power)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`power = (power_for_heat_per_cop_kw(p, required_thermal / cop))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/added_power_for_heat_per_cop_kw.GUARD_OFF.f57dc5dd.json b/tests/mutation_ledger/killed_by/thermal_model.py/added_power_for_heat_per_cop_kw.GUARD_OFF.f57dc5dd.json
new file mode 100644
index 000000000..175e04fe5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/added_power_for_heat_per_cop_kw.GUARD_OFF.f57dc5dd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:added_power_for_heat_per_cop_kw GUARD_OFF f57dc5dd",
+  "killed_by": "tests/features.py",
+  "old": "    if not params.cop_partload_derate:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.CLAMP_DROP.0d030b71.json b/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.CLAMP_DROP.0d030b71.json
new file mode 100644
index 000000000..54c47ecbd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.CLAMP_DROP.0d030b71.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:power_for_heat_per_cop_kw CLAMP_DROP 0d030b71",
+  "killed_by": "tests/features.py",
+  "old": "    on_band = 2.0 * h / (b + np.sqrt(np.maximum(b * b - 4.0 * a * h, 0.0)))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`on_band = 2.0 * h / (b + np.sqrt((b * b - 4.0 * a * h)))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.CMP_BOUND.7f1dd302.json b/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.CMP_BOUND.7f1dd302.json
new file mode 100644
index 000000000..22c373220
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.CMP_BOUND.7f1dd302.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:power_for_heat_per_cop_kw CMP_BOUND 7f1dd302",
+  "killed_by": "tests/features.py",
+  "old": "    if not d or band <= 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if not d or band < 0.0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.CMP_BOUND.e7058406.json b/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.CMP_BOUND.e7058406.json
new file mode 100644
index 000000000..acbd35802
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.CMP_BOUND.e7058406.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:power_for_heat_per_cop_kw CMP_BOUND e7058406",
+  "killed_by": "tests/features.py",
+  "old": "    power = np.where(h <= p_min, h, np.where(held >= p_max, held, on_band))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`power = np.where(h < p_min, h, np.where(held >= p_max, held, on_band))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.GUARD_OFF.7f1dd302.json b/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.GUARD_OFF.7f1dd302.json
new file mode 100644
index 000000000..6971de5bb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.GUARD_OFF.7f1dd302.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:power_for_heat_per_cop_kw GUARD_OFF 7f1dd302",
+  "killed_by": "tests/features.py",
+  "old": "    if not d or band <= 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.RETURN_DEL.bc569d66.json b/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.RETURN_DEL.bc569d66.json
new file mode 100644
index 000000000..c031be3bf
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.RETURN_DEL.bc569d66.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:power_for_heat_per_cop_kw RETURN_DEL bc569d66",
+  "killed_by": "tests/features.py",
+  "old": "    return float(power) if np.ndim(heat_per_cop) == 0 else power",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/survivor_triage/battery.py/VirtualBattery.charge_rate_kw.CLAMP_DROP.b403cdd2.json b/tests/mutation_ledger/survivor_triage/battery.py/VirtualBattery.charge_rate_kw.CLAMP_DROP.b403cdd2.json
new file mode 100644
index 000000000..55defcb64
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/battery.py/VirtualBattery.charge_rate_kw.CLAMP_DROP.b403cdd2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/battery.py:VirtualBattery.charge_rate_kw CLAMP_DROP b403cdd2",
+  "old": "        return max(self.cop, 0.1) * self.charge_heat_per_cop_kw",
+  "reason": "R10-COP-PARTLOAD p2 round 2 re-anchored this line (the factor became `charge_heat_per_cop_kw`); the clamp is the old line's. `battery.build`'s only caller (`coordinator.py`, the battery view) passes `cop` from `ThermalModel.compute_cop`, which returns `_cop_law`'s `max(cop, 1.0)` (#928's resistive bound), so `max(cop, 0.1)` cannot select its second arm.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CLAMP_DROP.33200ef3.json b/tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CLAMP_DROP.33200ef3.json
deleted file mode 100644
index f5c25bed9..000000000
--- a/tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CLAMP_DROP.33200ef3.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._capacity_caps CLAMP_DROP 33200ef3",
-  "old": "            cop_i = max((model or self._thermal_model).compute_cop(float(outdoor), humidity=hum), 1e-6)",
-  "reason": "R8-P3 round 2 re-anchored this line (it gained the humidity argument); it was unpinned at the merge base under its old text. `max(compute_cop(...), 1e-6)` cannot select the second arm: `compute_cop` returns `_cop_law`, which returns `max(cop, 1.0)` (#928's resistive bound). Re-keyed by #1736, which judges the caps on the solve's own model (`model or self._thermal_model`): every ThermalModel's `compute_cop` is the same `_cop_law`, so the second arm is still unreachable.",
-  "verdict": "equivalent"
-}
diff --git a/tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CLAMP_DROP.b267b48b.json b/tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CLAMP_DROP.b267b48b.json
new file mode 100644
index 000000000..d5657511e
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CLAMP_DROP.b267b48b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._capacity_caps CLAMP_DROP b267b48b",
+  "old": "            cop_i = max(model.compute_cop(float(outdoor), humidity=hum), 1e-6)",
+  "reason": "Re-keyed from 33200ef3 by R10-COP-PARTLOAD p2 round 2 (`model = model or self._thermal_model` hoisted above the loop). `max(compute_cop(...), 1e-6)` cannot select the second arm: `compute_cop` returns `_cop_law`, which returns `max(cop, 1.0)` (#928's resistive bound), on every ThermalModel.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._dhw_setpoint_sweep.CLAMP_DROP.67c35b2c.json b/tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._dhw_setpoint_sweep.CLAMP_DROP.67c35b2c.json
new file mode 100644
index 000000000..73476e903
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._dhw_setpoint_sweep.CLAMP_DROP.67c35b2c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._dhw_setpoint_sweep CLAMP_DROP 67c35b2c",
+  "old": "            cop = max(float(self._thermal_model.compute_cop_dhw(outdoor, t)), 0.5)",
+  "reason": "Equivalent: `cop` is `compute_cop_dhw`, which returns `ThermalModel._cop_law`, whose last line is `return max(cop, 1.0)`; the 0.5 floor can never bind on a finite COP, and on a NaN one `max(nan, 0.5)` is the NaN either way. The line's text changed only because R10-COP-PARTLOAD part 2 joined its wrapped call onto one line; the clamp itself is the base's.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._plan_dhw_min_cost.CLAMP_DROP.957b7a47.json b/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._plan_dhw_min_cost.CLAMP_DROP.957b7a47.json
new file mode 100644
index 000000000..25e2ea96d
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._plan_dhw_min_cost.CLAMP_DROP.957b7a47.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._plan_dhw_min_cost CLAMP_DROP 957b7a47",
+  "old": "            energy_max = np.maximum(cop * heat_per_cop_kw(params, p_dhw_max) * dt, 1e-9)",
+  "reason": "Equivalent in output: the 1e-9 floor differs from no floor only where `cop * heat_per_cop_kw(params, p_dhw_max) * dt` is 0, i.e. `p_dhw_max == 0` (COP is at least 1 and dt positive). There the LP may place up to 1e-9 kWh, and the back-conversion clips every step to [0, p_dhw_max] = 0, so the plan, and the refine pass's simulation of it, are the same array. The floor is the base's; R10-COP-PARTLOAD part 2 changed only its product's first factor.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._repair_dhw_floor.CLAMP_DROP.19b8216c.json b/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._repair_dhw_floor.CLAMP_DROP.19b8216c.json
new file mode 100644
index 000000000..f4b3b5308
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._repair_dhw_floor.CLAMP_DROP.19b8216c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._repair_dhw_floor CLAMP_DROP 19b8216c",
+  "old": "                    params, plan[j], float(room_c[j_local]) * c_dhw / max(dt * cop_room, 1e-6))",
+  "reason": "Re-keyed from 21bb873a by R10-COP-PARTLOAD p2 round 2 (the quotient became `added_power_for_heat_per_cop_kw`'s argument). `cop_room = max(cop_j, compute_cop_dhw(...))` and `cop_j = max(marginal_cop(...), 0.5)`, so `dt * cop_room >= 0.5 * dt`, which exceeds 1e-6 for any step longer than 2e-6 h; the planner's step is 0.25 h. The max cannot select its second arm.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._repair_dhw_floor.CLAMP_DROP.21bb873a.json b/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._repair_dhw_floor.CLAMP_DROP.21bb873a.json
deleted file mode 100644
index cf32cc621..000000000
--- a/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._repair_dhw_floor.CLAMP_DROP.21bb873a.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._repair_dhw_floor CLAMP_DROP 21bb873a",
-  "old": "                room_kw = float(room_c[j_local]) * c_dhw / max(dt * cop_room, 1e-6)",
-  "reason": "drawn by the round-7 D2-03 diff's per-file sample over optimizer.py. In `_repair_dhw_floor`, `cop_room = max(cop_j, compute_cop_dhw(...))` and `cop_j = max(marginal_cop(...), 0.5)`, so `dt * cop_room >= 0.5 * dt`, which exceeds 1e-6 for any step longer than 2e-6 h. The planner's step is `time_step_minutes / 60` = 0.25 h. The max cannot select its second arm.",
-  "verdict": "equivalent"
-}
diff --git a/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._repair_dhw_floor.CLAMP_DROP.eb4ca0bc.json b/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._repair_dhw_floor.CLAMP_DROP.eb4ca0bc.json
new file mode 100644
index 000000000..b2ca925f0
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._repair_dhw_floor.CLAMP_DROP.eb4ca0bc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._repair_dhw_floor CLAMP_DROP eb4ca0bc",
+  "old": "                    params, plan[j], float(deficit[b]) * c_dhw / max(dt * cop_j, 1e-6))",
+  "reason": "R10-COP-PARTLOAD p2 round 2 moved this quotient into `added_power_for_heat_per_cop_kw`'s argument. `cop_j = max(marginal_cop(...), 0.5)`, so `dt * cop_j >= 0.5 * dt`, which exceeds 1e-6 for any step longer than 2e-6 h; the planner's step is `time_step_minutes / 60` = 0.25 h. The max cannot select its second arm.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._tighten_buffer_caps.CLAMP_DROP.53178fd6.json b/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._tighten_buffer_caps.CLAMP_DROP.53178fd6.json
new file mode 100644
index 000000000..ba5634306
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._tighten_buffer_caps.CLAMP_DROP.53178fd6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._tighten_buffer_caps CLAMP_DROP 53178fd6",
+  "old": "                self.model.params, float(schedule[i]), -float(refused[i]) / max(cop_i, 1e-6))",
+  "reason": "R10-COP-PARTLOAD p2 round 2 moved this quotient into `added_power_for_heat_per_cop_kw`'s argument; the clamp is the old line's. `cop_i = marginal_cop(..., \"buffer\", ...)`, which is `compute_cop(..., flow_temp=...)`, which returns `_cop_law`'s `max(cop, 1.0)` (#928's resistive bound), so `max(cop_i, 1e-6)` cannot select its second arm.",
+  "verdict": "equivalent"
+}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/battery.py b/custom_components/heatpump_optimizer/battery.py
index 7de0ea626..516320016 100644
--- a/custom_components/heatpump_optimizer/battery.py
+++ b/custom_components/heatpump_optimizer/battery.py
@@ -31,6 +31,7 @@ from typing import Any
 
 from .const import WOOD_TANK_MAX_TEMP
 from .payload import Battery, BatteryComponent
+from .thermal_model import heat_per_cop_kw
 
 
 @dataclass
@@ -93,6 +94,9 @@ class VirtualBattery:
     charge_power_kw: float = 0.0
     #: COP at current conditions, needed to convert electrical to thermal.
     cop: float = 3.0
+    #: ``heat_per_cop_kw`` at ``charge_power_kw``: the draw itself, less the
+    #: part-load derate at that draw.
+    charge_heat_per_cop_kw: float = 0.0
 
     @property
     def stored_kwh(self) -> float:
@@ -112,7 +116,7 @@ class VirtualBattery:
     @property
     def charge_rate_kw(self) -> float:
         """Thermal charge rate: what the compressor can actually put in."""
-        return self.charge_power_kw * max(self.cop, 0.1)
+        return max(self.cop, 0.1) * self.charge_heat_per_cop_kw
 
     @property
     def discharge_rate_kw(self) -> float:
@@ -381,4 +385,5 @@ def build(
         components=components,
         charge_power_kw=params.max_electrical_power,
         cop=cop,
+        charge_heat_per_cop_kw=heat_per_cop_kw(params, params.max_electrical_power),
     )
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index b4b07c4ea..b3b1f4e1a 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -339,6 +339,7 @@ from .thermal_model import (
     planned_draw_runs,
     probe_install,
     reanchor_heat_loss,
+    power_for_heat_per_cop_kw,
 )
 from .dhw_schedule import (
     DHWWindowError,
@@ -4075,10 +4076,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
                 * max(0.5 * (t + params.dhw_min_temp) - TANK_ROOM_AMBIENT_TEMP, 0.0)
                 * 24.0
             )
-            cop = max(
-                float(self._thermal_model.compute_cop_dhw(outdoor, t)), 0.5
-            )
-            cost_day = (standby_kwh + draw_day_kwh) / cop * mean_price
+            cop = max(float(self._thermal_model.compute_cop_dhw(outdoor, t)), 0.5)
+            cost_day = mean_price * power_for_heat_per_cop_kw(
+                params, (standby_kwh + draw_day_kwh) / cop, hours=24.0)
             # Can a tank at this setpoint cover the heaviest window from
             # its usable band at all?
             usable_kwh = c_dhw * max(t - params.dhw_min_temp, 0.0)
@@ -9068,14 +9068,14 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         floor = CAPACITY_FLOOR_FRACTION * p_max
         caps = np.full(len(outdoor_temps), p_max, dtype=float)
         any_cap = False
+        model = model or self._thermal_model
         for i, outdoor in enumerate(outdoor_temps):
             entry = self._capacity_envelope.get(int(np.floor(outdoor / 3.0)))
             if entry is None or int(entry[1]) < CAPACITY_MIN_SAMPLES:
                 continue
-            has_hum = humidity is not None and i < len(humidity)
-            hum = float(humidity[i]) if has_hum else None
-            cop_i = max((model or self._thermal_model).compute_cop(float(outdoor), humidity=hum), 1e-6)
-            cap_i = float(np.clip(float(entry[0]) / cop_i, floor, p_max))
+            hum = float(humidity[i]) if humidity is not None and i < len(humidity) else None
+            cop_i = max(model.compute_cop(float(outdoor), humidity=hum), 1e-6)
+            cap_i = float(np.clip(power_for_heat_per_cop_kw(model.params, float(entry[0]) / cop_i), floor, p_max))
             if cap_i < p_max - 1e-9:
                 caps[i] = cap_i
                 any_cap = True
diff --git a/custom_components/heatpump_optimizer/dhw_planner.py b/custom_components/heatpump_optimizer/dhw_planner.py
index 05b9c16ae..3ab8a43eb 100644
--- a/custom_components/heatpump_optimizer/dhw_planner.py
+++ b/custom_components/heatpump_optimizer/dhw_planner.py
@@ -48,6 +48,10 @@ from .thermal_model import (
     _step_humidity,
     dhw_coil_draw_reduction,
     dhw_draw_scale,
+    added_power_for_heat_per_cop_kw,
+    delivered_heat_kw,
+    heat_per_cop_kw,
+    power_for_heat_per_cop_kw,
 )
 
 _LOGGER = logging.getLogger(__name__)
@@ -387,7 +391,8 @@ class DhwPlanner:
                 # see dhw_coil_draw_reduction for why the two must agree.
                 inlet_temp=p.dhw_inlet_reference,
             )
-        baseline_dhw = np.full(n_steps, (baseline_draw + standby_loss) / cop_dhw)
+        baseline_dhw = np.full(
+            n_steps, power_for_heat_per_cop_kw(p, (baseline_draw + standby_loss) / cop_dhw))
         # All three figures are piecewise in the PV surplus, like the objective.
         # The baseline house would self-consume the same sun, so pricing only
         # the optimized plan that way would manufacture fictitious savings.
@@ -642,11 +647,8 @@ class DhwPlanner:
             # leave it at the charge limit when the ramp starts — and with
             # the limit honoured a summer plan legitimately parks the tank at
             # ~37 °C. The repair stage does find the ramp from the cycle's
-            # own requirement, so this is belt and braces rather than the
-            # only thing holding the cycle up; it is cheap, it is what the
-            # linear program needs to seed a sensible shape, and it states
-            # the obligation where the ramp is computed instead of leaving it
-            # to be rediscovered.
+            # own requirement; this is belt and braces, and the shape the
+            # linear program needs as its seed.
             need = boost_top
             for m in range(legionella_step - 1, -1, -1):
                 # The transition from the END of step m to the END of step
@@ -659,7 +661,7 @@ class DhwPlanner:
                     ),
                     0.5,
                 )
-                rise = p_dhw_run * cop * dt / c_dhw
+                rise = delivered_heat_kw(params, cop, p_dhw_run) * dt / c_dhw
                 drawn = float(draw_rates[nxt]) * dt / c_dhw
                 need = (need + drawn - gain - rise) / max(decay, 1e-6)
                 if need > boost_top:
@@ -1441,7 +1443,7 @@ class DhwPlanner:
 
         best: np.ndarray | None = None
         for _ in range(2):
-            energy_max = np.maximum(p_dhw_max * cop * dt, 1e-9)
+            energy_max = np.maximum(cop * heat_per_cop_kw(params, p_dhw_max) * dt, 1e-9)
             # Shortfall slack keeps the program feasible when the requirement
             # simply cannot be met (cold start, undersized pump); it is priced
             # far above any real electricity cost so it is only ever used as a
@@ -1506,7 +1508,9 @@ class DhwPlanner:
             if solution is None:  # pragma: no cover - success implies a vector
                 return best
             energy = np.asarray(solution[:n_steps], dtype=float)
-            best = np.clip(energy / (cop * dt), 0.0, p_dhw_max)
+            best = np.clip(
+                power_for_heat_per_cop_kw(params, energy / (cop * dt)), 0.0, p_dhw_max
+            )
 
             # Refine the COP estimate against the tank temperatures this plan
             # actually produces, so the cost ranking reflects reality.
@@ -1648,7 +1652,8 @@ class DhwPlanner:
         # The tank's own per-step decay, the same factor the linear program
         # uses: heat added now is worth less later, so the ceiling bound
         # below can price how much of a top-up still survives at each step.
-        decay, _ = _tank_decay(self.model.params.dhw_tank_heat_loss_coefficient, dt, c_dhw)
+        params = self.model.params
+        decay, _ = _tank_decay(params.dhw_tank_heat_loss_coefficient, dt, c_dhw)
         # Breaches no ceiling-legal top-up can close. Skipped rather than
         # returned on: a demand window later in the day is not helped by
         # giving up at the first step the tank cannot quite reach, and a
@@ -1684,14 +1689,10 @@ class DhwPlanner:
             # ENFORCED: heat the tank cannot hold later is refused, not
             # stored, so a top-up displaces the plan's own later charging
             # instead of stacking on top of it, and the capacity clamp below
-            # performs exactly that displacement. Stating the bound over
-            # the whole tail instead — the first cut of this change — made
-            # every later step sitting ON the charge limit read as zero
-            # room, the suffix-minimum carried that zero back over every
-            # earlier candidate, and the repair refused every top-up there
-            # was: a 24 h matrix went from a worst deficit of 0.03 °C to
-            # 1.11 °C, inside a demand window, with no cycle due, and the
-            # run-up to a disinfection cycle was refused the same way.
+            # performs exactly that displacement. Bounded over the whole
+            # tail, every later step ON the charge limit reads as zero room
+            # and the suffix-minimum carries that zero back over every
+            # earlier candidate, refusing every top-up there is.
             gap = ceiling[lo : b + 1] - temps[lo + 1 : b + 2]
             if decay > 1e-6:
                 weight = np.power(decay, np.arange(b + 1 - lo))
@@ -1719,7 +1720,8 @@ class DhwPlanner:
                     ),
                     0.5,
                 )
-                needed = float(deficit[b]) * c_dhw / max(dt * cop_j, 1e-6)
+                needed = added_power_for_heat_per_cop_kw(
+                    params, plan[j], float(deficit[b]) * c_dhw / max(dt * cop_j, 1e-6))
                 # The room bound is sized against the HIGHEST COP that could
                 # apply at this step, not the marginal one used to size the
                 # need: the simulation delivers `compute_cop_dhw` thermal kWh
@@ -1733,7 +1735,8 @@ class DhwPlanner:
                         humidity=_step_humidity(humidity, j),
                     ),
                 )
-                room_kw = float(room_c[j_local]) * c_dhw / max(dt * cop_room, 1e-6)
+                room_kw = added_power_for_heat_per_cop_kw(
+                    params, plan[j], float(room_c[j_local]) * c_dhw / max(dt * cop_room, 1e-6))
                 add = min(
                     float(np.clip(needed, min_run_power, headroom[j_local])),
                     room_kw,
@@ -1872,7 +1875,9 @@ class DhwPlanner:
             q_draw = float(draw_rates[i]) * dhw_draw_scale(temp, inlet)
             q_loss = ua * (temp - TANK_ROOM_AMBIENT_TEMP)
             headroom_c = float(ceiling[i]) - temp
-            allowed = (headroom_c * capacity / dt + q_draw + q_loss) / cop
+            allowed = power_for_heat_per_cop_kw(
+                params, (headroom_c * capacity / dt + q_draw + q_loss) / cop
+            )
             plan[i] = float(np.clip(plan[i], 0.0, max(0.0, allowed)))
 
             # Stepped through the same simulation the planners use, so the
@@ -1880,7 +1885,7 @@ class DhwPlanner:
             temp = float(
                 self.model.simulate_dhw_step(
                     dhw_temp=temp,
-                    dhw_power_thermal=cop * plan[i],
+                    dhw_power_thermal=delivered_heat_kw(params, cop, plan[i]),
                     hour_of_day=0.0,
                     dt_hours=dt,
                     draw_power=float(draw_rates[i]),
@@ -2084,9 +2089,8 @@ class DhwPlanner:
 
         # Fraction of stored heat lost per hour of storage: raising the tank by
         # ΔT stores C·ΔT kWh but adds U·ΔT kW of standby loss.
-        loss_rate_per_hour = (
-            self.model.params.dhw_tank_heat_loss_coefficient / c_dhw
-        )
+        params = self.model.params
+        loss_rate_per_hour = params.dhw_tank_heat_loss_coefficient / c_dhw
 
         unreachable: set[int] = set()
         temps: np.ndarray | None = None
@@ -2145,7 +2149,9 @@ class DhwPlanner:
                         humidity=_step_humidity(humidity, j),
                     ),
                 )
-                spare_thermal_kwh = (p_dhw_max - plan[j]) * cop * dt
+                spare_thermal_kwh = (
+                    heat_per_cop_kw(params, p_dhw_max) - heat_per_cop_kw(params, plan[j])
+                ) * cop * dt
                 # Heat added at step j raises every later tank temperature, so
                 # the ceiling has to be respected across the whole stretch the
                 # heat is stored for — not just at step j. With a per-step
@@ -2164,7 +2170,7 @@ class DhwPlanner:
                 )
                 if take <= 1e-6:
                     continue
-                plan[j] += take / (cop * dt)
+                plan[j] += added_power_for_heat_per_cop_kw(params, plan[j], take / (cop * dt))
                 # Never plan a run below the pump's practical minimum: a
                 # fraction of a kW cannot be delivered by an on/off DHW valve.
                 if 0.0 < plan[j] < min_run_power:
diff --git a/custom_components/heatpump_optimizer/optimizer.py b/custom_components/heatpump_optimizer/optimizer.py
index f019fe6a0..eee005bc2 100644
--- a/custom_components/heatpump_optimizer/optimizer.py
+++ b/custom_components/heatpump_optimizer/optimizer.py
@@ -107,6 +107,8 @@ from .thermal_model import (
     valve_charge_demand,
     weather_or_calm,
     wood_share,
+    power_for_heat_per_cop_kw,
+    added_power_for_heat_per_cop_kw,
 )
 from .tariff import (
     CapacityTariff,
@@ -4168,7 +4170,8 @@ class HeatPumpOptimizer:
                 store_temp=self.model.params.buffer_max_temp,
                 humidity=_step_humidity(humidity, int(i)),
             )
-            allowed = float(schedule[i]) - float(refused[i]) / max(cop_i, 1e-6)
+            allowed = float(schedule[i]) + added_power_for_heat_per_cop_kw(
+                self.model.params, float(schedule[i]), -float(refused[i]) / max(cop_i, 1e-6))
             # Slightly under, or float noise re-trips the same step and burns
             # a repair round confirming it.
             new_cap = max(0.0, allowed) * 0.999
@@ -5336,7 +5339,7 @@ class HeatPumpOptimizer:
             # power is what determines energy use; a clamp burnt
             # min_electrical_power * 24 h per day on a house needing no heat.
             # Nor a clip at 0: the demand is floored at 0 above, the COP at 1.
-            power = min(required_thermal / cop, p.max_electrical_power)
+            power = min(power_for_heat_per_cop_kw(p, required_thermal / cop), p.max_electrical_power)
             baseline_power[i] = power
 
             state = self.model.simulate_step(
diff --git a/custom_components/heatpump_optimizer/thermal_model.py b/custom_components/heatpump_optimizer/thermal_model.py
index 3fb84bc92..da779ce62 100644
--- a/custom_components/heatpump_optimizer/thermal_model.py
+++ b/custom_components/heatpump_optimizer/thermal_model.py
@@ -2106,6 +2106,56 @@ def heat_per_cop_kw(params: ThermalParameters, electrical_power: Any) -> Any:
     return electrical_power
 
 
+def power_for_heat_per_cop_kw(
+    params: ThermalParameters, heat_per_cop: Any, hours: float = 1.0
+) -> Any:
+    """The inverse of :func:`heat_per_cop_kw`: the electrical kW whose heat per
+    unit of COP is ``heat_per_cop`` -- ``heat / cop`` in, the draw out.
+
+    The input itself while the derate is 0, so an inverse conversion with no
+    part-load term is byte-identical to the ``heat / cop`` it replaces. On the
+    band ``h = P - a * P * (P - p_min)``, ``a = d / band``, is quadratic, and
+    the draw is its smaller positive root, the one on the rising branch
+    ``_partload_derate`` keeps the band to: ``2h / (b + sqrt(b^2 - 4ah))``
+    with ``b = 1 + a * p_min``, the form that stays exact as ``a`` falls.
+    Below the floor the factor is 1 and the draw is ``h``; past max power the
+    factor is held, so it is ``h / (1 - d)``. Elementwise, like the forward.
+
+    ``hours`` reads ``heat_per_cop`` as an energy over that many hours of
+    steady draw and returns the electrical kWh: the band scales with it, so a
+    day's total converts without a division and multiplication that would
+    leave the zero-derate answer an ulp off ``heat / cop``."""
+    d = params.cop_partload_derate
+    band = (params.max_electrical_power - params.min_electrical_power) * hours
+    if not d or band <= 0.0:
+        return heat_per_cop
+    p_min = params.min_electrical_power * hours
+    p_max = params.max_electrical_power * hours
+    h = np.asarray(heat_per_cop, dtype=float)
+    a = d / band
+    b = 1.0 + a * p_min
+    on_band = 2.0 * h / (b + np.sqrt(np.maximum(b * b - 4.0 * a * h, 0.0)))
+    held = h / (1.0 - d)
+    power = np.where(h <= p_min, h, np.where(held >= p_max, held, on_band))
+    return float(power) if np.ndim(heat_per_cop) == 0 else power
+
+
+def added_power_for_heat_per_cop_kw(
+    params: ThermalParameters, power_kw: Any, heat_per_cop: Any
+) -> Any:
+    """The draw to add to ``power_kw`` so its heat per unit of COP grows by
+    ``heat_per_cop`` (negative: falls by it): a top-up, or a cut, of a step
+    already planned. On the band one kW more buys less heat at a higher draw,
+    so the increment is not the plain quotient's even where the total is.
+
+    ``heat_per_cop`` itself while the derate is 0, so ``plan + increment`` is
+    byte-identical to the ``plan + heat / cop`` it replaces."""
+    if not params.cop_partload_derate:
+        return heat_per_cop
+    return power_for_heat_per_cop_kw(
+        params, heat_per_cop_kw(params, power_kw) + heat_per_cop) - power_kw
+
+
 def delivered_heat_kw(params: ThermalParameters, cop: Any, electrical_power: Any) -> Any:
     """Heat the pump delivers at ``cop`` and ``electrical_power``, space or hot
     water: ``cop`` times :func:`heat_per_cop_kw`, the one association every
@@ -3348,9 +3398,7 @@ class ThermalModel:
         T_buf = state.buffer_tank_temperature
 
         # --- Buffer tank dynamics ---
-        C_buf = p.buffer_tank_thermal_mass
-        if C_buf < 1e-6:
-            C_buf = 0.04  # fallback for 35L
+        C_buf = _buffer_capacity(p)
 
         rad_fraction = p.radiator_power_fraction
 
@@ -3966,9 +4014,7 @@ class ThermalModel:
             start_hour is not None and p.internal_gains_profile is not None
         )
         # Configuration constants hoisted out of the step (uniform per batch).
-        C_buf = p.buffer_tank_thermal_mass
-        if C_buf < 1e-6:
-            C_buf = 0.04
+        C_buf = _buffer_capacity(p)
         rad_fraction = p.radiator_power_fraction
         area_ratio = p.upper_floor_area_ratio
         # Two-zone valve geometry: uniform per batch.
diff --git a/dev/audit/harnesses/r10_cop_conversions.py b/dev/audit/harnesses/r10_cop_conversions.py
new file mode 100644
index 000000000..c3d5d6964
--- /dev/null
+++ b/dev/audit/harnesses/r10_cop_conversions.py
@@ -0,0 +1,121 @@
+"""R10-COP-PARTLOAD: every conversion between heat and electrical power
+through a COP in the production package, by AST.
+
+    python3 dev/audit/harnesses/r10_cop_conversions.py [ROOT]
+
+ROOT defaults to ``custom_components/heatpump_optimizer``. A hit is a
+division whose divisor is COP-shaped (heat to power) or a product with a
+COP-shaped factor (power to heat), as a ``BinOp`` or an augmented
+assignment. COP-shaped: a name, attribute, call or subscript whose
+identifier contains ``cop`` (any case), but not ``copy`` or ``scope`` and not
+one of the conversion helpers themselves; a product of such terms
+(``cop * dt``); or a ``max``/``min``/``float``/``abs`` wrapping one
+(``max(dt * cop_j, 1e-6)``). Only the outermost hit of a nested pair is
+printed, so ``take / (cop * dt)`` is one hit, not two. Each line is
+``file:line:function:DIV|MUL:ROUTED|PLAIN: expression``; the function
+anchors the hit when a line shifts. ``ROUTED`` marks a hit that goes through
+a helper: an argument of one, or an expression with a helper call in an
+operand (``cop * heat_per_cop_kw(...)``). Every call of a helper is printed
+too, as ``CALL:ROUTED``, so a conversion written as one call
+(``delivered_heat_kw(params, cop, p)``) is still a listed seam. The last two
+lines count the hits, and the PLAIN ones among them.
+
+The rule is lexical by design: it over-fires on COP-named constants that are
+not a coefficient of performance (``COP_HEALTH_THRESHOLD``), which a
+disposition answers, and it cannot see a COP that was renamed before the
+conversion (a ``heat_per_kwh`` variable), which is why the heat-per-COP
+helpers in ``thermal_model.py`` are the only sanctioned conversion route.
+"""
+from __future__ import annotations
+
+import ast
+import re
+import sys
+from pathlib import Path
+
+_COP = re.compile(r"cop", re.I)
+_NOT_COP = re.compile(r"copy|scope", re.I)
+HELPERS = {
+    "heat_per_cop_kw", "power_for_heat_per_cop_kw",
+    "added_power_for_heat_per_cop_kw", "delivered_heat_kw",
+}
+_WRAPPERS = {"max", "min", "float", "abs", "maximum", "minimum"}
+
+
+def _ident(node: ast.AST) -> str | None:
+    if isinstance(node, ast.Name):
+        return node.id
+    if isinstance(node, ast.Attribute):
+        return node.attr
+    if isinstance(node, (ast.Call, ast.Subscript)):
+        return _ident(node.func if isinstance(node, ast.Call) else node.value)
+    return None
+
+
+def _copish(node: ast.AST) -> bool:
+    name = _ident(node)
+    if isinstance(node, ast.Call) and name in _WRAPPERS:
+        return any(_copish(arg) for arg in node.args)
+    if name and _COP.search(name) and not _NOT_COP.search(name) and name not in HELPERS:
+        return True
+    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
+        return _copish(node.left) or _copish(node.right)
+    return False
+
+
+def _hit(op: ast.operator, left: ast.AST, right: ast.AST) -> str | None:
+    if isinstance(op, ast.Div) and _copish(right):
+        return "DIV"
+    if isinstance(op, ast.Mult) and (_copish(left) or _copish(right)):
+        return "MUL"
+    return None
+
+
+def _helper_call(node: ast.AST) -> bool:
+    return isinstance(node, ast.Call) and _ident(node) in HELPERS
+
+
+def scan(root: Path) -> list[str]:
+    out: list[tuple[str, int, str]] = []
+    for path in sorted(root.rglob("*.py")):
+        tree = ast.parse(path.read_text(), filename=str(path))
+        rel = path.relative_to(root)
+
+        def walk(node: ast.AST, func: str, inside: bool, routed: bool) -> None:
+            kind = None
+            if isinstance(node, ast.BinOp):
+                kind = _hit(node.op, node.left, node.right)
+                pair = (node.left, node.right)
+            elif isinstance(node, ast.AugAssign):
+                kind = _hit(node.op, node.target, node.value)
+                pair = (node.target, node.value)
+            if _helper_call(node):
+                out.append((str(rel), node.lineno, f"{rel}:{node.lineno}:{func}:"
+                            f"CALL:ROUTED: {ast.unparse(node)}"))
+            if kind and not inside:
+                via = any(_helper_call(n) for side in pair for n in ast.walk(side))
+                route = "ROUTED" if routed or via else "PLAIN"
+                out.append((str(rel), node.lineno, f"{rel}:{node.lineno}:{func}:"
+                            f"{kind}:{route}: {ast.unparse(node)}"))
+            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
+                func = node.name
+            for child in ast.iter_child_nodes(node):
+                arg = _helper_call(node) and child in node.args
+                walk(child, func, inside or bool(kind), routed or arg)
+
+        walk(tree, "<module>", False, False)
+    return [line for _, _, line in sorted(out)]
+
+
+def main(argv: list[str]) -> int:
+    root = Path(argv[1] if len(argv) > 1 else "custom_components/heatpump_optimizer")
+    hits = scan(root)
+    for line in hits:
+        print(line)
+    print(f"RESULT hits={len(hits)}")
+    print(f"RESULT plain={sum(':PLAIN: ' in line for line in hits)}")
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv))
diff --git a/dev/governance/config/policy_budgets.json b/dev/governance/config/policy_budgets.json
index 243d8e824..60e213864 100644
--- a/dev/governance/config/policy_budgets.json
+++ b/dev/governance/config/policy_budgets.json
@@ -63,7 +63,7 @@
     "dev/governance/dimensions/D15.md": 37,
     "dev/governance/roles/design-review.md": 53,
     "dev/governance/roles/designer.md": 60,
-    "tools/audit/briefs/D2.md": 51,
+    "tools/audit/briefs/D2.md": 53,
     "tools/audit/briefs/D3.md": 46,
     "tools/audit/briefs/D4.md": 48,
     "tools/audit/briefs/D5.md": 42,
@@ -116,7 +116,7 @@
     "dev/governance/dimensions/D15.md": 690,
     "dev/governance/roles/design-review.md": 778,
     "dev/governance/roles/designer.md": 878,
-    "tools/audit/briefs/D2.md": 644,
+    "tools/audit/briefs/D2.md": 683,
     "tools/audit/briefs/D3.md": 607,
     "tools/audit/briefs/D4.md": 586,
     "tools/audit/briefs/D5.md": 514,
diff --git a/dev/governance/dimensions/D2.md b/dev/governance/dimensions/D2.md
index 713000db5..2e89ba601 100644
--- a/dev/governance/dimensions/D2.md
+++ b/dev/governance/dimensions/D2.md
@@ -23,7 +23,9 @@ tolerance, not by reading the code.
 2. **COP and derates.** COP monotone in outdoor and flow temperature, Carnot
    fraction within the stated band, every derate in [0, 1], defrost derate
    bounded and continuous at the band edges, capacity envelope never below
-   demand-at-derate without a reason code.
+   demand-at-derate without a reason code. First derive the priced
+   formula's inputs from the device's own control surface, and mark each a
+   modelled term, a documented constant, or out of scope.
 3. **Objective.** `predicted_cost == Σ price·power·dt` on every golden
    fixture; the savings identity; the terminal credit's sign and magnitude
    versus a re-simulated continuation; every penalty term's scaling with
diff --git a/dev/programme/delivery/3006.md b/dev/programme/delivery/3006.md
new file mode 100644
index 000000000..6b32abbe0
--- /dev/null
+++ b/dev/programme/delivery/3006.md
@@ -0,0 +1 @@
+- [#3006](https://github.com/tvofi/heatpump_optimizer/pull/3006) — **open**, R10-COP-PARTLOAD part 2: inverse conversions and residual carries (R10-COP-PARTLOAD)
diff --git a/tests/closures.json b/tests/closures.json
index 6f93af714..0683edda8 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3912,6 +3912,7 @@
    "dev/audit/harnesses/r10_cloud_setup_toolchain.py",
    "dev/audit/harnesses/r10_codescan_wait_race.py",
    "dev/audit/harnesses/r10_configflow_pages.py",
+   "dev/audit/harnesses/r10_cop_conversions.py",
    "dev/audit/harnesses/r10_cop_gate.py",
    "dev/audit/harnesses/r10_cop_gate_vent.py",
    "dev/audit/harnesses/r10_cop_partload.py",
diff --git a/tests/features.py b/tests/features.py
index 3e5c55705..3c7070fd2 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -72978,6 +72978,363 @@ R.check(
 )
 
 
+# R10-COP-PARTLOAD part 2: the inverse conversions. With a derate the forward
+# relation is quadratic in power, so ``heat / cop`` understates the draw a heat
+# needs; ``power_for_heat_per_cop_kw`` is its root on the rising branch, and
+# the four sites that close the loop (the hot-water LP and its clamp, the
+# savings baseline, the setpoint sweep) take it. 0 keeps every one exact.
+from heatpump_optimizer.thermal_model import (  # noqa: E402
+    heat_per_cop_kw as _pli_fwd,
+    power_for_heat_per_cop_kw as _pli_inv,
+)
+_pli_p = _pl_model(0.15).params
+_pli_grid = np.linspace(0.0, 6.5, 1301)
+# Raise on an invalid sqrt: past the parabola's vertex the on-band branch is
+# computed and discarded, and must not warn on every hot-water clamp step.
+with np.errstate(all="raise"):
+    _pli_back = _pli_fwd(_pli_p, _pli_inv(_pli_p, _pli_fwd(_pli_p, _pli_grid)))
+    _pli_far = _pli_inv(_pli_p, np.linspace(0.0, 50.0, 11))
+_pli_err = float(np.max(np.abs(_pli_back - _pli_fwd(_pli_p, _pli_grid))))
+_pli_x = 2.5
+_pli_day = _pli_inv(_pli_p, 60.0, hours=24.0)
+# The band's edges are taken exactly, not through the root, whose float at the
+# edge can land an ulp off: the floor on a 2-6 kW band at 0.3, and max power on
+# a 1.5-5 kW band at 0.4, where 5 * 0.6 / 0.6 is exactly 5.
+_pli_edges = (_pli_inv(_pl_model(0.3, 2.0, 6.0).params, 2.0),
+              _pli_inv(_pl_model(0.4).params, 3.0))
+R.check(
+    "the inverse conversion returns the draw whose derated heat is the heat "
+    "asked for, below the floor, on the band and past max power, to 1e-12; "
+    "on the band it needs more power than heat / cop; the band's edges are "
+    "exact and a fixed-speed band inverts to itself; a day's energy converts "
+    "as 24 h of its mean draw; "
+    "null control: a zero derate hands the quotient back unchanged",
+    _pli_err < 1e-12 and float(_pli_inv(_pli_p, 3.0)) > 3.0
+    and _pli_inv(_pli_p, 1.0) == 1.0 and _pli_edges == (2.0, 5.0)
+    and float(_pli_far[-1]) == 50.0 / 0.85
+    and _pli_inv(_pl_model(0.12, 3.0, 3.0).params, 2.0) == 2.0
+    and abs(_pli_day - 24.0 * float(_pli_inv(_pli_p, 2.5))) < 1e-9
+    and _pli_inv(_pl_model(0.0).params, _pli_x) is _pli_x
+    and _pli_inv(_pl_model(0.0).params, 60.0, hours=24.0) == 60.0,
+    f"round trip {_pli_err:.2e} on band {float(_pli_inv(_pli_p, 3.0)):.4f} "
+    f"day {_pli_day:.4f} edges {_pli_edges}",
+)
+
+
+def _pli_baseline(derate, outdoor):
+    p = ThermalParameters(min_electrical_power=1.5, max_electrical_power=5.0,
+                          cop_partload_derate=derate)
+    out = np.full(1, outdoor)
+    zero = np.zeros(1)
+    power, _ = _PvOpt(ThermalModel(p), _PvOptCfg(target_temp=21.0))._compute_baseline_power(
+        _WS(out, zero, zero, zero),
+        ThermalState(room_temperature=21.0, slab_temperature=26.0,
+                     outdoor_temperature=outdoor), 0.25)
+    return float(power[0])
+
+
+_pli_bl = {d: _pli_baseline(d, -15.0) for d in (0.0, 0.2)}
+_pli_bl_mild = {d: _pli_baseline(d, 15.0) for d in (0.0, 0.2)}
+R.check(
+    "the savings baseline buys a derated pump's heat at the power that "
+    "delivers it: on the band its draw rises with the derate; "
+    "null control: a draw below the modulation floor is unchanged",
+    _pli_bl[0.2] > _pli_bl[0.0] > 1.5 and _pli_bl_mild[0.2] == _pli_bl_mild[0.0] < 1.5,
+    f"cold {_pli_bl} mild {_pli_bl_mild}",
+)
+
+
+def _pli_clamp_end(derate):
+    """Tank temperatures after two clamped 5 kW steps aimed at the 52 C
+    ceiling, the second after a draw: its room is read off the clamp's own
+    walk of the first, so that walk must price the derate too."""
+    opt, _ = _r7d203_opt(200.0, cop_partload_derate=derate)
+    out, draws = np.full(2, 5.0), np.array([0.0, 4.0])
+    plan = _dhw_planner(opt)._clamp_dhw_to_capacity(
+        plan=np.full(2, 5.0), initial_temp=48.0, outdoor_temps=out,
+        draw_rates=draws, dt=0.25, max_temp=np.full(2, 52.0))
+    temps = np.array([48.0, 0.0, 0.0])
+    opt.model.extend_dhw_temps(temps, 0, plan, out, draws, dt_hours=0.25)
+    return float(plan[0]), float(temps[1]), float(temps[2])
+
+
+_pli_clamp = {d: _pli_clamp_end(d) for d in (0.0, 0.2)}
+R.check(
+    "the hot-water clamp's truncated steps land on their ceiling in the derated "
+    "simulation, not short of it or past it, at a draw above the plain "
+    "quotient's; null control: with no derate they land there too",
+    all(abs(t - 52.0) < 1e-9 for d in (0.0, 0.2) for t in _pli_clamp[d][1:])
+    and _pli_clamp[0.2][0] > _pli_clamp[0.0][0] > 1.0,
+    f"{_pli_clamp}",
+)
+
+
+def _pli_lp_end(derate, p_dhw_max=3.0, dt=1.0):
+    """Tank temperature where the minimum-cost LP must reach 58 C."""
+    n = 8
+    opt, _ = _r7d203_opt(200.0, cop_partload_derate=derate)
+    req = np.full(n, 40.0)
+    req[-1] = 58.0
+    prices = np.array([5.0] * (n - 1) + [1.0])
+    ctx = _dhw_ctx(prices=prices, outdoor=np.full(n, 5.0), n=n, dt=dt,
+                   c_dhw=opt.model.params.dhw_tank_thermal_mass, p_dhw_max=p_dhw_max)
+    planner = _dhw_planner(opt)
+    plan = planner._plan_dhw_min_cost(ctx, 45.0, req, np.zeros(n), np.full(n, 65.0))
+    temps = opt.model.simulate_dhw_only(
+        initial_temp=45.0, dhw_power_schedule=plan, outdoor_temps=np.full(n, 5.0),
+        draw_rates=np.zeros(n), dt_hours=dt)
+    return float(plan[-1]), float(temps[-1])
+
+
+_pli_lp = {d: _pli_lp_end(d) for d in (0.0, 0.2)}
+# Capped below the last step's need: the LP must buy the rest earlier, at the
+# heat a derated pump delivers at its cap, not the plain product's.
+_pli_lp_cap = {d: _pli_lp_end(d, 2.0, 0.5) for d in (0.0, 0.2)}
+R.check(
+    "the hot-water LP's plan, simulated with the derate, reaches the floor it "
+    "was solved against: its last-step draw is the root, not heat / cop; "
+    "and capped below that draw it sizes its energy ceiling by the derated "
+    "heat; null control: with no derate the floor is met at a lower draw",
+    all(r[1] > 58.0 - 0.05 for r in (*_pli_lp.values(), *_pli_lp_cap.values()))
+    and _pli_lp[0.2][0] > _pli_lp[0.0][0] > 1.0,
+    f"{_pli_lp} capped {_pli_lp_cap}",
+)
+
+
+def _pli_sweep(derate):
+    coord = Coord(FakeHass(), _r7d203_entry(
+        data={"tibber_token": "x", "weather_entity": "weather.home"}))
+    params = coord._thermal_params
+    params.dhw_enabled = True
+    params.min_electrical_power = 0.0
+    params.cop_partload_derate = derate
+    coord._prices = [{"total": 1.0}] * 24
+    return [c["cost_per_day"] for c in coord._dhw_setpoint_sweep()["candidates"]]
+
+
+_pli_sw = {d: _pli_sweep(d) for d in (0.0, 0.4)}
+R.check(
+    "the setpoint sweep prices a day's hot water at the draw that delivers it: "
+    "with a floorless band every candidate costs more under the derate; "
+    "null control: the zero-derate costs are the plain quotient's",
+    len(_pli_sw[0.0]) == 7
+    and all(b > a for a, b in zip(_pli_sw[0.0], _pli_sw[0.4])),
+    f"{_pli_sw}",
+)
+
+
+# Round 2: the hot-water planner's remaining conversions, the capacity caps,
+# the buffer-cap tightening and the battery's charge rate, enumerated by
+# dev/audit/harnesses/r10_cop_conversions.py. An increment on a planned step
+# is ``added_power_for_heat_per_cop_kw``: one kW more buys less heat on the band.
+from heatpump_optimizer.thermal_model import (  # noqa: E402
+    added_power_for_heat_per_cop_kw as _pli_add,
+)
+_pli_add_p = _pl_model(0.2).params
+_pli_add_x = 0.7
+_pli_add_back = [
+    float(_pli_fwd(_pli_add_p, p0 + _pli_add(_pli_add_p, p0, dh))
+          - _pli_fwd(_pli_add_p, p0))
+    for p0 in (0.5, 2.0, 4.0) for dh in (0.3, 1.0, -0.4)]
+R.check(
+    "a top-up's increment adds exactly the heat asked for to the step's own "
+    "derated heat, up or down, and costs more than the plain quotient on the "
+    "band; null control: a zero derate hands the quotient back unchanged",
+    max(abs(b - dh) for b, dh in zip(_pli_add_back, [0.3, 1.0, -0.4] * 3)) < 1e-12
+    and _pli_add(_pli_add_p, 2.0, 1.0) > 1.0
+    and _pli_add(_pl_model(0.0).params, 2.0, _pli_add_x) is _pli_add_x,
+    f"{_pli_add_back}",
+)
+
+
+def _pli_greedy(derate, need=50.0, n=4, dt=0.5, p_dhw_max=3.0):
+    """The cheapest-first planner's plan and the derated tank's end
+    temperature, filling one floor at the last (cheapest) step."""
+    opt, _ = _r7d203_opt(200.0, cop_partload_derate=derate)
+    out = np.full(n, 5.0)
+    req = np.full(n, 40.0)
+    req[-1] = need
+    plan = _dhw_planner(opt)._plan_dhw_cheapest_first(
+        _dhw_ctx(prices=np.linspace(2.0, 1.0, n), outdoor=out, n=n, dt=dt,
+                 c_dhw=opt.model.params.dhw_tank_thermal_mass, p_dhw_max=p_dhw_max),
+        45.0, req, np.zeros(n), np.full(n, 65.0))
+    temps = opt.model.simulate_dhw_only(
+        initial_temp=45.0, dhw_power_schedule=plan, outdoor_temps=out,
+        draw_rates=np.zeros(n), dt_hours=dt)
+    return [round(float(x), 6) for x in plan], float(temps[-1])
+
+
+_pli_gr = {d: _pli_greedy(d, need=53.0) for d in (0.0, 0.2)}
+# Capped at 1.5 kW the last step cannot hold it all: the planner fills it to
+# the cap and buys the rest a step earlier, sized by the derated heat the
+# cap delivers, not the plain product's.
+_pli_gr_cap = {d: _pli_greedy(d, need=56.0, p_dhw_max=1.5) for d in (0.0, 0.2)}
+R.check(
+    "the cheapest-first planner buys a derated pump's heat at the draw that "
+    "delivers it: one block lands the tank where the zero-derate block does, "
+    "at a higher draw; capped, its spare heat is the derated heat the cap "
+    "delivers and the floor is still met; null control: with no derate the "
+    "same tank and the plain draw",
+    abs(_pli_gr[0.2][1] - _pli_gr[0.0][1]) < 1e-9
+    and _pli_gr[0.2][0][-1] > _pli_gr[0.0][0][-1] > 1.0
+    and all(r[0][-1] == 1.5 and r[1] > 56.0 - 0.05 for r in _pli_gr_cap.values()),
+    f"{_pli_gr} capped {_pli_gr_cap}",
+)
+
+
+def _pli_runup(derate):
+    """The anti-legionella run-up floor, walked back from a 20:00 cycle."""
+    opt, params = _r7d203_opt(200.0, cop_partload_derate=derate)
+    n = 24
+    res = _dhw_planner(opt)._dhw_legionella_ceilings(
+        _dhw_horizon(prices=np.zeros(n), outdoor=np.full(n, -5.0), n=n, dt=1.0),
+        params=params, c_dhw=params.dhw_tank_thermal_mass, draw_rates=np.zeros(n),
+        floor_temps=np.full(n, 20.0), p_dhw_run=3.0, legionella_due=True,
+        legionella_hour=20.0, legionella_step=20)
+    return [round(float(x), 4) for x in res.runup_temps]
+
+
+_pli_ru = {d: _pli_runup(d) for d in (0.0, 0.2)}
+R.check(
+    "the anti-legionella run-up walks back along the heat a derated pump "
+    "delivers at its run power: each step lifts the tank less, so the floor "
+    "before the cycle starts higher; null control: no derate, the plain walk",
+    _pli_ru[0.2][18] > _pli_ru[0.0][18] > 0.0
+    and _pli_ru[0.2][19] > _pli_ru[0.0][19] > 0.0,
+    f"{_pli_ru[0.0][17:21]} vs {_pli_ru[0.2][17:21]}",
+)
+
+
+def _pli_repair(derate, need=52.0, ceiling=(65.0,) * 4, prices=(2.0, 1.6667, 1.3333, 1.0)):
+    """The floor repair topping up an empty plan: its first block, and the
+    derated tank's temperature at the floor step."""
+    n = 4
+    opt, _ = _r7d203_opt(200.0, cop_partload_derate=derate)
+    out = np.full(n, 5.0)
+    req = np.full(n, 40.0)
+    req[-1] = need
+    ctx = _dhw_ctx(prices=np.array(prices), outdoor=out, n=n, dt=0.5,
+                   c_dhw=opt.model.params.dhw_tank_thermal_mass, p_dhw_max=5.0)
+    plan = _dhw_planner(opt)._repair_dhw_floor(
+        ctx, plan=np.zeros(n), initial_temp=45.0, draw_rates=np.zeros(n),
+        requirement=req, max_temp=np.array(ceiling))
+    temps = opt.model.simulate_dhw_only(
+        initial_temp=45.0, dhw_power_schedule=plan, outdoor_temps=out,
+        draw_rates=np.zeros(n), dt_hours=0.5)
+    return [round(float(x), 6) for x in plan], [round(float(t), 6) for t in temps]
+
+
+_pli_rep = {d: _pli_repair(d) for d in (0.0, 0.2)}
+# The cheap first step sits under a 55 C ceiling at the next: its block is
+# bounded by that room, so the room must be converted at the derate too.
+_pli_rep_room = {d: _pli_repair(d, need=60.0, ceiling=(65.0, 55.0, 65.0, 65.0),
+                                prices=(1.0, 2.0, 3.0, 4.0)) for d in (0.0, 0.2)}
+R.check(
+    "the floor repair's top-up and its room under the ceiling are the draws "
+    "that deliver the heat at a derate: the derated tank walks the same "
+    "temperatures as the zero-derate one, at higher draws; "
+    "null control: with no derate the plain quotients",
+    all(max(abs(a - b) for a, b in zip(r[0.0][1], r[0.2][1])) < 1e-6
+        for r in (_pli_rep, _pli_rep_room))
+    and abs(_pli_rep[0.2][1][-1] - 52.0) < 1e-6
+    and abs(_pli_rep_room[0.2][1][2] - 55.0) < 1e-6
+    and _pli_rep[0.2][0][-1] > _pli_rep[0.0][0][-1]
+    and _pli_rep_room[0.2][0][0] > _pli_rep_room[0.0][0][0],
+    f"{_pli_rep} room {_pli_rep_room}",
+)
+
+
+def _pli_dhw_baseline(derate, p_min):
+    opt = _MbOpt(ThermalModel(ThermalParameters.from_config(_mb_profiles.house())),
+                 _MbCfg(horizon_hours=1))
+    opt.model.params.min_electrical_power = p_min
+    opt.model.params.cop_partload_derate = derate
+    bd, _, _, _ = _dhw_planner(opt)._baseline_dhw_economics(
+        ThermalState(wood_tank_temperature=None), np.full(3, -5.0), 3,
+        float(opt.model.params.dhw_setpoint), lambda p: float(np.sum(p)),
+        np.full(3, 2.0), np.ones(3), np.ones(3))
+    return float(bd[0])
+
+
+_pli_dbl = {(d, f): _pli_dhw_baseline(d, f) for d in (0.0, 0.4) for f in (0.0, 1.0)}
+R.check(
+    "the always-hot hot-water baseline buys its mean draw at the power that "
+    "delivers it: on a floorless band the derate raises it; null control: "
+    "below a 1 kW modulation floor, where real installs run it, unchanged",
+    _pli_dbl[(0.4, 0.0)] > _pli_dbl[(0.0, 0.0)] == _pli_dbl[(0.0, 1.0)]
+    and _pli_dbl[(0.4, 1.0)] == _pli_dbl[(0.0, 1.0)],
+    f"{_pli_dbl}",
+)
+
+
+def _pli_caps(derate):
+    c = _t2_coord(capacity_curve_enabled=True)
+    params = c._thermal_params
+    params.cop_partload_derate = derate
+    model = ThermalModel(params)
+    bucket = int(np.floor(-10.0 / 3.0))
+    # The envelope holds exactly the heat the model says nameplate delivers.
+    full = float(model.compute_cop(-10.0)) * float(_pli_fwd(params, params.max_electrical_power))
+    c._capacity_envelope[bucket] = [full, CAPACITY_MIN_SAMPLES + 2]
+    caps = c._capacity_caps(np.array([-10.0]), model=model)
+    return params.max_electrical_power, None if caps is None else float(caps[0])
+
+
+_pli_cap = {d: _pli_caps(d) for d in (0.0, 0.2)}
+R.check(
+    "the capacity caps turn an envelope that holds exactly the heat the model "
+    "says nameplate delivers back into nameplate, under a derate too, not a "
+    "cap trimmed by the derate; null control: no derate, no cap either",
+    _pli_cap[0.0] == (5.0, None) and _pli_cap[0.2] == (5.0, None),
+    f"{_pli_cap}",
+)
+
+
+def _pli_tighten(derate):
+    p, m, opt, st, _, out, zeros = _cap_fixture()
+    p.cop_partload_derate = derate
+    weather = _WS(out, zeros, zeros, zeros)
+    full = np.full(96, p.max_electrical_power)
+
+    class _Res:
+        power_schedule = full
+
+    caps = full.copy()
+    opt._tighten_buffer_caps(weather, st, _Res(), caps, 0.25)
+    _, _, _, _, _, refused, _ = m.simulate_trajectory(st, np.minimum(full, caps), weather, dt_hours=0.25)
+    return float(caps.min()), float(refused.max())
+
+
+_pli_tg = {d: _pli_tighten(d) for d in (0.0, 0.2)}
+R.check(
+    "the buffer-cap tightening cuts a refusing step to the draw whose derated "
+    "heat the tank takes: re-simulated at the new caps nothing is refused, "
+    "and the cut is shallower than the plain quotient's; null control: with "
+    "no derate it refuses nothing either",
+    all(r[1] < 1e-9 for r in _pli_tg.values()) and _pli_tg[0.2][0] > _pli_tg[0.0][0],
+    f"{_pli_tg}",
+)
+
+
+def _pli_battery(derate):
+    p = ThermalParameters(min_electrical_power=1.0, max_electrical_power=5.0,
+                          cop_partload_derate=derate)
+    view = battery_view.build(
+        p, ThermalState(room_temperature=21.0, slab_temperature=22.0,
+                        outdoor_temperature=0.0, dhw_temperature=50.0),
+        comfort_min=19.0, comfort_max=23.0, dhw_min=40.0, dhw_max=55.0, cop=3.0)
+    return view.charge_rate_kw
+
+
+_pli_bat = {d: _pli_battery(d) for d in (0.0, 0.2)}
+R.check(
+    "the virtual battery's charge rate is the heat the pump delivers at "
+    "nameplate, derate included; null control: no derate, power times COP",
+    _pli_bat == {0.0: 15.0, 0.2: 12.0},
+    f"{_pli_bat}",
+)
+
+
 # --- #2261: a delivered-heat counter, the mode dwell and one attribution --------
 # R10-HEAT-METER. A ``total_increasing`` kWh counter of the heat the pump
 # delivered is read per span (``heat_energy.HeatEnergyMeter``), the span closing
diff --git a/tests/mutation_ledger/killed_by/battery.py/VirtualBattery.charge_rate_kw.RETURN_DEL.b403cdd2.json b/tests/mutation_ledger/killed_by/battery.py/VirtualBattery.charge_rate_kw.RETURN_DEL.b403cdd2.json
new file mode 100644
index 000000000..d43fbc164
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/battery.py/VirtualBattery.charge_rate_kw.RETURN_DEL.b403cdd2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/battery.py:VirtualBattery.charge_rate_kw RETURN_DEL b403cdd2",
+  "killed_by": "tests/features.py",
+  "old": "        return max(self.cop, 0.1) * self.charge_heat_per_cop_kw",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.BOOLOP.a5d8d969.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.BOOLOP.a5d8d969.json
deleted file mode 100644
index 2b6dc5af4..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.BOOLOP.a5d8d969.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._capacity_caps BOOLOP a5d8d969",
-  "killed_by": "tests/features.py",
-  "old": "            has_hum = humidity is not None and i < len(humidity)",
-  "reason": "R8-P3 round 2 (fix review): the capacity envelope's per-step humidity. `and` -> `or` evaluates `len(None)` on every call without a forecast, so tests/features.py dies with `TypeError: object of type 'NoneType' has no len()` at the #17 envelope checks (`_capacity_caps(np.array([-10.0, -10.0, 15.0]))`), measured in a git-less copy of ef45f9ce's production. A crash, not a counted FAIL line: the kill is the uncaught error on the only path every install without a humidity forecast takes."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.BOOLOP.f3835ba8.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.BOOLOP.f3835ba8.json
new file mode 100644
index 000000000..b904337f0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.BOOLOP.f3835ba8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._capacity_caps BOOLOP f3835ba8",
+  "killed_by": "tests/features.py",
+  "old": "            hum = float(humidity[i]) if humidity is not None and i < len(humidity) else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`hum = float(humidity[i]) if humidity is not None or i < len(humidity) else None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CLAMP_DROP.8a6fab44.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CLAMP_DROP.8a6fab44.json
new file mode 100644
index 000000000..a913f9e42
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CLAMP_DROP.8a6fab44.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._capacity_caps CLAMP_DROP 8a6fab44",
+  "killed_by": "tests/features.py",
+  "old": "            cap_i = float(np.clip(power_for_heat_per_cop_kw(model.params, float(entry[0]) / cop_i), floor, p_max))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`cap_i = float((power_for_heat_per_cop_kw(model.params, float(entry[0]) / cop_i)))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CMP_BOUND.a5d8d969.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CMP_BOUND.a5d8d969.json
deleted file mode 100644
index 23fe60e39..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CMP_BOUND.a5d8d969.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._capacity_caps CMP_BOUND a5d8d969",
-  "killed_by": "tests/features.py",
-  "old": "            has_hum = humidity is not None and i < len(humidity)",
-  "reason": "Recorded by `mutation_table.py --drain`: CMP_BOUND (`has_hum = humidity is not None and i <= len(humidity)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CMP_BOUND.f3835ba8.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CMP_BOUND.f3835ba8.json
new file mode 100644
index 000000000..e8771f19c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CMP_BOUND.f3835ba8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._capacity_caps CMP_BOUND f3835ba8",
+  "killed_by": "tests/features.py",
+  "old": "            hum = float(humidity[i]) if humidity is not None and i < len(humidity) else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`hum = float(humidity[i]) if humidity is not None and i <= len(humidity) else None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.CLAMP_DROP.2bd515d1.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.CLAMP_DROP.2bd515d1.json
deleted file mode 100644
index c19a2cffd..000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.CLAMP_DROP.2bd515d1.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._compute_baseline_power CLAMP_DROP 2bd515d1",
-  "killed_by": "tests/features.py",
-  "old": "            power = min(required_thermal / cop, p.max_electrical_power)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 5c0ee109305fc4f377c9326c712156b9ceb0e638: CLAMP_DROP (`power = (required_thermal / cop)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.CLAMP_DROP.67fa09c5.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.CLAMP_DROP.67fa09c5.json
new file mode 100644
index 000000000..4439bdeb9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.CLAMP_DROP.67fa09c5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._compute_baseline_power CLAMP_DROP 67fa09c5",
+  "killed_by": "tests/features.py",
+  "old": "            power = min(power_for_heat_per_cop_kw(p, required_thermal / cop), p.max_electrical_power)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`power = (power_for_heat_per_cop_kw(p, required_thermal / cop))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/added_power_for_heat_per_cop_kw.GUARD_OFF.f57dc5dd.json b/tests/mutation_ledger/killed_by/thermal_model.py/added_power_for_heat_per_cop_kw.GUARD_OFF.f57dc5dd.json
new file mode 100644
index 000000000..175e04fe5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/added_power_for_heat_per_cop_kw.GUARD_OFF.f57dc5dd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:added_power_for_heat_per_cop_kw GUARD_OFF f57dc5dd",
+  "killed_by": "tests/features.py",
+  "old": "    if not params.cop_partload_derate:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.CLAMP_DROP.0d030b71.json b/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.CLAMP_DROP.0d030b71.json
new file mode 100644
index 000000000..54c47ecbd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.CLAMP_DROP.0d030b71.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:power_for_heat_per_cop_kw CLAMP_DROP 0d030b71",
+  "killed_by": "tests/features.py",
+  "old": "    on_band = 2.0 * h / (b + np.sqrt(np.maximum(b * b - 4.0 * a * h, 0.0)))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`on_band = 2.0 * h / (b + np.sqrt((b * b - 4.0 * a * h)))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.CMP_BOUND.7f1dd302.json b/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.CMP_BOUND.7f1dd302.json
new file mode 100644
index 000000000..22c373220
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.CMP_BOUND.7f1dd302.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:power_for_heat_per_cop_kw CMP_BOUND 7f1dd302",
+  "killed_by": "tests/features.py",
+  "old": "    if not d or band <= 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if not d or band < 0.0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.CMP_BOUND.e7058406.json b/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.CMP_BOUND.e7058406.json
new file mode 100644
index 000000000..acbd35802
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.CMP_BOUND.e7058406.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:power_for_heat_per_cop_kw CMP_BOUND e7058406",
+  "killed_by": "tests/features.py",
+  "old": "    power = np.where(h <= p_min, h, np.where(held >= p_max, held, on_band))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`power = np.where(h < p_min, h, np.where(held >= p_max, held, on_band))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.GUARD_OFF.7f1dd302.json b/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.GUARD_OFF.7f1dd302.json
new file mode 100644
index 000000000..6971de5bb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.GUARD_OFF.7f1dd302.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:power_for_heat_per_cop_kw GUARD_OFF 7f1dd302",
+  "killed_by": "tests/features.py",
+  "old": "    if not d or band <= 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.RETURN_DEL.bc569d66.json b/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.RETURN_DEL.bc569d66.json
new file mode 100644
index 000000000..c031be3bf
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/power_for_heat_per_cop_kw.RETURN_DEL.bc569d66.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:power_for_heat_per_cop_kw RETURN_DEL bc569d66",
+  "killed_by": "tests/features.py",
+  "old": "    return float(power) if np.ndim(heat_per_cop) == 0 else power",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/survivor_triage/battery.py/VirtualBattery.charge_rate_kw.CLAMP_DROP.b403cdd2.json b/tests/mutation_ledger/survivor_triage/battery.py/VirtualBattery.charge_rate_kw.CLAMP_DROP.b403cdd2.json
new file mode 100644
index 000000000..55defcb64
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/battery.py/VirtualBattery.charge_rate_kw.CLAMP_DROP.b403cdd2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/battery.py:VirtualBattery.charge_rate_kw CLAMP_DROP b403cdd2",
+  "old": "        return max(self.cop, 0.1) * self.charge_heat_per_cop_kw",
+  "reason": "R10-COP-PARTLOAD p2 round 2 re-anchored this line (the factor became `charge_heat_per_cop_kw`); the clamp is the old line's. `battery.build`'s only caller (`coordinator.py`, the battery view) passes `cop` from `ThermalModel.compute_cop`, which returns `_cop_law`'s `max(cop, 1.0)` (#928's resistive bound), so `max(cop, 0.1)` cannot select its second arm.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CLAMP_DROP.33200ef3.json b/tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CLAMP_DROP.33200ef3.json
deleted file mode 100644
index f5c25bed9..000000000
--- a/tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CLAMP_DROP.33200ef3.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._capacity_caps CLAMP_DROP 33200ef3",
-  "old": "            cop_i = max((model or self._thermal_model).compute_cop(float(outdoor), humidity=hum), 1e-6)",
-  "reason": "R8-P3 round 2 re-anchored this line (it gained the humidity argument); it was unpinned at the merge base under its old text. `max(compute_cop(...), 1e-6)` cannot select the second arm: `compute_cop` returns `_cop_law`, which returns `max(cop, 1.0)` (#928's resistive bound). Re-keyed by #1736, which judges the caps on the solve's own model (`model or self._thermal_model`): every ThermalModel's `compute_cop` is the same `_cop_law`, so the second arm is still unreachable.",
-  "verdict": "equivalent"
-}
diff --git a/tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CLAMP_DROP.b267b48b.json b/tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CLAMP_DROP.b267b48b.json
new file mode 100644
index 000000000..d5657511e
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._capacity_caps.CLAMP_DROP.b267b48b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._capacity_caps CLAMP_DROP b267b48b",
+  "old": "            cop_i = max(model.compute_cop(float(outdoor), humidity=hum), 1e-6)",
+  "reason": "Re-keyed from 33200ef3 by R10-COP-PARTLOAD p2 round 2 (`model = model or self._thermal_model` hoisted above the loop). `max(compute_cop(...), 1e-6)` cannot select the second arm: `compute_cop` returns `_cop_law`, which returns `max(cop, 1.0)` (#928's resistive bound), on every ThermalModel.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._dhw_setpoint_sweep.CLAMP_DROP.67c35b2c.json b/tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._dhw_setpoint_sweep.CLAMP_DROP.67c35b2c.json
new file mode 100644
index 000000000..73476e903
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._dhw_setpoint_sweep.CLAMP_DROP.67c35b2c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._dhw_setpoint_sweep CLAMP_DROP 67c35b2c",
+  "old": "            cop = max(float(self._thermal_model.compute_cop_dhw(outdoor, t)), 0.5)",
+  "reason": "Equivalent: `cop` is `compute_cop_dhw`, which returns `ThermalModel._cop_law`, whose last line is `return max(cop, 1.0)`; the 0.5 floor can never bind on a finite COP, and on a NaN one `max(nan, 0.5)` is the NaN either way. The line's text changed only because R10-COP-PARTLOAD part 2 joined its wrapped call onto one line; the clamp itself is the base's.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._plan_dhw_min_cost.CLAMP_DROP.957b7a47.json b/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._plan_dhw_min_cost.CLAMP_DROP.957b7a47.json
new file mode 100644
index 000000000..25e2ea96d
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._plan_dhw_min_cost.CLAMP_DROP.957b7a47.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._plan_dhw_min_cost CLAMP_DROP 957b7a47",
+  "old": "            energy_max = np.maximum(cop * heat_per_cop_kw(params, p_dhw_max) * dt, 1e-9)",
+  "reason": "Equivalent in output: the 1e-9 floor differs from no floor only where `cop * heat_per_cop_kw(params, p_dhw_max) * dt` is 0, i.e. `p_dhw_max == 0` (COP is at least 1 and dt positive). There the LP may place up to 1e-9 kWh, and the back-conversion clips every step to [0, p_dhw_max] = 0, so the plan, and the refine pass's simulation of it, are the same array. The floor is the base's; R10-COP-PARTLOAD part 2 changed only its product's first factor.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._repair_dhw_floor.CLAMP_DROP.19b8216c.json b/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._repair_dhw_floor.CLAMP_DROP.19b8216c.json
new file mode 100644
index 000000000..f4b3b5308
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._repair_dhw_floor.CLAMP_DROP.19b8216c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._repair_dhw_floor CLAMP_DROP 19b8216c",
+  "old": "                    params, plan[j], float(room_c[j_local]) * c_dhw / max(dt * cop_room, 1e-6))",
+  "reason": "Re-keyed from 21bb873a by R10-COP-PARTLOAD p2 round 2 (the quotient became `added_power_for_heat_per_cop_kw`'s argument). `cop_room = max(cop_j, compute_cop_dhw(...))` and `cop_j = max(marginal_cop(...), 0.5)`, so `dt * cop_room >= 0.5 * dt`, which exceeds 1e-6 for any step longer than 2e-6 h; the planner's step is 0.25 h. The max cannot select its second arm.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._repair_dhw_floor.CLAMP_DROP.21bb873a.json b/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._repair_dhw_floor.CLAMP_DROP.21bb873a.json
deleted file mode 100644
index cf32cc621..000000000
--- a/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._repair_dhw_floor.CLAMP_DROP.21bb873a.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._repair_dhw_floor CLAMP_DROP 21bb873a",
-  "old": "                room_kw = float(room_c[j_local]) * c_dhw / max(dt * cop_room, 1e-6)",
-  "reason": "drawn by the round-7 D2-03 diff's per-file sample over optimizer.py. In `_repair_dhw_floor`, `cop_room = max(cop_j, compute_cop_dhw(...))` and `cop_j = max(marginal_cop(...), 0.5)`, so `dt * cop_room >= 0.5 * dt`, which exceeds 1e-6 for any step longer than 2e-6 h. The planner's step is `time_step_minutes / 60` = 0.25 h. The max cannot select its second arm.",
-  "verdict": "equivalent"
-}
diff --git a/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._repair_dhw_floor.CLAMP_DROP.eb4ca0bc.json b/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._repair_dhw_floor.CLAMP_DROP.eb4ca0bc.json
new file mode 100644
index 000000000..b2ca925f0
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/dhw_planner.py/DhwPlanner._repair_dhw_floor.CLAMP_DROP.eb4ca0bc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._repair_dhw_floor CLAMP_DROP eb4ca0bc",
+  "old": "                    params, plan[j], float(deficit[b]) * c_dhw / max(dt * cop_j, 1e-6))",
+  "reason": "R10-COP-PARTLOAD p2 round 2 moved this quotient into `added_power_for_heat_per_cop_kw`'s argument. `cop_j = max(marginal_cop(...), 0.5)`, so `dt * cop_j >= 0.5 * dt`, which exceeds 1e-6 for any step longer than 2e-6 h; the planner's step is `time_step_minutes / 60` = 0.25 h. The max cannot select its second arm.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._tighten_buffer_caps.CLAMP_DROP.53178fd6.json b/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._tighten_buffer_caps.CLAMP_DROP.53178fd6.json
new file mode 100644
index 000000000..ba5634306
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._tighten_buffer_caps.CLAMP_DROP.53178fd6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._tighten_buffer_caps CLAMP_DROP 53178fd6",
+  "old": "                self.model.params, float(schedule[i]), -float(refused[i]) / max(cop_i, 1e-6))",
+  "reason": "R10-COP-PARTLOAD p2 round 2 moved this quotient into `added_power_for_heat_per_cop_kw`'s argument; the clamp is the old line's. `cop_i = marginal_cop(..., \"buffer\", ...)`, which is `compute_cop(..., flow_temp=...)`, which returns `_cop_law`'s `max(cop, 1.0)` (#928's resistive bound), so `max(cop_i, 1e-6)` cannot select its second arm.",
+  "verdict": "equivalent"
+}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index f735922a4..ad931aedd 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17656,
+ "class_excess_loc": 17654,
  "const_modules_over_50": 3,
  "coordinator_attrs": 142,
  "coordinator_multiassigned_attrs": 109,
@@ -11,11 +11,11 @@
  "functions_cc_over_25": 8,
  "import_cycle_modules": 0,
  "max_cc": 44,
- "max_class_loc": 8061,
+ "max_class_loc": 8060,
  "max_method_loc": 373,
  "methods_over_150": 15,
  "methods_over_200": 8,
  "name_kept_members": 38,
- "recorded_at": "5d4e0bcfb88413ddf9ca7f0884c36bbec9235447",
+ "recorded_at": "be7584c4904e243ffb48c166be39221623d81415",
  "seam_cut_total": 422
 }

