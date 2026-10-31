# Review packet #3038
head: d51d7c46caf7896426cb8e503f288e7c4c3db0b5
base: cabfaadc3a13f61eaf0303918c7b1d5beda9c07c

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=124480523689 success
arch-score / arch-score id=124490772552 success
arm id=124480295307 skipped
budget-raise-gate / budget-raise-gate id=124490772468 success
cancel-superseded id=124480297740 success
codeql id=124490773362 skipped
codeql / Analyze (actions) id=124480374857 success
codeql / Analyze (javascript-typescript) id=124480374895 success
codeql / Analyze (python) id=124480374929 success
gate id=124491176600 success
governance id=124490773478 skipped
governance / delivery-status id=124480375019 success
governance / delivery-status-publish id=124480375940 skipped
governance / env-matrix id=124480375020 success
governance / instrument-self-tests id=124480374882 success
governance / policy-docs id=124480374957 success
governance / record id=124480376219 skipped
governance / wave-script id=124480374980 success
hassfest id=124490773082 skipped
hassfest / hassfest id=124480374809 success
kernel-points id=124490773429 skipped
pr-contract / pr-contract id=124491029185 success
prelude id=124480297733 success
refresh id=124480297649 success
tests id=124490773155 skipped
tests / arch-instrument id=124480450908 success
tests / briefs id=124480374851 success
tests / browser id=124480450921 success
tests / ci-ratchet id=124486461746 skipped
tests / claims-autofix id=124485674618 skipped
tests / closure-scope id=124480374923 success
tests / closures id=124480450924 success
tests / closures-autofix id=124484866169 skipped
tests / coverage id=124480450889 success
tests / coverage-ratchet id=124486460396 success
tests / fast (3.14) id=124480450900 success
tests / graders-head-copy id=124486460314 success
tests / lane-proofs id=124486460311 success
tests / mutation id=124480374861 success
tests / mutation-autofix id=124490460715 skipped
tests / mutation-pins id=124490460363 skipped
tests / nightly-ha id=124480451974 skipped
tests / nightly-status id=124480374939 success
tests / replay id=124480450919 success
tests / typing id=124480450881 success
validate id=124490773209 skipped
validate / validate-hacs id=124480374802 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE stale tree: d51d7c46caf7896426cb8e503f288e7c4c3db0b5 lacks origin/main 0d33c9348b39ab289a64e26ac9c9f42c17adab7f; roster read at origin/main
NOTE body item 954c9135: R10-COP-GATE
NOTE body item 2eaaed41: R10-COP-GATE
NOTE body item be8b711f: R10-COP-GATE
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         tests/features.py
             `tests/features.py` is in the tree at this head
  ok         dev/audit/rounds/round10/study-ident/owner_rows.py
             `dev/audit/rounds/round10/study-ident/owner_rows.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/features.py
             `tests/features.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         node tests/card.mjs
             `tests/card.mjs` is in the tree at this head
  ok         NODE_OPTIONS=--max-old-space-size=8192 node tests/card.mjs
             `tests/card.mjs` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         bash tools/pr/prepr.sh body.md
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 10 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.cd19f403.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.cd19f403.json
new file mode 100644
index 000000000..63ac676bf
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.cd19f403.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._interval_space_power GUARD_OFF cd19f403",
+  "killed_by": "tests/features.py",
+  "old": "        if heat_energy.ran_hot_water(heat_energy.meter_of(self).attribution((commanded_space, dhw_share))):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.b36c07ff.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.fe5030a3.json
similarity index 63%
rename from tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.b36c07ff.json
rename to tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.fe5030a3.json
index cf6a9c195..55ee71d13 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.b36c07ff.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.fe5030a3.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._record_accuracy GUARD_OFF b36c07ff",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._record_accuracy GUARD_OFF fe5030a3",
   "killed_by": "tests/features.py",
