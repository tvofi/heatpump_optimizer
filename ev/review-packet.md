# Review packet #3220
head: 6dcd1abb85eca7b53bfe390c5b934907f38419f8
base: 499162c89d0f4f8369e16e6e41fb3a620bc1ecb0

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=126998111372 neutral
arch-score / arch-score id=126997344041 success
arm id=126996398214 skipped
budget-raise-gate / budget-raise-gate id=126997344061 success
cancel-superseded id=126996407695 success
codeql / Analyze (actions) id=126997343962 success
codeql / Analyze (javascript-typescript) id=126997343934 success
codeql / Analyze (python) id=126997343941 in_progress
governance / delivery-status id=126997344133 queued
governance / delivery-status-publish id=126997345331 skipped
governance / env-matrix id=126997344010 in_progress
governance / instrument-self-tests id=126997344064 in_progress
governance / policy-docs id=126997344004 in_progress
governance / record id=126997346182 skipped
governance / wave-script id=126997344034 success
hassfest / hassfest id=126997343925 success
kernel-points id=126997345727 skipped
prelude id=126996407693 in_progress
refresh id=126996407485 success
tests / briefs id=126997344011 success
tests / closure-scope id=126997344067 queued
tests / mutation id=126997344022 failure
tests / mutation-pins (1) id=126998444911 queued
tests / mutation-pins (2) id=126998445049 queued
tests / mutation-pins (3) id=126998444907 queued
tests / mutation-pins (4) id=126998444881 queued
tests / mutation-pins (5) id=126998444807 queued
tests / mutation-pins (6) id=126998444861 queued
tests / mutation-pins (7) id=126998444801 queued
tests / nightly-status id=126997344080 queued
validate / validate-hacs id=126997343834 success

## Refusals
red-unanswered: concluded red check `tests / mutation` is not named in ## Red checks

## Advisories
none

## carry_audit at the head
NOTE body item 31ee5e06: R10-FLY-REPLAY-MASK: R10-FLY-REPLAY-MASK resolved on origin/handoff/audit-r10-roster
NOTE body item 476710bb: R10-SAV-COMFORT
NOTE body item 0497bde5: R10-SAV-COMFORT
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 dev/audit/harnesses/r10_sav_wood_reference.py first
             `dev/audit/harnesses/r10_sav_wood_reference.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_sav_wood_reference.py valve-flat
             `dev/audit/harnesses/r10_sav_wood_reference.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_sav_wood_reference.py valve-vary
             `dev/audit/harnesses/r10_sav_wood_reference.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_sav_wood_reference.py --quick wood-cold
             `dev/audit/harnesses/r10_sav_wood_reference.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_sav_wood_reference.py --quick wood-stale
             `dev/audit/harnesses/r10_sav_wood_reference.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_sav_wood_reference.py --quick wood-coast
             `dev/audit/harnesses/r10_sav_wood_reference.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_sav_wood_reference.py --quick wood-fire
             `dev/audit/harnesses/r10_sav_wood_reference.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_sav_wood_reference.py --quick wood-full
             `dev/audit/harnesses/r10_sav_wood_reference.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_sav_wood_reference.py --quick wood-unforeseen
             `dev/audit/harnesses/r10_sav_wood_reference.py` is in the tree at this head
  ok         GOLDEN_MODE=drift GOLDEN_REF=2a9cd3476dae9f45d3091b546fdd2723bcb0ce4e PYTHONPATH=tests/hastub python3 tests/golden.py
             `tests/golden.py` is in the tree at this head
  ok         node tests/card_drift.mjs 2a9cd3476dae9f45d3091b546fdd2723bcb0ce4e
             `tests/card_drift.mjs` is in the tree at this head
  ok         python3 tests/closure.py select --diff 2a9cd3476dae9f45d3091b546fdd2723bcb0ce4e
             `tests/closure.py` is in the tree at this head
  ok         tests/optimality.py
             `tests/optimality.py` is in the tree at this head
  ok         tests/stress.py
             `tests/stress.py` is in the tree at this head
  ok         tests/card_browser.mjs
             `tests/card_browser.mjs` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tools/pr/ci_predict.py
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         node tests/card_browser.mjs
             `tests/card_browser.mjs` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  unverified git grep -n "_settle_horizon(\|_thermostat_held_state(\|_sharing_wood_side(" -- custom_components
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -nE "savings_pct|saving_pct" -- custom_components
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 19 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/ledger.py/savings_pct.RETURN_DEL.4bbcde55.json b/tests/mutation_ledger/killed_by/ledger.py/savings_pct.RETURN_DEL.4bbcde55.json
deleted file mode 100644
index 7f288f3b3..000000000
--- a/tests/mutation_ledger/killed_by/ledger.py/savings_pct.RETURN_DEL.4bbcde55.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/ledger.py:savings_pct RETURN_DEL 4bbcde55",
-  "killed_by": "tests/features.py",
-  "old": "    return float(np.clip(savings_sek / baseline_sek * 100.0, -100.0, 100.0))",
-  "reason": "Recorded by `mutation_table.py --drain` against 9111acceb7831fa4c16ed42a30c579cda404130f: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.BOOLOP.03ee6373.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.BOOLOP.03ee6373.json
deleted file mode 100644
index ad5623a79..000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.BOOLOP.03ee6373.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._compute_baseline_power BOOLOP 03ee6373",
-  "killed_by": "tests/features.py",
-  "old": "            if two_tank and state.wood_tank_temperature is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 5c0ee109305fc4f377c9326c712156b9ceb0e638: BOOLOP (`if two_tank or state.wood_tank_temperature is not None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.BOOLOP.64b1ab84.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.BOOLOP.64b1ab84.json
deleted file mode 100644
index 9478c052b..000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.BOOLOP.64b1ab84.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._compute_baseline_power BOOLOP 64b1ab84",
-  "killed_by": "tests/doc_claims.py",
-  "old": "                if external_heat_kw is not None and i < len(external_heat_kw)",
-  "reason": "Recorded by `mutation_table.py --drain` against a1da8d381aa0afd2d1be6753678a8fc6191604ec: BOOLOP (`if external_heat_kw is not None or i < len(external_heat_kw)`) took tests/doc_claims.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.CLAMP_DROP.bea58ed9.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.CLAMP_DROP.bea58ed9.json
deleted file mode 100644
index afe9dd76e..000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.CLAMP_DROP.bea58ed9.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._compute_baseline_power CLAMP_DROP bea58ed9",
-  "killed_by": "tests/features.py",
-  "old": "            required_thermal = max(0.0, required_thermal - ext_i)",
-  "reason": "Recorded by `mutation_table.py --drain`: CLAMP_DROP (`required_thermal = (0.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.03ee6373.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.03ee6373.json
deleted file mode 100644
index 0b61b3c95..000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.03ee6373.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._compute_baseline_power GUARD_OFF 03ee6373",
-  "killed_by": "tests/features.py",
-  "old": "            if two_tank and state.wood_tank_temperature is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 5c0ee109305fc4f377c9326c712156b9ceb0e638: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.308a9d57.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.308a9d57.json
deleted file mode 100644
index 11e2ce53b..000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.308a9d57.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._compute_baseline_power GUARD_OFF 308a9d57",
-  "killed_by": "tests/features.py",
-  "old": "        if not p.dhw_coil_active:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 9c6b923f2614936aad89e1408dabca8ddd721322: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.52814e2f.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.52814e2f.json
deleted file mode 100644
index 96147d56b..000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.52814e2f.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._compute_baseline_power GUARD_OFF 52814e2f",
-  "killed_by": "tests/features.py",
-  "old": "            if coil_draws is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 9c6b923f2614936aad89e1408dabca8ddd721322: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/valve_charge_demand.CLAMP_DROP.4f2d48ae.json b/tests/mutation_ledger/killed_by/thermal_model.py/valve_charge_demand.CLAMP_DROP.4f2d48ae.json
deleted file mode 100644
index 1c4506a69..000000000
--- a/tests/mutation_ledger/killed_by/thermal_model.py/valve_charge_demand.CLAMP_DROP.4f2d48ae.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:valve_charge_demand CLAMP_DROP 4f2d48ae",
-  "killed_by": "tests/features.py",
-  "old": "        min(t, p.buffer_max_temp) for _, top, zone in circuits for t in (top, zone)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`(t) for _, top, zone in circuits for t in (top, zone)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._compute_baseline_power.CMP_BOUND.64b1ab84.json b/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._compute_baseline_power.CMP_BOUND.64b1ab84.json
deleted file mode 100644
index 13c91481a..000000000
--- a/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._compute_baseline_power.CMP_BOUND.64b1ab84.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._compute_baseline_power CMP_BOUND 64b1ab84",
-  "old": "                if external_heat_kw is not None and i < len(external_heat_kw)",
-  "reason": "R10 mutation-anchor: the `killed_by: tests/entities.py` pin was vacuous. Re-driven at 0be5e2de5 by dev/audit/harnesses/r10_anchor_vacuous.py with the 2 ledger row(s) the mutant itself makes stale hidden from its tree, 0 of 1 site(s) were killed by tests/entities.py: the recorded kill was a check refusing a ledger row the mutant made stale (the --anchor self-test, or the survivor_triage staleness check), not one that saw the mutation. Was: Recorded by `mutation_table.py --drain` against 816547efe270a08e18e3b92f52185fe8c1fee2ef: CMP_BOUND (`if external_heat_kw is not None and i <= len(external_heat_kw)`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1. Not re-driven here against the other drivers in its closure, so a gap until one is shown to kill it.",
-  "verdict": "gap"
-}


## Three-dot diff
diff --git a/README.md b/README.md
index e62f74c36..6418a5b7e 100644
--- a/README.md
+++ b/README.md
@@ -580,7 +580,7 @@ every sensor is created on every install regardless of which group it is in.
 
 | Sensor | Unit | What it tells you | Notes |
 |---|---|---|---|
-| Plan Predicted Savings | CUR | Saving over 24 h against a simulated conventional thermostat following the same comfort schedule | Only the hot-water half of the baseline is always-on |
+| Plan Predicted Savings | CUR | Saving over 24 h against a simulated conventional thermostat following the same comfort schedule, with no wood: heat from wood counts in the saving, firewood's cost does not | Only the hot-water half of the baseline is always-on |
 | Plan Savings Percentage | % | The same saving as a percentage | |
 | Cost Predicted | CUR | Cost of the optimized 24 h plan | |
 | Cost Baseline | CUR | Cost of the baseline over the same 24 h | |
diff --git a/custom_components/heatpump_optimizer/const.py b/custom_components/heatpump_optimizer/const.py
index b1e71b925..ea3065c28 100644
--- a/custom_components/heatpump_optimizer/const.py
+++ b/custom_components/heatpump_optimizer/const.py
@@ -655,7 +655,7 @@ ACCURACY_STORE_VERSION: Final = 1
 ENERGY_STORE_VERSION: Final = 1
 # One version per store (#1740): a bump migrates the store it names, no other.
 SNAPSHOT_STORE_VERSION: Final = 1
-LEDGER_STORE_VERSION: Final = 1
+LEDGER_STORE_VERSION: Final = 2
 
 
 # Service for the card's what-if simulator (item 21).
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index eb26be357..2cfb5c9a2 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -87,7 +87,7 @@ from .payload import (
     SpacePlan,
     ThermalView,
 )
-from .store import QuarantiningStore, admitted, load_mapping
+from .store import LedgerStore, QuarantiningStore, admitted, load_mapping
 from .entry_config import EntryConfig, factory_settings, undo_point, undone_settings
 from homeassistant.util import dt as dt_util
 
@@ -3627,7 +3627,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         # offending value, cleared unconditionally (setpoint_check.ConfigNotices).
         self._config_notices = setpoint_check.ConfigNotices()
         self._ledger = MonthlyLedger()
-        self._ledger_store: QuarantiningStore[dict[str, Any]] = QuarantiningStore(
+        self._ledger_store: LedgerStore[dict[str, Any]] = LedgerStore(
             hass,
             LEDGER_STORE_VERSION,
             f"{DOMAIN}_{entry.entry_id}_ledger",
@@ -7857,7 +7857,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             "peak_month": self._peak_tracker.month,
             "pv_enabled": _ctx_of(self)._config.pv_enabled,
             "pv": self._pv_summary,
-            "savings_months": self._ledger.savings_months(dt_util.now()),
+            "savings_months": self._ledger.savings_months(dt_util.now(), wood_configured=wood_furnace_on(_ctx_of(self)._config)),
             "receipts": [self._month_reports[k] for k in sorted(self._month_reports)],
             "plan_replay": self._accuracy.replay(dt_util.now()),
         }
diff --git a/custom_components/heatpump_optimizer/dhw_planner.py b/custom_components/heatpump_optimizer/dhw_planner.py
index 3ab8a43eb..97bee8dc7 100644
--- a/custom_components/heatpump_optimizer/dhw_planner.py
+++ b/custom_components/heatpump_optimizer/dhw_planner.py
@@ -373,26 +373,10 @@ class DhwPlanner:
         standby_loss = p.dhw_tank_heat_loss_coefficient * max(
             dhw_setpoint - TANK_ROOM_AMBIENT_TEMP, 0.0
         )
-        baseline_draw = p.dhw_draw_power
-        if (
-            p.dhw_coil_active
-            and initial_state.wood_tank_temperature is not None
-        ):
-            # The baseline house owns the same refill coil (v3.15.1) — the
-            # plumbing is not optimizer value. Held at the initial wood
-            # temperature for the whole day: the real coil weakens as the
-            # tank cools, so this makes the baseline at least as cheap as
-            # reality and the reported savings err low, never high.
-            baseline_draw, _ = dhw_coil_draw_reduction(
-                baseline_draw,
-                initial_state.wood_tank_temperature,
-                p.dhw_setpoint,
-                # The same inlet reference the draw itself was computed from;
-                # see dhw_coil_draw_reduction for why the two must agree.
-                inlet_temp=p.dhw_inlet_reference,
-            )
+        # The reference house has no wood side, so no refill coil: whatever the
+        # coil saves counts in the saving (owner ruling, 2026-11-04).
         baseline_dhw = np.full(
-            n_steps, power_for_heat_per_cop_kw(p, (baseline_draw + standby_loss) / cop_dhw))
+            n_steps, power_for_heat_per_cop_kw(p, (p.dhw_draw_power + standby_loss) / cop_dhw))
         # All three figures are piecewise in the PV surplus, like the objective.
         # The baseline house would self-consume the same sun, so pricing only
         # the optimized plan that way would manufacture fictitious savings.
