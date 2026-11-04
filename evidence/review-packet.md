# Review packet #3193
head: af8ff29be58edf8c15eb146c9d9432be60899e23
base: d7582ed404a87603bd02fefda610d7ebbe4181e1

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=126802055372 neutral
arch-score / arch-score id=126801625779 success
arm id=126801349719 skipped
budget-raise-gate / budget-raise-gate id=126801625891 success
cancel-superseded id=126801359297 success
codeql / Analyze (actions) id=126801625620 success
codeql / Analyze (javascript-typescript) id=126801625630 success
codeql / Analyze (python) id=126801625597 in_progress
governance / delivery-status id=126801625992 success
governance / delivery-status-publish id=126801628317 skipped
governance / env-matrix id=126801625887 success
governance / instrument-self-tests id=126801625820 in_progress
governance / policy-docs id=126801626004 success
governance / record id=126801628016 skipped
governance / wave-script id=126801625685 success
hassfest / hassfest id=126801625972 success
kernel-points id=126801627328 skipped
prelude id=126801358768 success
refresh id=126801359352 success
tests / arch-instrument id=126802013206 in_progress
tests / briefs id=126801626000 success
tests / browser id=126802013302 success
tests / closure-scope id=126801625825 success
tests / closures id=126802013253 in_progress
tests / coverage id=126802013123 in_progress
tests / fast (3.14) id=126802013116 in_progress
tests / mutation id=126801625869 in_progress
tests / nightly-ha id=126802016972 skipped
tests / nightly-status id=126801625776 failure
tests / replay id=126802013348 failure
tests / typing id=126802013185 success
validate / validate-hacs id=126801625806 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_cop_gate_top.py
             `dev/audit/harnesses/r10_cop_gate_top.py` is in the tree at this head
  ok         tests/features.py
             `tests/features.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  unverified git grep -n max_electrical_power -- custom_components
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift bash tests/run.sh
             `tests/run.sh` is in the tree at this head

FIGURES: 5 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_manual_release.GUARD_OFF.e973f3a4.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_manual_release.GUARD_OFF.e973f3a4.json
deleted file mode 100644
index 2d5f00ffc..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_manual_release.GUARD_OFF.e973f3a4.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._record_manual_release GUARD_OFF e973f3a4",
-  "killed_by": "tests/features.py",
-  "old": "        if override is None:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_band_fields.GUARD_OFF.7ead7e8a.json b/tests/mutation_ledger/killed_by/coordinator.py/_band_fields.GUARD_OFF.7ead7e8a.json
new file mode 100644
index 000000000..254991df7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_band_fields.GUARD_OFF.7ead7e8a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_band_fields GUARD_OFF 7ead7e8a",
+  "killed_by": "tests/features.py",
+  "old": "    if band.source == \"configured\":",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_band_fields.RETURN_DEL.b3c33916.json b/tests/mutation_ledger/killed_by/coordinator.py/_band_fields.RETURN_DEL.b3c33916.json
new file mode 100644
index 000000000..8600e5843
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_band_fields.RETURN_DEL.b3c33916.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_band_fields RETURN_DEL b3c33916",
+  "killed_by": "tests/features.py",
+  "old": "    return {\"max_electrical_power\": band.max_kw, \"min_electrical_power\": band.min_kw}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_record_manual_release.GUARD_OFF.8dc0f9a5.json b/tests/mutation_ledger/killed_by/coordinator.py/_record_manual_release.GUARD_OFF.8dc0f9a5.json
new file mode 100644
index 000000000..ab16b5169
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_record_manual_release.GUARD_OFF.8dc0f9a5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_record_manual_release GUARD_OFF 8dc0f9a5",
+  "killed_by": "tests/features.py",
+  "old": "    if override is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_solve_band.RETURN_DEL.0d061913.json b/tests/mutation_ledger/killed_by/coordinator.py/_solve_band.RETURN_DEL.0d061913.json
new file mode 100644
index 000000000..62ac6506d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_solve_band.RETURN_DEL.0d061913.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_solve_band RETURN_DEL 0d061913",
+  "killed_by": "tests/features.py",
+  "old": "    return draw_range.solve_band(draw, hub, probe_install(config), dt_util.now().timestamp())",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/solve_band.CLAMP_DROP.4d045bab.json b/tests/mutation_ledger/killed_by/draw_range.py/solve_band.CLAMP_DROP.4d045bab.json
new file mode 100644
index 000000000..2094357ea
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/solve_band.CLAMP_DROP.4d045bab.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:solve_band CLAMP_DROP 4d045bab",
+  "killed_by": "tests/features.py",
+  "old": "        cfg_max, learned, min(cfg_min, learned), \"ceiling_probe\",",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`cfg_max, learned, (cfg_min), \"ceiling_probe\",`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/solve_band.CMP_BOUND.87d22127.json b/tests/mutation_ledger/killed_by/draw_range.py/solve_band.CMP_BOUND.87d22127.json
new file mode 100644
index 000000000..46dbbfa1b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/solve_band.CMP_BOUND.87d22127.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:solve_band CMP_BOUND 87d22127",
+  "killed_by": "tests/features.py",
+  "old": "        return configured(\"lapsed\" if samples >= CEILING_MIN_SAMPLES else \"awaiting_probe\")",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return configured(\"lapsed\" if samples > CEILING_MIN_SAMPLES else \"awaiting_probe\")`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/solve_band.CMP_BOUND.d82c7c5e.json b/tests/mutation_ledger/killed_by/draw_range.py/solve_band.CMP_BOUND.d82c7c5e.json
new file mode 100644
index 000000000..82ecadf88
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/solve_band.CMP_BOUND.d82c7c5e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:solve_band CMP_BOUND d82c7c5e",
+  "killed_by": "tests/features.py",
+  "old": "    if learned >= (1.0 - AGREE_TOLERANCE) * cfg_max:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if learned > (1.0 - AGREE_TOLERANCE) * cfg_max:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/solve_band.GUARD_OFF.42b5905c.json b/tests/mutation_ledger/killed_by/draw_range.py/solve_band.GUARD_OFF.42b5905c.json
new file mode 100644
index 000000000..7bd638b28
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/solve_band.GUARD_OFF.42b5905c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:solve_band GUARD_OFF 42b5905c",
+  "killed_by": "tests/features.py",
+  "old": "    if learned is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/solve_band.GUARD_OFF.6a6c4f30.json b/tests/mutation_ledger/killed_by/draw_range.py/solve_band.GUARD_OFF.6a6c4f30.json
new file mode 100644
index 000000000..82783c6d8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/solve_band.GUARD_OFF.6a6c4f30.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:solve_band GUARD_OFF 6a6c4f30",
+  "killed_by": "tests/features.py",
+  "old": "    if cap.plan_writes_power():",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/solve_band.GUARD_OFF.d82c7c5e.json b/tests/mutation_ledger/killed_by/draw_range.py/solve_band.GUARD_OFF.d82c7c5e.json
new file mode 100644
index 000000000..6964d34b8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/solve_band.GUARD_OFF.d82c7c5e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:solve_band GUARD_OFF d82c7c5e",
+  "killed_by": "tests/features.py",
+  "old": "    if learned >= (1.0 - AGREE_TOLERANCE) * cfg_max:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._warm_start_starts.CLAMP_DROP.e8734c97.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._warm_start_starts.CLAMP_DROP.e8734c97.json
new file mode 100644
index 000000000..a52ca6caa
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._warm_start_starts.CLAMP_DROP.e8734c97.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._warm_start_starts CLAMP_DROP e8734c97",
+  "killed_by": "tests/features.py",
+  "old": "        return (np.clip(np.asarray(prev, dtype=float), 0.0, self.model.params.max_electrical_power),)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return ((np.asarray(prev, dtype=float)),)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._warm_start_starts.RETURN_DEL.e8734c97.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._warm_start_starts.RETURN_DEL.e8734c97.json
new file mode 100644
index 000000000..1a9f3e689
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._warm_start_starts.RETURN_DEL.e8734c97.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._warm_start_starts RETURN_DEL e8734c97",
+  "killed_by": "tests/features.py",
+  "old": "        return (np.clip(np.asarray(prev, dtype=float), 0.0, self.model.params.max_electrical_power),)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_band_kw.BOOLOP.55c98a93.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_band_kw.BOOLOP.55c98a93.json
new file mode 100644
index 000000000..3bb523ee5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_band_kw.BOOLOP.55c98a93.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_band_kw BOOLOP 55c98a93",
+  "killed_by": "tests/features.py",
+  "old": "    if band and _experiment_kw(inp) is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if band or _experiment_kw(inp) is None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_band_kw.GUARD_OFF.55c98a93.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_band_kw.GUARD_OFF.55c98a93.json
new file mode 100644
index 000000000..be3a2c8dc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_band_kw.GUARD_OFF.55c98a93.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_band_kw GUARD_OFF 55c98a93",
+  "killed_by": "tests/features.py",
+  "old": "    if band and _experiment_kw(inp) is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index eb26be357..b337f865f 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -2174,6 +2174,9 @@ class SolveRecord:
     config: OptimizationConfig
     params: ThermalParameters
     inputs: SolveInputs
+    #: The band ``params`` books (``draw_range.solve_band``), stamped on the
+    #: plan this record solves so the arbiter maps it by the same band.
+    band: draw_range.SolveBand
 
     def optimizer(self) -> HeatPumpOptimizer:
         return HeatPumpOptimizer(ThermalModel(self.params), self.config)
@@ -2221,6 +2224,38 @@ def _sweep_price(kwh_price: float | None, prices: list[dict[str, Any]]) -> float
     return level if level > 1e-6 else max(abs(level), 0.1)
 
 
+def _solve_band(draw: draw_range.DrawRange, hub: ThermalParameters, config: Any) -> draw_range.SolveBand:
+    """This moment's ``draw_range.solve_band`` from the hub and the store."""
+    return draw_range.solve_band(draw, hub, probe_install(config), dt_util.now().timestamp())
+
+
+def _band_fields(band: draw_range.SolveBand) -> dict[str, float]:
+    """The solve copy's power range under ``band``; none where configured,
+    so a configured band leaves the copy the hub's figures byte for byte."""
+    if band.source == "configured":
+        return {}
+    return {"max_electrical_power": band.max_kw, "min_electrical_power": band.min_kw}
+
+
+def _record_manual_release(
+    result: "OptimizationResult", override: "ManualOverride | None"
+) -> None:
+    """Fold the solve's safety releases onto the override it pinned (#1754).
+
+    ``override`` is the one this solve's pins were built from, captured
+    before the await and passed by identity; reading the live
+    ``self._manual_override`` here let a mid-solve swap inherit them.
+    """
+    if override is None:
+        return
+    override.released_space = [
+        {"step": i, "reason": "safety"} for i in result.manual_released_space
+    ]
+    override.released_dhw = [
+        {"step": i, "reason": "safety"} for i in result.manual_released_dhw
+    ]
+
+
 def _whatif_banded(state: Any) -> bool:
     """Whether the card's what-if plans with the away setback (R9-UX-5).
 
@@ -5941,7 +5976,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             _raise_update_failed("update_failed", f"Error updating data: {err}", err, error=str(err))
 
     def _solve_hubs(
-        self, n_steps: int, *, banded: bool
+        self, n_steps: int, *, banded: bool, band: draw_range.SolveBand | None = None
     ) -> tuple[OptimizationConfig, ThermalParameters, ThermalState]:
         """Private copies of the three hubs with this moment's solve values.
 
@@ -5994,6 +6029,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             **dhw_bands,
             **self._model_corrections(now),
             **self._dhw_plan_fields(now),
+            **_band_fields(band or _solve_band(self._accuracy.draw, ctx._thermal_params, ctx._config)),
         )
         state = replace(
             copy.deepcopy(ctx._current_state),
@@ -6025,7 +6061,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         """
         ctx = getattr(self, "_ctx", self)
         n = len(horizon.prices)
-        config, params, state = self._solve_hubs(n, banded=True)
+        band = _solve_band(self._accuracy.draw, ctx._thermal_params, ctx._config)
+        config, params, state = self._solve_hubs(n, banded=True, band=band)
         space_pins, dhw_pins = self._manual_pins(solve_now, n)
         # The opt-in fuse guard (#3): a hard per-step ceiling on heat pump
         # power at what the fuse leaves after the rest of the house.
@@ -6080,7 +6117,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
                 off_steps=quiet.off_steps,
                 quiet_actions=quiet.actions,
             ),
-        ))
+        ), band)
 
     async def async_run_optimization(self) -> str | None:
         """Run the MPC optimization.
@@ -6192,9 +6229,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
                     f"solver returned a failed plan: {result.status}"
                 )
 