-  "old": "        if pending is not None and pending.get(\"split\") is not None and pairs_interval(_utc_age_seconds(now, pending[\"when\"]) / 3600.0):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+  "old": "        if pending is not None and pending.get(\"split\") is not None and pairs_interval(_utc_age_seconds(now, pending[\"when\"]) / 3600.0) and not heat_energy.ran_hot_water(heat_energy.meter_of(self).attribution(pending[\"split\"])):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
 }
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/ran_hot_water.BOOLOP.39172521.json b/tests/mutation_ledger/killed_by/heat_energy.py/ran_hot_water.BOOLOP.39172521.json
new file mode 100644
index 000000000..b92e720e4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/ran_hot_water.BOOLOP.39172521.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:ran_hot_water BOOLOP 39172521",
+  "killed_by": "tests/features.py",
+  "old": "    return a.observed and a.dhw > 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return a.observed or a.dhw > 0.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/ran_hot_water.CMP_BOUND.39172521.json b/tests/mutation_ledger/killed_by/heat_energy.py/ran_hot_water.CMP_BOUND.39172521.json
new file mode 100644
index 000000000..1909dd074
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/ran_hot_water.CMP_BOUND.39172521.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:ran_hot_water CMP_BOUND 39172521",
+  "killed_by": "tests/features.py",
+  "old": "    return a.observed and a.dhw > 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return a.observed and a.dhw >= 0.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/ran_hot_water.RETURN_DEL.39172521.json b/tests/mutation_ledger/killed_by/heat_energy.py/ran_hot_water.RETURN_DEL.39172521.json
new file mode 100644
index 000000000..1e8cf6d2a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/ran_hot_water.RETURN_DEL.39172521.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:ran_hot_water RETURN_DEL 39172521",
+  "killed_by": "tests/features.py",
+  "old": "    return a.observed and a.dhw > 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index b4b07c4ea..4f5feaf70 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -4711,9 +4711,12 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         flow meter measures the interval's heat instead (#2016). The hot
         water subtracted is ``_commanded_split``'s, which zeroes a channel the
         observed mode cannot serve: a phantom allocation would bias every
