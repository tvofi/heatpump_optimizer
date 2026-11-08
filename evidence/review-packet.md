# Review packet #3297
head: 7fe24f9f61f1935fab269f006e126fc6f84184b3
base: 4fe7d5934b0a4bc092c9398f29b579fbd2df8b50

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=128711962905 success
arch-score / arch-score id=128751247162 success
arm id=128711422566 skipped
budget-raise-gate / budget-raise-gate id=128751243412 success
cancel-superseded id=128751253516 success
codeql id=128711629984 skipped
codeql / Analyze (actions) id=128751220771 success
codeql / Analyze (javascript-typescript) id=128751262299 success
codeql / Analyze (python) id=128751252347 success
gate id=128759633548 failure
governance id=128711630211 skipped
governance / delivery-status id=128751221526 success
governance / delivery-status-publish id=128751261200 skipped
governance / env-matrix id=128751250851 success
governance / instrument-self-tests id=128751252961 success
governance / policy-docs id=128751220381 success
governance / record id=128751249800 skipped
governance / wave-script id=128751220681 success
hassfest id=128711629864 skipped
hassfest / hassfest id=128751254752 success
kernel-points id=128751245383 skipped
pr-contract id=128712246133 skipped
pr-contract / pr-contract id=128759406743 failure
prelude id=128751260928 success
refresh id=128751242091 success
tests id=128711630269 skipped
tests / arch-instrument id=128751221131 success
tests / briefs id=128751247263 success
tests / browser id=128751221039 success
tests / ci-ratchet id=128759294963 skipped
tests / claims-autofix id=128759293462 success
tests / closure-scope id=128751247992 success
tests / closures id=128751221145 success
tests / closures-autofix id=128751221053 skipped
tests / coverage id=128751221120 success
tests / coverage-ratchet id=128751221209 success
tests / fast (3.14) id=128751219984 failure
tests / graders-head-copy id=128751221631 success
tests / lane-proofs id=128759293434 success
tests / mutation id=128751219848 success
tests / mutation-autofix id=128751221810 skipped
tests / mutation-pins id=128751221398 skipped
tests / nightly-ha (2025.2.0) id=128751221747 success
tests / nightly-ha (stable) id=128751220857 success
tests / nightly-status id=128751243080 success
tests / replay id=128751220955 success
tests / typing id=128751220634 success
validate id=128711629998 skipped
validate / validate-hacs id=128751220147 success

## Refusals
structure: tests/structure.py refuses the head merged with main: head does not merge cleanly with origin/main: ['100644 b873faaf3188680cd55bdedc22f5161e5f974766 1\tcustom_components/heatpump_optimizer/thermal_model.py', '100644 7e3e082325166257dbc499eb0115ee9609d979d0 2\tcustom_components/heatpump_optimizer/thermal_model.py']
red-unanswered: concluded red check `tests / fast (3.14)` is not named in ## Red checks
required-red: required context `gate` concluded failure at 7fe24f9f61f1935fab269f006e126fc6f84184b3

## Advisories
none

## carry_audit at the head
NOTE body item 23234112: dismissed:a fixer seat may not write the roster branch, so this seat cannot land it; the orchestrator lands it on R10-PREPR-CAP (owner of tools/pr/prepr.sh) from this return
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub python3 tests/features.py
             `tests/features.py` is in the tree at this head
  ok         python3 tests/env_drift.py
             `tests/env_drift.py` is in the tree at this head
  ok         python3 tests/env_drift.py --all 73365699a135fb813a43380096b6776d57f8ff4c
             `tests/env_drift.py` is in the tree at this head
  ok         node tests/card_drift.mjs 2a3c05644d85b7ee5c2c314fde5aca950e4aba91
             `tests/card_drift.mjs` is in the tree at this head
  ok         tests/plan_view.py
             `tests/plan_view.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD
             `tools/audit/archscore/score.py` is in the tree at this head
  unverified bash <scratch>/mut.sh
             the path `<scratch>/mut.sh` is a template or an expansion, not a literal
  ok         PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude "<the 36 top-level statements of tests/features.py the section reads>" 'R.section("R10-HOTFIX-COP-UNMEASURED' 'R.section("early cut-off'
             `tools/audit/seat/features_block.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/mutant_run.py --diff "$(git merge-base origin/main HEAD)...HEAD" --cmd "$MUTANT_CMD" --max-mutants 0 --report-only
             `tools/audit/seat/mutant_run.py` is in the tree at this head
  ok         PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  unverified git diff --stat $(git merge-base origin/main HEAD)...HEAD -- '*_budgets.json'
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -n -e "_measured_cop.record(" -e "_observe_cop_health(" -- custom_components
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 10 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.ac5ca5ae.json b/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.75c968b4.json
similarity index 71%
rename from tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.ac5ca5ae.json
rename to tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.75c968b4.json
index 95594139b..cb766b020 100644
--- a/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.ac5ca5ae.json
+++ b/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.75c968b4.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:cop_observability GUARD_OFF ac5ca5ae",
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:cop_observability GUARD_OFF 75c968b4",
   "killed_by": "tests/features.py",
-  "old": "    if measured_heat:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+  "old": "    if not measured_heat:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
 }
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.RETURN_DEL.e75e96f9.json b/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.RETURN_DEL.8b12f886.json
similarity index 64%
rename from tests/mutation_ledger/killed_by/accuracy.py/cop_observability.RETURN_DEL.e75e96f9.json
rename to tests/mutation_ledger/killed_by/accuracy.py/cop_observability.RETURN_DEL.8b12f886.json
index 57131144a..3564adb19 100644
--- a/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.RETURN_DEL.e75e96f9.json
+++ b/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.RETURN_DEL.8b12f886.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:cop_observability RETURN_DEL e75e96f9",
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:cop_observability RETURN_DEL 8b12f886",
   "killed_by": "tests/features.py",
-  "old": "    return COP_DRAW_FOLLOWS if follows else COP_NOT_MEASURABLE",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+  "old": "    return COP_ESTIMATED if estimated else COP_HEAT_METERED",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
 }
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_cop_evidence.GUARD_OFF.690970ce.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_cop_evidence.GUARD_OFF.690970ce.json
new file mode 100644
index 000000000..2f153a927
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_cop_evidence.GUARD_OFF.690970ce.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_cop_evidence GUARD_OFF 690970ce",
+  "killed_by": "tests/features.py",
+  "old": "        if measured:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=17."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_cop_evidence.GUARD_OFF.afc1c494.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_cop_evidence.GUARD_OFF.afc1c494.json
new file mode 100644
index 000000000..ded6d89fd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_cop_evidence.GUARD_OFF.afc1c494.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_cop_evidence GUARD_OFF afc1c494",
+  "killed_by": "tests/features.py",
+  "old": "        if (measured := probe_install(_ctx_of(self)._config).cop_sample(heat_kw, bool(cop_curve_dhw))) is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.c1dafc5f.json b/tests/mutation_ledger/killed_by/coordinator.py/machine_score.GUARD_OFF.6bdb5987.json
similarity index 57%
rename from tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.c1dafc5f.json
rename to tests/mutation_ledger/killed_by/coordinator.py/machine_score.GUARD_OFF.6bdb5987.json
index c64de4327..d11c0770f 100644
--- a/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.c1dafc5f.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/machine_score.GUARD_OFF.6bdb5987.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:cop_observability GUARD_OFF c1dafc5f",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:machine_score GUARD_OFF 6bdb5987",
   "killed_by": "tests/features.py",
-  "old": "    if follows is None:",
+  "old": "    if not measurable:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
 }