diff --git a/custom_components/heatpump_optimizer/ledger.py b/custom_components/heatpump_optimizer/ledger.py
index 8e0507118..a2afeec8e 100644
--- a/custom_components/heatpump_optimizer/ledger.py
+++ b/custom_components/heatpump_optimizer/ledger.py
@@ -65,6 +65,18 @@ SPOT_PRICE_META = "spot_price"
 #: 2026-10-24): the baseline runs at the power levels the pump recorded.
 SAVINGS_PLAN_LINE = "savings_plan"
 
+#: Which reference a month's savings lines were booked against. Stamped on the
+#: month's first booking; a month's totals cannot be rebooked, so a row whose
+#: stamp is not ``REFERENCE_BASIS`` keeps its two columns and states no saving.
+REFERENCE_BASIS_META = "reference_basis"
+
+#: The reference in force: a heat-pump thermostat with no wood tank and no fire,
+#: its horizon spread by steady demand. Bump when the booked reference changes.
+REFERENCE_BASIS = 1
+
+#: What ``migrate_ledger_v1`` stamps: every month a v1 store holds predates it.
+OLD_REFERENCE_BASIS = 0
+
 #: Below this many modelled kWh a month the plan commanded almost nothing:
 #: a meter-over-model ratio over it measures the meter's own residue, not
 #: the plan's power levels, so the thermostat stays at modelled power.
@@ -115,14 +127,30 @@ def coverage_factor(meta: Mapping[str, Any], now: datetime) -> float:
 
 
 def savings_pct(baseline_sek: float, savings_sek: float) -> float | None:
-    """Same clip as optimizer._savings_percentage, but None when the baseline is ~0.
+    """The saving over the baseline, in percent; None when the baseline is ~0.
 
-    The optimizer helper returns 0.0 in that case; the published row must omit
-    the percentage instead of claiming 0 %.
+    Unclipped: the row publishes both amounts beside it, so -100 beside a saving
+    six times its baseline states what the row's own figures refute. The plan's
+    clip (``optimizer._savings_percentage``) guards a near-zero baseline, which
+    this answers by omitting the figure.
     """
     if baseline_sek <= 0.01:
         return None
-    return float(np.clip(savings_sek / baseline_sek * 100.0, -100.0, 100.0))
+    return savings_sek / baseline_sek * 100.0
+
+
+def migrate_ledger_v1(stored: dict[str, Any]) -> dict[str, Any]:
+    """A v1 ledger document at v2: every month it holds is on the old basis.
+
+    Only a meta entry is added; no line, so no total, is rewritten.
+    """
+    ledger = stored.get("ledger")
+    months = ledger.get("months") if isinstance(ledger, dict) else None
+    for month in months.values() if isinstance(months, dict) else ():
+        meta = month.get("meta") if isinstance(month, dict) else None
+        if isinstance(meta, dict):
+            meta.setdefault(REFERENCE_BASIS_META, {"sum": float(OLD_REFERENCE_BASIS), "count": 1})
+    return stored
 
 
 def _leaf(raw: Any) -> float:
@@ -255,8 +283,11 @@ class MonthlyLedger:
         """
         if baseline_kw is None or not all(np.isfinite(v) for v in (baseline_kw, actual_kwh, spot, dt)):
             return
-        lines = self._month(month_key(when))["lines"]
+        month = self._month(month_key(when))
+        lines = month["lines"]
         calibrated = SAVINGS_PLAN_LINE in lines or "savings_baseline" not in lines