-        sample low, in one direction (v5.3.0).
+        sample low, in one direction (v5.3.0). A mode dwell that saw hot water
+        leaves neither the reading nor the ask a space figure (``ran_hot_water``).
         """
         commanded_space, dhw_share = self._commanded_split()
+        if heat_energy.ran_hot_water(heat_energy.meter_of(self).attribution((commanded_space, dhw_share))):
+            return None
         if not getattr(self, "_ctx", self)._config.heat_pump_power_entity:
             return commanded_space
         # #1067: the pump's own heaters join the immersion latch, for the
@@ -4729,12 +4732,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         ):
             return None
         if self._pump_signals.mode_observed and not self._pump_signals.space_heat:
-            # v5.3.0: the pump is in a mode that heats no rooms, so whatever
-            # the meter is reading went somewhere else — hot water, or the
-            # cooling circuit. There is no space figure to extract, and
-            # returning zero would be a *confident* claim that the house got
-            # nothing, which the house heat-loss learner would then replay as
-            # thermal behaviour. Skip the sample instead.
+            # v5.3.0: a mode heating no rooms sent the reading elsewhere; a
+            # 0 kW sample would be a confident claim the house got nothing.
             return None
         # The subtraction only splits the meter correctly while the pump is
         # plausibly running the plan: a deferred DHW start, or a
@@ -9746,10 +9745,10 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         _fold_flow_lift(self, now)
         power_frozen = self._learning_frozen(CONF_POWER_ENTITY)  # read once: the defrost settlement below gates on it too
         # The meter read now closes the interval ``pending`` governed, so the
-        # draw pairs with that interval's ask and set-point, not the action the
-        # solve just adopted for the next one (#2262), within the window the
-        # accuracy pairing below trusts; a prediction recording no split is none.
-        if pending is not None and pending.get("split") is not None and pairs_interval(_utc_age_seconds(now, pending["when"]) / 3600.0):
+        # draw pairs with that interval's ask and set-point, not the next one's
+        # (#2262), within the window the accuracy pairing below trusts; a
+        # prediction recording no split, or a dwell that saw hot water, is none.
+        if pending is not None and pending.get("split") is not None and pairs_interval(_utc_age_seconds(now, pending["when"]) / 3600.0) and not heat_energy.ran_hot_water(heat_energy.meter_of(self).attribution(pending["split"])):
             draw_range.fold(self._accuracy.draw, self._measured_power, pending["split"], ctx._thermal_params, frozen=power_frozen is not None, distorted=_cop_fold_blocked(self), defrost=defrost_window.any_defrost, command=pending.get("flow_command"))
 
         # T5 #16: settle every matured lead-time promise against the same
diff --git a/custom_components/heatpump_optimizer/heat_energy.py b/custom_components/heatpump_optimizer/heat_energy.py
index cba578cc7..2081dd702 100644
--- a/custom_components/heatpump_optimizer/heat_energy.py
+++ b/custom_components/heatpump_optimizer/heat_energy.py
@@ -242,6 +242,16 @@ def space_heat_kw(heat_kw: float | None, a: Attribution, integrated: bool) -> fl
     return heat_kw if a.dhw <= 0.0 < a.space else None
 
 
+def ran_hot_water(a: Attribution) -> bool:
+    """Whether the dwell saw the pump on hot water within the interval.
+
+    A meter reading taken at the close is then not the interval's space
+    figure, whatever the plan asked. An unobserved interval says nothing
+    here: the caller's own plan rule stands.
+    """
+    return a.observed and a.dhw > 0.0
+
+
 def cop_duty(a: Attribution, share_limit: float) -> str | None:
     """The curve a COP sample is judged against: one duty, or ``None`` for a blend."""
     total = a.space + a.dhw
diff --git a/dev/programme/delivery/3038.md b/dev/programme/delivery/3038.md
new file mode 100644
index 000000000..ae6b8c5d6
--- /dev/null
+++ b/dev/programme/delivery/3038.md
@@ -0,0 +1 @@
+- [#3038](https://github.com/tvofi/heatpump_optimizer/pull/3038) — **open**, R10-COP-GATE part 6 (R10-COP-GATE)
diff --git a/tests/features.py b/tests/features.py
index 3e5c55705..b2438c8d0 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -67179,6 +67179,88 @@ R.check(
     f"0.15 {_cf_s15} / 0.16 {_cf_s16}",
 )
 
+# R10-COP-GATE part 6 (leads 20 and 21): a point meter reading is the
+# interval's space figure only where the dwell saw the space circuit alone.
+# A switch-back window -- 0.45 h hot water, then 0.05 h space, under a
+# space-only plan -- books the 2.2 kW read at its close as neither the house
+# learners' space power nor a running sample of the space draw range. The
+# all-space dwell, and an interval with no dwell (the plan's own rule, here a
+# planned 1.0 kW hot-water share subtracted from a 3.2 kW total), are nulls.
+def _cg6_coord(segments, measured=2.2, dhw_kw=0.0, now=None, metered=True):
+    coord = _cf_coord(p_max=6.0)
+    if not metered:
+        coord = _Coord(_FakeHass(dict(_CF_STATES)), _FakeEntry(data={
+            k: v for k, v in dict(_L5_CFG, heat_pump_max_power=6.0, heat_pump_min_power=1.0).items()
+            if k != "heat_pump_power_entity"}))
+    coord._current_action = {"power": 2.2, "dhw_power": dhw_kw}
+    coord._measured_power = measured
+    meter = _cf_he.meter_of(coord)
+    now = now or _T6
+    at = now - timedelta(hours=sum(h for _, h in segments))
+    meter.cycle = (at, now)
+    meter.dwell.segments = []
+    for duty, hours in segments:
+        meter.dwell.segments.append(_cf_he.Segment(at, duty))
+        at += timedelta(hours=hours)
+    return coord
+
+
+_CG6_ARMS = {
+    "switch-back": ([(_cf_he.DHW, 0.45), (_cf_he.SPACE, 0.05)], 2.2, 0.0),
+    "hot water to the close": ([(_cf_he.SPACE, 0.05), (_cf_he.DHW, 0.45)], 2.2, 0.0),
+    "all-space": ([(_cf_he.SPACE, 0.5)], 2.2, 0.0),
+    "no dwell, planned hot water": ([(None, 0.5)], 3.2, 1.0),
+}
+_cg6_space = {
+    name: _cg6_coord(segs, measured, dhw)._interval_space_power()
+    for name, (segs, measured, dhw) in _CG6_ARMS.items()
+}
+R.check(
+    "a switch-back interval gives the house learners no space power; an "
+    "all-space dwell books the reading and an unobserved one the plan's "
+    "subtraction, as before (nulls)",
+    _cg6_space == {"switch-back": None, "hot water to the close": None,
+                   "all-space": 2.2, "no dwell, planned hot water": 2.2},
+    f"{_cg6_space}",
+)
+# With no power entity the ask is the only estimate, and it too stood for a
+# space duty the pump left; the all-space dwell still books the ask (null).
+_cg6_ask = {name: _cg6_coord(_CG6_ARMS[name][0], metered=False)._interval_space_power()
+            for name in ("switch-back", "all-space")}
+R.check(
+    "without a power entity a switch-back interval books no commanded space "
+    "power; an all-space dwell books the ask (null)",
+    _cg6_ask == {"switch-back": None, "all-space": 2.2},
+    f"{_cg6_ask}",
+)
+
+
+def _cg6_draw_folds(segments, measured, dhw_kw):
+    now = dt_util.now()
+    coord = _cg6_coord(segments, measured, dhw_kw, now=now)
+    coord._pending_prediction = {
+        "when": now - timedelta(minutes=30), "split": (2.2, dhw_kw), "flow_command": None,
+        "predicted_temp": 20.5, "power": 2.2 + dhw_kw, "space_power": 2.2,
+        "dhw_power": dhw_kw, "outdoor_temp": 8.0, "indoor_entity": "sensor.indoor",
+    }
+    before = len(coord._accuracy.draw.samples)
+    coord._record_accuracy()
+    return len(coord._accuracy.draw.samples) - before
+
+
+_cg6_folds = {
+    name: _cg6_draw_folds(segs, 2.2, 0.0)
+    for name, (segs, _measured, _dhw) in _CG6_ARMS.items() if name != "no dwell, planned hot water"
+}
+_cg6_folds["no dwell"] = _cg6_draw_folds([(None, 0.5)], 2.2, 0.0)
+R.check(
+    "a hot-water dwell under a space plan folds no running-draw sample; an "
+    "all-space dwell and an unobserved interval fold one each (nulls)",
+    _cg6_folds == {"switch-back": 0, "hot water to the close": 0,
+                   "all-space": 1, "no dwell": 1},
+    f"{_cg6_folds}",
+)
+
 # The refusal is published where Home Assistant does not hide it: the
 # observed-COP sensor is unavailable exactly while this is the explanation,
 # and an unavailable entity's attributes are suppressed. A 3 kW modulation
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.cd19f403.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.cd19f403.json
new file mode 100644
index 000000000..63ac676bf
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.cd19f403.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._interval_space_power GUARD_OFF cd19f403",
+  "killed_by": "tests/features.py",
+  "old": "        if heat_energy.ran_hot_water(heat_energy.meter_of(self).attribution((commanded_space, dhw_share))):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.b36c07ff.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.fe5030a3.json
similarity index 63%
rename from tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.b36c07ff.json
rename to tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.fe5030a3.json
index cf6a9c195..55ee71d13 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.b36c07ff.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.fe5030a3.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._record_accuracy GUARD_OFF b36c07ff",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._record_accuracy GUARD_OFF fe5030a3",
   "killed_by": "tests/features.py",
-  "old": "        if pending is not None and pending.get(\"split\") is not None and pairs_interval(_utc_age_seconds(now, pending[\"when\"]) / 3600.0):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+  "old": "        if pending is not None and pending.get(\"split\") is not None and pairs_interval(_utc_age_seconds(now, pending[\"when\"]) / 3600.0) and not heat_energy.ran_hot_water(heat_energy.meter_of(self).attribution(pending[\"split\"])):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
 }
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/ran_hot_water.BOOLOP.39172521.json b/tests/mutation_ledger/killed_by/heat_energy.py/ran_hot_water.BOOLOP.39172521.json
new file mode 100644
index 000000000..b92e720e4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/ran_hot_water.BOOLOP.39172521.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:ran_hot_water BOOLOP 39172521",
+  "killed_by": "tests/features.py",
+  "old": "    return a.observed and a.dhw > 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return a.observed or a.dhw > 0.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/ran_hot_water.CMP_BOUND.39172521.json b/tests/mutation_ledger/killed_by/heat_energy.py/ran_hot_water.CMP_BOUND.39172521.json
new file mode 100644
index 000000000..1909dd074
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/ran_hot_water.CMP_BOUND.39172521.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:ran_hot_water CMP_BOUND 39172521",
+  "killed_by": "tests/features.py",
+  "old": "    return a.observed and a.dhw > 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return a.observed and a.dhw >= 0.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/ran_hot_water.RETURN_DEL.39172521.json b/tests/mutation_ledger/killed_by/heat_energy.py/ran_hot_water.RETURN_DEL.39172521.json
new file mode 100644
index 000000000..1e8cf6d2a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/ran_hot_water.RETURN_DEL.39172521.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:ran_hot_water RETURN_DEL 39172521",
+  "killed_by": "tests/features.py",
+  "old": "    return a.observed and a.dhw > 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index f735922a4..ceb1d5c12 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17656,
+ "class_excess_loc": 17655,
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

