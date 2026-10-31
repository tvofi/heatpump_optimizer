# Review packet #3022
head: d5ce36c662d21c6376cad6701d77f6c5ad15fe4d
base: cabfaadc3a13f61eaf0303918c7b1d5beda9c07c

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=124476215872 success
arch-score / arch-score id=124476117410 success
arm id=124476054089 skipped
budget-raise-gate / budget-raise-gate id=124476117363 success
cancel-superseded id=124476035635 success
codeql / Analyze (actions) id=124476117400 success
codeql / Analyze (javascript-typescript) id=124476117443 success
codeql / Analyze (python) id=124476117465 success
gate id=124485274847 success
governance / delivery-status id=124476117373 success
governance / delivery-status-publish id=124476118209 skipped
governance / env-matrix id=124476117405 success
governance / instrument-self-tests id=124476117343 success
governance / policy-docs id=124476117484 success
governance / record id=124476118386 skipped
governance / wave-script id=124476117372 success
hassfest / hassfest id=124476117401 success
kernel-points id=124476118157 skipped
pr-contract / pr-contract id=124485155256 success
prelude id=124476035958 success
refresh id=124476035843 success
tests / arch-instrument id=124476193450 success
tests / briefs id=124476117486 success
tests / browser id=124476193605 success
tests / ci-ratchet id=124481949694 skipped
tests / claims-autofix id=124479607796 skipped
tests / closure-scope id=124476117470 success
tests / closures id=124476193511 success
tests / closures-autofix id=124481842568 skipped
tests / coverage id=124476193411 success
tests / coverage-ratchet id=124481948731 success
tests / fast (3.14) id=124476193464 success
tests / graders-head-copy id=124481948688 success
tests / lane-proofs id=124482356335 success
tests / mutation id=124476117462 success
tests / mutation-autofix id=124485156190 skipped
tests / mutation-pins id=124485156353 skipped
tests / nightly-ha (2025.2.0) id=124476193512 success
tests / nightly-ha (stable) id=124476193430 success
tests / nightly-status id=124476117435 success
tests / replay id=124476193491 success
tests / typing id=124476193433 success
validate / validate-hacs id=124476117359 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item c40d50f7: R10-FACTORY-RESET: R10-FACTORY-RESET resolved on origin/handoff/audit-r10-roster
NOTE body item 34daf5c3: dismissed:not recognisable from the entity; the orchestrator may put the declaration option to proposal triage
NOTE body item b66f0cc2: dismissed:the reset action this PR adds is the remedy after such a change, and auto-voiding would also wipe converged learners on a like-for-like sensor replacement, which no measurement here prices
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified arm                                    base                                 head
             no segment of this names a program this check knows
  unverified unchanged sensors                      (1.2356, 1.943, 400, 400, 0.3396)    (1.2356, 1.943, 400, 400, 0.3396)
             no segment of this names a program this check knows
  unverified move: indoor=bthome, lower=t6          (1.2356, 1.943, 400, 400, 0.3396)    (1.0, 1.0, 0, 0, 0.19)
             no segment of this names a program this check knows
  unverified lower only: lower=t6                   (1.2356, 1.943, 400, 400, 0.3396)    (1.2356, 1.0, 400, 0, 0.2348)
             no segment of this names a program this check knows
  unverified null: outdoor + comfort_weight edit    (1.2356, 1.943, 400, 400, 0.3396)    (1.2356, 1.943, 400, 400, 0.3396)
             no segment of this names a program this check knows
  unverified zero evidence (1.0, 1.0, n=0), move    (1.0, 1.0, 0, 0, 0.19)               (1.0, 1.0, 0, 0, 0.19)
             no segment of this names a program this check knows
  unverified on the clamp (3.0, 3.0, n=400), move   (3.0, 3.0, 400, 400, 1.11)           (1.0, 1.0, 0, 0, 0.19)
             no segment of this names a program this check knows
  unverified basis: no power entity (null)          commanded                            commanded
             no segment of this names a program this check knows
  unverified basis: power = a revenue meter         metered                              metered
             no segment of this names a program this check knows
  unverified basis: power = the pump's own estimate metered                              metered
             no segment of this names a program this check knows
  ok         dev/audit/harnesses/learner_inputs_swap.py
             `dev/audit/harnesses/learner_inputs_swap.py` is in the tree at this head
  ok         python3 -I dev/audit/harnesses/learner_inputs_swap.py [TREE]
             `dev/audit/harnesses/learner_inputs_swap.py` is in the tree at this head
  unverified git archive
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tests/features.py
             `tests/features.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         tests/ha_contract.py
             `tests/ha_contract.py` is in the tree at this head
  ok         tests/layout.py
             `tests/layout.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/features.py
             `tests/features.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head

FIGURES: 11 resolved, 11 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._void_heat_loss_learners.GUARD_OFF.11a66faf.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._void_heat_loss_learners.GUARD_OFF.11a66faf.json
new file mode 100644
index 000000000..aee5b686b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._void_heat_loss_learners.GUARD_OFF.11a66faf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._void_heat_loss_learners GUARD_OFF 11a66faf",
+  "killed_by": "tests/features.py",
+  "old": "        if HEAT_LOSS_LEARNERS[1] in learners:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._void_heat_loss_learners.GUARD_OFF.5a8d9665.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._void_heat_loss_learners.GUARD_OFF.5a8d9665.json
new file mode 100644
index 000000000..b3d9507f6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._void_heat_loss_learners.GUARD_OFF.5a8d9665.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._void_heat_loss_learners GUARD_OFF 5a8d9665",
+  "killed_by": "tests/features.py",
+  "old": "        if HEAT_LOSS_LEARNERS[0] in learners:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._void_heat_loss_learners.RETURN_DEL.7055cd47.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._void_heat_loss_learners.RETURN_DEL.7055cd47.json
new file mode 100644
index 000000000..e6d13da18
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._void_heat_loss_learners.RETURN_DEL.7055cd47.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._void_heat_loss_learners RETURN_DEL 7055cd47",
+  "killed_by": "tests/features.py",
+  "old": "        return bool(learners)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/services.py/handle_reset_heat_loss.RETURN_DEL.d37047a8.json b/tests/mutation_ledger/killed_by/services.py/handle_reset_heat_loss.RETURN_DEL.d37047a8.json
new file mode 100644
index 000000000..acc06bc3e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/services.py/handle_reset_heat_loss.RETURN_DEL.d37047a8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/services.py:handle_reset_heat_loss RETURN_DEL d37047a8",
+  "killed_by": "tests/entities.py",
+  "old": "    return {\"reset\": reset, \"learners\": list(learners)}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/heat_loss_entity_voids.BOOLOP.19eef99a.json b/tests/mutation_ledger/killed_by/thermal_model.py/heat_loss_entity_voids.BOOLOP.19eef99a.json
new file mode 100644
index 000000000..3662bf48e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/heat_loss_entity_voids.BOOLOP.19eef99a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:heat_loss_entity_voids BOOLOP 19eef99a",
+  "killed_by": "tests/features.py",
+  "old": "        if key in was and (was[key] or None) != now.get(key)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if key in was or (was[key] or None) != now.get(key)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=15."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/heat_loss_entity_voids.GUARD_OFF.02cbf88f.json b/tests/mutation_ledger/killed_by/thermal_model.py/heat_loss_entity_voids.GUARD_OFF.02cbf88f.json
new file mode 100644
index 000000000..151c23b5a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/heat_loss_entity_voids.GUARD_OFF.02cbf88f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:heat_loss_entity_voids GUARD_OFF 02cbf88f",
+  "killed_by": "tests/features.py",
+  "old": "    if not isinstance(was, Mapping):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/heat_loss_zone_entities.RETURN_DEL.47e79f51.json b/tests/mutation_ledger/killed_by/thermal_model.py/heat_loss_zone_entities.RETURN_DEL.47e79f51.json
new file mode 100644
index 000000000..d6d377e51
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/heat_loss_zone_entities.RETURN_DEL.47e79f51.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:heat_loss_zone_entities RETURN_DEL 47e79f51",
+  "killed_by": "tests/features.py",
+  "old": "    return {key: cfg.get(key) or None for key in HEAT_LOSS_ZONE_ENTITIES}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}


## Three-dot diff
diff --git a/README.md b/README.md
index 8bc921ac2..2b2412ad5 100644
--- a/README.md
+++ b/README.md
@@ -511,7 +511,7 @@ Every field and its range is documented in
 
 ### Your first week
 
-- **Immediately.** All 81 entities appear and the first plan is solved within one
+- **Immediately.** All 82 entities appear and the first plan is solved within one
   optimization interval (30 minutes by default). Add the dashboard card and you
   can see what it intends to do.
 - **Day one.** If you want the commissioning step test, first switch on *Allow a
@@ -685,13 +685,14 @@ Heating Schedule, DHW Setpoint Advisor and Plan DHW Heating (next 24 h).
 | Mold Floor Breach | The measured room sits below the mold-safe floor the plan promises | Diagnostic; on when the measured room is below the mold floor by the configured margin (default 0.5 °C), typically because space heating is blocked. `floor_c`, `shortfall_c` and `space_blocked` in attributes |
 | Wood Cheaper Than Heat Pump | Burning wood costs less per kWh than running the heat pump | Disabled by default. Unavailable until the furnace is on, a wood-tank probe is set, external-heat detection or the DHW wood coil is on, type and packing are set, the billed price per m³ is greater than 0 (no silent default), and furnace efficiency is 10–95 %. A usable wood tank alone is not enough. Price and cheaper-hour count in attributes |
 
-### Buttons (5 total)
+### Buttons (6 total)
 
 | Button | What it does |
 |---|---|
 | Optimize Now | Force an optimization run. Unavailable while one is in flight |
 | Learning Run System Identification | Arm the commissioning step test for the next mild, cheap night. Inert until *Allow a one-off measurement experiment* is enabled on Advanced settings → Self-learning and diagnostics, which is off by default |
 | Learning Reset Comfort Weight | Undo the revealed-preference tuning |
+| Learning Reset Heat Loss | Return the learned house heat loss scale and lower floor loss ratio to 1.0, so the plan uses the heat loss values in the settings; learning starts again from there. The other learners are left alone |
 | Learning Finalize Debug Collection | End the week of debug data now, so Download diagnostics carries it final. Unavailable unless *Collect a week of debug data* is on and the collection has not already stopped |
 | Prediction Accuracy Diagnose Last Interval | Explain the last interval's temperature error input by input, on the Prediction Accuracy sensor |
 
@@ -763,7 +764,7 @@ that deliver them.
 
 ## Services
 
-13 services are registered under the `heatpump_optimizer` domain. Field-level
+14 services are registered under the `heatpump_optimizer` domain. Field-level
 detail for each — including all 31 fields of `set_thermal_parameters` — is in
 [docs/configuration.md](./docs/configuration.md). Worked automation examples — an
 EV charger following the Cost Power Headroom sensor, mode switching on price — are in
@@ -780,6 +781,7 @@ EV charger following the Cost Power Headroom sensor, mode switching on price —
 | `apply_manual_plan` | Pin exact run slots for up to 20 hours; the optimizer plans around them, and safety still releases any it cannot honour | Optional |
 | `clear_manual_plan` | Drop the manual plan and return to fully automatic planning | Optional |
 | `restore_learned_snapshot` | Roll every learner back to the last weekly snapshot taken with healthy inputs | Optional |
+| `reset_heat_loss_learners` | Return the learned house heat loss scale, the lower floor loss ratio, or both to 1.0 and re-plan; the other learners are left alone | Optional |
 | `diagnose_interval` | Attribute the last interval's temperature error input by input | Optional |
 | `debug_collect` | Start, stop or read the week of debug data that Download diagnostics carries | Optional |
 | `assign_entity` | Assign or clear one optional sensor slot | Optional |
diff --git a/custom_components/heatpump_optimizer/button.py b/custom_components/heatpump_optimizer/button.py
index c412d9ea0..6f94c7ebd 100644
--- a/custom_components/heatpump_optimizer/button.py
+++ b/custom_components/heatpump_optimizer/button.py
@@ -1,6 +1,6 @@
 """Button entities for Heat Pump Cost Optimizer.
 
-Five momentary actions with no lasting state, which is exactly what a
+Six momentary actions with no lasting state, which is exactly what a
 ``ButtonEntity`` is for. A switch would have to bounce itself back off, and
 until it did, the UI would imply a state that does not exist:
 
@@ -8,10 +8,12 @@ until it did, the UI would imply a state that does not exist:
 * "Learning Run System Identification" — arm the commissioning step test,
 * "Learning Reset Comfort Weight" — undo the revealed-preference comfort
   tuning,
+* "Learning Reset Heat Loss" — return the learned heat-loss scale and
+  lower-floor ratio to the configuration,
 * "Prediction Accuracy Diagnose Last Interval" — attribute the last
   interval's temperature residual,
 
-and a fifth, "Finalize Debug Collection", which ends the week's collection
+and a sixth, "Finalize Debug Collection", which ends the week's collection
 now and is unavailable unless that option is on.
 
 The runs take real time — an optimization fetches prices and weather and then
@@ -55,6 +57,7 @@ async def async_setup_entry(
         ForceOptimizationButton(coordinator, entry),
         SystemIdentificationButton(coordinator, entry),
         ResetComfortWeightButton(coordinator, entry),
+        ResetHeatLossButton(coordinator, entry),
         DiagnoseIntervalButton(coordinator, entry),
     ]
     buttons.append(DebugFinalizeButton(coordinator, entry))
@@ -172,6 +175,23 @@ class ResetComfortWeightButton(_OptimizerButtonBase):
         off_the_action(self, self.coordinator.async_request_refresh())
 
 
+class ResetHeatLossButton(_OptimizerButtonBase):
+    """Return both heat-loss learners to the configuration (R10-HOTFIX-LEARNER-INPUTS).
+
+    The house heat-loss scale and the lower-floor ratio, through the one
+    void path a zone-sensor swap takes; the coordinator re-plans.
+    """
+
+    def __init__(
+        self, coordinator: HeatPumpOptimizerCoordinator, entry: HeatPumpOptimizerConfigEntry
+    ) -> None:
+        super().__init__(coordinator, entry, "reset_heat_loss", "learning_reset_heat_loss")
+
+    async def async_press(self) -> None:
+        await self.coordinator.async_reset_heat_loss_learners()
+        off_the_action(self, self.coordinator.async_request_refresh())
+
+
 class DiagnoseIntervalButton(_OptimizerButtonBase):
     """Attribute the last interval's temperature residual (T6 #52).
 
diff --git a/custom_components/heatpump_optimizer/const.py b/custom_components/heatpump_optimizer/const.py
index 7302a27d4..9597b56d8 100644
--- a/custom_components/heatpump_optimizer/const.py
+++ b/custom_components/heatpump_optimizer/const.py
@@ -675,6 +675,8 @@ SERVICE_RESTORE_SNAPSHOT: Final = "restore_learned_snapshot"
 SERVICE_DIAGNOSE_INTERVAL: Final = "diagnose_interval"
 #: #1939 — start, stop or read an entry's debug collection.
 SERVICE_DEBUG_COLLECT: Final = "debug_collect"
+#: R10-HOTFIX-LEARNER-INPUTS — the heat-loss learners back to the configuration.
+SERVICE_RESET_HEAT_LOSS: Final = "reset_heat_loss_learners"
 MANUAL_PLAN_STORE_VERSION: Final = 1
 # A full solve is seconds of CPU. Dragging a slider must not trigger one per
 # pixel, so simulation requests are rate-limited to this interval.
@@ -1424,6 +1426,9 @@ LOWER_FLOOR_LOSS_RATIO_MAX: Final = 3.0
 # selector, where no interval is space-only. A counter install folds the
 # scale at span close alone, so it mixes nothing.
 HEAT_LOSS_BASES: Final = ("commanded", "metered", "measured_heat")
+#: The heat-loss learners by their store key: what the one void path
+#: (``_void_heat_loss_learners``) resets and the reset action's ``learners`` offers.
+HEAT_LOSS_LEARNERS: Final = ("house_heat_loss_scale", "lower_floor_loss_ratio")
 
 # DHW demand window defaults
 DEFAULT_DHW_SCHEDULE_ENABLED: Final = True
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index b4b07c4ea..075ac67b5 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -119,6 +119,7 @@ from .const import (
     HOUSE_HEAT_LOSS_SCALE_MAX,
     HOUSE_HEAT_LOSS_SCALE_MIN,
     DEFAULT_LOWER_FLOOR_LOSS_RATIO,
+    HEAT_LOSS_LEARNERS,
     LOWER_FLOOR_LOSS_RATIO_MAX,
     LOWER_FLOOR_LOSS_RATIO_MIN,
     DHW_COOLING_REFERENCE_DELTA,
@@ -330,6 +331,8 @@ from .thermal_model import (
     heat_loss_anchor_pair,
     heat_loss_basis,
     heat_loss_basis_voids,
+    heat_loss_entity_voids,
+    heat_loss_zone_entities,
     learner_newton_step,
     learner_room_unread,
     mold_safe_room_floor,
@@ -1457,7 +1460,7 @@ HOUSE_LOSS_SAMPLE_BOUNDS_H = (HOUSE_LOSS_MIN_SAMPLE_HOURS, HOUSE_LOSS_MAX_SAMPLE
 # ``HOUSE_LOSS_ALPHA * _LEARNER_TRUST_REGION`` of it (``learner_newton_step``).
 HOUSE_LOSS_MAX_STEP = 0.05
 # What the re-anchor reads back; a store missing any is adopted on load.
-_HEAT_LOSS_ANCHOR_KEYS = ("house_heat_loss_anchor", "lower_floor_loss_anchor", "house_heat_loss_basis")
+_HEAT_LOSS_ANCHOR_KEYS = ("house_heat_loss_anchor", "lower_floor_loss_anchor", "house_heat_loss_basis", "heat_loss_zone_entities")
 # Residuals beyond this are a door left open, a wood stove, or a sensor glitch
 # rather than a heat loss error.
 HOUSE_LOSS_MAX_RESIDUAL = 1.0  # °C
@@ -4247,11 +4250,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             except (TypeError, ValueError, OverflowError) as err:
                 _LOGGER.debug("Could not load lower floor loss ratio: %s", err)
 
-        # v5.7.0 (issue #86): the store records the UA the scale was fitted
-        # against, and an options edit that changed it is corrected here --
-        # on load, before anything solves -- not restored verbatim. The
-        # gated write adopts an anchor for a pre-fix store and re-anchors;
-        # `updated_at` defeats the content-hash skip, so not unconditionally.
+        # Re-anchored before anything solves; gated write: `updated_at` defeats the hash skip.
         _had_anchor = all(k in stored for k in _HEAT_LOSS_ANCHOR_KEYS)
         _reanchored = self._reanchor_house_heat_loss_scale(stored)
         if _reanchored or not _had_anchor:
@@ -4382,10 +4381,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         return {
             "buffer_cooling_rate": self._buffer_cooling_rate,
             "buffer_cooling_samples": self._buffer_cooling_samples,
-            # The configured UA and power basis the learners were fitted
-            # against, so an options edit can be corrected on load instead of
-            # multiplying a correction by the new nameplate (issue #86, #2239;
-            # _reanchor_house_heat_loss_scale; dev/archive/backlog.md "Open").
+            # What the learners were fitted against, read back on load (_reanchor_house_heat_loss_scale).
             **self._heat_loss_anchors(),
             "house_heat_loss_scale": self._house_heat_loss_scale,
             "house_heat_loss_samples": self._house_heat_loss_samples,
@@ -5170,14 +5166,31 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         self._lower_floor_loss_ratio = float(np.clip(ratio, LOWER_FLOOR_LOSS_RATIO_MIN, LOWER_FLOOR_LOSS_RATIO_MAX))
         _publish_params(self, lower_floor_loss_ratio=self._lower_floor_loss_ratio)
 
+    def _void_heat_loss_learners(self, learners: Sequence[str], why: str) -> bool:
+        """The one void path (a zone-sensor swap, the reset action): each named learner to 1.0, no samples."""
+        if HEAT_LOSS_LEARNERS[0] in learners:
+            self._apply_house_heat_loss_scale(DEFAULT_HOUSE_HEAT_LOSS_SCALE)
+            self._house_heat_loss_samples = 0
+        if HEAT_LOSS_LEARNERS[1] in learners:
+            self._apply_lower_floor_loss_ratio(DEFAULT_LOWER_FLOOR_LOSS_RATIO)
+            self._lower_floor_loss_samples = 0
+        for learner in learners:
+            _LOGGER.warning("Learned %s reset to the configuration: %s", learner, why)
+        return bool(learners)
+
+    async def async_reset_heat_loss_learners(self, learners: Sequence[str] = HEAT_LOSS_LEARNERS) -> None:
+        """The reset action: void ``learners`` and save; the button and the service refresh."""
+        await self._thermal_learning_store.async_wait_for_read()
+        self._void_heat_loss_learners(learners, "reset on request")
+        await self._async_save_thermal_learning()
+
     def _house_heat_loss_anchor(self) -> float:
         """The total base UA the learned scale currently multiplies.
 
         In two-zone mode the scale owns the *level* of both zones -- the
         ratio owns the split -- so the quantity it multiplies is the zone
         total with the learned ratio applied, not the upper zone the fit
-        reads. Round 1 of the re-anchor got exactly this wrong and went
-        sign-negative on every single-zone edit in a two-zone house.
+        reads (taking the upper zone went sign-negative on single-zone edits).
         """
         p = getattr(self, "_ctx", self)._thermal_params
         if p.two_zone_enabled:
@@ -5195,19 +5208,16 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             "lower_floor_loss_anchor": ctx._thermal_params.lower_floor_heat_loss
             if ctx._thermal_params.two_zone_enabled else None,
             "house_heat_loss_basis": heat_loss_basis(ctx._config, heat_energy.meter_of(self).earned),
+            "heat_loss_zone_entities": heat_loss_zone_entities(ctx._config),
         }
 
     def _reanchor_house_heat_loss_scale(self, stored: Mapping[str, Any]) -> bool:
         """Re-express the learned scale and ratio against the UA now configured.
 
-        An options edit reloads the entry with new nameplates while the store
-        still holds corrections fitted against the old ones; restoring them
-        verbatim left the model up to 1.94x wrong (issue #86, four prior
-        attempts recorded in dev/archive/backlog.md), and re-expressing the
-        scale alone mis-split the zones (#2239). The law is
-        ``reanchor_heat_loss``'s, on the nameplates ``heat_loss_anchor_pair``
-        reads from the anchors the payload records. Two guards, both from
-        the recorded decisions:
+        Restoring corrections fitted against other nameplates verbatim left
+        the model up to 1.94x wrong (#86), re-expressing the scale alone
+        mis-split the zones (#2239). The law is ``reanchor_heat_loss``'s, on
+        the nameplates ``heat_loss_anchor_pair`` reads from the stored anchors:
 
         * **Threshold gate.** Below a ``HOUSE_LOSS_MAX_STEP`` change of the
           total and of the nameplate split the store is kept verbatim: below
@@ -5222,26 +5232,25 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         A basis earlier than the one in force (G-ID-3: a power meter added, or
         a measured heat earned, ``_async_earn_heat_basis``) voids both
         learners' evidence, so the law runs at zero confidence. A stored
-        ``measured_heat`` restores the earned basis first.
-
-        Returns whether the stored state changed, so callers can gate
-        the one persistence write (``updated_at`` moves every save, so
-        the content-hash skip cannot gate this store).
-        """
+        ``measured_heat`` restores the earned basis first. A changed zone
+        sensor voids its learner (``heat_loss_entity_voids``) first, the stored total
+        re-expressed at the voided ratio so the law cannot write it back. Returns
+        whether the stored state changed, so callers can gate the one write."""
         heat_energy.meter_of(self).restore_basis(stored.get("house_heat_loss_basis"))
-        anchor = finite_float(stored.get("house_heat_loss_anchor"), 0.0)
+        ratio_was, lower_then = self._lower_floor_loss_ratio, finite_float(stored.get("lower_floor_loss_anchor"), 0.0)
+        swapped = self._void_heat_loss_learners(heat_loss_entity_voids(stored, self._heat_loss_anchors()), "its zone sensor changed")
+        anchor = finite_float(stored.get("house_heat_loss_anchor"), 0.0) - lower_then * (ratio_was - self._lower_floor_loss_ratio)
         live, ratio = self._heat_loss_anchors(), self._lower_floor_loss_ratio
-        current = live["house_heat_loss_anchor"]
         void = heat_loss_basis_voids(stored.get("house_heat_loss_basis"), live["house_heat_loss_basis"])
         pair = heat_loss_anchor_pair(
-            (anchor, finite_float(stored.get("lower_floor_loss_anchor"), 0.0)),
-            (current, live["lower_floor_loss_anchor"]),
+            (anchor, lower_then),
+            (live["house_heat_loss_anchor"], live["lower_floor_loss_anchor"]),
             ratio, void=void, step=HOUSE_LOSS_MAX_STEP,
         )
         if pair is None:
             # Below the gate, or a pre-fix store with no anchor to re-express,
             # which the caller adopts on its next save.
-            return False
+            return swapped
         if void:
             self._house_heat_loss_samples = self._lower_floor_loss_samples = 0
         phi = (house_loss_confidence(self._house_heat_loss_samples), house_loss_confidence(self._lower_floor_loss_samples))
@@ -5261,7 +5270,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             _LOGGER.warning(
                 "Learned house heat loss scale %.3f (fitted against %.4f kW/°C, %d samples) cannot be "
                 "expressed against the newly configured %.4f kW/°C: resetting to the configuration",
-                self._house_heat_loss_scale, anchor, self._house_heat_loss_samples, current,
+                self._house_heat_loss_scale, anchor, self._house_heat_loss_samples, live["house_heat_loss_anchor"],
             )
             self._house_heat_loss_samples, phi = 0, (0.0, phi[1])
         _LOGGER.info(
@@ -5269,7 +5278,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             "against the configured UA %.4f -> %.4f kW/°C (confidence %.2f, %.2f; "
             "evidence voided by a later basis: %s)",
             self._house_heat_loss_scale, new_scale, ratio, new_ratio,
-            anchor, current, *phi, void,
+            anchor, live["house_heat_loss_anchor"], *phi, void,
         )
         self._apply_house_heat_loss_scale(new_scale)
         self._apply_lower_floor_loss_ratio(new_ratio)
@@ -9321,18 +9330,12 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             # pre-T7 snapshot restores it to inert. The fallback latch does
             # NOT ride this path — see _async_load_thermal_learning.
             self._freq_map = FrequencyMap()
-            # #1067: and the flow-curve bias, for exactly the reason above.
-            # A snapshot from before this feature carries no ``flow_bias``
-            # key, so without this reset the restore would silently keep the
-            # drifted bias it was asked to roll back.
+            # #1067: the flow-curve bias too, for the reason above: a snapshot
+            # without ``flow_bias`` restores it inert, not drifted.
             self._flow_bias = FlowCurveBias()
             self._load_t4b_learners(thermal)
-            # v5.7.0 (issue #86): a snapshot from before an options edit
-            # carries a scale fitted against the pre-edit anchor; restoring
-            # it verbatim here would re-install the pre-edit correction
-            # against the new configuration. The same law the loader uses,
-            # without the save -- snapshots are restores, and the next
-            # regular save records the fresh anchor.
+            # A pre-edit snapshot is re-anchored as the loader does, without the
+            # save: the next regular save records the fresh anchors.
             self._reanchor_house_heat_loss_scale(thermal)
         profile = learners.get("dhw_profile")
         if isinstance(profile, dict):
diff --git a/custom_components/heatpump_optimizer/icons.json b/custom_components/heatpump_optimizer/icons.json
index d087d58e9..bbe71b405 100644
--- a/custom_components/heatpump_optimizer/icons.json
+++ b/custom_components/heatpump_optimizer/icons.json
@@ -43,6 +43,9 @@
       "learning_reset_comfort_weight": {
         "default": "mdi:restore"
       },
+      "learning_reset_heat_loss": {
+        "default": "mdi:home-thermometer-outline"
+      },
       "learning_run_system_identification": {
         "default": "mdi:flask-outline"
       },
@@ -327,6 +330,9 @@
     "diagnose_interval": {
       "service": "mdi:stethoscope"
     },
+    "reset_heat_loss_learners": {
+      "service": "mdi:home-thermometer-outline"
+    },
     "restore_learned_snapshot": {
       "service": "mdi:backup-restore"
     },
diff --git a/custom_components/heatpump_optimizer/services.py b/custom_components/heatpump_optimizer/services.py
index aa51e0bc1..456411380 100644
--- a/custom_components/heatpump_optimizer/services.py
+++ b/custom_components/heatpump_optimizer/services.py
@@ -1,4 +1,4 @@
-"""The domain's thirteen services: schemas, handlers and registration.
+"""The domain's fourteen services: schemas, handlers and registration.
 
 Moved verbatim from ``__init__.py`` (#222, the decomposition program's
 opener; the block used to be ``_async_register_services`` and the module
@@ -56,6 +56,7 @@ from .const import (
     DEFAULT_DHW_MIN_TEMP,
     DEFAULT_DHW_SETPOINT,
     DHW_MIN_TEMP_SETPOINT_MARGIN,
+    HEAT_LOSS_LEARNERS,
     CONF_TOPOLOGY_LAYOUT,
     CONF_TOPOLOGY_POSITIONS,
     SERVICE_APPLY_SCHEDULE,
@@ -65,6 +66,7 @@ from .const import (
     SERVICE_CLEAR_MANUAL_PLAN,
     SERVICE_DEBUG_COLLECT,
     SERVICE_DIAGNOSE_INTERVAL,
+    SERVICE_RESET_HEAT_LOSS,
     SERVICE_RESTORE_SNAPSHOT,
     SERVICE_RUN_OPTIMIZATION,
     SERVICE_SET_AWAY,
@@ -287,6 +289,14 @@ SERVICE_SCHEMA_RESTORE_SNAPSHOT = vol.Schema(
     }
 )
 
+SERVICE_SCHEMA_RESET_HEAT_LOSS = vol.Schema(
+    {
+        vol.Optional("entry_id"): cv.string,
+        # Empty or absent: both learners.
+        vol.Optional("learners", default=list): [vol.In(HEAT_LOSS_LEARNERS)],
+    }
+)
+
 SERVICE_SCHEMA_DIAGNOSE_INTERVAL = vol.Schema(
     {
         vol.Optional("entry_id"): cv.string,
@@ -1154,6 +1164,17 @@ async def handle_clear_manual_plan(hass: HomeAssistant, call: ServiceCall) -> di
         cleared.append(entry_id)
     return {"cleared": cleared}
 
+async def handle_reset_heat_loss(hass: HomeAssistant, call: ServiceCall) -> dict[str, Any]:
+    """Return the named heat-loss learners (default both) to the configuration and re-plan."""
+    data = dict(call.data)
+    learners = tuple(data.get("learners") or HEAT_LOSS_LEARNERS)
+    reset: list[str] = []
+    for entry_id, coord in _manual_targets(hass, data.get("entry_id")):
+        await coord.async_reset_heat_loss_learners(learners)
+        await coord.async_request_refresh()
+        reset.append(entry_id)
+    return {"reset": reset, "learners": list(learners)}
+
 async def handle_restore_snapshot(hass: HomeAssistant, call: ServiceCall) -> dict[str, Any]:
     """Roll the learners back to the newest trustworthy snapshot (#42).
 
@@ -1305,6 +1326,13 @@ def async_register_services(hass: HomeAssistant) -> None:
         schema=SERVICE_SCHEMA_RESTORE_SNAPSHOT,
         supports_response=SupportsResponse.OPTIONAL,
     )
+    hass.services.async_register(
+        DOMAIN,
+        SERVICE_RESET_HEAT_LOSS,
+        partial(handle_reset_heat_loss, hass),
+        schema=SERVICE_SCHEMA_RESET_HEAT_LOSS,
+        supports_response=SupportsResponse.OPTIONAL,
+    )
     hass.services.async_register(
         DOMAIN,
         SERVICE_DIAGNOSE_INTERVAL,
diff --git a/custom_components/heatpump_optimizer/services.yaml b/custom_components/heatpump_optimizer/services.yaml
index 67bb08ccd..9cac097bc 100644
--- a/custom_components/heatpump_optimizer/services.yaml
+++ b/custom_components/heatpump_optimizer/services.yaml
@@ -533,6 +533,20 @@ restore_learned_snapshot:
           options:
           - snapshot
           - refit
+reset_heat_loss_learners:
+  fields:
+    entry_id:
+      selector:
+        text: null
+    learners:
+      example:
+      - house_heat_loss_scale
+      selector:
+        select:
+          multiple: true
+          options:
+          - house_heat_loss_scale
+          - lower_floor_loss_ratio
 diagnose_interval:
   fields:
     entry_id:
diff --git a/custom_components/heatpump_optimizer/store.py b/custom_components/heatpump_optimizer/store.py
index 58549ff0b..706aea6d1 100644
--- a/custom_components/heatpump_optimizer/store.py
+++ b/custom_components/heatpump_optimizer/store.py
@@ -326,6 +326,11 @@ DOMAINS: dict[str, dict[str, Domain | str]] = {
         "house_heat_loss_basis": Domain("choice", choices=c.HEAT_LOSS_BASES, unread=(
             "earned at the first measured-heat fold, else re-derived from the configured "
             "meters on save; the load reads it to void evidence on an earlier basis")),
+        # R10-HOTFIX-LEARNER-INPUTS: the zone sensors each heat-loss learner was fitted on.
+        "heat_loss_zone_entities/~": Domain("choice", choices=(c.CONF_INDOOR_TEMP_ENTITY, c.CONF_LOWER_FLOOR_TEMP_ENTITY)),
+        "heat_loss_zone_entities/*": Domain("text", null=True, unread=(
+            "re-derived from the configured zone sensors on save; the load reads it to void "
+            "a learner whose sensor changed")),
         c.CONF_COP_SCALE: Domain("real", c.COP_SCALE_MIN, c.COP_SCALE_MAX),
         **{f"{k}_samples": _COUNT for k in ("buffer_cooling", "house_heat_loss", "lower_floor_loss", "cop")},
         # MeasuredCop.from_dict: the learner refuses a COP at or under 0.1 before rounding.
diff --git a/custom_components/heatpump_optimizer/strings.json b/custom_components/heatpump_optimizer/strings.json
index 67ef0dc61..13977fde4 100644
--- a/custom_components/heatpump_optimizer/strings.json
+++ b/custom_components/heatpump_optimizer/strings.json
@@ -2051,6 +2051,9 @@
       "learning_reset_comfort_weight": {
         "name": "Learning Reset Comfort Weight"
       },
+      "learning_reset_heat_loss": {
+        "name": "Learning Reset Heat Loss"
+      },
       "learning_run_system_identification": {
         "name": "Learning Run System Identification"
       },
@@ -2469,6 +2472,20 @@
         }
       }
     },
+    "reset_heat_loss_learners": {
+      "name": "Reset Heat Loss Learning",
+      "description": "Return the learned house heat loss scale and the learned lower floor loss ratio to 1.0, so the plan uses the heat loss values in the settings as they stand, and the learners start collecting evidence again from there. Use this after you have corrected those settings, moved a temperature sensor, or when the learned values have visibly gone wrong. Only these two are reset: the comfort weight, the hot water, COP and defrost learners are left as they are. The plan is recalculated straight away.",
+      "fields": {
+        "entry_id": {
+          "name": "Config entry",
+          "description": "Restrict the reset to one config entry. Leave empty to reset every configured heat pump."
+        },
+        "learners": {
+          "name": "Learners",
+          "description": "Which to reset: the house heat loss scale, the lower floor loss ratio, or both. Leave empty to reset both."
+        }
+      }
+    },
     "diagnose_interval": {
       "name": "Diagnose Last Interval",
       "description": "Explain the last interval's temperature error, input by input. The optimizer re-runs the interval that just settled through its own thermal model, swapping one realised input at a time into the plan's assumptions — measured power for commanded power, realised outdoor temperature for the forecast, realised solar for the assumed — and reports how much of the error each swap explains. What no swap explains is the model's own residual, reported as \"unexplained\". The result is published on the Prediction Accuracy sensor and returned as the service response.",
diff --git a/custom_components/heatpump_optimizer/thermal_model.py b/custom_components/heatpump_optimizer/thermal_model.py
index 3fb84bc92..07d5f48cb 100644
--- a/custom_components/heatpump_optimizer/thermal_model.py
+++ b/custom_components/heatpump_optimizer/thermal_model.py
@@ -1488,6 +1488,39 @@ def heat_loss_basis(config: Any, earned: bool = False) -> str:
     return const.HEAT_LOSS_BASES[2 if earned and cap.measured_heat else 1 if cap.measured_power else 0]
 
 
+#: The temperature entity each heat-loss learner fits its residual on, by
+#: config key (R10-HOTFIX-LEARNER-INPUTS): the scale the indoor (upper zone)
+#: sensor, the ratio the lower floor's. Evidence fitted against one sensor
+#: says nothing about a sensor in another place.
+HEAT_LOSS_ZONE_ENTITIES: dict[str, str] = {
+    const.CONF_INDOOR_TEMP_ENTITY: const.HEAT_LOSS_LEARNERS[0],
+    const.CONF_LOWER_FLOOR_TEMP_ENTITY: const.HEAT_LOSS_LEARNERS[1],
+}
+
+
+def heat_loss_zone_entities(config: Any) -> dict[str, str | None]:
+    """The ``HEAT_LOSS_ZONE_ENTITIES`` ids configured now, ``None`` where unset."""
+    cfg = config or {}
+    return {key: cfg.get(key) or None for key in HEAT_LOSS_ZONE_ENTITIES}
+
+
+def heat_loss_entity_voids(stored: Mapping[str, Any], live: Mapping[str, Any]) -> tuple[str, ...]:
+    """The learners whose zone entity id changed since their evidence was saved.
+
+    ``stored`` and ``live`` are the thermal-learning payload as saved and as
+    the configuration writes it now; each holds ``heat_loss_zone_entities``.
+    An added or removed entity is a change. A store from before the record,
+    or a key it does not hold, voids nothing: the next save adopts the ids.
+    """
+    was, now = stored.get("heat_loss_zone_entities"), live.get("heat_loss_zone_entities") or {}
+    if not isinstance(was, Mapping):
+        return ()
+    return tuple(
+        learner for key, learner in HEAT_LOSS_ZONE_ENTITIES.items()
+        if key in was and (was[key] or None) != now.get(key)
+    )
+
+
 def heat_loss_basis_voids(stored: Any, basis: str) -> bool:
     """Whether evidence fitted on ``stored`` is void on ``basis`` (an earlier one)."""
     bases = const.HEAT_LOSS_BASES
diff --git a/custom_components/heatpump_optimizer/translations/en.json b/custom_components/heatpump_optimizer/translations/en.json
index 950f65ad6..389553bcf 100644
--- a/custom_components/heatpump_optimizer/translations/en.json
+++ b/custom_components/heatpump_optimizer/translations/en.json
@@ -2051,6 +2051,9 @@
       "learning_reset_comfort_weight": {
         "name": "Learning Reset Comfort Weight"
       },
+      "learning_reset_heat_loss": {
+        "name": "Learning Reset Heat Loss"
+      },
       "learning_run_system_identification": {
         "name": "Learning Run System Identification"
       },
@@ -2469,6 +2472,20 @@
         }
       }
     },
+    "reset_heat_loss_learners": {
+      "name": "Reset Heat Loss Learning",
+      "description": "Return the learned house heat loss scale and the learned lower floor loss ratio to 1.0, so the plan uses the heat loss values in the settings as they stand, and the learners start collecting evidence again from there. Use this after you have corrected those settings, moved a temperature sensor, or when the learned values have visibly gone wrong. Only these two are reset: the comfort weight, the hot water, COP and defrost learners are left as they are. The plan is recalculated straight away.",
+      "fields": {
+        "entry_id": {
+          "name": "Config entry",
+          "description": "Restrict the reset to one config entry. Leave empty to reset every configured heat pump."
+        },
+        "learners": {
+          "name": "Learners",
+          "description": "Which to reset: the house heat loss scale, the lower floor loss ratio, or both. Leave empty to reset both."
+        }
+      }
+    },
     "diagnose_interval": {
       "name": "Diagnose Last Interval",
       "description": "Explain the last interval's temperature error, input by input. The optimizer re-runs the interval that just settled through its own thermal model, swapping one realised input at a time into the plan's assumptions — measured power for commanded power, realised outdoor temperature for the forecast, realised solar for the assumed — and reports how much of the error each swap explains. What no swap explains is the model's own residual, reported as \"unexplained\". The result is published on the Prediction Accuracy sensor and returned as the service response.",
diff --git a/custom_components/heatpump_optimizer/translations/sv.json b/custom_components/heatpump_optimizer/translations/sv.json
index d9f0a22eb..f0f050a88 100644
--- a/custom_components/heatpump_optimizer/translations/sv.json
+++ b/custom_components/heatpump_optimizer/translations/sv.json
@@ -2051,6 +2051,9 @@
       "learning_reset_comfort_weight": {
         "name": "Inlärning återställ komfortvikt"
       },
+      "learning_reset_heat_loss": {
+        "name": "Inlärning återställ värmeförlust"
+      },
       "learning_run_system_identification": {
         "name": "Inlärning kör systemidentifiering"
       },
@@ -2469,6 +2472,20 @@
         }
       }
     },
+    "reset_heat_loss_learners": {
+      "name": "Återställ värmeförlustinlärning",
+      "description": "Återställ den inlärda värmeförlustskalan för huset och det inlärda förlustförhållandet för nedervåningen till 1,0, så att planen använder värmeförlustvärdena i inställningarna som de står, och inlärningen börjar samla underlag igen därifrån. Använd detta när du har rättat de inställningarna, flyttat en temperaturgivare, eller när de inlärda värdena uppenbart har blivit fel. Bara dessa två återställs: komfortvikten och inlärningen för varmvatten, COP och avfrostning lämnas som de är. Planen räknas om direkt.",
+      "fields": {
+        "entry_id": {
+          "name": "Konfigurationspost",
+          "description": "Begränsa återställningen till en konfigurationspost. Lämna tomt för att återställa alla konfigurerade värmepumpar."
+        },
+        "learners": {
+          "name": "Inlärning",
+          "description": "Vad som ska återställas: värmeförlustskalan för huset, förlustförhållandet för nedervåningen, eller båda. Lämna tomt för att återställa båda."
+        }
+      }
+    },
     "diagnose_interval": {
       "name": "Diagnostisera senaste intervallet",
       "description": "Förklara temperaturfelet i det senaste intervallet, insignal för insignal. Optimeringen kör om det intervall som just avslutats genom sin egen termiska modell och byter in en verklig insignal i taget i planens antaganden — uppmätt effekt i stället för beordrad, verklig utomhustemperatur i stället för prognostiserad, verklig sol i stället för antagen — och rapporterar hur mycket av felet varje byte förklarar. Det som inget byte förklarar är modellens eget residualfel, som rapporteras som \"unexplained\". Resultatet publiceras på givaren Prognosträffsäkerhet och returneras som tjänstens svar.",
diff --git a/dev/audit/harnesses/learner_inputs_swap.py b/dev/audit/harnesses/learner_inputs_swap.py
new file mode 100644
index 000000000..00655d1d1
--- /dev/null
+++ b/dev/audit/harnesses/learner_inputs_swap.py
@@ -0,0 +1,89 @@
+#!/usr/bin/env python3
+"""R10-HOTFIX-LEARNER-INPUTS: the heat-loss learners' inputs, through the production coordinator.
+
+(1) What decides the heat-loss basis: ``heat_loss_basis`` over a config with no
+power entity, a meter, and an estimate. (2) A zone-sensor move through
+``_async_load_thermal_learning``: a store the coordinator wrote with
+indoor=``sensor.t6``, lower=``sensor.floor_old`` and the owner's learned
+scale 1.2356 / ratio 1.943 (400 samples each), reloaded under each arm, plus
+both ends of the input range (zero evidence; both learners on the 3.0 clamp).
+UA is ``(upper + lower * ratio) * scale`` on the stock two-zone house
+(``tests/profiles.house``), kW/K.
+
+    python3 -I dev/audit/harnesses/learner_inputs_swap.py [TREE]
+
+TREE defaults to this checkout; pass a ``git archive`` export of another
+commit (custom_components and tests) to measure it.
+"""
+import asyncio
+import os
+import sys
+
+T = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.abspath(
+    os.path.join(os.path.dirname(__file__), "..", "..", ".."))
+sys.path[:0] = [f"{T}/tests/hastub", f"{T}/custom_components", f"{T}/tests"]
+from harness import FakeEntry, FakeHass  # noqa: E402
+from profiles import house  # noqa: E402
+from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Coord  # noqa: E402
+from heatpump_optimizer.thermal_model import heat_loss_basis  # noqa: E402
+
+
+class Store:
+    def __init__(self):
+        self.saved = None
+
+    async def async_save(self, data):
+        self.saved = data
+
+    async def async_load(self):
+        return self.saved
+
+    async def async_wait_for_read(self):
+        return None
+
+
+BASE = dict(house(two_zone=True, dhw=False), indoor_temp_entity="sensor.t6",
+            lower_floor_temp_entity="sensor.floor_old")
+MOVE = dict(BASE, indoor_temp_entity="sensor.bthome", lower_floor_temp_entity="sensor.t6")
+
+
+def coord(cfg, store):
+    c = Coord(FakeHass({}), FakeEntry(data=cfg))
+    c._thermal_learning_store = store
+    return c
+
+
+def learned(scale=1.2356, ratio=1.943, n=400):
+    c = coord(BASE, Store())
+    c._apply_house_heat_loss_scale(scale)
+    c._apply_lower_floor_loss_ratio(ratio)
+    c._house_heat_loss_samples, c._lower_floor_loss_samples = n, n
+    asyncio.run(c._async_save_thermal_learning())
+    return c._thermal_learning_store
+
+
+def reload(cfg, **kw):
+    c = coord(cfg, learned(**kw))
+    asyncio.run(c._async_load_thermal_learning())
+    p = c._thermal_params
+    ua = (p.upper_floor_heat_loss + p.lower_floor_heat_loss * c._lower_floor_loss_ratio) * c._house_heat_loss_scale
+    return (round(c._house_heat_loss_scale, 4), round(c._lower_floor_loss_ratio, 4),
+            c._house_heat_loss_samples, c._lower_floor_loss_samples, round(ua, 4))
+
+
+if __name__ == "__main__":
+    for name, cfg in (
+        ("no power entity (null)", {}),
+        ("power = a revenue meter", {"heat_pump_power_entity": "sensor.shelly_em_power"}),
+        ("power = the pump's own estimate", {"heat_pump_power_entity": "sensor.pump_estimated_power"}),
+    ):
+        print(f"basis  {name:<38} {heat_loss_basis(cfg)}")
+    for name, cfg, kw in (
+        ("unchanged sensors", BASE, {}),
+        ("move: indoor=bthome, lower=t6", MOVE, {}),
+        ("lower only: lower=t6", dict(BASE, lower_floor_temp_entity="sensor.t6"), {}),
+        ("null: outdoor + comfort_weight edit", dict(BASE, outdoor_temp_entity="sensor.out2", comfort_weight=3.0), {}),
+        ("zero evidence (1.0, 1.0, n=0), move", MOVE, {"scale": 1.0, "ratio": 1.0, "n": 0}),
+        ("on the clamp (3.0, 3.0, n=400), move", MOVE, {"scale": 3.0, "ratio": 3.0}),
+    ):
+        print(f"swap   {name:<38} (scale, ratio, n_scale, n_ratio, UA kW/K) = {reload(cfg, **kw)}")
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index 730fc10a6..b6df29eea 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -2,9 +2,9 @@
  {
   "id": "C1",
   "source": "README.md:Entities",
-  "claim": "All 81 entities are created on every install",
+  "claim": "All 82 entities are created on every install",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=81 measured=81",
+  "result": "documented=82 measured=82",
   "verdict": "true",
   "truth": ""
  },
@@ -29,18 +29,18 @@
  {
   "id": "C4",
   "source": "README.md:### Buttons",
-  "claim": "Buttons (5 total)",
+  "claim": "Buttons (6 total)",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=5 measured=5",
+  "result": "documented=6 measured=6",
   "verdict": "true",
   "truth": ""
  },
  {
   "id": "C5",
   "source": "docs/architecture.md:mermaid",
-  "claim": "81 entities / 62 sensors / 6 binary sensors / 5 buttons / 6 switches / 1 climate / 1 datetime",
+  "claim": "82 entities / 62 sensors / 6 binary sensors / 6 buttons / 6 switches / 1 climate / 1 datetime",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=(81, 62, 6, 5, 6, 1, 1) measured=(81, 62, 6, 5, 6, 1, 1)",
+  "result": "documented=(82, 62, 6, 6, 6, 1, 1) measured=(82, 62, 6, 6, 6, 1, 1)",
   "verdict": "true",
   "truth": ""
  },
@@ -112,7 +112,7 @@
   "source": "README.md:### Buttons",
   "claim": "the button table names exactly the buttons the platform constructs",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=['Learning Finalize Debug Collection', 'Learning Reset Comfort Weight', 'Learning Run System Identification', 'Optimize Now', 'Prediction Accuracy Diagnose Last Interval'] measured=['Learning Finalize Debug Collection', 'Learning Reset Comfort Weight', 'Learning Run System Identification', 'Optimize Now', 'Prediction Accuracy Diagnose Last Interval']",
+  "result": "documented=['Learning Finalize Debug Collection', 'Learning Reset Comfort Weight', 'Learning Reset Heat Loss', 'Learning Run System Identification', 'Optimize Now', 'Prediction Accuracy Diagnose Last Interval'] measured=['Learning Finalize Debug Collection', 'Learning Reset Comfort Weight', 'Learning Reset Heat Loss', 'Learning Run System Identification', 'Optimize Now', 'Prediction Accuracy Diagnose Last Interval']",
   "verdict": "true",
   "truth": ""
  },
@@ -128,18 +128,18 @@
  {
   "id": "C15",
   "source": "README.md:## Services",
-  "claim": "13 services are registered under the heatpump_optimizer domain",
+  "claim": "14 services are registered under the heatpump_optimizer domain",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=13 measured=13",
+  "result": "documented=14 measured=14",
   "verdict": "true",
   "truth": ""
  },
  {
   "id": "C16",
   "source": "docs/configuration.md:## Services",
-  "claim": "13 services are registered",
+  "claim": "14 services are registered",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=13 measured=13",
+  "result": "documented=14 measured=14",
   "verdict": "true",
   "truth": ""
  },
@@ -148,7 +148,7 @@
   "source": "README.md:## Services",
   "claim": "the Services table names exactly services.yaml's keys",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=['apply_manual_plan', 'apply_schedule', 'apply_topology', 'assign_entity', 'clear_manual_plan', 'debug_collect', 'diagnose_interval', 'restore_learned_snapshot', 'run_optimization', 'set_away', 'set_mode', 'set_thermal_parameters', 'simulate_plan'] measured=['apply_manual_plan', 'apply_schedule', 'apply_topology', 'assign_entity', 'clear_manual_plan', 'debug_collect', 'diagnose_interval', 'restore_learned_snapshot', 'run_optimization', 'set_away', 'set_mode', 'set_thermal_parameters', 'simulate_plan']",
+  "result": "documented=['apply_manual_plan', 'apply_schedule', 'apply_topology', 'assign_entity', 'clear_manual_plan', 'debug_collect', 'diagnose_interval', 'reset_heat_loss_learners', 'restore_learned_snapshot', 'run_optimization', 'set_away', 'set_mode', 'set_thermal_parameters', 'simulate_plan'] measured=['apply_manual_plan', 'apply_schedule', 'apply_topology', 'assign_entity', 'clear_manual_plan', 'debug_collect', 'diagnose_interval', 'reset_heat_loss_learners', 'restore_learned_snapshot', 'run_optimization', 'set_away', 'set_mode', 'set_thermal_parameters', 'simulate_plan']",
   "verdict": "true",
   "truth": ""
  },
@@ -173,9 +173,9 @@
  {
   "id": "C20",
   "source": "docs/configuration.md",
-  "claim": "eight services accept an optional entry_id",
+  "claim": "nine services accept an optional entry_id",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=8 measured=8",
+  "result": "documented=9 measured=9",
   "verdict": "true",
   "truth": ""
  },
@@ -193,7 +193,7 @@
   "source": "services.yaml",
   "claim": "every services.yaml `example` payload passes its own service schema",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "services with examples=8, failures=[]",
+  "result": "services with examples=9, failures=[]",
   "verdict": "true",
   "truth": ""
  },
@@ -202,7 +202,7 @@
   "source": "README.md:## Services",
   "claim": "the Returns column is each service's registered SupportsResponse (\u2014 = none, Always = ONLY, Optional = OPTIONAL)",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented={'run_optimization': '\u2014', 'set_away': '\u2014', 'set_mode': '\u2014', 'set_thermal_parameters': '\u2014', 'simulate_plan': 'Always', 'apply_schedule': 'Optional', 'apply_manual_plan': 'Optional', 'clear_manual_plan': 'Optional', 'restore_learned_snapshot': 'Optional', 'diagnose_interval': 'Optional', 'debug_collect': 'Optional', 'assign_entity': 'Optional', 'apply_topology': 'Optional'}, registered={'run_optimization': 'none', 'set_mode': 'none', 'set_away': 'none', 'set_thermal_parameters': 'none', 'simulate_plan': 'only', 'apply_schedule': 'optional', 'assign_entity': 'optional', 'apply_topology': 'optional', 'apply_manual_plan': 'optional', 'clear_manual_plan': 'optional', 'restore_learned_snapshot': 'optional', 'diagnose_interval': 'optional', 'debug_collect': 'optional'}, mismatches=[]",
+  "result": "documented={'run_optimization': '\u2014', 'set_away': '\u2014', 'set_mode': '\u2014', 'set_thermal_parameters': '\u2014', 'simulate_plan': 'Always', 'apply_schedule': 'Optional', 'apply_manual_plan': 'Optional', 'clear_manual_plan': 'Optional', 'restore_learned_snapshot': 'Optional', 'reset_heat_loss_learners': 'Optional', 'diagnose_interval': 'Optional', 'debug_collect': 'Optional', 'assign_entity': 'Optional', 'apply_topology': 'Optional'}, registered={'run_optimization': 'none', 'set_mode': 'none', 'set_away': 'none', 'set_thermal_parameters': 'none', 'simulate_plan': 'only', 'apply_schedule': 'optional', 'assign_entity': 'optional', 'apply_topology': 'optional', 'apply_manual_plan': 'optional', 'clear_manual_plan': 'optional', 'restore_learned_snapshot': 'optional', 'reset_heat_loss_learners': 'optional', 'diagnose_interval': 'optional', 'debug_collect': 'optional'}, mismatches=[]",
   "verdict": "true",
   "truth": ""
  },
@@ -326,18 +326,18 @@
  {
   "id": "C37",
   "source": "docs/architecture.md:module map",
-  "claim": "__init__.py -- the 13 services",
+  "claim": "__init__.py -- the 14 services",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=13 measured=13",
+  "result": "documented=14 measured=14",
   "verdict": "true",
   "truth": ""
  },
  {
   "id": "C38",
   "source": "docs/architecture.md:module map",
-  "claim": "services.yaml -- The 13 service definitions",
+  "claim": "services.yaml -- The 14 service definitions",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=13 measured=13",
+  "result": "documented=14 measured=14",
   "verdict": "true",
   "truth": ""
  },
@@ -1030,7 +1030,7 @@
   "source": "README.md",
   "claim": "the Swedish translation actually differs from the English entity names",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "0 of 81 entity names identical in sv and en",
+  "result": "0 of 82 entity names identical in sv and en",
   "verdict": "true",
   "truth": ""
  },
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index 3c3796370..1e353093f 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -4,11 +4,11 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 
 | id | source | claim | check | result | verdict | if false, the truth |
 |---|---|---|---|---|---|---|
-| C1 | `README.md:Entities` | All 81 entities are created on every install | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=81 measured=81 | **true** |  |
+| C1 | `README.md:Entities` | All 82 entities are created on every install | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=82 measured=82 | **true** |  |
 | C2 | `README.md:### Sensors` | Sensors (62 total) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=62 measured=62 | **true** |  |
 | C3 | `README.md:### Binary Sensors` | Binary Sensors (6 total) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=6 measured=6 | **true** |  |
