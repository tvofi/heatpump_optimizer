# Review packet #3866
head: f36611dd23542a73d141963c1eb7860f8a219edb
base: 8cc3fb3e35b8cf320124af236f1c713a928e5685

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=137310117480 success
arch-score / arch-score id=137327856131 success
arm id=137309595762 skipped
budget-raise-gate / budget-raise-gate id=137327855634 success
cancel-superseded id=137337666140 in_progress
codeql id=137319075176 skipped
codeql / Analyze (actions) id=137327885634 success
codeql / Analyze (javascript-typescript) id=137327856627 success
codeql / Analyze (python) id=137327856821 success
gate id=137321863998 failure
governance id=137319075051 skipped
governance / env-matrix id=137327856286 success
governance / instrument-self-tests id=137327854660 success
governance / policy-docs id=137327856459 success
governance / record id=137327856105 skipped
governance / wave-script id=137327856125 success
hassfest id=137319075722 skipped
hassfest / hassfest id=137327856229 success
kernel-points id=137327855722 skipped
pr-contract id=137321865222 skipped
prelude id=137337666368 queued
refresh id=137337666527 queued
sweep-self id=137322975445 skipped
tests id=137319075470 skipped
tests / arch-instrument id=137327857480 success
tests / briefs id=137327856007 success
tests / browser id=137327857661 success
tests / closure-scope id=137327856495 success
tests / closures id=137327857123 success
tests / closures-autofix id=137327857849 skipped
tests / coverage id=137327858101 success
tests / coverage-ratchet id=137327858483 success
tests / fast (3.14) id=137327855655 in_progress
tests / graders-head-copy id=137327857856 success
tests / mutation id=137327854447 failure
tests / mutation-pins (1) id=137328273247 in_progress
tests / mutation-pins (2) id=137328273306 in_progress
tests / mutation-pins (3) id=137328273357 success
tests / mutation-pins (4) id=137328273334 in_progress
tests / mutation-pins (5) id=137328273267 in_progress
tests / mutation-pins (6) id=137328273314 in_progress
tests / nightly-ha id=137327856755 skipped
tests / nightly-status id=137327855774 success
tests / replay id=137327857212 skipped
tests / typing id=137327857583 success
validate id=137319075282 skipped
validate / validate-hacs id=137327855851 success

## Refusals
none