-            self._record_manual_release(result, pinned_override)
+            _record_manual_release(result, pinned_override)
 
-            self._optimization_result = result
+            self._optimization_result = replace(result, solve_band=record.band.as_dict())
             self._last_optimization = dt_util.now()
             if self._solve_failures >= SOLVE_FAILURE_ISSUE_COUNT:
                 ir.async_delete_issue(self.hass, DOMAIN, "solve_failures")
@@ -7742,6 +7779,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             "measured_cop": self._measured_cop.cop,
             "measured_cop_at": None if self._measured_cop.at is None else self._measured_cop.at.isoformat(),
             "cop_refusal": self._measured_cop.refusal,
+            "pump_max_power": getattr(self._optimization_result, "solve_band", None) or None,
             "cop_observability": cop_observability(
                 electric=install.cop_electric(), measured_heat=install.measured_heat,
                 follows=draw_range.follows_ask(self._accuracy.draw),
@@ -8293,24 +8331,6 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             np.array(dhw, dtype=float) if dhw is not None else None,
         )
 
-    def _record_manual_release(
-        self, result: "OptimizationResult", override: "ManualOverride | None"
-    ) -> None:
-        """Fold the solve's safety releases onto the override it pinned (#1754).
-
-        ``override`` is the one this solve's pins were built from, captured
-        before the await and passed by identity; reading the live
-        ``self._manual_override`` here let a mid-solve swap inherit them.
-        """
-        if override is None:
-            return
-        override.released_space = [
-            {"step": i, "reason": "safety"} for i in result.manual_released_space
-        ]
-        override.released_dhw = [
-            {"step": i, "reason": "safety"} for i in result.manual_released_dhw
-        ]
-
     def _manual_plan_state(self) -> ManualPlan | None:
         """The override state the plan sensors expose, or ``None`` when inactive.
 
diff --git a/custom_components/heatpump_optimizer/draw_range.py b/custom_components/heatpump_optimizer/draw_range.py
index 125266a5e..6615fa7a4 100644
--- a/custom_components/heatpump_optimizer/draw_range.py
+++ b/custom_components/heatpump_optimizer/draw_range.py
@@ -7,13 +7,14 @@ maximum is several times its real running draw had every plan book levels it
 never reached, and the heat they were credited with was never delivered.
 
 ``DrawRange`` keeps the running samples -- the metered draw beside the space
-level the plan asked for -- and answers one question: the range the plan
-may book. Until there is evidence the configured figures stand; with it, the
-plan is clamped to the metered range. ``is_running_space`` is the one
-filter saying which intervals are running samples, from values the
-coordinator reads (it alone can see the meter, the freezes, a resistive
-element and the defrost window); ``planned_range`` is the one answer to
-which installs the clamp applies to and how far. Nothing here takes the
+level the plan asked for -- and judges whether the plan and the meter
+disagree (``engaged``); ``planned_range`` is the metered range that judgement
+would clamp to, published in diagnostics and read by no solve. The range a
+solve books is ``solve_band``'s: the configured figures, or the ceiling
+store's learned top where the experiment metered the pump below them.
+``is_running_space`` is the one filter saying which intervals are running
+samples, from values the coordinator reads (it alone can see the meter, the
+freezes, a resistive element and the defrost window). Nothing here takes the
 coordinator.
 
 **Why evidence, and a latch.** A pump in mild weather runs well below its
@@ -560,10 +561,12 @@ def fold(
 def planned_range(
     draw: DrawRange, params: Any, cap: InstallCapability
 ) -> tuple[float, float] | None:
-    """The effective ``(min, max)`` a solve may book, or ``None``.
+    """The window's latched ``(min, max)``, or ``None``: diagnostics only.
 
-    ``None`` -- the configured figures stand -- until ``draw`` has the
-    evidence, and always where the plan writes the power itself
+    No solve reads it: the range a solve books is ``solve_band``'s. Kept as
+    the window's view beside the ceiling store's in ``diagnostics_view``.
+
+    ``None`` until ``draw`` has the evidence, and always where the plan writes the power itself
     (``plan_writes_power``): there the metered draw is the plan's own echo.
     On an install that can duty-cycle the min end stays configured: a level
     below it is an average over the step, which a pump running at its metered
@@ -595,3 +598,71 @@ def diagnostics_view(
     view["effective_max_kw"] = None if effective is None else round(effective[1], 3)
     view["learned_max_kw"] = None if learned is None else round(learned, 3)
     return view
+
+
+@dataclass(frozen=True)
+class SolveBand:
+    """The draw range one solve books, and which top it used and why.
+
+    The coordinator computes it once per solve and stamps it on the plan
+    (``OptimizationResult.solve_band``), so the arbiter maps a plan's steps
+    by the band they were solved on, never a recomputed one.
+    """
+
+    configured_max_kw: float
+    max_kw: float
+    min_kw: float
+    source: str
+    reason: str
+    #: The learned top (or the store's sample count while awaiting it) and
+    #: the newest sample's epoch seconds: the reason's evidence.
+    learned_max_kw: float | None = None
+    samples: int = 0
+    since_s: float | None = None
+
+    def as_dict(self) -> dict[str, Any]:
+        return {
+            "configured_max_kw": round(self.configured_max_kw, 3),
+            "planned_max_kw": round(self.max_kw, 3),
+            "planned_min_kw": round(self.min_kw, 3),
+            "source": self.source,
+            "reason": self.reason,
+            "learned_max_kw": None if self.learned_max_kw is None else round(self.learned_max_kw, 3),
+            "samples": self.samples,
+            "since_s": self.since_s,
+        }
+
+
+def solve_band(
+    draw: DrawRange, params: Any, cap: InstallCapability, now_s: float
+) -> SolveBand:
+    """The ``(min, max)`` a solve books: the configured figures, or the
+    ceiling store's learned top where it measured the pump below them.
+
+    The top only ever comes down (a learned top above the configured one
+    books the configured one: less heat, never fictional heat), and only by
+    more than ``AGREE_TOLERANCE``, so a correctly configured pump keeps its
+    figures. The bottom end never moves except to stay at or under the top.
+    Where the plan writes the power itself the draw is the plan's echo and
+    the configured figures stand. The hub keeps the configured figures: a
+    caller applies ``max_kw`` and ``min_kw`` to its solve copy only.
+    """
+    cfg_min = float(params.min_electrical_power)
+    cfg_max = float(params.max_electrical_power)
+    since = draw.ceiling_since()
+    samples = len(draw.ceiling)
+
+    def configured(reason: str, learned: float | None = None) -> SolveBand:
+        return SolveBand(cfg_max, cfg_max, cfg_min, "configured", reason, learned, samples, since)
+
+    if cap.plan_writes_power():
+        return configured("plan_writes_power")
+    learned = draw.learned_max_kw(now_s)
+    if learned is None:
+        return configured("lapsed" if samples >= CEILING_MIN_SAMPLES else "awaiting_probe")
+    if learned >= (1.0 - AGREE_TOLERANCE) * cfg_max:
+        return configured("not_below_configured", learned)
+    return SolveBand(
+        cfg_max, learned, min(cfg_min, learned), "ceiling_probe",
+        "measured_below_configured", learned, samples, since,
+    )
diff --git a/custom_components/heatpump_optimizer/optimizer.py b/custom_components/heatpump_optimizer/optimizer.py
index 6814f859d..391e98e62 100644
--- a/custom_components/heatpump_optimizer/optimizer.py
+++ b/custom_components/heatpump_optimizer/optimizer.py
@@ -1785,6 +1785,10 @@ class OptimizationResult:
     #: Absent (None) keeps ``step_duty``'s duty-cycle reading. Not a
     #: caller argument: the plan carries the floor it was solved under.
     duty_floor_kw: float | None = None
+    #: ``draw_range.SolveBand.as_dict()`` of the band this plan was solved
+    #: on, stamped by the coordinator; empty means the hub's configured band.
+    #: The arbiter maps the plan's steps by it (R10-COP-GATE part D).
+    solve_band: dict[str, Any] = field(default_factory=dict)
 
 
 @dataclass
@@ -3715,12 +3719,15 @@ class HeatPumpOptimizer:
         A different step count means the caller is planning a different
         horizon (the coordinator's own horizon is fixed, but a service call or
         a test need not match it), and a plan of the wrong width is dropped
-        rather than clipped or padded into a plausible-looking guess.
+        rather than clipped or padded into a plausible-looking guess. Its
+        levels are clipped to this solve's top: a band narrowed since the
+        previous plan (R10-COP-GATE part D, item D6) would otherwise score the
+        candidate at levels this solve cannot book.
         """
         prev = getattr(self, "_prev_shipped_plan", None)
         if prev is None or len(prev) != n_steps:
             return None
