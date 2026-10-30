# Review packet #3006
head: dfb981d7a0066c472ef408467a88630e77227f70
base: cf4f6b7a660f5b61e0f2b933bd18647fe3ba90c7

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124218334751 neutral
arch-score / arch-score id=124217877145 queued
arm id=124219210921 skipped
budget-raise-gate / budget-raise-gate id=124217877259 queued
cancel-superseded id=124217005475 queued
codeql / Analyze (actions) id=124217877161 queued
codeql / Analyze (javascript-typescript) id=124217877166 queued
codeql / Analyze (python) id=124217877150 queued
governance / delivery-status id=124217877351 queued
governance / env-matrix id=124217877255 queued
governance / instrument-self-tests id=124217877316 queued
governance / policy-docs id=124217877339 queued
governance / wave-script id=124217877569 queued
hassfest / hassfest id=124217877051 queued
prelude id=124217005619 queued
refresh id=124217005802 queued
tests / arch-instrument id=124219989452 queued
tests / briefs id=124217877266 queued
tests / browser id=124219989259 queued
tests / closure-scope id=124217877267 queued
tests / closures id=124219989366 queued
tests / coverage id=124219989289 queued
tests / fast (3.14) id=124219989371 queued
tests / mutation id=124217877236 queued
tests / nightly-status id=124217877230 queued
tests / replay id=124219989404 queued
tests / typing id=124219989426 queued
validate / validate-hacs id=124217877202 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE stale tree: dfb981d7a0066c472ef408467a88630e77227f70 lacks origin/main cc930cdd1a3cfb005ba7ec557f4451ff5e53e364; roster read at origin/main
NOTE body item dccf1c30: R10-COP-PARTLOAD
NOTE body item bee4b506: R10-COP-PARTLOAD
NOTE body item 23f0d5d1: dismissed:a session-local plugin, not repository policy
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         node tools/policy/rules_sync.mjs --check
             `tools/policy/rules_sync.mjs` is in the tree at this head
  ok         tests/stress.py
             `tests/stress.py` is in the tree at this head
  ok         python3 tests/structure.py --record
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff 507a9ec264eb373b132248d752259254d8a9fa4d HEAD
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_buffer_store.py bench 3
             `dev/audit/harnesses/r10_buffer_store.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 -u tests/features.py
             `tests/features.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 -u dev/audit/harnesses/r10_cop_partload.py
             `dev/audit/harnesses/r10_cop_partload.py` is in the tree at this head