## Advisories
required-wait: required context `gate` reads concluded failure at f36611dd23542a73d141963c1eb7860f8a219edb in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
NOTE body item 05fe2dae: #3744
NOTE body item da84febe: dismissed:the orchestrator dispatches the root-cause seat, and a fixer may not run it (`root-cause.md`).
NOTE body item 0422ca11: dismissed:CI mutation-autofix re-pins killed mutants (`ci-autofix.md`).
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         tests/features.py
             `tests/features.py` is in the tree at this head
  unverified PYTHONPATH=tests/hastub python3 owner_flowcap_harness.py .
             `owner_flowcap_harness.py` does not look like a path in this tree
  unverified git grep -n 'write_setpoint\b\|write_setpoint(\|write_setpoint_c(\|"set_value"\|"set_temperature"\|SETPOINT_SERVICES\[' -- custom_components/
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -n '"space_setpoint"' -- custom_components/heatpump_optimizer/pump_arbiter.py
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff 3a98735a7e
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 tests/closure.py select --base $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/config_flow_steps.py
             `tests/config_flow_steps.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head

FIGURES: 7 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/inputs.py/setpoint_range_c.RETURN_DEL.703db2ba.json b/tests/mutation_ledger/killed_by/inputs.py/setpoint_range_c.RETURN_DEL.703db2ba.json
deleted file mode 100644
index bf902d7b31..0000000000
--- a/tests/mutation_ledger/killed_by/inputs.py/setpoint_range_c.RETURN_DEL.703db2ba.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/inputs.py:setpoint_range_c RETURN_DEL 703db2ba",
-  "killed_by": "tests/guard_pins.py",
-  "old": "    return temperature_c(attrs.get(low_key), unit), temperature_c(attrs.get(high_key), unit)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 694120d5aa296b65c7d7be097f8684e7bc3b5f61: RETURN_DEL (`pass`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.BOOLOP.e74f8c8c.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.BOOLOP.e74f8c8c.json
deleted file mode 100644
index a7763a6b16..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.BOOLOP.e74f8c8c.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_boost_ceiling_c BOOLOP e74f8c8c",
-  "killed_by": "tests/features.py",
-  "old": "    if limit is not None and limit > _gate_floor_c(inp.config):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if limit is not None or limit > _gate_floor_c(inp.config):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.CMP_BOUND.e74f8c8c.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.CMP_BOUND.e74f8c8c.json
deleted file mode 100644
index 3aeba63c75..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.CMP_BOUND.e74f8c8c.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_boost_ceiling_c CMP_BOUND e74f8c8c",
-  "killed_by": "tests/features.py",
-  "old": "    if limit is not None and limit > _gate_floor_c(inp.config):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if limit is not None and limit >= _gate_floor_c(inp.config):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.GUARD_OFF.e74f8c8c.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.GUARD_OFF.e74f8c8c.json
deleted file mode 100644
index 7127158872..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.GUARD_OFF.e74f8c8c.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_boost_ceiling_c GUARD_OFF e74f8c8c",
-  "killed_by": "tests/features.py",
-  "old": "    if limit is not None and limit > _gate_floor_c(inp.config):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_feedback_bounds.BOOLOP.9ec2e031.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_feedback_bounds.BOOLOP.9ec2e031.json
deleted file mode 100644
index dfc8deabb8..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_feedback_bounds.BOOLOP.9ec2e031.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_feedback_bounds BOOLOP 9ec2e031",
-  "killed_by": "tests/features.py",
-  "old": "    highs += [v for v in (rec.cut_hi_c, high) if v is not None and v >= lowest]",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`highs += [v for v in (rec.cut_hi_c, high) if v is not None or v >= lowest]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_feedback_bounds.CMP_BOUND.9ec2e031.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_feedback_bounds.CMP_BOUND.9ec2e031.json
deleted file mode 100644
index 002f2d41fd..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_feedback_bounds.CMP_BOUND.9ec2e031.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_feedback_bounds CMP_BOUND 9ec2e031",
-  "killed_by": "tests/features.py",
-  "old": "    highs += [v for v in (rec.cut_hi_c, high) if v is not None and v >= lowest]",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`highs += [v for v in (rec.cut_hi_c, high) if v is not None and v > lowest]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_flow_target.RETURN_DEL.e1fd0819.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_flow_target.RETURN_DEL.e1fd0819.json
deleted file mode 100644
index 46bf44b024..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_flow_target.RETURN_DEL.e1fd0819.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_flow_target RETURN_DEL e1fd0819",
-  "killed_by": "tests/features.py",
-  "old": "    return _bounded(inp, \"space_setpoint\", hold, _gate_floor_c(inp.config))",
-  "reason": "Recorded by applying the mutant on feat/water-setpoint-lift-ceiling (gate fix, over e0d2751f6): RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 of 4991 to rc=1 failed=12 of 4991: every baseline-hold check (the rated 35 degC, the curve above it, the ceiling cap, and the return target's hold less the rated spread, D5) reads None."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_inside_silent.BOOLOP.6f93e870.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_inside_silent.BOOLOP.6f93e870.json
deleted file mode 100644
index c4bc06bcfd..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_inside_silent.BOOLOP.6f93e870.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_inside_silent BOOLOP 6f93e870",
-  "killed_by": "tests/features.py",
-  "old": "    return actions is not None and int(actions[0]) == quiet_windows.ACTION_SILENT",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 6001b09a557259f37319b400d219cf83e02c563f: BOOLOP (`return actions is not None or int(actions[0]) == quiet_windows.ACTION_SILENT`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_inside_silent.RETURN_DEL.6f93e870.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_inside_silent.RETURN_DEL.6f93e870.json
deleted file mode 100644
index 0acf1de45f..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_inside_silent.RETURN_DEL.6f93e870.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_inside_silent RETURN_DEL 6f93e870",
-  "killed_by": "tests/features.py",
-  "old": "    return actions is not None and int(actions[0]) == quiet_windows.ACTION_SILENT",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 6001b09a557259f37319b400d219cf83e02c563f: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_silent_target.GUARD_OFF.6ad8ff62.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_silent_target.GUARD_OFF.6ad8ff62.json
deleted file mode 100644
index 3238a12b8a..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_silent_target.GUARD_OFF.6ad8ff62.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_silent_target GUARD_OFF 6ad8ff62",
-  "killed_by": "tests/features.py",
-  "old": "    if not _silent_rows(spec):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 6001b09a557259f37319b400d219cf83e02c563f: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_silent_target.RETURN_DEL.b9ef128b.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_silent_target.RETURN_DEL.b9ef128b.json
deleted file mode 100644
index 8a868ef28b..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_silent_target.RETURN_DEL.b9ef128b.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_silent_target RETURN_DEL b9ef128b",
-  "killed_by": "tests/structure.py",
-  "old": "    return _inside_silent(spec, cfg.quiet_off_windows, now)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 816547efe270a08e18e3b92f52185fe8c1fee2ef: RETURN_DEL (`pass`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_silent_rows.RETURN_DEL.3b1c1ccd.json b/tests/mutation_ledger/killed_by/quiet_windows.py/silent_rows.RETURN_DEL.3b1c1ccd.json
similarity index 72%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_silent_rows.RETURN_DEL.3b1c1ccd.json
rename to tests/mutation_ledger/killed_by/quiet_windows.py/silent_rows.RETURN_DEL.3b1c1ccd.json
index 4598d96d4c..132dbeb27f 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_silent_rows.RETURN_DEL.3b1c1ccd.json
+++ b/tests/mutation_ledger/killed_by/quiet_windows.py/silent_rows.RETURN_DEL.3b1c1ccd.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_silent_rows RETURN_DEL 3b1c1ccd",
+  "anchor": "custom_components/heatpump_optimizer/quiet_windows.py:silent_rows RETURN_DEL 3b1c1ccd",
   "killed_by": "tests/features.py",
   "old": "    return actions is not None",
   "reason": "Recorded by `mutation_table.py --pin-killed` against 6001b09a557259f37319b400d219cf83e02c563f: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
diff --git a/tests/mutation_ledger/survivor_triage/pump_arbiter.py/_silent_rows.GUARD_OFF.eefa4cf2.json b/tests/mutation_ledger/survivor_triage/quiet_windows.py/silent_rows.GUARD_OFF.eefa4cf2.json
similarity index 85%
rename from tests/mutation_ledger/survivor_triage/pump_arbiter.py/_silent_rows.GUARD_OFF.eefa4cf2.json
rename to tests/mutation_ledger/survivor_triage/quiet_windows.py/silent_rows.GUARD_OFF.eefa4cf2.json
index 8d1c1edfd2..4a07d09f93 100644
--- a/tests/mutation_ledger/survivor_triage/pump_arbiter.py/_silent_rows.GUARD_OFF.eefa4cf2.json
+++ b/tests/mutation_ledger/survivor_triage/quiet_windows.py/silent_rows.GUARD_OFF.eefa4cf2.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_silent_rows GUARD_OFF eefa4cf2",
+  "anchor": "custom_components/heatpump_optimizer/quiet_windows.py:silent_rows GUARD_OFF eefa4cf2",
   "old": "    if not isinstance(spec, str) or not spec.strip():",
   "reason": "GUARD_OFF (`if False`). quiet_windows.step_actions on the Monday anchor returns None for None, '', '   ', and the non-str 3, which is the same False this guard returns. Measured: PYTHONPATH=tests/hastub:custom_components python3 calling step_actions(datetime(2026, 1, 5, tzinfo=timezone.utc), 4, 0.25, spec, None) for those four specs. A real window still comes back as an array from that function; the RETURN_DEL of `return actions is not None` is the site features.py kills.",
   "verdict": "equivalent"


## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/config_flow.py b/custom_components/heatpump_optimizer/config_flow.py
index 24858c41b9..3416ad6933 100644
--- a/custom_components/heatpump_optimizer/config_flow.py
+++ b/custom_components/heatpump_optimizer/config_flow.py
@@ -218,7 +218,9 @@ from .const import (
     CONF_FLOW_HEAT_C,
     DEFAULT_FLOW_HEAT_C,
     FLOW_HEAT_C_MAX,
+    FLOW_LIMIT_C_MIN,
     CONF_FLOW_MIN_LIFT_K,
+    CONF_SPACE_SETPOINT_HIGH_LIMIT_C,
     CONF_SPACE_SETPOINT_HIGH_LIMIT_ENTITY,
     CONF_SPACE_SETPOINT_LOW_LIMIT_ENTITY,
     CONF_SPACE_SETPOINT_POWER_FEEDBACK,
@@ -659,11 +661,6 @@ def _number(
 ) -> selector.NumberSelector:
     """A numeric field.
 
-    The nested ``NumberSelector(NumberSelectorConfig(...))`` construction
-    appeared eighty-two times in this file; collapsing it makes each field one
-    readable line, so a form reads as a list of settings rather than as a wall
-    of constructor calls.
-
     A box field takes ``"any"`` as its step (#1679): its increment pinned the
     frontend's validity check, so a default or a derived value off that
     increment — eight shipped defaults and four ``presets.derive`` outputs,
@@ -1706,6 +1703,9 @@ def _water_space_setpoint(config: Mapping[str, Any]) -> bool:
     )
 
 
+#: The heating ceiling and the manual high limit: one water set-point range, °C.
+_WATER_LIMIT_C: Final = _number(FLOW_LIMIT_C_MIN, FLOW_HEAT_C_MAX, 0.5, '°C')
+
 #: Every field the options flow presents, in the order each page renders them.
 _OPTION_FIELDS: Final[tuple[_F, ...]] = (
     # -- entities
@@ -1732,14 +1732,15 @@ _OPTION_FIELDS: Final[tuple[_F, ...]] = (
     _F("entities", CONF_FLOW_MIN_LIFT_K, DEFAULT_FLOW_MIN_LIFT_K, _number(0.5, 15, 0.5, 'K'), when=_water_space_setpoint, group="indoor"),
     # The ceiling's minimum sits above pump_arbiter.FLOW_GATE_C (25 °C): a
     # ceiling at the gate would write "off" on every heating step.
-    _F("entities", CONF_FLOW_HEAT_C, DEFAULT_FLOW_HEAT_C, _number(30, FLOW_HEAT_C_MAX, 0.5, '°C'), when=_water_space_setpoint, group="indoor"),
+    _F("entities", CONF_FLOW_HEAT_C, DEFAULT_FLOW_HEAT_C, _WATER_LIMIT_C, when=_water_space_setpoint, group="indoor"),
     # Closing that flow on the measured draw (R10-WATER-SETPOINT-FEEDBACK):
     # on by default, and it acts only where a power meter is configured too.
     _F("entities", CONF_SPACE_SETPOINT_POWER_FEEDBACK, DEFAULT_SPACE_SETPOINT_POWER_FEEDBACK, selector.BooleanSelector(), when=_water_space_setpoint, group="indoor"),
-    # The controller's own limits on that set-point, where it publishes them
-    # (a Smart Home Interface's inputs 10104 and 10103): the loop stays inside them.
+    # The controller's limits on that set-point where it publishes them (a Smart Home Interface's
+    # inputs 10104 and 10103), and the upper one typed by hand: space writes stay inside (flow_limit).
     _F("entities", CONF_SPACE_SETPOINT_LOW_LIMIT_ENTITY, _STORED, _entity_of('sensor', 'temperature'), when=_water_space_setpoint, group="indoor"),
     _F("entities", CONF_SPACE_SETPOINT_HIGH_LIMIT_ENTITY, _STORED, _entity_of('sensor', 'temperature'), when=_water_space_setpoint, group="indoor"),
+    _F("entities", CONF_SPACE_SETPOINT_HIGH_LIMIT_C, _STORED, _WATER_LIMIT_C, when=_water_space_setpoint, group="indoor"),
     # -- entities_metering
     _F("entities_metering", CONF_SOLAR_RADIATION_ENTITY, _STORED, _entity_of('sensor'), group="solar"),
     _F("entities_metering", CONF_SOLAR_FORECAST_SOURCE, DEFAULT_SOLAR_FORECAST_SOURCE, _solar_source_selector(), group="solar"),
diff --git a/custom_components/heatpump_optimizer/const.py b/custom_components/heatpump_optimizer/const.py
index 233a4eff49..181e139d87 100644
--- a/custom_components/heatpump_optimizer/const.py
+++ b/custom_components/heatpump_optimizer/const.py
@@ -855,6 +855,9 @@ DEFAULT_FLOW_HEAT_C: Final = 55.0
 #: _boost_ceiling_c``): above it the entity is no heating-flow set-point
 #: (a generic number helper reads 100), so a boost keeps the planned level.
 FLOW_HEAT_C_MAX: Final = 70.0
+#: The lowest heating-flow ceiling and manual high limit the options flow
+#: offers, °C: above the 25 °C gate, which a ceiling there would write as off.
+FLOW_LIMIT_C_MIN: Final = 30.0
 #: The flow set-point's lift over the measured inlet water at the modulation
 #: floor, K. Absent keeps :data:`thermal_model.FLOW_MIN_LIFT_K`. A controller
 #: that takes the set-point as its return-water target modulates on the gap
@@ -875,6 +878,9 @@ DEFAULT_SPACE_SETPOINT_POWER_FEEDBACK: Final = True
 #: register 10001 (#3372 comment 6756915104). Unset, nothing reads them.
 CONF_SPACE_SETPOINT_LOW_LIMIT_ENTITY: Final = "space_setpoint_low_limit_entity"
 CONF_SPACE_SETPOINT_HIGH_LIMIT_ENTITY: Final = "space_setpoint_high_limit_entity"
+#: The upper limit typed by hand, °C, for a controller that publishes none
+#: (``flow_limit``): with the sensor too, the lower of the two binds.
+CONF_SPACE_SETPOINT_HIGH_LIMIT_C: Final = "space_setpoint_high_limit_c"
 #: ``false`` keeps the duty-cycle reading on a switch-plus-setpoint
 #: install. Absent follows the install probe (#1955).
 CONF_CLAMP_PLANNED_LEVELS: Final = "clamp_planned_levels"
diff --git a/custom_components/heatpump_optimizer/entry_config.py b/custom_components/heatpump_optimizer/entry_config.py
index 4a19640d9a..172ac49f3c 100644
--- a/custom_components/heatpump_optimizer/entry_config.py
+++ b/custom_components/heatpump_optimizer/entry_config.py
@@ -208,6 +208,7 @@ class EntryConfig(Mapping[str, Any]):
 
     # A fraction this version cannot read caps nothing: None, not the default.
     silent_mode_power_fraction: float | None = _key(const.DEFAULT_SILENT_MODE_FRACTION, _refused_number)
+    space_setpoint_high_limit_c: float | None = _key(None, _refused_number)
 
     # Optional numbers: None keeps the weekday or ordinary-day value.
     comfort_temp_day_weekend: float | None = _key(None, finite_float)
diff --git a/custom_components/heatpump_optimizer/flow_limit.py b/custom_components/heatpump_optimizer/flow_limit.py
new file mode 100644
index 0000000000..41fbc1df47
--- /dev/null
+++ b/custom_components/heatpump_optimizer/flow_limit.py
@@ -0,0 +1,56 @@
+"""The space water set-point's effective high limit, °C (R11-OWNER-FLOWCAP).
+
+An entity's advertised maximum can sit above the highest value the pump
+accepts. Two sources state the lower one: the controller's maximum set-point
+sensor (``space_setpoint_high_limit_entity``) and the manual option
+(``space_setpoint_high_limit_c``, tvofi 2026-11-22: "add an option to manually
+configure the high-limit if there is no such sensor"). This module is the one
+owner of how they combine; ``pump_arbiter`` reads the sources and caps every
+space water write on the answer. Pure: no Home Assistant.
+"""
+
+from __future__ import annotations
+
+from typing import NamedTuple
+
+from .const import FLOW_HEAT_C_MAX, FLOW_LIMIT_C_MIN, finite_float
+
+
+class HighLimit(NamedTuple):
+    """The effective limit, °C or ``None``, and each source set aside
+    (``sensor``, ``option``), which the caller logs."""
+
+    limit_c: float | None
+    dropped: tuple[str, ...]
+
+
+def option_c(stored: object) -> float | None:
+    """The manual option, °C, or ``None`` for one unset, not a number, or
+    outside the :data:`FLOW_LIMIT_C_MIN` to :data:`FLOW_HEAT_C_MAX` the
+    options flow offers."""
+    value = finite_float(stored)
+    return value if value is not None and FLOW_LIMIT_C_MIN <= value <= FLOW_HEAT_C_MAX else None
+
+
+def high_limit(sensor_c: float | None, manual_c: float | None, lowest_c: float) -> HighLimit:
+    """Combine the two sources into the one limit.
+
+    Each source is judged alone first: one below ``lowest_c``, the lowest
+    heating write (the gate plus its clearance, on the entity's step), leaves
+    no heating value and is dropped; one equal to it is kept, the boundary
+    ``_feedback_bounds`` always had. The gate is bounded up to the entity's
+    minimum, so ``lowest_c`` sits above it, and a limit under the minimum is
+    dropped here rather than written under it. ``sensor_c`` arrives with the
+    crossed-pair rule already applied (``pump_arbiter._setpoint_limits_c``),
+    so a dropped or unread sensor leaves the option in force. Of the kept
+    sources the lower binds (orchestrator ruling, 2026-11-22): a sensor never
+    lifts a limit the person typed.
+    """
+    kept: list[float] = []
+    dropped: list[str] = []
+    for name, value in (("sensor", sensor_c), ("option", manual_c)):
+        if value is not None and value >= lowest_c:
+            kept.append(value)
+        elif value is not None:
+            dropped.append(name)
+    return HighLimit(min(kept) if kept else None, tuple(dropped))
diff --git a/custom_components/heatpump_optimizer/inputs.py b/custom_components/heatpump_optimizer/inputs.py
index 9d85331747..63b2ea888d 100644
--- a/custom_components/heatpump_optimizer/inputs.py
+++ b/custom_components/heatpump_optimizer/inputs.py
@@ -571,10 +571,17 @@ def setpoint_range_c(hass: Any, entity_id: str | None) -> tuple[float | None, fl
     state = hass.states.get(entity_id) if entity_id else None
     if not entity_id or state is None:
         return None, None
+    unit = setpoint_unit(hass, entity_id, state)
+    low, high = _own_range(entity_id, state)
+    return temperature_c(low, unit), temperature_c(high, unit)
+
+
+def _own_range(entity_id: str, state: Any) -> tuple[float | None, float | None]:
+    """The (min, max) ``state`` states, in the entity's own unit; ``None`` for an
+    end it does not state as a number."""
     attrs = getattr(state, "attributes", None) or {}
     low_key, high_key = _RANGE_KEYS.get(entity_id.split(".", 1)[0], _NUMBER_RANGE_KEYS)
-    unit = setpoint_unit(hass, entity_id, state)
-    return temperature_c(attrs.get(low_key), unit), temperature_c(attrs.get(high_key), unit)
+    return finite_float(attrs.get(low_key)), finite_float(attrs.get(high_key))
 
 
 #: The step a set-point entity that states none accepts, in its own unit:
@@ -715,17 +722,27 @@ def quantise_setpoint_c(
 async def write_setpoint(hass: Any, entity_id: str, value: float) -> bool:
     """Write ``value``, already in the entity's own unit, to a set-point entity.
 
-    The one service call every set-point write goes through, so the value
-    sent is on the entity's step (``setpoint_step``, whole degrees where it
-    states none) -- a whole one as an integer, which a pump that takes no
-    decimals accepts. ``False``, and nothing called, for a domain with no
-    set-point service.
+    The one service call every set-point write goes through. The value sent
+    is on the entity's step (``setpoint_step``, whole degrees where it states
+    none), a whole one as an integer, which a pump that takes no decimals
+    accepts. It is inside the range the entity states when written
+    (:func:`_own_range`): the maximum rounded down onto the step, the minimum
+    up, whichever caller asked. A caller's own bound (``SetpointGrid.bounded``)
+    is the meaning of its value; this one is what the entity accepts. Crossed
+    ends send the maximum. ``False``, and nothing
+    called, for a domain with no set-point service.
     """
     domain = entity_id.split(".", 1)[0]
     service = SETPOINT_SERVICES.get(domain)
     if service is None:
         return False
-    sent = _on_step(float(value), setpoint_step(hass, entity_id), "nearest")
+    step = setpoint_step(hass, entity_id)
+    sent = _on_step(float(value), step, "nearest")
+    low, high = _own_range(entity_id, hass.states.get(entity_id))
+    if low is not None:
+        sent = max(sent, _on_step(low, step, "up"))
+    if high is not None:
+        sent = min(sent, _on_step(high, step, "down"))
     await hass.services.async_call(
         domain, service[0],
         {"entity_id": entity_id, service[1]: int(sent) if sent.is_integer() else sent},
diff --git a/custom_components/heatpump_optimizer/pump_arbiter.py b/custom_components/heatpump_optimizer/pump_arbiter.py
index 8fc1cc6845..6a6f8d9fbc 100644
--- a/custom_components/heatpump_optimizer/pump_arbiter.py
+++ b/custom_components/heatpump_optimizer/pump_arbiter.py
@@ -152,8 +152,8 @@ import math
 from collections import Counter, deque
 from collections.abc import Awaitable, Callable, Mapping
 from dataclasses import dataclass, field, replace
-from datetime import datetime, timedelta, timezone
-from typing import Any, NamedTuple, TypeGuard, cast
+from datetime import datetime, timedelta
+from typing import Any, NamedTuple, cast
 from weakref import WeakKeyDictionary
 
 from homeassistant.core import callback
@@ -164,7 +164,7 @@ from homeassistant.helpers.event import (
 )
 from homeassistant.util import dt as dt_util
 
-from . import boost, draw_range, duty_switch, issues, off_restore, pump_mode, quiet_windows
+from . import boost, draw_range, duty_switch, flow_limit, issues, off_restore, pump_mode, quiet_windows
 from .const import (
     CONF_BUFFER_TANK_TEMP_ENTITY,
     CONF_FLOOR_RETURN_TEMP_ENTITY,
@@ -198,7 +198,7 @@ from .inputs import (
 )
 from .log_latch import log_held
 from .payload import REASON_LEGIONELLA, CurrentAction
-from .plan_step import PLAN_STEP_HOURS, PLAN_STEP_MINUTES, plan_step_index, plan_step_start
+from .plan_step import PLAN_STEP_MINUTES, plan_step_index, plan_step_start
 from .drift import utc_elapsed_seconds, utc_shift
 from .drift import stored_instant
 from .store import QuarantiningStore, load_mapping
@@ -614,6 +614,24 @@ def _grid(inp: ArbiterInputs, slot: str) -> SetpointGrid | None:
     return setpoint_grid(inp.hass, _entities(inp.config)[slot])
 
 
+def _space_limit_c(inp: ArbiterInputs) -> float | None:
+    """The space water set-point's high limit (:func:`flow_limit.high_limit`), degC, or ``None``,
+    always for an indoor unit; a source set aside is logged. Heating writes, a boost and the loop
+    take it as their ``hi``, under which the entity's own maximum still binds; the gate, the
+    draw-range ceiling (a capped write commands no top draw) and an adopted edit do not read it."""
+    entity = _entities(inp.config)["space_setpoint"]
+    if _grid(inp, "space_setpoint") is None or not _flow_unit(inp.config):
+        return None
+    out = flow_limit.high_limit(
+        _setpoint_limits_c(inp)[1],
+        flow_limit.option_c(EntryConfig.from_mapping(inp.config).space_setpoint_high_limit_c),
+        _heating_floor_c(inp)[1],
+    )
+    log_held(inp.hass, f"space_limit_dropped:{entity}", bool(out.dropped), "Pump duty: the %s high "
+             "limit leaves no heating value on %s; not used", " and ".join(out.dropped), entity)
+    return out.limit_c
+
+
 def _planned_room(
     result: Any, now: datetime, attr: str = "optimal_setpoints"
 ) -> float | None:
@@ -897,8 +915,8 @@ def _boost_ceiling_c(inp: ArbiterInputs) -> float | None:
 
     The set-point entity's own maximum (tvofi, 2026-11-13: "set at the
     maximum value"), capped by a heating ceiling (``flow_heat_c``) set to
-    anything but its default, and by the controller's upper-limit sensor
-    where it reads (:func:`_setpoint_limits_c`). The default caps nothing: an
+    anything but its default, and by the high limit (:func:`_space_limit_c`:
+    the controller's sensor, the manual option). The default caps nothing: an
     absent key reads as it, and an untouched options page must change
     nothing (``tests/config_flow_steps.py``), so a stored default cannot be
     told from no setting.
@@ -915,8 +933,7 @@ def _boost_ceiling_c(inp: ArbiterInputs) -> float | None:
     caps = [high]
     if (ceiling := _heat_ceiling_c(inp.config)) != DEFAULT_FLOW_HEAT_C:
         caps.append(ceiling)
-    limit = _setpoint_limits_c(inp)[1]
-    if limit is not None and limit > _gate_floor_c(inp.config):
+    if (limit := _space_limit_c(inp)) is not None:
         caps.append(limit)
     return min(caps)
 
@@ -970,7 +987,7 @@ def _flow_target(
     target = _as_target(inp.config, FLOW_HOLD_C if curve is None else max(curve, FLOW_HOLD_C))
     capped = curve is not None or _return_unit(inp.config)
     hold = min(target, ceiling) if capped else target
-    return _bounded(inp, "space_setpoint", hold, _gate_floor_c(inp.config))
+    return _bounded(inp, "space_setpoint", hold, _gate_floor_c(inp.config), hi=_space_limit_c(inp))
 
 
 class MapInputs(NamedTuple):
@@ -990,7 +1007,8 @@ def _map_inputs(inp: ArbiterInputs, now: datetime, boosted: bool) -> MapInputs:
     for the write (:func:`_flow_target`) and the pass record (:func:`_pass_record`)."""
     p_min, p_max = _band_kw(inp)
     boost_c = _boost_ceiling_c(inp) if boosted else None
-    heat_c = _heat_ceiling_c(inp.config) if boost_c is None else boost_c
+    # The level map's top is one the pump takes: under the high limit.
+    heat_c = min(_heat_ceiling_c(inp.config) if boost_c is None else boost_c, _space_limit_c(inp) or math.inf)
     floor_c = _or_hold(modulation_floor_flow_c(
         _flow_inlet_c(inp), _gate_c(inp),
         start_flow_min_lift_k(inp.config, getattr(inp.state, "space_start_hysteresis_k", None)),
@@ -1086,26 +1104,25 @@ def _feedback_bounds(held: ArbiterState, rec: FeedbackRun, inp: ArbiterInputs, i
     never above the ceiling.
 
     The gate is the value a step that does not heat writes, so a heating
-    write at or below it tells the controller the step is off. A
-    controller's upper limit, read from its sensor or from a cut, that
-    sits under the lowest heating write (the gate plus one entity step)
-    leaves no heating value inside it: it is not the limit of a heating
-    set-point (a sensor in the wrong slot, a placeholder, a parked
-    circuit), and it is left out as an unreadable one is.
-    """
-    gate = _gate_c(inp) or _gate_floor_c(inp.config)
-    clear = gate + FEEDBACK_GATE_CLEAR_K
-    lowest = _bounded(inp, "space_setpoint", clear, lo=clear) or clear
-    lows = [inlet - FEEDBACK_DOWN_K, rec.cut_lo_c, clear]
+    write at or below it tells the controller the step is off. A cut under the lowest heating write
+    (:func:`_heating_floor_c`) is left out; the upper limit is :func:`_space_limit_c`'s, under the same rule.
+    """
+    clear, lowest = _heating_floor_c(inp)
+    lows = [inlet - FEEDBACK_DOWN_K, rec.cut_lo_c, clear, _setpoint_limits_c(inp)[0]]
     if held.stop_gap_k is not None:
         lows.append(inlet - held.stop_gap_k + FEEDBACK_STOP_MARGIN_K)
-    low, high = _setpoint_limits_c(inp)
-    lows.append(low)
     highs = [_heat_ceiling_c(inp.config)]
-    highs += [v for v in (rec.cut_hi_c, high) if v is not None and v >= lowest]
+    highs += [v for v in (rec.cut_hi_c, _space_limit_c(inp)) if v is not None and v >= lowest]
     return (max(v for v in lows if v is not None), min(highs))
 
 
+def _heating_floor_c(inp: ArbiterInputs) -> tuple[float, float]:
+    """``(clear, lowest)``, degC: the gate plus :data:`FEEDBACK_GATE_CLEAR_K`, and that on the step, the
+    lowest heating write; a limit below it (a misplaced sensor, a placeholder) leaves no heating value."""
+    clear = (_gate_c(inp) or _gate_floor_c(inp.config)) + FEEDBACK_GATE_CLEAR_K
+    return clear, _bounded(inp, "space_setpoint", clear, lo=clear) or clear
+
+
 def _setpoint_limits_c(inp: ArbiterInputs) -> tuple[float | None, float | None]:
     """The controller's ``(lower, upper)`` limit on the space set-point, °C.
 
@@ -1206,37 +1223,6 @@ def _clamp_cut(held: ArbiterState, slot: str, value: Any, observed: Any, at: dat
     return True
 
 
-def _silent_rows(spec: Any) -> TypeGuard[str]:
-    """Whether ``spec`` names a silent window the week can reach.
-
-    The same ``step_actions`` the solve uses, over seven days from a Monday,
-    so a weekday token and an overnight window are rows and an empty or
-    unreadable spec is not. No rows means the switch is never written.
-    True only for a ``str``, which is what lets the caller pass it to
-    :func:`_inside_silent`.
-    """
-    if not isinstance(spec, str) or not spec.strip():
-        return False
-    monday = datetime(2026, 1, 5, tzinfo=timezone.utc)
-    actions = quiet_windows.step_actions(
-        monday, 7 * 24 * 60 // PLAN_STEP_MINUTES, PLAN_STEP_HOURS, spec, None,
-    )
-    return actions is not None
-
-
-def _inside_silent(silent_spec: str, off_spec: Any, now: datetime) -> bool:
-    """Whether the step covering ``now`` is silent, off winning an overlap.
-
-    The same ``step_actions`` the solve uses, so a hand-edited store whose
-    off row overlaps a silent row holds the switch off: that step is idle,
-    not a silent one.
-    """
-    actions = quiet_windows.step_actions(
-        plan_step_start(now), 1, PLAN_STEP_HOURS, silent_spec, off_spec,
-    )
-    return actions is not None and int(actions[0]) == quiet_windows.ACTION_SILENT
-
-
 def _silent_target(coord: Any, inp: ArbiterInputs, now: datetime) -> bool | None:
     """On inside a silent window, off outside; ``None`` when the slot is not ours.
 
@@ -1248,14 +1234,14 @@ def _silent_target(coord: Any, inp: ArbiterInputs, now: datetime) -> bool | None
         return None
     cfg = EntryConfig.from_mapping(inp.config)
     spec = cfg.quiet_silent_windows
-    if not _silent_rows(spec):
+    if not quiet_windows.silent_rows(spec):
         return None
     if inp.mode == MODE_BOOST:
         return False
     held = boost.held_for(coord)
     if held.active(boost.CHANNEL_SPACE, now) or held.active(boost.CHANNEL_DHW, now):
         return False
-    return _inside_silent(spec, cfg.quiet_off_windows, now)
+    return quiet_windows.inside_silent(spec, cfg.quiet_off_windows, now)
 
 
 def _dhw_write(inp: ArbiterInputs) -> float | None:
diff --git a/custom_components/heatpump_optimizer/quiet_windows.py b/custom_components/heatpump_optimizer/quiet_windows.py
index f6c713cc39..6afcc9d950 100644
--- a/custom_components/heatpump_optimizer/quiet_windows.py
+++ b/custom_components/heatpump_optimizer/quiet_windows.py
@@ -51,8 +51,8 @@ from __future__ import annotations
 
 from collections.abc import Callable, Mapping
 from dataclasses import dataclass
-from datetime import datetime, timedelta, time
-from typing import Any, Final
+from datetime import datetime, timedelta, time, timezone
+from typing import Any, Final, TypeGuard
 
 import numpy as np
 
@@ -83,7 +83,7 @@ from .dhw_schedule import (
 from .inputs import state_power_kw
 from .modbus_prefill import night_mode_write_ids, package_prefix
 from .drift import utc_step_starts
-from .plan_step import PLAN_STEP_HOURS, plan_step_start
+from .plan_step import PLAN_STEP_HOURS, PLAN_STEP_MINUTES, plan_step_start
 
 #: The per-step action codes, as one int8 array element per step.
 ACTION_NONE: Final = 0
@@ -152,6 +152,37 @@ def step_actions(
     return out if bool(np.any(out)) else None
 
 
+def silent_rows(spec: Any) -> TypeGuard[str]:
+    """Whether ``spec`` names a silent window the week can reach.
+
+    The same ``step_actions`` the solve uses, over seven days from a Monday,
+    so a weekday token and an overnight window are rows and an empty or
+    unreadable spec is not. No rows means the switch is never written.
+    True only for a ``str``, which is what lets the caller pass it to
+    :func:`inside_silent`.
+    """
+    if not isinstance(spec, str) or not spec.strip():
+        return False
+    monday = datetime(2026, 1, 5, tzinfo=timezone.utc)
+    actions = step_actions(
+        monday, 7 * 24 * 60 // PLAN_STEP_MINUTES, PLAN_STEP_HOURS, spec, None,
+    )
+    return actions is not None
+
+
+def inside_silent(silent_spec: str, off_spec: Any, now: datetime) -> bool:
+    """Whether the step covering ``now`` is silent, off winning an overlap.
+
+    The same ``step_actions`` the solve uses, so a hand-edited store whose
+    off row overlaps a silent row holds the switch off: that step is idle,
+    not a silent one.
+    """
+    actions = step_actions(
+        plan_step_start(now), 1, PLAN_STEP_HOURS, silent_spec, off_spec,
+    )
+    return actions is not None and int(actions[0]) == ACTION_SILENT
+
+
 def quiet_reason(config: Mapping[str, Any], now: datetime) -> str | None:
     """Why the step covering ``now`` is inside a configured quiet window, or ``None``.
 
diff --git a/custom_components/heatpump_optimizer/strings.json b/custom_components/heatpump_optimizer/strings.json
index 64e36d0449..81dfd8d780 100644
--- a/custom_components/heatpump_optimizer/strings.json
+++ b/custom_components/heatpump_optimizer/strings.json
@@ -592,7 +592,8 @@
               "flow_heat_c": "Heating flow ceiling (°C)",
               "space_setpoint_power_feedback": "Follow the planned power on the measured draw",
               "space_setpoint_low_limit_entity": "Controller's minimum set-point sensor (optional)",
-              "space_setpoint_high_limit_entity": "Controller's maximum set-point sensor (optional)"
+              "space_setpoint_high_limit_entity": "Controller's maximum set-point sensor (optional)",
+              "space_setpoint_high_limit_c": "Controller's maximum set-point (°C, optional)"
             },
             "data_description": {
               "indoor_temp_entity": "Optional. The actual room temperature. Without it the optimizer trusts its own model, which drifts over time.",
@@ -603,7 +604,8 @@
               "flow_heat_c": "The water set-point written at full planned power, and the highest one written while the plan is in charge. 55 °C suits a supply target. For a Return temperature entity choose it above the highest return you see in normal heating plus the lift, and no higher than the controller accepts; on a low-temperature floor heating 35–40 °C may be a starting point to check against measurements. Below 30 °C is not offered: the gate that means off is 25 °C for a flow target and 20 °C for a return target. A space boost or Boost mode writes the set-point entity's own maximum (up to 70 °C) on every step instead; a value other than 55 °C set here caps that too, so set one on a low-temperature floor heating.",
               "space_setpoint_power_feedback": "On by default. Acts only with Pump duty control at Control, a Flow or Return temperature unit and a heat-pump power sensor; otherwise nothing changes. After a 5-minute start hold, the water set-point is nudged down while the measured draw is above the planned level and up while it is below, and held while it is within 10 %, instead of following the rising inlet water. Off writes the inlet plus the lift. Requirements on the controller: its heating hysteresis at most the lift (0.5 K on a Luxtronik, for example), or a stopped compressor is not started; its minimum return target below the heating-season return; its integration polling it at least every 10 minutes, and restoring its heating mode after a controller restart, since a controller can drop what was set when it goes unread (a Luxtronik Smart Home Interface, for one, drops every set value after 600 s without access); and no second tool writing the same registers (a Luxtronik, for one, then silently discards writes).",
               "space_setpoint_low_limit_entity": "Optional. A temperature sensor that reports the lowest value the controller accepts for the set-point entity above (for example a Luxtronik through ha-luxtronik-shi: \"Temperature: return target minimum\", input 10104). With it, Follow the planned power never sends a value below it, instead of finding the limit when the controller cuts a write. Used by that option alone; left empty, nothing changes.",
-              "space_setpoint_high_limit_entity": "Optional. A temperature sensor that reports the highest value the controller accepts for the set-point entity above (for example a Luxtronik through ha-luxtronik-shi: \"Temperature: return limit\", input 10103). With it, Follow the planned power never sends a value above it, instead of finding the limit when the controller cuts a write. Used by that option alone; left empty, nothing changes."
+              "space_setpoint_high_limit_entity": "Optional. A temperature sensor that reports the highest value the controller accepts for the set-point entity above (for example a Luxtronik through ha-luxtronik-shi: \"Temperature: return limit\", input 10103). No space water set-point above it is written: Follow the planned power, a boost and every heating step stay under it, instead of finding the limit when the controller cuts a write. With a maximum set-point typed below as well, the lower of the two applies; left empty, nothing changes.",
+              "space_setpoint_high_limit_c": "Optional. The highest value the pump accepts for the set-point entity above, where that is lower than the entity's own maximum. No space water set-point above it is written, a boost's included. With a maximum set-point sensor as well, the lower of the two applies. Left empty, the entity's own maximum applies."
             }
           },
           "plant": {
diff --git a/custom_components/heatpump_optimizer/translations/de.json b/custom_components/heatpump_optimizer/translations/de.json
index d024d3c067..95a69510cf 100644
--- a/custom_components/heatpump_optimizer/translations/de.json
+++ b/custom_components/heatpump_optimizer/translations/de.json
@@ -592,7 +592,8 @@
               "flow_heat_c": "Obergrenze der Heizungsvorlauftemperatur (°C)",
               "space_setpoint_power_feedback": "Geplanter Leistung über die gemessene Aufnahme folgen",
               "space_setpoint_low_limit_entity": "Sensor für den minimalen Sollwert des Reglers (optional)",
-              "space_setpoint_high_limit_entity": "Sensor für den maximalen Sollwert des Reglers (optional)"
+              "space_setpoint_high_limit_entity": "Sensor für den maximalen Sollwert des Reglers (optional)",
+              "space_setpoint_high_limit_c": "Maximaler Sollwert des Reglers (°C, optional)"
             },
             "data_description": {
               "indoor_temp_entity": "Optional. Die tatsächliche Raumtemperatur. Ohne sie vertraut der Optimierer seinem eigenen Modell, das mit der Zeit abdriftet.",
@@ -603,7 +604,8 @@
               "flow_heat_c": "Der bei voller Planleistung geschriebene Wasser-Sollwert und der höchste, der geschrieben wird, solange der Plan die Führung hat. 55 °C passt zu einem Vorlaufziel. Wähle ihn bei einer Entität mit Rücklauftemperatur über dem höchsten Rücklauf, den du im normalen Heizbetrieb siehst, plus dem Hub, und nicht höher, als der Regler annimmt; bei einer Niedertemperatur-Fußbodenheizung können 35–40 °C ein Ausgangspunkt sein, der an Messungen zu prüfen ist. Unter 30 °C wird nicht angeboten: Die Schwelle, die aus bedeutet, liegt bei 25 °C für ein Vorlaufziel und bei 20 °C für ein Rücklaufziel. Ein Raumheizungs-Boost oder der Boost-Modus schreibt stattdessen in jedem Schritt das eigene Maximum der Sollwert-Entität (höchstens 70 °C); ein anderer Wert als 55 °C begrenzt auch das, also stelle bei einer Niedertemperatur-Fußbodenheizung einen ein.",
               "space_setpoint_power_feedback": "Standardmäßig an. Wirkt nur mit Wärmepumpen-Betriebssteuerung auf Steuern, einer Einheit Vorlauf- oder Rücklauftemperatur und einem Leistungssensor der Wärmepumpe; sonst ändert sich nichts. Nach 5 Minuten Starthaltezeit wird der Wasser-Sollwert gesenkt, solange die gemessene Aufnahme über der geplanten Leistung liegt, angehoben, solange sie darunter liegt, und innerhalb von 10 % gehalten, statt dem steigenden Eingangswasser zu folgen. Aus schreibt das Eingangswasser plus den Hub. Anforderungen an den Regler: seine Heizungshysterese höchstens der Hub (bei einer Luxtronik zum Beispiel 0,5 K), sonst startet ein stehender Verdichter nicht; sein minimales Rücklaufziel unter dem Rücklauf der Heizperiode; seine Integration fragt ihn mindestens alle 10 Minuten ab und stellt nach einem Reglerneustart die Heizbetriebsart wieder her, denn ein Regler kann Gesetztes verwerfen, wenn er nicht abgefragt wird (eine Luxtronik Smart Home Interface etwa verwirft nach 600 s ohne Zugriff alle gesetzten Werte); und kein zweites Werkzeug schreibt dieselben Register (eine Luxtronik etwa verwirft Schreibvorgänge dann stillschweigend).",
               "space_setpoint_low_limit_entity": "Optional. Ein Temperatursensor, der den niedrigsten Wert meldet, den der Regler für die Sollwert-Entität oben annimmt (zum Beispiel eine Luxtronik über ha-luxtronik-shi: \"Temperature: return target minimum\", Eingang 10104). Damit sendet Geplanter Leistung über die gemessene Aufnahme folgen nie einen Wert darunter, statt die Grenze erst zu finden, wenn der Regler einen Schreibwert kappt. Nur von dieser Option verwendet; leer ändert sich nichts.",
-              "space_setpoint_high_limit_entity": "Optional. Ein Temperatursensor, der den höchsten Wert meldet, den der Regler für die Sollwert-Entität oben annimmt (zum Beispiel eine Luxtronik über ha-luxtronik-shi: \"Temperature: return limit\", Eingang 10103). Damit sendet Geplanter Leistung über die gemessene Aufnahme folgen nie einen Wert darüber, statt die Grenze erst zu finden, wenn der Regler einen Schreibwert kappt. Nur von dieser Option verwendet; leer ändert sich nichts."
+              "space_setpoint_high_limit_entity": "Optional. Ein Temperatursensor, der den höchsten Wert meldet, den der Regler für die Sollwert-Entität oben annimmt (zum Beispiel eine Luxtronik über ha-luxtronik-shi: \"Temperature: return limit\", Eingang 10103). Kein Wassersollwert darüber wird geschrieben: Geplanter Leistung über die gemessene Aufnahme folgen, ein Boost und jeder Heizschritt bleiben darunter, statt die Grenze erst zu finden, wenn der Regler einen Schreibwert kappt. Mit einem unten eingetragenen maximalen Sollwert gilt der niedrigere der beiden; leer ändert sich nichts.",
+              "space_setpoint_high_limit_c": "Optional. Der höchste Wert, den die Pumpe für die Sollwert-Entität oben annimmt, wo er unter dem eigenen Maximum der Entität liegt. Kein Wassersollwert darüber wird geschrieben, auch nicht bei einem Boost. Mit einem Sensor für den maximalen Sollwert gilt der niedrigere der beiden. Leer gilt das eigene Maximum der Entität."
             }
           },
           "plant": {
diff --git a/custom_components/heatpump_optimizer/translations/en.json b/custom_components/heatpump_optimizer/translations/en.json
index 64e36d0449..81dfd8d780 100644
--- a/custom_components/heatpump_optimizer/translations/en.json
+++ b/custom_components/heatpump_optimizer/translations/en.json
@@ -592,7 +592,8 @@
               "flow_heat_c": "Heating flow ceiling (°C)",
               "space_setpoint_power_feedback": "Follow the planned power on the measured draw",
               "space_setpoint_low_limit_entity": "Controller's minimum set-point sensor (optional)",
-              "space_setpoint_high_limit_entity": "Controller's maximum set-point sensor (optional)"
+              "space_setpoint_high_limit_entity": "Controller's maximum set-point sensor (optional)",
+              "space_setpoint_high_limit_c": "Controller's maximum set-point (°C, optional)"
             },
             "data_description": {
               "indoor_temp_entity": "Optional. The actual room temperature. Without it the optimizer trusts its own model, which drifts over time.",
@@ -603,7 +604,8 @@
               "flow_heat_c": "The water set-point written at full planned power, and the highest one written while the plan is in charge. 55 °C suits a supply target. For a Return temperature entity choose it above the highest return you see in normal heating plus the lift, and no higher than the controller accepts; on a low-temperature floor heating 35–40 °C may be a starting point to check against measurements. Below 30 °C is not offered: the gate that means off is 25 °C for a flow target and 20 °C for a return target. A space boost or Boost mode writes the set-point entity's own maximum (up to 70 °C) on every step instead; a value other than 55 °C set here caps that too, so set one on a low-temperature floor heating.",
               "space_setpoint_power_feedback": "On by default. Acts only with Pump duty control at Control, a Flow or Return temperature unit and a heat-pump power sensor; otherwise nothing changes. After a 5-minute start hold, the water set-point is nudged down while the measured draw is above the planned level and up while it is below, and held while it is within 10 %, instead of following the rising inlet water. Off writes the inlet plus the lift. Requirements on the controller: its heating hysteresis at most the lift (0.5 K on a Luxtronik, for example), or a stopped compressor is not started; its minimum return target below the heating-season return; its integration polling it at least every 10 minutes, and restoring its heating mode after a controller restart, since a controller can drop what was set when it goes unread (a Luxtronik Smart Home Interface, for one, drops every set value after 600 s without access); and no second tool writing the same registers (a Luxtronik, for one, then silently discards writes).",
               "space_setpoint_low_limit_entity": "Optional. A temperature sensor that reports the lowest value the controller accepts for the set-point entity above (for example a Luxtronik through ha-luxtronik-shi: \"Temperature: return target minimum\", input 10104). With it, Follow the planned power never sends a value below it, instead of finding the limit when the controller cuts a write. Used by that option alone; left empty, nothing changes.",
-              "space_setpoint_high_limit_entity": "Optional. A temperature sensor that reports the highest value the controller accepts for the set-point entity above (for example a Luxtronik through ha-luxtronik-shi: \"Temperature: return limit\", input 10103). With it, Follow the planned power never sends a value above it, instead of finding the limit when the controller cuts a write. Used by that option alone; left empty, nothing changes."
+              "space_setpoint_high_limit_entity": "Optional. A temperature sensor that reports the highest value the controller accepts for the set-point entity above (for example a Luxtronik through ha-luxtronik-shi: \"Temperature: return limit\", input 10103). No space water set-point above it is written: Follow the planned power, a boost and every heating step stay under it, instead of finding the limit when the controller cuts a write. With a maximum set-point typed below as well, the lower of the two applies; left empty, nothing changes.",
+              "space_setpoint_high_limit_c": "Optional. The highest value the pump accepts for the set-point entity above, where that is lower than the entity's own maximum. No space water set-point above it is written, a boost's included. With a maximum set-point sensor as well, the lower of the two applies. Left empty, the entity's own maximum applies."
             }
           },
           "plant": {
diff --git a/custom_components/heatpump_optimizer/translations/sv.json b/custom_components/heatpump_optimizer/translations/sv.json
index 42c981d30b..87e3212587 100644
--- a/custom_components/heatpump_optimizer/translations/sv.json
+++ b/custom_components/heatpump_optimizer/translations/sv.json
@@ -592,7 +592,8 @@
               "flow_heat_c": "Högsta framledning vid värme (°C)",
               "space_setpoint_power_feedback": "Följ planerad effekt efter uppmätt förbrukning",
               "space_setpoint_low_limit_entity": "Givare för styrenhetens lägsta börvärde (valfri)",
-              "space_setpoint_high_limit_entity": "Givare för styrenhetens högsta börvärde (valfri)"
+              "space_setpoint_high_limit_entity": "Givare för styrenhetens högsta börvärde (valfri)",
+              "space_setpoint_high_limit_c": "Styrenhetens högsta börvärde (°C, valfritt)"
             },
             "data_description": {
               "indoor_temp_entity": "Valfritt. Den verkliga rumstemperaturen. Utan den litar optimeringen på sin egen modell, som glider med tiden.",
@@ -603,7 +604,8 @@
               "flow_heat_c": "Vattenbörvärdet som skrivs vid full planerad effekt, och det högsta som skrivs medan planen styr. 55 °C passar ett framledningsmål. För en entitet med Returtemperatur väljs det över den högsta retur du ser vid normal uppvärmning plus höjningen, och inte högre än styrenheten accepterar; för en lågtemperatur-golvvärme kan 35–40 °C vara en startpunkt att kontrollera mot mätningar. Under 30 °C erbjuds inte: grinden som betyder av är 25 °C för ett framledningsmål och 20 °C för ett returmål. En rumsvärmeboost eller Boost-läget skriver i stället börvärdesentitetens eget maximum (högst 70 °C) vid varje steg; ett annat värde än 55 °C här begränsar även det, så ange ett för en lågtemperatur-golvvärme.",
               "space_setpoint_power_feedback": "På som standard. Verkar bara med Styrning av pumpens uppgift på Styrning, enheten Framlednings- eller Returtemperatur och en effektgivare för värmepumpen; annars ändras ingenting. Efter 5 minuters starthållning sänks vattenbörvärdet medan den uppmätta förbrukningen ligger över planerad nivå, höjs medan den ligger under och hålls inom 10 %, i stället för att följa det stigande inkommande vattnet. Av skriver inkommande vatten plus höjningen. Krav på styrenheten: dess värmehysteres högst höjningen (0,5 K på till exempel en Luxtronik), annars startas inte en stoppad kompressor; dess lägsta returmål under returen under eldningssäsongen; dess integration läser den minst var 10:e minut och återställer värmeläget efter en omstart av styrenheten, eftersom en styrenhet kan släppa det som satts när den inte läses (ett Luxtronik Smart Home Interface till exempel släpper alla satta värden efter 600 s utan åtkomst); och inget annat verktyg skriver samma register (en Luxtronik till exempel kastar då skrivningar tyst).",
               "space_setpoint_low_limit_entity": "Valfri. En temperaturgivare som rapporterar det lägsta värde styrenheten tar emot för börvärdesentiteten ovan (till exempel en Luxtronik via ha-luxtronik-shi: \"Temperature: return target minimum\", ingång 10104). Med den skickar Följ planerad effekt efter uppmätt förbrukning aldrig ett värde under det, i stället för att hitta gränsen först när styrenheten kapar en skrivning. Används bara av det alternativet; lämnas den tom ändras ingenting.",
-              "space_setpoint_high_limit_entity": "Valfri. En temperaturgivare som rapporterar det högsta värde styrenheten tar emot för börvärdesentiteten ovan (till exempel en Luxtronik via ha-luxtronik-shi: \"Temperature: return limit\", ingång 10103). Med den skickar Följ planerad effekt efter uppmätt förbrukning aldrig ett värde över det, i stället för att hitta gränsen först när styrenheten kapar en skrivning. Används bara av det alternativet; lämnas den tom ändras ingenting."
+              "space_setpoint_high_limit_entity": "Valfri. En temperaturgivare som rapporterar det högsta värde styrenheten tar emot för börvärdesentiteten ovan (till exempel en Luxtronik via ha-luxtronik-shi: \"Temperature: return limit\", ingång 10103). Inget framledningsbörvärde över det skrivs: Följ planerad effekt efter uppmätt förbrukning, en boost och varje uppvärmningssteg håller sig under det, i stället för att hitta gränsen först när styrenheten kapar en skrivning. Med ett högsta börvärde inskrivet nedan också gäller det lägre av de två; lämnas den tom ändras ingenting.",
+              "space_setpoint_high_limit_c": "Valfritt. Det högsta värde pumpen tar emot för börvärdesentiteten ovan, där det är lägre än entitetens eget maximum. Inget framledningsbörvärde över det skrivs, inte heller vid en boost. Med en givare för högsta börvärde också gäller det lägre av de två. Lämnas det tomt gäller entitetens eget maximum."
             }
           },
           "plant": {
diff --git a/dev/programme/delivery/3866.md b/dev/programme/delivery/3866.md
new file mode 100644
index 0000000000..c0fcb3a841
--- /dev/null
+++ b/dev/programme/delivery/3866.md
@@ -0,0 +1 @@
+- [#3866](https://github.com/tvofi/heatpump_optimizer/pull/3866) — **open**, R11-OWNER-FLOWCAP: clamp set-point writes to the entity range and add a manual high flow limit (R11-OWNER-FLOWCAP)
diff --git a/docs/architecture.md b/docs/architecture.md
index 17319c4fa4..a19277f197 100644
--- a/docs/architecture.md
+++ b/docs/architecture.md
@@ -5,7 +5,7 @@ integration does rather than how it is built, start with
 [how-it-works.md](how-it-works.md).
 
 The shape is a thin Home Assistant layer wrapped around a much larger core that
-knows nothing about Home Assistant: 98 modules, of which 34 import the
+knows nothing about Home Assistant: 99 modules, of which 34 import the
 `homeassistant` package at module level, one more touches it inside a single
 function, and the rest take numbers in and give numbers back. The glue reads
 entity states, writes actuators and persists learned state. Keeping those two
@@ -214,6 +214,8 @@ custom_components/heatpump_optimizer/
 │                         #   interval once the room passes its threshold
 ├── flow_lift.py          # Supply and return water: how far the real supply
 │                         #   sits from the model's own weather curve
+├── flow_limit.py         # The space water set-point's high limit: the lower
+│                         #   of the maximum set-point sensor and option
 ├── flow_meter.py         # The water flow sensor: thermal output from flow,
 │                         #   supply and return, when no power or frequency
 │                         #   signal exists
@@ -286,7 +288,7 @@ custom_components/heatpump_optimizer/
 
 ## The Home Assistant boundary
 
-34 of the 98 modules import `homeassistant` at module level: `__init__`,
+34 of the 99 modules import `homeassistant` at module level: `__init__`,
 `config_flow`, `coordinator`, `open_meteo`, `frontend`, the six entity
 platforms `sensor`, `binary_sensor`, `button`, `climate`, `switch`, `datetime`,
 and the supporting modules `accuracy`, `away`, `boost`, `currency`, `debugger`, `defrost`,
@@ -295,7 +297,7 @@ and the supporting modules `accuracy`, `away`, `boost`, `currency`, `debugger`,
 reaches for `homeassistant.util.dt` inside a function, as the fallback when no
 clock function was injected.
 
-The other 63 modules are deliberately free of it, so each can be driven
+The other 64 modules are deliberately free of it, so each can be driven
 directly by `tests/features.py` with no Home Assistant running. That matters
 because the failure mode of this integration is a *plausible* plan: a detector
 that never fires, or a watchdog that lets a flatline through, produces output
diff --git a/docs/configuration.md b/docs/configuration.md
index aeee5c2bed..4e734359dc 100644
--- a/docs/configuration.md
+++ b/docs/configuration.md
@@ -630,7 +630,8 @@ are on **Power and solar sensors**; mode / defrost / online / fault are on
 | Heating flow ceiling (`flow_heat_c`) | 55 °C | 30–70 °C, 0.5 steps | Shown when the unit above is *Flow* or *Return temperature*. The heating value at full planned power, and the highest heating value written while the plan is in charge. A space boost or Boost mode writes the set-point entity's own maximum instead (up to 70 °C), capped by a value here other than 55 °C. A stored value at or below the 25 °C gate is read as 55 °C. |
 | Follow the planned power on the measured draw (`space_setpoint_power_feedback`) | On | on / off | Shown when the unit above is *Flow* or *Return temperature*; acts only when a heat-pump power sensor is configured too. Closes the heating value on the measured draw (see [Pump duty control](#pump-duty-control)). Off writes the inlet plus the lift. |
 | Controller's minimum set-point sensor (`space_setpoint_low_limit_entity`) | none | a temperature sensor | Shown when the unit above is *Flow* or *Return temperature*. Optional: the lowest value the controller accepts for the set-point entity (for example a Luxtronik through ha-luxtronik-shi: “Temperature: return target minimum”, input 10104). *Follow the planned power* then never sends a value below it (see [Pump duty control](#pump-duty-control)). Empty changes nothing. |
-| Controller's maximum set-point sensor (`space_setpoint_high_limit_entity`) | none | a temperature sensor | Shown when the unit above is *Flow* or *Return temperature*. Optional: the highest value the controller accepts (for example a Luxtronik: “Temperature: return limit”, input 10103). *Follow the planned power* then never sends a value above it. Empty changes nothing. |
+| Controller's maximum set-point sensor (`space_setpoint_high_limit_entity`) | none | a temperature sensor | Shown when the unit above is *Flow* or *Return temperature*. Optional: the highest value the controller accepts (for example a Luxtronik: “Temperature: return limit”, input 10103). No space water set-point above it is written: *Follow the planned power*, a boost and every heating step stay under it. With a maximum set-point typed in the next row as well, the lower of the two applies. Empty changes nothing. |
+| Controller's maximum set-point (`space_setpoint_high_limit_c`) | none | 30–70 °C, 0.5 steps | Shown when the unit above is *Flow* or *Return temperature*. Optional: the highest value the pump accepts, typed by hand, for a set-point entity whose own maximum is higher than what the pump takes. No space water set-point above it is written, a boost's included. With the sensor in the row above as well, the lower of the two applies; one below the lowest heating value (the gate plus one step of the set-point entity) is left out and logged, and so is one below the entity's own minimum, which the gate already sits above. Empty: the entity's own maximum applies. |
 
 ### Power and solar sensors
 
@@ -889,7 +890,7 @@ writes, at every 15-minute plan step:
   write the set-point entity's own maximum on every step they cover,
   whatever power the plan booked for the step, capped by a heating flow
   ceiling set to anything but its 55 °C default and by the controller's
-  maximum set-point sensor when one is configured. An entity whose maximum it cannot read, or one above
+  maximum set-point, its sensor or the value typed by hand, the lower where both are set. An entity whose maximum it cannot read, or one above
   70 °C (a generic number helper), keeps the planned level instead. A boost
   lasts two hours and is not trimmed on the room temperature, so on a
   low-temperature floor heating set the heating flow ceiling to bound it.
diff --git a/tests/closures.json b/tests/closures.json
index 65f5750a3c..89fb6f7b1c 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -215,6 +215,7 @@
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
+   "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
    "custom_components/heatpump_optimizer/freq_control.py",
    "custom_components/heatpump_optimizer/frontend.py",
@@ -394,6 +395,7 @@
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
+   "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
    "custom_components/heatpump_optimizer/freq_control.py",
    "custom_components/heatpump_optimizer/frontend.py",
@@ -514,6 +516,7 @@
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
+   "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
    "custom_components/heatpump_optimizer/freq_control.py",
    "custom_components/heatpump_optimizer/grid_fee.py",
@@ -624,6 +627,7 @@
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
+   "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
    "custom_components/heatpump_optimizer/freq_control.py",
    "custom_components/heatpump_optimizer/grid_fee.py",
@@ -748,6 +752,7 @@
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
+   "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
    "custom_components/heatpump_optimizer/freq_control.py",
    "custom_components/heatpump_optimizer/grid_fee.py",
@@ -875,6 +880,7 @@
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
+   "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
    "custom_components/heatpump_optimizer/freq_control.py",
    "custom_components/heatpump_optimizer/frontend.py",
@@ -1017,6 +1023,7 @@
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
+   "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
    "custom_components/heatpump_optimizer/freq_control.py",
    "custom_components/heatpump_optimizer/grid_fee.py",
@@ -1149,6 +1156,7 @@
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
+   "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
    "custom_components/heatpump_optimizer/freq_control.py",
    "custom_components/heatpump_optimizer/frontend.py",
@@ -1293,6 +1301,7 @@
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
+   "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
    "custom_components/heatpump_optimizer/freq_control.py",
    "custom_components/heatpump_optimizer/frontend.py",
@@ -1682,6 +1691,7 @@
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
+   "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
    "custom_components/heatpump_optimizer/freq_control.py",
    "custom_components/heatpump_optimizer/frontend.py",
@@ -2225,6 +2235,7 @@
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
+   "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
    "custom_components/heatpump_optimizer/freq_control.py",
    "custom_components/heatpump_optimizer/frontend.py",
@@ -2429,6 +2440,7 @@
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
+   "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
    "custom_components/heatpump_optimizer/freq_control.py",
    "custom_components/heatpump_optimizer/frontend.py",
@@ -2591,6 +2603,7 @@
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
+   "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
    "custom_components/heatpump_optimizer/freq_control.py",
    "custom_components/heatpump_optimizer/frontend.py",
@@ -2742,6 +2755,7 @@
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
+   "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
    "custom_components/heatpump_optimizer/freq_control.py",
    "custom_components/heatpump_optimizer/frontend.py",
@@ -2939,6 +2953,7 @@
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
+   "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
    "custom_components/heatpump_optimizer/freq_control.py",
    "custom_components/heatpump_optimizer/grid_fee.py",
@@ -3115,6 +3130,7 @@
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
+   "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
    "custom_components/heatpump_optimizer/freq_control.py",
    "custom_components/heatpump_optimizer/frontend.py",
@@ -3517,6 +3533,7 @@
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
+   "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
    "custom_components/heatpump_optimizer/freq_control.py",
    "custom_components/heatpump_optimizer/frontend.py",
@@ -3700,6 +3717,7 @@
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
+   "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
    "custom_components/heatpump_optimizer/freq_control.py",
    "custom_components/heatpump_optimizer/grid_fee.py",
@@ -3811,6 +3829,7 @@
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
+   "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
    "custom_components/heatpump_optimizer/freq_control.py",
    "custom_components/heatpump_optimizer/grid_fee.py",
@@ -3974,6 +3993,7 @@
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
+   "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
    "custom_components/heatpump_optimizer/freq_control.py",
    "custom_components/heatpump_optimizer/frontend.py",
@@ -4077,6 +4097,7 @@
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
+   "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
    "custom_components/heatpump_optimizer/freq_control.py",
    "custom_components/heatpump_optimizer/frontend.py",
@@ -4215,6 +4236,7 @@
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
+   "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
    "custom_components/heatpump_optimizer/freq_control.py",
    "custom_components/heatpump_optimizer/grid_fee.py",
diff --git a/tests/config_flow_steps.py b/tests/config_flow_steps.py
index 1ce16fb27b..95e47de2e4 100644
--- a/tests/config_flow_steps.py
+++ b/tests/config_flow_steps.py
@@ -2791,8 +2791,9 @@ NO_DEFAULT = object()
 STORED_ARM_PAGES = ("entities", "comfort", "hot_water", "building")
 
 
-def entity_field_defaults(result):
-    """Every entity picker on a form, mapped to the value it presents.
+def entity_field_defaults(result, kinds=("EntitySelector",)):
+    """Every entity picker on a form (every field of a selector in ``kinds``),
+    mapped to the value it presents.
 
     A picker is pre-filled either from ``default`` or from
     ``description["suggested_value"]``, and the frontend shows and posts both
@@ -2807,7 +2808,7 @@ def entity_field_defaults(result):
     schema = result.get("data_schema")
     out = {}
     for key, value in _presented_fields(schema):
-        if type(value).__name__ != "EntitySelector":
+        if type(value).__name__ not in kinds:
             continue
         name = str(getattr(key, "schema", key))
         try:
@@ -2930,7 +2931,7 @@ async def entity_clear_survives_the_flow_manager():
     not_presented: dict[str, list[str]] = {}
     for step in pages:
         keys = [row.key for row in rows if row.step == step]
-        seed = {key: f"sensor.stored_{key}" for key in keys}
+        seed = {row.key: _stored_seed(row, row.key) for row in rows if row.step == step}
         # The wood block renders only with its gate on, and the gate is a
         # field of the same page: seeding it drives the gated slots too.
         seed[config_flow.CONF_WOOD_FURNACE_ENABLED] = True
@@ -4374,6 +4375,13 @@ def offered_entity_fields(result):
     return entity_field_defaults(result)
 
 
+def offered_clearable_fields(result):
+    """:func:`offered_entity_fields` and every number field too: the one
+    offered undefaulted (``space_setpoint_high_limit_c``) is a ``_STORED`` row
+    and clears the same way; a number with a default is never ``NO_DEFAULT``."""
+    return entity_field_defaults(result, ("EntitySelector", "NumberSelector"))
+
+
 def rendered_keys(result):
     """Every option key a rendered page presents, section nesting included."""
     schema = result.get("data_schema")
@@ -4500,12 +4508,16 @@ async def registry_drives_every_page():
     # named ``away_return_entity`` -- a key no option page has ever offered --
     # and nothing failed, because its only reader is a seven-key hand list
     # that does not mention it.
+    # The one number on the roster (``space_setpoint_high_limit_c``) is read
+    # with the pickers; the other undefaulted numbers are model parameters a
+    # page suggests from the learned model, not ``_STORED`` rows.
     two_armed = {}
     for page in pages:
         flow = bare_options(REGISTRY_SEED)
-        offered = offered_entity_fields(await getattr(flow, f"async_step_{page}")(None))
-        for key, default in offered.items():
-            if default is NO_DEFAULT:
+        shown = await getattr(flow, f"async_step_{page}")(None)
+        pickers = offered_entity_fields(shown)
+        for key, default in offered_clearable_fields(shown).items():
+            if default is NO_DEFAULT and (key in pickers or key == const.CONF_SPACE_SETPOINT_HIGH_LIMIT_C):
                 two_armed.setdefault(key, []).append(page)
     roster = set(Flow._OPTIONAL_ENTITY_KEYS)
     check(
@@ -4523,11 +4535,12 @@ async def registry_drives_every_page():
     per_page = {}
     for key, owners in two_armed.items():
         for page in owners:
-            per_page.setdefault(page, {})[key] = f"sensor.registry_{key}"
+            per_page.setdefault(page, {})[key] = (
+                51.0 if key == const.CONF_SPACE_SETPOINT_HIGH_LIMIT_C else f"sensor.registry_{key}")
     not_carried = {}
     for page, stored in sorted(per_page.items()):
         flow = bare_options({**REGISTRY_SEED, **stored})
-        rendered = offered_entity_fields(
+        rendered = offered_clearable_fields(
             await getattr(flow, f"async_step_{page}")(None)
         )
         wrong = {k: rendered.get(k) for k, v in stored.items() if rendered.get(k) != v}
@@ -7855,7 +7868,16 @@ def _page_stored_entities(step, base):
         )
         if row.default is config_flow._STORED
     ]
-    return {row.key: f"sensor.stored_{i}" for i, row in enumerate(rows)}
+    return {row.key: _stored_seed(row, i) for i, row in enumerate(rows)}
+
+
+def _stored_seed(row, tag):
+    """A distinct stored value for a ``_STORED`` row: an entity id for a
+    picker, an in-range number for the one optional number
+    (``space_setpoint_high_limit_c``), which clears the same way."""
+    if isinstance(row.widget, selector.NumberSelector):
+        return float(row.widget.config["min"]) + 1.0
+    return f"sensor.stored_{tag}"
 
 
 async def options_rejected_page_rerenders_the_clear():
diff --git a/tests/deployment_shape.py b/tests/deployment_shape.py
index 35be7f2db5..888dbc95e3 100644
--- a/tests/deployment_shape.py
+++ b/tests/deployment_shape.py
@@ -37,9 +37,9 @@ child from ``inspect.getfile``.
 
 COST OF THE SHAPE (#1218, round-5 D3-08). Materialising the shape copies the
 tracked package file by file (``_materialise``, below), and the gate's tracer
-records every read, so this lane's recorded closure is the package: all 117
+records every read, so this lane's recorded closure is the package: all 118
 files under ``custom_components/heatpump_optimizer/``, Python and non-Python
-alike (115 until R11-OUTSIDE-ROOMS-P3's ``room_history.py`` and ``room_record.py``, 114 until R11-OUTSIDE-ROOMS-P1's ``rooms.py``, 113 until R11-OUTSIDE-HONEST-STARTS-RUNS's ``runs.py``, 112 until #3616's ``slab_seed.py``, 111 until R10-START-COUNTER-EDGES's ``running_signal.py``, 110 until
+alike (117 until R11-OWNER-FLOWCAP's ``flow_limit.py``, 115 until R11-OUTSIDE-ROOMS-P3's ``room_history.py`` and ``room_record.py``, 114 until R11-OUTSIDE-ROOMS-P1's ``rooms.py``, 113 until R11-OUTSIDE-HONEST-STARTS-RUNS's ``runs.py``, 112 until #3616's ``slab_seed.py``, 111 until R10-START-COUNTER-EDGES's ``running_signal.py``, 110 until
 R10-ADVISOR-STEADY-START's ``whatif.py``, 109 until R10-DUTY-SWITCH-PLANNER-PRICE's
 ``duty_legs.py``, 108 until the supply-hold PR's ``supply_hold.py``, 107 until
 R10-DUTY-SWITCH-RESTART-LEARNING's ``duty_switch.py``, 78 until R9 F2.5's ``batchmath.py``, 79 until R9 UI-1's six brand
diff --git a/tests/features.py b/tests/features.py
index 658969c8a4..695dbc7b27 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -65123,6 +65123,206 @@ R.check(
     and 90 > _PA_FLOW_HEAT_C_MAX,
     f"{_pa_bl_offer=}",
 )
+# R11-OWNER-FLOWCAP (tvofi, 2026-11-22: "add an option to manually configure the
+# high-limit if there is no such sensor"). The space water set-point's high limit is
+# flow_limit's: the controller's sensor and the manual option, each judged alone (a
+# limit under the lowest heating write is dropped, one equal to it kept), then the
+# lower of the two. The gate is bounded up to the entity's minimum, so a limit under
+# that minimum is under the lowest heating write too, and dropped. Heating
+# writes, a boost and the feedback loop stay under it; the gate, the draw-range
+# ceiling and an indoor unit do not read it. Synthetic numbers throughout; 48 is
+# the fixture's hot-water write, so no limit here is 48.
+from heatpump_optimizer import flow_limit as _fl  # noqa: E402
+from heatpump_optimizer import draw_range as _fl_dr  # noqa: E402
+from heatpump_optimizer.const import CONF_SPACE_SETPOINT_HIGH_LIMIT_C as _FL_KEY  # noqa: E402
+
+_fl_pure = {
+    "both, option lower": _fl.high_limit(52.0, 46.0, 27.0),
+    "both, sensor lower": _fl.high_limit(52.0, 58.0, 27.0),
+    "option only": _fl.high_limit(None, 46.0, 27.0),
+    "neither": _fl.high_limit(None, None, 27.0),
+    "sensor under lowest": _fl.high_limit(26.0, 46.0, 27.0),
+    "option under lowest": _fl.high_limit(52.0, 26.0, 27.0),
+    "sensor at lowest": _fl.high_limit(27.0, None, 27.0),
+}
+R.check(
+    "R11-OWNER-FLOWCAP: the lower of sensor and option binds; a source under the lowest heating write is "
+    "dropped and named with the other in force, one equal to it kept; null control: neither source is no limit",
+    {k: tuple(v) for k, v in _fl_pure.items()} == {
+        "both, option lower": (46.0, ()), "both, sensor lower": (52.0, ()),
+        "option only": (46.0, ()), "neither": (None, ()),
+        "sensor under lowest": (46.0, ("sensor",)), "option under lowest": (52.0, ("option",)),
+        "sensor at lowest": (27.0, ()),
+    },
+    f"{_fl_pure=}",
+)
+_fl_opts = [_fl.option_c(v) for v in (29.5, 30, 70, 70.5, "x", None, "46")]
+R.check(
+    "R11-OWNER-FLOWCAP: the option reads only inside the 30-70 degC the options flow offers; "
+    "outside it, not a number, or unset is no option",
+    _fl_opts == [None, 30.0, 70.0, None, None, None, 46.0],
+    f"{_fl_opts=}",
+)
+
+
+def _fl_coord(kw=1.0, how=None, attrs=None, option=None, sensor=None, low_sensor=None, unit="flow"):
+    """One pass on a two-step space plan at ``kw`` of a 0.4-2.0 kW band; the space writes."""
+    coord = _PaCoord(_PA_TUYA, duties="ss")
+    coord.hass.states.set("number.water_set", FakeState("40", attributes=attrs or {"min": 25, "max": 70}))
+    coord._optimization_result.power_schedule = [kw, kw]
+    coord._thermal_params = _PaNS(dhw_setpoint=48.0, dhw_max_temp=48.0, dhw_cycle_temp=None,
+                                  min_electrical_power=0.4, max_electrical_power=2.0)
+    extra = {"space_setpoint_unit": unit}
+    if option is not None:
+        extra[_FL_KEY] = option
+    for key, entity, value in (("space_setpoint_high_limit_entity", "sensor.fl_hi", sensor),
+                               ("space_setpoint_low_limit_entity", "sensor.fl_lo", low_sensor)):
+        if value is not None:
+            extra[key] = entity
+            coord.hass.states.set(entity, FakeState(str(value), unit="°C"))
+    with_config(coord, extra)
+    if how == "channel":
+        boost_mod.held_for(coord).set("space", True, _PA_T0)
+    _pa_run(coord, 1)
+    return coord, [v for d, _sv, v in coord.writes() if d == "number" and v != 48.0]
+
+
+_fl_boost = {
+    name: _fl_coord(how="channel", **kw)[1]
+    for name, kw in {
+        "option 46": {"option": 46}, "sensor 52, option 46": {"sensor": 52, "option": 46},
+        "sensor 52, option 58": {"sensor": 52, "option": 58},
+        "sensor unavailable, option 46": {"sensor": "unavailable", "option": 46},
+        "crossed pair, option 58": {"sensor": 52, "low_sensor": 60, "option": 58},
+        "option 70 over a 60 maximum": {"option": 70, "attrs": {"min": 25, "max": 60}},
+        "neither": {},
+    }.items()
+}
+R.check(
+    "R11-OWNER-FLOWCAP: a space boost writes the high limit: the option, the lower of sensor and option, "
+    "the option where the sensor is unavailable or its pair crossed, and never above the entity's "
+    "maximum; null control: with neither it writes the entity's maximum, 70",
+    _fl_boost == {
+        "option 46": [46], "sensor 52, option 46": [46], "sensor 52, option 58": [52],
+        "sensor unavailable, option 46": [46], "crossed pair, option 58": [58],
+        "option 70 over a 60 maximum": [60], "neither": [70],
+    },
+    f"{_fl_boost=}",
+)
+_fl_top = {o: _fl_coord(kw=2.0, option=o)[1] for o in (46, 58, None)}
+R.check(
+    "R11-OWNER-FLOWCAP: a band-top heating step is held at an option under the 55 degC heating "
+    "ceiling; null controls: an option above the ceiling and no option both write the ceiling",
+    _fl_top == {46: [46], 58: [55], None: [55]},
+    f"{_fl_top=}",
+)
+_fl_min = {}
+for _name, _attrs in (("min 40", {"min": 40, "max": 70}), ("min 41, step 5", {"min": 41, "max": 70, "step": 5})):
+    _c, _w = _fl_coord(how="channel", option=35, attrs=_attrs)
+    _fl_min[_name] = (_w, _pa.state_for(_c).written["space_setpoint"][0])
+_c, _w = _fl_coord(how="channel", option=45, attrs={"min": 40, "max": 70})
+_fl_min["option 45 over min 40"] = (_w, _pa.state_for(_c).written["space_setpoint"][0])
+R.check(
+    "R11-OWNER-FLOWCAP: an option under the entity's minimum (35 under 40, and under 41 on a 5-degree step) "
+    "is under the gate the minimum lifts, so it is dropped and a boost writes the entity's maximum, never a "
+    "value under the minimum, with the record equal to what was sent; null control: an option over the "
+    "minimum is written as itself",
+    _fl_min == {"min 40": ([70], 70.0), "min 41, step 5": ([70], 70.0), "option 45 over min 40": ([45], 45.0)},
+    f"{_fl_min=}",
+)
+def _fl_ceiling_coord(option):
+    coord = _PaCoord(_PA_TUYA, duties="ss")
+    coord.hass.states.set("number.water_set", FakeState("40", attributes={"min": 25, "max": 60}))
+    coord._optimization_result.power_schedule = [2.0, 2.0]
+    coord._thermal_params = _PaNS(dhw_setpoint=48.0, dhw_max_temp=48.0, dhw_cycle_temp=None,
+                                  min_electrical_power=0.4, max_electrical_power=2.0)
+    extra = {"space_setpoint_unit": "flow", "flow_heat_c": 70}
+    if option is not None:
+        extra[_FL_KEY] = option
+    with_config(coord, extra)
+    _pa_run(coord, 1)
+    return [v for d, _sv, v in coord.writes() if d == "number" and v != 48.0], \
+        _pa.state_for(coord).written["space_setpoint"][0]
+
+
+_fl_over = {o: _fl_ceiling_coord(o) for o in (65, 50, None)}
+R.check(
+    "R11-OWNER-FLOWCAP: a limit above the entity's own maximum never lifts a heating write past it: a "
+    "band-top step under a 70 degC heating ceiling with option 65 on a 60 maximum writes and records 60, "
+    "not 65 (which the entity would read back as 60, an edit); option 50 writes 50; null control: no "
+    "option writes the maximum, 60",
+    _fl_over == {65: ([60], 60.0), 50: ([50], 50.0), None: ([60], 60.0)},
+    f"{_fl_over=}",
+)
+_fl_part = {o: _fl_coord(kw=1.2, option=o)[1] for o in (46, None)}
+R.check(
+    "R11-OWNER-FLOWCAP: a partial level maps on a band whose top is the limit, so it sits below both the "
+    "limit and the unlimited level's value, not on the limit itself; null control: no option maps on 55",
+    len(_fl_part[46]) == 1 and len(_fl_part[None]) == 1
+    and _fl_part[46][0] < min(46, _fl_part[None][0]),
+    f"{_fl_part=}",
+)
+_fl_hold = {}
+for _o in (30, None):
+    _c = _fl_coord(option=_o)[0]
+    _fl_hold[_o] = _pa._flow_target(_c.arbiter_inputs(), None, _PA_T0)
+R.check(
+    "R11-OWNER-FLOWCAP: the fallback's hold stays under the limit (option 30 holds 30); null control: no "
+    "option holds above it",
+    _fl_hold[30] == 30.0 and _fl_hold[None] is not None and _fl_hold[None] > 30.0,
+    f"{_fl_hold=}",
+)
+_fl_room = {}
+for _o in (46, None):
+    _c, _w = _fl_coord(option=_o, unit="indoor", attrs={"min": 5, "max": 30})
+    _fl_room[_o] = (_w, _pa._space_limit_c(_c.arbiter_inputs()))
+_fl_flow_limit = _pa._space_limit_c(_fl_coord(option=46)[0].arbiter_inputs())
+R.check(
+    "R11-OWNER-FLOWCAP: an indoor unit reads no high limit and writes the same room value with the option "
+    "stored as without; null control: the same option on a flow unit is its limit, 46",
+    _fl_room[46] == (_fl_room[None][0], None) and _fl_room[None][1] is None and _fl_flow_limit == 46.0,
+    f"{_fl_room=} {_fl_flow_limit=}",
+)
+_fl_cmd = {o: _pa.flow_command(_fl_coord(kw=2.0, option=o)[0]) for o in (46, None)}
+_fl_at_top = {o: c is not None and c.written_c >= c.ceiling_c - _fl_dr.CEILING_TOLERANCE_K for o, c in _fl_cmd.items()}
+R.check(
+    "R11-OWNER-FLOWCAP: a band-top write capped at the option is not read as commanding the pump's top "
+    "draw (written 46 under the 55 ceiling draw_range keys on); null control: with no option the band-top "
+    "write is the ceiling",
+    _fl_at_top == {46: False, None: True}
+    and (_fl_cmd[46].written_c, _fl_cmd[46].ceiling_c) == (46.0, 55.0),
+    f"{_fl_cmd=}",
+)
+
+
+def _fl_loop_hi(**kw):
+    coord = _fl_coord(**kw)[0]
+    run = _pa.FeedbackRun(_PA_T0, 40.0, _PA_T0)
+    return _pa._feedback_bounds(_pa.state_for(coord), run, coord.arbiter_inputs(), 35.0)[1]
+
+
+_fl_loop = {"option 46": _fl_loop_hi(option=46), "sensor 52, option 58": _fl_loop_hi(sensor=52, option=58),
+            "neither": _fl_loop_hi()}
+R.check(
+    "R11-OWNER-FLOWCAP: the feedback loop's ceiling is the high limit (the option, the lower of the two); "
+    "null control: with neither it is the 55 degC heating ceiling",
+    _fl_loop == {"option 46": 46.0, "sensor 52, option 58": 52.0, "neither": 55.0},
+    f"{_fl_loop=}",
+)
+_fl_row = [row for row in _pa_cf._OPTION_FIELDS if row.key == _FL_KEY]
+_fl_fit = _pa_cf._fit_stored_values(__import__("voluptuous").Schema(
+    {__import__("voluptuous").Optional(_FL_KEY, description={"suggested_value": 80.0}): _fl_row[0].widget}))[1]
+_fl_fit_in = _pa_cf._fit_stored_values(__import__("voluptuous").Schema(
+    {__import__("voluptuous").Optional(_FL_KEY, description={"suggested_value": 46.0}): _fl_row[0].widget}))[1]
+R.check(
+    "R11-OWNER-FLOWCAP: the option row offers 30 to 70 degC with no default, and a stored 80 widens it and "
+    "is named for stored_value_out_of_range; null control: a stored 46 widens nothing",
+    len(_fl_row) == 1 and (_fl_row[0].widget.config["min"], _fl_row[0].widget.config["max"]) == (30.0, 70.0)
+    and _fl_row[0].default is _pa_cf._STORED and _fl_fit == [_FL_KEY] and _fl_fit_in == [],
+    f"{_fl_row=} {_fl_fit=} {_fl_fit_in=}",
+)
+
+
 _pa_bl_fb, _ = _pa_boost_level("ss", 1.0, "channel", power_meter=True)
 _pa_bl_fb_on = _pa._feedback_on(_pa_bl_fb.arbiter_inputs(), "space", _PA_T0 + timedelta(minutes=1),
                                 boost_mod.held_for(_pa_bl_fb))
@@ -79190,7 +79390,7 @@ from heatpump_optimizer import inputs as _bst_in  # noqa: E402
 def _bst_sent(value, attrs=None, unit="°C", entity="number.bst_q"):
     hass = FakeHass({entity: FakeState("40", unit=unit, attributes=attrs or {})})
     _bst_aio.run(_bst_in.write_setpoint(hass, entity, value))
-    return [data["value" if not entity.startswith("climate") else "temperature"]
+    return [data["value" if entity.startswith("number") else "temperature"]
             for _d, _s, data in hass.services.calls]
 
 
@@ -79207,6 +79407,69 @@ R.check(
     "null control: an already-whole write sends the same whole number",
     _bst_sent(35.0) == [35] and _bst_sent(35) == [35],
 )
+# The entity's own range binds at that same one call, read at write time,
+# whatever the caller (owner item: a flow set-point written above the pump's
+# maximum). A number's ``min``/``max``, a climate or water heater's
+# ``min_temp``/``max_temp``, in the entity's own unit; the maximum rounds
+# down onto the step and the minimum up, so the value sent is one the
+# entity accepts. A range with its ends crossed is clamped to the maximum.
+R.check(
+    "a set-point above the entity's maximum is sent as the maximum, below its "
+    "minimum as the minimum: a number's min/max and a climate's min_temp/max_temp",
+    _bst_sent(65.0, {"min": 5, "max": 62}) == [62]
+    and _bst_sent(3.0, {"min": 5, "max": 62}) == [5]
+    and _bst_sent(65.0, {"min_temp": 5, "max_temp": 62}, entity="climate.bst_q") == [62]
+    and _bst_sent(65.0, {"min_temp": 5, "max_temp": 62}, entity="water_heater.bst_q") == [62],
+    f"{_bst_sent(65.0, {'min': 5, 'max': 62})} {_bst_sent(3.0, {'min': 5, 'max': 62})} "
+    f"{_bst_sent(65.0, {'min_temp': 5, 'max_temp': 62}, entity='climate.bst_q')}",
+)
+R.check(
+    "the range ends land on the step the entity accepts: a maximum off the step "
+    "rounds down, a minimum off it rounds up; crossed ends send the maximum",
+    _bst_sent(65.0, {"max": 63, "step": 5}) == [60]
+    and _bst_sent(10.0, {"min": 22, "step": 5}) == [25]
+    and _bst_sent(50.0, {"min": 60, "max": 40}) == [40],
+    f"{_bst_sent(65.0, {'max': 63, 'step': 5})} {_bst_sent(10.0, {'min': 22, 'step': 5})} "
+    f"{_bst_sent(50.0, {'min': 60, 'max': 40})}",
+)
+R.check(
+    "null control: a value inside the range, an entity stating no range, a "
+    "non-numeric bound and an entity with no state are sent unchanged",
+    _bst_sent(45.0, {"min": 5, "max": 62}) == [45]
+    and _bst_sent(65.0) == [65]
+    and _bst_sent(65.0, {"max": "unknown"}) == [65]
+    and (lambda h: (_bst_aio.run(_bst_in.write_setpoint(h, "number.bst_none", 65.0)),
+                    [d["value"] for _d, _s, d in h.services.calls])[1])(FakeHass({})) == [65],
+)
+
+
+def _bst_c_sent(value_c, attrs, unit):
+    hass = FakeHass({"number.bst_q": FakeState("100", unit=unit, attributes=attrs)})
+    _bst_aio.run(_bst_in.write_setpoint_c(hass, "number.bst_q", value_c))
+    return [data["value"] for _d, _s, data in hass.services.calls]
+
+
+R.check(
+    "a degC write to a Fahrenheit entity is clamped in the entity's own unit: "
+    "65 degC (149 degF) to a 140 degF maximum sends 140",
+    _bst_c_sent(65.0, {"max": 140}, "°F") == [140],
+    f"{_bst_c_sent(65.0, {'max': 140}, '°F')}",
+)
+
+
+def _bst_valve_sent(target_c, attrs):
+    from heatpump_optimizer import coordinator as _bst_cmod
+    hass = FakeHass({"number.bst_valve": FakeState("40", unit="°C", attributes=attrs)})
+    _bst_aio.run(_bst_cmod._valve_write_problem(hass, "number.bst_valve", target_c))
+    return [data["value"] for _d, _s, data in hass.services.calls]
+
+
+R.check(
+    "a production caller that bounds nothing itself, the mixing-valve write, is "
+    "held inside the entity's maximum by the one call",
+    _bst_valve_sent(65.0, {"max": 62}) == [62] and _bst_valve_sent(45.0, {"max": 62}) == [45],
+    f"{_bst_valve_sent(65.0, {'max': 62})} {_bst_valve_sent(45.0, {'max': 62})}",
+)
 
 
 def _bst_q(value_c, rounding="nearest", lo=None, hi=None, attrs=None, unit="°C"):
@@ -91885,11 +92148,27 @@ R.check(
     "the loop",
     _fb_sim(limits=(None, _fb_old), **_FB_STEP_UP)["writes"] == _fb_limit_hi["writes"],
 )
-# The limits act on the loop alone (I1, I3): today's target is not moved by
-# them, so an install the loop does not act on writes the same with them.
+# The limits act on the loop alone (I1, I3), but for the high limit: today's
+# target is not moved by the low one, and R11-OWNER-FLOWCAP (owner ruling,
+# 2026-11-22) holds every heating write at or under the high one, which is the
+# most the pump accepts. So an install the loop does not act on writes the same
+# with both sensors as with neither wherever that write sits under the high
+# limit, and the limit where it sat above; an indoor unit writes the same.
+
+
+def _fb_capped(limited, blind, high):
+    """``limited`` is ``blind`` with every value above ``high`` held at it, a
+    held value that repeats the last one sent not sent again."""
+    want = []
+    for minute, sent, _ret in blind:
+        if not want or want[-1][1] != min(sent, high):
+            want.append((minute, min(sent, high)))
+    return bool(blind) and [(m, v) for m, v, _r in limited] == want
+
+
 _fb_limit_cells = {
-    label: _fb_sim(minutes=60, limits=(27.0, 27.6), **kw)["writes"]
-    == _fb_sim(minutes=60, **kw)["writes"]
+    label: _fb_capped(_fb_sim(minutes=60, limits=(27.0, 27.6), **kw)["writes"],
+                      _fb_sim(minutes=60, **kw)["writes"], 99.0 if label == "indoor" else 27.6)
     for label, kw in (
         ("indoor", {"unit": "indoor"}),
         ("no power entity", {"power_entity": False}),
@@ -91897,8 +92176,9 @@ _fb_limit_cells = {
     )
 }
 R.check(
-    "R10-WATER-SETPOINT-FEEDBACK part 3 I1: an indoor unit, no power entity or the option "
-    "off writes the same with both limit sensors as with neither",
+    "R10-WATER-SETPOINT-FEEDBACK part 3 I1: an indoor unit writes the same with both limit "
+    "sensors as with neither; no power entity or the option off writes the same but held "
+    "at the 27.6 degC high limit (R11-OWNER-FLOWCAP)",
     all(_fb_limit_cells.values()),
     f"same: {_fb_limit_cells}",
 )
@@ -91999,8 +92279,9 @@ R.check(
 )
 # The sibling write paths of the space set-point (the indoor target, today's
 # open-loop target with the loop off or unmetered, the gate of a step that
-# does not heat, the start hold) read neither sensor: a high limit that binds
-# the loop, and one at the gate, change none of their writes.
+# does not heat, the start hold) read no loop bound: a high limit at the gate,
+# or below it, changes none of their writes, and one that binds the loop holds
+# a heating write at it and changes nothing under it (R11-OWNER-FLOWCAP).
 _FB_SIBLINGS = (
     ("indoor", {"unit": "indoor", "minutes": 60}),
     ("no power entity", {"power_entity": False, "minutes": 60}),
@@ -92010,13 +92291,15 @@ _FB_SIBLINGS = (
 )
 _fb_sibling_blind = {label: _fb_sim(**kw)["writes"] for label, kw in _FB_SIBLINGS}
 _fb_sibling_same = {
-    (label, high): _fb_sim(limits=(None, high), **kw)["writes"] == _fb_sibling_blind[label]
+    (label, high): _fb_capped(_fb_sim(limits=(None, high), **kw)["writes"],
+                              _fb_sibling_blind[label], high if label != "indoor" and high > 20.0 else 99.0)
     for label, kw in _FB_SIBLINGS for high in (24.0, 20.0, 15.0)
 }
 R.check(
     "R10-WATER-SETPOINT-FEEDBACK part 3 I1: the indoor target, an unmetered or switched-off "
     "loop, a step that does not heat and the start hold each write the same under a high "
-    "limit that binds the loop, one at the gate and one below it as with no sensor",
+    "limit at the gate or below it as with no sensor, and under one that binds the loop the "
+    "same but held at it (R11-OWNER-FLOWCAP)",
     all(_fb_sibling_same.values()) and all(_fb_sibling_blind.values()),
     f"same: {_fb_sibling_same}, writes { {k: len(v) for k, v in _fb_sibling_blind.items()} }",
 )
diff --git a/tests/mutation_ledger/killed_by/inputs.py/setpoint_range_c.RETURN_DEL.703db2ba.json b/tests/mutation_ledger/killed_by/inputs.py/setpoint_range_c.RETURN_DEL.703db2ba.json
deleted file mode 100644
index bf902d7b31..0000000000
--- a/tests/mutation_ledger/killed_by/inputs.py/setpoint_range_c.RETURN_DEL.703db2ba.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/inputs.py:setpoint_range_c RETURN_DEL 703db2ba",
-  "killed_by": "tests/guard_pins.py",
-  "old": "    return temperature_c(attrs.get(low_key), unit), temperature_c(attrs.get(high_key), unit)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 694120d5aa296b65c7d7be097f8684e7bc3b5f61: RETURN_DEL (`pass`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.BOOLOP.e74f8c8c.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.BOOLOP.e74f8c8c.json
deleted file mode 100644
index a7763a6b16..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.BOOLOP.e74f8c8c.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_boost_ceiling_c BOOLOP e74f8c8c",
-  "killed_by": "tests/features.py",
-  "old": "    if limit is not None and limit > _gate_floor_c(inp.config):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if limit is not None or limit > _gate_floor_c(inp.config):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.CMP_BOUND.e74f8c8c.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.CMP_BOUND.e74f8c8c.json
deleted file mode 100644
index 3aeba63c75..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.CMP_BOUND.e74f8c8c.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_boost_ceiling_c CMP_BOUND e74f8c8c",
-  "killed_by": "tests/features.py",
-  "old": "    if limit is not None and limit > _gate_floor_c(inp.config):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if limit is not None and limit >= _gate_floor_c(inp.config):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.GUARD_OFF.e74f8c8c.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.GUARD_OFF.e74f8c8c.json
deleted file mode 100644
index 7127158872..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.GUARD_OFF.e74f8c8c.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_boost_ceiling_c GUARD_OFF e74f8c8c",
-  "killed_by": "tests/features.py",
-  "old": "    if limit is not None and limit > _gate_floor_c(inp.config):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_feedback_bounds.BOOLOP.9ec2e031.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_feedback_bounds.BOOLOP.9ec2e031.json
deleted file mode 100644
index dfc8deabb8..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_feedback_bounds.BOOLOP.9ec2e031.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_feedback_bounds BOOLOP 9ec2e031",
-  "killed_by": "tests/features.py",
-  "old": "    highs += [v for v in (rec.cut_hi_c, high) if v is not None and v >= lowest]",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`highs += [v for v in (rec.cut_hi_c, high) if v is not None or v >= lowest]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_feedback_bounds.CMP_BOUND.9ec2e031.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_feedback_bounds.CMP_BOUND.9ec2e031.json
deleted file mode 100644
index 002f2d41fd..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_feedback_bounds.CMP_BOUND.9ec2e031.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_feedback_bounds CMP_BOUND 9ec2e031",
-  "killed_by": "tests/features.py",
-  "old": "    highs += [v for v in (rec.cut_hi_c, high) if v is not None and v >= lowest]",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`highs += [v for v in (rec.cut_hi_c, high) if v is not None and v > lowest]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_flow_target.RETURN_DEL.e1fd0819.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_flow_target.RETURN_DEL.e1fd0819.json
deleted file mode 100644
index 46bf44b024..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_flow_target.RETURN_DEL.e1fd0819.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_flow_target RETURN_DEL e1fd0819",
-  "killed_by": "tests/features.py",
-  "old": "    return _bounded(inp, \"space_setpoint\", hold, _gate_floor_c(inp.config))",
-  "reason": "Recorded by applying the mutant on feat/water-setpoint-lift-ceiling (gate fix, over e0d2751f6): RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 of 4991 to rc=1 failed=12 of 4991: every baseline-hold check (the rated 35 degC, the curve above it, the ceiling cap, and the return target's hold less the rated spread, D5) reads None."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_inside_silent.BOOLOP.6f93e870.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_inside_silent.BOOLOP.6f93e870.json
deleted file mode 100644
index c4bc06bcfd..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_inside_silent.BOOLOP.6f93e870.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_inside_silent BOOLOP 6f93e870",
-  "killed_by": "tests/features.py",
-  "old": "    return actions is not None and int(actions[0]) == quiet_windows.ACTION_SILENT",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 6001b09a557259f37319b400d219cf83e02c563f: BOOLOP (`return actions is not None or int(actions[0]) == quiet_windows.ACTION_SILENT`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_inside_silent.RETURN_DEL.6f93e870.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_inside_silent.RETURN_DEL.6f93e870.json
deleted file mode 100644
index 0acf1de45f..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_inside_silent.RETURN_DEL.6f93e870.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_inside_silent RETURN_DEL 6f93e870",
-  "killed_by": "tests/features.py",
-  "old": "    return actions is not None and int(actions[0]) == quiet_windows.ACTION_SILENT",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 6001b09a557259f37319b400d219cf83e02c563f: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_silent_target.GUARD_OFF.6ad8ff62.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_silent_target.GUARD_OFF.6ad8ff62.json
deleted file mode 100644
index 3238a12b8a..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_silent_target.GUARD_OFF.6ad8ff62.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_silent_target GUARD_OFF 6ad8ff62",
-  "killed_by": "tests/features.py",
-  "old": "    if not _silent_rows(spec):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 6001b09a557259f37319b400d219cf83e02c563f: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_silent_target.RETURN_DEL.b9ef128b.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_silent_target.RETURN_DEL.b9ef128b.json
deleted file mode 100644
index 8a868ef28b..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_silent_target.RETURN_DEL.b9ef128b.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_silent_target RETURN_DEL b9ef128b",
-  "killed_by": "tests/structure.py",
-  "old": "    return _inside_silent(spec, cfg.quiet_off_windows, now)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 816547efe270a08e18e3b92f52185fe8c1fee2ef: RETURN_DEL (`pass`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_silent_rows.RETURN_DEL.3b1c1ccd.json b/tests/mutation_ledger/killed_by/quiet_windows.py/silent_rows.RETURN_DEL.3b1c1ccd.json
similarity index 72%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_silent_rows.RETURN_DEL.3b1c1ccd.json
rename to tests/mutation_ledger/killed_by/quiet_windows.py/silent_rows.RETURN_DEL.3b1c1ccd.json
index 4598d96d4c..132dbeb27f 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_silent_rows.RETURN_DEL.3b1c1ccd.json
+++ b/tests/mutation_ledger/killed_by/quiet_windows.py/silent_rows.RETURN_DEL.3b1c1ccd.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_silent_rows RETURN_DEL 3b1c1ccd",
+  "anchor": "custom_components/heatpump_optimizer/quiet_windows.py:silent_rows RETURN_DEL 3b1c1ccd",
   "killed_by": "tests/features.py",
   "old": "    return actions is not None",
   "reason": "Recorded by `mutation_table.py --pin-killed` against 6001b09a557259f37319b400d219cf83e02c563f: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
diff --git a/tests/mutation_ledger/survivor_triage/pump_arbiter.py/_silent_rows.GUARD_OFF.eefa4cf2.json b/tests/mutation_ledger/survivor_triage/quiet_windows.py/silent_rows.GUARD_OFF.eefa4cf2.json
similarity index 85%
rename from tests/mutation_ledger/survivor_triage/pump_arbiter.py/_silent_rows.GUARD_OFF.eefa4cf2.json
rename to tests/mutation_ledger/survivor_triage/quiet_windows.py/silent_rows.GUARD_OFF.eefa4cf2.json
index 8d1c1edfd2..4a07d09f93 100644
--- a/tests/mutation_ledger/survivor_triage/pump_arbiter.py/_silent_rows.GUARD_OFF.eefa4cf2.json
+++ b/tests/mutation_ledger/survivor_triage/quiet_windows.py/silent_rows.GUARD_OFF.eefa4cf2.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_silent_rows GUARD_OFF eefa4cf2",
+  "anchor": "custom_components/heatpump_optimizer/quiet_windows.py:silent_rows GUARD_OFF eefa4cf2",
   "old": "    if not isinstance(spec, str) or not spec.strip():",
   "reason": "GUARD_OFF (`if False`). quiet_windows.step_actions on the Monday anchor returns None for None, '', '   ', and the non-str 3, which is the same False this guard returns. Measured: PYTHONPATH=tests/hastub:custom_components python3 calling step_actions(datetime(2026, 1, 5, tzinfo=timezone.utc), 4, 0.25, spec, None) for those four specs. A real window still comes back as an array from that function; the RETURN_DEL of `return actions is not None` is the site features.py kills.",
   "verdict": "equivalent"
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 87b424eaa0..1252b0d5ed 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -16,9 +16,9 @@
  "max_method_loc": 373,
  "methods_over_150": 14,
  "methods_over_200": 7,
- "module_excess_loc": 21779,
+ "module_excess_loc": 21766,
  "name_kept_members": 38,
- "recorded_at": "4ebd430fbff9a7b19582ca530a817f34abbafa16",
+ "recorded_at": "3a98735a7ecc59e7ecc095a0429cdf6251d956ec",
  "seam_cut_total": 413,
  "unloaded_package_imports": 14
 }

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