diff --git a/tests/mutation_ledger/killed_by/sensor.py/ObservedCOPSensor._waiting_for.GUARD_OFF.c85dda37.json b/tests/mutation_ledger/killed_by/sensor.py/ObservedCOPSensor._waiting_for.GUARD_OFF.c85dda37.json
new file mode 100644
index 000000000..200195514
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sensor.py/ObservedCOPSensor._waiting_for.GUARD_OFF.c85dda37.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sensor.py:ObservedCOPSensor._waiting_for GUARD_OFF c85dda37",
+  "killed_by": "tests/entities.py",
+  "old": "        if data.get(\"cop_observability\") == COP_ESTIMATED:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.cop_sample.BOOLOP.d31f43a0.json b/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.cop_sample.BOOLOP.d31f43a0.json
new file mode 100644
index 000000000..0d86ffde0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.cop_sample.BOOLOP.d31f43a0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:InstallCapability.cop_sample BOOLOP d31f43a0",
+  "killed_by": "tests/features.py",
+  "old": "            return None if self.measured_heat and not self.heat_counter else False",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return None if self.measured_heat or not self.heat_counter else False`) took tests/features.py from rc=0 failed=0 to rc=1 failed=18."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.cop_sample.GUARD_OFF.1d188586.json b/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.cop_sample.GUARD_OFF.1d188586.json
new file mode 100644
index 000000000..3dfa8635d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.cop_sample.GUARD_OFF.1d188586.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:InstallCapability.cop_sample GUARD_OFF 1d188586",
+  "killed_by": "tests/features.py",
+  "old": "        if heat_kw is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.cop_sample.RETURN_DEL.af9c59c9.json b/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.cop_sample.RETURN_DEL.af9c59c9.json
new file mode 100644
index 000000000..cdc1f708b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.cop_sample.RETURN_DEL.af9c59c9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:InstallCapability.cop_sample RETURN_DEL af9c59c9",
+  "killed_by": "tests/features.py",
+  "old": "        return self.cop_measured(dhw)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/_estimated.GUARD_OFF.0b2cd5cf.json b/tests/mutation_ledger/killed_by/thermal_model.py/_estimated.GUARD_OFF.0b2cd5cf.json
new file mode 100644
index 000000000..5762883a3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/_estimated.GUARD_OFF.0b2cd5cf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:_estimated GUARD_OFF 0b2cd5cf",
+  "killed_by": "tests/features.py",
+  "old": "    if source == const.METER_SOURCE_ESTIMATE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/_estimated.GUARD_OFF.82c38afb.json b/tests/mutation_ledger/killed_by/thermal_model.py/_estimated.GUARD_OFF.82c38afb.json
new file mode 100644
index 000000000..071a8ee8c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/_estimated.GUARD_OFF.82c38afb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:_estimated GUARD_OFF 82c38afb",
+  "killed_by": "tests/features.py",
+  "old": "    if source == const.METER_SOURCE_METER:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/_estimated.RETURN_DEL.51801b43.json b/tests/mutation_ledger/killed_by/thermal_model.py/_estimated.RETURN_DEL.51801b43.json
new file mode 100644
index 000000000..2caf43097
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/_estimated.RETURN_DEL.51801b43.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:_estimated RETURN_DEL 51801b43",
+  "killed_by": "tests/features.py",
+  "old": "    return const.ESTIMATE_ID_MARK in str(entity_id or \"\").lower()",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/accuracy.py b/custom_components/heatpump_optimizer/accuracy.py
index cef4c9248..378edb3bd 100644
--- a/custom_components/heatpump_optimizer/accuracy.py
+++ b/custom_components/heatpump_optimizer/accuracy.py
@@ -810,38 +810,39 @@ COP_REFUSED_OBSERVED = "observed_cop"
 #: ``heat_energy``'s ``SPAN_REFUSED_*`` codes.
 COP_REFUSED_SPAN_OPEN = "span_open"
 COP_REFUSED_UNALIGNED = "unaligned_meters"
+#: A thermal power entity is configured and read no heat this interval
+#: (unavailable, or negative): the plan's inference does not stand in for it.
+COP_REFUSED_NO_HEAT = "no_heat_reading"
 
 #: How far the metered draw may depart from the plan's ask, as a share of the
 #: ask, before the interval is judged on ``draw_range.follows_ask``'s evidence
 #: (``MeasuredCop.judge_ratio``).
 COP_ASK_TOLERANCE = 0.15
 
-#: Whether this install can observe its COP at all (#2262; ``cop_observability``):
-#: a heat reading over an electrical one measures it; without a heat reading
-#: the ratio of draw to ask is an efficiency reading only where the draw follows
-#: the ask, which ``draw_range.follows_ask`` judges.
+#: Whether this install can measure its COP at all (#2262,
+#: R10-HOTFIX-COP-UNMEASURED; ``cop_observability``): only a heat reading over
+#: an electrical one, neither of them a vendor's model, measures it. Without a
+#: heat reading the ratio of draw to ask still trains the COP scale, but it is
+#: the model's own COP scaled by plan tracking, never a measurement.
 COP_HEAT_METERED = "heat_metered"
-COP_DRAW_FOLLOWS = "draw_follows_plan"
+COP_ESTIMATED = "estimated_inputs"
 COP_NOT_MEASURABLE = "not_measurable"
 COP_NO_ELECTRIC = "no_electric_meter"
 
 
-def cop_observability(*, electric: bool, measured_heat: bool, follows: bool | None) -> str:
-    """This install's COP observability: one of the ``COP_*`` states above, or
-    ``COP_REFUSED_NO_EVIDENCE`` while the draw window cannot say yet.
+def cop_observability(*, electric: bool, measured_heat: bool, estimated: bool) -> str:
+    """This install's COP observability: one of the ``COP_*`` states above.
 
     ``electric``: an electrical figure the COP divides by (the power entity,
     or the electric counter a heat counter's span reads); ``measured_heat``:
     ``probe_install(...).measured_heat``, the heat counter or the thermal power
-    entity; ``follows``: ``follows_ask`` on the running-draw window.
+    entity; ``estimated``: either side is a vendor's estimate.
     """
     if not electric:
         return COP_NO_ELECTRIC
-    if measured_heat:
-        return COP_HEAT_METERED
-    if follows is None:
-        return COP_REFUSED_NO_EVIDENCE
-    return COP_DRAW_FOLLOWS if follows else COP_NOT_MEASURABLE
+    if not measured_heat:
+        return COP_NOT_MEASURABLE
+    return COP_ESTIMATED if estimated else COP_HEAT_METERED
 
 
 @dataclass
diff --git a/custom_components/heatpump_optimizer/config_flow.py b/custom_components/heatpump_optimizer/config_flow.py
index c43b8f690..532397527 100644
--- a/custom_components/heatpump_optimizer/config_flow.py
+++ b/custom_components/heatpump_optimizer/config_flow.py
@@ -355,6 +355,14 @@ from .const import (
     CONF_COMPRESSOR_FREQ_SENSOR,
     CONF_FLOW_METER_ENTITY,
     CONF_THERMAL_POWER_ENTITY,
+    CONF_THERMAL_POWER_SOURCE,
+    CONF_POWER_SOURCE,
+    CONF_HEAT_METER_SEES_DHW,
+    DEFAULT_HEAT_METER_SEES_DHW,
+    DEFAULT_METER_SOURCE,
+    METER_SOURCE_AUTO,
+    METER_SOURCE_ESTIMATE,
+    METER_SOURCE_METER,
     CONF_HEAT_ENERGY_ENTITY,
     CONF_COMPRESSOR_FREQ_MIN_HZ,
     CONF_COMPRESSOR_FREQ_MAX_HZ,
@@ -1071,6 +1079,17 @@ def _select(options: list[str], translation_key: str) -> selector.SelectSelector
     )
 
 
+def _meter_source_selector() -> selector.SelectSelector:
+    """Meter, vendor estimate, or read from the entity's id (R10-HOTFIX-COP-UNMEASURED)."""
+    return selector.SelectSelector(
+        selector.SelectSelectorConfig(
+            options=[METER_SOURCE_AUTO, METER_SOURCE_METER, METER_SOURCE_ESTIMATE],
+            translation_key="meter_source",
+            mode=selector.SelectSelectorMode.DROPDOWN,
+        )
+    )
+
+
 def _freq_mode_selector() -> selector.SelectSelector:
     """Observe or control (T7 #61).
 
@@ -1594,9 +1613,12 @@ _OPTION_FIELDS: Final[tuple[_F, ...]] = (
     _F("entities_metering", CONF_SOLAR_FORECAST_SOURCE, DEFAULT_SOLAR_FORECAST_SOURCE, _solar_source_selector(), group="solar"),
     _F("entities_metering", CONF_SOLAR_LOCATION, _Computed(lambda cur, hass: _default_location(hass, cur)), _solar_location_selector(), group="solar"),
     _F("entities_metering", CONF_POWER_ENTITY, _STORED, _entity_of('sensor', 'power'), group="meters"),
+    _F("entities_metering", CONF_POWER_SOURCE, DEFAULT_METER_SOURCE, _meter_source_selector(), group="meters"),
     _F("entities_metering", CONF_THERMAL_POWER_ENTITY, _STORED, _entity_of('sensor', 'power'), group="meters"),
+    _F("entities_metering", CONF_THERMAL_POWER_SOURCE, DEFAULT_METER_SOURCE, _meter_source_selector(), group="meters"),
     _F("entities_metering", CONF_ENERGY_ENTITY, _STORED, _entity_of('sensor', 'energy'), group="meters"),
     _F("entities_metering", CONF_HEAT_ENERGY_ENTITY, _STORED, _entity_of('sensor', 'energy'), group="meters"),
+    _F("entities_metering", CONF_HEAT_METER_SEES_DHW, DEFAULT_HEAT_METER_SEES_DHW, selector.BooleanSelector(), group="meters"),
     _F("entities_metering", CONF_HOUSE_POWER_ENTITY, _STORED, _entity_of('sensor', 'power'), group="meters"),
     _F("entities_metering", CONF_COMPRESSOR_FREQ_ENTITY, _STORED, _entity_of('number'), group="compressor"),
     _F("entities_metering", CONF_COMPRESSOR_FREQ_SENSOR, _STORED, _entity_of('sensor', 'frequency'), group="compressor"),
diff --git a/custom_components/heatpump_optimizer/const.py b/custom_components/heatpump_optimizer/const.py
index ea3065c28..b3b8abbb6 100644
--- a/custom_components/heatpump_optimizer/const.py
+++ b/custom_components/heatpump_optimizer/const.py
@@ -1149,6 +1149,24 @@ CONF_FLOW_METER_ENTITY: Final = "flow_meter_entity"
 #: outranks the meter whenever it is configured, and with a power entity it
 #: makes COP an observable (``flow_meter.read_heat_output_kw``).
 CONF_THERMAL_POWER_ENTITY: Final = "heat_pump_thermal_power_entity"
+#: Whether the power and the thermal power entity are meters or a vendor's
+#: model (R10-HOTFIX-COP-UNMEASURED): a COP is measured only from metered heat
+#: over metered power (``thermal_model.InstallCapability.cop_measured``), while
+#: every learner trains on either. ``auto`` reads an entity whose id names an
+#: estimate (``ESTIMATE_ID_MARK``, as an "Estimated Power Draw" sensor's does) as
+#: one and any other as a meter; the explicit answers override it.
+CONF_POWER_SOURCE: Final = "heat_pump_power_source"
+CONF_THERMAL_POWER_SOURCE: Final = "heat_pump_thermal_power_source"
+METER_SOURCE_AUTO: Final = "auto"
+METER_SOURCE_METER: Final = "meter"
+METER_SOURCE_ESTIMATE: Final = "estimate"
+DEFAULT_METER_SOURCE: Final = METER_SOURCE_AUTO
+ESTIMATE_ID_MARK: Final = "estimat"
+#: Whether the heat reading (the heat counter, else the thermal power entity)
+#: sees the hot-water circuit, as a meter ahead of the diverter does. Declared,
+#: never assumed: off, a hot-water interval records no measured COP.
+CONF_HEAT_METER_SEES_DHW: Final = "heat_meter_sees_dhw"
+DEFAULT_HEAT_METER_SEES_DHW: Final = False
 CONF_FREQ_CONTROL_MODE: Final = "freq_control_mode"
 #: The two frequency-control stages. Anything unrecognised in config reads
 #: as observe. Here rather than in ``freq_control`` because ``entry_config``
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index 3d34ee24a..ae7252e46 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -236,6 +236,7 @@ from .accuracy import (
     COP_REFUSED_FROST_BAND,
     COP_REFUSED_FROZEN,
     COP_REFUSED_MODELLED,
+    COP_REFUSED_NO_HEAT,
     COP_REFUSED_NO_POWER,
     COP_REFUSED_OBSERVED,
     COP_REFUSED_SPAN_OPEN,
@@ -382,6 +383,11 @@ _LOGGER = logging.getLogger(__name__)
 _create_issue = issues.create_issue
 # The learned scale's store key and published attribute are this config key.
 _COP_STORE_KEY = CONF_COP_SCALE
+#: The COP health watch's memory in the thermal-learning store, keyed apart
+#: from its pre-R10-HOTFIX-COP-UNMEASURED "cop_baseline" and "cop_health_cusum",
+#: whose samples a heat measurement never vouched for: the key is the provenance.
+_COP_BASELINE_KEY: Final = "cop_baseline_measured"
+_COP_HEALTH_CUSUM_KEY: Final = "cop_health_cusum_measured"
 
 # Forecast wind speed arrives in whatever unit the user's Home Assistant is
 # configured for, so it has to be converted explicitly rather than guessed.
@@ -1437,7 +1443,7 @@ async def async_adopt_heat_loss_refit(coord: Any) -> bool:
 _FACTORY_VOID: Final[tuple[tuple[str, tuple[str, ...] | None], ...]] = (
     ("thermal_learning", (
         "buffer_cooling_rate", "buffer_cooling_samples", _COP_STORE_KEY, "cop_samples",
-        "vent_cusum", "cop_baseline", "cop_health_cusum", "immersion_events",
+        "vent_cusum", _COP_BASELINE_KEY, _COP_HEALTH_CUSUM_KEY, "immersion_events",
         "capacity_envelope", "solar_aperture", "internal_gains_profile",
         "curve_learner", "freq_map", "flow_bias",
     )),
@@ -3351,15 +3357,19 @@ SCORE_REFERENCE: dict[str, float] = {
 
 
 def machine_score(
-    baseline: Mapping[Any, Any], cusum_stat: float
+    baseline: Mapping[Any, Any], cusum_stat: float, measurable: bool
 ) -> tuple[float | None, str | None, list[dict[str, Any]]]:
     """The heat pump grade (#65), the code saying why it is None, and its drivers.
 
     100 while the COP watch (#12) accumulates no shortfall; the grade falls
-    as the Cusum climbs toward its alarm. No watched bucket is no evidence.
+    as the Cusum climbs toward its alarm. No watched bucket is no evidence;
+    ``measurable`` False (``InstallCapability.cop_measured``) is no grade ever,
+    said so rather than as evidence still to come.
     Its one driver, ``cop_shortfall``, is the grade's distance below 100,
     the pump matching its own COP history (``SCORE_REFERENCE``).
     """
+    if not measurable:
+        return None, "cop_unmeasurable", []
     if not _watched_cop_buckets(baseline):
         return None, "cop_watch_learning", []
     grade = (1.0 - float(np.clip(cusum_stat / COP_HEALTH_THRESHOLD, 0.0, 1.0))) * 100.0
@@ -4624,13 +4634,13 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         # Re-anchored before anything solves; gated write, last: `updated_at` defeats the hash skip.
         save = self._reanchor_house_heat_loss_scale(stored) or not all(
             k in stored for k in _HEAT_LOSS_ANCHOR_KEYS)
-        self._measured_cop = MeasuredCop.from_dict(stored.get("measured_cop"))
+        self._measured_cop = MeasuredCop.from_dict(stored.get("measured_cop") if _COP_BASELINE_KEY in stored else None)
 
         # v4.0.0 T4a — the detectors' memory. Absent from every pre-T4
         # payload, and each loader tolerates garbage on its own.
         self._vent_cusum.load(stored.get("vent_cusum"))
-        self._cop_health_cusum.load(stored.get("cop_health_cusum"))
-        raw_baseline = stored.get("cop_baseline")
+        self._cop_health_cusum.load(stored.get(_COP_HEALTH_CUSUM_KEY))
+        raw_baseline = stored.get(_COP_BASELINE_KEY)
         if isinstance(raw_baseline, dict):
             for key, entry in raw_baseline.items():
                 try:
@@ -4753,18 +4763,18 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             "measured_cop": self._measured_cop.as_dict(),  # the sensor's value, kept across a restart
             # v4.0.0 T4a — the detectors' memory, all additive keys.
             "vent_cusum": self._vent_cusum.as_dict(),
-            # A space-curve bucket keeps its pre-v5.3.0 key ("4"), so an
-            # older store loads unchanged and a downgrade still reads it; a
-            # DHW-curve bucket rides alongside under "4:dhw". Additive, and
-            # nothing is discarded on upgrade.
-            "cop_baseline": {
+            # A space-curve bucket keeps its pre-v5.3.0 key ("4"); a DHW-curve
+            # bucket rides alongside under "4:dhw". Under _COP_BASELINE_KEY, so
+            # a downgrade reads no baseline and starts afresh, never one mixing
+            # measured and inferred samples.
+            _COP_BASELINE_KEY: {
                 (f"{k[0]}:{'dhw' if k[1] is True else k[1]}" if k[1] else str(k[0])): [
                     round(v[0], 4),
                     int(v[1]),
                 ]
                 for k, v in self._cop_baseline.items()
             },
-            "cop_health_cusum": self._cop_health_cusum.as_dict(),
+            _COP_HEALTH_CUSUM_KEY: self._cop_health_cusum.as_dict(),
             "immersion_events": list(self._immersion_events),
             # T4b #30: roof-snow memory, so a restart mid-snow does not
             # brighten the roof. Weather memory riding the nearest store.
@@ -5349,9 +5359,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         """Compare measured electrical input with modelled thermal output.
 
         Without a power entity or a heat counter the COP is a curve fitted to
-        a nameplate figure, and since every plan is priced through it, an
-        error there is an error in every cost the integration reports. With
-        either, COP becomes an observable and can join the other learners.
+        a nameplate figure every plan's cost runs through. With either the COP
+        scale learns; a measured COP needs metered heat too (``cop_sample``).
 
         Only intervals where the pump is genuinely running carry information;
         at low duty the measured average is dominated by standby draw.
@@ -5391,11 +5400,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         if heat_energy.meter_of(self).counter:
             return COP_REFUSED_SPAN_OPEN
 
-        # v4.0.5: without a heat meter this ratio reads as efficiency only
-        # while the pump plausibly runs the plan, so outliers are judged
-        # against a walking ratio EWMA (a fixed gate deadlocks on a true
-        # efficiency past it); a draw off the ask needs draw_range's
-        # evidence. A measured heat (fold e) leaves the gates nothing to judge.
+        # v4.0.5: without a heat reading this ratio trains the scale only while the pump
+        # plausibly runs the plan: outliers are judged against a walking ratio EWMA (a fixed gate
+        # deadlocks past it), a draw off the ask on draw_range's evidence; heat skips both.
         ratio = float(cast(float, self._measured_power)) / max(commanded, 1e-6)  # the two guards leave a power here
         # Seeded at 1.0, the model's own expectation, and gated against the
         # value BEFORE this sample updates it, so a first-sample blip cannot
@@ -5424,6 +5431,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             return COP_REFUSED_BLENDED
         if modelled_cop <= 0.1:
             return COP_REFUSED_MODELLED
+        if (measured := probe_install(_ctx_of(self)._config).cop_sample(heat_kw, bool(cop_curve_dhw))) is None:
+            return COP_REFUSED_NO_HEAT
 
         # ``cop_scale`` multiplies the *nameplate* curve and ``modelled_cop``
         # already carries it, so the target is the current scale times the
@@ -5434,7 +5443,6 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         )
         if not np.isfinite(observed_cop) or observed_cop <= 0.1:
             return COP_REFUSED_OBSERVED
-        self._measured_cop.record(observed_cop, cop_curve_dhw, cop_dhw_temp, dt_util.now())
 
         alpha = COP_LEARNING_ALPHA
         new_scale = (1.0 - alpha) * self._cop_scale + alpha * target_scale
@@ -5453,10 +5461,11 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             "against a modelled %.2f; scale now %.3f (%d samples)",
             commanded, electrical_kw, observed_cop, modelled_cop, self._cop_scale, self._cop_samples,
         )
-        # #12: the same vetted sample feeds the weeks-scale health watch —
-        # this path is already guarded against frost, immersion, freezes
-        # and low duty, so the baseline inherits every filter for free.
-        self._observe_cop_health(float(observed_cop), cop_curve_dhw)
+        # #12: a measured sample, vetted on this path for frost, immersion, freezes and
+        # low duty, feeds the health watch; an inference or estimate trains the scale alone.
+        if measured:
+            self._measured_cop.record(observed_cop, cop_curve_dhw, cop_dhw_temp, dt_util.now())
+            self._observe_cop_health(float(observed_cop), cop_curve_dhw)
         # #17 (gated): and the capacity envelope, for the same reason.
         self._fold_capacity_envelope(float(observed_cop), heat_kw)
         return None
@@ -8036,7 +8045,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             "pump_max_power": getattr(self._optimization_result, "solve_band", None) or None,
             "cop_observability": cop_observability(
                 electric=install.cop_electric(), measured_heat=install.measured_heat,
-                follows=draw_range.follows_ask(self._accuracy.draw),
+                estimated=install.heat_estimated or install.power_estimated,
             ),
             "defrost_derate": self._defrost.factor(
                 ctx._current_state.outdoor_temperature, self._current_humidity()
@@ -10661,7 +10670,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
                 self._house_heat_loss_samples, advice,
                 getattr(self, "_ctx", self)._config,
             ),
-            machine_score(self._cop_baseline, self._cop_health_cusum.stat),
+            machine_score(self._cop_baseline, self._cop_health_cusum.stat,
+                      probe_install(_ctx_of(self)._config).cop_measured(False)),
             (operation, None if operation is not None else operation_reason(self._score_day),
              driving_grade.published(driving_grade.held(self), operation)),
             machine_evidence(self._cop_baseline, self._measured_cop.frozen_refusals),
diff --git a/custom_components/heatpump_optimizer/sensor.py b/custom_components/heatpump_optimizer/sensor.py
index 738400cf3..6f3ff2dd2 100644
--- a/custom_components/heatpump_optimizer/sensor.py
+++ b/custom_components/heatpump_optimizer/sensor.py
@@ -22,7 +22,7 @@ from homeassistant.helpers.entity_platform import AddEntitiesCallback
 
 from . import narrative
 from . import topology
-from .accuracy import COP_NOT_MEASURABLE
+from .accuracy import COP_ESTIMATED, COP_NOT_MEASURABLE
 from .const import (
     CONF_BUFFER_TANK_TEMP_ENTITY,
     CONF_DHW_TEMP_ENTITY,
@@ -1721,6 +1721,10 @@ class ObservedCOPSensor(
         data = self._data()
         if not data.get("measured_power_available"):
             return "measured_power_entity"
+        if data.get("cop_observability") == COP_ESTIMATED:
+            # R10-HOTFIX-COP-UNMEASURED: a vendor's estimate on either side
+            # makes heat over power the vendor's own COP, never a measurement.
+            return "metered_inputs"
         if data.get("cop_observability") == COP_NOT_MEASURABLE:
             # #2262: the draw does not follow the plan's ask, so its ratio to
             # the ask is no COP; only a heat reading measures one here.
diff --git a/custom_components/heatpump_optimizer/store.py b/custom_components/heatpump_optimizer/store.py
index 326882305..7b95e60fd 100644
--- a/custom_components/heatpump_optimizer/store.py
+++ b/custom_components/heatpump_optimizer/store.py
@@ -344,8 +344,8 @@ DOMAINS: dict[str, dict[str, Domain | str]] = {
         "measured_cop/curve_dhw": _FLAG, "measured_cop/dhw_temp": _N, "measured_cop/at": _AT0,
         # The cap, as Cusum.as_dict rounds it (1.2 * 1.5 is 1.7999999999999998).
         "vent_cusum/stat": Domain("real", 0.0, round(c.VENT_CUSUM_THRESHOLD_C * STAT_CAP_FACTOR, 4)),
-        "cop_health_cusum/stat": Domain("real", 0.0, round(c.COP_HEALTH_THRESHOLD * STAT_CAP_FACTOR, 4)),
-        **{f"{k}_cusum/{f}": d for k in ("vent", "cop_health") for f, d in (
+        "cop_health_cusum_measured/stat": Domain("real", 0.0, round(c.COP_HEALTH_THRESHOLD * STAT_CAP_FACTOR, 4)),
+        **{f"{k}/{f}": d for k in ("vent_cusum", "cop_health_cusum_measured") for f, d in (
             ("tripped", _FLAG), ("evidence/#", _TEXT), ("last_fed", _AT0))},
         # The open-window detector's fit (#2241, Cusum._departure): None
         # until seeded; a cell no fit can hold drops the whole fit, which
@@ -353,8 +353,8 @@ DOMAINS: dict[str, dict[str, Domain | str]] = {
         "vent_cusum/reference": _ABSENT, "vent_cusum/reference/#": Domain("real", whole=_REFIT),
         "vent_cusum/reference_cov": _ABSENT, "vent_cusum/reference_cov/#": Domain(
             "real", -REFERENCE_PRIOR_COV, REFERENCE_PRIOR_COV, whole=_REFIT),
-        "cop_baseline/~": _TEXT, "cop_baseline/*/0": Domain("real", _POS),
-        "cop_baseline/*/1": Domain("int", 1),
+        "cop_baseline_measured/~": _TEXT, "cop_baseline_measured/*/0": Domain("real", _POS),
+        "cop_baseline_measured/*/1": Domain("int", 1),
         "immersion_events/#": _AT,
         "snow_accum_cm": _Z, "snow_accum_last": _AT0, "last_heavy_snow": _AT0,
         "capacity_envelope/~": Domain("int"), "capacity_envelope/*/0": Domain("real", _POS),
diff --git a/custom_components/heatpump_optimizer/strings.json b/custom_components/heatpump_optimizer/strings.json
index 7d48935ba..309a6610f 100644
--- a/custom_components/heatpump_optimizer/strings.json
+++ b/custom_components/heatpump_optimizer/strings.json
@@ -1174,6 +1174,9 @@
               "heat_pump_heat_energy_entity": "Heat pump heat energy meter (optional)",
               "heat_pump_power_entity": "Heat pump power meter (optional)",
               "heat_pump_thermal_power_entity": "Heat pump thermal power meter (optional)",
+              "heat_pump_power_source": "Heat pump power meter: meter or estimate",
+              "heat_pump_thermal_power_source": "Heat pump thermal power meter: meter or estimate",
+              "heat_meter_sees_dhw": "Heat reading covers hot water",
               "house_power_entity": "Whole-house power meter (optional)"
             },
             "data_description": {
@@ -1181,6 +1184,9 @@
               "heat_pump_heat_energy_entity": "A cumulative kWh meter of the heat the pump delivers, from a heat meter. It counts the heat over each hour, short compressor runs included, so it is used instead of the thermal power meter and the water flow sensor when set. With the energy meter it makes efficiency an observation, and the house heat-loss learner reads the heat that was actually delivered. A meter that also counts hot water is split by the operating mode entity, by the time the pump spent heating the house and the tank; without one, or in a combined mode, an hour that heated the tank is not read as space heating.",
               "heat_pump_power_entity": "Actual electrical draw. Without it the integration only knows what it asked the pump to do. With it, efficiency becomes measurable, predicted costs get a real counterpart to check against, and a wood furnace can be detected reliably. Watts or kilowatts both work.",
               "heat_pump_thermal_power_entity": "The heat the pump delivers, from a heat meter, in watts or kilowatts. With the power meter it makes efficiency an observation rather than an inference, and the house heat-loss learner and the capacity curve read the heat that was actually delivered. When set it is used instead of the water flow sensor.",
+              "heat_pump_power_source": "Whether the power meter is a real meter or a figure the pump or its integration estimates, such as an \"Estimated Power Draw\" sensor. Every learner trains on either; only metered heat over metered power is shown and graded as a measured COP. Auto reads an entity whose id contains \"estimat\" as an estimate.",
+              "heat_pump_thermal_power_source": "Whether the thermal power meter is a real heat meter or a figure the pump or its integration estimates, such as an \"Estimated Heating Output\" sensor. An estimate trains the learners but never makes a measured COP. Auto reads an entity whose id contains \"estimat\" as an estimate.",
+              "heat_meter_sees_dhw": "Turn on only if the heat energy meter or the thermal power meter also measures the heat sent to the hot-water tank, for example a meter ahead of the diverter valve. Off, hot-water runs record no measured COP.",
               "house_power_entity": "Total consumption at the meter. A capacity tariff is billed on the whole house, not on the heat pump alone, so without this the peak the optimizer avoids is only part of the real one."
             }
           },
@@ -1649,6 +1655,13 @@
         "control": "Control (turn the switch on and off)"
       }
     },
+    "meter_source": {
+      "options": {
+        "auto": "Auto (an id naming an estimate is one)",
+        "meter": "Meter (a measurement)",
+        "estimate": "Estimate (a vendor model)"
+      }
+    },
     "freq_control_mode": {
       "options": {
         "observe": "Observe (learn and recommend only)",
diff --git a/custom_components/heatpump_optimizer/thermal_model.py b/custom_components/heatpump_optimizer/thermal_model.py
index b873faaf3..e77657414 100644
--- a/custom_components/heatpump_optimizer/thermal_model.py
+++ b/custom_components/heatpump_optimizer/thermal_model.py
@@ -1267,6 +1267,9 @@ class InstallCapability:
     entity or sensor, read or write. ``measured_heat`` is a thermal power
     entity or a heat counter (fold e). ``heat_counter`` is the heat counter
     alone and ``electric_counter`` the electric counter its span divides by.
+    ``heat_estimated`` and ``power_estimated``: the heat and the electrical
+    figure a COP divides are a vendor's model, not a meter; ``heat_sees_dhw``:
+    the heat reading covers the hot-water circuit (``cop_measured``).
     (a), (c), (d) and (e) all read this probe.
     """
 
@@ -1276,12 +1279,47 @@ class InstallCapability:
     measured_heat: bool = False
     heat_counter: bool = False
     electric_counter: bool = False
+    heat_estimated: bool = False
+    power_estimated: bool = False
+    heat_sees_dhw: bool = False
 
     def cop_electric(self) -> bool:
         """An electrical figure a COP divides by: a heat counter's span reads
         the electric counter, every other reading the power entity (#2262)."""
         return self.electric_counter if self.heat_counter else self.measured_power
 
+    def cop_measured(self, dhw: bool) -> bool:
+        """Heat over electricity on this install is a measured COP.
+
+        Both sides metered, neither a vendor's model: estimated heat over
+        estimated power is the vendor's own fitted COP, and either one alone is
+        the model on that side. A hot-water interval also needs a heat reading
+        declared to see that circuit. The interval's own heat reading is the
+        caller's to check: this is what the install can measure at all.
+        """
+        return (
+            self.measured_heat
+            and self.cop_electric()
+            and not (self.heat_estimated or self.power_estimated)
+            and (self.heat_sees_dhw or not dhw)
+        )
+
+    def cop_sample(self, heat_kw: float | None, dhw: bool) -> bool | None:
+        """Whether one folded interval is a measured COP (R10-HOTFIX-COP-UNMEASURED).
+
+        ``True`` for an interval's heat reading where this install measures
+        that curve (``cop_measured``): recorded and graded. ``False`` for no
+        heat slot, or an estimate: the plan's inference or the vendor's fitted
+        COP trains the COP scale alone (tvofi, 2026-11-07: "Training on
+        estimated power should be good enough and better than nothing though
+        so retain that"). ``None`` -- refuse -- for a configured thermal power
+        that read no heat, unavailable or negative: a missing input, never an
+        inference.
+        """
+        if heat_kw is None:
+            return None if self.measured_heat and not self.heat_counter else False
+        return self.cop_measured(dhw)
+
     def can_duty_cycle(self) -> bool:
         """A sub-minimum average is realizable.
 
@@ -1360,9 +1398,26 @@ def probe_install(config: Any) -> InstallCapability:
         ),
         heat_counter=bool(cfg.get(const.CONF_HEAT_ENERGY_ENTITY)),
         electric_counter=bool(cfg.get(const.CONF_ENERGY_ENTITY)),
+        # A counter outranks the entity on its side, and is read as metered.
+        heat_estimated=not cfg.get(const.CONF_HEAT_ENERGY_ENTITY) and _estimated(
+            cfg.get(const.CONF_THERMAL_POWER_SOURCE, const.DEFAULT_METER_SOURCE),
+            cfg.get(const.CONF_THERMAL_POWER_ENTITY)),
+        power_estimated=not cfg.get(const.CONF_HEAT_ENERGY_ENTITY) and _estimated(
+            cfg.get(const.CONF_POWER_SOURCE, const.DEFAULT_METER_SOURCE),
+            cfg.get(const.CONF_POWER_ENTITY)),
+        heat_sees_dhw=bool(cfg.get(const.CONF_HEAT_METER_SEES_DHW, const.DEFAULT_HEAT_METER_SEES_DHW)),
     )
 
 
+def _estimated(source: Any, entity_id: Any) -> bool:
+    """Whether ``entity_id`` is a vendor's estimate, by its ``source`` answer (``CONF_POWER_SOURCE``)."""
+    if source == const.METER_SOURCE_ESTIMATE:
+        return True
+    if source == const.METER_SOURCE_METER:
+        return False
+    return const.ESTIMATE_ID_MARK in str(entity_id or "").lower()
+
+
 def flow_setpoint_driven(config: Any) -> bool:
     """The pump-duty arbiter drives the space circuit through a flow set-point.
 
diff --git a/custom_components/heatpump_optimizer/translations/en.json b/custom_components/heatpump_optimizer/translations/en.json
index 7d48935ba..309a6610f 100644
--- a/custom_components/heatpump_optimizer/translations/en.json
+++ b/custom_components/heatpump_optimizer/translations/en.json
@@ -1174,6 +1174,9 @@
               "heat_pump_heat_energy_entity": "Heat pump heat energy meter (optional)",
               "heat_pump_power_entity": "Heat pump power meter (optional)",
               "heat_pump_thermal_power_entity": "Heat pump thermal power meter (optional)",
+              "heat_pump_power_source": "Heat pump power meter: meter or estimate",
+              "heat_pump_thermal_power_source": "Heat pump thermal power meter: meter or estimate",
+              "heat_meter_sees_dhw": "Heat reading covers hot water",
               "house_power_entity": "Whole-house power meter (optional)"
             },
             "data_description": {
@@ -1181,6 +1184,9 @@
               "heat_pump_heat_energy_entity": "A cumulative kWh meter of the heat the pump delivers, from a heat meter. It counts the heat over each hour, short compressor runs included, so it is used instead of the thermal power meter and the water flow sensor when set. With the energy meter it makes efficiency an observation, and the house heat-loss learner reads the heat that was actually delivered. A meter that also counts hot water is split by the operating mode entity, by the time the pump spent heating the house and the tank; without one, or in a combined mode, an hour that heated the tank is not read as space heating.",
               "heat_pump_power_entity": "Actual electrical draw. Without it the integration only knows what it asked the pump to do. With it, efficiency becomes measurable, predicted costs get a real counterpart to check against, and a wood furnace can be detected reliably. Watts or kilowatts both work.",
               "heat_pump_thermal_power_entity": "The heat the pump delivers, from a heat meter, in watts or kilowatts. With the power meter it makes efficiency an observation rather than an inference, and the house heat-loss learner and the capacity curve read the heat that was actually delivered. When set it is used instead of the water flow sensor.",
+              "heat_pump_power_source": "Whether the power meter is a real meter or a figure the pump or its integration estimates, such as an \"Estimated Power Draw\" sensor. Every learner trains on either; only metered heat over metered power is shown and graded as a measured COP. Auto reads an entity whose id contains \"estimat\" as an estimate.",
+              "heat_pump_thermal_power_source": "Whether the thermal power meter is a real heat meter or a figure the pump or its integration estimates, such as an \"Estimated Heating Output\" sensor. An estimate trains the learners but never makes a measured COP. Auto reads an entity whose id contains \"estimat\" as an estimate.",
+              "heat_meter_sees_dhw": "Turn on only if the heat energy meter or the thermal power meter also measures the heat sent to the hot-water tank, for example a meter ahead of the diverter valve. Off, hot-water runs record no measured COP.",
               "house_power_entity": "Total consumption at the meter. A capacity tariff is billed on the whole house, not on the heat pump alone, so without this the peak the optimizer avoids is only part of the real one."
             }
           },
@@ -1649,6 +1655,13 @@
         "control": "Control (turn the switch on and off)"
       }
     },
+    "meter_source": {
+      "options": {
+        "auto": "Auto (an id naming an estimate is one)",
+        "meter": "Meter (a measurement)",
+        "estimate": "Estimate (a vendor model)"
+      }
+    },
     "freq_control_mode": {
       "options": {
         "observe": "Observe (learn and recommend only)",
diff --git a/custom_components/heatpump_optimizer/translations/sv.json b/custom_components/heatpump_optimizer/translations/sv.json
index a59596d56..ff90f39d4 100644
--- a/custom_components/heatpump_optimizer/translations/sv.json
+++ b/custom_components/heatpump_optimizer/translations/sv.json
@@ -1174,6 +1174,9 @@
               "heat_pump_heat_energy_entity": "Värmemängdsmätare för värmepumpen (valfritt)",
               "heat_pump_power_entity": "Effektmätare för värmepumpen (valfritt)",
               "heat_pump_thermal_power_entity": "Värmeeffektmätare för värmepumpen (valfritt)",
+              "heat_pump_power_source": "Värmepumpens effektmätare: mätare eller uppskattning",
+              "heat_pump_thermal_power_source": "Värmepumpens värmeeffektmätare: mätare eller uppskattning",
+              "heat_meter_sees_dhw": "Värmeavläsningen omfattar varmvatten",
               "house_power_entity": "Effektmätare för hela huset (valfritt)"
             },
             "data_description": {
@@ -1181,6 +1184,9 @@
               "heat_pump_heat_energy_entity": "En ackumulerande kWh-mätare för värmen pumpen levererar, från en värmemätare. Den räknar värmen över varje timme, korta kompressorkörningar inräknade, så den används i stället för värmeeffektmätaren och givaren för vattenflöde när den är vald. Tillsammans med energimätaren blir verkningsgraden en mätning, och husets värmeförlustinlärning läser den värme som faktiskt levererades. En mätare som också räknar varmvatten delas upp med driftlägesentiteten, efter den tid pumpen värmde huset och tanken; utan en sådan, eller i ett kombinerat läge, räknas inte en timme som värmde tanken som husvärme.",
               "heat_pump_power_entity": "Faktisk elförbrukning. Utan den vet integrationen bara vad den bad pumpen om. Med den blir verkningsgraden mätbar, de beräknade kostnaderna får något att stämmas av mot, och en vedpanna kan upptäckas säkert. Både watt och kilowatt fungerar.",
               "heat_pump_thermal_power_entity": "Värmen pumpen levererar, från en värmemätare, i watt eller kilowatt. Tillsammans med effektmätaren blir verkningsgraden en mätning i stället för en slutsats, och husets värmeförlustinlärning och kapacitetskurvan läser den värme som faktiskt levererades. När den är vald används den i stället för givaren för vattenflöde.",
+              "heat_pump_power_source": "Om effektmätaren är en verklig mätare eller ett värde som pumpen eller dess integration uppskattar, till exempel en sensor för \"Estimated Power Draw\". All inlärning tränar på båda; bara uppmätt värme genom uppmätt effekt visas och betygsätts som uppmätt COP. Auto läser en entitet vars id innehåller \"estimat\" som en uppskattning.",
+              "heat_pump_thermal_power_source": "Om värmeeffektmätaren är en verklig värmemätare eller ett värde som pumpen eller dess integration uppskattar, till exempel en sensor för \"Estimated Heating Output\". En uppskattning tränar inlärningen men ger aldrig en uppmätt COP. Auto läser en entitet vars id innehåller \"estimat\" som en uppskattning.",
+              "heat_meter_sees_dhw": "Slå på bara om värmemängdsmätaren eller värmeeffektmätaren även mäter värmen till varmvattenberedaren, till exempel en mätare före växelventilen. Avstängd ger varmvattenkörningar ingen uppmätt COP.",
               "house_power_entity": "Total förbrukning vid mätaren. Effekttariff debiteras på hela huset, inte bara på värmepumpen, så utan denna är den topp optimeraren undviker bara en del av den verkliga."
             }
           },
@@ -1636,6 +1642,13 @@
         "control": "Styra (slå på och av brytaren)"
       }
     },
+    "meter_source": {
+      "options": {
+        "auto": "Auto (ett id som anger en uppskattning är en)",
+        "meter": "Mätare (en mätning)",
+        "estimate": "Uppskattning (en tillverkarmodell)"
+      }
+    },
     "freq_control_mode": {
       "options": {
         "observe": "Observera (lär och rekommendera enbart)",
diff --git a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
index 9073a1716..1803bfeaa 100644
--- a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
+++ b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
@@ -209,8 +209,9 @@ const STRINGS = {
     "health.model_unobservable": "Not observable without a power meter.",
     "health.cop_measured": "Measured {age} ago.",
     "health.cop_reason_heat_metered": "Measured by the heat meter.",
-    "health.cop_reason_draw_follows_plan": "Read from the power draw, which follows the plan.",
-    "health.cop_reason_not_measurable": "Not measurable here: without a heat meter the power draw does not follow the plan closely enough to read efficiency from.",
+    "health.cop_reason_not_measurable": "COP cannot be measured on this install: it has no heat reading, and without one the efficiency shown is the model's own. A heat energy meter or a thermal power meter covering the heating circuit, hot water included, would measure it.",
+    "health.cop_reason_estimated_inputs": "COP cannot be measured on this install: its power or heat reading is the pump's own estimate, so heat over power is the vendor model's COP. A real heat meter and power meter, the hot-water circuit included, would measure it.",
+    "health.cop_reason_no_heat_reading": "The heat meter gave no usable reading in the interval.",
     "health.cop_reason_awaiting_draw_evidence": "Waiting to see whether the power draw follows the plan.",
     "health.cop_reason_no_electric_meter": "Needs a power or energy meter on the heat pump.",
     "health.cop_reason_no_measured_power": "Waiting for a power reading from the heat pump.",
@@ -845,11 +846,13 @@ const STRINGS = {
       "era. 50 is typical for that type and era; above is tighter, below " +
       "leakier. Never 0 — that is only for no data.",
     "score.part_machine":
-      "Heat pump: the measured COP — heat delivered per kWh of electricity " +
-      "— in each 3 °C outdoor band, against the pump's own history in that " +
-      "band. 100 is matching its history; each point below is a lasting " +
-      "COP shortfall (see the COP health diagnostics). A band is watched " +
-      "once it holds 20 samples; no grade yet means no band does — not a zero.",
+      "Heat pump: the measured COP — heat delivered per kWh of electricity, " +
+      "from a heat meter over a power meter, neither an estimate — in each " +
+      "3 °C outdoor band, against the pump's own history in that band. 100 " +
+      "is matching its history; each point below is a lasting COP shortfall " +
+      "(see the COP health diagnostics). A band is watched once it holds 20 " +
+      "samples; no grade yet means no band does — not a zero. Without a " +
+      "metered heat reading there is no grade at all.",
     "score.part_operation":
       "Driving: whether the plan buys at the cheap hours. Each day's " +
       "energy is priced against that day's flat mean spot price — buying " +
@@ -864,6 +867,8 @@ const STRINGS = {
     "score.reason_heat_loss_refit_disagrees":
       "The learned heat loss disagrees with recent days; a refit is on offer.",
     "score.reason_cop_watch_learning": "Not enough COP data yet to watch the heat pump.",
+    "score.reason_cop_unmeasurable":
+      "COP cannot be measured on this install, so the heat pump is not graded: it needs a heat energy meter or a thermal power meter covering the heating circuit, hot water included, and a power meter, neither an estimate.",
     "score.reason_no_scored_day": "Waiting for the first scored day.",
     "score.reason_free_price_reset":
       "Reset after a run of free-price days; waiting for a priced day.",
@@ -1094,8 +1099,9 @@ const STRINGS = {
     "health.model_unobservable": "Går inte att observera utan effektmätare.",
     "health.cop_measured": "Mätt för {age} sedan.",
     "health.cop_reason_heat_metered": "Mätt med värmemängdsmätaren.",
-    "health.cop_reason_draw_follows_plan": "Avläst från effektuttaget, som följer planen.",
-    "health.cop_reason_not_measurable": "Går inte att mäta här: utan värmemängdsmätare följer effektuttaget inte planen tillräckligt nära för att verkningsgraden ska kunna avläsas.",
+    "health.cop_reason_not_measurable": "COP går inte att mäta i den här installationen: den saknar värmeavläsning, och utan en sådan är verkningsgraden modellens egen. En värmemängdsmätare eller värmeeffektmätare som omfattar värmekretsen, varmvattnet inräknat, skulle mäta den.",
+    "health.cop_reason_estimated_inputs": "COP går inte att mäta i den här installationen: dess effekt- eller värmeavläsning är pumpens egen uppskattning, så värme genom effekt är tillverkarmodellens COP. En verklig värmemätare och effektmätare, varmvattenkretsen inräknad, skulle mäta den.",
+    "health.cop_reason_no_heat_reading": "Värmemätaren gav ingen användbar avläsning under intervallet.",
     "health.cop_reason_awaiting_draw_evidence": "Väntar på att se om effektuttaget följer planen.",
     "health.cop_reason_no_electric_meter": "Behöver en effekt- eller energimätare på värmepumpen.",
     "health.cop_reason_no_measured_power": "Väntar på en effektavläsning från värmepumpen.",
@@ -1696,11 +1702,13 @@ const STRINGS = {
       "byggperioden. 50 är typiskt för den typen och perioden; över är " +
       "tätare, under läckigare. Aldrig 0 — det betyder bara inget underlag.",
     "score.part_machine":
-      "Värmepumpen: uppmätt COP — levererad värme per kWh el — i varje " +
-      "utomhusband om 3 °C, mot pumpens egen historik i det bandet. 100 är " +
-      "som historiken; varje poäng under är ett bestående COP-underskott " +
-      "(se COP-hälsodiagnostiken). Ett band bevakas när det har 20 prov; " +
-      "inget betyg ännu betyder att inget band har det — inte noll.",
+      "Värmepumpen: uppmätt COP — levererad värme per kWh el, från en " +
+      "värmemätare genom en effektmätare, ingen av dem en uppskattning — i " +
+      "varje utomhusband om 3 °C, mot pumpens egen historik i det bandet. " +
+      "100 är som historiken; varje poäng under är ett bestående " +
+      "COP-underskott (se COP-hälsodiagnostiken). Ett band bevakas när det " +
+      "har 20 prov; inget betyg ännu betyder att inget band har det — inte " +
+      "noll. Utan uppmätt värme finns inget betyg alls.",
     "score.part_operation":
       "Körningen: om planen köper på de billiga timmarna. Varje dags " +
       "energi prissätts mot dagens platta medelspotpris — 20 % under platt " +
@@ -1713,6 +1721,8 @@ const STRINGS = {
     "score.reason_heat_loss_refit_disagrees":
       "Den inlärda värmeförlusten stämmer inte med de senaste dagarna; en omanpassning erbjuds.",
     "score.reason_cop_watch_learning": "Ännu för lite COP-data för att bevaka värmepumpen.",
+    "score.reason_cop_unmeasurable":
+      "COP går inte att mäta i den här installationen, så värmepumpen betygsätts inte: det krävs en värmemängdsmätare eller värmeeffektmätare som omfattar värmekretsen, varmvattnet inräknat, och en effektmätare, ingen av dem en uppskattning.",
     "score.reason_no_scored_day": "Väntar på den första bedömda dagen.",
     "score.reason_free_price_reset":
       "Nollställd efter en rad dagar med gratis el; väntar på en dag med pris.",
@@ -9814,16 +9824,16 @@ function copState(cop) {
   const words = (code) => (STRINGS.en[`health.cop_reason_${code}`] !== undefined ? L(`health.cop_reason_${code}`) : null);
   const scale = readNumber(c.scale);
   if (c.alarm) return { value: L("health.model_cop_low"), reason: L("health.model_cop_alarm"), tone: "warn", watched: true };
-  if (obs === "not_measurable" || obs === "no_electric_meter") {
+  if (obs === "not_measurable" || obs === "no_electric_meter" || obs === "estimated_inputs") {
     return { value: "—", reason: words(obs), tone: "ok", watched: false };
   }
   if (readNumber(c.watched_buckets) > 0 && scale !== null) {
-    const source = obs === "heat_metered" || obs === "draw_follows_plan" ? words(obs) : "";
+    const source = obs === "heat_metered" ? words(obs) : "";
     return { value: L("health.model_cop_normal", { v: scale.toFixed(2) }),
       reason: [L("health.model_cop_fine"), source].filter(Boolean).join(" "), tone: "ok", watched: true };
   }
   return { value: "—", tone: "ok", watched: false,
-    reason: words(c.cop_refusal) || (obs === "awaiting_draw_evidence" && words(obs)) || scoreReasonText("cop_watch_learning") };
+    reason: words(c.cop_refusal) || scoreReasonText("cop_watch_learning") };
 }
 
 /** "What the model has learned" (R9-UX-7): the model status sensor's rows. */
diff --git a/dev/audit/rounds/round3/D5/option_doc_coverage.py b/dev/audit/rounds/round3/D5/option_doc_coverage.py
index 92a7f8899..1aa07703b 100644
--- a/dev/audit/rounds/round3/D5/option_doc_coverage.py
+++ b/dev/audit/rounds/round3/D5/option_doc_coverage.py
@@ -92,14 +92,17 @@ EXPECTED on this tree (ae36eff printed option_fields_rendered=174 and
     its row in docs/configuration.md in the same commit. R10-WOOD-NOTIFY
     moved them once more, 203 -> 204 and 236 -> 237: the wood lighting lead
     time on the wood page, with its row in docs/configuration.md in the same
-    commit. This block is an
+    commit. R10-HOTFIX-COP-UNMEASURED moved them once more, 204 -> 207 and
+    237 -> 240: the power and thermal power meter source selects and the
+    hot-water coverage switch on the entities_metering page, with their rows
+    in docs/configuration.md in the same commit. This block is an
     ASSERTION `tests/harness_headers.py` executes the script against, and it
     is reached by a shell-out the closure recorder cannot see, so it does not
     go red on a pull request: it is re-measured in the commit that changes
     what the script prints, or main's forced-full run finds it):
-    RESULT option_fields_rendered=204 count
+    RESULT option_fields_rendered=207 count
     RESULT option_fields_undocumented=0 count
-    RESULT option_schema_keys_rendered=237 count
+    RESULT option_schema_keys_rendered=240 count
     RESULT wood_economics_fields_rendered=4 count
     RESULT wood_economics_doc_lines=8 count      (tolerance: exact;
     moved 6 -> 8 by #1645/F8.1: the Services section's `simulate_plan`
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index 447994fad..71201ad5d 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -1118,9 +1118,9 @@
  {
   "id": "C125",
   "source": "strings.json:selector",
-  "claim": "every SelectSelector option on every options page has a translated label (45 selects)",
+  "claim": "every SelectSelector option on every options page has a translated label (47 selects)",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "45 selects, untranslated=[]",
+  "result": "47 selects, untranslated=[]",
   "verdict": "true",
   "truth": ""
  }
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index 30491f447..5c125a778 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -128,4 +128,4 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C122 | `docs/configuration.md` | set_mode takes auto, comfort, economy, boost or off | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['auto', 'boost', 'comfort', 'economy', 'off'] measured=['auto', 'boost', 'comfort', 'economy', 'off'] | **true** |  |
 | C123 | `DISCLAIMER.md` | the licence is MIT | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=True measured=True | **true** |  |
 | C124 | `DISCLAIMER.md` | the disclaimer states the software is not a safety device and carries no warranty | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 'not a safety device' present=True, 'no warranty' present=True | **true** |  |
-| C125 | `strings.json:selector` | every SelectSelector option on every options page has a translated label (45 selects) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 45 selects, untranslated=[] | **true** |  |
+| C125 | `strings.json:selector` | every SelectSelector option on every options page has a translated label (47 selects) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 47 selects, untranslated=[] | **true** |  |
diff --git a/dev/programme/delivery/3297.md b/dev/programme/delivery/3297.md
new file mode 100644
index 000000000..cbfba9897
--- /dev/null
+++ b/dev/programme/delivery/3297.md
@@ -0,0 +1 @@
+- [#3297](https://github.com/tvofi/heatpump_optimizer/pull/3297) — **open**, R10-HOTFIX-COP-UNMEASURED: hotfix cop unmeasured (R10-HOTFIX-COP-UNMEASURED)
diff --git a/docs/configuration.md b/docs/configuration.md
index 3bb603b97..4165c54f1 100644
--- a/docs/configuration.md
+++ b/docs/configuration.md
@@ -626,10 +626,13 @@ are on **Power and solar sensors**; mode / defrost / online / fault are on
 | Solar radiation sensor | the setup value | an irradiance sensor | As on [Optional sensors](#2--optional-sensors). |
 | Solar irradiance source | Weather entity | Weather entity / Open-Meteo | As on Optional sensors. |
 | Solar irradiance location | your Home Assistant home location | a coordinate | As on Optional sensors. Only used with Open-Meteo. |
-| Heat pump power meter | none | a `power` sensor | Actual electrical draw. A figure the pump estimates for itself is read the same way as a meter, so prefer a real one ([why](how-it-works.md#the-house-heat-loss-coefficient)). With it, efficiency becomes measurable, predicted cost gets a real counterpart, and a wood fire is detected reliably. Several sensors stay unavailable without it. |
+| Heat pump power meter | none | a `power` sensor | Actual electrical draw. A figure the pump estimates for itself trains the learners the same way as a meter, so prefer a real one ([why](how-it-works.md#the-house-heat-loss-coefficient)); it never makes a measured COP (the next row). With it, predicted cost gets a real counterpart, predicted cost gets a real counterpart, and a wood fire is detected reliably. Several sensors stay unavailable without it. |
 | Heat pump thermal power meter | none | a `power` sensor in W or kW | The heat the pump delivers, from a heat meter. Published as `measured_heat_output_kw` on the Recommended Power sensor. With the power meter, COP is measured (heat over electricity) rather than inferred from the commanded draw, and the efficiency scale is judged at the supply temperature the pump actually ran at when a supply sensor is mapped, so it stops absorbing weather-driven lift as wear. The house heat-loss and lower-floor learners replay the measured heat for a space-heating interval, and the capacity curve takes it at every load as a floor (it may raise a bucket; only near-nameplate intervals count towards capping). When set it replaces the water flow sensor's estimate, also in a cycle where its own reading is unusable, and an unusable reading pauses the learners that read it. |
+| Heat pump power meter: meter or estimate (`heat_pump_power_source`) | auto | auto, meter or estimate | Whether the power meter measures or is the pump's own estimate (an "Estimated Power Draw" sensor). Auto reads an entity whose id contains `estimat` as an estimate. An estimate trains every learner as a meter does, but heat over estimated power is the vendor model's COP, so no COP is shown as measured and the heat pump is not graded. |
+| Heat pump thermal power meter: meter or estimate (`heat_pump_thermal_power_source`) | auto | auto, meter or estimate | The same answer for the thermal power meter (an "Estimated Heating Output" sensor is an estimate). |
 | Heat pump energy meter | none | an `energy` sensor | A cumulative kWh meter is more accurate than adding up power readings, which misses short runs. |
 | Heat pump heat energy meter | none | an `energy` sensor in Wh, kWh or MWh | A cumulative kWh meter of the heat the pump delivers. It is read over each span of about an hour, so short compressor runs count, and when set it is used instead of the thermal power meter and the water flow sensor. With the energy meter on the same read instants, efficiency is measured as heat over electricity for the span; the house heat-loss learner replays the heat that was delivered. A span whose counter went backwards (a meter reset), jumped past the pump's nameplate, or whose counter resolution is too coarse for the heat expected in it is not learned from. A meter that also counts hot water is split by the operating mode entity, by the time the pump spent in each mode; without that entity, or in a combined mode, the split falls back to the plan's, and an hour that heated the tank is not read as space heating. |
+| Heat reading covers hot water (`heat_meter_sees_dhw`) | off | on or off | Turn on only if the heat energy meter, or else the thermal power meter, also measures the heat sent to the hot-water tank (a meter ahead of the diverter valve). Off, a hot-water interval records no measured COP. A measured COP, and the heat pump grade, need metered heat over metered power; without a heat reading at all the Health tab says COP cannot be measured on this install. |
 | Whole-house power meter | none | a `power` sensor | A capacity tariff is billed on the whole house, so without this the peak being avoided is only part of the real one. |
 | Compressor frequency entity | none | a `number` entity | Typically from Modbus or ESPHome. With it the optimizer learns a kW-per-Hz map and recommends a frequency. |
 | Actual frequency sensor | none | a `frequency` sensor | Many number entities are setpoint registers that echo the last written value. Read from an echo, the watchdog can never see divergence. Leave empty only if the number entity genuinely tracks the machine. Without a number entity, this sensor alone is enough to observe. |
diff --git a/tests/card.mjs b/tests/card.mjs
index dbf3c1b1a..9e858b29d 100644
--- a/tests/card.mjs
+++ b/tests/card.mjs
@@ -5898,7 +5898,7 @@ function ctxL(card, key) {
   // grade the input does not carry.
   const CODES = {
     envelope: ["no_house_model", "heat_loss_learning", "heat_loss_refit_disagrees"],
-    machine: ["cop_watch_learning"],
+    machine: ["cop_unmeasurable", "cop_watch_learning"],
     operation: ["no_scored_day", "free_price_reset"],
   };
   const LABEL = { envelope: "House", machine: "Heat pump", operation: "Driving" };
@@ -12415,9 +12415,15 @@ check("without an indoor reading the corner now label is absent",
     const both = copRow({ scale: 1.0, watched_buckets: 0, cop_observability: "awaiting_draw_evidence", cop_refusal: "duty_floor" });
     check("UX-HEALTH E: the learner's own refusal is said before the gate's wait for draw evidence",
       /ran too little/.test(both) && !/Waiting to see whether/.test(both), both);
-    const awaiting = copRow({ scale: 1.0, watched_buckets: 0, cop_observability: "awaiting_draw_evidence" });
-    check("UX-HEALTH E: with no refusal the gate's wait for draw evidence is said",
-      /Waiting to see whether the power draw follows the plan/.test(awaiting), awaiting);
+    // R10-HOTFIX-COP-UNMEASURED: no heat reading, or an estimated input, is
+    // said as never measurable here, not as data still to come.
+    const noHeat = copRow({ scale: 1.0, watched_buckets: 0, cop_observability: "not_measurable",
+      cop_refusal: "awaiting_draw_evidence" });
+    const estimated = copRow({ scale: 1.0, watched_buckets: 0, cop_observability: "estimated_inputs" });
+    check("UX-HEALTH E: a COP this install cannot measure says so and names what would measure it, never 'not enough data yet'",
+      /COP cannot be measured on this install: it has no heat reading/.test(noHeat)
+      && /COP cannot be measured on this install: its power or heat reading is the pump's own estimate/.test(estimated)
+      && ![noHeat, estimated].some((row) => /Not enough COP data yet/.test(row)), `${noHeat}\n${estimated}`);
     const aged = copRow({ scale: 0.97, watched_buckets: 2, measured_cop_at: new Date(FROZEN - 2 * 3600e3).toISOString() });
     check("UX-HEALTH E: the latched COP shows its age", /Measured 2 h ago/.test(aged), aged);
     check("UX-HEALTH E: a watched COP still reads Normal (null control)",
@@ -12429,7 +12435,7 @@ check("without an indoor reading the corner now label is absent",
     const nmPage = pageOf(mkHealth(nm).html());
     const learnCop = (/Heat pump COP<span class="adv-sub">([^<]*)</.exec(nmPage) || [])[1] || "";
     check("UX-HEALTH E: the learning row says the same COP reason as the model row",
-      /^Not measurable here/.test(learnCop) && !/Needs a power meter/.test(nmPage), learnCop);
+      /^COP cannot be measured on this install/.test(learnCop) && !/Needs a power meter/.test(nmPage), learnCop);
     // Every code the COP gate and the heat counter publish has words in both
     // languages; the count is asserted non-zero so a grep miss cannot pass.
     const pySrc = ["accuracy.py", "heat_energy.py"].map((f) => fs.readFileSync(`custom_components/heatpump_optimizer/${f}`, "utf8")).join("\n");
diff --git a/tests/entities.py b/tests/entities.py
index b89f597f3..6100a7827 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -6199,9 +6199,10 @@ R.check(
     == "measured_power_entity",
 )
 
-# R10-COP-GATE (#2262): where the draw does not follow the plan's ask and no
-# heat reading exists, a latched COP is no reading of this install: the sensor
-# waits for a heat meter instead of showing it. A heat counter's open span is
+# R10-COP-GATE (#2262), R10-HOTFIX-COP-UNMEASURED: where no heat reading
+# exists, or either reading is a vendor's estimate, a latched COP is no reading
+# of this install: the sensor waits for a heat meter, or for metered inputs,
+# instead of showing it. A heat counter's open span is
 # its own code beside a measured COP, never a refusal, and the latch's time
 # rides with it.
 _cg_cop = {
@@ -6210,7 +6211,7 @@ _cg_cop = {
         "cop_refusal": "span_open" if obs == "heat_metered" else "draw_off_ask",
         "measured_cop_at": "2026-10-24T03:00:00+00:00",
     }), ENTRY)
-    for obs in ("not_measurable", "heat_metered", "draw_follows_plan")
+    for obs in ("not_measurable", "heat_metered", "estimated_inputs")
 }
 _cg_view = {
     obs: (ent.available, ent.extra_state_attributes.get("waiting_for"),
@@ -6219,13 +6220,13 @@ _cg_view = {
     for obs, ent in _cg_cop.items()
 }
 R.check(
-    "a COP not measurable here waits for a heat meter; a heat-metered COP "
-    "between span closes stays measured with span_open as its code; a draw "
-    "that follows the plan keeps its COP (null); each carries its fold time",
+    "a COP not measurable here waits for a heat meter, one from estimated "
+    "inputs for metered ones; a heat-metered COP between span closes stays "
+    "measured with span_open as its code (null); each carries its fold time",
     _cg_view == {
         "not_measurable": (False, "heat_meter", "draw_off_ask", "2026-10-24T03:00:00+00:00"),
         "heat_metered": (True, None, "span_open", "2026-10-24T03:00:00+00:00"),
-        "draw_follows_plan": (True, None, "draw_off_ask", "2026-10-24T03:00:00+00:00"),
+        "estimated_inputs": (False, "metered_inputs", "draw_off_ask", "2026-10-24T03:00:00+00:00"),
     },
     f"{_cg_view!r}",
 )
diff --git a/tests/features.py b/tests/features.py
index c08b186ca..ea9349688 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -8187,8 +8187,27 @@ R.check(
 from heatpump_optimizer.accuracy import MeasuredCop as _CopRecord  # noqa: E402
 
 
+from heatpump_optimizer.thermal_model import InstallCapability as _cg_cap  # noqa: E402
+
+
 class _CopGate:
-    _learn_measured_cop = Coord._learn_measured_cop
+    #: R10-HOTFIX-COP-UNMEASURED: this stub has no heat reading, so the fold
+    #: records nothing as measured. ``as_measured`` hands the fold's tail an
+    #: interval it treats as a measured one, for the checks that pin what the
+    #: tail credits a measured sample; which samples are measured is pinned on
+    #: the real coordinator (that section's checks).
+    as_measured = False
+
+    def _learn_measured_cop(self, draw=None):
+        if not self.as_measured:
+            return Coord._learn_measured_cop(self, draw)
+        saved = _cg_cap.cop_sample
+        _cg_cap.cop_sample = lambda cap, heat_kw, dhw: True
+        try:
+            return Coord._learn_measured_cop(self, draw)
+        finally:
+            _cg_cap.cop_sample = saved
+
     _fold_measured_cop = Coord._fold_measured_cop
     _fold_cop_evidence = Coord._fold_cop_evidence
     _commanded_power = Coord._commanded_power
@@ -8205,6 +8224,7 @@ class _CopGate:
         # all, and this fixture is about the frost-band *split*, not the
         # magnitude — it has to stay on the efficiency side of that gate.
         self._measured_power = 2.6
+        self._config = {}  # no heat slot: probe_install's empty install
         self._current_action = dict(action) if action else {"power": 3.0}
         # v5.3.0: with no mode entity the signals are the full-capability
         # default, which masks nothing and selects the space curve — the
@@ -23752,7 +23772,10 @@ R.check(
     and _ce1_lossless["reasons"]["envelope"] == "no_house_model",
     f"massless {_ce1_massless} lossless {_ce1_lossless}",
 )
-_cmach = _t2_coord()
+# R10-HOTFIX-COP-UNMEASURED: a grade needs an install that measures its COP,
+# metered heat over metered power; the grading fixtures below carry one.
+_CMACH_METERED = {"heat_pump_power_entity": "sensor.hp_power", "heat_pump_thermal_power_entity": "sensor.heat_kw"}
+_cmach = _t2_coord(**_CMACH_METERED)
 R.check(
     "no COP evidence means no machine grade, not a failing one",
     _cmach._scores_view(_rs_advice(_cmach))["machine"] is None,
@@ -23761,7 +23784,7 @@ R.check(
 # so a bucket at exactly that count is watched; one short of it is not.
 _cmach_edge = {}
 for _cmach_n in (COP_BASELINE_MIN_SAMPLES - 1, COP_BASELINE_MIN_SAMPLES):
-    _cmach_c = _t2_coord()
+    _cmach_c = _t2_coord(**_CMACH_METERED)
     _cmach_c._cop_baseline[(3, False)] = [3.0, _cmach_n]
     _cmach_edge[_cmach_n] = _cmach_c._scores_view(_rs_advice(_cmach_c))["machine"]
 R.check(
@@ -23784,7 +23807,7 @@ R.check(
     "a machine past the alarm threshold still grades 0, never below (#2258)",
     _cmach._scores_view(_rs_advice(_cmach))["machine"] == 0.0,
 )
-_cedge = _t2_coord()
+_cedge = _t2_coord(**_CMACH_METERED)
 _cedge._cop_baseline[(3, False)] = [3.0, COP_BASELINE_MIN_SAMPLES]
 _cedge_view = _cedge._scores_view(_rs_advice(_cedge))
 R.check(
@@ -23957,17 +23980,22 @@ R.check(
 )
 _fresh6_c = _t2_coord()
 _fresh6 = _fresh6_c._scores_view(_rs_advice(_fresh6_c))
+_fresh6_m = _t2_coord(**_CMACH_METERED)
+_fresh6_mv = _fresh6_m._scores_view(_rs_advice(_fresh6_m))
 R.check(
-    "a fresh install grades nothing, and says why for each part (#2258)",
+    "a fresh install grades nothing, and says why for each part (#2258): with "
+    "no heat reading the heat pump is never graded (R10-HOTFIX-COP-UNMEASURED); "
+    "a metered one is still learning",
     _fresh6["machine"] is None
     and _fresh6["operation"] is None
     and _fresh6["overall"] is None
     and _fresh6["envelope"] is None
     and _fresh6["reasons"] == {
-        "envelope": "heat_loss_learning", "machine": "cop_watch_learning",
+        "envelope": "heat_loss_learning", "machine": "cop_unmeasurable",
         "operation": "no_scored_day", "overall": "first_scored_day",
-    },
-    f"{_fresh6}",
+    }
+    and _fresh6_mv["machine"] is None and _fresh6_mv["reasons"]["machine"] == "cop_watch_learning",
+    f"{_fresh6} / {_fresh6_mv['reasons']}",
 )
 
 # --- R10-GRADE-DRIVERS: the heat-pump and Driving grades publish drivers in
@@ -23983,7 +24011,7 @@ R.check(
     and _fresh6["machine_evidence"] == {"required": 20, "bands": [], "refused_frozen": 0},
     f"{_fresh6}",
 )
-_gd_m = _t2_coord()
+_gd_m = _t2_coord(**_CMACH_METERED)
 _gd_m._cop_baseline[(-1, False)] = [3.1, 12]
 _gd_m._cop_baseline[(0, True)] = [2.4, 5]
 _gd_m._measured_power = 1.0
@@ -24266,7 +24294,7 @@ R.check(
 
 # The machine counts the buckets the Health tab counts: a non-finite sample
 # count is no evidence, never a raise and never a watched bucket.
-_sc_m = _t2_coord()
+_sc_m = _t2_coord(**_CMACH_METERED)
 _sc_m._cop_baseline[(3, False)] = [3.0, float("nan")]
 _sc_mv = _sc_view(_sc_m)
 R.check(
@@ -31788,23 +31816,24 @@ _dhw_action = {"power": 0.0, "dhw_power": 3.0}
 _cop_dhw = _CopGate(outdoor=8.0, signals=_DHW_ONLY, action=_dhw_action)
 _cop_dhw._current_state.dhw_temperature = 55.0
 _cop_dhw._learn_measured_cop()
+# With no heat slot neither interval is a measured COP (R10-HOTFIX-COP-
+# UNMEASURED), so the curve each is judged against is read where the fold
+# takes it, and both still trained the scale.
+_cop_space_ref = _cop_space._cop_reference_curve()
+_cop_dhw_ref = _cop_dhw._cop_reference_curve()
 R.check(
     "a hot-water interval is judged against the DHW curve",
-    _cop_dhw._measured_cop.cop is not None
-    and _cop_dhw._measured_cop.cop < _cop_space._measured_cop.cop,
-    f"dhw {_cop_dhw._measured_cop.cop} vs space {_cop_space._measured_cop.cop}",
-)
-_expected_dhw_cop = _cop_space._measured_cop.cop * (
-    _cop_dhw._thermal_model.compute_cop_dhw(8.0, 55.0)
-    / _cop_dhw._thermal_model.compute_cop(8.0)
+    _cop_dhw_ref[1] is True and _cop_space_ref[1] is False
+    and _cop_dhw_ref[0] < _cop_space_ref[0]
+    and _cop_dhw._cop_samples == 1 and _cop_space._cop_samples == 1,
+    f"dhw {_cop_dhw_ref} vs space {_cop_space_ref}",
 )
 R.check(
     "and the gap is exactly the model's own DHW law at the tank's "
     "temperature, not a fudge",
-    abs(_cop_dhw._measured_cop.cop - round(_expected_dhw_cop, 2)) <= 0.02,
-    f"{_cop_dhw._measured_cop.cop} vs {round(_expected_dhw_cop, 2)} "
-    f"(the law's ratio at 8 °C / 55 °C is "
-    f"{_cop_dhw._thermal_model.compute_cop_dhw(8.0, 55.0) / _cop_dhw._thermal_model.compute_cop(8.0):.4f})",
+    _cop_dhw_ref == (_cop_dhw._thermal_model.compute_cop_dhw(8.0, 55.0), True, 55.0)
+    and _cop_space_ref[0] == _cop_dhw._thermal_model.compute_cop(8.0),
+    f"{_cop_dhw_ref} vs {_cop_dhw._thermal_model.compute_cop_dhw(8.0, 55.0)}",
 )
 R.check(
     "the reported COP for a healthy pump on the space curve is unchanged",
@@ -31846,6 +31875,7 @@ R.check(
 # re-pointed the residual's reference while leaving the stored COP alone — and
 # in HEATDHW with an even split that is every cycle on the target hardware.
 _cop_pair = _CopGate(outdoor=8.0, signals=_DHW_ONLY, action=_dhw_action)
+_cop_pair.as_measured = True
 _cop_pair._current_state.dhw_temperature = 55.0
 _cop_pair._learn_measured_cop()
 _cop_pair_cop = _cop_pair._measured_cop.cop
@@ -32094,6 +32124,7 @@ _EH_NIGHT_SIG = pump_signals.PumpSignals(
 )
 
 _eh_cop_ok = _CopGate(outdoor=8.0)
+_eh_cop_ok.as_measured = True
 _eh_cop_ok._learn_measured_cop()
 R.check(
     "the control: the same interval with no electric-heat evidence folds",
@@ -32537,6 +32568,7 @@ def _fl_model1_gate(outdoor, supply_phys, mapped):
     commanded = 3.0
     measured = commanded * c0 / ct
     gate = _CopGate(outdoor=outdoor, action={"power": commanded})
+    gate.as_measured = True
     gate._measured_power = measured
     # A persistent ratio, not a blip: the tracking gate judges against it.
     gate._cop_ratio_ewma = measured / commanded
@@ -32948,6 +32980,7 @@ R.check(
 # priced C0 x L(curve + bias); the credit must still be Ct exactly.
 def _g3_credit(supply_phys):
     gate = _CopGate(outdoor=-3.0, action={"power": 3.0})
+    gate.as_measured = True
     gate._thermal_params = ThermalParameters.from_config({_G3_KEY: True, **_G3_HOT})
     gate._thermal_params.flow_curve_bias = 5.0
     gate._thermal_model = ThermalModel(gate._thermal_params)
@@ -33103,12 +33136,12 @@ R.check(
     and not _g3_tog._cop_health_cusum.tripped,
     f"{_g3_tog._cop_baseline}, tripped={_g3_tog._cop_health_cusum.tripped}",
 )
-_g3_saved = _g3_tog._thermal_learning_payload()["cop_baseline"]
+_g3_saved = _g3_tog._thermal_learning_payload()["cop_baseline_measured"]
 _g3_back = _g3_watch(True)
 
 
 async def _g3_fake_load():
-    return {"cop_baseline": _g3_saved}
+    return {"cop_baseline_measured": _g3_saved}
 
 
 _g3_back._thermal_learning_store.async_load = _g3_fake_load
@@ -33120,7 +33153,7 @@ _g3_old = _g3_watch(True)
 
 
 async def _g3_old_load():
-    return {"cop_baseline": {"2": [3.1, 25], "2:dhw": [2.6, 25], "2:zzz": [9.0, 9]}}
+    return {"cop_baseline_measured": {"2": [3.1, 25], "2:dhw": [2.6, 25], "2:zzz": [9.0, 9]}}
 
 
 _g3_old._thermal_learning_store.async_load = _g3_old_load
@@ -36590,8 +36623,10 @@ R.check(
 # curve it used. Separate baselines are worthless if every sample arrives
 # labelled "space".
 _hw_gate_space = _CopGate(outdoor=8.0)
+_hw_gate_space.as_measured = True
 _hw_gate_space._learn_measured_cop()
 _hw_gate_dhw = _CopGate(outdoor=8.0, signals=_DHW_ONLY, action=_dhw_action)
+_hw_gate_dhw.as_measured = True
 _hw_gate_dhw._current_state.dhw_temperature = 55.0
 _hw_gate_dhw._learn_measured_cop()
 R.check(
@@ -36606,7 +36641,7 @@ R.check(
 # Persistence: additive, and an existing store keeps every bucket it had.
 _hw_old = _t2_coord()
 _hw_old._cop_baseline = {}
-_hw_v1_payload = {"cop_baseline": {"1": [3.2, 40], "2": [3.5, 25]}}
+_hw_v1_payload = {"cop_baseline_measured": {"1": [3.2, 40], "2": [3.5, 25]}}
 
 
 async def _hw_load_v1(_p=_hw_v1_payload):
@@ -36624,7 +36659,7 @@ R.check(
 )
 _hw_old._current_state.outdoor_temperature = _HW_OUT
 _hw_old._observe_cop_health(_hw_dhw, True)
-_hw_written = _hw_old._thermal_learning_payload()["cop_baseline"]
+_hw_written = _hw_old._thermal_learning_payload()["cop_baseline_measured"]
 R.check(
     "and it writes back under the SAME keys, with the DHW curve alongside",
     _hw_written.get("1") == [3.2, 40]
@@ -47227,7 +47262,7 @@ _T2_GOOD_STORE = {
     "snow_accum_cm": 5.0,
     "last_heavy_snow": "2026-01-02T03:04:05",
     "snow_accum_last": "2026-01-03T04:05:06",
-    "cop_baseline": {"4": [3.0, 7], "5:dhw": [2.0, 3]},
+    "cop_baseline_measured": {"4": [3.0, 7], "5:dhw": [2.0, 3]},
 }
 _t2_store_good = _t2_load(dict(_T2_GOOD_STORE))
 R.check(
@@ -47290,7 +47325,7 @@ R.check(
 _t2_store_base = _t2_load(
     dict(
         _T2_GOOD_STORE,
-        cop_baseline={"nope": [1.0, 1], "4": [3.0, 7], "6": "x"},
+        cop_baseline_measured={"nope": [1.0, 1], "4": [3.0, 7], "6": "x"},
     )
 )
 R.check(
@@ -61245,7 +61280,7 @@ R.check(
 _f14b_counts = _t1_coord()
 _f14b_counts._thermal_learning_store = _T1DictStore(
     _f14b_store._sanitize({
-        "cop_baseline": {"4": [3.1, 1e20], "4:dhw": [2.5, 1e308],
+        "cop_baseline_measured": {"4": [3.1, 1e20], "4:dhw": [2.5, 1e308],
                          "5": [2.0, 5]},
         "capacity_envelope": {"-3": [5.0, 1e308], "2": [4.0, 9]},
     }))
@@ -69954,7 +69989,18 @@ R.check(
 
 # The last measured COP survives a restart beside cop_scale, with the curve
 # it was judged against, so the sensor does not go dark until the next fold.
-_cf_live = _cf_coord()
+# Measured: metered heat over the metered power (R10-HOTFIX-COP-UNMEASURED).
+
+
+def _cf_metered(heat_kw=6.0):
+    cfg = dict(_L5_CFG, heat_pump_max_power=14.0, heat_pump_min_power=1.0,
+               heat_pump_thermal_power_entity="sensor.heat_kw")
+    coord = _Coord(_FakeHass(dict(_CF_STATES)), _FakeEntry(data=cfg))
+    coord._flow_bias.heat_output_kw = heat_kw
+    return coord
+
+
+_cf_live = _cf_metered()
 _cf_learn(_cf_live, 2.4, 2)
 if hasattr(_cf_live, "_measured_cop"):
     _cf_live._measured_cop.curve_dhw, _cf_live._measured_cop.dhw_temp = True, 52.0
@@ -70132,18 +70178,20 @@ R.check(
 )
 
 # The observability state the payload publishes: a heat reading (the heat
-# counter, or the thermal power entity) measures the COP whatever the draw
-# does; without one, the draw window decides; without an electrical figure to
-# divide by there is none. A heat counter divides by its electric counter.
+# counter, or the thermal power entity) over an electrical one measures the
+# COP; without a heat reading it cannot be measured, whatever the draw does
+# (R10-HOTFIX-COP-UNMEASURED); a vendor's estimate on either side is not a
+# measurement; without an electrical figure to divide by there is none. A heat
+# counter divides by its electric counter.
 _cg_obs = _cg_acc.cop_observability
 R.check(
-    "cop_observability: heat metered beats a draw that ignores the ask; no "
-    "electrical figure is no COP; the draw window decides the rest",
-    _cg_obs(electric=True, measured_heat=True, follows=False) == "heat_metered"
-    and _cg_obs(electric=False, measured_heat=True, follows=True) == "no_electric_meter"
-    and _cg_obs(electric=True, measured_heat=False, follows=False) == "not_measurable"
-    and _cg_obs(electric=True, measured_heat=False, follows=True) == "draw_follows_plan"
-    and _cg_obs(electric=True, measured_heat=False, follows=None) == "awaiting_draw_evidence",
+    "cop_observability: metered heat measures; no heat reading is not "
+    "measurable; an estimate is an estimate; no electrical figure is no COP",
+    _cg_obs(electric=True, measured_heat=True, estimated=False) == "heat_metered"
+    and _cg_obs(electric=False, measured_heat=True, estimated=False) == "no_electric_meter"
+    and _cg_obs(electric=True, measured_heat=False, estimated=False) == "not_measurable"
+    and _cg_obs(electric=True, measured_heat=False, estimated=True) == "not_measurable"
+    and _cg_obs(electric=True, measured_heat=True, estimated=True) == "estimated_inputs",
 )
 
 
@@ -70163,12 +70211,12 @@ _cg_states = {
         heat_pump_heat_energy_entity="sensor.heat_kwh", heat_pump_energy_entity="sensor.elec_kwh"),
 }
 R.check(
-    "the coordinator's state: a self-set draw with no heat reading is not "
-    "measurable, a thermal-power install never is, and a heat counter without "
-    "an electric counter has nothing to divide by",
+    "the coordinator's state: no heat reading is not measurable whether or not "
+    "the draw follows the ask, a metered thermal-power install is, and a heat "
+    "counter without an electric counter has nothing to divide by",
     _cg_states == {
         "power, self-set draw": "not_measurable",
-        "power, following draw": "draw_follows_plan",
+        "power, following draw": "not_measurable",
         "thermal power, self-set draw": "heat_metered",
         "heat counter, no electric counter": "no_electric_meter",
         "heat counter and electric counter": "heat_metered",
@@ -70176,10 +70224,222 @@ R.check(
     f"{_cg_states!r}",
 )
 
+# ---------------------------------------------------------------------------
+R.section("R10-HOTFIX-COP-UNMEASURED: a COP sample is measured only from metered heat over metered power")
+
+# A measured COP sample, and with it the COP health watch, needs a heat
+# measurement for the interval over an electrical one, neither of them a vendor
+# estimate, and for a hot-water interval a heat measurement that sees the
+# hot-water circuit (``InstallCapability.cop_measured``). Everything else still
+# trains the COP scale (tvofi, 2026-11-07: "Training on estimated power should
+# be good enough and better than nothing though so retain that").
+from heatpump_optimizer import flow_meter as _cu_fm  # noqa: E402
+from heatpump_optimizer import thermal_model as _cu_tm  # noqa: E402
+
+
+def _cu_coord(**extra):
+    cfg = dict(_L5_CFG, heat_pump_max_power=14.0, heat_pump_min_power=1.0, **extra)
+    return _Coord(_FakeHass(dict(_CF_STATES)), _FakeEntry(data=cfg))
+
+
+def _cu_fold(coord, heat_kw, dhw, elec=2.0, commanded=2.0, outdoor=8.0, tank=48.0):
+    """One interval through the fold's tail; (refusal, baseline, measured cop, model)."""
+    coord._current_state.outdoor_temperature = outdoor
+    model = coord._thermal_model
+    ref = (model.compute_cop_dhw(outdoor, tank), True, tank) if dhw else (model.compute_cop(outdoor), False, None)
+    refusal = coord._fold_cop_evidence(commanded, elec, heat_kw, ref)
+    return refusal, dict(coord._cop_baseline), coord._measured_cop.cop, ref[0]
+
+
+# The null control: no heat slot, a hot-water interval drawing exactly what the
+# plan asked. The inference then IS the model (compute_cop_dhw), so a sample
+# recorded here is the model graded against itself.
+_cu_null = _cu_coord()
+_cu_null_ref = _cu_null._thermal_model.compute_cop_dhw(8.0, 48.0)
+_cu_null_inferred = _cu_fm.cop_evidence(_cu_null_ref, 2.0, 2.0, None, _cu_null._cop_scale)[0]
+_cu_null_out = _cu_fold(_cu_null, None, True)
+R.check(
+    "no heat input: a hot-water interval whose draw equals its ask records no "
+    "measured COP and no health-watch sample, though its inference is the model "
+    "exactly; the COP scale still trains on it",
+    _cu_null_inferred == _cu_null_ref
+    and _cu_null_out[0] is None and _cu_null_out[1] == {} and _cu_null_out[2] is None
+    and _cu_null._cop_samples == 1,
+    f"inferred {_cu_null_inferred} model {_cu_null_ref}; {_cu_null_out}; scale samples {_cu_null._cop_samples}",
+)
+
+# Both inputs are the vendor's models (the Tuya "Estimated Heating Output" and
+# "Estimated Power Draw"): heat over power is the vendor's own fitted COP on
+# every interval, so nothing is measured, by name; the explicit source wins
+# either way.
+_CU_TUYA = {
+    "heat_pump_power_entity": "sensor.pump_estimated_power_draw",
+    "heat_pump_thermal_power_entity": "sensor.pump_estimated_heating_output",
+}
+_cu_fitted = (3.1, 2.4, 4.05)
+_cu_tuya = _cu_coord(**_CU_TUYA)
+_cu_tuya_obs = [_cu_fm.cop_evidence(2.9, 2.0, 2.0, cop * 2.0, 1.0)[0] for cop in _cu_fitted]
+for _cu_cop in _cu_fitted:
+    _cu_tuya_out = _cu_fold(_cu_tuya, _cu_cop * 2.0, False)
+_cu_meter = _cu_coord(**_CU_TUYA, heat_pump_power_source="meter", heat_pump_thermal_power_source="meter")
+_cu_meter_out = _cu_fold(_cu_meter, 3.1 * 2.0, False)
+_cu_named = _cu_coord(heat_pump_power_entity="sensor.hp_power", heat_pump_thermal_power_entity="sensor.heat_kw",
+                      heat_pump_thermal_power_source="estimate")
+_cu_named_out = _cu_fold(_cu_named, 3.1 * 2.0, False)
+R.check(
+    "estimated heat over estimated power observes the fitted COP on every "
+    "interval and records nothing measured; marked metered it records; an "
+    "estimate marked by its source records nothing whatever its name",
+    _cu_tuya_obs == [c for c in _cu_fitted]
+    and _cu_tuya_out[1] == {} and _cu_tuya_out[2] is None and _cu_tuya._cop_samples == 3
+    and _cu_meter_out[1] == {(2, False): [3.1, 1]} and _cu_meter_out[2] == 3.1
+    and _cu_named_out[1] == {} and _cu_named_out[2] is None,
+    f"observed {_cu_tuya_obs}; tuya {_cu_tuya_out}; meter {_cu_meter_out}; named {_cu_named_out}",
+)
+_cu_probe = _cu_tm.probe_install
+R.check(
+    "probe_install: an estimate on either side is not a measured COP; a heat "
+    "counter outranks an estimated thermal power and divides by its electric counter",
+    not _cu_probe(_CU_TUYA).cop_measured(False)
+    and not _cu_probe({**_CU_TUYA, "heat_pump_power_source": "meter"}).cop_measured(False)
+    and not _cu_probe({**_CU_TUYA, "heat_pump_thermal_power_source": "meter"}).cop_measured(False)
+    and _cu_probe({**_CU_TUYA, "heat_pump_power_source": "meter",
+                   "heat_pump_thermal_power_source": "meter"}).cop_measured(False)
+    and _cu_probe({**_CU_TUYA, "heat_pump_heat_energy_entity": "sensor.heat_kwh",
+                   "heat_pump_energy_entity": "sensor.elec_kwh"}).cop_measured(False)
+    and not _cu_probe({"heat_pump_power_entity": "sensor.hp_power"}).cop_measured(False),
+)
+
+# Hot-water coverage is declared, never assumed: a metered heat reading counts
+# for a hot-water sample only once the install says it sees that circuit.
+_CU_METERED = {"heat_pump_power_entity": "sensor.hp_power", "heat_pump_thermal_power_entity": "sensor.heat_kw"}
+_cu_space = _cu_fold(_cu_coord(**_CU_METERED), 6.0, False)
+_cu_dhw_blind = _cu_fold(_cu_coord(**_CU_METERED), 5.0, True)
+_cu_dhw_seen = _cu_fold(_cu_coord(**_CU_METERED, heat_meter_sees_dhw=True), 5.0, True)
+R.check(
+    "metered heat over metered power records a space sample; a hot-water sample "
+    "only where the heat meter is declared to see the hot-water circuit",
+    _cu_space[1] == {(2, False): [3.0, 1]} and _cu_space[2] == 3.0
+    and _cu_dhw_blind[1] == {} and _cu_dhw_blind[2] is None
+    and _cu_dhw_seen[1] == {(2, True): [2.5, 1]} and _cu_dhw_seen[2] == 2.5,
+    f"space {_cu_space}; blind {_cu_dhw_blind}; seen {_cu_dhw_seen}",
+)
+
+# A configured thermal power that reads no heat (unavailable, or negative,
+# which read_heat_output_kw turns into None) stops the COP fold rather than
+# falling back to the plan's inference.
+_cu_neg = _cu_coord(**_CU_METERED)
+_cu_neg._flow_bias.heat_output_kw = None
+_cu_neg_n = _cf_learn(_cu_neg, 2.0, 2)
+_cu_neg_ctl = _cf_learn(_cu_coord(heat_pump_power_entity="sensor.hp_power"), 2.0, 2)
+R.check(
+    "a thermal-power install with no heat reading refuses the COP fold; with no "
+    "heat slot the same interval still trains the scale (null)",
+    _cu_neg_n == 0 and _cf_last(_cu_neg, "refusal") == _cg_acc.COP_REFUSED_NO_HEAT
+    and _cu_neg_ctl == 2,
+    f"thermal {_cu_neg_n} ({_cf_last(_cu_neg, 'refusal')}); no slot {_cu_neg_ctl}",
+)
+
+# The observability the card and the sensors read.
+_cu_states = {
+    "no heat input": _cg_install_obs(selfset=False),
+    "estimated heat and power": _cg_install_obs(**_CU_TUYA),
+    "metered heat and power": _cg_install_obs(**_CU_METERED),
+}
+R.check(
+    "cop_observability: no heat input is not measurable, an estimated input is "
+    "an estimate, metered heat over metered power is heat-metered",
+    _cu_states == {
+        "no heat input": "not_measurable",
+        "estimated heat and power": "estimated_inputs",
+        "metered heat and power": "heat_metered",
+    },
+    f"{_cu_states!r}",
+)
+
+# The migration: bands stored before this fix were recorded without a heat
+# measurement on at least the owner's install, and carry no provenance, so
+# they are dropped with the CUSUM built on them and the last COP they reported
+# as measured; bands and a measured COP stored since load.
+_cu_old = _cu_coord()
+_cu_old_payload = {"cop_baseline": {"0:dhw": [2.3031, 2], "2": [2.5166, 2]},
+                   "cop_health_cusum": {"stat": 0.5, "tripped": True},
+                   "measured_cop": {"cop": 2.55, "curve_dhw": True, "dhw_temp": 48.0,
+                                    "at": "2026-11-01T12:00:00+00:00"}}
+
+
+async def _cu_old_load(_p=_cu_old_payload):
+    return _p
+
+
+_cu_old._thermal_learning_store.async_load = _cu_old_load
+_asyncio.run(_cu_old._async_load_thermal_learning())
+_cu_new = _cu_coord(**_CU_METERED)
+_cu_fold(_cu_new, 6.0, False)
+_cu_new_payload = _cu_new._thermal_learning_payload()
+_cu_back = _cu_coord()
+
+
+async def _cu_new_load(_p=_cu_new_payload):
+    return _p
+
+
+_cu_back._thermal_learning_store.async_load = _cu_new_load
+_asyncio.run(_cu_back._async_load_thermal_learning())
+R.check(
+    "a COP baseline stored before measured provenance loads empty with its CUSUM "
+    "reset; one stored since round-trips",
+    _cu_old._cop_baseline == {} and not _cu_old._cop_health_cusum.tripped
+    and "cop_baseline" not in _cu_new_payload
+    and _cu_back._cop_baseline == {(2, False): [3.0, 1]},
+    f"old {_cu_old._cop_baseline} tripped {_cu_old._cop_health_cusum.tripped}; back {_cu_back._cop_baseline}",
+)
+# The same CUSUM under the since-fix key is kept: the reset above is the key's,
+# not the loader dropping every CUSUM (the old check's null control).
+_cu_kept = _cu_coord()
+
+
+_cu_kept_payload = {"cop_baseline_measured": {"2": [3.0, 1]},
+                    "cop_health_cusum_measured": {"stat": 0.5, "tripped": True}}
+
+
+async def _cu_kept_load(_p=_cu_kept_payload):
+    return _p
+
+
+_cu_kept._thermal_learning_store.async_load = _cu_kept_load
+_asyncio.run(_cu_kept._async_load_thermal_learning())
+from heatpump_optimizer import store as _cu_store  # noqa: E402
+
+# The store declares what the coordinator writes under the new keys: a band of
+# one sample and a CUSUM below its first unit both load, not quarantined.
+R.check(
+    "the store's domains admit a since-fix COP payload: the one the fold wrote, "
+    "and a one-sample band beside a CUSUM part-way to its alarm",
+    _cu_store.off_domain("heatpump_optimizer_thermal_learning", _cu_new_payload) == []
+    and _cu_store.off_domain("heatpump_optimizer_thermal_learning", _cu_kept_payload) == [],
+    f"{_cu_store.off_domain('heatpump_optimizer_thermal_learning', _cu_new_payload)} "
+    f"{_cu_store.off_domain('heatpump_optimizer_thermal_learning', _cu_kept_payload)}",
+)
+R.check(
+    "a COP health CUSUM stored since measured provenance loads with its state",
+    _cu_kept._cop_health_cusum.tripped and _cu_kept._cop_baseline == {(2, False): [3.0, 1]},
+    f"tripped {_cu_kept._cop_health_cusum.tripped}; baseline {_cu_kept._cop_baseline}",
+)
+R.check(
+    "a last COP stored before measured provenance does not load as measured; "
+    "one stored since round-trips",
+    _cu_old._measured_cop.cop is None and _cu_old._measured_cop.at is None
+    and _cu_new_payload.get("measured_cop", {}).get("cop") is not None
+    and _cu_back._measured_cop.as_dict() == _cu_new._measured_cop.as_dict(),
+    f"old {_cu_old._measured_cop.as_dict()}; new {_cu_new_payload.get('measured_cop')}; "
+    f"back {_cu_back._measured_cop.as_dict()}",
+)
+
 # The latch outlives every later refusal, so the time it folded is kept with
 # it, round-trips the store, and a record stored before the instant was loads
 # with its age unknown, never now.
-_cg_t = _cf_coord()
+_cg_t = _cf_metered()
 _cf_learn(_cg_t, 2.0, 1)
 _cg_at = _cg_t._measured_cop.at
 _cg_back = _cf_MC.from_dict(_cg_t._measured_cop.as_dict())
@@ -75136,6 +75396,8 @@ R.check(
 _tp_track = {}
 for _tp_heat in (None, 6.0):
     _g = _CopGate(outdoor=8.0, action={"power": 3.0})
+    # A metered install: its measured COP is recorded (R10-HOTFIX-COP-UNMEASURED).
+    _g._config = {"heat_pump_power_entity": "sensor.hp_power", "heat_pump_thermal_power_entity": "sensor.heat_kw"}
     _g._measured_power = 1.4
     _g._flow_bias.observe_temps(40.0, 35.0, heat_output_kw=_tp_heat)
     _g._learn_measured_cop()
diff --git a/tests/golden/card_claimed_drift.txt b/tests/golden/card_claimed_drift.txt
index 89d7b4eb5..53a25f59d 100644
--- a/tests/golden/card_claimed_drift.txt
+++ b/tests/golden/card_claimed_drift.txt
@@ -776,3 +776,9 @@
 # narrative list; planStates publishes no `why_now`, so the block shows its
 # no-data line. Only score_open renders a headline with a narrative here;
 # card_drift reports the other 44 states identical.
+
+# R10-HOTFIX-COP-UNMEASURED: the heat pump grade's explanation says a measured
+# COP is metered heat over a power meter, neither an estimate, and that without
+# a metered heat reading there is no grade at all. Only score_open moves; the
+# other 44 states are identical.
+score_open  # R10-HOTFIX-COP-UNMEASURED: grade explanation says measured COP is metered heat, no grade without it
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index 0613eac7c..46b7d28c1 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -763,3 +763,9 @@
 # changes exactly two leaves (the plain and the seeded render of
 # dhw_setpoint_entity.config.filter gain the water_heater domain); no plan reads
 # it, so every other fixture is byte-identical. Re-recorded in the committed file.
+coord_all_features # R10-HOTFIX-COP-UNMEASURED: no heat reading is no measured COP: the machine grade's reason (insight and optimization-score attributes) moves cop_watch_learning -> cop_unmeasurable; two string leaves, no float moved; edited in the committed file, never recorded
+coord_dhw # R10-HOTFIX-COP-UNMEASURED: no heat reading is no measured COP: the machine grade's reason (insight and optimization-score attributes) moves cop_watch_learning -> cop_unmeasurable; two string leaves, no float moved; edited in the committed file, never recorded
+coord_grid_fee # R10-HOTFIX-COP-UNMEASURED: no heat reading is no measured COP: the machine grade's reason (insight and optimization-score attributes) moves cop_watch_learning -> cop_unmeasurable; two string leaves, no float moved; edited in the committed file, never recorded
+coord_minimal # R10-HOTFIX-COP-UNMEASURED: no heat reading is no measured COP: the machine grade's reason (insight and optimization-score attributes) moves cop_watch_learning -> cop_unmeasurable; two string leaves, no float moved; edited in the committed file, never recorded
+coord_two_zone # R10-HOTFIX-COP-UNMEASURED: no heat reading is no measured COP: the machine grade's reason (insight and optimization-score attributes) moves cop_watch_learning -> cop_unmeasurable; two string leaves, no float moved; edited in the committed file, never recorded
+config_flow # R10-HOTFIX-COP-UNMEASURED: the metering page gains heat_pump_power_source, heat_pump_thermal_power_source (auto, meter, estimate) and heat_meter_sees_dhw; leaves added only, none moved; float-free, re-recorded in the committed file
diff --git a/tests/golden/config_flow.json b/tests/golden/config_flow.json
index 9f3b6bf9d..4a4fc98c7 100644
--- a/tests/golden/config_flow.json
+++ b/tests/golden/config_flow.json
@@ -1063,6 +1063,7 @@
   "flow_meter_entity": "sensor.seed_flow_meter_entity",
   "fuse_guard_enabled": true,
   "grid_fee_entity": "sensor.seed_grid_fee_entity",
+  "heat_meter_sees_dhw": true,
   "heat_pump_backup_heater_entity": "sensor.seed_heat_pump_backup_heater_entity",
   "heat_pump_capacity_limited_entity": "sensor.seed_heat_pump_capacity_limited_entity",
   "heat_pump_defrost_entity": "sensor.seed_heat_pump_defrost_entity",
@@ -2138,6 +2139,12 @@
     },
     "default": null,
     "fields": {
+     "heat_meter_sees_dhw": {
+      "config": null,
+      "default": "True",
+      "required": "Optional",
+      "selector": "BooleanSelector"
+     },
      "heat_pump_energy_entity": {
       "config": {
        "filter": "[{'domain': ['sensor'], 'device_class': ['energy']}]"
@@ -2162,6 +2169,16 @@
       "required": "Optional",
       "selector": "EntitySelector"
      },
+     "heat_pump_power_source": {
+      "config": {
+       "mode": "'dropdown'",
+       "options": "['auto', 'meter', 'estimate']",
+       "translation_key": "'meter_source'"
+      },
+      "default": "'auto'",
+      "required": "Optional",
+      "selector": "SelectSelector"
+     },
      "heat_pump_thermal_power_entity": {
       "config": {
        "filter": "[{'domain': ['sensor'], 'device_class': ['power']}]"
@@ -2170,6 +2187,16 @@
       "required": "Optional",
       "selector": "EntitySelector"
      },
+     "heat_pump_thermal_power_source": {
+      "config": {
+       "mode": "'dropdown'",
+       "options": "['auto', 'meter', 'estimate']",
+       "translation_key": "'meter_source'"
+      },
+      "default": "'auto'",
+      "required": "Optional",
+      "selector": "SelectSelector"
+     },
      "house_power_entity": {
       "config": {
        "filter": "[{'domain': ['sensor'], 'device_class': ['power']}]"
@@ -4729,6 +4756,12 @@
    },
    "default": null,
    "fields": {
+    "heat_meter_sees_dhw": {
+     "config": null,
+     "default": "False",
+     "required": "Optional",
+     "selector": "BooleanSelector"
+    },
     "heat_pump_energy_entity": {
      "config": {
       "filter": "[{'domain': ['sensor'], 'device_class': ['energy']}]"
@@ -4753,6 +4786,16 @@
      "required": "Optional",
      "selector": "EntitySelector"
     },
+    "heat_pump_power_source": {
+     "config": {
+      "mode": "'dropdown'",
+      "options": "['auto', 'meter', 'estimate']",
+      "translation_key": "'meter_source'"
+     },
+     "default": "'auto'",
+     "required": "Optional",
+     "selector": "SelectSelector"
+    },
     "heat_pump_thermal_power_entity": {
      "config": {
       "filter": "[{'domain': ['sensor'], 'device_class': ['power']}]"
@@ -4761,6 +4804,16 @@
      "required": "Optional",
      "selector": "EntitySelector"
     },
+    "heat_pump_thermal_power_source": {
+     "config": {
+      "mode": "'dropdown'",
+      "options": "['auto', 'meter', 'estimate']",
+      "translation_key": "'meter_source'"
+     },
+     "default": "'auto'",
+     "required": "Optional",
+     "selector": "SelectSelector"
+    },
     "house_power_entity": {
      "config": {
       "filter": "[{'domain': ['sensor'], 'device_class': ['power']}]"
diff --git a/tests/golden/coord_all_features.json b/tests/golden/coord_all_features.json
index 19dc6fe35..5039e1357 100644
--- a/tests/golden/coord_all_features.json
+++ b/tests/golden/coord_all_features.json
@@ -334,7 +334,7 @@
     "overall": null,
     "reasons": {
      "envelope": "heat_loss_learning",
-     "machine": "cop_watch_learning",
+     "machine": "cop_unmeasurable",
      "operation": "no_scored_day",
      "overall": "first_scored_day"
     }
@@ -2227,7 +2227,7 @@
     "price_tiles": {},
     "reasons": {
      "envelope": "heat_loss_learning",
-     "machine": "cop_watch_learning",
+     "machine": "cop_unmeasurable",
      "operation": "no_scored_day",
      "overall": "first_scored_day"
     },
diff --git a/tests/golden/coord_dhw.json b/tests/golden/coord_dhw.json
index c3a004a9b..6a339fc9a 100644
--- a/tests/golden/coord_dhw.json
+++ b/tests/golden/coord_dhw.json
@@ -334,7 +334,7 @@
     "overall": null,
     "reasons": {
      "envelope": "heat_loss_learning",
-     "machine": "cop_watch_learning",
+     "machine": "cop_unmeasurable",
      "operation": "no_scored_day",
      "overall": "first_scored_day"
     }
@@ -2148,7 +2148,7 @@
     "price_tiles": {},
     "reasons": {
      "envelope": "heat_loss_learning",
-     "machine": "cop_watch_learning",
+     "machine": "cop_unmeasurable",
      "operation": "no_scored_day",
      "overall": "first_scored_day"
     },
diff --git a/tests/golden/coord_grid_fee.json b/tests/golden/coord_grid_fee.json
index bd082b312..0065d0bb2 100644
--- a/tests/golden/coord_grid_fee.json
+++ b/tests/golden/coord_grid_fee.json
@@ -269,7 +269,7 @@
     "overall": null,
     "reasons": {
      "envelope": "heat_loss_learning",
-     "machine": "cop_watch_learning",
+     "machine": "cop_unmeasurable",
      "operation": "no_scored_day",
      "overall": "first_scored_day"
     }
@@ -1987,7 +1987,7 @@
     "price_tiles": {},
     "reasons": {
      "envelope": "heat_loss_learning",
-     "machine": "cop_watch_learning",
+     "machine": "cop_unmeasurable",
      "operation": "no_scored_day",
      "overall": "first_scored_day"
     },
diff --git a/tests/golden/coord_minimal.json b/tests/golden/coord_minimal.json
index 454f8bfee..ab4c002e2 100644
--- a/tests/golden/coord_minimal.json
+++ b/tests/golden/coord_minimal.json
@@ -269,7 +269,7 @@
     "overall": null,
     "reasons": {
      "envelope": "heat_loss_learning",
-     "machine": "cop_watch_learning",
+     "machine": "cop_unmeasurable",
      "operation": "no_scored_day",
      "overall": "first_scored_day"
     }
@@ -1987,7 +1987,7 @@
     "price_tiles": {},
     "reasons": {
      "envelope": "heat_loss_learning",
-     "machine": "cop_watch_learning",
+     "machine": "cop_unmeasurable",
      "operation": "no_scored_day",
      "overall": "first_scored_day"
     },
diff --git a/tests/golden/coord_two_zone.json b/tests/golden/coord_two_zone.json
index a4f37477a..e5a62c5c7 100644
--- a/tests/golden/coord_two_zone.json
+++ b/tests/golden/coord_two_zone.json
@@ -279,7 +279,7 @@
     "overall": null,
     "reasons": {
      "envelope": "heat_loss_learning",
-     "machine": "cop_watch_learning",
+     "machine": "cop_unmeasurable",
      "operation": "no_scored_day",
      "overall": "first_scored_day"
     }
@@ -2033,7 +2033,7 @@
     "price_tiles": {},
     "reasons": {
      "envelope": "heat_loss_learning",
-     "machine": "cop_watch_learning",
+     "machine": "cop_unmeasurable",
      "operation": "no_scored_day",
      "overall": "first_scored_day"
     },
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.ac5ca5ae.json b/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.75c968b4.json
similarity index 71%
rename from tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.ac5ca5ae.json
rename to tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.75c968b4.json
index 95594139b..cb766b020 100644
--- a/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.ac5ca5ae.json
+++ b/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.75c968b4.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:cop_observability GUARD_OFF ac5ca5ae",
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:cop_observability GUARD_OFF 75c968b4",
   "killed_by": "tests/features.py",
-  "old": "    if measured_heat:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+  "old": "    if not measured_heat:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
 }
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.RETURN_DEL.e75e96f9.json b/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.RETURN_DEL.8b12f886.json
similarity index 64%
rename from tests/mutation_ledger/killed_by/accuracy.py/cop_observability.RETURN_DEL.e75e96f9.json
rename to tests/mutation_ledger/killed_by/accuracy.py/cop_observability.RETURN_DEL.8b12f886.json
index 57131144a..3564adb19 100644
--- a/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.RETURN_DEL.e75e96f9.json
+++ b/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.RETURN_DEL.8b12f886.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:cop_observability RETURN_DEL e75e96f9",
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:cop_observability RETURN_DEL 8b12f886",
   "killed_by": "tests/features.py",
-  "old": "    return COP_DRAW_FOLLOWS if follows else COP_NOT_MEASURABLE",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+  "old": "    return COP_ESTIMATED if estimated else COP_HEAT_METERED",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
 }
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_cop_evidence.GUARD_OFF.690970ce.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_cop_evidence.GUARD_OFF.690970ce.json
new file mode 100644
index 000000000..2f153a927
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_cop_evidence.GUARD_OFF.690970ce.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_cop_evidence GUARD_OFF 690970ce",
+  "killed_by": "tests/features.py",
+  "old": "        if measured:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=17."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_cop_evidence.GUARD_OFF.afc1c494.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_cop_evidence.GUARD_OFF.afc1c494.json
new file mode 100644
index 000000000..ded6d89fd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_cop_evidence.GUARD_OFF.afc1c494.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_cop_evidence GUARD_OFF afc1c494",
+  "killed_by": "tests/features.py",
+  "old": "        if (measured := probe_install(_ctx_of(self)._config).cop_sample(heat_kw, bool(cop_curve_dhw))) is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.c1dafc5f.json b/tests/mutation_ledger/killed_by/coordinator.py/machine_score.GUARD_OFF.6bdb5987.json
similarity index 57%
rename from tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.c1dafc5f.json
rename to tests/mutation_ledger/killed_by/coordinator.py/machine_score.GUARD_OFF.6bdb5987.json
index c64de4327..d11c0770f 100644
--- a/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.c1dafc5f.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/machine_score.GUARD_OFF.6bdb5987.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:cop_observability GUARD_OFF c1dafc5f",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:machine_score GUARD_OFF 6bdb5987",
   "killed_by": "tests/features.py",
-  "old": "    if follows is None:",
+  "old": "    if not measurable:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
 }
diff --git a/tests/mutation_ledger/killed_by/sensor.py/ObservedCOPSensor._waiting_for.GUARD_OFF.c85dda37.json b/tests/mutation_ledger/killed_by/sensor.py/ObservedCOPSensor._waiting_for.GUARD_OFF.c85dda37.json
new file mode 100644
index 000000000..200195514
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sensor.py/ObservedCOPSensor._waiting_for.GUARD_OFF.c85dda37.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sensor.py:ObservedCOPSensor._waiting_for GUARD_OFF c85dda37",
+  "killed_by": "tests/entities.py",
+  "old": "        if data.get(\"cop_observability\") == COP_ESTIMATED:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.cop_sample.BOOLOP.d31f43a0.json b/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.cop_sample.BOOLOP.d31f43a0.json
new file mode 100644
index 000000000..0d86ffde0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.cop_sample.BOOLOP.d31f43a0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:InstallCapability.cop_sample BOOLOP d31f43a0",
+  "killed_by": "tests/features.py",
+  "old": "            return None if self.measured_heat and not self.heat_counter else False",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return None if self.measured_heat or not self.heat_counter else False`) took tests/features.py from rc=0 failed=0 to rc=1 failed=18."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.cop_sample.GUARD_OFF.1d188586.json b/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.cop_sample.GUARD_OFF.1d188586.json
new file mode 100644
index 000000000..3dfa8635d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.cop_sample.GUARD_OFF.1d188586.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:InstallCapability.cop_sample GUARD_OFF 1d188586",
+  "killed_by": "tests/features.py",
+  "old": "        if heat_kw is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.cop_sample.RETURN_DEL.af9c59c9.json b/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.cop_sample.RETURN_DEL.af9c59c9.json
new file mode 100644
index 000000000..cdc1f708b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.cop_sample.RETURN_DEL.af9c59c9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:InstallCapability.cop_sample RETURN_DEL af9c59c9",
+  "killed_by": "tests/features.py",
+  "old": "        return self.cop_measured(dhw)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/_estimated.GUARD_OFF.0b2cd5cf.json b/tests/mutation_ledger/killed_by/thermal_model.py/_estimated.GUARD_OFF.0b2cd5cf.json
new file mode 100644
index 000000000..5762883a3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/_estimated.GUARD_OFF.0b2cd5cf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:_estimated GUARD_OFF 0b2cd5cf",
+  "killed_by": "tests/features.py",
+  "old": "    if source == const.METER_SOURCE_ESTIMATE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/_estimated.GUARD_OFF.82c38afb.json b/tests/mutation_ledger/killed_by/thermal_model.py/_estimated.GUARD_OFF.82c38afb.json
new file mode 100644
index 000000000..071a8ee8c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/_estimated.GUARD_OFF.82c38afb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:_estimated GUARD_OFF 82c38afb",
+  "killed_by": "tests/features.py",
+  "old": "    if source == const.METER_SOURCE_METER:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/_estimated.RETURN_DEL.51801b43.json b/tests/mutation_ledger/killed_by/thermal_model.py/_estimated.RETURN_DEL.51801b43.json
new file mode 100644
index 000000000..2caf43097
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/_estimated.RETURN_DEL.51801b43.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:_estimated RETURN_DEL 51801b43",
+  "killed_by": "tests/features.py",
+  "old": "    return const.ESTIMATE_ID_MARK in str(entity_id or \"\").lower()",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