FIGURES: 12 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
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


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index 88ac5122a..2fdc19e08 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -338,6 +338,7 @@ from .thermal_model import (
     planned_draw_runs,
     probe_install,
     reanchor_heat_loss,
+    power_for_heat_per_cop_kw,
 )
 from .dhw_schedule import (
     DHWWindowError,
@@ -4084,10 +4085,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
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
diff --git a/custom_components/heatpump_optimizer/dhw_planner.py b/custom_components/heatpump_optimizer/dhw_planner.py
index 05b9c16ae..ce99569e2 100644
--- a/custom_components/heatpump_optimizer/dhw_planner.py
+++ b/custom_components/heatpump_optimizer/dhw_planner.py
@@ -48,6 +48,9 @@ from .thermal_model import (
     _step_humidity,
     dhw_coil_draw_reduction,
     dhw_draw_scale,
+    delivered_heat_kw,
+    heat_per_cop_kw,
+    power_for_heat_per_cop_kw,
 )
 
 _LOGGER = logging.getLogger(__name__)
@@ -1441,7 +1444,7 @@ class DhwPlanner:
 
         best: np.ndarray | None = None
         for _ in range(2):
-            energy_max = np.maximum(p_dhw_max * cop * dt, 1e-9)
+            energy_max = np.maximum(cop * heat_per_cop_kw(params, p_dhw_max) * dt, 1e-9)
             # Shortfall slack keeps the program feasible when the requirement
             # simply cannot be met (cold start, undersized pump); it is priced
             # far above any real electricity cost so it is only ever used as a
@@ -1506,7 +1509,9 @@ class DhwPlanner:
             if solution is None:  # pragma: no cover - success implies a vector
                 return best
             energy = np.asarray(solution[:n_steps], dtype=float)
-            best = np.clip(energy / (cop * dt), 0.0, p_dhw_max)
+            best = np.clip(
+                power_for_heat_per_cop_kw(params, energy / (cop * dt)), 0.0, p_dhw_max
+            )
 
             # Refine the COP estimate against the tank temperatures this plan
             # actually produces, so the cost ranking reflects reality.
@@ -1872,7 +1877,9 @@ class DhwPlanner:
             q_draw = float(draw_rates[i]) * dhw_draw_scale(temp, inlet)
             q_loss = ua * (temp - TANK_ROOM_AMBIENT_TEMP)
             headroom_c = float(ceiling[i]) - temp
-            allowed = (headroom_c * capacity / dt + q_draw + q_loss) / cop
+            allowed = power_for_heat_per_cop_kw(
+                params, (headroom_c * capacity / dt + q_draw + q_loss) / cop
+            )
             plan[i] = float(np.clip(plan[i], 0.0, max(0.0, allowed)))
 
             # Stepped through the same simulation the planners use, so the
@@ -1880,7 +1887,7 @@ class DhwPlanner:
             temp = float(
                 self.model.simulate_dhw_step(
                     dhw_temp=temp,
-                    dhw_power_thermal=cop * plan[i],
+                    dhw_power_thermal=delivered_heat_kw(params, cop, plan[i]),
                     hour_of_day=0.0,
                     dt_hours=dt,
                     draw_power=float(draw_rates[i]),
diff --git a/custom_components/heatpump_optimizer/optimizer.py b/custom_components/heatpump_optimizer/optimizer.py
index 1de730eb3..d629361c7 100644
--- a/custom_components/heatpump_optimizer/optimizer.py
+++ b/custom_components/heatpump_optimizer/optimizer.py
@@ -106,6 +106,7 @@ from .thermal_model import (
     valve_charge_demand,
     weather_or_calm,
     wood_share,
+    power_for_heat_per_cop_kw,
 )
 from .tariff import (
     CapacityTariff,
@@ -5335,7 +5336,7 @@ class HeatPumpOptimizer:
             # power is what determines energy use; a clamp burnt
             # min_electrical_power * 24 h per day on a house needing no heat.
             # Nor a clip at 0: the demand is floored at 0 above, the COP at 1.
-            power = min(required_thermal / cop, p.max_electrical_power)
+            power = min(power_for_heat_per_cop_kw(p, required_thermal / cop), p.max_electrical_power)
             baseline_power[i] = power
 
             state = self.model.simulate_step(
diff --git a/custom_components/heatpump_optimizer/thermal_model.py b/custom_components/heatpump_optimizer/thermal_model.py
index bfa379dd3..f19e2fb3b 100644
--- a/custom_components/heatpump_optimizer/thermal_model.py
+++ b/custom_components/heatpump_optimizer/thermal_model.py
@@ -2090,6 +2090,40 @@ def heat_per_cop_kw(params: ThermalParameters, electrical_power: Any) -> Any:
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
 def delivered_heat_kw(params: ThermalParameters, cop: Any, electrical_power: Any) -> Any:
     """Heat the pump delivers at ``cop`` and ``electrical_power``, space or hot
     water: ``cop`` times :func:`heat_per_cop_kw`, the one association every
@@ -3332,9 +3366,7 @@ class ThermalModel:
         T_buf = state.buffer_tank_temperature
 
         # --- Buffer tank dynamics ---
-        C_buf = p.buffer_tank_thermal_mass
-        if C_buf < 1e-6:
-            C_buf = 0.04  # fallback for 35L
+        C_buf = _buffer_capacity(p)
 
         rad_fraction = p.radiator_power_fraction
 
@@ -3950,9 +3982,7 @@ class ThermalModel:
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
diff --git a/tests/features.py b/tests/features.py
index d82394cf4..d4e1e71b2 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -72619,6 +72619,151 @@ R.check(
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
 # --- #2261: a delivered-heat counter, the mode dwell and one attribution --------
 # R10-HEAT-METER. A ``total_increasing`` kWh counter of the heat the pump
 # delivered is read per span (``heat_energy.HeatEnergyMeter``), the span closing
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
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index a81608f11..4ef2ff226 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17672,
+ "class_excess_loc": 17671,
  "const_modules_over_50": 3,
  "coordinator_attrs": 142,
  "coordinator_multiassigned_attrs": 109,
@@ -11,11 +11,11 @@
  "functions_cc_over_25": 8,
  "import_cycle_modules": 0,
  "max_cc": 44,
- "max_class_loc": 8065,
+ "max_class_loc": 8064,
  "max_method_loc": 373,
  "methods_over_150": 15,
  "methods_over_200": 8,
  "name_kept_members": 38,
- "recorded_at": "88c6ad5bbec69bfe157e04597a74d0c9c3e4775c",
+ "recorded_at": "507a9ec264eb373b132248d752259254d8a9fa4d",
  "seam_cut_total": 422
 }