-        return (np.asarray(prev, dtype=float),)
+        return (np.clip(np.asarray(prev, dtype=float), 0.0, self.model.params.max_electrical_power),)
 
     def _stash_price_horizon(
         self,
diff --git a/custom_components/heatpump_optimizer/payload.py b/custom_components/heatpump_optimizer/payload.py
index 5d9a01055..aba9b11ad 100644
--- a/custom_components/heatpump_optimizer/payload.py
+++ b/custom_components/heatpump_optimizer/payload.py
@@ -812,6 +812,8 @@ class LearningView(TypedDict, total=False):
     #: and ``accuracy.cop_observability`` (#2262).
     measured_cop_at: str | None
     cop_refusal: str | None
+    #: ``draw_range.SolveBand.as_dict()`` stamped on the live plan, or None.
+    pump_max_power: dict[str, Any] | None
     cop_observability: str
     defrost_derate: float
     defrost_samples: int
diff --git a/custom_components/heatpump_optimizer/pump_arbiter.py b/custom_components/heatpump_optimizer/pump_arbiter.py
index 13459a804..9d5c31835 100644
--- a/custom_components/heatpump_optimizer/pump_arbiter.py
+++ b/custom_components/heatpump_optimizer/pump_arbiter.py
@@ -504,7 +504,17 @@ def _experiment_kw(inp: ArbiterInputs) -> float | None:
 
 
 def _band_kw(inp: ArbiterInputs) -> tuple[Any, Any]:
-    """``(p_min, p_max)`` from the model when the params snapshot lacks them."""
+    """``(p_min, p_max)`` the step's power maps on.
+
+    A plan's step maps on the band the plan was solved on, its stamped
+    ``solve_band`` (R10-COP-GATE part D): a plan booked on a learned top
+    below the nameplate commands the ceiling at that top. An experiment's
+    step maps on the hub's band, which sysid sized it on; so does a plan with
+    no stamp. The hub's band from the model when the params snapshot lacks it.
+    """
+    band = getattr(inp.plan, "solve_band", None) or {}
+    if band and _experiment_kw(inp) is None:
+        return band["planned_min_kw"], band["planned_max_kw"]
     params = inp.params
     thermal_params = getattr(inp.thermal, "params", None)
     p_min = getattr(params, "min_electrical_power", None)
diff --git a/custom_components/heatpump_optimizer/sensor.py b/custom_components/heatpump_optimizer/sensor.py
index e477c2bc0..3375c846a 100644
--- a/custom_components/heatpump_optimizer/sensor.py
+++ b/custom_components/heatpump_optimizer/sensor.py
@@ -2044,9 +2044,24 @@ class ModelStatusSensor(HeatPumpOptimizerSensorBase):
             "system_identification": data.get("system_identification"),
             "system_identification_outcome": _sysid_outcome(data.get("system_identification")),
             "learner_progress": data.get("learner_progress"),
+            **_pump_max_power(data.get("pump_max_power")),
         }
 
 