+        if "savings_baseline" not in lines:
+            month["meta"].setdefault(REFERENCE_BASIS_META, {"sum": float(REFERENCE_BASIS), "count": 1})
         base_kwh = float(baseline_kw) * float(dt)
         self.add(
             when, "savings_baseline", kwh=base_kwh, sek=base_kwh * float(spot)
@@ -382,7 +413,7 @@ class MonthlyLedger:
             return None
         return self.line(month, "savings_actual")["kwh"] / plan_kwh
 
-    def savings_months(self, now: datetime) -> list[SavingsMonth]:
+    def savings_months(self, now: datetime, *, wood_configured: bool = False) -> list[SavingsMonth]:
         """Published rows: months that booked savings_baseline, oldest first.
 
         One basis for every cell: the intervals a plan covered, priced at
@@ -392,11 +423,15 @@ class MonthlyLedger:
         are the pump's recorded ones and a model that under-reads the meter
         is not booked as a loss; ``savings_sek`` is the one less the other.
         At one flat price the saving is the volume difference alone. The
+        reference has no wood, so wood's heat counts in the saving and
+        firewood's cost nowhere (owner ruling, 2026-11-04). The
         lines no thermostat prices (capacity, wear, uncovered intervals)
         are in neither column: the receipt states them.
 
         The open month is an estimate: every figure is scaled by
-        ``coverage_factor``.
+        ``coverage_factor``. A month booked against another reference
+        (``REFERENCE_BASIS_META``) states its two columns and no saving. With
+        wood configured the calibration only raises the thermostat.
         """
         open_key = month_key(now)
         rows: list[SavingsMonth] = []
@@ -405,6 +440,11 @@ class MonthlyLedger:
             if "savings_baseline" not in lines:
                 continue
             calibration = self.meter_calibration(key)
+            if wood_configured and calibration is not None:
+                # A meter under the plan is what a fire the plan did not foresee
+                # looks like; scaling down by it would cancel wood's heat from
+                # the saving. Only an under-read model is corrected here.
+                calibration = max(1.0, calibration)
             baseline_sek = self.line(key, "savings_baseline")["sek"] * (
                 1.0 if calibration is None else calibration
             )
@@ -416,13 +456,15 @@ class MonthlyLedger:
                 actual_sek *= factor
             baseline_sek, actual_sek = round(baseline_sek, 2), round(actual_sek, 2)
             saved = round(baseline_sek - actual_sek, 2)
+            old_basis = self.meta_mean(key, REFERENCE_BASIS_META) != REFERENCE_BASIS
             rows.append(
                 {
                     "month": key,
                     "baseline_sek": baseline_sek,
                     "actual_sek": actual_sek,
-                    "savings_sek": saved,
-                    "savings_pct": savings_pct(baseline_sek, saved),
+                    "savings_sek": None if old_basis else saved,
+                    "savings_pct": None if old_basis else savings_pct(baseline_sek, saved),
+                    "old_basis": old_basis,
                     "estimated": estimated,
                     "meter_calibration": None if calibration is None else round(calibration, 3),
                 }
diff --git a/custom_components/heatpump_optimizer/notifier.py b/custom_components/heatpump_optimizer/notifier.py
index 61efc3082..38f662f70 100644
--- a/custom_components/heatpump_optimizer/notifier.py
+++ b/custom_components/heatpump_optimizer/notifier.py
@@ -54,6 +54,7 @@ EVENT_MANUAL_PLAN_RELEASED = f"{DOMAIN}_manual_plan_released"
 EVENT_DATA: dict[str, tuple[str, ...]] = {
     EVENT_MONTHLY_RECEIPT: (
         "entry_id", "month", "total_sek", "saving_sek", "saving_pct", "currency",
+        "saving_old_basis", "saving_includes_wood",
     ),
     EVENT_COMFORT_AT_RISK: (
         "entry_id", "predicted_min_c", "at", "floor_c",
@@ -95,6 +96,11 @@ def _monthly_receipt(data: Payload) -> Detected:
         "saving_sek": saving.get("savings_sek") if saving else None,
         "saving_pct": saving.get("savings_pct") if saving else None,
         "currency": data.get("currency"),
+        # What the card states beside the figure: a month on a retired reference
+        # has no saving, and with wood configured the saving includes its heat
+        # and not its cost.
+        "saving_old_basis": bool(saving and saving.get("old_basis")),
+        "saving_includes_wood": bool((data.get("wood_fuel") or {}).get("show_whatif")),
     })}
 
 
diff --git a/custom_components/heatpump_optimizer/optimizer.py b/custom_components/heatpump_optimizer/optimizer.py
index 6814f859d..ce7308f9d 100644
--- a/custom_components/heatpump_optimizer/optimizer.py
+++ b/custom_components/heatpump_optimizer/optimizer.py
@@ -106,8 +106,8 @@ from .thermal_model import (
     delivered_heat_kw,
     project_planned_levels,
     valve_charge_demand,
+    valve_hold_temperature,
     weather_or_calm,
-    wood_share,
     power_for_heat_per_cop_kw,
     added_power_for_heat_per_cop_kw,
 )
@@ -392,6 +392,28 @@ def _floor_demand_at_target(
     return u_lower * (target - outdoor_temp) - q_solar_lower - q_int_lower
 
 
+#: The wood side of a reference that has none: colder than any zone it could feed.
+_NO_WOOD_TANK_C = 0.0
+
+
+def _sharing_wood_side(reference: ThermalState, plan: ThermalState) -> ThermalState:
+    """The reference with the plan's wood side: heat wood left, or brought, is no store to settle."""
+    return replace(reference, wood_tank_temperature=plan.wood_tank_temperature)
+
+
+def _wood_covered_share(model: ThermalModel, state: ThermalState, reference_kwh: float, target: float) -> float:
+    """The share of the reference's kWh the plan's measured wood tank could cover.
+
+    The reference has no wood and the plan's house does, so its starts anchor on
+    what that house buys. Starts only: it decides nothing the reference reports.
+    """
+    p = model.params
+    if not p.two_tank_modelled or state.wood_tank_temperature is None or reference_kwh <= 0.0:
+        return 0.0
+    usable_kwh_th = p.wood_tank_thermal_mass * max(0.0, state.wood_tank_temperature - target)
+    return min(1.0, usable_kwh_th / p.cop_nominal_floored / reference_kwh)
+
+
 def _thermostat_held_state(
     model: ThermalModel, state: ThermalState, weather: WeatherSeries, target: float
 ) -> ThermalState:
@@ -399,8 +421,9 @@ def _thermostat_held_state(
 
     The zones at ``target`` and the slab at the temperature that delivers the
     step's demand -- the cascade's own slab target with no pull-back -- so the
-    first step draws the steady holding power. Tanks and every other field
-    stay as measured; the thermostat does not own them.
+    first step draws the steady holding power. Behind a valve its tank sits at
+    the temperature that delivers the need, whatever the plan left in the
+    measured one. Every other field stays as measured.
     """
     if not len(weather.outdoor_temps):
         return state
@@ -410,13 +433,32 @@ def _thermostat_held_state(
         model, target, float(weather.outdoor_temps[0]), float(weather.wind_speeds[0]),
         float(weather.precipitation[0]), float(weather.solar_radiation[0]),
     )
-    return replace(
+    held = replace(
         state,
         room_temperature=target,
         upper_floor_temperature=target,
         lower_floor_temperature=target,
         slab_temperature=target + max(0.0, q_floor) / model.params.slab_heat_transfer_floored,
     )
+    p = model.params
+    if not mixing_valve.is_throttling(p.mixing_valve_mode):
+        return held
+    wind, rain = float(weather.wind_speeds[0]), float(weather.precipitation[0])
+    outdoor = float(weather.outdoor_temps[0])
+    zoned = _thermostat_demand_two_zone if p.two_zone_enabled else _thermostat_demand_single
+    need = zoned(
+        model, held, target, outdoor, wind, rain, float(weather.solar_radiation[0]),
+        0.25, p.slab_heat_transfer_floored,
+    )
+    held.buffer_tank_temperature = (
+        valve_hold_temperature(model, held, need, outdoor, wind, rain)
+        if need > 0.0 else held.buffer_tank_temperature
+    )
+    if p.two_tank_modelled:
+        # The reference has no wood: below every zone the valve takes nothing
+        # from this side (``wood_share`` 0), so the step is the plain valve's.
+        held.wood_tank_temperature = _NO_WOOD_TANK_C
+    return held
 
 
 def _thermostat_demand_single(
@@ -4568,11 +4610,14 @@ class HeatPumpOptimizer:
         baseline_power, baseline_end = self._compute_baseline_power(
             weather, initial_state, dt, comfort_targets,
         )
-        baseline_energy = float(np.sum(baseline_power) * dt)
+        seed_power = baseline_power * (1.0 - _wood_covered_share(
+            self.model, initial_state, float(np.sum(baseline_power) * dt), self.config.target_temp,
+        ))
+        baseline_energy = float(np.sum(seed_power) * dt)
         starts = [
             initial_power,
             _price_ranked_start(prices, baseline_energy, p_max, dt),
-            np.clip(baseline_power, 0.0, p_max),
+            np.clip(seed_power, 0.0, p_max),
             _price_ranked_start(
                 prices,
                 baseline_energy * _LOW_ENERGY_START_FRACTION,
@@ -4669,7 +4714,7 @@ class HeatPumpOptimizer:
             valve_targets=h.valve_targets, humidity=h.humidity,
         )
         deferred_cost = self._settle_horizon(
-            h, weather, comfort_targets, baseline_end, optimized_end, baseline_cost,
+            h, weather, comfort_targets, _sharing_wood_side(baseline_end, optimized_end), optimized_end, baseline_cost,
         )
         savings = baseline_cost - predicted_cost - deferred_cost
 
@@ -4926,12 +4971,10 @@ class HeatPumpOptimizer:
         # schedules.
         achieved_objective = float(objective(optimal_space, optimal_dhw))
 
-        # Baseline cost; its house owns the plan's refill coil and draws. The
-        # reference holds the comfort schedule, not the comfort the plan
+        # Baseline cost. The reference holds the comfort schedule, not the comfort the plan
         # delivered (#2255): the baseline must not move with the plan's start.
         baseline_power, baseline_end = self._compute_baseline_power(
             weather, initial_state, dt, comfort_targets,
-            coil_draws=dhw_draw_rates, coil_dhw_temp=dhw_setpoint,
         )
         baseline_dhw, baseline_cost, predicted_cost, dhw_cost = (
             planner._baseline_dhw_economics(
@@ -4951,7 +4994,7 @@ class HeatPumpOptimizer:
         # the horizon. Outside a demand window that is the idle minimum, so a
         # cold tank at midnight is not treated as borrowed heat.
         deferred_cost = self._settle_horizon(
-            h, weather, comfort_targets, baseline_end, optimized_end,
+            h, weather, comfort_targets, _sharing_wood_side(baseline_end, optimized_end), optimized_end,
             float(energy_cost_of(baseline_power)),
             dhw_caps=self._settlement_caps(
                 outdoor_temps, dhw_cap=float(dhw_floor_temps[-1]), humidity=h.humidity
@@ -5251,8 +5294,6 @@ class HeatPumpOptimizer:
         initial_state: ThermalState,
         dt: float,
         comfort_targets: np.ndarray | None = None,
-        coil_draws: np.ndarray | None = None,
-        coil_dhw_temp: float = 0.0,
     ) -> tuple[np.ndarray, ThermalState]:
         """Simulate a conventional thermostat following the comfort schedule.
 
@@ -5277,17 +5318,19 @@ class HeatPumpOptimizer:
         running all along never inherits the optimiser's coasted or
         pre-heated house, whose recovery transient the settlement booked.
 
+        The reference has no wood: no wood tank, no fire, no refill coil, on
+        every house (owner ruling, 2026-11-04). The actual stays metered, so
+        wood's heat counts in the saving, and firewood's cost is not counted;
+        the card says so where wood is configured.
+
         Returns the power schedule and the final state, the latter so the
         caller can account for the thermal energy left stored at the end of the
-        horizon. ``coil_draws`` (the hot-water path's raw draws) runs the
-        wood-tank refill coil on that state each step, from a tank at
-        ``coil_dhw_temp``, as the plan's own trajectory does.
+        horizon.
         """
         outdoor_temps = weather.outdoor_temps
         wind_speeds = weather.wind_speeds
         precipitation = weather.precipitation
         solar_radiation = weather.solar_radiation
-        external_heat_kw = weather.external_heat_kw
         humidity = weather.humidity
         # The thermostat runs the same heat-loss physics as the plan, so its
         # weather is the horizon's: the series the loss multiplies are
@@ -5297,64 +5340,20 @@ class HeatPumpOptimizer:
         assert solar_radiation is not None
         n_steps = len(outdoor_temps)
         p = self.model.params
-        if not p.dhw_coil_active:
-            coil_draws = None
 
         baseline_power = np.zeros(n_steps)
         # Read once, not per step: the loop below runs to the horizon's end.
         targets = _baseline_targets(comfort_targets, n_steps, self.config.target_temp)
         hums = [None] * n_steps if humidity is None else np.asarray(humidity, float).tolist()
-        two_tank, k_slab = p.two_tank_modelled, p.slab_heat_transfer_floored
+        k_slab = p.slab_heat_transfer_floored
         state = _thermostat_held_state(self.model, initial_state, weather, targets[0])
 
         for i in range(n_steps):
             target = targets[i]
-            required_thermal = _thermostat_demand(
+            required_thermal = max(0.0, _thermostat_demand(
                 self.model, state, target, outdoor_temps[i], wind_speeds[i],
                 precipitation[i], solar_radiation[i], dt, k_slab,
-            )
-
-            # A thermostat's house receives a furnace burn too, and its
-            # sensor sees the warmth: the reference backs off by the free
-            # heat, or the burn would be booked as optimizer savings.
-            ext_i = (
-                float(external_heat_kw[i])
-                if external_heat_kw is not None and i < len(external_heat_kw)
-                else 0.0
-            )
-            if two_tank and state.wood_tank_temperature is not None:
-                # With the wood tank modelled, the 4-way valve covers part
-                # of the draw from the wood side; the reference backs its
-                # electric demand off by that share, computed with the SAME
-                # wood_share law the plan's physics uses so the two cannot
-                # drift. Subtracting ext_i afterwards as well is deliberate
-                # double counting in the conservative direction: the
-                # baseline can only get cheaper, so reported savings are
-                # understated, never inflated.
-                u_up = self.model.effective_heat_loss_coefficient(
-                    p.upper_floor_heat_loss, wind_speeds[i], precipitation[i]
-                )
-                u_lo = self.model.effective_heat_loss_coefficient(
-                    p.lower_floor_heat_loss_learned,
-                    wind_speeds[i] * 0.5, precipitation[i] * 0.5,
-                )
-                design_power = p.max_electrical_power * p.cop_nominal_floored
-                flow_set = mixing_valve.flow_setpoint(
-                    target_temp=p.mixing_valve_target or p.comfort_ceiling,
-                    outdoor_temp=float(outdoor_temps[i]),
-                    heat_loss_coefficient=u_up + u_lo,
-                    emitter_ua=design_power / p.emitter_design_delta_t_floored,
-                )
-                w_i = wood_share(
-                    state.wood_tank_temperature,
-                    state.buffer_tank_temperature,
-                    flow_set,
-                    min(
-                        state.upper_floor_temperature, state.slab_temperature
-                    ),
-                )
-                required_thermal *= 1.0 - w_i
-            required_thermal = max(0.0, required_thermal - ext_i)
+            ))
 
             hum_i = hums[i]
             cop = _reference_cop(self.model, state, outdoor_temps[i], hum_i)
@@ -5369,15 +5368,37 @@ class HeatPumpOptimizer:
             state = self.model.simulate_step(
                 state, power, outdoor_temps[i],
                 wind_speeds[i], precipitation[i], solar_radiation[i], dt,
-                external_heat_kw=ext_i, humidity=hum_i,
+                humidity=hum_i,
             )
-            if coil_draws is not None:
-                self.model.apply_dhw_coil(
-                    state, float(coil_draws[i]), coil_dhw_temp, dt
-                )
 
+        if mixing_valve.is_throttling(p.mixing_valve_mode):
+            baseline_power = self._apportion_by_steady_demand(baseline_power, weather, targets)
         return baseline_power, state
 
+    def _apportion_by_steady_demand(
+        self, simulated: np.ndarray, weather: WeatherSeries, targets: list[float]
+    ) -> np.ndarray:
+        """The simulated horizon's energy, spread by the steady demand per step.
+
+        Behind a valve the first steps are the stores' transient, not the
+        thermostat's power: a tank above the curve zeroes them, one below it
+        overshoots. The settlement books step 0 of a plan re-made every
+        interval, so it would book only the transient. The simulation decides
+        how much the horizon draws; the demand decides when.
+        """
+        assert weather.wind_speeds is not None and weather.precipitation is not None
+        assert weather.solar_radiation is not None
+        steady = np.array([
+            max(0.0, _floor_demand_at_target(
+                self.model, targets[i], float(weather.outdoor_temps[i]),
+                float(weather.wind_speeds[i]), float(weather.precipitation[i]),
+                float(weather.solar_radiation[i]),
+            ))
+            for i in range(len(simulated))
+        ])
+        total = float(np.sum(steady))
+        return simulated if total <= 0.0 else steady * (float(np.sum(simulated)) / total)
+
     def _settle_horizon(
         self,
         h: _Horizon,
@@ -5427,10 +5448,10 @@ class HeatPumpOptimizer:
         heat the thermostat buys plus the end's credit (``end_cost`` below 0),
         never more -- a summer house's passive warmth displaced nothing.
         """
-        held = _thermostat_held_state(
+        held = _sharing_wood_side(_thermostat_held_state(
             self.model, initial_state, weather,
             _baseline_target(comfort_targets, 0, self.config.target_temp),
-        )
+        ), initial_state)
         capped = self._deferred_energy_cost(
             held, initial_state, prices, outdoor_temps, caps=caps, humidity=humidity,
         )
diff --git a/custom_components/heatpump_optimizer/payload.py b/custom_components/heatpump_optimizer/payload.py
index 5d9a01055..d6fba3af1 100644
--- a/custom_components/heatpump_optimizer/payload.py
+++ b/custom_components/heatpump_optimizer/payload.py
@@ -249,8 +249,10 @@ class SavingsMonth(TypedDict, total=False):
     month: str
     baseline_sek: float
     actual_sek: float
-    savings_sek: float
+    savings_sek: float | None
     savings_pct: float | None
+    # Booked against a retired reference: the two columns stand, no saving does.
+    old_basis: bool
     estimated: bool
     # Metered over modelled kWh on the row's intervals: the factor the
     # thermostat's cost is scaled by; None where it was left at modelled.
diff --git a/custom_components/heatpump_optimizer/store.py b/custom_components/heatpump_optimizer/store.py
index 835b23ba4..a96f097fa 100644
--- a/custom_components/heatpump_optimizer/store.py
+++ b/custom_components/heatpump_optimizer/store.py
@@ -49,7 +49,7 @@ from .price_tiles import TILE_NAMES
 from .drift import REFERENCE_PRIOR_COV, STAT_CAP_FACTOR
 from .flow_lift import FLOW_BIAS_CLAMP_K, FLOW_SUPPLY_MAX_C
 from .freq_control import FREQ_DECILES, FREQ_MAX_KW_PER_HZ
-from .ledger import BILLED_LINES
+from .ledger import BILLED_LINES, migrate_ledger_v1
 from .price_model import (
     QUARTER_FACTOR_MAX, QUARTER_FACTOR_MIN, RESIDUAL_VAR_MAX, SHAPE_MAX, SHAPE_MIN,
 )
@@ -820,3 +820,14 @@ class QuarantiningStore(Store[_StorePayload]):
         """
         if self._reading is not None:
             await asyncio.shield(self._reading)
+
+
+class LedgerStore(QuarantiningStore):
+    """The money store; v2 stamps what a v1 document holds as the old basis."""
+
+    async def _async_migrate_func(
+        self, old_major_version: int, old_minor_version: int, old_data: Any
+    ) -> Any:
+        if old_major_version == 1 and isinstance(old_data, dict):
+            return migrate_ledger_v1(old_data)
+        return await super()._async_migrate_func(old_major_version, old_minor_version, old_data)
diff --git a/custom_components/heatpump_optimizer/thermal_model.py b/custom_components/heatpump_optimizer/thermal_model.py
index 2864ac70e..b873faaf3 100644
--- a/custom_components/heatpump_optimizer/thermal_model.py
+++ b/custom_components/heatpump_optimizer/thermal_model.py
@@ -1897,6 +1897,30 @@ def _circuit_draw(circuits: list[tuple[float, float, float]], tank: float) -> fl
     return sum(ua * max(0.0, min(tank, top) - zone) for ua, top, zone in circuits)
 
 
+def valve_hold_temperature(
+    model: "ThermalModel", state: ThermalState, need_kw: float,
+    outdoor_temp: float, wind_speed: float, precipitation: float,
+) -> float:
+    """The lowest tank temperature whose draw behind the valve is ``need_kw``.
+
+    Capped at the curve the valve mixes down to and ``buffer_max_temp``: heat
+    above it reaches no emitter. Where a thermostat keeps its tank
+    (R10-BUFFER-STORE), and so where its first step starts from.
+    """
+    p = model.params
+    circuits = _valve_draw_circuits(
+        model, state, outdoor_temp, wind_speed, precipitation)
+    # The draw is piecewise linear in the tank temperature, kinked where a
+    # circuit starts drawing (its zone) and where its curve caps it; the
+    # highest kink is the curve's top, or the cap behind a direct slab.
+    # Its inverse is the same line read the other way, and a need past the
+    # highest kink's draw holds that kink.
+    kinks = sorted({
+        min(t, p.buffer_max_temp) for _, top, zone in circuits for t in (top, zone)
+    })
+    return float(np.interp(need_kw, [_circuit_draw(circuits, k) for k in kinks], kinks))
+
+
 def valve_charge_demand(
     model: "ThermalModel", state: ThermalState, need_kw: float,
     outdoor_temp: float, wind_speed: float, precipitation: float,
@@ -1920,15 +1944,8 @@ def valve_charge_demand(
     circuits = _valve_draw_circuits(
         model, state, outdoor_temp, wind_speed, precipitation)
     tank = state.buffer_tank_temperature
-    # The draw is piecewise linear in the tank temperature, kinked where a
-    # circuit starts drawing (its zone) and where its curve caps it; the
-    # highest kink is the curve's top, or the cap behind a direct slab.
-    # Its inverse is the same line read the other way, and a need past the
-    # highest kink's draw holds that kink.
-    kinks = sorted({
-        min(t, p.buffer_max_temp) for _, top, zone in circuits for t in (top, zone)
-    })
-    goal = float(np.interp(need_kw, [_circuit_draw(circuits, k) for k in kinks], kinks))
+    goal = valve_hold_temperature(
+        model, state, need_kw, outdoor_temp, wind_speed, precipitation)
     loss = p.buffer_tank_heat_loss_coefficient * (tank - TANK_ROOM_AMBIENT_TEMP)
     return (
         _circuit_draw(circuits, tank) + loss
@@ -2349,8 +2366,8 @@ def wood_share(
     lets any real tank cover a whole step, so priority degenerates to
     "wood to the floor" even at 30 °C against a 40 °C curve.
 
-    Module-level and pure so the savings baseline can reuse it verbatim —
-    two copies of this law would drift the first time one is tuned.
+    Module-level and pure: two copies of this law would drift the first time
+    one is tuned.
     """
     if wood_temp >= flow_set:
         return 1.0
diff --git a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
index 8f094f78a..cb38cf349 100644
--- a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
+++ b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
@@ -327,6 +327,8 @@ const STRINGS = {
     "savings.col_savings": "Savings",
     "savings.col_pct": "%",
     "savings.estimated": "estimated",
+    "savings.old_basis": "old basis",
+    "savings.wood_note": "The saving includes heat from wood. Firewood's cost is not counted.",
     "savings.empty": "No settled savings months yet.",
     "receipt.closed": "{month} \u00b7 closed",
     "receipt.saved": "Saved {amount} {unit} ({pct}) against a plain thermostat",
@@ -1165,6 +1167,8 @@ const STRINGS = {
     "savings.col_savings": "Sparande",
     "savings.col_pct": "%",
     "savings.estimated": "uppskattat",
+    "savings.old_basis": "gammalt underlag",
+    "savings.wood_note": "Sparandet inkluderar värme från ved. Vedens kostnad räknas inte.",
     "savings.empty": "Inga avräknade sparandemånader ännu.",
     "receipt.closed": "{month} \u00b7 avslutad",
     "receipt.saved": "Sparade {amount} {unit} ({pct}) mot en vanlig termostat",
@@ -14872,8 +14876,11 @@ class HeatpumpOptimizerCard extends HTMLElement {
       const est = row.estimated
         ? ` <span class="savings-est">${esc(L("savings.estimated"))}</span>`
         : "";
+      const old = row.old_basis
+        ? ` <span class="savings-est savings-old">${esc(L("savings.old_basis"))}</span>`
+        : "";
       return `<tr class="${row.estimated ? "estimated" : ""}">
-        <td>${esc(String(row.month || ""))}${est}</td>
+        <td>${esc(String(row.month || ""))}${est}${old}</td>
         <td class="num">${money(row.baseline_sek)}</td>
         <td class="num">${money(row.actual_sek)}</td>
         <td class="num">${mag(row.savings_sek)}<span class="sv-val">${money(row.savings_sek)}</span></td>
@@ -14884,6 +14891,10 @@ class HeatpumpOptimizerCard extends HTMLElement {
     // the same unit down the whole column, and repeating it is what pushed
     // the decimal points out of line.
     const head = (key) => `${esc(L(key))} (${esc(cur)})`;
+    const fuel = this.plan.woodFuel();
+    const woodNote = fuel && fuel.show_whatif
+      ? `<div class="savings-wood-note" style="margin-top:.6em;font-size:.9em;color:var(--secondary-text-color)">${esc(L("savings.wood_note"))}</div>`
+      : "";
     return `${top}<table class="savings-table">
       <thead><tr>
         <th>${esc(L("savings.col_month"))}</th>
@@ -14893,7 +14904,7 @@ class HeatpumpOptimizerCard extends HTMLElement {
         <th class="num">${esc(L("savings.col_pct"))}</th>
       </tr></thead>
       <tbody>${rows.map(tr).join("")}</tbody>
-    </table>`;
+    </table>${woodNote}`;
   }
 
   // The sensor advisor page's renderer and wiring live at module level
diff --git a/dev/audit/harnesses/r10_sav_wood_reference.py b/dev/audit/harnesses/r10_sav_wood_reference.py
new file mode 100644
index 000000000..42f2c63e1
--- /dev/null
+++ b/dev/audit/harnesses/r10_sav_wood_reference.py
@@ -0,0 +1,245 @@
+#!/usr/bin/env python3
+"""R10-HOTFIX-SAV-ESTIMATE: the valved house's month row, closed loop.
+
+WHY IT EXISTS. The owner's November row read baseline/actual 0.14 because the
+settlement books the thermostat's FIRST step of a plan re-made every interval,
+and behind a valve that step read the stores' transient: a tank above the curve
+zeroed it through ``valve_charge_demand``, a wood side above it through
+``wood_share``, and a tank below it overshot. The reference now has no wood. No bundle data: every figure is
+this synthetic install's.
+
+Asserted arms (rc 1 on DEFECT):
+
+  first   step 0 over the horizon mean at one outdoor, across installs and tank
+          starts, and the null control: a wood house reads the plain valved
+          house's kW exactly. A steady demand makes a sound first step the mean, so any ratio
+          off 1 is transient. Spread across starts is no acceptance: all-zero
+          first steps have spread 0 (#2411's metric read SOUND on this defect).
+  valve   a valved house with no wood tank, plant equal to the model, booked
+          through ``MonthlyLedger.observe_spot_and_settle_savings``: the row at a
+          flat and a varying price, with its gap split into terms. Only the flat
+          row is asserted, inside ``FLAT_BAND_PCT``.
+
+Measured, not asserted: ``wood-*`` drive the same loop on a modelled wood tank.
+The reference has no wood (owner ruling, 2026-11-04) and the actual stays metered,
+so a positive row on these arms is wood's heat, expected, and the card says so:
+firewood's cost is not counted. ``wood-unforeseen`` meters under the plan: with
+wood configured the row's calibration only raises the reference (floor 1.0), and
+the arm prints what the uncalibrated row reads beside it.
+
+    PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py [--quick] [arm ...]
+"""
+from __future__ import annotations
+
+import sys
+from datetime import datetime, timedelta
+
+import numpy as np
+
+from profiles import DT, house, prices, solve_inputs, weather
+from heatpump_optimizer.ledger import MonthlyLedger
+from heatpump_optimizer.optimizer import (
+    HeatPumpOptimizer, OptimizationConfig, _floor_demand_at_target, _reference_cop,
+    _thermostat_held_state,
+)
+from heatpump_optimizer.thermal_model import (
+    ThermalModel, ThermalParameters, ThermalState, WeatherSeries,
+)
+
+START = datetime(2026, 1, 15, 0, 0)
+#: Intervals between solves; the reference is booked per interval regardless.
+REPLAN = 4
+DAYS = 1.0 if "--quick" in sys.argv else 2.0
+VALVE_CFG = {
+    "mixing_valve_mode": "manual", "mixing_valve_target": 21.0, "buffer_tank_volume": 750.0,
+    "buffer_max_temperature": 56.0, "heat_pump_max_power": 4.0,
+}
+WOOD_CFG = {
+    **VALVE_CFG, "wood_furnace_enabled": True, "wood_tank_volume": 750.0,
+    "wood_tank_top_entity": "sensor.wood_top",
+}
+#: Flat row's acceptance, percent: main reads tens of points past it; the terms
+#: printed beside the row say what the remainder is.
+FLAT_BAND_PCT = 10.0
+
+
+def _install(wood: bool, two_zone: bool = True):
+    cfg = dict(WOOD_CFG if wood else VALVE_CFG, two_zone_mode="on" if two_zone else "off")
+    params = ThermalParameters.from_config(house(two_zone=two_zone, dhw=False, **cfg))
+    assert params.two_tank_modelled is wood, "the arm's install is not the one it names"
+    model = ThermalModel(params)
+    return HeatPumpOptimizer(model, OptimizationConfig(
+        horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=17.0, max_temp=23.0,
+    )), model
+
+
+def closed_loop(wood: bool, burn_kw, wood0, buf0: float, price: str = "flat", metered=None, foresee: bool = True):
+    """A solve per ``REPLAN`` on a plant equal to the model; the row and the terms."""
+    opt, model = _install(wood)
+    total, hs = int(DAYS * 24 / DT), int(24 / DT)
+    span = total + hs + 4
+
+    def tile(a):
+        a = np.asarray(a, dtype=float)
+        return np.tile(a, int(np.ceil(span / len(a))))[:span]
+
+    pr = tile(prices(price, START))
+    out, wind, rain, sol = (tile(a) for a in weather("winter_cold", START))
+    ext = np.array([burn_kw(START + timedelta(hours=k * DT)) for k in range(span)], float)
+    state = first = ThermalState(
+        room_temperature=20.5, slab_temperature=22.0, outdoor_temperature=float(out[0]),
+        upper_floor_temperature=20.5, lower_floor_temperature=20.5,
+        buffer_tank_temperature=buf0, wood_tank_temperature=wood0,
+    )
+    led = MonthlyLedger()
+    plan_kwh = ref_kwh = plan_heat = 0.0
+    rooms, states, booked_series, plan = [], [], [], None
+    for k in range(total):
+        now = START + timedelta(hours=k * DT)
+        # The detector's bound: a fire is forecast two hours ahead, never more.
+        forecast = ext[k:k + hs].copy()
+        forecast[int(2.0 / DT):] = 0.0
+        if not foresee:
+            forecast[:] = 0.0
+        series = WeatherSeries(
+            outdoor_temps=out[k:k + hs], wind_speeds=wind[k:k + hs], precipitation=rain[k:k + hs],
+            solar_radiation=sol[k:k + hs], external_heat_kw=forecast,
+        )
+        if k % REPLAN == 0:
+            plan = opt.optimize(inputs=solve_inputs(
+                initial_state=state, prices=pr[k:k + hs], outdoor_temps=out[k:k + hs],
+                wind_speeds=wind[k:k + hs], precipitation=rain[k:k + hs],
+                solar_radiation=sol[k:k + hs], start_time=now, external_heat_kw=forecast,
+            ))
+        power = float(plan.power_schedule[k % REPLAN])
+        # The coordinator re-plans every interval, so it books step 0 of a plan
+        # from THIS state; the solve is hourly for cost, the booked reference is
+        # the production call a fresh solve makes.
+        booked = float(opt._compute_baseline_power(series, state, DT)[0][0])
+        booked_series.append(booked)
+        plan_kwh += power * DT
+        ref_kwh += booked * DT
+        plan_heat += power * DT * model.compute_cop(
+            float(out[k]), flow_temp=state.buffer_tank_temperature
+        )
+        meter = power * DT * (1.0 if metered is None else metered(now))
+        led.observe_spot_and_settle_savings(
+            now, float(pr[k]), {"baseline_kw": booked, "power": power}, meter, DT
+        )
+        led.add(now, "spot", kwh=meter, sek=meter * float(pr[k]))
+        states.append((state, series))
+        state = model.simulate_step(
+            state, power, float(out[k]), float(wind[k]), float(rain[k]), float(sol[k]), DT,
+            external_heat_kw=float(ext[k]),
+        )
+        rooms.append(state.room_temperature)
+    row = led.savings_months(datetime(2026, 2, 1), wood_configured=wood)[0]
+    print(f"  row: baseline {row['baseline_sek']} actual {row['actual_sek']} saved {row['savings_sek']} pct {row['savings_pct']}")
+    # The month row's meter calibration, read off: what it does to the percent.
+    raw = led.line("2026-01", "savings_baseline")["sek"]
+    print(f"  calibration {row['meter_calibration']}; uncalibrated baseline {raw:.2f}, pct {(raw - row['actual_sek']) / raw * 100.0 if raw > 0 else float('nan'):.2f}")
+    # The row's gap in kWh, split. Every term re-reads the same states; none is
+    # fitted. Comfort is R10-SAV-COMFORT's rule: the steady thermostat at the
+    # comfort target less at the room the plan delivered.
+    room = float(np.mean(rooms))
+    comfort = ref_heat = 0.0
+    for (s, series), booked_kw, delivered in zip(states, booked_series, rooms):
+        held = _thermostat_held_state(model, s, series, 21.0)
+        o, w, r, g = (float(a[0]) for a in (
+            series.outdoor_temps, series.wind_speeds, series.precipitation, series.solar_radiation))
+        cop_ref = _reference_cop(model, held, o, None)
+        ref_heat += booked_kw * DT * cop_ref
+        comfort += (
+            _floor_demand_at_target(model, 21.0, o, w, r, g)
+            - _floor_demand_at_target(model, delivered, o, w, r, g)
+        ) / cop_ref * DT
+    cop = plan_heat / plan_kwh if plan_kwh > 0 else 0.0
+    cop_ref_mean = ref_heat / ref_kwh if ref_kwh > 0 else 0.0
+    stored = (opt._stored_thermal_energy(state) - opt._stored_thermal_energy(first)) / max(cop, 1e-9)
+    settled = ref_kwh - comfort + stored
+    residual = (settled - plan_kwh) / settled * 100.0 if settled > 0 else float("nan")
+    print(f"  plan kWh {plan_kwh:.2f} at COP {cop:.3f}; booked reference {ref_kwh:.2f} at COP {cop_ref_mean:.3f}; gap {ref_kwh - plan_kwh:+.2f}; mean room {room:.2f} C against 21.00")
+    print(f"  comfort term {comfort:+.2f} kWh_e (the reference's warmer house); stored term {stored:+.2f} kWh_e (the plan's store change)")
+    print(f"  residual: reference less comfort, plus stored, {settled:.2f} kWh against plan {plan_kwh:.2f}: {residual:+.2f} %")
+    return row, residual
+
+
+INSTALLS = {
+    "wood-valve": (True, True), "valve-only 2z": (True, False), "valve-only 1z": (False, False),
+}
+
+
+def first_step() -> bool:
+    ok = True
+    plain = None
+    for name, (two_zone, wood) in reversed(list(INSTALLS.items())):
+        opt, _ = _install(wood, two_zone)
+        out, zero = np.full(96, -5.0), np.zeros(96)
+        series = WeatherSeries(outdoor_temps=out, wind_speeds=zero, precipitation=zero, solar_radiation=zero)
+        for buf in (20.0, 27.3, 40.0):
+            for w0 in ((5.0, 28.0) if wood else (None,)):
+                state = ThermalState(
+                    room_temperature=20.0, slab_temperature=22.0, outdoor_temperature=-5.0,
+                    upper_floor_temperature=20.0, lower_floor_temperature=20.0,
+                    buffer_tank_temperature=buf, wood_tank_temperature=w0,
+                )
+                ref = opt._compute_baseline_power(series, state, DT)[0]
+                ratio = float(ref[0]) / max(float(np.mean(ref)), 1e-9)
+                bad = abs(ratio - 1.0) > 0.01
+                if name == "valve-only 2z":
+                    plain = ref
+                if wood:
+                    gap = float(np.abs(ref - plain).max())
+                    bad = bad or gap > 1e-9
+                    print(f"    null: gap to the plain valved house {gap:.2e} kW")
+                ok = ok and not bad
+                print(f"  {name:14s} buf {buf:5.1f} wood {w0}: step0 {ref[0]:.3f} mean {np.mean(ref):.3f} step0/mean {ratio:.3f} zero {int((ref < 1e-6).sum())}{' BAD' if bad else ''}")
+    return ok
+
+
+def valve_arm(price: str) -> bool:
+    row, residual = closed_loop(False, lambda t: 0.0, None, 30.0, price)
+    print(f"  {price}: pct {row['savings_pct']}, residual {residual:+.2f} % (rule: flat |pct| < {FLAT_BAND_PCT}; vary pct above flat by the timing saving, printed)")
+    return price != "flat" or abs(row["savings_pct"]) < FLAT_BAND_PCT
+
+
+ARMS = {
+    "first": first_step,
+    "valve-flat": lambda: valve_arm("flat"),
+    "valve-vary": lambda: valve_arm("winter_typical"),
+}
+OWED = {
+    # A fire the plan did not foresee: the pump draws half the plan while it
+    # burns and the tank coasts after. The meter's fall is wood's; the row's
+    # meter calibration scales the reference down by it (triage P387).
+    "wood-unforeseen": lambda: closed_loop(
+        True, lambda t: 12.0 if 17 <= t.hour < 21 else 0.0, 40.0, 30.0, foresee=False,
+        metered=lambda t: 0.5 if 17 <= t.hour < 24 else 1.0,
+    ),
+    "wood-cold": lambda: closed_loop(True, lambda t: 0.0, 15.0, 30.0),
+    "wood-full": lambda: closed_loop(True, lambda t: 6.0, 60.0, 30.0),
+    "wood-fire": lambda: closed_loop(True, lambda t: 12.0 if 17 <= t.hour < 21 else 0.0, 40.0, 30.0),
+    "wood-stale": lambda: closed_loop(True, lambda t: 0.0, 28.0, 27.3),
+    "wood-coast": lambda: closed_loop(True, lambda t: 0.0, 75.0, 30.0),
+}
+
+
+def main(argv: list[str]) -> int:
+    names = [a for a in argv if a != "--quick"] or list(ARMS)
+    failed = []
+    for name in names:
+        print(name)
+        if name in OWED:
+            OWED[name]()
+            print(f"{name}: measured, not asserted (the saving includes wood's heat; firewood not counted)")
+            continue
+        ok = ARMS[name]()
+        print(f"{name}: {'SOUND' if ok else 'DEFECT'}")
+        if not ok:
+            failed.append(name)
+    print(f"arms run {len(names)}, defect {len(failed)}: {' '.join(failed) or '-'}")
+    return 1 if failed else 0
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/dev/programme/delivery/3220.md b/dev/programme/delivery/3220.md
new file mode 100644
index 000000000..97947567d
--- /dev/null
+++ b/dev/programme/delivery/3220.md
@@ -0,0 +1 @@
+- [#3220](https://github.com/tvofi/heatpump_optimizer/pull/3220) — **open**, R10-HOTFIX-SAV-ESTIMATE: the savings month row settles against the meter (R10-HOTFIX-SAV-ESTIMATE)
diff --git a/docs/automations.md b/docs/automations.md
index 3d44b59cb..7ed7f4ea5 100644
--- a/docs/automations.md
+++ b/docs/automations.md
@@ -143,7 +143,7 @@ temperature and back on successive refreshes, which fires at each crossing.
 
 | Event | Fires when | Data |
 |---|---|---|
-| `heatpump_optimizer_monthly_receipt` | a month has closed and its receipt is published | `entry_id`, `month` (`YYYY-MM`), `total_sek`, `saving_sek` and `saving_pct` (against a plain thermostat, `null` when the month has no savings row), `currency` |
+| `heatpump_optimizer_monthly_receipt` | a month has closed and its receipt is published | `entry_id`, `month` (`YYYY-MM`), `total_sek`, `saving_sek` and `saving_pct` (against a plain thermostat with no wood, `null` when the month has no savings row or was booked on an older reference), `currency`, `saving_old_basis` (`true` for that older reference), `saving_includes_wood` (`true` where wood is configured: the saving includes its heat, and firewood's cost is not counted) |
 | `heatpump_optimizer_comfort_at_risk` | the coldest step of the plan is below your minimum temperature | `entry_id`, `predicted_min_c`, `at` (the step's time), `floor_c`, `peak_guard_suppressing` (the peak guard is holding heating back), `cause` (the coldest step's published reason, for example `idle_fuse`, or null when the plan has none) |
 | `heatpump_optimizer_input_stale` | a required input has not updated within its limit; once per input | `entry_id`, `input`, `age_minutes`, `max_age_minutes` |
 | `heatpump_optimizer_plan_stale` | the plan is older than three solve cycles (at least 90 minutes) | `entry_id`, `age_minutes` |
diff --git a/docs/how-it-works.md b/docs/how-it-works.md
index f90744ae2..fb55a7234 100644
--- a/docs/how-it-works.md
+++ b/docs/how-it-works.md
@@ -882,8 +882,10 @@ point of the split is that a fire cannot make the heat pump's modelled
 efficiency look worse — a single-tank model would charge the modelled COP
 for water the pump never made — and cannot eat the buffer's
 safe-temperature headroom, so the plan keeps charging cheap hours right through
-a burn. Heat still in the wood tank at day's end counts in the savings
-settlement and the thermal-battery view, up to 95 °C. Without the probe, or
+a burn. Heat still in the wood tank at day's end counts in the thermal-battery
+view, up to 95 °C. The savings reference has no wood at all, so wood's heat
+counts in the saving and firewood's cost is not counted; the savings page says
+so where wood is configured. Without the probe, or
 while it is stale, the wood tank is not a store of its own: the model keeps the
 one buffer tank, and a burn is the bounded free heat described above.
 
diff --git a/tests/card.mjs b/tests/card.mjs
index bd09965b7..5f6051323 100644
--- a/tests/card.mjs
+++ b/tests/card.mjs
@@ -10226,6 +10226,18 @@ const STOCK_THEMES = {
     };
   };
 
+  // R10-HOTFIX-SAV-ESTIMATE: an old-basis month states no saving, and says why.
+  {
+    const held = tableOf([
+      { month: "2026-09", baseline_sek: 1779.92, actual_sek: 344.81, savings_sek: null, savings_pct: null, old_basis: true },
+    ], "old-basis-savings");
+    const text = held.cells.map((c) => c.text);
+    check("an old-basis month draws both columns, a dash for saving and percent, and the note",
+      text[1] === "1779.92" && text[2] === "344.81" && text[3] === "—" && text[4] === "—"
+        && text[0].includes("old basis"),
+      JSON.stringify(text));
+  }
+
   const { dump, table, cells, heads } = tableOf(months, "c3-savings");
   // "Numeric" by position, not by a regex over the rendered text: the month
   // column reads as digits too ("2025-11") and must NOT be right-aligned.
diff --git a/tests/card_browser.mjs b/tests/card_browser.mjs
index 50c6ef82b..938416388 100644
--- a/tests/card_browser.mjs
+++ b/tests/card_browser.mjs
@@ -235,6 +235,10 @@ function gridStates(plan) {
         { month: "2026-01", baseline_sek: 900, actual_sek: 820, savings_sek: 80, savings_pct: 8.9, estimated: true },
         { month: "2025-12", baseline_sek: 700, actual_sek: 712, savings_sek: -12, savings_pct: -1.7 }] } } },
       steps: [["cardClick"], ["page", "savings"]] }),
+    S("savings_page_wood", { states: { ...wood({ cheaper: false, show_whatif: true, ready: true, slots: [] }),
+      "sensor.heat_pump_optimizer_plan_monthly_savings": { state: "8.1", attributes: { unit_of_measurement: "SEK", savings_months: [
+        { month: "2025-12", baseline_sek: 700, actual_sek: 712, savings_sek: null, savings_pct: null, old_basis: true }] } } },
+      steps: [["cardClick"], ["page", "savings"]] }),
     S("estimated_price_hover", { states: (() => { const st = planStates(plan);
       for (const id of [DEFAULT_SPACE, DEFAULT_DHW]) st[id].attributes.forecast = st[id].attributes.forecast.map((p) => ({ ...p, price_known: false }));
       return st; })(), steps: [["cardClick"], ["hover", 3]] }),
@@ -2000,6 +2004,56 @@ try {
     `${Math.min(...clipCells.map((c) => c.runs))} text run(s) in the thinnest cell, ` +
     `${Math.min(...clipCells.filter((c) => c.pg === "savings").map((c) => c.tableRuns))} ` +
     `in the thinnest savings table`);
+  // R10-HOTFIX-SAV-ESTIMATE: an old-basis month draws its two columns, a dash
+  // for the saving and the percent, and the note; a house with wood configured
+  // carries the disclaimer, painted, and a house without it does not.
+  const savingsRows = (woodConfigured) => clipPage.evaluate(async ([st]) => {
+    document.body.innerHTML = "";
+    const card = document.createElement("heatpump-optimizer-card");
+    card.setConfig({ type: "custom:heatpump-optimizer-card" });
+    card.hass = { states: st, language: "en" };
+    document.body.style.width = "320px";
+    document.body.appendChild(card);
+    card._onCardClick({});
+    card.dialog.page = "savings";
+    card._render();
+    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
+    const note = card.shadowRoot.querySelector(".savings-wood-note");
+    return {
+      note: note && note.getClientRects().length > 0 ? note.textContent.trim() : "",
+      noteRight: note ? note.getBoundingClientRect().right : 0,
+      rows: [...card.shadowRoot.querySelectorAll(".savings-table tbody tr")].map((tr) => ({
+        cells: [...tr.querySelectorAll("td")].map((td) => td.textContent.trim().replace(/\s+/g, " ")),
+        old: !!tr.querySelector(".savings-old"),
+        barWidth: tr.querySelector(".sv-mag")?.getBoundingClientRect().width ?? -1,
+      })),
+    };
+  }, [(() => {
+    const st = { ...clipStates, "sensor.heat_pump_optimizer_monthly_savings": {
+      state: "0", attributes: { unit_of_measurement: "SEK", savings_months: [
+        { month: "2026-09", baseline_sek: 1779.92, actual_sek: 344.81, savings_sek: null, savings_pct: null, old_basis: true, estimated: false },
+        { month: "2026-12", baseline_sek: 900, actual_sek: 1500, savings_sek: -600, savings_pct: -66.7, old_basis: false, estimated: false },
+      ] } } };
+    st[DEFAULT_SPACE] = { ...st[DEFAULT_SPACE], attributes: { ...st[DEFAULT_SPACE].attributes,
+      wood_fuel: woodConfigured ? { ready: true, cheaper: false, show_whatif: true } : { ready: false, cheaper: false, show_whatif: false } } };
+    return st;
+  })()]);
+  await clipPage.setViewportSize({ width: 320, height: 640 });
+  const woodPage = await savingsRows(true);
+  const plainPage = await savingsRows(false);
+  const [oldRow, statedRow] = woodPage.rows;
+  check("an old-basis row draws its two columns, a dash for saving and percent, and the note",
+    /old basis/.test(oldRow?.cells[0]) && oldRow.cells[1] === "1779.92" && oldRow.cells[2] === "344.81"
+      && oldRow.cells[3] === "—" && oldRow.cells[4] === "—" && oldRow.old && oldRow.barWidth === 0,
+    JSON.stringify(oldRow));
+  check("and a new-basis row beside it states its saving, its unclipped percent and its bar",
+    statedRow?.cells[3].includes("-600.00") && statedRow.cells[4] === "-67%" && !statedRow.old && statedRow.barWidth > 0,
+    JSON.stringify(statedRow));
+  check("a house with wood configured carries the disclaimer, painted within a phone's width",
+    /includes heat from wood/.test(woodPage.note) && /not counted/.test(woodPage.note) && woodPage.noteRight <= 320.5,
+    JSON.stringify([woodPage.note, woodPage.noteRight]));
+  check("a house with no wood configured carries none",
+    plainPage.note === "" && plainPage.rows.length === 2, JSON.stringify(plainPage.note));
   await clipPage.close();
 
   // #258: axis unit labels must not ink-collide with their top tick once the
diff --git a/tests/closures.json b/tests/closures.json
index 7e882192e..65a09b69e 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4042,6 +4042,7 @@
    "dev/audit/harnesses/r10_sav_baseline_mutants.py",
    "dev/audit/harnesses/r10_sav_null_terms.py",
    "dev/audit/harnesses/r10_sav_volume.py",
+   "dev/audit/harnesses/r10_sav_wood_reference.py",
    "dev/audit/harnesses/r10_savings_upgrade_month.py",
    "dev/audit/harnesses/r10_scores_envelope.py",
    "dev/audit/harnesses/r10_seat_selftests_mutants.py",
diff --git a/tests/features.py b/tests/features.py
index 27a67b98a..d4fc603c3 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -13762,7 +13762,7 @@ _fr_found = set()
 for _fr_p in sorted(_FrPath("custom_components/heatpump_optimizer").glob("*.py")):
     for _fr_n in _fr_ast.walk(_fr_ast.parse(_fr_p.read_text())):
         if (isinstance(_fr_n, _fr_ast.Call) and isinstance(_fr_n.func, _fr_ast.Name)
-                and _fr_n.func.id == "QuarantiningStore"):
+                and _fr_n.func.id in ("QuarantiningStore", "LedgerStore")):
             for _fr_arg in _fr_n.args:
                 if isinstance(_fr_arg, _fr_ast.JoinedStr):
                     _fr_found.add(_fr_arg.values[-1].value.lstrip("_"))
@@ -14533,12 +14533,8 @@ R.check(
 )
 
 
-# The savings reference backs its electric demand off by the same wood share,
-# and only where the layout models the wood tank: a single-tank state that
-# carries a wood reading is the thermostat it would be without one. The HP
-# tank starts at 25 C, below the curve: behind a valve the reference coasts
-# on a tank above the curve before it buys anything (R10-BUFFER-STORE), so
-# the 45 C tank of the states above would leave both arms at zero.
+# The savings reference has no wood (owner ruling, 2026-11-04): a wood reading
+# moves it on no layout, hot or cold, and the actual keeps wood's heat.
 def _w2t_reference(params, wood, n=16):
     _z = np.zeros(n)
     return _PvOpt(_PvModel(params), _PvOptCfg(target_temp=21.0))._compute_baseline_power(
@@ -14550,9 +14546,8 @@ _w2t_ref_cold = _w2t_reference(_w2t_params_two, 20.0)
 _w2t_ref_off = _w2t_reference(_w2t_params_off, 80.0)
 _w2t_ref_off_none = _w2t_reference(_w2t_params_off, None)
 R.check(
-    "the savings reference backs off by the wood share on the two-tank layout, "
-    "and a wood reading on any other layout moves it not at all",
-    float(np.sum(_w2t_ref_hot)) < float(np.sum(_w2t_ref_cold)) - 1.0
+    "the savings reference has no wood: a wood reading moves it on no layout",
+    np.array_equal(_w2t_ref_hot, _w2t_ref_cold)
     and np.array_equal(_w2t_ref_off, _w2t_ref_off_none),
     f"two-tank hot {np.sum(_w2t_ref_hot):.2f} vs cold {np.sum(_w2t_ref_cold):.2f} kW-steps; "
     f"single-tank with a reading {np.sum(_w2t_ref_off):.2f} vs without "
@@ -34736,14 +34731,12 @@ _de_coil_none, _, _, _ = _dhw_planner(_de_coil_opt)._baseline_dhw_economics(
     _de_price, _de_bp, _de_sp, _de_dh,
 )
 R.check(
-    "the refill coil cheapens the always-hot baseline only when wood is known",
-    # 0.1002 / 0.2059 before R8-P3 (#1530): this valve config prices the tank
-    # at the buffer's Carnot lift now, a lower COP, so both figures rise.
-    abs(_de_coil_70[0] - 0.11854480778140909) < 1e-12
+    "the reference's hot water has no refill coil: a known wood tank moves nothing "
+    "(owner ruling, 2026-11-04)",
+    _de_coil_70[0] == _de_coil_none[0]
     and abs(_de_coil_none[0] - 0.24359207337361277) < 1e-12,
-    f"coil+70 {_de_coil_70[0]} coil+None {_de_coil_none[0]} — equal values "
-    f"mean the coil reduction was dropped; a 70 C tank that still prices "
-    f"the full electric draw invents savings",
+    f"coil+70 {_de_coil_70[0]} coil+None {_de_coil_none[0]} — a lower coil+70 means "
+    f"the reference owns the coil again, and the coil's heat leaves the saving",
 )
 
 _de_coil_arg, _, _, _ = _dhw_planner(_de_coil_opt)._baseline_dhw_economics(
@@ -34751,11 +34744,9 @@ _de_coil_arg, _, _, _ = _dhw_planner(_de_coil_opt)._baseline_dhw_economics(
     _de_out, 3, 40.0, _de_price, _de_bp, _de_sp, _de_dh,
 )
 R.check(
-    "standby uses the passed setpoint; the coil still uses the configured one",
-    abs(_de_coil_arg[0] - 0.07429802182888166) < 1e-12,  # 0.0699 before R8-P3
-    f"{_de_coil_arg[0]} — 0.119 means standby ignored the 40 C argument; "
-    f"a different third figure means the coil used the argument instead of "
-    f"params.dhw_setpoint, which is the inlet identity the draw was built on",
+    "standby uses the passed setpoint",
+    abs(_de_coil_arg[0] - 0.17257582848084152) < 1e-12,
+    f"{_de_coil_arg[0]} — 0.2436 means standby ignored the 40 C argument",
 )
 
 
@@ -42365,10 +42356,11 @@ R.check(
     repr(_sav_factor(_jan31)),
 )
 R.check(
-    "pct is baseline-relative and clipped",
+    "pct is baseline-relative and unclipped: the row's percent is its own two amounts' ratio",
     abs(_sav_pct(100.0, 60.0) - 60.0) < 1e-12
-    and abs(_sav_pct(100.0, 200.0) - 100.0) < 1e-12
-    and abs(_sav_pct(100.0, -200.0) - (-100.0)) < 1e-12,
+    and abs(_sav_pct(100.0, 200.0) - 200.0) < 1e-12
+    and abs(_sav_pct(151.85, -909.91) - (-909.91 / 151.85 * 100.0)) < 1e-9,
+    repr(_sav_pct(151.85, -909.91)),
 )
 R.check(
     "pct is omitted when baseline_sek <= 0.01, not published as 0.0",
@@ -42566,6 +42558,268 @@ R.check(
     and abs(_neg_row["savings_pct"] + 100.0 / 3.0) < 1e-9,
     repr(_neg_row),
 )
+# R10-HOTFIX-SAV-ESTIMATE: a month's reference basis. Totals cannot be rebooked,
+# so a month booked against a retired reference keeps its columns and states no
+# saving; a fresh month is stamped at its first booking.
+import asyncio as _sb_asyncio
+import copy as _sb_copy
+
+from heatpump_optimizer.const import LEDGER_STORE_VERSION as _SB_VERSION
+from heatpump_optimizer.ledger import (
+    OLD_REFERENCE_BASIS as _SB_OLD,
+    REFERENCE_BASIS as _SB_NOW,
+    REFERENCE_BASIS_META as _SB_META,
+)
+from heatpump_optimizer.store import LedgerStore as _SbStore
+from homeassistant.helpers import storage as _sb_storage
+
+_sb_led = _SavLedger()
+_sb_t = _SavDT(2026, 2, 9, 3, 0)
+_sb_led.observe_spot_and_settle_savings(_sb_t, 1.0, {"baseline_kw": 2.0, "power": 2.0}, 1.0, 1.0)
+_sb_led.observe_spot_and_settle_savings(_sb_t, 1.0, {"baseline_kw": 2.0, "power": 2.0}, 1.0, 1.0)
+_sb_row = _sb_led.savings_months(_SavDT(2026, 3, 2, 0, 0))[0]
+_sb_meta = _sb_led.months["2026-02"]["meta"][_SB_META]
+R.check(
+    "a month's first savings booking stamps the reference in force, once",
+    _sb_meta == {"sum": float(_SB_NOW), "count": 1} and _sb_row["old_basis"] is False
+    and _sb_row["savings_sek"] is not None and _sb_row["savings_pct"] is not None,
+    repr((_sb_meta, _sb_row)),
+)
+_sb_v1 = {"ledger": _sb_copy.deepcopy(_sb_led.as_dict()), "starts": {"kept": 1}}
+del _sb_v1["ledger"]["months"]["2026-02"]["meta"][_SB_META]
+_sb_lines = _sb_copy.deepcopy(_sb_v1["ledger"]["months"]["2026-02"]["lines"])
+_sb_run = _sb_asyncio.run
+_sb_run(_sb_storage.Store(None, 1, "sb_ledger").async_save(_sb_v1))
+_sb_loaded = _sb_run(_SbStore(None, _SB_VERSION, "sb_ledger").async_load())
+_sb_run(_SbStore(None, _SB_VERSION, "sb_ledger").async_remove())
+_sb_old = _SavLedger.from_dict(_sb_loaded["ledger"])
+_sb_old_row = _sb_old.savings_months(_SavDT(2026, 3, 2, 0, 0))[0]
+R.check(
+    "a v1 ledger migrates to v2: every month on the old basis, every line as stored",
+    _SB_VERSION == 2 and _sb_loaded["starts"] == {"kept": 1}
+    and _sb_loaded["ledger"]["months"]["2026-02"]["lines"] == _sb_lines
+    and _sb_loaded["ledger"]["months"]["2026-02"]["meta"][_SB_META]
+    == {"sum": float(_SB_OLD), "count": 1},
+    repr(_sb_loaded),
+)
+R.check(
+    "an old-basis row keeps both columns and states no saving and no percent",
+    _sb_old_row["old_basis"] is True and _sb_old_row["savings_sek"] is None
+    and _sb_old_row["savings_pct"] is None
+    and _sb_old_row["baseline_sek"] == _sb_row["baseline_sek"]
+    and _sb_old_row["actual_sek"] == _sb_row["actual_sek"],
+    repr(_sb_old_row),
+)
+_sb_old.observe_spot_and_settle_savings(_SavDT(2026, 2, 9, 5, 0), 1.0, {"baseline_kw": 2.0, "power": 2.0}, 1.0, 1.0)
+R.check(
+    "an old-basis month stays old when it books on: its total is mixed",
+    _sb_old.savings_months(_SavDT(2026, 3, 2, 0, 0))[0]["old_basis"] is True
+    and _sb_old.months["2026-02"]["meta"][_SB_META]["sum"] == float(_SB_OLD),
+    repr(_sb_old.months["2026-02"]["meta"]),
+)
+_sb_bare = _SavLedger()
+_sb_bare.add(_sb_t, "savings_baseline", kwh=1.0, sek=1.0)
+R.check(
+    "a month with savings lines and no stamp reads as the old basis",
+    _sb_bare.savings_months(_SavDT(2026, 3, 2, 0, 0))[0]["old_basis"] is True,
+    repr(_sb_bare.months),
+)
+# R10-HOTFIX-SAV-ESTIMATE: the settlement books step 0 of a plan re-made every
+# interval, so behind a valve the first step must not be the stores' transient.
+# At one outdoor the steady demand is flat, so a sound step 0 IS the horizon mean;
+# spread across starts is no acceptance (all-zero first steps have spread 0).
+def _sb_first_steps(two_zone, wood_probe, valve="manual"):
+    import numpy as _np
+    from profiles import house as _h
+    from heatpump_optimizer.optimizer import HeatPumpOptimizer as _O, OptimizationConfig as _C
+    from heatpump_optimizer.thermal_model import (
+        ThermalModel as _M, ThermalParameters as _P, ThermalState as _S, WeatherSeries as _W,
+    )
+    cfg = {"mixing_valve_mode": valve, "mixing_valve_target": 21.0, "buffer_tank_volume": 750.0,
+           "heat_pump_max_power": 4.0, "buffer_max_temperature": 56.0,
+           "two_zone_mode": "on" if two_zone else "off"}
+    if wood_probe:
+        cfg.update(wood_furnace_enabled=True, wood_tank_volume=750.0, wood_tank_top_entity="sensor.w")
+    model = _M(_P.from_config(_h(two_zone=two_zone, dhw=False, **cfg)))
+    opt = _O(model, _C(horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=17.0, max_temp=23.0))
+    out, zero = _np.full(96, -5.0), _np.zeros(96)
+    weather = _W(outdoor_temps=out, wind_speeds=zero, precipitation=zero, solar_radiation=zero)
+    return {
+        (buf, wood): opt._compute_baseline_power(weather, _S(
+            room_temperature=20.0, slab_temperature=22.0, outdoor_temperature=-5.0,
+            upper_floor_temperature=20.0, lower_floor_temperature=20.0,
+            buffer_tank_temperature=buf, wood_tank_temperature=wood,
+        ), 0.25)[0]
+        for buf in (20.0, 27.3, 40.0) for wood in ((5.0, 28.0) if wood_probe else (None,))
+    }
+
+
+for _sb_name, _sb_args in (
+    ("a wood tank, cold or warm", (True, True)),
+    ("two zones and no wood tank", (True, False)),
+    ("one zone and no wood tank", (False, False)),
+):
+    _sb_arms = _sb_first_steps(*_sb_args)
+    _sb_ratios = {k: float(v[0] / v.mean()) if v.mean() > 0 else 0.0 for k, v in _sb_arms.items()}
+    R.check(
+        f"behind a valve with {_sb_name}, the thermostat's first step is its horizon mean, not 0 or an overshoot",
+        all(abs(r - 1.0) < 1e-9 for r in _sb_ratios.values()),
+        repr(_sb_ratios),
+    )
+    R.check(
+        f"behind a valve with {_sb_name}, a positive reference with no zero step",
+        all(v.min() > 0.0 for v in _sb_arms.values()),
+        repr({k: float(v.min()) for k, v in _sb_arms.items()}),
+    )
+    R.check(
+        f"behind a valve with {_sb_name}, the thermostat's horizon does not inherit the measured buffer",
+        max(abs(_sb_arms[(20.0, k[1])].mean() - v.mean()) for k, v in _sb_arms.items()) < 1e-9,
+        repr({k: float(v.mean()) for k, v in _sb_arms.items()}),
+    )
+# The owner's no-wood ruling against the 10-24 calibration: a meter under the
+# plan on a wood house is heat wood delivered, so it must count (triage P387).
+def _sb_meter_row(meter_over_plan, wood):
+    led = _SavLedger()
+    for hour in range(24):
+        led.observe_spot_and_settle_savings(
+            _SavDT(2026, 2, 9, hour, 0), 1.0, {"baseline_kw": 2.0, "power": 1.0}, meter_over_plan, 1.0
+        )
+    return led.savings_months(_SavDT(2026, 3, 2, 0, 0), wood_configured=wood)[0]
+
+
+_sb_wood_pct = {f: _sb_meter_row(f, True)["savings_pct"] for f in (1.0, 0.5, 0.25)}
+_sb_plain_pct = {f: _sb_meter_row(f, False)["savings_pct"] for f in (1.0, 0.5, 0.25)}
+R.check(
+    "with wood configured a meter under the plan earns its saving: the calibration does not cancel it",
+    _sb_wood_pct == {1.0: 50.0, 0.5: 75.0, 0.25: 87.5},
+    repr(_sb_wood_pct),
+)
+R.check(
+    "with no wood the calibration stands as specified: the meter cancels at every ratio",
+    _sb_plain_pct == {1.0: 50.0, 0.5: 50.0, 0.25: 50.0},
+    repr(_sb_plain_pct),
+)
+_sb_up = _sb_meter_row(1.5, True)
+R.check(
+    "with wood configured a model that under-reads the meter is still corrected, and the row publishes what it applied",
+    _sb_up["meter_calibration"] == 1.5 and _sb_up["baseline_sek"] == 72.0
+    and _sb_meter_row(0.5, True)["meter_calibration"] == 1.0,
+    repr(_sb_up),
+)
+from heatpump_optimizer.notifier import _monthly_receipt as _sb_receipt
+
+
+def _sb_event(row, wood_on):
+    data = {"insight": {"monthly_report": {"month": "2026-09", "total_sek": 1.0}},
+            "savings_months": [row], "wood_fuel": {"show_whatif": wood_on}, "currency": "SEK"}
+    return _sb_receipt(data)["receipt"].data
+
+
+_sb_ev_old = _sb_event({"month": "2026-09", "savings_sek": None, "savings_pct": None, "old_basis": True}, True)
+_sb_ev_new = _sb_event({"month": "2026-09", "savings_sek": -600.0, "savings_pct": -300.0, "old_basis": False}, False)
+R.check(
+    "the receipt event carries what the card states: no saving on the old basis, the percent unclipped, wood stated",
+    _sb_ev_old["saving_sek"] is None and _sb_ev_old["saving_pct"] is None
+    and _sb_ev_old["saving_old_basis"] is True and _sb_ev_old["saving_includes_wood"] is True
+    and _sb_ev_new["saving_pct"] == -300.0 and _sb_ev_new["saving_old_basis"] is False
+    and _sb_ev_new["saving_includes_wood"] is False,
+    repr((_sb_ev_old, _sb_ev_new)),
+)
+_sb_plain = _sb_first_steps(True, False)[(20.0, None)]
+_sb_wood = _sb_first_steps(True, True)
+_sb_gap = max(abs(v - _sb_plain).max() for v in _sb_wood.values())
+R.check(
+    "the reference has no wood: a wood tank, cold or warm, reads the plain valved house's kW",
+    _sb_gap < 1e-9,
+    repr(_sb_gap),
+)
+# A thermostat that wants no heat buys none. Its demand goes negative on a warm
+# house, and with no floor the reference sells heat back to itself: a plain
+# house's summer plan read 56.99 % against the 5.88 % of a floored one.
+def _sb_warm_reference():
+    import numpy as _np
+    from profiles import house as _h
+    from heatpump_optimizer.optimizer import HeatPumpOptimizer as _O, OptimizationConfig as _C
+    from heatpump_optimizer.thermal_model import (
+        ThermalModel as _M, ThermalParameters as _P, ThermalState as _S, WeatherSeries as _W,
+    )
+    opt = _O(_M(_P.from_config(_h(dhw=False))), _C(
+        horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=17.0, max_temp=23.0))
+    zero = _np.zeros(96)
+    return opt._compute_baseline_power(
+        _W(outdoor_temps=_np.full(96, 22.0), wind_speeds=zero, precipitation=zero,
+           solar_radiation=_np.full(96, 300.0)),
+        _S(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=22.0,
+           upper_floor_temperature=21.0, lower_floor_temperature=21.0), 0.25)
+
+
+_sb_warm_power, _sb_warm_end = _sb_warm_reference()
+R.check(
+    "a thermostat on a warm plain house buys no heat and sells none: not one reference step is negative",
+    float(_sb_warm_power.min()) == 0.0 and float(_sb_warm_power.max()) == 0.0
+    and _sb_warm_end.room_temperature > 21.0,
+    repr((float(_sb_warm_power.min()), float(_sb_warm_power.max()), _sb_warm_end.room_temperature)),
+)
+# The solve's starts anchor on what the plan's house buys, and that house has its
+# wood: a tank that covers the reference's kWh seeds nothing, a house with none
+# seeds them all, and the reference itself is not scaled.
+def _sb_seed_share():
+    from profiles import house as _h
+    from heatpump_optimizer.optimizer import _wood_covered_share as _share
+    from heatpump_optimizer.thermal_model import (
+        ThermalModel as _M, ThermalParameters as _P, ThermalState as _S,
+    )
+    valve = dict(mixing_valve_mode="manual", buffer_tank_volume=750.0, two_zone_mode="on")
+    wood = _M(_P.from_config(_h(two_zone=True, dhw=False, wood_furnace_enabled=True, wood_tank_volume=500.0,
+                                wood_tank_top_entity="sensor.w", **valve)))
+    plain = _M(_P.from_config(_h(two_zone=True, dhw=False, **valve)))
+    full_kwh = wood.params.wood_tank_thermal_mass * 34.0 / wood.params.cop_nominal_floored
+    hot = _S(wood_tank_temperature=55.0)
+    return (_share(wood, hot, full_kwh / 2.0, 21.0), _share(wood, hot, full_kwh * 2.0, 21.0),
+            _share(wood, _S(wood_tank_temperature=15.0), full_kwh, 21.0),
+            _share(wood, _S(wood_tank_temperature=None), full_kwh, 21.0),
+            _share(plain, hot, full_kwh, 21.0), _share(wood, hot, 0.0, 21.0))
+
+
+_sb_seed = _sb_seed_share()
+R.check(
+    "a wood tank's usable heat, at the pump's COP, is the share of the solve's starts it covers: all, half, "
+    "none when cold, none unread, none with no wood tank, none of nothing",
+    _sb_seed[0] == 1.0 and abs(_sb_seed[1] - 0.5) < 1e-12 and _sb_seed[2:] == (0.0, 0.0, 0.0, 0.0),
+    repr(_sb_seed),
+)
+# The reference's wood tank is its 0 C stand-in, so a start gap against it reads
+# wood's measured heat as the plan's borrowed heat and debits it: the wood side
+# is shared at the start, as at the end. The buffer's gap is the null control:
+# it is a store the settlement does value, so it must still move the figure.
+def _sb_start_gap(wood, buffer):
+    import numpy as _np
+    from profiles import house as _h
+    from heatpump_optimizer.optimizer import HeatPumpOptimizer as _O, OptimizationConfig as _C
+    from heatpump_optimizer.thermal_model import (
+        ThermalModel as _M, ThermalParameters as _P, ThermalState as _S, WeatherSeries as _W,
+    )
+    opt = _O(_M(_P.from_config(_h(
+        two_zone=True, dhw=False, mixing_valve_mode="manual", mixing_valve_target=21.0,
+        buffer_tank_volume=750.0, buffer_max_temperature=56.0, wood_furnace_enabled=True,
+        wood_tank_volume=750.0, wood_tank_top_entity="sensor.w",
+    ))), _C(horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=17.0, max_temp=23.0))
+    out, zero, price = _np.full(96, -5.0), _np.zeros(96), _np.full(96, 1.0)
+    return opt._start_gap_cost(
+        _S(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=-5.0,
+           upper_floor_temperature=21.0, lower_floor_temperature=21.0,
+           buffer_tank_temperature=buffer, wood_tank_temperature=wood),
+        _W(outdoor_temps=out, wind_speeds=zero, precipitation=zero, solar_radiation=zero),
+        None, price, out, opt._settlement_caps(out), None, 500.0, 0.0,
+    )
+
+
+_sb_gap_hot, _sb_gap_cold, _sb_gap_buf = _sb_start_gap(55.0, 32.0), _sb_start_gap(20.0, 32.0), _sb_start_gap(55.0, 50.0)
+R.check(
+    "the start gap settles no wood: a measured wood tank, hot or cold, is the plan's own and debits nothing",
+    _sb_gap_hot == _sb_gap_cold and abs(_sb_gap_buf - _sb_gap_hot) > 1.0,
+    repr((_sb_gap_hot, _sb_gap_cold, _sb_gap_buf)),
+)
 # An interval of no length settled no hours, so the stored coverage (the
 # payload the ledger store saves) takes no sample from it, as it takes none
 # from a backwards one.
@@ -63287,33 +63541,50 @@ R.check(
     _f23_opt.model.params.dhw_coil_active and max(_f23_gaps.values()) <= 1e-9,
     f"end gaps (K): {({k: round(v, 6) for k, v in _f23_gaps.items()})}",
 )
-# The reference's no-coil twin: the same call, the coil's draws withheld.
+# The reference has no coil (owner ruling, 2026-11-04): switching the plan's coil
+# off leaves its simulated end as it was, and its settled end shares the plan's wood.
 _f23_ba, _f23_bk = _f23_seen["base_call"]
-_f23_bk_full = dict(_f23_bk)
-_f23_bk.pop("coil_draws", None)
-_, _f23_bend_nocoil = _f23_real_base(_f23_opt, *_f23_ba, **_f23_bk)
-R.check(
-    "R9-F2.3 D2-s2-03: the thermostat reference's wood tank ends lower than "
-    "its no-coil twin -- it owns the coil the plan owns",
-    float(_f23_bend.wood_tank_temperature)
-    < float(_f23_bend_nocoil.wood_tank_temperature) - 1e-6,
-    f"reference wood end {float(_f23_bend.wood_tank_temperature):.6f} vs "
-    f"no-coil {float(_f23_bend_nocoil.wood_tank_temperature):.6f}",
-)
-# ... and only while the coil is on: switched off, the draws change nothing.
+_, _f23_bend_on = _f23_real_base(_f23_opt, *_f23_ba, **_f23_bk)
 _f23_opt.model.params.dhw_wood_coil_enabled = False
 try:
-    _, _f23_bend_off = _f23_real_base(_f23_opt, *_f23_ba, **_f23_bk_full)
+    _, _f23_bend_off = _f23_real_base(_f23_opt, *_f23_ba, **_f23_bk)
 finally:
     _f23_opt.model.params.dhw_wood_coil_enabled = True
 R.check(
-    "R9-F2.3 D2-s2-03: with the coil switched off, the reference's draws "
-    "leave its wood tank as its no-coil twin's",
-    np.any(np.asarray(_f23_bk_full.get("coil_draws", [])) > 0)
-    and float(_f23_bend_off.wood_tank_temperature)
-    == float(_f23_bend_nocoil.wood_tank_temperature),
-    f"off {float(_f23_bend_off.wood_tank_temperature):.6f} vs no-coil "
-    f"{float(_f23_bend_nocoil.wood_tank_temperature):.6f}",
+    "the thermostat reference owns no coil: its wood stand-in ends the same with the coil on or off",
+    float(_f23_bend_on.wood_tank_temperature) == float(_f23_bend_off.wood_tank_temperature)
+    and float(_f23_bend_on.wood_tank_temperature) < float(_f23_oend.wood_tank_temperature),
+    f"on {float(_f23_bend_on.wood_tank_temperature):.6f} off "
+    f"{float(_f23_bend_off.wood_tank_temperature):.6f} plan {float(_f23_oend.wood_tank_temperature):.6f}",
+)
+R.check(
+    "the settle-up's reference end carries the plan's wood side: heat wood left is no store to settle",
+    float(_f23_bend.wood_tank_temperature) == float(_f23_oend.wood_tank_temperature),
+    f"reference {float(_f23_bend.wood_tank_temperature):.6f} plan "
+    f"{float(_f23_oend.wood_tank_temperature):.6f}",
+)
+# The space-only path settles through its own call, and a plan's deferred cost
+# reads the wood store directly: a stand-in end there debits the plan its firewood.
+from golden import SCENARIOS as _f23_scenarios, capture as _f23_capture  # noqa: E402
+
+_f23_space_ends = []
+
+
+def _f23_space_def(self, *a, **k):
+    _f23_space_ends.append((a[0].wood_tank_temperature, a[1].wood_tank_temperature))
+    return _f23_real_def(self, *a, **k)
+
+
+_F23Opt._deferred_energy_cost = _f23_space_def
+try:
+    _f23_capture("wood_two_tank", _f23_scenarios["wood_two_tank"])
+finally:
+    _F23Opt._deferred_energy_cost = _f23_real_def
+# The start gap's call shares it as well, so every call reads the two equal.
+R.check(
+    "the space-only settle-up's reference end carries the plan's wood side too",
+    bool(_f23_space_ends) and all(ref == plan for ref, plan in _f23_space_ends),
+    repr(_f23_space_ends[:3]),
 )
 
 # D7-s1-71 / D5-s2-03: the cold-water inlet default is defined once. The
diff --git a/tests/finite_boundary.py b/tests/finite_boundary.py
index b91409b92..c984d9fab 100644
--- a/tests/finite_boundary.py
+++ b/tests/finite_boundary.py
@@ -118,11 +118,20 @@ SUBSTITUTES = NONFINITE + WRONG_TYPE
 # Arm 1 — the seam set is derived, not carried
 # ---------------------------------------------------------------------------
 
+#: The boundary's class and every subclass, read off the module that owns them,
+#: so a store with its own migration is a boundary without being named here.
+_QUARANTINE_CLASSES = frozenset(
+    name for name, obj in vars(_store).items()
+    if isinstance(obj, type) and issubclass(obj, QuarantiningStore)
+)
+
+
 def _boundary_sites() -> tuple[list[str], list[str]]:
     """Every ``QuarantiningStore(...)`` and raw ``Store(...)`` construction.
 
     The enumeration rule: walk the package's AST; a ``Call`` whose callee is the
-    bare name ``QuarantiningStore`` is a store-load boundary, and a ``Call``
+    bare name ``QuarantiningStore`` or a subclass the store module defines is a
+    store-load boundary, and a ``Call``
     whose callee is the bare name ``Store`` is a boundary that skipped the
     choke point. ``Store[_T]`` in a base class or a type annotation is neither
     (a ``Subscript``/base, not a ``Call``), so it never trips the raw check.
@@ -137,7 +146,7 @@ def _boundary_sites() -> tuple[list[str], list[str]]:
             func = node.func
             if isinstance(func, ast.Name):
                 rel = str(path.relative_to(ROOT))
-                if func.id == "QuarantiningStore":
+                if func.id in _QUARANTINE_CLASSES:
                     quarantined.append(f"{rel}:{node.lineno}")
                 elif func.id == "Store":
                     raw.append(f"{rel}:{node.lineno}")
@@ -2206,7 +2215,7 @@ def _version_names() -> list[tuple[str, str | None]]:
     for path in sorted(PKG.rglob("*.py")):
         for node in ast.walk(ast.parse(path.read_text(), filename=str(path))):
             if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
-                    and node.func.id == "QuarantiningStore"):
+                    and node.func.id in _QUARANTINE_CLASSES):
                 continue
             arg = node.args[1] if len(node.args) > 1 else next(
                 (k.value for k in node.keywords if k.arg == "version"), None)
@@ -2323,9 +2332,13 @@ def _version_arm(by_name) -> None:
                     if key not in _storage._DISK:
                         overwritten.append(f"{name}@reload:unsaved")
                 warned, issued = _surfaced(coord, key)
-                if not lag and (warned or issued):
+                # One below a store with its own migration is that migration's,
+                # no mismatch: it surfaces nothing. features.py pins what it migrates to.
+                migrated = lag == 1 and type(stores[key])._async_migrate_func is not (
+                    QuarantiningStore._async_migrate_func)
+                if (not lag or migrated) and (warned or issued):
                     noisy.append(name)
-                elif lag and not (warned and issued):
+                elif lag and not migrated and not (warned and issued):
                     unsurfaced.append(f"{name}@{lag}:warned={warned},issued={issued}")
     finally:
         QuarantiningStore.async_load = real_load
@@ -2336,7 +2349,7 @@ def _version_arm(by_name) -> None:
         _storage._VERSIONS.clear()
         _store._NEWER_ON_DISK.clear()
     R.check(
-        "a store read at its own version surfaces nothing (the control)",
+        "a store read at its own version, or one its own migration reads, surfaces nothing (the control)",
         not noisy and len(stores) == len(LOADERS),
         f"noisy={noisy} stores={len(stores)} loaders={len(LOADERS)}",
     )
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index 079f94e17..cc3d0a727 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -68,6 +68,15 @@
 # next branch restates its own footprint, claims included.
 #
 shape: space_reasons[*]|dhw_reasons[*] * -> 'idle_coasting'|'idle'  # R10-ARCH-SHAPES-CLASSIFIER (D8-s1-01): the reason classifiers read each channel's draw only on the steps the plan runs the pump at, so a share on a step the plan calls off is idle; which fixtures carry such a step is the host's basin (#996)
+valve_storage  # R10-HOTFIX-SAV-ESTIMATE: baseline_cost DOWN: booked by the steady demand: its kWh rises, its price paid falls, with no 6 kW first-step transient
+valve_storage_smart_write  # R10-HOTFIX-SAV-ESTIMATE: baseline_cost DOWN: as valve_storage, the same reference
+valve_storage_small_tank  # R10-HOTFIX-SAV-ESTIMATE: baseline_cost DOWN, predicted_savings and savings_percentage DOWN with it: spread by steady demand; the plan does not move
+valve_storage_flat_prices  # R10-HOTFIX-SAV-ESTIMATE: baseline_cost UP with the reference's kWh (its tank starts held, not on the measured charge); plan leaves move, the reference seeds the solve's starts
+valve_storage_low_target  # R10-HOTFIX-SAV-ESTIMATE: baseline_cost UP as flat_prices; plan lands in another basin (seeded starts), objective +0.24 %
+valve_upper_direct_slab  # R10-HOTFIX-SAV-ESTIMATE: baseline_cost UP: the held tank buys the direct slab's need
+wood_coil  # R10-HOTFIX-SAV-ESTIMATE: baseline_cost UP: the reference has no wood tank, no fire, no coil
+wood_two_tank  # R10-HOTFIX-SAV-ESTIMATE: baseline_cost UP: the reference has no wood; it reads the plain valve_storage reference
+wood_two_tank_smart_write  # R10-HOTFIX-SAV-ESTIMATE: baseline_cost UP: as wood_two_tank
 #
 # may-drift: flat_prices -- #1208 polish-every-candidate, owner ruling #1208 comment 208bed25
 # (option (a)): the move's margin is inside the noise band (objective rel
@@ -94,11 +103,16 @@ shape: space_reasons[*]|dhw_reasons[*] * -> 'idle_coasting'|'idle'  # R10-ARCH-S
 # one was restored.
 #
 #
-# may-drift: valve_storage_smart_write -- machine-sensitive; the DHW plan can reach it, per local optimum
-# may-drift: wood_two_tank -- machine-sensitive; the DHW plan can reach it, per local optimum
-# may-drift: wood_two_tank_smart_write -- machine-sensitive; the DHW plan can reach it, per local optimum
-# may-drift: wood_coil -- machine-sensitive; the DHW plan can reach it, per local optimum
-# may-drift: valve_upper_direct_slab -- machine-sensitive; the DHW plan can reach it, per local optimum
+# (R10-HOTFIX-SAV-ESTIMATE suspends valve_storage_smart_write's may-drift entry for its claim below; restore it,
+#  verbatim, when the stamp empties the list) valve_storage_smart_write -- machine-sensitive; the DHW plan can reach it, per local optimum
+# (R10-HOTFIX-SAV-ESTIMATE suspends wood_two_tank's may-drift entry for its claim below; restore it,
+#  verbatim, when the stamp empties the list) wood_two_tank -- machine-sensitive; the DHW plan can reach it, per local optimum
+# (R10-HOTFIX-SAV-ESTIMATE suspends wood_two_tank_smart_write's may-drift entry for its claim below; restore it,
+#  verbatim, when the stamp empties the list) wood_two_tank_smart_write -- machine-sensitive; the DHW plan can reach it, per local optimum
+# (R10-HOTFIX-SAV-ESTIMATE suspends wood_coil's may-drift entry for its claim below; restore it,
+#  verbatim, when the stamp empties the list) wood_coil -- machine-sensitive; the DHW plan can reach it, per local optimum
+# (R10-HOTFIX-SAV-ESTIMATE suspends valve_upper_direct_slab's may-drift entry for its claim below; restore it,
+#  verbatim, when the stamp empties the list) valve_upper_direct_slab -- machine-sensitive; the DHW plan can reach it, per local optimum
 # may-drift: winter_two_zone_no_dhw -- #1208 polish-every-candidate, owner
 # ruling #1208 comment 208bed25 (option (a)): the move's margin is inside the
 # noise band (objective rel -1.3365e-03, predicted_cost rel +8.39e-03),
@@ -183,7 +197,8 @@ shape: space_reasons[*]|dhw_reasons[*] * -> 'idle_coasting'|'idle'  # R10-ARCH-S
 # byte-identical on the dev box), runner-conditional for the same reason;
 # judged keys still fail. Remove when drift lanes are pinned or the polish
 # improvement scale leaves 5e-5-2e-2.
-# may-drift: valve_storage -- #1207 keep-gate (2e-2 -> 2e-5), widened to
+# (R10-HOTFIX-SAV-ESTIMATE suspends valve_storage's may-drift entry for its claim below; restore it,
+#  verbatim, when the stamp empties the list) valve_storage -- #1207 keep-gate (2e-2 -> 2e-5), widened to
 # the runner's union by the owner's ruling (i) on the options recorded in
 # #1207 comment 1ec15c8 (2026-09-20): 625 leaves moved on the CI
 # x86_64/py3.14 runner only (as recorded on that comment; byte-identical
@@ -743,3 +758,11 @@ shape: space_reasons[*]|dhw_reasons[*] * -> 'idle_coasting'|'idle'  # R10-ARCH-S
 # valve_storage_low_target, whose plan leaves move too: the reference's energy
 # anchors three of the space solve's starts, so a valved plan can land in
 # another basin. Unvalved fixtures do not move.
+# R10-HOTFIX-SAV-ESTIMATE: the reference has no wood on any house and holds its tank behind a
+# valve, booked by the steady demand (owner ruling, 2026-11-04). Measured with
+# env_drift --all against the merge base in one environment: exactly the nine
+# fixtures claimed move, every one valved or wood; every unvalved fixture is
+# byte-identical, which is the null. The objective is unchanged and the reference
+# is never optimised, but its kWh seeds the space solve's starts, so plans move
+# in basin only: the objective falls on four of the eight solved plans compared
+# and rises on three, by at most 0.25, and one is unchanged.
diff --git a/tests/mutation_ledger/killed_by/ledger.py/savings_pct.RETURN_DEL.4bbcde55.json b/tests/mutation_ledger/killed_by/ledger.py/savings_pct.RETURN_DEL.4bbcde55.json
deleted file mode 100644
index 7f288f3b3..000000000
--- a/tests/mutation_ledger/killed_by/ledger.py/savings_pct.RETURN_DEL.4bbcde55.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/ledger.py:savings_pct RETURN_DEL 4bbcde55",
-  "killed_by": "tests/features.py",
-  "old": "    return float(np.clip(savings_sek / baseline_sek * 100.0, -100.0, 100.0))",
-  "reason": "Recorded by `mutation_table.py --drain` against 9111acceb7831fa4c16ed42a30c579cda404130f: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.BOOLOP.03ee6373.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.BOOLOP.03ee6373.json
deleted file mode 100644
index ad5623a79..000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.BOOLOP.03ee6373.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._compute_baseline_power BOOLOP 03ee6373",
-  "killed_by": "tests/features.py",
-  "old": "            if two_tank and state.wood_tank_temperature is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 5c0ee109305fc4f377c9326c712156b9ceb0e638: BOOLOP (`if two_tank or state.wood_tank_temperature is not None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.BOOLOP.64b1ab84.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.BOOLOP.64b1ab84.json
deleted file mode 100644
index 9478c052b..000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.BOOLOP.64b1ab84.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._compute_baseline_power BOOLOP 64b1ab84",
-  "killed_by": "tests/doc_claims.py",
-  "old": "                if external_heat_kw is not None and i < len(external_heat_kw)",
-  "reason": "Recorded by `mutation_table.py --drain` against a1da8d381aa0afd2d1be6753678a8fc6191604ec: BOOLOP (`if external_heat_kw is not None or i < len(external_heat_kw)`) took tests/doc_claims.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.CLAMP_DROP.bea58ed9.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.CLAMP_DROP.bea58ed9.json
deleted file mode 100644
index afe9dd76e..000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.CLAMP_DROP.bea58ed9.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._compute_baseline_power CLAMP_DROP bea58ed9",
-  "killed_by": "tests/features.py",
-  "old": "            required_thermal = max(0.0, required_thermal - ext_i)",
-  "reason": "Recorded by `mutation_table.py --drain`: CLAMP_DROP (`required_thermal = (0.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.03ee6373.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.03ee6373.json
deleted file mode 100644
index 0b61b3c95..000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.03ee6373.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._compute_baseline_power GUARD_OFF 03ee6373",
-  "killed_by": "tests/features.py",
-  "old": "            if two_tank and state.wood_tank_temperature is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 5c0ee109305fc4f377c9326c712156b9ceb0e638: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.308a9d57.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.308a9d57.json
deleted file mode 100644
index 11e2ce53b..000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.308a9d57.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._compute_baseline_power GUARD_OFF 308a9d57",
-  "killed_by": "tests/features.py",
-  "old": "        if not p.dhw_coil_active:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 9c6b923f2614936aad89e1408dabca8ddd721322: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.52814e2f.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.52814e2f.json
deleted file mode 100644
index 96147d56b..000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.52814e2f.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._compute_baseline_power GUARD_OFF 52814e2f",
-  "killed_by": "tests/features.py",
-  "old": "            if coil_draws is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 9c6b923f2614936aad89e1408dabca8ddd721322: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/valve_charge_demand.CLAMP_DROP.4f2d48ae.json b/tests/mutation_ledger/killed_by/thermal_model.py/valve_charge_demand.CLAMP_DROP.4f2d48ae.json
deleted file mode 100644
index 1c4506a69..000000000
--- a/tests/mutation_ledger/killed_by/thermal_model.py/valve_charge_demand.CLAMP_DROP.4f2d48ae.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:valve_charge_demand CLAMP_DROP 4f2d48ae",
-  "killed_by": "tests/features.py",
-  "old": "        min(t, p.buffer_max_temp) for _, top, zone in circuits for t in (top, zone)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`(t) for _, top, zone in circuits for t in (top, zone)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._compute_baseline_power.CMP_BOUND.64b1ab84.json b/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._compute_baseline_power.CMP_BOUND.64b1ab84.json
deleted file mode 100644
index 13c91481a..000000000
--- a/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._compute_baseline_power.CMP_BOUND.64b1ab84.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._compute_baseline_power CMP_BOUND 64b1ab84",
-  "old": "                if external_heat_kw is not None and i < len(external_heat_kw)",
-  "reason": "R10 mutation-anchor: the `killed_by: tests/entities.py` pin was vacuous. Re-driven at 0be5e2de5 by dev/audit/harnesses/r10_anchor_vacuous.py with the 2 ledger row(s) the mutant itself makes stale hidden from its tree, 0 of 1 site(s) were killed by tests/entities.py: the recorded kill was a check refusing a ledger row the mutant made stale (the --anchor self-test, or the survivor_triage staleness check), not one that saw the mutation. Was: Recorded by `mutation_table.py --drain` against 816547efe270a08e18e3b92f52185fe8c1fee2ef: CMP_BOUND (`if external_heat_kw is not None and i <= len(external_heat_kw)`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1. Not re-driven here against the other drivers in its closure, so a gap until one is shown to kill it.",
-  "verdict": "gap"
-}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index aeee1873e..73db69c39 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17630,
+ "class_excess_loc": 17602,
  "const_modules_over_50": 3,
  "coordinator_attrs": 141,
  "coordinator_multiassigned_attrs": 108,
@@ -16,6 +16,6 @@
  "methods_over_150": 15,
  "methods_over_200": 8,
  "name_kept_members": 38,
- "recorded_at": "c3a279e3252a8b57bb00b5a677318cd4fe20387f",
+ "recorded_at": "2a9cd3476dae9f45d3091b546fdd2723bcb0ce4e",
  "seam_cut_total": 423
 }

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