-| C4 | `README.md:### Buttons` | Buttons (5 total) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=5 measured=5 | **true** |  |
-| C5 | `docs/architecture.md:mermaid` | 81 entities / 62 sensors / 6 binary sensors / 5 buttons / 6 switches / 1 climate / 1 datetime | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=(81, 62, 6, 5, 6, 1, 1) measured=(81, 62, 6, 5, 6, 1, 1) | **true** |  |
+| C4 | `README.md:### Buttons` | Buttons (6 total) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=6 measured=6 | **true** |  |
+| C5 | `docs/architecture.md:mermaid` | 82 entities / 62 sensors / 6 binary sensors / 6 buttons / 6 switches / 1 climate / 1 datetime | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=(82, 62, 6, 6, 6, 1, 1) measured=(82, 62, 6, 6, 6, 1, 1) | **true** |  |
 | C6 | `README.md:Entities` | Twenty entities are disabled by default, and these are they (#1335) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Buffer Tank Temperature (Model)', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Contract Comparison', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Temperature', 'ECL110 Displace', 'ECL110 Effective Displace', 'Floor Heating Return Temperature', 'Lower Floor Temperature', 'Measured Power', 'Slab Temperature (Estimated)', 'Solar Surplus Forecast', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood Cheaper Than Heat Pump', 'Wood-Burn Night Advisor'] measured=['Buffer Tank Temperature (Model)', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Contract Comparison', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Temperature', 'ECL110 Displace', 'ECL110 Effective Displace', 'Floor Heating Return Temperature', 'Lower Floor Temperature', 'Measured Power', 'Slab Temperature (Estimated)', 'Solar Surplus Forecast', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood Cheaper Than Heat Pump', 'Wood-Burn Night Advisor'] | **true** |  |
 | C7 | `README.md:Entities` | exactly twenty entities are disabled by default (#1335) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=20 measured=20 | **true** |  |
 | C8 | `README.md:### Sensors` | the sensor table names exactly the sensors the platform constructs | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Buffer Tank Temperature (Model)', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Baseline', 'Cost Contract Comparison', 'Cost Electricity Price (now)', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'Cost Predicted', 'DHW Cost (lifetime)', 'DHW Energy (lifetime)', 'DHW Heating Cost (next 24 h)', 'DHW Heating Schedule', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Setpoint Advisor', 'DHW Temperature', 'ECL110 Displace', 'ECL110 Effective Displace', 'Floor Heating Return Temperature', 'Heat Pump Action', 'Indoor Temperature (Optimizer)', 'Indoor Temperature (Predicted)', 'Last Optimization', 'Learning Comfort Weight', 'Learning Estimated COP', 'Learning Model Status', 'Learning Observed COP', 'Lifetime Space Heating Cost', 'Lifetime Space Heating Energy', 'Lifetime Total Energy', 'Lifetime Total Heating Cost', 'Lower Floor Temperature', 'Measured Power', 'Model Restart Advisor', 'Next Optimization', 'Optimal Setpoint', 'Optimization Mode', 'Optimization Schedule', 'Optimization Schedule Steps', 'Optimization Status', 'Outdoor Temperature (Optimizer)', 'Plan DHW Heating (next 24 h)', 'Plan Monthly Savings', 'Plan Narrative', 'Plan Optimization Score', 'Plan Predicted Savings', 'Plan Savings Percentage', 'Plan Space Heating (next 24 h)', 'Prediction Accuracy', 'Predictive Optimization Insight', 'Recommended Power', 'Sensor-Gap Advisor', 'Slab Temperature (Estimated)', 'Solar Heat Gain', 'Solar Irradiance', 'Solar Surplus Forecast', 'Thermal Battery Charge', 'Thermal Battery Energy', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood-Burn Night Advisor'] measured=['Buffer Tank Temperature (Model)', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Baseline', 'Cost Contract Comparison', 'Cost Electricity Price (now)', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'Cost Predicted', 'DHW Cost (lifetime)', 'DHW Energy (lifetime)', 'DHW Heating Cost (next 24 h)', 'DHW Heating Schedule', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Setpoint Advisor', 'DHW Temperature', 'ECL110 Displace', 'ECL110 Effective Displace', 'Floor Heating Return Temperature', 'Heat Pump Action', 'Indoor Temperature (Optimizer)', 'Indoor Temperature (Predicted)', 'Last Optimization', 'Learning Comfort Weight', 'Learning Estimated COP', 'Learning Model Status', 'Learning Observed COP', 'Lifetime Space Heating Cost', 'Lifetime Space Heating Energy', 'Lifetime Total Energy', 'Lifetime Total Heating Cost', 'Lower Floor Temperature', 'Measured Power', 'Model Restart Advisor', 'Next Optimization', 'Optimal Setpoint', 'Optimization Mode', 'Optimization Schedule', 'Optimization Schedule Steps', 'Optimization Status', 'Outdoor Temperature (Optimizer)', 'Plan DHW Heating (next 24 h)', 'Plan Monthly Savings', 'Plan Narrative', 'Plan Optimization Score', 'Plan Predicted Savings', 'Plan Savings Percentage', 'Plan Space Heating (next 24 h)', 'Prediction Accuracy', 'Predictive Optimization Insight', 'Recommended Power', 'Sensor-Gap Advisor', 'Slab Temperature (Estimated)', 'Solar Heat Gain', 'Solar Irradiance', 'Solar Surplus Forecast', 'Thermal Battery Charge', 'Thermal Battery Energy', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood-Burn Night Advisor'] | **true** |  |
@@ -16,17 +16,17 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C10 | `README.md:### Sensors` | every row whose Notes begin `Diagnostic` is EntityCategory.DIAGNOSTIC, and no other row is | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | mismatches=[] | **true** |  |
 | C11 | `README.md:### Sensors` | every row whose Notes say `disabled by default` has entity_registry_enabled_default False, and no other row does | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | mismatches=[] | **true** |  |
 | C12 | `README.md:### Binary Sensors` | the binary-sensor table names exactly the binary sensors the platform constructs | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Away Mode', 'External Heat Source', 'Input Problem', 'Mold Floor Breach', 'Open Window Detected', 'Wood Cheaper Than Heat Pump'] measured=['Away Mode', 'External Heat Source', 'Input Problem', 'Mold Floor Breach', 'Open Window Detected', 'Wood Cheaper Than Heat Pump'] | **true** |  |
-| C13 | `README.md:### Buttons` | the button table names exactly the buttons the platform constructs | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Learning Finalize Debug Collection', 'Learning Reset Comfort Weight', 'Learning Run System Identification', 'Optimize Now', 'Prediction Accuracy Diagnose Last Interval'] measured=['Learning Finalize Debug Collection', 'Learning Reset Comfort Weight', 'Learning Run System Identification', 'Optimize Now', 'Prediction Accuracy Diagnose Last Interval'] | **true** |  |
+| C13 | `README.md:### Buttons` | the button table names exactly the buttons the platform constructs | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Learning Finalize Debug Collection', 'Learning Reset Comfort Weight', 'Learning Reset Heat Loss', 'Learning Run System Identification', 'Optimize Now', 'Prediction Accuracy Diagnose Last Interval'] measured=['Learning Finalize Debug Collection', 'Learning Reset Comfort Weight', 'Learning Reset Heat Loss', 'Learning Run System Identification', 'Optimize Now', 'Prediction Accuracy Diagnose Last Interval'] | **true** |  |
 | C14 | `README.md:Switches` | Optimizer Active, Away, Block DHW, Block Space Heating, DHW Boost and Boost Space Heating are the switches | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Away', 'Block DHW', 'Block Space Heating', 'Boost Space Heating', 'DHW Boost', 'Optimizer Active'] measured=['Away', 'Block DHW', 'Block Space Heating', 'Boost Space Heating', 'DHW Boost', 'Optimizer Active'] | **true** |  |
-| C15 | `README.md:## Services` | 13 services are registered under the heatpump_optimizer domain | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=13 measured=13 | **true** |  |
-| C16 | `docs/configuration.md:## Services` | 13 services are registered | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=13 measured=13 | **true** |  |
-| C17 | `README.md:## Services` | the Services table names exactly services.yaml's keys | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['apply_manual_plan', 'apply_schedule', 'apply_topology', 'assign_entity', 'clear_manual_plan', 'debug_collect', 'diagnose_interval', 'restore_learned_snapshot', 'run_optimization', 'set_away', 'set_mode', 'set_thermal_parameters', 'simulate_plan'] measured=['apply_manual_plan', 'apply_schedule', 'apply_topology', 'assign_entity', 'clear_manual_plan', 'debug_collect', 'diagnose_interval', 'restore_learned_snapshot', 'run_optimization', 'set_away', 'set_mode', 'set_thermal_parameters', 'simulate_plan'] | **true** |  |
+| C15 | `README.md:## Services` | 14 services are registered under the heatpump_optimizer domain | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=14 measured=14 | **true** |  |
+| C16 | `docs/configuration.md:## Services` | 14 services are registered | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=14 measured=14 | **true** |  |
+| C17 | `README.md:## Services` | the Services table names exactly services.yaml's keys | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['apply_manual_plan', 'apply_schedule', 'apply_topology', 'assign_entity', 'clear_manual_plan', 'debug_collect', 'diagnose_interval', 'reset_heat_loss_learners', 'restore_learned_snapshot', 'run_optimization', 'set_away', 'set_mode', 'set_thermal_parameters', 'simulate_plan'] measured=['apply_manual_plan', 'apply_schedule', 'apply_topology', 'assign_entity', 'clear_manual_plan', 'debug_collect', 'diagnose_interval', 'reset_heat_loss_learners', 'restore_learned_snapshot', 'run_optimization', 'set_away', 'set_mode', 'set_thermal_parameters', 'simulate_plan'] | **true** |  |
 | C18 | `README.md + docs/configuration.md` | set_thermal_parameters takes 31 fields | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=31 measured=31 | **true** |  |
 | C19 | `docs/configuration.md` | simulate_plan takes 19 optional fields | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=19 measured=19 | **true** |  |
-| C20 | `docs/configuration.md` | eight services accept an optional entry_id | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=8 measured=8 | **true** |  |
+| C20 | `docs/configuration.md` | nine services accept an optional entry_id | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=9 measured=9 | **true** |  |
 | C21 | `services.yaml` | services.yaml documents exactly the fields each voluptuous schema accepts | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | symmetric differences={}, catalogue gap=[] | **true** |  |
-| C22 | `services.yaml` | every services.yaml `example` payload passes its own service schema | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | services with examples=8, failures=[] | **true** |  |
-| C23 | `README.md:## Services` | the Returns column is each service's registered SupportsResponse (— = none, Always = ONLY, Optional = OPTIONAL) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented={'run_optimization': '—', 'set_away': '—', 'set_mode': '—', 'set_thermal_parameters': '—', 'simulate_plan': 'Always', 'apply_schedule': 'Optional', 'apply_manual_plan': 'Optional', 'clear_manual_plan': 'Optional', 'restore_learned_snapshot': 'Optional', 'diagnose_interval': 'Optional', 'debug_collect': 'Optional', 'assign_entity': 'Optional', 'apply_topology': 'Optional'}, registered={'run_optimization': 'none', 'set_mode': 'none', 'set_away': 'none', 'set_thermal_parameters': 'none', 'simulate_plan': 'only', 'apply_schedule': 'optional', 'assign_entity': 'optional', 'apply_topology': 'optional', 'apply_manual_plan': 'optional', 'clear_manual_plan': 'optional', 'restore_learned_snapshot': 'optional', 'diagnose_interval': 'optional', 'debug_collect': 'optional'}, mismatches=[] | **true** |  |
+| C22 | `services.yaml` | every services.yaml `example` payload passes its own service schema | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | services with examples=9, failures=[] | **true** |  |
+| C23 | `README.md:## Services` | the Returns column is each service's registered SupportsResponse (— = none, Always = ONLY, Optional = OPTIONAL) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented={'run_optimization': '—', 'set_away': '—', 'set_mode': '—', 'set_thermal_parameters': '—', 'simulate_plan': 'Always', 'apply_schedule': 'Optional', 'apply_manual_plan': 'Optional', 'clear_manual_plan': 'Optional', 'restore_learned_snapshot': 'Optional', 'reset_heat_loss_learners': 'Optional', 'diagnose_interval': 'Optional', 'debug_collect': 'Optional', 'assign_entity': 'Optional', 'apply_topology': 'Optional'}, registered={'run_optimization': 'none', 'set_mode': 'none', 'set_away': 'none', 'set_thermal_parameters': 'none', 'simulate_plan': 'only', 'apply_schedule': 'optional', 'assign_entity': 'optional', 'apply_topology': 'optional', 'apply_manual_plan': 'optional', 'clear_manual_plan': 'optional', 'restore_learned_snapshot': 'optional', 'reset_heat_loss_learners': 'optional', 'diagnose_interval': 'optional', 'debug_collect': 'optional'}, mismatches=[] | **true** |  |
 | C24 | `docs/configuration.md` | assign_entity's `key` is one of 21 assignable configuration keys, listed | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['buffer_tank_temp_entity', 'dhw_temp_entity', 'external_heat_entity', 'floor_return_temp_entity', 'heat_pump_defrost_entity', 'heat_pump_energy_entity', 'heat_pump_fault_entity', 'heat_pump_mode_entity', 'heat_pump_online_entity', 'heat_pump_power_entity', 'heat_pump_switch_entity', 'house_power_entity', 'indoor_temp_entity', 'lower_floor_temp_entity', 'mixing_valve_target_entity', 'outdoor_temp_entity', 'pv_production_entity', 'solar_radiation_entity', 'valve_outlet_temp_entity', 'wood_tank_bottom_entity', 'wood_tank_top_entity'] measured=['buffer_tank_temp_entity', 'dhw_temp_entity', 'external_heat_entity', 'floor_return_temp_entity', 'heat_pump_defrost_entity', 'heat_pump_energy_entity', 'heat_pump_fault_entity', 'heat_pump_mode_entity', 'heat_pump_online_entity', 'heat_pump_power_entity', 'heat_pump_switch_entity', 'house_power_entity', 'indoor_temp_entity', 'lower_floor_temp_entity', 'mixing_valve_target_entity', 'outdoor_temp_entity', 'pv_production_entity', 'solar_radiation_entity', 'valve_outlet_temp_entity', 'wood_tank_bottom_entity', 'wood_tank_top_entity'] | **true** |  |
 | C25 | `docs/configuration.md` | the count in that sentence is 21 | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=21 measured=21 | **true** |  |
 | C26 | `README.md` | a menu of 23 pages | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=23 measured=23 | **true** |  |
@@ -40,8 +40,8 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C34 | `docs/architecture.md:The Home Assistant boundary` | the boundary sentence's count of modules importing `homeassistant` at module level | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=28 measured=28 | **true** |  |
 | C35 | `docs/architecture.md:The Home Assistant boundary` | the named modules are the complete set of module-level importers | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | named=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'issues.py', 'legionella.py', 'notifier.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'sensor.py', 'services.py', 'store.py', 'switch.py'], measured=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'issues.py', 'legionella.py', 'notifier.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'sensor.py', 'services.py', 'store.py', 'switch.py'], unnamed=[] | **true** | unnamed module-level importers:  |
 | C36 | `docs/architecture.md:The Home Assistant boundary` | everything outside the named set is free of homeassistant, so each module can be driven with no Home Assistant running | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 0 modules outside the named set import homeassistant at module level | **true** | modules outside the named set import homeassistant at module level and cannot be imported without it:  |
-| C37 | `docs/architecture.md:module map` | __init__.py -- the 13 services | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=13 measured=13 | **true** |  |
-| C38 | `docs/architecture.md:module map` | services.yaml -- The 13 service definitions | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=13 measured=13 | **true** |  |
+| C37 | `docs/architecture.md:module map` | __init__.py -- the 14 services | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=14 measured=14 | **true** |  |
+| C38 | `docs/architecture.md:module map` | services.yaml -- The 14 service definitions | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=14 measured=14 | **true** |  |
 | C39 | `docs/architecture.md:module map` | sensor.py -- 62 sensors | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=62 measured=62 | **true** |  |
 | C40 | `docs/architecture.md:module map` | switch.py -- the comment names every switch the platform constructs | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Away', 'Block DHW', 'Block Space Heating', 'Boost Space Heating', 'DHW Boost', 'Optimizer Active'], the platform constructs ['Away', 'Block DHW', 'Block Space Heating', 'Boost Space Heating', 'DHW Boost', 'Optimizer Active'] | **true** |  |
 | C41 | `docs/architecture.md:module map` | binary_sensor.py -- the comment names every binary sensor the platform constructs | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Away Mode', 'External Heat Source', 'Input Problem', 'Mold Floor Breach', 'Open Window Detected', 'Wood Cheaper Than Heat Pump'], the platform constructs ['Away Mode', 'External Heat Source', 'Input Problem', 'Mold Floor Breach', 'Open Window Detected', 'Wood Cheaper Than Heat Pump'] | **true** |  |
@@ -118,7 +118,7 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C112 | `strings.json + translations/*.json` | every translation file carries exactly the keys strings.json declares | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | languages=['en', 'sv'], missing={'en': 0, 'sv': 0}, extra={'en': 0, 'sv': 0} | **true** |  |
 | C113 | `README.md` | entity names are translated into English and Swedish | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['en', 'sv'] measured=['en', 'sv'] | **true** |  |
 | C114 | `README.md` | every entity's display name comes from the translation files | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | untranslated=[] | **true** |  |
-| C115 | `README.md` | the Swedish translation actually differs from the English entity names | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 0 of 81 entity names identical in sv and en | **true** |  |
+| C115 | `README.md` | the Swedish translation actually differs from the English entity names | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 0 of 82 entity names identical in sv and en | **true** |  |
 | C116 | `README.md` | the integration domain is heatpump_optimizer | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='heatpump_optimizer' measured='heatpump_optimizer' | **true** |  |
 | C117 | `manifest.json` | config_flow is declared | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=True measured=True | **true** |  |
 | C118 | `README.md` | the documentation url in the manifest points at the project | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='https://github.com/tvofi/heatpump_optimizer' measured='https://github.com/tvofi/heatpump_optimizer' | **true** |  |
diff --git a/dev/audit/rounds/round4/D6/claims.py b/dev/audit/rounds/round4/D6/claims.py
index eaf7e8d55..7626132ba 100644
--- a/dev/audit/rounds/round4/D6/claims.py
+++ b/dev/audit/rounds/round4/D6/claims.py
@@ -515,6 +515,7 @@ SCHEMAS = {
     "clear_manual_plan": svc.SERVICE_SCHEMA_CLEAR_MANUAL_PLAN,
     "restore_learned_snapshot": svc.SERVICE_SCHEMA_RESTORE_SNAPSHOT,
     "diagnose_interval": svc.SERVICE_SCHEMA_DIAGNOSE_INTERVAL,
+    "reset_heat_loss_learners": svc.SERVICE_SCHEMA_RESET_HEAT_LOSS,
     "debug_collect": svc.SERVICE_SCHEMA_DEBUG_COLLECT,
 }
 # The label is the sentence's own number, as C26's is: a label frozen at
diff --git a/dev/programme/delivery/3022.md b/dev/programme/delivery/3022.md
new file mode 100644
index 000000000..406ce8006
--- /dev/null
+++ b/dev/programme/delivery/3022.md
@@ -0,0 +1 @@
+- [#3022](https://github.com/tvofi/heatpump_optimizer/pull/3022) — **open**, HOTFIX R10-HOTFIX-LEARNER-INPUTS: a sensor swap voids the heat-loss learners, and a reset action (R10-HOTFIX-LEARNER-INPUTS)
diff --git a/docs/architecture.md b/docs/architecture.md
index 6471baa4d..ac2500895 100644
--- a/docs/architecture.md
+++ b/docs/architecture.md
@@ -28,7 +28,7 @@ flowchart TB
         states["Entity states<br/>temperatures, power, tank probes,<br/>presence, humidity"]
 
         subgraph glue["Integration glue — imports homeassistant"]
-            entities["Entity layer<br/>81 entities<br/>62 sensors, 6 binary sensors,<br/>5 buttons, 6 switches,<br/>1 climate, 1 datetime"]
+            entities["Entity layer<br/>82 entities<br/>62 sensors, 6 binary sensors,<br/>6 buttons, 6 switches,<br/>1 climate, 1 datetime"]
             ui["config_flow · services · frontend<br/>repairs · diagnostics · notifier"]
             reader["inputs.py — InputReader<br/>freshness and unit guards"]
             coord["coordinator.py<br/>HeatPumpOptimizerCoordinator<br/>the orchestration seam"]
@@ -105,7 +105,7 @@ Read the diagram as four regions.
 
 ```text
 custom_components/heatpump_optimizer/
-├── __init__.py           # Setup and unload, the 13 services, entry migrations
+├── __init__.py           # Setup and unload, the 14 services, entry migrations
 ├── const.py              # Every config key, default and tuning constant
 ├── entry_config.py       # The entry's configuration, parsed once: one default
 │                         #   and one coercion per key
@@ -229,7 +229,7 @@ custom_components/heatpump_optimizer/
 │                         #   Boost Space Heating, DHW Boost, Optimizer Active
 ├── datetime.py           # The away-override return instant, as one datetime entity
 ├── frontend.py           # Serves and registers the Lovelace card
-├── services.py           # The domain's 13 services: schemas, handlers and registration
+├── services.py           # The domain's 14 services: schemas, handlers and registration
 ├── debugger.py           # A week of cycle rows for one entry, kept across a
 │                         #   reload and carried by Download diagnostics
 ├── replay_doc.py         # The replay document's allowlist and sanitiser, one
@@ -240,7 +240,7 @@ custom_components/heatpump_optimizer/
 ├── www/                  # The dashboard card, one self-contained file
 ├── brand/                # Icon and logo
 ├── icon.png              # Integration icon
-├── services.yaml         # The 13 service definitions
+├── services.yaml         # The 14 service definitions
 ├── strings.json          # UI strings
 ├── translations/
 │   ├── en.json           # English
diff --git a/docs/configuration.md b/docs/configuration.md
index bba7b039c..8fd441ab2 100644
--- a/docs/configuration.md
+++ b/docs/configuration.md
@@ -232,7 +232,7 @@ single field takes the same grammar, including day selectors such as
 | Rain sensitivity | 1.15 | 1.0–1.5, 0.01 steps | Loss multiplier while it is raining. 1.0 means rain makes no difference. |
 
 Saving this page moves to the read-only review screen — confirming there is
-what creates the entry. All 81 entities appear at once and the first plan is
+what creates the entry. All 82 entities appear at once and the first plan is
 solved within one optimization interval.
 
 ---
@@ -946,13 +946,13 @@ feeding the buffer tank — its heat is folded in rather than stored separately.
 
 ## Services
 
-13 services are registered under the `heatpump_optimizer` domain. The eight
+14 services are registered under the `heatpump_optimizer` domain. The nine
 that act on a specific config entry also accept an optional `entry_id`; omitting
 it applies the call to every loaded entry, which is what a single-heat-pump
-install wants. Of those eight, `assign_entity`, `apply_topology`,
+install wants. Of those nine, `assign_entity`, `apply_topology`,
 `apply_schedule` and `debug_collect` write configuration back into the entry —
 `debug_collect`'s start turns the collection option on, which reloads the
-entry — and the other four act on the running coordinator. `run_optimization`,
+entry — and the other five act on the running coordinator. `run_optimization`,
 `set_away`, `set_mode`, `set_thermal_parameters` and `simulate_plan` always act
 on every loaded entry.
 
@@ -974,6 +974,7 @@ or is not loaded — fails with a validation error rather than doing nothing.
 | `apply_manual_plan` | `space_slots`, `dhw_slots`, `expires_at`, `entry_id` | optional |
 | `clear_manual_plan` | `entry_id` | optional |
 | `restore_learned_snapshot` | `entry_id` | optional |
+| `reset_heat_loss_learners` | `learners`, `entry_id` | optional |
 | `diagnose_interval` | `entry_id` | optional |
 | `debug_collect` | `action` (required), `entry_id` | optional |
 
@@ -1089,6 +1090,15 @@ weekly snapshot — the manual counterpart of the drift watchdog. When no
 snapshot qualifies (healthy inputs and in-band accuracy at capture time are
 required) the call fails with an error instead of answering with an empty
 restore.
+**`reset_heat_loss_learners`** returns the learned house heat loss scale and the
+learned lower floor loss ratio to 1.0, so the plan uses the heat loss values in
+the settings as they stand, and the learners start collecting evidence again
+from there; the plan is recalculated straight away. `learners` names which:
+`house_heat_loss_scale`, `lower_floor_loss_ratio`, or both when left empty. The
+comfort weight and the hot-water, COP and defrost learners are left alone. The
+**Learning Reset Heat Loss** button resets both. Changing the indoor or the
+lower-floor temperature sensor resets the learner fitted on it the same way,
+because evidence fitted against one sensor says nothing about another.
 **`diagnose_interval`** attributes the last interval's temperature error
 input by input and publishes the result on the Prediction Accuracy sensor.
 **`debug_collect`** takes `action`: `start`, `stop` or `status`. Collect a week of debug data is the learning page's option that turns the collection on. `start` turns
diff --git a/tests/closures.json b/tests/closures.json
index 6f93af714..b08e69482 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3870,6 +3870,7 @@
    "dev/audit/harnesses/hpo_ci_container_setup.sh",
    "dev/audit/harnesses/j5_gil.py",
    "dev/audit/harnesses/k1725_blas_kernel_gap.py",
+   "dev/audit/harnesses/learner_inputs_swap.py",
    "dev/audit/harnesses/merge_subject_guard_block.mjs",
    "dev/audit/harnesses/pulse_replay.py",
    "dev/audit/harnesses/r10_2205_replay_cost_arms.py",
diff --git a/tests/entities.py b/tests/entities.py
index d70832183..c0bcaec43 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -7267,7 +7267,7 @@ R.section("Buttons")
 
 buttons = collect(button)
 btn_by_name = {display_name("button", b): b for b in buttons}
-R.check("five buttons are added", len(buttons) == 5, str(len(buttons)))
+R.check("six buttons are added", len(buttons) == 6, str(len(buttons)))
 for name in (
     "Optimize Now",
     "Learning Run System Identification",
@@ -7309,6 +7309,17 @@ R.check(
     "weight unpublished until the next cycle",
 )
 
+heat_loss_reset = button.ResetHeatLossButton(coord, ENTRY)
+heat_loss_reset.hass = EagerHass()
+coord.refreshes.clear()
+coord.on_refresh = lambda: "reset_heat_loss" in coord.pressed
+asyncio.run(heat_loss_reset.async_press())
+R.check(
+    "the heat-loss reset button reaches the coordinator, then asks for one refresh",
+    "reset_heat_loss" in coord.pressed and coord.refreshes == [True],
+    f"pressed={coord.pressed} refreshes={coord.refreshes}",
+)
+
 
 # ===========================================================================
 # Options flow
@@ -12884,6 +12895,7 @@ _CLUSTER_PREFIXES: dict[str, dict[str, str]] = {
         "learning_finalize_debug": "Learning ",
         "learning_run_system_identification": "Learning ",
         "learning_reset_comfort_weight": "Learning ",
+        "learning_reset_heat_loss": "Learning ",
     },
     "switch": {"dhw_boost": "DHW "},
 }
@@ -15047,6 +15059,7 @@ _svc_coord.async_clear_manual_plan = _svc_record("clear_manual")
 _svc_coord.async_restore_learned_snapshot = _svc_record("restore", True)
 _svc_coord.async_set_away = _svc_record("set_away")
 _svc_coord.async_diagnose_interval = _svc_record("diagnose", {"residual": None})
+_svc_coord.async_reset_heat_loss_learners = _svc_record("reset_heat_loss")
 
 
 def _svc_call(service, payload=None):
@@ -15399,6 +15412,14 @@ R.check(
     _restored["restored"] == [_svc_entry.entry_id],
 )
 
+_heat_loss_reset = _svc_call(const.SERVICE_RESET_HEAT_LOSS, {"learners": ["lower_floor_loss_ratio"]})
+R.check(
+    "reset_heat_loss_learners reaches the coordinator and reports what it reset",
+    "reset_heat_loss" in _svc_log
+    and _heat_loss_reset == {"reset": [_svc_entry.entry_id], "learners": ["lower_floor_loss_ratio"]},
+    str(_heat_loss_reset),
+)
+
 _diag = _svc_call(const.SERVICE_DIAGNOSE_INTERVAL)
 R.check(
     "diagnose_interval returns the per-entry report",
@@ -15436,6 +15457,7 @@ _svc_covered = {
     const.SERVICE_RESTORE_SNAPSHOT,
     const.SERVICE_DIAGNOSE_INTERVAL,
     const.SERVICE_DEBUG_COLLECT,
+    const.SERVICE_RESET_HEAT_LOSS,
 }
 R.check(
     "every registered service was invoked above",
@@ -40302,6 +40324,9 @@ _R10_LOG_ALLOWED_BY_REASON = {
     "once per event by the function's own state (a refit, an issue raised, a "
     "rollback per alarm, a malformed month closed so it is not retried)": {
         ("coordinator.py", "_reanchor_house_heat_loss_scale"): 2,
+        # One line per learner voided: a sensor swap, voided once because the
+        # save records the new id, or a reset the user asked for.
+        ("coordinator.py", "_void_heat_loss_learners"): 1,
         ("coordinator.py", "_raise_cop_issue"): 1,
         ("coordinator.py", "_async_watch_learning_drift"): 1, ("ledger.py", "roll_receipts"): 1,
     },
diff --git a/tests/features.py b/tests/features.py
index 3e5c55705..77cf581ef 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -8247,6 +8247,7 @@ class _LearnPersist:
     _house_heat_loss_anchor = Coord._house_heat_loss_anchor
     _heat_loss_anchors = Coord._heat_loss_anchors
     _reanchor_house_heat_loss_scale = Coord._reanchor_house_heat_loss_scale
+    _void_heat_loss_learners = Coord._void_heat_loss_learners
     _apply_learner_payloads = Coord._apply_learner_payloads
 
     def __init__(self, store) -> None:
@@ -12931,6 +12932,238 @@ R.check(
 )
 
 
+# --- R10-HOTFIX-LEARNER-INPUTS: a zone-sensor swap and the reset action ------
+#
+# Each heat-loss learner fits its residual on one zone sensor: the scale on
+# the indoor (upper zone) one, the ratio on the lower floor's. Evidence fitted
+# against one sensor says nothing about a sensor in another place, so a
+# changed entity id voids that learner, and the reset button and service void
+# either or both -- one void path, ``_void_heat_loss_learners``. Real
+# coordinators over the stock two-zone house, every expectation a property.
+from homeassistant.config_entries import ConfigEntryState as _li_state  # noqa: E402
+from harness import FakeServiceCall as _li_call  # noqa: E402
+from heatpump_optimizer import services as _li_services  # noqa: E402
+
+R.section("A zone-sensor swap and the reset action void the heat-loss learners")
+
+_LI_CFG = dict(_RA_CFG, indoor_temp_entity="sensor.indoor")
+_LI_LEARNED = (_RA_S, _RA_R, _RA_NS, _RA_NR)
+
+
+def _li_state_of(c):
+    return (c._house_heat_loss_scale, c._lower_floor_loss_ratio,
+            c._house_heat_loss_samples, c._lower_floor_loss_samples)
+
+
+def _li_swap(cfg_now, store=None):
+    store = store or _ra_learned(_LI_CFG)
+    saves = store.saves
+    c = _ra_reload(cfg_now, store)
+    return _li_state_of(c), store.saves - saves, store
+
+
+_li_lower, _li_lower_saves, _ = _li_swap(dict(_LI_CFG, lower_floor_temp_entity="sensor.t6"))
+R.check(
+    "a lower-floor sensor swap voids the ratio and leaves the scale intact",
+    _li_lower == (_RA_S, 1.0, _RA_NS, 0) and _li_lower_saves == 1,
+    f"(scale, ratio, samples) {_li_lower}, {_li_lower_saves} save(s)",
+)
+_li_indoor, _li_indoor_saves, _ = _li_swap(dict(_LI_CFG, indoor_temp_entity="sensor.bthome"))
+R.check(
+    "an indoor sensor swap voids the scale and leaves the ratio intact",
+    _li_indoor == (1.0, _RA_R, 0, _RA_NR) and _li_indoor_saves == 1,
+    f"(scale, ratio, samples) {_li_indoor}, {_li_indoor_saves} save(s)",
+)
+# The owner's move: T6 from indoor to lower floor, a room sensor as indoor.
+_li_both, _, _ = _li_swap(dict(_LI_CFG, indoor_temp_entity="sensor.bthome",
+                               lower_floor_temp_entity="sensor.indoor"))
+R.check(
+    "moving a sensor from indoor to the lower floor voids both learners",
+    _li_both == (1.0, 1.0, 0, 0),
+    f"(scale, ratio, samples) {_li_both}",
+)
+# Null control: an options change touching neither zone sensor.
+_li_null, _li_null_saves, _ = _li_swap(dict(_LI_CFG, outdoor_temp_entity="sensor.other_outdoor",
+                                            comfort_weight=3.0))
+R.check(
+    "an unrelated options change keeps both learners verbatim and writes nothing",
+    _li_null == _LI_LEARNED and _li_null_saves == 0,
+    f"(scale, ratio, samples) {_li_null}, {_li_null_saves} save(s)",
+)
+# A store from before the record proves nothing about which sensor it fitted:
+# the load adopts the ids in force, it does not void.
+_li_old = _ra_learned(_LI_CFG)
+_li_old.saved = {k: v for k, v in _li_old.saved.items() if k != "heat_loss_zone_entities"}
+_li_pre, _li_pre_saves, _ = _li_swap(dict(_LI_CFG, lower_floor_temp_entity="sensor.t6"), _li_old)
+R.check(
+    "a store without recorded zone sensors keeps both learners and adopts the ids",
+    _li_pre == _LI_LEARNED and _li_pre_saves == 1
+    and _li_old.saved.get("heat_loss_zone_entities", {}).get("lower_floor_temp_entity") == "sensor.t6",
+    f"(scale, ratio, samples) {_li_pre}, adopted {_li_old.saved.get('heat_loss_zone_entities')!r}",
+)
+# And a second load over the same sensors keeps what the first one left.
+_li_twice, _li_twice_saves, _ = _li_swap(dict(_LI_CFG, lower_floor_temp_entity="sensor.t6"),
+                                        _ra_reload(dict(_LI_CFG, lower_floor_temp_entity="sensor.t6"),
+                                                   _ra_learned(_LI_CFG))._thermal_learning_store)
+R.check(
+    "a reload over the swapped sensor voids nothing more",
+    _li_twice == (_RA_S, 1.0, _RA_NS, 0) and _li_twice_saves == 0,
+    f"(scale, ratio, samples) {_li_twice}, {_li_twice_saves} save(s)",
+)
+
+# A key the record does not hold voids nothing for that learner, as a store
+# from before the record voids nothing: the docstring's branch, pinned.
+_li_part = _ra_learned(_LI_CFG)
+_li_part.saved = dict(_li_part.saved, heat_loss_zone_entities={"indoor_temp_entity": "sensor.indoor"})
+_li_part_got, _, _ = _li_swap(dict(_LI_CFG, lower_floor_temp_entity="sensor.t6"), _li_part)
+R.check(
+    "a record without the lower-floor key keeps the ratio through a lower-floor swap",
+    _li_part_got == _LI_LEARNED,
+    f"(scale, ratio, samples) {_li_part_got}",
+)
+
+# Fix review round 1 (swap-void-undone): a swap in the same options change as
+# a nameplate edit past the re-anchor gate. The void runs first and the stored
+# total is re-expressed at the voided ratio, so the law cannot write the
+# pre-void ratio back; one load lands where the same two changes in two loads
+# land (the path-independent control).
+_LI_EDIT = dict(upper_floor_heat_loss=_RA_U * 1.5, lower_floor_heat_loss=_RA_L * 1.5)
+
+
+def _li_two_loads(swap, edit):
+    first = _ra_reload(dict(_LI_CFG, **swap), _ra_learned(_LI_CFG))
+    return _li_state_of(_ra_reload(dict(_LI_CFG, **swap, **edit), first._thermal_learning_store))
+
+
+for _li_name, _li_sw in (
+    ("a lower-floor swap", {"lower_floor_temp_entity": "sensor.t6"}),
+    ("both swapped", {"indoor_temp_entity": "sensor.bthome", "lower_floor_temp_entity": "sensor.indoor"}),
+):
+    _li_one, _, _ = _li_swap(dict(_LI_CFG, **_li_sw, **_LI_EDIT))
+    _li_two = _li_two_loads(_li_sw, _LI_EDIT)
+    R.check(
+        f"{_li_name} with a nameplate edit past the gate, in one load, keeps the ratio voided "
+        "and lands where the two changes in two loads land",
+        _li_one[1] == 1.0 and _li_one[3] == 0
+        and all(abs(x - y) < 1e-9 for x, y in zip(_li_one, _li_two)),
+        f"one load {_li_one}, two loads {_li_two}",
+    )
+# The snapshot restore takes the same path: a pre-swap snapshot rolled back
+# onto the swapped, edited configuration keeps the void.
+_li_snap_c = _ra_coord(dict(_LI_CFG, lower_floor_temp_entity="sensor.t6", **_LI_EDIT), _CountingLearnStore())
+_li_snap_c._apply_learner_payloads({"thermal_learning": dict(_ra_learned(_LI_CFG).saved)})
+R.check(
+    "a pre-swap snapshot restored onto a swapped, edited configuration keeps the ratio voided",
+    _li_snap_c._lower_floor_loss_ratio == 1.0 and _li_snap_c._lower_floor_loss_samples == 0,
+    f"(scale, ratio, samples) {_li_state_of(_li_snap_c)}",
+)
+
+
+def _li_others(c):
+    """Every learner's persisted shape but the two heat-loss learners', the zone-total
+    anchor their ratio enters (re-derived on save), and the save stamp."""
+    out = c._learner_snapshot_payloads()
+    out["thermal_learning"] = {k: v for k, v in out["thermal_learning"].items() if k not in (
+        "house_heat_loss_scale", "house_heat_loss_samples", "lower_floor_loss_ratio",
+        "lower_floor_loss_samples", "house_heat_loss_anchor", "updated_at")}
+    return out
+
+
+def _li_reset(learners=None):
+    c = _ra_reload(_LI_CFG, _ra_learned(_LI_CFG))
+    c._apply_cop_scale(1.13)
+    c._comfort_learner.evidence = -1.4
+    before = _li_others(c)
+    _aio.run(c.async_reset_heat_loss_learners(*([learners] if learners else [])))
+    return c, before
+
+
+_li_r, _li_r_before = _li_reset()
+_li_r_after = _ra_reload(_LI_CFG, _li_r._thermal_learning_store)
+R.check(
+    "the reset returns both learners to 1.0 with no samples, and saves it",
+    _li_state_of(_li_r) == _li_state_of(_li_r_after) == (1.0, 1.0, 0, 0)
+    and _li_r._thermal_params.house_heat_loss_scale == 1.0
+    and _li_r._thermal_params.lower_floor_heat_loss_learned == _li_r._thermal_params.lower_floor_heat_loss,
+    f"live {_li_state_of(_li_r)}, reloaded {_li_state_of(_li_r_after)}",
+)
+R.check(
+    "the reset leaves the comfort weight and the DHW, COP and defrost learners as they were",
+    _li_others(_li_r) == _li_r_before and _li_r._cop_scale == 1.13
+    and _li_r._comfort_learner.evidence == -1.4,
+    str(sorted(f"{k}/{f}" for k, v in _li_others(_li_r).items() for f in set(v) | set(_li_r_before[k])
+               if v.get(f) != _li_r_before[k].get(f))),
+)
+_li_one, _ = _li_reset(("lower_floor_loss_ratio",))
+R.check(
+    "resetting the ratio alone leaves the scale and its samples intact",
+    _li_state_of(_li_one) == (_RA_S, 1.0, _RA_NS, 0),
+    f"(scale, ratio, samples) {_li_state_of(_li_one)}",
+)
+_li_one_s, _ = _li_reset(("house_heat_loss_scale",))
+R.check(
+    "resetting the scale alone leaves the ratio and its samples intact",
+    _li_state_of(_li_one_s) == (1.0, _RA_R, 0, _RA_NR),
+    f"(scale, ratio, samples) {_li_state_of(_li_one_s)}",
+)
+
+
+async def _li_service(data, store):
+    """The service over a loaded coordinator, with the refresh it asks for counted."""
+    hass = FakeHass({})
+    entry = _ra_entry(data=_LI_CFG, entry_id="li_service")
+    coord = _ra_coord(_LI_CFG, store)
+    await coord._async_load_thermal_learning()
+    refreshes = []
+
+    async def _refresh(*_a, **_k):
+        refreshes.append(_li_state_of(coord))
+
+    coord.async_request_refresh = _refresh
+    entry.state = _li_state.LOADED
+    entry.runtime_data = coord
+    hass.config_entries.entries.append(entry)
+    answer = await _li_services.handle_reset_heat_loss(
+        hass, _li_call("heatpump_optimizer", "reset_heat_loss_learners",
+                       _li_services.SERVICE_SCHEMA_RESET_HEAT_LOSS(data)))
+    return _li_state_of(coord), refreshes, answer
+
+
+_li_svc_both = _aio.run(_li_service({}, _ra_learned(_LI_CFG)))
+_li_svc_one = _aio.run(_li_service({"learners": ["lower_floor_loss_ratio"]}, _ra_learned(_LI_CFG)))
+R.check(
+    "the service resets both by default, then re-plans on the reset values",
+    _li_svc_both[0] == (1.0, 1.0, 0, 0) and _li_svc_both[1] == [(1.0, 1.0, 0, 0)],
+    f"state {_li_svc_both[0]}, refreshes {_li_svc_both[1]}, answer {_li_svc_both[2]}",
+)
+R.check(
+    "the service's learners field resets one learner alone",
+    _li_svc_one[0] == (_RA_S, 1.0, _RA_NS, 0) and len(_li_svc_one[1]) == 1,
+    f"state {_li_svc_one[0]}, answer {_li_svc_one[2]}",
+)
+try:
+    _li_services.SERVICE_SCHEMA_RESET_HEAT_LOSS({"learners": ["cop_scale"]})
+    _li_refused = False
+except Exception:  # vol.Invalid
+    _li_refused = True
+R.check("the service refuses a learner it does not reset", _li_refused)
+
+# After a reset the next fold starts from the configuration: the reset
+# coordinator and one that never learned take the same interval to the same
+# ratio, one sample each.
+_li_fold = _two_zone_learner(lower_entity="sensor.lower", ratio=2.4)
+_li_fold._lower_floor_loss_samples = 90
+_aio.run(_li_fold.async_reset_heat_loss_learners())
+_li_fresh = _two_zone_learner(lower_entity="sensor.lower")
+_li_fold_got = _drive_lower(_li_fold, observed_lower=19.6)
+_li_fresh_got = _drive_lower(_li_fresh, observed_lower=19.6)
+R.check(
+    "the next fold after a reset starts from the configuration",
+    _li_fold_got == _li_fresh_got and _li_fold_got[1] == 1 and _li_fold_got[0] != 1.0,
+    f"reset {_li_fold_got} vs never learned {_li_fresh_got}",
+)
+
+
 R.section("Runtime parameter updates")
 
 import asyncio
@@ -25435,6 +25668,7 @@ _HPO_MOVED = (
     "handle_clear_manual_plan",
     "handle_restore_snapshot",
     "handle_diagnose_interval",
+    "handle_reset_heat_loss",
     "_manual_targets",
     "_loaded_entries",
     "_loaded_coordinators",
@@ -25505,6 +25739,7 @@ _HPO_SERVICE_MAP = {
     "restore_learned_snapshot": "handle_restore_snapshot",
     "diagnose_interval": "handle_diagnose_interval",
     "debug_collect": "handle_debug_collect",
+    "reset_heat_loss_learners": "handle_reset_heat_loss",
 }
 _hpo_hass = FakeHass()
 _asyncio.run(_ha_setup_component(_integ, _hpo_hass))
@@ -43831,6 +44066,8 @@ _RC2_ROWS = [
 _RC2_ROWS += [
     (_rc2_button.ResetComfortWeightButton, "async_press", (), ("comfort", -1.9),
      ("coordinator._comfort_learner.evidence", 0.0)),
+    (_rc2_button.ResetHeatLossButton, "async_press", (), ("heat-loss", 1.8),
+     ("coordinator._house_heat_loss_scale", 1.0)),
     (_rc2_button.ForceOptimizationButton, "async_press", (), ("mode", "auto"), None),
     (_rc2_button.DiagnoseIntervalButton, "async_press", (), ("mode", "auto"), None),
     (_rc2_button.SystemIdentificationButton, "async_press", (), ("mode", "auto"), None),
@@ -43853,6 +44090,7 @@ _RC2_SETTERS = {
     "async_apply_manual_plan": "saves the plan before it asks for the refresh",
     "async_clear_manual_plan": "saves the clear before it asks for the refresh",
     "async_reset_comfort_weight": "row: the reset button",
+    "async_reset_heat_loss_learners": "row: the heat-loss reset button",
     "async_restore_learned_snapshot": "restores from the store it reads",
     "async_arm_system_identification": "in memory by design: arms tonight's run",
     "async_update_thermal_params": "the call's fields persist into entry "
@@ -43904,6 +44142,9 @@ async def _rc2_prelude(coord, what, value):
     elif what == "comfort":
         coord._comfort_learner.evidence = value
         await coord._async_save_accuracy()
+    elif what == "heat-loss":
+        coord._apply_house_heat_loss_scale(value)
+        await coord._async_save_thermal_learning()
     elif isinstance(what, str) and what.startswith("block-"):
         boost_mod.held_for(coord).set(
             what.removeprefix("block-"), value, _rc2_dt_util.now(), block=True,
@@ -43918,6 +44159,7 @@ async def _rc2_boot(entry):
     coord = HeatPumpOptimizerCoordinator(FakeHass(), entry)
     coord.hass.config_entries.entries.append(entry)
     await coord._async_load_accuracy()
+    await coord._async_load_thermal_learning()
     await boost_mod.restore_session(
         coord, coord._adopt_away_override, coord._config, coord._entity_state
     )
@@ -59845,6 +60087,8 @@ _P5_DISPOSED = {
     "_async_load_thermal_learning": "restore from the store",
     "_load_t4b_learners": "restore from the store",
     "_reanchor_house_heat_loss_scale": "re-expresses a restored scale (#86)",
+    "_void_heat_loss_learners": "voids evidence (a sensor swap, a nameplate edit, "
+    "the reset action); no evidence enters",
     # #2261: the COP fold's tail. _fold_measured_cop consults the freeze, and
     # a heat counter's span folds only when that consult passed on every cycle
     # of the span (_async_learn_heat_span); the two below it are fed only here.
diff --git a/tests/harness.py b/tests/harness.py
index a44d07112..6f29b8e37 100644
--- a/tests/harness.py
+++ b/tests/harness.py
@@ -454,6 +454,9 @@ class FakeCoordinator:
     async def async_reset_comfort_weight(self):
         self.pressed.append("reset_comfort_weight")
 
+    async def async_reset_heat_loss_learners(self):
+        self.pressed.append("reset_heat_loss")
+
 
 class FakeEntry:
     def __init__(
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._void_heat_loss_learners.GUARD_OFF.11a66faf.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._void_heat_loss_learners.GUARD_OFF.11a66faf.json
new file mode 100644
index 000000000..aee5b686b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._void_heat_loss_learners.GUARD_OFF.11a66faf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._void_heat_loss_learners GUARD_OFF 11a66faf",
+  "killed_by": "tests/features.py",
+  "old": "        if HEAT_LOSS_LEARNERS[1] in learners:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._void_heat_loss_learners.GUARD_OFF.5a8d9665.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._void_heat_loss_learners.GUARD_OFF.5a8d9665.json
new file mode 100644
index 000000000..b3d9507f6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._void_heat_loss_learners.GUARD_OFF.5a8d9665.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._void_heat_loss_learners GUARD_OFF 5a8d9665",
+  "killed_by": "tests/features.py",
+  "old": "        if HEAT_LOSS_LEARNERS[0] in learners:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._void_heat_loss_learners.RETURN_DEL.7055cd47.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._void_heat_loss_learners.RETURN_DEL.7055cd47.json
new file mode 100644
index 000000000..e6d13da18
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._void_heat_loss_learners.RETURN_DEL.7055cd47.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._void_heat_loss_learners RETURN_DEL 7055cd47",
+  "killed_by": "tests/features.py",
+  "old": "        return bool(learners)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/services.py/handle_reset_heat_loss.RETURN_DEL.d37047a8.json b/tests/mutation_ledger/killed_by/services.py/handle_reset_heat_loss.RETURN_DEL.d37047a8.json
new file mode 100644
index 000000000..acc06bc3e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/services.py/handle_reset_heat_loss.RETURN_DEL.d37047a8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/services.py:handle_reset_heat_loss RETURN_DEL d37047a8",
+  "killed_by": "tests/entities.py",
+  "old": "    return {\"reset\": reset, \"learners\": list(learners)}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/heat_loss_entity_voids.BOOLOP.19eef99a.json b/tests/mutation_ledger/killed_by/thermal_model.py/heat_loss_entity_voids.BOOLOP.19eef99a.json
new file mode 100644
index 000000000..3662bf48e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/heat_loss_entity_voids.BOOLOP.19eef99a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:heat_loss_entity_voids BOOLOP 19eef99a",
+  "killed_by": "tests/features.py",
+  "old": "        if key in was and (was[key] or None) != now.get(key)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if key in was or (was[key] or None) != now.get(key)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=15."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/heat_loss_entity_voids.GUARD_OFF.02cbf88f.json b/tests/mutation_ledger/killed_by/thermal_model.py/heat_loss_entity_voids.GUARD_OFF.02cbf88f.json
new file mode 100644
index 000000000..151c23b5a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/heat_loss_entity_voids.GUARD_OFF.02cbf88f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:heat_loss_entity_voids GUARD_OFF 02cbf88f",
+  "killed_by": "tests/features.py",
+  "old": "    if not isinstance(was, Mapping):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/heat_loss_zone_entities.RETURN_DEL.47e79f51.json b/tests/mutation_ledger/killed_by/thermal_model.py/heat_loss_zone_entities.RETURN_DEL.47e79f51.json
new file mode 100644
index 000000000..d6d377e51
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/heat_loss_zone_entities.RETURN_DEL.47e79f51.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:heat_loss_zone_entities RETURN_DEL 47e79f51",
+  "killed_by": "tests/features.py",
+  "old": "    return {key: cfg.get(key) or None for key in HEAT_LOSS_ZONE_ENTITIES}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/seam_map.json b/tests/seam_map.json
index 729e4bf64..a678a9b69 100644
--- a/tests/seam_map.json
+++ b/tests/seam_map.json
@@ -116,6 +116,7 @@
   "_horizon_step_starts": "core",
   "_heat_loss_anchors": "core",
   "_house_heat_loss_anchor": "core",
+  "_void_heat_loss_learners": "learning",
   "_immersion_dhw_margin": "dhw",
   "_indoor_humidity_value": "core",
   "_init_dhw_learning": "dhw",
@@ -213,6 +214,7 @@
   "async_publish_current_action": "views",
   "async_publish_ecl110_command": "views",
   "async_reset_comfort_weight": "learning",
+  "async_reset_heat_loss_learners": "learning",
   "async_restore_learned_snapshot": "learning",
   "async_run_optimization": "core",
   "async_set_away": "core",