+def _pump_max_power(band: Any) -> dict[str, Any]:
+    """Which electrical maximum the live plan booked, and why (R10-COP-GATE
+    part D). ``source`` and ``reason`` are top-level codes, so the entity's
+    ``state_attributes`` translations render them; the evidence rides the
+    ``pump_max_power`` row. No plan publishes all three as ``None``."""
+    b = _mapping(band)
+    row = {k: b.get(k) for k in ("configured_max_kw", "planned_max_kw", "learned_max_kw", "samples", "since_s")}
+    return {
+        "pump_max_power": row if b else None,
+        "pump_max_power_source": b.get("source"),
+        "pump_max_power_reason": b.get("reason"),
+    }
+
+
 def _sysid_outcome(view: Any) -> dict[str, Any] | None:
     """The experiment's outcome, compact enough to record (#2808).
 
diff --git a/custom_components/heatpump_optimizer/strings.json b/custom_components/heatpump_optimizer/strings.json
index de3fbaa77..8b53ccb74 100644
--- a/custom_components/heatpump_optimizer/strings.json
+++ b/custom_components/heatpump_optimizer/strings.json
@@ -2045,6 +2045,25 @@
           "learning": "Learning",
           "learned": "Learned",
           "attention": "Needs attention"
+        },
+        "state_attributes": {
+          "pump_max_power_source": {
+            "name": "Maximum power the plan used",
+            "state": {
+              "configured": "Configured maximum",
+              "ceiling_probe": "Measured by the ceiling probe"
+            }
+          },
+          "pump_max_power_reason": {
+            "name": "Why the plan used that maximum",
+            "state": {
+              "plan_writes_power": "Configured: the plan writes the power itself, so the meter only echoes it",
+              "awaiting_probe": "Configured: the ceiling probe has too few samples yet",
+              "lapsed": "Configured: the ceiling probe's measurement is too old",
+              "not_below_configured": "Configured: the measured maximum agrees with it",
+              "measured_below_configured": "Measured: the pump draws clearly less than its configured maximum"
+            }
+          }
         }
       },
       "indoor_temperature_predicted": {
diff --git a/custom_components/heatpump_optimizer/translations/en.json b/custom_components/heatpump_optimizer/translations/en.json
index 8244039ec..8b53ccb74 100644
--- a/custom_components/heatpump_optimizer/translations/en.json
+++ b/custom_components/heatpump_optimizer/translations/en.json
@@ -1217,7 +1217,7 @@
         },
         "data_description": {
           "heat_pump_mode_entity": "Optional. The pump's own mode selector - cooling, heating, hot water, or a combination of two. Read only, unless Pump duty control is set to Control. A pump in a cooling or hot-water-only mode cannot heat the house, and one in a heating-only mode cannot make hot water, so without this the plan can promise heat the pump is not currently able to deliver. Left empty, the optimizer assumes the pump can do everything.",
-          "pump_duty_mode": "Off (the default) never writes the pump. Observe writes nothing and keeps a 24-hour ledger, in the diagnostics, of the duty each plan step asked for against what the pump did (from the power entity, the mode and the tank temperature). Control writes the operating mode above (hot water only on hot-water-only steps, heating only on space-heating-only steps, Heating + DHW when both are planned or a disinfection cycle is on, unchanged on idle steps), the hot water set-point entity (the hot water set-point configured on the hot water page) and the space set-point entity (for a flow set-point, 55 °C or the entity maximum on steps that heat the house, its minimum on steps that do not, and 35 °C or the weather curve when the plan is not in charge; for an indoor one, the planned room temperature). Where the mode offers no single-duty option, as on the GCHV Modbus package, the other duty's set-point is lowered to its minimum instead. A hot-water-only stretch is capped at 90 minutes (30 below -10 °C outdoors), unless the room is already at its planned temperature. While Optimizer active is on, any change to those entities the optimizer did not make is written back at once; turn Optimizer active off to change the pump by hand. A value the pump does not hold raises a warning and is sent again every 5 minutes.",
+          "pump_duty_mode": "Off (the default) never writes the pump. Observe writes nothing and keeps a 24-hour ledger, in the diagnostics, of the duty each plan step asked for against what the pump did (from the power entity, the mode and the tank temperature). Control writes the operating mode above (hot water only on hot-water-only steps, heating only on space-heating-only steps, Heating + DHW when both are planned or a disinfection cycle is on, unchanged on idle steps), the hot water set-point entity (the hot water set-point configured on the hot water page) and the space set-point entity (for a flow set-point, a target that follows the planned power — the heating flow (55 °C, or flow_heat_c) at full power, toward 5 °C above the first fresh reading of the heat-pump return, buffer tank, floor return or valve outlet (35 °C when none is configured) at the modulation floor — or the entity maximum on steps that heat the house, its minimum on steps that do not, and 35 °C or the weather curve when the plan is not in charge; for an indoor one, the planned room temperature). Where the mode offers no single-duty option, as on the GCHV Modbus package, the other duty's set-point is lowered to its minimum instead. A hot-water-only stretch is capped at 90 minutes (30 below -10 °C outdoors), unless the room is already at its planned temperature. While Optimizer active is on, any change to those entities the optimizer did not make is written back at once; turn Optimizer active off to change the pump by hand. A value the pump does not hold raises a warning and is sent again every 5 minutes.",
           "heat_pump_defrost_entity": "Optional. On while the pump reverses to melt frost off the outdoor coil. The electricity bought during a defrost goes into the coil rather than into the house. Note that many pumps are only polled every few minutes, so short defrosts are missed entirely: this is a sample of defrost activity, not a stopwatch.",
           "heat_pump_online_entity": "Optional, and strongly recommended for a cloud-connected pump. On while the pump is actually reachable. A cloud integration can keep republishing its last known readings while the pump itself has dropped off the network, which leaves every other sensor looking perfectly fresh; this is the one signal that says otherwise. On a local (LAN) connection the sensors go unavailable by themselves and this adds little.",
           "heat_pump_fault_entity": "Optional. On while the pump is reporting a fault. Only whether there is a fault is used, never the code itself.",
@@ -2045,6 +2045,25 @@
           "learning": "Learning",
           "learned": "Learned",
           "attention": "Needs attention"
+        },
+        "state_attributes": {
+          "pump_max_power_source": {
+            "name": "Maximum power the plan used",
+            "state": {
+              "configured": "Configured maximum",
+              "ceiling_probe": "Measured by the ceiling probe"
+            }
+          },
+          "pump_max_power_reason": {
+            "name": "Why the plan used that maximum",
+            "state": {
+              "plan_writes_power": "Configured: the plan writes the power itself, so the meter only echoes it",
+              "awaiting_probe": "Configured: the ceiling probe has too few samples yet",
+              "lapsed": "Configured: the ceiling probe's measurement is too old",
+              "not_below_configured": "Configured: the measured maximum agrees with it",
+              "measured_below_configured": "Measured: the pump draws clearly less than its configured maximum"
+            }
+          }
         }
       },
       "indoor_temperature_predicted": {
diff --git a/custom_components/heatpump_optimizer/translations/sv.json b/custom_components/heatpump_optimizer/translations/sv.json
index b5a2e57d1..85c3c0c6d 100644
--- a/custom_components/heatpump_optimizer/translations/sv.json
+++ b/custom_components/heatpump_optimizer/translations/sv.json
@@ -2045,6 +2045,25 @@
           "learning": "Lär sig",
           "learned": "Inlärd",
           "attention": "Behöver åtgärd"
+        },
+        "state_attributes": {
+          "pump_max_power_source": {
+            "name": "Maxeffekt som planen använde",
+            "state": {
+              "configured": "Inställd maxeffekt",
+              "ceiling_probe": "Uppmätt av takprovet"
+            }
+          },
+          "pump_max_power_reason": {
+            "name": "Varför planen använde den maxeffekten",
+            "state": {
+              "plan_writes_power": "Inställd: planen skriver effekten själv, så mätaren visar bara den",
+              "awaiting_probe": "Inställd: takprovet har ännu för få mätpunkter",
+              "lapsed": "Inställd: takprovets mätning är för gammal",
+              "not_below_configured": "Inställd: den uppmätta maxeffekten stämmer med den",
+              "measured_below_configured": "Uppmätt: pumpen drar tydligt mindre än sin inställda maxeffekt"
+            }
+          }
         }
       },
       "indoor_temperature_predicted": {
diff --git a/dev/audit/harnesses/r10_cop_gate_top.py b/dev/audit/harnesses/r10_cop_gate_top.py
new file mode 100644
index 000000000..a3fa29a4a
--- /dev/null
+++ b/dev/audit/harnesses/r10_cop_gate_top.py
@@ -0,0 +1,177 @@
+"""R10-COP-GATE part D harness: does the ceiling store's learned top reach the
+range a solve books, and the band the arbiter maps the plan's steps on?
+
+Ported from the finder's ``evidence/r3_probe_reader.py`` at
+``design-verdict/R10-CEILING-PROBE`` 3a261d864 (the measurement carry 12
+cites: the store's median published, no solve reading it) and extended, as
+the design note asks, to print the solve's ruling and its top.
+
+  reader    store-only reads at 11 and 12 samples of a 3.0 kW pump behind a
+            configured (1.0, 5.0): ``learned_max_kw``, the window's
+            ``planned_range`` and the top the solve books
+  rule      every row of the design's rule table, plus the 15 % edge
+  map       the flow set-point one arbiter pass writes for a 3.0 kW plan step,
+            the plan stamped with the learned band against unstamped
+  plan      one live coordinator cycle per row (the round-9 rig: fixed
+            hourly prices, -5 degC, the clock frozen): the plan's top step,
+            a sha1 of its power_schedule and the stamp, for a fresh install,
+            a store within 15 %, eleven samples, a plan-writes-power install,
+            a learned top at half the configured one, and both again at a
+            flat price. Every configured row must hash as the fresh install
+
+Synthetic inputs only. Run from a worktree root (any tree; an arm whose
+symbols the tree lacks prints ``absent``, and at a base with no ruling the
+solve books the hub's configured top):
+  PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_cop_gate_top.py
+"""
+from __future__ import annotations
+
+from datetime import datetime, timedelta, timezone
+from types import SimpleNamespace as NS
+
+import asyncio
+import hashlib
+import json
+from unittest import mock
+
+from harness import FakeEntry, FakeHass, FakeState
+from homeassistant.util import dt as dt_util
+from heatpump_optimizer import const
+from heatpump_optimizer import coordinator as cmod
+from heatpump_optimizer import draw_range as dr
+from heatpump_optimizer import pump_arbiter as pa
+from heatpump_optimizer.entry_config import EntryConfig
+
+NOW = datetime(2026, 10, 27, 1, 0, tzinfo=timezone.utc)
+NOW_S = NOW.timestamp()
+CFG = (1.0, 5.0)
+PARAMS = NS(min_electrical_power=CFG[0], max_electrical_power=CFG[1])
+CAP = NS(plan_writes_power=lambda: False, can_duty_cycle=lambda: True)
+ECHO = NS(plan_writes_power=lambda: True, can_duty_cycle=lambda: True)
+
+
+def store(values, newest_s=NOW_S):
+    d = dr.DrawRange()
+    for k, v in enumerate(values):
+        d.observe_ceiling(v, newest_s - (len(values) - 1 - k) * 1800.0)
+    return d
+
+
+def ruling(d, cap=CAP, now_s=NOW_S, params=PARAMS):
+    fn = getattr(dr, "solve_band", None)
+    if fn is None:
+        return None
+    return fn(d, params, cap, now_s)
+
+
+def solve_top(d, cap=CAP, now_s=NOW_S):
+    """The top the solve copy books: the ruling's, or the hub's with none."""
+    b = ruling(d, cap, now_s)
+    return CFG[1] if b is None else b.max_kw
+
+
+def reader_arm() -> None:
+    for n in (11, 12):
+        d = store([3.0] * n)
+        b = ruling(d)
+        print(f"reader: {n} samples -> learned_max_kw {d.learned_max_kw(NOW_S)!r} "
+              f"planned_range {dr.planned_range(d, PARAMS, CAP)!r} solve top {solve_top(d)!r} "
+              f"solve_band {'absent' if b is None else (b.source, b.reason)}")
+
+
+def rule_arm() -> None:
+    rows = (
+        ("eleven samples", store([3.0] * 11), CAP, NOW_S),
+        ("twelve at 3.0", store([3.0] * 12), CAP, NOW_S),
+        ("lapsed (+46 d)", store([3.0] * 12), CAP, NOW_S + 46 * 86400.0),
+        ("within 15 % (4.5)", store([4.5] * 12), CAP, NOW_S),
+        ("edge (4.25)", store([4.25] * 12), CAP, NOW_S),
+        ("above (6.0)", store([6.0] * 12), CAP, NOW_S),
+        ("plan writes power", store([3.0] * 12), ECHO, NOW_S),
+    )
+    for label, d, cap, now_s in rows:
+        b = ruling(d, cap, now_s)
+        print(f"rule: {label:18s} -> " + ("absent" if b is None else
+              f"{b.source} {b.reason} max {b.max_kw} min {b.min_kw}"))
+
+
+def _flow(band) -> float | None:
+    hass = FakeHass({"number.water_set": FakeState("40", attributes={"min": 25, "max": 63})})
+    config = EntryConfig.from_mapping({"pump_duty_mode": "control", "space_setpoint_entity": "number.water_set",
+                                       "space_setpoint_unit": "flow"})
+    plan = NS(timestamps=[NOW], power_schedule=[3.0], dhw_power_schedule=[0.0], optimal_setpoints=[21.0])
+    if band is not None:
+        plan.solve_band = band
+    params = NS(dhw_setpoint=48.0, min_electrical_power=CFG[0], max_electrical_power=CFG[1])
+    inp = pa.ArbiterInputs(hass=hass, config=config, mode="auto", plan=plan, plan_stale=False,
+                           entry_released=False, state=NS(outdoor_temperature=2.0, room_temperature=21.0),
+                           thermal=NS(params=params, curve_flow_temp=lambda _o: 34.2), params=params,
+                           action={"mode": "eco", "power": 3.0}, measured_power_kw=None, disinfecting=False)
+    target = pa._flow_target(inp, "space", NOW + timedelta(minutes=1))
+    return None if target is None else getattr(target, "value", target)
+
+
+def map_arm() -> None:
+    b = ruling(store([3.0] * 12))
+    print(f"map: 3.0 kW plan step, unstamped -> {_flow(None)!r}")
+    print(f"map: 3.0 kW plan step, stamped {'absent' if b is None else 'learned (1.0, 3.0)'} -> "
+          f"{_flow(None if b is None else b.as_dict())!r}")
+
+
+RIG_NOW = datetime(2026, 1, 15, 6, 0, tzinfo=timezone.utc)
+FLOW = {"pump_duty_mode": "control", "space_setpoint_unit": "flow",
+        "space_setpoint_entity": "number.water_set", "heat_pump_power_entity": "sensor.hp_power"}
+FREQ = {"compressor_freq_entity": "number.hp_compressor_hz", "freq_control_mode": "control"}
+
+
+def _rig(entry_id, extra, flat):
+    hass = FakeHass()
+    hass.states.set("sensor.indoor", FakeState("21.0"))
+    hass.states.set("sensor.outdoor", FakeState("-3.0"))
+    entry = FakeEntry(data={const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
+                            const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor", **extra}, entry_id=entry_id)
+    coord = cmod.HeatPumpOptimizerCoordinator(hass, entry)
+    coord._prices = [{"total": 0.8 if flat else round(0.6 + 0.5 * (h % 12) / 12.0, 4),
+                      "starts_at": (RIG_NOW + timedelta(hours=h - 2)).isoformat(), "level": "NORMAL"}
+                     for h in range(50)]
+    coord._weather_forecast = [{"datetime": (RIG_NOW + timedelta(hours=h)).isoformat(), "temperature": -5.0,
+                                "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0} for h in range(48)]
+
+    async def noop(*_a, **_k):
+        return None
+
+    coord._fetch_tibber_prices = coord._fetch_weather_forecast = coord._fetch_solar_forecast = noop
+    return coord
+
+
+async def _inline(hass, optimizer, inputs):
+    from heatpump_optimizer.optimizer import optimize_in_process
+    return optimize_in_process(optimizer, inputs)
+
+
+def plan_arm() -> None:
+    dt_util.freeze(RIG_NOW)
+    rows = (("fresh, no store", FLOW, 0, 0.0, False), ("store 12 @ 0.9 (within 15 %)", FLOW, 12, 0.9, False),
+            ("store 11 @ 0.5", FLOW, 11, 0.5, False), ("plan-writes-power, 12 @ 0.5", FREQ, 12, 0.5, False),
+            ("store 12 @ 0.5 (learned)", FLOW, 12, 0.5, False), ("flat price, no store", FLOW, 0, 0.0, True),
+            ("flat price, 12 @ 0.5", FLOW, 12, 0.5, True))
+    for label, extra, n, frac, flat in rows:
+        c = _rig("top_" + label, extra, flat)
+        hub_max = float(cmod._ctx_of(c)._thermal_params.max_electrical_power)
+        if n:
+            c._accuracy.draw = store([frac * hub_max] * n, dt_util.now().timestamp() - 60.0)
+        with mock.patch.object(cmod, "_await_optimize", _inline):
+            asyncio.run(c.async_run_optimization())
+        ps = [round(float(x), 12) for x in c._optimization_result.power_schedule]
+        band = getattr(c._optimization_result, "solve_band", None)
+        print(f"plan: {label:28s} hub max {hub_max} top step {max(ps):.4f} "
+              f"sha {hashlib.sha1(json.dumps(ps).encode()).hexdigest()[:12]} "
+              f"stamp {'absent' if not band else (band['source'], band['reason'])}")
+    dt_util.freeze(None)
+
+
+if __name__ == "__main__":
+    reader_arm()
+    rule_arm()
+    map_arm()
+    plan_arm()
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index b3c3d6a4c..271985a54 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -1030,7 +1030,7 @@
   "source": "README.md",
   "claim": "the Swedish translation actually differs from the English entity names",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "0 of 82 entity names identical in sv and en",
+  "result": "0 of 84 entity names identical in sv and en",
   "verdict": "true",
   "truth": ""
  },
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index fe23a8ab3..df30e27e2 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -118,7 +118,7 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C112 | `strings.json + translations/*.json` | every translation file carries exactly the keys strings.json declares | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | languages=['en', 'sv'], missing={'en': 0, 'sv': 0}, extra={'en': 0, 'sv': 0} | **true** |  |
 | C113 | `README.md` | entity names are translated into English and Swedish | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['en', 'sv'] measured=['en', 'sv'] | **true** |  |
 | C114 | `README.md` | every entity's display name comes from the translation files | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | untranslated=[] | **true** |  |
-| C115 | `README.md` | the Swedish translation actually differs from the English entity names | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 0 of 82 entity names identical in sv and en | **true** |  |
+| C115 | `README.md` | the Swedish translation actually differs from the English entity names | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 0 of 84 entity names identical in sv and en | **true** |  |
 | C116 | `README.md` | the integration domain is heatpump_optimizer | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='heatpump_optimizer' measured='heatpump_optimizer' | **true** |  |
 | C117 | `manifest.json` | config_flow is declared | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=True measured=True | **true** |  |
 | C118 | `README.md` | the documentation url in the manifest points at the project | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='https://github.com/tvofi/heatpump_optimizer' measured='https://github.com/tvofi/heatpump_optimizer' | **true** |  |
diff --git a/dev/programme/delivery/3193.md b/dev/programme/delivery/3193.md
new file mode 100644
index 000000000..c55464050
--- /dev/null
+++ b/dev/programme/delivery/3193.md
@@ -0,0 +1 @@
+- [#3193](https://github.com/tvofi/heatpump_optimizer/pull/3193) — **open**, R10-COP-GATE-D: cop gate d (R10-COP-GATE-D)
diff --git a/tests/closures.json b/tests/closures.json
index dfa5dbfcb..8f030659f 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3946,6 +3946,7 @@
    "dev/audit/harnesses/r10_configflow_pages.py",
    "dev/audit/harnesses/r10_cop_conversions.py",
    "dev/audit/harnesses/r10_cop_gate.py",
+   "dev/audit/harnesses/r10_cop_gate_top.py",
    "dev/audit/harnesses/r10_cop_gate_vent.py",
    "dev/audit/harnesses/r10_cop_partload.py",
    "dev/audit/harnesses/r10_cop_partload_equiv.py",
diff --git a/tests/entities.py b/tests/entities.py
index d87040eba..44c0ebea9 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -10021,11 +10021,42 @@ base_keys = all_keys(strings)
 for name, data in files.items():
     diff = base_keys ^ all_keys(data)
     R.check(
-        f"{name}.json matches strings.json exactly",
+        f"{name}.json has exactly strings.json's keys",
         not diff,
         ", ".join(sorted(diff)[:6]),
     )
 
+
+def leaf_values(data, prefix=""):
+    """``{dotted path: leaf}`` for every non-dict leaf."""
+    out = {}
+    for key, value in data.items():
+        path = f"{prefix}.{key}" if prefix else key
+        out.update(leaf_values(value, path) if isinstance(value, dict) else {path: value})
+    return out
+
+
+# Carry 0 (R10-COP-GATE-D): Home Assistant serves translations/en.json, so the
+# English text shipped is en.json's, not strings.json's. The key check above
+# read "exactly" while comparing keys only, and en.json's pump_duty_mode text
+# went stale beside an edited source. en.json is a copy of strings.json leaf
+# for leaf; sv.json is a translation, so only its keys are pinned.
+def en_value_drift(source, en):
+    """The dotted paths where en's leaf differs from the source's."""
+    a, b = leaf_values(source), leaf_values(en)
+    return sorted(k for k in a.keys() & b.keys() if a[k] != b[k])
+
+
+_en_drift = en_value_drift(strings, files["en"])
+R.check(
+    "en.json equals strings.json leaf for leaf (null: a source compared with itself "
+    "drifts nowhere, and one edited leaf is found)",
+    not _en_drift
+    and en_value_drift(strings, strings) == []
+    and en_value_drift({"a": {"b": "x"}}, {"a": {"b": "y"}}) == ["a.b"],
+    ", ".join(_en_drift[:6]),
+)
+
 # D4-s2-03 (N-escape): a translation leaf written with two backslashes before
 # a \u escape (\\u00b0 in the JSON source) survives json.loads as the six
 # literal characters "°" in the Python string, not the degree sign the
@@ -12473,7 +12504,8 @@ _PUBLISHED_ATTRS: dict[str, frozenset[str]] = {
     }),
     "ModelStatusSensor": frozenset({
         "capacity_envelope", "cop", "heat_loss", "heat_loss_w_per_k",
-        "internal_gains_kw", "learner_progress", "lower_floor", "solar_aperture",
+        "internal_gains_kw", "learner_progress", "lower_floor", "pump_max_power",
+        "pump_max_power_reason", "pump_max_power_source", "solar_aperture",
         "system_identification", "system_identification_outcome", "tank_cooling"
     }),
     "MonthlyPeakSensor": frozenset({
diff --git a/tests/features.py b/tests/features.py
index 0249ef301..8cd5ff0b4 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -74896,6 +74896,20 @@ R.check(
     and _he_noelec._measured_cop.refusal == _HE_UNALIGNED,
     f"{_he_noelec_ref} {_he_noelec._measured_cop.refusal}",
 )
+# R10-COP-GATE part D carry 1: the published surfaces render that refusal and
+# never a COP gate pass over it (null: the known-COP span publishes its COP and
+# no refusal).
+_he_noelec_view = _he_noelec._learning_view()
+_he_known_view = _he_known._learning_view()
+R.check(
+    "carry 1: a counter install with no electric counter publishes unaligned_meters "
+    "and no measured COP; the aligned span publishes its COP",
+    _he_noelec_view["cop_refusal"] == _HE_UNALIGNED and _he_noelec_view["measured_cop"] is None
+    and _he_known_view["measured_cop"] == _he_known._measured_cop.cop
+    and _he_known_view["cop_refusal"] != _HE_UNALIGNED,
+    f"{_he_noelec_view['cop_refusal']} {_he_noelec_view['measured_cop']} "
+    f"{_he_known_view['measured_cop']} {_he_known_view['cop_refusal']}",
+)
 
 # #2854 round 4: the install the brief promises -- the heat counter and the
 # electric energy counter, no power entity -- folds its span's COP too. The
@@ -76421,6 +76435,252 @@ R.check(
     f"late {len(_cp_pump_late.ceiling)} window {len(_cp_pump_late.samples)}",
 )
 
+# -- R10-COP-GATE part D: the learned top reaching the plan -------------------
+# ``draw_range.solve_band`` rules the band a solve books, once per solve; the
+# coordinator stamps it on the plan; ``pump_arbiter._band_kw`` maps the plan's
+# steps by the stamp and an experiment's by the hub. Synthetic pump: a 3.0 kW
+# real maximum behind a configured (1.0, 5.0).
+import json as _cpd_json  # noqa: E402
+import time as _cpd_time  # noqa: E402
+from dataclasses import replace as _cpd_replace  # noqa: E402
+from pathlib import Path as _CpdPath  # noqa: E402
+
+_CPD_CAP = _CpNS(plan_writes_power=lambda: False)
+_CPD_ECHO = _CpNS(plan_writes_power=lambda: True)
+
+
+def _cpd_band(values, now_s=_CP_NOW, lo=1.0, hi=5.0, cap=_CPD_CAP, newest_s=_CP_NOW):
+    return _cp_dr.solve_band(_cp_store(values, newest_s), _cp_params(lo, hi), cap, now_s)
+
+
+_cpd_eleven = _cpd_band([3.0] * 11)
+_cpd_twelve = _cpd_band([3.0] * 12)
+_cpd_lapsed = _cpd_band([3.0] * 12, now_s=_CP_NOW + 46 * 86400.0)
+_cpd_ahead = _cpd_band([3.0] * 12, now_s=_CP_NOW - 3600.0)
+_cpd_agree = _cpd_band([4.5] * 12)
+_cpd_above = _cpd_band([6.0] * 12)
+_cpd_echo = _cpd_band([3.0] * 12, cap=_CPD_ECHO)
+_cpd_lowmin = _cpd_band([3.0] * 12, lo=3.5)
+_cpd_edge = _cpd_band([4.25] * 12)
+_cpd_rows = lambda b: (b.source, b.reason, b.max_kw, b.min_kw)  # noqa: E731
+R.check(
+    "part D's rule table: eleven samples, a lapsed store, a top within 15 %, a top above "
+    "the configured one and a plan-writes-power install book the configured (1.0, 5.0) "
+    "with their reasons; twelve samples at 3.0 kW book the learned 3.0",
+    _cpd_rows(_cpd_eleven) == ("configured", "awaiting_probe", 5.0, 1.0)
+    and _cpd_eleven.samples == 11
+    and _cpd_rows(_cpd_twelve) == ("ceiling_probe", "measured_below_configured", 3.0, 1.0)
+    and _cpd_twelve.since_s == _CP_NOW
+    and _cpd_rows(_cpd_lapsed) == ("configured", "lapsed", 5.0, 1.0)
+    and _cpd_rows(_cpd_ahead) == ("configured", "lapsed", 5.0, 1.0)
+    and _cpd_rows(_cpd_agree) == ("configured", "not_below_configured", 5.0, 1.0)
+    and _cpd_agree.learned_max_kw == 4.5
+    and _cpd_rows(_cpd_above) == ("configured", "not_below_configured", 5.0, 1.0)
+    and _cpd_rows(_cpd_echo) == ("configured", "plan_writes_power", 5.0, 1.0),
+    f"{[_cpd_rows(b) for b in (_cpd_eleven, _cpd_twelve, _cpd_lapsed, _cpd_agree, _cpd_above, _cpd_echo)]}",
+)
+R.check(
+    "part D: the 15 % edge is exclusive (4.25 of 5.0 keeps the configured top), and the "
+    "bottom never exceeds the top (a configured 3.5 kW minimum under a learned 3.0 books 3.0)",
+    _cpd_rows(_cpd_edge) == ("configured", "not_below_configured", 5.0, 1.0)
+    and _cpd_band([4.2] * 12).max_kw == 4.2
+    and _cpd_rows(_cpd_lowmin) == ("ceiling_probe", "measured_below_configured", 3.0, 3.0),
+    f"{_cpd_rows(_cpd_edge)} {_cpd_rows(_cpd_lowmin)}",
+)
+_cpd_d = _cpd_twelve.as_dict()
+R.check(
+    "part D: the stamp carries the configured and planned tops, the source and the reason",
+    {k: _cpd_d[k] for k in ("configured_max_kw", "planned_max_kw", "planned_min_kw", "source", "reason")}
+    == {"configured_max_kw": 5.0, "planned_max_kw": 3.0, "planned_min_kw": 1.0,
+        "source": "ceiling_probe", "reason": "measured_below_configured"},
+    f"{_cpd_d}",
+)
+# Item D3: the solve copy's floors survive the replaced top.
+from heatpump_optimizer.thermal_model import ThermalParameters as _CpdTP  # noqa: E402
+_cpd_tp = _cpd_replace(_CpdTP(min_electrical_power=1.0, max_electrical_power=5.0), max_electrical_power=3.0, min_electrical_power=1.0)
+R.check(
+    "item D3: ``replace`` with the learned top keeps a valid ThermalParameters, min <= max",
+    _cpd_tp.max_electrical_power == 3.0 and _cpd_tp.min_electrical_power <= _cpd_tp.max_electrical_power,
+    f"{_cpd_tp.min_electrical_power} {_cpd_tp.max_electrical_power}",
+)
+
+
+def _cpd_arbitrate(action, power_schedule, band):
+    """``_cp_arbitrate`` with the plan stamped with ``band`` (a dict, or {})."""
+    c = _CpArb(action, power_schedule)
+    c._optimization_result.solve_band = band
+    _cp_aio.run(_cp_pa.apply(c, _CP_T0 + timedelta(minutes=1)))
+    flow = [x["value"] for d, s, x in c.hass.services.calls
+            if d == "number" and (x or {}).get("entity_id") == "number.water_set"]
+    return flow[-1] if flow else None
+
+
+_CPD_LEARNED = _cpd_twelve.as_dict()
+_CPD_CFG = _cpd_eleven.as_dict()
+_cpd_top_learned = _cpd_arbitrate({"mode": "eco", "power": 3.0}, (3.0,), _CPD_LEARNED)
+_cpd_top_cfg = _cpd_arbitrate({"mode": "eco", "power": 3.0}, (3.0,), _CPD_CFG)
+_cpd_top_none = _cpd_arbitrate({"mode": "eco", "power": 3.0}, (3.0,), {})
+R.check(
+    "invariant 2: a 3.0 kW plan step solved on the learned (1.0, 3.0) writes the 55 degC "
+    "ceiling; the same step stamped configured, or unstamped, writes the configured band's level",
+    _cpd_top_learned == 55.0 and _cpd_top_cfg == _cpd_top_none and _cpd_top_cfg < 55.0,
+    f"learned {_cpd_top_learned} configured {_cpd_top_cfg} unstamped {_cpd_top_none}",
+)
+_cpd_probe_learned = _cpd_arbitrate({**_CP_SID, "power": 5.0}, (3.0,), _CPD_LEARNED)
+_cpd_fit_learned = _cpd_arbitrate({**_CP_SID, "power": 1.5}, (3.0,), _CPD_LEARNED)
+_cpd_fit_cfg = _cpd_arbitrate({**_CP_SID, "power": 1.5}, (3.0,), {})
+R.check(
+    "item D5: on a plan stamped with the learned band, the probe's configured 5.0 kW step "
+    "still writes the heat level, and the fit's sized 1.5 kW step maps on the hub's band",
+    _cpd_probe_learned == 55.0 and _cpd_fit_learned == _cpd_fit_cfg == _cp_fit[1],
+    f"probe {_cpd_probe_learned} fit {_cpd_fit_learned} vs {_cpd_fit_cfg}",
+)
+
+# The coordinator: the solve copy books the ruling, the hub never does.
+_cpd_c = _cp_coord(**_CP_PROBE_CFG)
+_cpd_hub = _cp_cmod._ctx_of(_cpd_c)._thermal_params
+_cpd_hub_max = float(_cpd_hub.max_electrical_power)
+_cpd_c._accuracy.draw = _cp_store([0.5 * _cpd_hub_max] * 12, _cpd_time.time())
+_cpd_band_c = _cp_cmod._solve_band(_cpd_c._accuracy.draw, _cpd_hub, _cp_cmod._ctx_of(_cpd_c)._config)
+_cpd_cfg_c, _cpd_params_c, _cpd_state_c = _cpd_c._solve_hubs(8, banded=False, band=_cpd_band_c)
+_cpd_c._accuracy.draw = _cp_store([0.5 * _cpd_hub_max] * 11, _cpd_time.time())
+_cpd_band_11 = _cp_cmod._solve_band(_cpd_c._accuracy.draw, _cpd_hub, _cp_cmod._ctx_of(_cpd_c)._config)
+_cpd_params_11 = _cpd_c._solve_hubs(8, banded=False, band=_cpd_band_11)[1]
+R.check(
+    "invariants 1 and 3(iv): twelve store samples at half the hub's maximum put the learned "
+    "top in the solve copy and never in the hub; eleven leave the copy on the hub's figures",
+    _cpd_band_c.source == "ceiling_probe"
+    and _cpd_params_c.max_electrical_power == _cpd_band_c.max_kw == 0.5 * _cpd_hub_max
+    and _cpd_hub.max_electrical_power == _cpd_hub_max
+    and _cpd_band_11.source == "configured"
+    and _cpd_params_11.max_electrical_power == _cpd_hub_max
+    and _cpd_params_11.min_electrical_power == _cpd_hub.min_electrical_power,
+    f"{_cpd_band_c} copy {_cpd_params_c.max_electrical_power} hub {_cpd_hub.max_electrical_power}",
+)
+# ``_band_fields`` itself, fed bands whose figures differ from the hub's: a
+# configured band books nothing (the copy keeps the hub's figures byte for
+# byte), the learned band books its own top and bottom (null control).
+_cpd_bf_cfg = _cp_cmod.draw_range.SolveBand(5.0, 9.0, 2.0, "configured", "awaiting_probe", None, 0, None)
+_cpd_bf_probe = _cp_cmod.draw_range.SolveBand(5.0, 3.0, 1.0, "ceiling_probe", "measured_below_configured", 3.0, 12, None)
+R.check(
+    "_band_fields: a configured band returns no fields; a ceiling_probe band returns its "
+    "max and min as the solve copy's electrical power range",
+    _cp_cmod._band_fields(_cpd_bf_cfg) == {}
+    and _cp_cmod._band_fields(_cpd_bf_probe) == {"max_electrical_power": 3.0, "min_electrical_power": 1.0},
+    f"{_cp_cmod._band_fields(_cpd_bf_cfg)} {_cp_cmod._band_fields(_cpd_bf_probe)}",
+)
+# Invariant 3 through the live cycle: the plan is stamped with the band it
+# was solved on, and the arbiter and the payload read the stamp until the next
+# solve, whatever the store does in between.
+_r9f13_dt.freeze(_R9F13_NOW)  # the rig's price series is anchored here
+_, _, _cpd_live = _r9f13_make("cpd_stamp", dict(_CP_PROBE_CFG))
+_cpd_live_hub = _cp_cmod._ctx_of(_cpd_live)._thermal_params
+_cpd_live_top = 0.5 * float(_cpd_live_hub.max_electrical_power)
+_cpd_now_s = _cp_cmod.dt_util.now().timestamp()
+_cpd_live._accuracy.draw = _cp_store([_cpd_live_top] * 11, _cpd_now_s - 3600.0)
+
+
+def _cpd_solve(coord):
+    with _r9f13_mock.patch.object(_r9f13_cmod, "_await_optimize", _r9f13_inline):
+        return _r9f13_aio.run(coord.async_run_optimization())
+
+
+_cpd_r1 = _cpd_solve(_cpd_live)
+_cpd_stamp1 = dict(_cpd_live._optimization_result.solve_band)
+_cpd_live._accuracy.draw.observe_ceiling(_cpd_live_top, _cpd_now_s - 60.0)  # the twelfth
+_cpd_band_after_fold = _cp_pa._band_kw(_cpd_live.arbiter_inputs())
+_cpd_view_after_fold = _cpd_live._learning_view().get("pump_max_power")
+_cpd_r2 = _cpd_solve(_cpd_live)
+_cpd_stamp2 = dict(_cpd_live._optimization_result.solve_band)
+_cpd_plan_max = max(_cpd_live._optimization_result.power_schedule)
+_cpd_live._accuracy.draw.ceiling.clear()  # the store lapses or drops, no solve
+_cpd_band_after_drop = _cp_pa._band_kw(_cpd_live.arbiter_inputs())
+_r9f13_dt.freeze(None)
+R.check(
+    "invariant 3 (i, ii, v): solved on eleven samples the plan is stamped configured; the "
+    "twelfth folded without a solve leaves the arbiter's band and the published reason on "
+    "that stamp; the next solve books the learned top and stamps it; a store dropped "
+    "without a solve keeps the stamped learned band",
+    _cpd_r1 is None and _cpd_r2 is None
+    and (_cpd_stamp1.get("source"), _cpd_stamp1.get("reason")) == ("configured", "awaiting_probe")
+    and _cpd_band_after_fold == (_cpd_stamp1.get("planned_min_kw"), _cpd_stamp1.get("planned_max_kw"))
+    and (_cpd_view_after_fold or {}).get("source") == "configured"
+    and _cpd_stamp2.get("source") == "ceiling_probe"
+    and abs(_cpd_stamp2.get("planned_max_kw", 0.0) - _cpd_live_top) < 1e-3
+    and _cpd_plan_max <= _cpd_live_top + 1e-6
+    and _cpd_band_after_drop == (_cpd_stamp2.get("planned_min_kw"), _cpd_stamp2.get("planned_max_kw"))
+    and float(_cpd_live_hub.max_electrical_power) == 2.0 * _cpd_live_top,
+    f"r {_cpd_r1} {_cpd_r2} stamp1 {_cpd_stamp1.get('reason')} fold-band {_cpd_band_after_fold} "
+    f"stamp2 {_cpd_stamp2.get('source')} {_cpd_stamp2.get('planned_max_kw')} plan-max {_cpd_plan_max} "
+    f"drop-band {_cpd_band_after_drop}",
+)
+_cpd_c._optimization_result = None
+_cpd_none_view = _cpd_c._learning_view().get("pump_max_power", "absent")
+_cpd_c._optimization_result = _CpNS(solve_band=_cpd_band_c.as_dict())
+_cpd_stamped_view = _cpd_c._learning_view().get("pump_max_power")
+R.check(
+    "part D publish: the learning view carries the live plan's stamp, None with no plan",
+    _cpd_none_view is None and _cpd_stamped_view == _cpd_band_c.as_dict(),
+    f"{_cpd_none_view} {_cpd_stamped_view}",
+)
+_cpd_status = _CpStatus.__new__(_CpStatus)
+_cpd_status._data = lambda: {"pump_max_power": _CPD_LEARNED}
+_cpd_attrs = _CpStatus.extra_state_attributes.fget(_cpd_status)
+_cpd_status._data = lambda: {}
+_cpd_attrs_none = _CpStatus.extra_state_attributes.fget(_cpd_status)
+R.check(
+    "part D publish: the model status sensor names the configured and planned tops and "
+    "publishes source and reason as top-level codes; no plan publishes None",
+    (_cpd_attrs.get("pump_max_power") or {}).get("configured_max_kw") == 5.0
+    and (_cpd_attrs.get("pump_max_power") or {}).get("planned_max_kw") == 3.0
+    and _cpd_attrs.get("pump_max_power_source") == "ceiling_probe"
+    and _cpd_attrs.get("pump_max_power_reason") == "measured_below_configured"
+    and all(k in _cpd_attrs_none for k in ("pump_max_power", "pump_max_power_source", "pump_max_power_reason"))
+    and (_cpd_attrs_none["pump_max_power"], _cpd_attrs_none["pump_max_power_source"],
+         _cpd_attrs_none["pump_max_power_reason"]) == (None, None, None),
+    f"{_cpd_attrs.get('pump_max_power')} {_cpd_attrs_none.get('pump_max_power')}",
+)
+# Item D6: the previous plan handed to the next solve as a start is clipped
+# to that solve's top, so a band narrowed at the twelfth sample scores no
+# candidate step above it (null: a plan inside the band is handed unchanged).
+from heatpump_optimizer.optimizer import HeatPumpOptimizer as _CpdOpt, OptimizationConfig as _CpdOC  # noqa: E402
+from heatpump_optimizer.thermal_model import ThermalModel as _CpdTM  # noqa: E402
+_cpd_opt = _CpdOpt(_CpdTM(_CpdTP(min_electrical_power=1.0, max_electrical_power=3.0)), _CpdOC())
+_cpd_opt._prev_shipped_plan = np.array([5.0, 4.0, 2.0, 0.0])
+_cpd_warm = _cpd_opt._warm_start_starts(4)[0]
+_cpd_opt._prev_shipped_plan = np.array([3.0, 2.5, 1.0, 0.0])
+_cpd_warm_null = _cpd_opt._warm_start_starts(4)[0]
+R.check(
+    "item D6: a warm start from a (1.0, 5.0) plan into a (1.0, 3.0) solve holds no step "
+    "above 3.0; a plan inside the band is handed unchanged",
+    list(_cpd_warm) == [3.0, 3.0, 2.0, 0.0] and list(_cpd_warm_null) == [3.0, 2.5, 1.0, 0.0],
+    f"{list(_cpd_warm)} {list(_cpd_warm_null)}",
+)
+# Carry 6: every source and reason code has its user string in strings.json,
+# en and sv, under the entity's state_attributes, so no raw code is shown.
+_cpd_codes = {
+    "pump_max_power_source": {"configured", "ceiling_probe"},
+    "pump_max_power_reason": {"plan_writes_power", "awaiting_probe", "lapsed",
+                              "not_below_configured", "measured_below_configured"},
+}
+_cpd_tr_missing = []
+for _cpd_name in ("strings.json", "translations/en.json", "translations/sv.json"):
+    _cpd_tr = _cpd_json.loads((_CpdPath(__file__).resolve().parents[1] / "custom_components/heatpump_optimizer" / _cpd_name).read_text())
+    _cpd_attrs_tr = _cpd_tr["entity"]["sensor"]["learning_model_status"].get("state_attributes", {})
+    for _cpd_attr, _cpd_vals in _cpd_codes.items():
+        _cpd_states = _cpd_attrs_tr.get(_cpd_attr, {}).get("state", {})
+        _cpd_tr_missing += [f"{_cpd_name}:{_cpd_attr}.{v}" for v in sorted(_cpd_vals) if not _cpd_states.get(v)]
+R.check(
+    "carry 6: each pump_max_power source and reason code has its user string in "
+    "strings.json, en and sv (null: the rule table's codes are the set checked)",
+    not _cpd_tr_missing
+    and {b.reason for b in (_cpd_eleven, _cpd_twelve, _cpd_lapsed, _cpd_agree, _cpd_echo)}
+    == _cpd_codes["pump_max_power_reason"]
+    and {b.source for b in (_cpd_eleven, _cpd_twelve)} == _cpd_codes["pump_max_power_source"],
+    f"missing {_cpd_tr_missing}",
+)
+
+
 # #2808: the outcome is recorded. The bulky view stays unrecorded; a compact
 # outcome row beside it is recorded, so a refusal has a history.
 _cp_status = _CpStatus.__new__(_CpStatus)
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index 079f94e17..26645cda1 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -67,8 +67,13 @@
 # v7.1.1: factory reset, ceiling probe, SAV comfort, away-mode and learner fixes. The stamp empties the list; the
 # next branch restates its own footprint, claims included.
 #
-shape: space_reasons[*]|dhw_reasons[*] * -> 'idle_coasting'|'idle'  # R10-ARCH-SHAPES-CLASSIFIER (D8-s1-01): the reason classifiers read each channel's draw only on the steps the plan runs the pump at, so a share on a step the plan calls off is idle; which fixtures carry such a step is the host's basin (#996)
 #
+shape: space_reasons[*]|dhw_reasons[*] * -> 'idle_coasting'|'idle'  # R10-ARCH-SHAPES-CLASSIFIER (D8-s1-01): the reason classifiers read each channel's draw only on the steps the plan runs the pump at, so a share on a step the plan calls off is idle; which fixtures carry such a step is the host's basin (#996)
+coord_all_features  # R10-COP-GATE-D: four pump_max_power keys added (null), nothing else moves
+coord_dhw  # R10-COP-GATE-D: four pump_max_power keys added (null), nothing else moves
+coord_grid_fee  # R10-COP-GATE-D: four pump_max_power keys added (null), nothing else moves
+coord_minimal  # R10-COP-GATE-D: four pump_max_power keys added (null), nothing else moves
+coord_two_zone  # R10-COP-GATE-D: four pump_max_power keys added (null), nothing else moves
 # may-drift: flat_prices -- #1208 polish-every-candidate, owner ruling #1208 comment 208bed25
 # (option (a)): the move's margin is inside the noise band (objective rel
 # -1.2171e-03, deterministic on one box), so which runner sees it move is the
@@ -743,3 +748,13 @@ shape: space_reasons[*]|dhw_reasons[*] * -> 'idle_coasting'|'idle'  # R10-ARCH-S
 # valve_storage_low_target, whose plan leaves move too: the reference's energy
 # anchors three of the space solve's starts, so a valved plan can land in
 # another basin. Unvalved fixtures do not move.
+# R10-COP-GATE-D: the plan carries the band it was solved on and the model
+# status sensor publishes which electrical maximum the plan used, so every
+# coord capture gains `data.pump_max_power` and, under
+# `sensors.model_status.extra_state_attributes`, `pump_max_power`,
+# `pump_max_power_reason` and `pump_max_power_source`. Those four leaves are
+# the whole diff in each fixture, each "present on one side only" and ADDED at
+# this head (the direction); no other leaf moves (tests/env_drift.py --all
+# origin/main, one environment). Claimed rather than re-recorded, as
+# R10-HOUSE-GRADE's key was: the committed files were patched in those four
+# paths alone, each null because a coord fixture holds no plan.
diff --git a/tests/golden/coord_all_features.json b/tests/golden/coord_all_features.json
index b3b42b419..0b8b10450 100644
--- a/tests/golden/coord_all_features.json
+++ b/tests/golden/coord_all_features.json
@@ -528,6 +528,7 @@
   "problem_messages": [],
   "projected_peak_cost": 0.0,
   "projected_peak_kw": 0.0,
+  "pump_max_power": null,
   "pv": {
    "export_price": 0.3,
    "forecast_production_kwh": 15.36,
@@ -2126,6 +2127,9 @@
      "ratio": 1.0,
      "samples": 0
     },
+    "pump_max_power": null,
+    "pump_max_power_reason": null,
+    "pump_max_power_source": null,
     "solar_aperture": {
      "needed": 30,
      "samples": 0,
diff --git a/tests/golden/coord_dhw.json b/tests/golden/coord_dhw.json
index 1895c8ffe..573f6e817 100644
--- a/tests/golden/coord_dhw.json
+++ b/tests/golden/coord_dhw.json
@@ -520,6 +520,7 @@
   "problem_messages": [],
   "projected_peak_cost": 0.0,
   "projected_peak_kw": 0.0,
+  "pump_max_power": null,
   "pv": {},
   "pv_enabled": false,
   "pv_self_consumed_kwh": 0.0,
@@ -2047,6 +2048,9 @@
      "ratio": 1.0,
      "samples": 0
     },
+    "pump_max_power": null,
+    "pump_max_power_reason": null,
+    "pump_max_power_source": null,
     "solar_aperture": {
      "needed": 30,
      "samples": 0,
diff --git a/tests/golden/coord_grid_fee.json b/tests/golden/coord_grid_fee.json
index 673db3b96..4ea16f016 100644
--- a/tests/golden/coord_grid_fee.json
+++ b/tests/golden/coord_grid_fee.json
@@ -455,6 +455,7 @@
   "problem_messages": [],
   "projected_peak_cost": 0.0,
   "projected_peak_kw": 0.0,
+  "pump_max_power": null,
   "pv": {},
   "pv_enabled": false,
   "pv_self_consumed_kwh": 0.0,
@@ -1890,6 +1891,9 @@
      "ratio": 1.0,
      "samples": 0
     },
+    "pump_max_power": null,
+    "pump_max_power_reason": null,
+    "pump_max_power_source": null,
     "solar_aperture": {
      "needed": 30,
      "samples": 0,
diff --git a/tests/golden/coord_minimal.json b/tests/golden/coord_minimal.json
index 81cf31074..853ee5b02 100644
--- a/tests/golden/coord_minimal.json
+++ b/tests/golden/coord_minimal.json
@@ -455,6 +455,7 @@
   "problem_messages": [],
   "projected_peak_cost": 0.0,
   "projected_peak_kw": 0.0,
+  "pump_max_power": null,
   "pv": {},
   "pv_enabled": false,
   "pv_self_consumed_kwh": 0.0,
@@ -1890,6 +1891,9 @@
      "ratio": 1.0,
      "samples": 0
     },
+    "pump_max_power": null,
+    "pump_max_power_reason": null,
+    "pump_max_power_source": null,
     "solar_aperture": {
      "needed": 30,
      "samples": 0,
diff --git a/tests/golden/coord_two_zone.json b/tests/golden/coord_two_zone.json
index 6a947b460..6998095e4 100644
--- a/tests/golden/coord_two_zone.json
+++ b/tests/golden/coord_two_zone.json
@@ -465,6 +465,7 @@
   "problem_messages": [],
   "projected_peak_cost": 0.0,
   "projected_peak_kw": 0.0,
+  "pump_max_power": null,
   "pv": {},
   "pv_enabled": false,
   "pv_self_consumed_kwh": 0.0,
@@ -1936,6 +1937,9 @@
      "ratio": 1.0,
      "samples": 0
     },
+    "pump_max_power": null,
+    "pump_max_power_reason": null,
+    "pump_max_power_source": null,
     "solar_aperture": {
      "needed": 30,
      "samples": 0,
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_manual_release.GUARD_OFF.e973f3a4.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_manual_release.GUARD_OFF.e973f3a4.json
deleted file mode 100644
index 2d5f00ffc..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_manual_release.GUARD_OFF.e973f3a4.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._record_manual_release GUARD_OFF e973f3a4",
-  "killed_by": "tests/features.py",
-  "old": "        if override is None:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_band_fields.GUARD_OFF.7ead7e8a.json b/tests/mutation_ledger/killed_by/coordinator.py/_band_fields.GUARD_OFF.7ead7e8a.json
new file mode 100644
index 000000000..254991df7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_band_fields.GUARD_OFF.7ead7e8a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_band_fields GUARD_OFF 7ead7e8a",
+  "killed_by": "tests/features.py",
+  "old": "    if band.source == \"configured\":",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_band_fields.RETURN_DEL.b3c33916.json b/tests/mutation_ledger/killed_by/coordinator.py/_band_fields.RETURN_DEL.b3c33916.json
new file mode 100644
index 000000000..8600e5843
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_band_fields.RETURN_DEL.b3c33916.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_band_fields RETURN_DEL b3c33916",
+  "killed_by": "tests/features.py",
+  "old": "    return {\"max_electrical_power\": band.max_kw, \"min_electrical_power\": band.min_kw}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_record_manual_release.GUARD_OFF.8dc0f9a5.json b/tests/mutation_ledger/killed_by/coordinator.py/_record_manual_release.GUARD_OFF.8dc0f9a5.json
new file mode 100644
index 000000000..ab16b5169
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_record_manual_release.GUARD_OFF.8dc0f9a5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_record_manual_release GUARD_OFF 8dc0f9a5",
+  "killed_by": "tests/features.py",
+  "old": "    if override is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_solve_band.RETURN_DEL.0d061913.json b/tests/mutation_ledger/killed_by/coordinator.py/_solve_band.RETURN_DEL.0d061913.json
new file mode 100644
index 000000000..62ac6506d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_solve_band.RETURN_DEL.0d061913.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_solve_band RETURN_DEL 0d061913",
+  "killed_by": "tests/features.py",
+  "old": "    return draw_range.solve_band(draw, hub, probe_install(config), dt_util.now().timestamp())",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/solve_band.CLAMP_DROP.4d045bab.json b/tests/mutation_ledger/killed_by/draw_range.py/solve_band.CLAMP_DROP.4d045bab.json
new file mode 100644
index 000000000..2094357ea
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/solve_band.CLAMP_DROP.4d045bab.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:solve_band CLAMP_DROP 4d045bab",
+  "killed_by": "tests/features.py",
+  "old": "        cfg_max, learned, min(cfg_min, learned), \"ceiling_probe\",",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`cfg_max, learned, (cfg_min), \"ceiling_probe\",`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/solve_band.CMP_BOUND.87d22127.json b/tests/mutation_ledger/killed_by/draw_range.py/solve_band.CMP_BOUND.87d22127.json
new file mode 100644
index 000000000..46dbbfa1b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/solve_band.CMP_BOUND.87d22127.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:solve_band CMP_BOUND 87d22127",
+  "killed_by": "tests/features.py",
+  "old": "        return configured(\"lapsed\" if samples >= CEILING_MIN_SAMPLES else \"awaiting_probe\")",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return configured(\"lapsed\" if samples > CEILING_MIN_SAMPLES else \"awaiting_probe\")`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/solve_band.CMP_BOUND.d82c7c5e.json b/tests/mutation_ledger/killed_by/draw_range.py/solve_band.CMP_BOUND.d82c7c5e.json
new file mode 100644
index 000000000..82ecadf88
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/solve_band.CMP_BOUND.d82c7c5e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:solve_band CMP_BOUND d82c7c5e",
+  "killed_by": "tests/features.py",
+  "old": "    if learned >= (1.0 - AGREE_TOLERANCE) * cfg_max:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if learned > (1.0 - AGREE_TOLERANCE) * cfg_max:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/solve_band.GUARD_OFF.42b5905c.json b/tests/mutation_ledger/killed_by/draw_range.py/solve_band.GUARD_OFF.42b5905c.json
new file mode 100644
index 000000000..7bd638b28
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/solve_band.GUARD_OFF.42b5905c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:solve_band GUARD_OFF 42b5905c",
+  "killed_by": "tests/features.py",
+  "old": "    if learned is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/solve_band.GUARD_OFF.6a6c4f30.json b/tests/mutation_ledger/killed_by/draw_range.py/solve_band.GUARD_OFF.6a6c4f30.json
new file mode 100644
index 000000000..82783c6d8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/solve_band.GUARD_OFF.6a6c4f30.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:solve_band GUARD_OFF 6a6c4f30",
+  "killed_by": "tests/features.py",
+  "old": "    if cap.plan_writes_power():",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/solve_band.GUARD_OFF.d82c7c5e.json b/tests/mutation_ledger/killed_by/draw_range.py/solve_band.GUARD_OFF.d82c7c5e.json
new file mode 100644
index 000000000..6964d34b8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/solve_band.GUARD_OFF.d82c7c5e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:solve_band GUARD_OFF d82c7c5e",
+  "killed_by": "tests/features.py",
+  "old": "    if learned >= (1.0 - AGREE_TOLERANCE) * cfg_max:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._warm_start_starts.CLAMP_DROP.e8734c97.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._warm_start_starts.CLAMP_DROP.e8734c97.json
new file mode 100644
index 000000000..a52ca6caa
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._warm_start_starts.CLAMP_DROP.e8734c97.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._warm_start_starts CLAMP_DROP e8734c97",
+  "killed_by": "tests/features.py",
+  "old": "        return (np.clip(np.asarray(prev, dtype=float), 0.0, self.model.params.max_electrical_power),)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return ((np.asarray(prev, dtype=float)),)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._warm_start_starts.RETURN_DEL.e8734c97.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._warm_start_starts.RETURN_DEL.e8734c97.json
new file mode 100644
index 000000000..1a9f3e689
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._warm_start_starts.RETURN_DEL.e8734c97.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._warm_start_starts RETURN_DEL e8734c97",
+  "killed_by": "tests/features.py",
+  "old": "        return (np.clip(np.asarray(prev, dtype=float), 0.0, self.model.params.max_electrical_power),)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_band_kw.BOOLOP.55c98a93.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_band_kw.BOOLOP.55c98a93.json
new file mode 100644
index 000000000..3bb523ee5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_band_kw.BOOLOP.55c98a93.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_band_kw BOOLOP 55c98a93",
+  "killed_by": "tests/features.py",
+  "old": "    if band and _experiment_kw(inp) is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if band or _experiment_kw(inp) is None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_band_kw.GUARD_OFF.55c98a93.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_band_kw.GUARD_OFF.55c98a93.json
new file mode 100644
index 000000000..be3a2c8dc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_band_kw.GUARD_OFF.55c98a93.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_band_kw GUARD_OFF 55c98a93",
+  "killed_by": "tests/features.py",
+  "old": "    if band and _experiment_kw(inp) is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/seam_map.json b/tests/seam_map.json
index 17772e9b2..293f15c82 100644
--- a/tests/seam_map.json
+++ b/tests/seam_map.json
@@ -172,7 +172,6 @@
   "_reading_ok": "core",
   "_reanchor_house_heat_loss_scale": "learning",
   "_record_accuracy": "core",
-  "_record_manual_release": "core",
   "_record_quiet_comfort_period": "learning",
   "_refresh_model_corrections": "learning",
   "_release_registrations": "core",
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index aeee1873e..98bc6e02c 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17630,
+ "class_excess_loc": 17618,
  "const_modules_over_50": 3,
  "coordinator_attrs": 141,
  "coordinator_multiassigned_attrs": 108,
@@ -11,7 +11,7 @@
  "functions_cc_over_25": 8,
  "import_cycle_modules": 0,
  "max_cc": 44,
- "max_class_loc": 7975,
+ "max_class_loc": 7960,
  "max_method_loc": 373,
  "methods_over_150": 15,
  "methods_over_200": 8,

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
