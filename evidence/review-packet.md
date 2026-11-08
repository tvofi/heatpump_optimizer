# Review packet #3308
head: 6016f9dd6e0ff482d0e140946721657357653726
base: 6188936a8bdc58b510ecb8794ad86350283c49a7

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=128700836363 success
arch-score / arch-score id=128753207395 success
arm id=128700336034 skipped
budget-raise-gate / budget-raise-gate id=128753204180 success
cancel-superseded id=128753196432 success
codeql id=128721563969 skipped
codeql / Analyze (actions) id=128753170500 success
codeql / Analyze (javascript-typescript) id=128753208964 success
codeql / Analyze (python) id=128753201168 success
gate id=128753622846 success
governance id=128721563853 skipped
governance / delivery-status id=128753199661 success
governance / delivery-status-publish id=128753212061 skipped
governance / env-matrix id=128753199247 success
governance / instrument-self-tests id=128753171722 success
governance / policy-docs id=128753198042 success
governance / record id=128753171969 skipped
governance / wave-script id=128753208529 success
hassfest id=128721593226 skipped
hassfest / hassfest id=128753198426 success
kernel-points id=128753171614 skipped
pr-contract id=128721564187 skipped
pr-contract / pr-contract id=128753384570 success
prelude id=128753203400 success
refresh id=128753171472 success
tests id=128721564042 skipped
tests / arch-instrument id=128753172853 success
tests / briefs id=128753205668 success
tests / browser id=128753172528 success
tests / ci-ratchet id=128753173386 skipped
tests / claims-autofix id=128753173737 skipped
tests / closure-scope id=128753213876 success
tests / closures id=128753173114 success
tests / closures-autofix id=128753173404 skipped
tests / coverage id=128753172749 success
tests / coverage-ratchet id=128753173543 success
tests / fast (3.14) id=128753172843 success
tests / graders-head-copy id=128753173250 success
tests / lane-proofs id=128753173752 success
tests / mutation id=128753172372 success
tests / mutation-autofix id=128753173405 skipped
tests / mutation-pins id=128753172384 skipped
tests / nightly-ha (2025.2.0) id=128753172746 success
tests / nightly-ha (stable) id=128753172864 success
tests / nightly-status id=128753172345 success
tests / replay id=128753172731 success
tests / typing id=128753172816 success
validate id=128721563801 skipped
validate / validate-hacs id=128753172169 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE stale tree: 6016f9dd6e0ff482d0e140946721657357653726 lacks origin/main 8a4cf2618c53a6dca6b65df3eae5efc8832d1796; roster read at origin/main
NOTE body item c7e2fe29: R10-I18N-DE: R10-I18N-DE resolved on origin/handoff/audit-r10-roster
NOTE body item cc1cca91: R10-USER-DOCS-VERIFY
NOTE body item a4565419: R10-MIN-POWER-FLOOR: R10-MIN-POWER-FLOOR resolved on origin/handoff/audit-r10-roster
NOTE body item de37a181: R10-MIN-POWER-FLOOR: R10-MIN-POWER-FLOOR resolved on origin/handoff/audit-r10-roster
NOTE body item b8c2d996: R10-MIN-POWER-FLOOR: R10-MIN-POWER-FLOOR resolved on origin/handoff/audit-r10-roster
NOTE body item 03a73a59: dismissed:steps correct once projected (item f3c0e349)
NOTE body item 05ac7044: #201
CARRY-AUDIT: 7 finding item(s): 7 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>
             `tools/pr/prepr.sh` is in the tree at this head
  ok         python3 tests/env_drift.py
             `tests/env_drift.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/stress.py
             `tests/stress.py` is in the tree at this head
  ok         dev/audit/harnesses/r10_min_power_floor.py
             `dev/audit/harnesses/r10_min_power_floor.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_min_power_floor.py
             `dev/audit/harnesses/r10_min_power_floor.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py "# --- #3289 a declared on/off" "# --- R10-SETPOINT-POWER"
             `tools/audit/seat/features_block.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/mutant_run.py --diff dee8b413fd7da7b07f13e28a93d7d49b4a9e978a...HEAD --cmd "$MUTANT_CMD" --max-mutants 0 --report-only
             `tools/audit/seat/mutant_run.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=dee8b413f PYTHONPATH=tests/hastub bash tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/features.py
             `tests/features.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/env_drift.py --all dee8b413f…
             `tests/env_drift.py` is in the tree at this head
  unverified git diff --numstat
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified /etc/profile.d/hpo-toolchain.sh
             `/etc/profile.d/hpo-toolchain.sh` resolves outside this repository, so whether it is in the tree at this head is not a question this check can answer
  ok         tools/audit/seat/cloud-setup.sh
             `tools/audit/seat/cloud-setup.sh` is in the tree at this head
  unverified bash
             bash with no script argument
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff dee8b413f
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/typing_ruler.py
             `tests/typing_ruler.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components python3 dev/audit/rounds/round3/D5/option_doc_coverage.py
             `dev/audit/rounds/round3/D5/option_doc_coverage.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py
             `dev/audit/rounds/round4/D6/claims.py` is in the tree at this head

FIGURES: 19 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_realize_draw.GUARD_OFF.bcb6002f.json b/tests/mutation_ledger/killed_by/optimizer.py/_realize_draw.GUARD_OFF.bcb6002f.json
new file mode 100644
index 000000000..bd6a4a5a9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_realize_draw.GUARD_OFF.bcb6002f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_realize_draw GUARD_OFF bcb6002f",
+  "killed_by": "tests/features.py",
+  "old": "    if dhw is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_realize_draw.RETURN_DEL.fb58784b.json b/tests/mutation_ledger/killed_by/optimizer.py/_realize_draw.RETURN_DEL.fb58784b.json
new file mode 100644
index 000000000..f5270324c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_realize_draw.RETURN_DEL.fb58784b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_realize_draw RETURN_DEL fb58784b",
+  "killed_by": "tests/plan_view.py",
+  "old": "    return _realize_joint(clamp, space, dhw, p_min, p_max)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_realize_joint.GUARD_OFF.55b8330e.json b/tests/mutation_ledger/killed_by/optimizer.py/_realize_joint.GUARD_OFF.55b8330e.json
new file mode 100644
index 000000000..724ee290d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_realize_joint.GUARD_OFF.55b8330e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_realize_joint GUARD_OFF 55b8330e",
+  "killed_by": "tests/doc_claims.py",
+  "old": "    if not clamp:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/doc_claims.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_realize_joint.RETURN_DEL.ca8c2e8b.json b/tests/mutation_ledger/killed_by/optimizer.py/_realize_joint.RETURN_DEL.ca8c2e8b.json
new file mode 100644
index 000000000..40f6cacfa
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_realize_joint.RETURN_DEL.ca8c2e8b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_realize_joint RETURN_DEL ca8c2e8b",
+  "killed_by": "tests/features.py",
+  "old": "    return project_space_against(space, tank, p_min, p_max), tank",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.can_duty_cycle.GUARD_OFF.1329ac75.json b/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.can_duty_cycle.GUARD_OFF.1329ac75.json
new file mode 100644
index 000000000..242383a5d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.can_duty_cycle.GUARD_OFF.1329ac75.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:InstallCapability.can_duty_cycle GUARD_OFF 1329ac75",
+  "killed_by": "tests/features.py",
+  "old": "        if self.on_off:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/project_planned_levels.RETURN_DEL.920a8da2.json b/tests/mutation_ledger/killed_by/thermal_model.py/project_planned_levels.RETURN_DEL.920a8da2.json
new file mode 100644
index 000000000..76b3e42a8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/project_planned_levels.RETURN_DEL.920a8da2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:project_planned_levels RETURN_DEL 920a8da2",
+  "killed_by": "tests/features.py",
+  "old": "    return _onto_band(np.asarray(power, dtype=float), float(p_min), float(p_max))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/config_flow.py b/custom_components/heatpump_optimizer/config_flow.py
index c43b8f690..848499b97 100644
--- a/custom_components/heatpump_optimizer/config_flow.py
+++ b/custom_components/heatpump_optimizer/config_flow.py
@@ -394,6 +394,9 @@ from .const import (
     DEFAULT_DEBUG_COLLECT,
     CONF_COMFORT_LEARNING_ENABLED,
     DEFAULT_COMFORT_LEARNING_ENABLED,
+    CONF_COMPRESSOR_MODULATION,
+    COMPRESSOR_MODULATIONS,
+    COMPRESSOR_MODULATION_AUTO,
     CONF_TWO_ZONE_MODE,
     TWO_ZONE_MODES,
     TWO_ZONE_MODE_AUTO,
@@ -1719,6 +1722,7 @@ _OPTION_FIELDS: Final[tuple[_F, ...]] = (
     _F("thermal_model", CONF_HEAT_PUMP_COP_NOMINAL, _SUGGESTED, _number(1.5, 6.0, 0.1)),
     _F("thermal_model", CONF_HEAT_PUMP_MAX_POWER, _SUGGESTED, _number(1, 20, 0.5, 'kW')),
     _F("thermal_model", CONF_HEAT_PUMP_MIN_POWER, _SUGGESTED, _number(0, 10, 0.5, 'kW')),
+    _F("thermal_model", CONF_COMPRESSOR_MODULATION, _Suggested(COMPRESSOR_MODULATION_AUTO), _select(list(COMPRESSOR_MODULATIONS), 'compressor_modulation')),
     _F("thermal_model", CONF_HEAT_PUMP_COP_PARTLOAD_DERATE, _SUGGESTED, _number(0, MAX_HEAT_PUMP_COP_PARTLOAD_DERATE, 0.01)),
     # -- thermal_model_zones
     _F("thermal_model_zones", CONF_TWO_ZONE_MODE, _Suggested(TWO_ZONE_MODE_AUTO), _select(list(TWO_ZONE_MODES), 'two_zone_mode'), group="mode"),
diff --git a/custom_components/heatpump_optimizer/const.py b/custom_components/heatpump_optimizer/const.py
index ea3065c28..0533011b2 100644
--- a/custom_components/heatpump_optimizer/const.py
+++ b/custom_components/heatpump_optimizer/const.py
@@ -802,6 +802,20 @@ DEFAULT_FLOW_HEAT_C: Final = 55.0
 #: ``false`` keeps the duty-cycle reading on a switch-plus-setpoint
 #: install. Absent follows the install probe (#1955).
 CONF_CLAMP_PLANNED_LEVELS: Final = "clamp_planned_levels"
+#: Whether the compressor can run below its minimum power (#3289). ``on_off``
+#: plans every step at 0 or between min and max power; ``modulating`` keeps a
+#: level below the minimum as a duty-cycle average; ``auto`` (the default, same
+#: as absent) follows ``clamp_planned_levels``, then the install probe.
+CONF_COMPRESSOR_MODULATION: Final = "compressor_modulation"
+COMPRESSOR_MODULATION_AUTO: Final = "auto"
+COMPRESSOR_MODULATION_ON_OFF: Final = "on_off"
+COMPRESSOR_MODULATION_MODULATING: Final = "modulating"
+COMPRESSOR_MODULATIONS: Final = (
+    COMPRESSOR_MODULATION_AUTO,
+    COMPRESSOR_MODULATION_ON_OFF,
+    COMPRESSOR_MODULATION_MODULATING,
+)
+DEFAULT_COMPRESSOR_MODULATION: Final = COMPRESSOR_MODULATION_AUTO
 CONF_DHW_DAILY_CONSUMPTION: Final = "dhw_daily_consumption"  # liters/day
 # How fast the tank cools when nothing is drawn, expressed at a reference
 # condition so it stays meaningful regardless of tank size. Self-learned at
diff --git a/custom_components/heatpump_optimizer/optimizer.py b/custom_components/heatpump_optimizer/optimizer.py
index bff693241..a87b313cb 100644
--- a/custom_components/heatpump_optimizer/optimizer.py
+++ b/custom_components/heatpump_optimizer/optimizer.py
@@ -105,6 +105,7 @@ from .thermal_model import (
     planned_draws_run,
     delivered_heat_kw,
     project_planned_levels,
+    project_space_against,
     valve_charge_demand,
     valve_hold_temperature,
     weather_or_calm,
@@ -154,13 +155,28 @@ def _realize_draw(
     p_max: float,
 ) -> tuple[np.ndarray, np.ndarray | None]:
     """Space and, when present, DHW at the power the write surface can deliver."""
-    return (
-        _published_levels(clamp, space, p_min, p_max),
-        (
-            None if dhw is None
-            else _published_levels(clamp, dhw, p_min, p_max)
-        ),
-    )
+    if dhw is None:
+        return _published_levels(clamp, space, p_min, p_max), None
+    return _realize_joint(clamp, space, dhw, p_min, p_max)
+
+
+def _realize_joint(
+    clamp: bool,
+    space: np.ndarray,
+    dhw: np.ndarray,
+    p_min: float,
+    p_max: float,
+) -> tuple[np.ndarray, np.ndarray]:
+    """Space and DHW as :func:`_realize_draw` ships them, DHW present.
+
+    On a clamped install one compressor serves both channels: DHW ships as
+    its own projection and space projects against it (#3289), so the total
+    never exceeds ``p_max`` nor runs below ``p_min``.
+    """
+    if not clamp:
+        return space, dhw
+    tank = project_planned_levels(dhw, p_min, p_max)
+    return project_space_against(space, tank, p_min, p_max), tank
 
 
 def _scores_rounded(opt: HeatPumpOptimizer) -> bool:
@@ -5122,11 +5138,9 @@ class HeatPumpOptimizer:
             p_max=p_max,
             planner=planner,
         )
-        optimal_space = _published_levels(
-            self.config.clamp_planned_levels, optimal_space, p_min, p_max
-        )
-        optimal_dhw = _published_levels(
-            self.config.clamp_planned_levels, optimal_dhw, p_min, p_max
+        optimal_space, optimal_dhw = _realize_joint(
+            self.config.clamp_planned_levels, optimal_space, optimal_dhw,
+            p_min, p_max,
         )
 
         # Simulate with optimal schedule
diff --git a/custom_components/heatpump_optimizer/strings.json b/custom_components/heatpump_optimizer/strings.json
index 7d48935ba..af664910a 100644
--- a/custom_components/heatpump_optimizer/strings.json
+++ b/custom_components/heatpump_optimizer/strings.json
@@ -1003,6 +1003,7 @@
           "heat_pump_cop_nominal": "Heat pump nominal COP",
           "heat_pump_max_power": "Heat pump max power (kW)",
           "heat_pump_min_power": "Heat pump min power (kW)",
+          "compressor_modulation": "Compressor runs below min power",
           "heat_pump_cop_partload_derate": "Heat pump COP loss at max power",
           "after_save": "After saving"
         },
@@ -1014,6 +1015,7 @@
           "heat_pump_cop_nominal": "Units of heat produced per unit of electricity under normal conditions. Check the data sheet; 3 to 4 is typical for air-to-water, 4 to 5 for ground source.",
           "heat_pump_max_power": "Electrical input at full output. Caps how much cheap electricity can be stored per hour.",
           "heat_pump_min_power": "Lowest electrical input the pump can run at without cycling on and off.",
+          "compressor_modulation": "Whether the compressor can run below the min power above. On/off: every planned step is either off or between min and max power, with hot water and space heating sharing that one compressor. Modulating: a level below min power is planned as an average the pump reaches by running part of the step. Automatic decides from the mapped entities: a power switch plus a setpoint and no frequency entity counts as on/off, anything else as modulating.",
           "heat_pump_cop_partload_derate": "Share of efficiency lost running at max power rather than min power, as a fraction (0.1 = 10 %). Larger heat flows need larger temperature differences across the heat exchangers. 0 leaves power out of the COP; typical air-to-water units lose 0.05 to 0.15. A heat meter is not needed. Keep it below band / (band + max power), band being max minus min power, or heat would fall as power rises.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
         }
@@ -1616,6 +1618,13 @@
         "flow": "Flow temperature"
       }
     },
+    "compressor_modulation": {
+      "options": {
+        "auto": "Automatic (from the mapped entities)",
+        "on_off": "No: on/off",
+        "modulating": "Yes: modulating"
+      }
+    },
     "two_zone_mode": {
       "options": {
         "auto": "Automatic (on once zone values exist)",
diff --git a/custom_components/heatpump_optimizer/thermal_model.py b/custom_components/heatpump_optimizer/thermal_model.py
index b873faaf3..7e3e08232 100644
--- a/custom_components/heatpump_optimizer/thermal_model.py
+++ b/custom_components/heatpump_optimizer/thermal_model.py
@@ -1276,6 +1276,7 @@ class InstallCapability:
     measured_heat: bool = False
     heat_counter: bool = False
     electric_counter: bool = False
+    on_off: bool = False
 
     def cop_electric(self) -> bool:
         """An electrical figure a COP divides by: a heat counter's span reads
@@ -1289,8 +1290,12 @@ class InstallCapability:
         that is not exactly a power switch plus a setpoint is not known to
         be unable to, so the duty-cycle reading stands. Switch plus setpoint
         and no frequency cannot: the compressor runs at or above its
-        modulation floor whenever the switch is on.
+        modulation floor whenever the switch is on. Neither can a compressor
+        declared on/off (``on_off``, from :func:`declared_modulation`),
+        whatever the surface.
         """
+        if self.on_off:
+            return False
         return (
             True
             if self.frequency or "frequency" in self.writes
@@ -1360,6 +1365,30 @@ def probe_install(config: Any) -> InstallCapability:
         ),
         heat_counter=bool(cfg.get(const.CONF_HEAT_ENERGY_ENTITY)),
         electric_counter=bool(cfg.get(const.CONF_ENERGY_ENTITY)),
+        on_off=declared_modulation(cfg) is False,
+    )
+
+
+def declared_modulation(config: Any) -> bool | None:
+    """Whether the user declared the compressor modulating, ``None`` undeclared.
+
+    The one reader of ``compressor_modulation`` and of the legacy
+    ``clamp_planned_levels`` (#3289): ``on_off`` -> ``False``,
+    ``modulating`` -> ``True``. ``auto`` or absent reads the legacy key,
+    ``true`` clamping (on/off) and ``false`` opting out (modulating); any
+    other value of either is undeclared, and the probe decides.
+    """
+    cfg = config or {}
+    mode = cfg.get(
+        const.CONF_COMPRESSOR_MODULATION, const.DEFAULT_COMPRESSOR_MODULATION
+    )
+    legacy = cfg.get(const.CONF_CLAMP_PLANNED_LEVELS)
+    return (
+        False if mode == const.COMPRESSOR_MODULATION_ON_OFF
+        else True if mode == const.COMPRESSOR_MODULATION_MODULATING
+        else False if legacy is True
+        else True if legacy is False
+        else None
     )
 
 
@@ -1434,8 +1463,8 @@ def feedback_gaps(config: Any) -> list[dict[str, str]]:
 def duty_cycle_realizable(config: Any) -> bool:
     """The duty-cycle reading stands for this config.
 
-    ``clamp_planned_levels: false`` is the opt-out. Otherwise the probe
-    decides, and an absent key follows the probe.
+    A compressor declared modulating (:func:`declared_modulation`) is the
+    opt-out. Otherwise the probe decides, and an undeclared one follows it.
     """
     cfg = config or {}
     cap = probe_install(cfg)
@@ -1443,7 +1472,7 @@ def duty_cycle_realizable(config: Any) -> bool:
     # frequency-plus-power plant stay byte-identical (#1955).
     return (
         True
-        if cfg.get(const.CONF_CLAMP_PLANNED_LEVELS) is False
+        if declared_modulation(cfg) is True
         else True if cap.fully_metered() else cap.can_duty_cycle()
     )
 
@@ -1499,14 +1528,14 @@ def learner_unmetered(config: Any) -> str | None:
 
     No measured power, and the probe says the write surface cannot
     duty-cycle. A frequency install still learns from the commanded figure
-    (the compressor can realize it); an explicit clamp opt-out keeps
-    today's learner. Ranked with the boost freeze, after ventilation.
+    (the compressor can realize it); a compressor declared modulating
+    keeps today's learner. Ranked with the boost freeze, after ventilation.
     """
     cfg = config or {}
     cap = probe_install(cfg)
     return (
         None
-        if cfg.get(const.CONF_CLAMP_PLANNED_LEVELS) is False
+        if declared_modulation(cfg) is True
         else None
         if cap.measured_power or cap.can_duty_cycle()
         else UNMETERED_POWER_FREEZE
@@ -1572,9 +1601,14 @@ def project_planned_levels(power: Any, p_min: float, p_max: float) -> np.ndarray
     set is not the closed interval ``[p_min, p_max]``, which would force
     the pump on for the whole horizon.
     """
-    arr = np.asarray(power, dtype=float)
-    lo = float(p_min)
-    hi = float(p_max)
+    return _onto_band(np.asarray(power, dtype=float), float(p_min), float(p_max))
+
+
+def _onto_band(arr: np.ndarray, lo: Any, hi: Any) -> np.ndarray:
+    """``arr`` clipped to ``[0, hi]``, a value in ``(0, lo)`` raised to ``lo``.
+
+    ``lo`` and ``hi`` are floats or arrays broadcasting against ``arr``.
+    """
     capped = np.where(np.greater(arr, hi), hi, arr)
     nonneg = np.where(np.less(capped, 0.0), 0.0, capped)
     return np.where(
@@ -1584,6 +1618,29 @@ def project_planned_levels(power: Any, p_min: float, p_max: float) -> np.ndarray
     )
 
 
+def project_space_against(
+    space: Any, dhw: Any, p_min: float, p_max: float
+) -> np.ndarray:
+    """Space heating onto what one on/off compressor leaves beside ``dhw``.
+
+    ``dhw`` is the DHW schedule already projected by
+    :func:`project_planned_levels`, an ``N`` vector; ``space`` is an ``N``
+    vector or a ``B x N`` matrix, broadcast row by row (#3289). One
+    compressor serves both channels, so per step space is clipped to
+    ``[0, p_max - dhw]`` and a value in ``(0, p_min - dhw)`` is raised to
+    that bound: the total lands in ``{0} ∪ [p_min, p_max]`` and DHW keeps
+    the level its planner booked. A negative bound needs no floor at 0: a
+    cap below 0 clips to 0, and a raise below 0 matches no running level.
+    With ``dhw`` zero this is :func:`project_planned_levels`. Design choice:
+    a shared scale on the total lost because it writes into the DHW plan the
+    space solve treats as fixed.
+    """
+    other = np.asarray(dhw, dtype=float)
+    return _onto_band(
+        np.asarray(space, dtype=float), float(p_min) - other, float(p_max) - other
+    )
+
+
 def _span_when(left: float | None, right: float | None, ready: bool) -> float:
     """``left - right`` once both ends are floats, else ``0``."""
     span = 0.0
diff --git a/custom_components/heatpump_optimizer/translations/en.json b/custom_components/heatpump_optimizer/translations/en.json
index 7d48935ba..af664910a 100644
--- a/custom_components/heatpump_optimizer/translations/en.json
+++ b/custom_components/heatpump_optimizer/translations/en.json
@@ -1003,6 +1003,7 @@
           "heat_pump_cop_nominal": "Heat pump nominal COP",
           "heat_pump_max_power": "Heat pump max power (kW)",
           "heat_pump_min_power": "Heat pump min power (kW)",
+          "compressor_modulation": "Compressor runs below min power",
           "heat_pump_cop_partload_derate": "Heat pump COP loss at max power",
           "after_save": "After saving"
         },
@@ -1014,6 +1015,7 @@
           "heat_pump_cop_nominal": "Units of heat produced per unit of electricity under normal conditions. Check the data sheet; 3 to 4 is typical for air-to-water, 4 to 5 for ground source.",
           "heat_pump_max_power": "Electrical input at full output. Caps how much cheap electricity can be stored per hour.",
           "heat_pump_min_power": "Lowest electrical input the pump can run at without cycling on and off.",
+          "compressor_modulation": "Whether the compressor can run below the min power above. On/off: every planned step is either off or between min and max power, with hot water and space heating sharing that one compressor. Modulating: a level below min power is planned as an average the pump reaches by running part of the step. Automatic decides from the mapped entities: a power switch plus a setpoint and no frequency entity counts as on/off, anything else as modulating.",
           "heat_pump_cop_partload_derate": "Share of efficiency lost running at max power rather than min power, as a fraction (0.1 = 10 %). Larger heat flows need larger temperature differences across the heat exchangers. 0 leaves power out of the COP; typical air-to-water units lose 0.05 to 0.15. A heat meter is not needed. Keep it below band / (band + max power), band being max minus min power, or heat would fall as power rises.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
         }
@@ -1616,6 +1618,13 @@
         "flow": "Flow temperature"
       }
     },
+    "compressor_modulation": {
+      "options": {
+        "auto": "Automatic (from the mapped entities)",
+        "on_off": "No: on/off",
+        "modulating": "Yes: modulating"
+      }
+    },
     "two_zone_mode": {
       "options": {
         "auto": "Automatic (on once zone values exist)",
diff --git a/custom_components/heatpump_optimizer/translations/sv.json b/custom_components/heatpump_optimizer/translations/sv.json
index a59596d56..c3bddba05 100644
--- a/custom_components/heatpump_optimizer/translations/sv.json
+++ b/custom_components/heatpump_optimizer/translations/sv.json
@@ -1003,6 +1003,7 @@
           "heat_pump_cop_nominal": "Värmepumpens nominella COP",
           "heat_pump_max_power": "Värmepump max effekt (kW)",
           "heat_pump_min_power": "Värmepump min effekt (kW)",
+          "compressor_modulation": "Kompressorn går under min effekt",
           "heat_pump_cop_partload_derate": "Värmepumpens COP-förlust vid maxeffekt",
           "after_save": "Efter sparande"
         },
@@ -1014,6 +1015,7 @@
           "heat_pump_cop_nominal": "Enheter värme per enhet el under normala förhållanden. Se databladet; 3 till 4 är vanligt för luft/vatten, 4 till 5 för bergvärme.",
           "heat_pump_max_power": "Eleffekt vid full drift. Sätter taket för hur mycket billig el som kan lagras per timme.",
           "heat_pump_min_power": "Lägsta eleffekt pumpen klarar utan att börja starta och stanna.",
+          "compressor_modulation": "Om kompressorn kan gå under min effekt ovan. Av/på: varje planerat steg är antingen avstängt eller mellan min- och maxeffekt, och varmvatten och rumsvärme delar den enda kompressorn. Modulerande: en nivå under min effekt planeras som ett medelvärde som pumpen når genom att gå en del av steget. Automatiskt avgör utifrån de kopplade entiteterna: en strömbrytare plus ett börvärde och ingen frekvensentitet räknas som av/på, allt annat som modulerande.",
           "heat_pump_cop_partload_derate": "Andel av verkningsgraden som går förlorad vid maxeffekt jämfört med mineffekt, som bråkdel (0,1 = 10 %). Större värmeflöden kräver större temperaturskillnad över värmeväxlarna. 0 låter effekten vara utan inverkan på COP; vanliga luft/vatten-pumpar förlorar 0,05 till 0,15. Ingen värmemätare behövs. Håll den under band / (band + maxeffekt), där bandet är max- minus mineffekt, annars sjunker värmen när effekten stiger.",
           "after_save": "Sparandet slår igenom direkt; detta val avgör vart dialogen går näst."
         }
@@ -1616,6 +1618,13 @@
         "flow": "Framledningstemperatur"
       }
     },
+    "compressor_modulation": {
+      "options": {
+        "auto": "Automatiskt (utifrån de kopplade entiteterna)",
+        "on_off": "Nej: av/på",
+        "modulating": "Ja: modulerande"
+      }
+    },
     "two_zone_mode": {
       "options": {
         "auto": "Automatiskt (på när zonvärden finns)",
diff --git a/dev/audit/harnesses/r10_min_power_floor.py b/dev/audit/harnesses/r10_min_power_floor.py
new file mode 100644
index 000000000..4bdf93c37
--- /dev/null
+++ b/dev/audit/harnesses/r10_min_power_floor.py
@@ -0,0 +1,53 @@
+"""r10-min-power-floor (issue 3289): per-step electrical power against heat_pump_min_power.
+
+Solves a 2.5-3.5 kW pump over 24 h with clamp_planned_levels False and True, spread and
+flat prices, DHW off/on, two outdoor means, and counts running steps (space+DHW > 0.1 kW)
+below the 2.5 kW minimum. The clamp=True arm on identical inputs is the null control: the
+counter reads 0 where the floor is honoured.
+
+R10-MIN-POWER-FLOOR fix extension: the arm `clamp=on_off` takes `clamp_planned_levels` from
+`levels_clamped` on a fully metered map (power entity, frequency sensor) declaring
+`compressor_modulation: on_off`; an install no probe clamps without the declaration.
+`max_total` is the largest space+DHW step (above p_max 3.5 is a draw the pump cannot
+deliver); `space_only_below_min` counts space steps below 2.5 kW where DHW is off
+(<= MIN_RUNNING_DRAW_KW): in a mixed step space is a diverter share of a compressor that
+runs at >= p_min, so only a space-only step is a sub-minimum compressor level.
+
+    PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_min_power_floor.py [-v]
+"""
+import sys
+from datetime import datetime, timezone
+import numpy as np
+from heatpump_optimizer import const
+from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
+from heatpump_optimizer.thermal_model import MIN_RUNNING_DRAW_KW, ThermalModel, ThermalParameters, ThermalState, channel_heating_steps, levels_clamped
+from heatpump_optimizer.plan_slots import plan_slots
+from profiles import solve_inputs
+S = np.arange(96)
+SPREAD = 1.3 + 0.9*np.sin(2*np.pi*(S-30)/96.0)
+FLAT = np.full(96, float(SPREAD.mean()))
+ON_OFF_METERED = {const.CONF_POWER_ENTITY: "sensor.p", const.CONF_COMPRESSOR_FREQ_SENSOR: "sensor.f",
+                  "compressor_modulation": "on_off"}
+def run(clamp, prices, dhw, out_mean):
+    p = ThermalParameters(); p.mixing_valve_mode="none"; p.buffer_tank_volume=0.0
+    p.min_electrical_power, p.max_electrical_power = 2.5, 3.5
+    p.dhw_enabled = dhw
+    out = out_mean + 3*np.sin(2*np.pi*(S-50)/96)
+    opt = HeatPumpOptimizer(ThermalModel(p), OptimizationConfig(
+        clamp_planned_levels=levels_clamped(ON_OFF_METERED) if clamp == "on_off" else clamp))
+    r = opt.optimize(inputs=solve_inputs(initial_state=ThermalState(room_temperature=20.5, upper_floor_temperature=20.5,
+        lower_floor_temperature=20.5, slab_temperature=21.0, outdoor_temperature=float(out[0]), dhw_temperature=50.0),
+        prices=prices, outdoor_temps=out, start_time=datetime(2026,1,10,tzinfo=timezone.utc)))
+    sp = np.asarray(r.power_schedule,float); dw = np.asarray(r.dhw_power_schedule or np.zeros(96),float)
+    tot = sp+dw; on = tot>0.1
+    below = int(np.sum(on & (tot < 2.5-1e-9)))
+    sl = plan_slots(list(r.timestamps), list(sp), list(r.prices), 0.25, other_powers=list(dw))
+    slot_min = min((s["avg_power_kw"] for s in sl), default=None)
+    space_only_below = int(np.sum(np.array(channel_heating_steps(sp,dw)) & (sp<2.5-1e-9)))
+    lone = int(np.sum((sp > MIN_RUNNING_DRAW_KW) & (dw <= MIN_RUNNING_DRAW_KW) & (sp < 2.5-1e-9)))
+    print(f"clamp={clamp} prices={'flat' if prices is FLAT else 'spread'} dhw={dhw} out={out_mean}: steps_on={int(on.sum())} total_below_min={below} space_steps_below_min={space_only_below} slots={len(sl)} min_slot_avg={slot_min} cost={r.objective_value:.3f} max_total={tot.max():.2f} space_only_below_min={lone}")
+    if '-v' in sys.argv: print(' space', np.round(sp,2).tolist()); print(' dhw', np.round(dw,2).tolist()); print(' slots', [(s['start'][11:16],s['end'][11:16],s['avg_power_kw']) for s in sl])
+CASES = [(False, FLAT, False, 5.0)] if "-v" in sys.argv else None
+import itertools
+for c in CASES or itertools.product((False, True, "on_off"),(SPREAD, FLAT),(False, True),(-4.0,5.0)):
+    run(*c)
diff --git a/dev/audit/rca/r10-min-power-floor-STOP.md b/dev/audit/rca/r10-min-power-floor-STOP.md
new file mode 100644
index 000000000..699b7d2d1
--- /dev/null
+++ b/dev/audit/rca/r10-min-power-floor-STOP.md
@@ -0,0 +1,62 @@
+# r10-min-power-floor: stopped for a design (issue 3289)
+
+Fixer seat, base 4b5d771bdf8feb1f83d7d9443e5117b771a0ab76 (origin/main at the run). No production code changed.
+
+## Measurement (the brief's MEASURE FIRST)
+
+The reporting hypothesis is refuted. A merged slot averages only its own heating steps
+(`plan_slots.plan_slots`, steps from `thermal_model.channel_heating_steps`), so a 6 h slot
+averaging 0.4 kW cannot be made of steps at or above 2.5 kW: the steps themselves are below
+the floor.
+
+Harness `dev/audit/harnesses/r10_min_power_floor.py` (sha1 e21d29905d30bc08dcb8ec4cc1427c8ce824419d),
+min 2.5 / max 3.5 kW, 96 x 15 min steps, rule: a step runs when space+DHW > 0.1 kW
+(`MIN_RUNNING_DRAW_KW`) and counts when that total is < 2.5 kW.
+
+```
+clamp=False prices=spread dhw=False out=-4.0: steps_on=34 total_below_min=0 space_steps_below_min=0 slots=2 min_slot_avg=3.5 cost=30.869
+clamp=False prices=spread dhw=False out=5.0: steps_on=19 total_below_min=0 space_steps_below_min=0 slots=2 min_slot_avg=3.5 cost=14.825
+clamp=False prices=spread dhw=True out=-4.0: steps_on=43 total_below_min=7 space_steps_below_min=4 slots=2 min_slot_avg=3.2 cost=37.317
+clamp=False prices=spread dhw=True out=5.0: steps_on=26 total_below_min=5 space_steps_below_min=1 slots=2 min_slot_avg=3.25 cost=19.497
+clamp=False prices=flat dhw=False out=-4.0: steps_on=85 total_below_min=62 space_steps_below_min=62 slots=2 min_slot_avg=1.42 cost=57.823
+clamp=False prices=flat dhw=False out=5.0: steps_on=41 total_below_min=27 space_steps_below_min=27 slots=4 min_slot_avg=0.13 cost=28.815
+clamp=False prices=flat dhw=True out=-4.0: steps_on=84 total_below_min=55 space_steps_below_min=64 slots=2 min_slot_avg=1.45 cost=63.745
+clamp=False prices=flat dhw=True out=5.0: steps_on=54 total_below_min=39 space_steps_below_min=39 slots=3 min_slot_avg=0.31 cost=33.794
+clamp=True prices=spread dhw=False out=-4.0: steps_on=34 total_below_min=0 space_steps_below_min=0 slots=2 min_slot_avg=3.5 cost=30.869
+clamp=True prices=spread dhw=False out=5.0: steps_on=20 total_below_min=0 space_steps_below_min=0 slots=2 min_slot_avg=3.39 cost=14.876
+clamp=True prices=spread dhw=True out=-4.0: steps_on=45 total_below_min=0 space_steps_below_min=0 slots=4 min_slot_avg=2.5 cost=38.844
+clamp=True prices=spread dhw=True out=5.0: steps_on=26 total_below_min=0 space_steps_below_min=0 slots=2 min_slot_avg=3.39 cost=20.652
+clamp=True prices=flat dhw=False out=-4.0: steps_on=53 total_below_min=0 space_steps_below_min=0 slots=2 min_slot_avg=2.5 cost=58.944
+clamp=True prices=flat dhw=False out=5.0: steps_on=9 total_below_min=0 space_steps_below_min=0 slots=1 min_slot_avg=3.39 cost=32.407
+clamp=True prices=flat dhw=True out=-4.0: steps_on=40 total_below_min=0 space_steps_below_min=0 slots=1 min_slot_avg=3.4 cost=67.571
+clamp=True prices=flat dhw=True out=5.0: steps_on=20 total_below_min=0 space_steps_below_min=0 slots=1 min_slot_avg=3.47 cost=39.167
+```
+
+- `clamp_planned_levels=False` (the duty-cycle reading): sub-minimum running steps in 6 of 8
+  cells; flat prices put 27 of 41 (out 5 C) and 62 of 85 (out -4 C) running steps below 2.5 kW,
+  with space steps of 0.01-0.23 kW and a slot averaging 0.21 kW -- the shape the issue reports.
+- `clamp_planned_levels=True`, identical inputs (null control): 0 sub-minimum steps in all 8 cells.
+- Flat-price control on cost: the flat-price cells are in the table; the cost figures above are
+  objective values under each arm and are not a savings claim.
+
+## Why this stops
+
+The solver treats `heat_pump_min_power` as the bottom of a modulation band, and a level in
+`(0, p_min)` as a duty-cycle average (#1955). The floor is honoured only by the post-solve
+projection `thermal_model.project_planned_levels`, which ships only when `levels_clamped`
+holds: `probe_install` sees a switch plus a setpoint write and no frequency entity or sensor.
+`duty_cycle_realizable` lets `clamp_planned_levels: false` opt out but offers no opt-in, so a
+non-modulating pump on any other write surface, or with a frequency sensor, plans sub-minimum
+steps. Honouring the minimum as an on/off floor for those installs is a choice between (a) an
+explicit non-modulating declaration that forces the existing projection (and its relaxed-start
+scoring, `optimizer._relaxed_starts`), (b) an on/off (integer) constraint in the solve, or
+(c) changing the probe's default; each changes which installs the #1955 design clamps and the
+goldens of those installs. Per the brief, this is size L for `designer.md` before any fixer.
+
+## For the designer
+
+- Rerun the harness above at both ends; its clamp=True arm is the control.
+- The reporter's config surface (which entities they map) is not in the issue; the design must
+  not assume it is switch plus setpoint.
+- With clamp=False and DHW on, slot averages stay above 2.5 kW while 5-7 running steps are below
+  the floor (time-shared steps): a slot-average test does not detect this, a per-step one does.
diff --git a/dev/audit/rounds/round3/D5/option_doc_coverage.py b/dev/audit/rounds/round3/D5/option_doc_coverage.py
index 92a7f8899..28107173e 100644
--- a/dev/audit/rounds/round3/D5/option_doc_coverage.py
+++ b/dev/audit/rounds/round3/D5/option_doc_coverage.py
@@ -92,14 +92,16 @@ EXPECTED on this tree (ae36eff printed option_fields_rendered=174 and
     its row in docs/configuration.md in the same commit. R10-WOOD-NOTIFY
     moved them once more, 203 -> 204 and 236 -> 237: the wood lighting lead
     time on the wood page, with its row in docs/configuration.md in the same
-    commit. This block is an
+    commit. R10-MIN-POWER-FLOOR moved them once more, 204 -> 205 and
+    237 -> 238: the compressor modulation select on the thermal model page,
+    with its row in docs/configuration.md in the same commit. This block is an
     ASSERTION `tests/harness_headers.py` executes the script against, and it
     is reached by a shell-out the closure recorder cannot see, so it does not
     go red on a pull request: it is re-measured in the commit that changes
     what the script prints, or main's forced-full run finds it):
-    RESULT option_fields_rendered=204 count
+    RESULT option_fields_rendered=205 count
     RESULT option_fields_undocumented=0 count
-    RESULT option_schema_keys_rendered=237 count
+    RESULT option_schema_keys_rendered=238 count
     RESULT wood_economics_fields_rendered=4 count
     RESULT wood_economics_doc_lines=8 count      (tolerance: exact;
     moved 6 -> 8 by #1645/F8.1: the Services section's `simulate_plan`
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index 447994fad..a95a41e09 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -1118,9 +1118,9 @@
  {
   "id": "C125",
   "source": "strings.json:selector",
-  "claim": "every SelectSelector option on every options page has a translated label (45 selects)",
+  "claim": "every SelectSelector option on every options page has a translated label (46 selects)",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "45 selects, untranslated=[]",
+  "result": "46 selects, untranslated=[]",
   "verdict": "true",
   "truth": ""
  }
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index 30491f447..bbd2123e8 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -128,4 +128,4 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C122 | `docs/configuration.md` | set_mode takes auto, comfort, economy, boost or off | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['auto', 'boost', 'comfort', 'economy', 'off'] measured=['auto', 'boost', 'comfort', 'economy', 'off'] | **true** |  |
 | C123 | `DISCLAIMER.md` | the licence is MIT | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=True measured=True | **true** |  |
 | C124 | `DISCLAIMER.md` | the disclaimer states the software is not a safety device and carries no warranty | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 'not a safety device' present=True, 'no warranty' present=True | **true** |  |
-| C125 | `strings.json:selector` | every SelectSelector option on every options page has a translated label (45 selects) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 45 selects, untranslated=[] | **true** |  |
+| C125 | `strings.json:selector` | every SelectSelector option on every options page has a translated label (46 selects) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 46 selects, untranslated=[] | **true** |  |
diff --git a/dev/programme/delivery/3308.md b/dev/programme/delivery/3308.md
new file mode 100644
index 000000000..46a265286
--- /dev/null
+++ b/dev/programme/delivery/3308.md
@@ -0,0 +1 @@
+- [#3308](https://github.com/tvofi/heatpump_optimizer/pull/3308) — **open**, R10-MIN-POWER-FLOOR: min power floor (R10-MIN-POWER-FLOOR)
diff --git a/docs/configuration.md b/docs/configuration.md
index 3bb603b97..601b70fc5 100644
--- a/docs/configuration.md
+++ b/docs/configuration.md
@@ -210,6 +210,11 @@ Then three numbers off the heat pump's nameplate:
 | Heat pump max power | 5.0 kW | 1–20, 0.5 steps | Electrical input at full output. Caps how much cheap electricity can be stored per hour. |
 | Heat pump min power | 1.0 kW | 0–10, 0.5 steps | The lowest input the pump can hold without cycling. Must not exceed the maximum. |
 
+A pump that cannot run below its min power at all, only on or off, is
+declared on **Thermal model (expert)** as *Compressor runs below min power:
+No: on/off*; otherwise the plan may book steps below the minimum as averages
+the pump would reach by modulating.
+
 That is the whole questionnaire path — the two-zone and solar pages are skipped
 deliberately. Their fields, once written, are what switches the two-zone model
 on, and a fresh install should not be given a two-zone model it did not ask
@@ -853,6 +858,7 @@ the per-floor numbers live on **Two-zone model**.
 | Heat pump nominal COP | the setup value | 1.5–6.0 | Units of heat per unit of electricity under normal conditions. |
 | Heat pump max power | the setup value | 1–20 kW | Electrical input at full output. |
 | Heat pump min power | the setup value | 0–10 kW | The lowest input the pump can hold without cycling. |
+| Compressor runs below min power | Automatic | Automatic, No: on/off, Yes: modulating | **No: on/off** plans every step at 0 or between min and max power, hot water and space heating together. **Yes: modulating** plans a level below min power as an average the pump reaches by running part of the step. **Automatic** counts a power switch plus a setpoint with no frequency entity as on/off, anything else as modulating. |
 | Heat pump COP loss at max power | the setup value | 0–0.5 | The share of efficiency lost at max power rather than min power. See [the setup screen](#thermal-model--optimization) for the limit the page enforces. |
 
 **Changing a derived value turns the derivation off.** These fields are what
diff --git a/tests/closures.json b/tests/closures.json
index 0a6011505..4f2d0f33d 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4098,6 +4098,7 @@
    "dev/audit/harnesses/r10_merge_subject_plants.sh",
    "dev/audit/harnesses/r10_mermaid_gantt_title.mjs",
    "dev/audit/harnesses/r10_mermaid_parse.mjs",
+   "dev/audit/harnesses/r10_min_power_floor.py",
    "dev/audit/harnesses/r10_month_last_window_billed.py",
    "dev/audit/harnesses/r10_mutant_skip/null_drive.py",
    "dev/audit/harnesses/r10_mutant_skip/replay.py",
diff --git a/tests/features.py b/tests/features.py
index c08b186ca..f74104846 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -69107,6 +69107,192 @@ R.check(
     f"{_pp_low}",
 )
 
+# --- #3289 a declared on/off compressor; space projected against the DHW ------
+# R10-MIN-POWER-FLOOR. ``compressor_modulation`` declares whether the
+# compressor can run below p_min; ``thermal_model.declared_modulation`` is its
+# only reader. On a clamped install one compressor serves space and DHW, so
+# space ships projected against the DHW the step already carries
+# (``project_space_against``): every step's total is 0 or in [p_min, p_max].
+# The solve cell is the finder's (dev/audit/harnesses/r10_min_power_floor.py):
+# a 2.5-3.5 kW pump, spread prices, DHW on, outdoor mean -4 degC.
+from heatpump_optimizer.const import (  # noqa: E402
+    CONF_CLAMP_PLANNED_LEVELS as _MPF_CLAMP_KEY,
+    CONF_COMPRESSOR_FREQ_ENTITY as _MPF_FREQ,
+    CONF_HEAT_PUMP_SWITCH_ENTITY as _MPF_SWITCH,
+    CONF_POWER_ENTITY as _MPF_POWER,
+    CONF_SPACE_SETPOINT_ENTITY as _MPF_SETPOINT,
+    COMPRESSOR_MODULATION_AUTO as _MPF_AUTO,
+    COMPRESSOR_MODULATION_MODULATING as _MPF_MOD,
+    COMPRESSOR_MODULATION_ON_OFF as _MPF_ON_OFF,
+    CONF_COMPRESSOR_FREQ_SENSOR as _MPF_FREQ_SENSOR,
+    CONF_COMPRESSOR_MODULATION as _MPF_KEY,
+    CONF_FREQ_CONTROL_MODE as _MPF_FREQ_MODE,
+    FREQ_MODE_CONTROL as _MPF_FREQ_CONTROL,
+)
+from heatpump_optimizer.optimizer import (  # noqa: E402
+    HeatPumpOptimizer as _MpfOpt,
+    OptimizationConfig as _MpfCfg,
+    _realize_draw as _mpf_realize,
+)
+from heatpump_optimizer.thermal_model import (  # noqa: E402
+    UNMETERED_POWER_FREEZE as _MPF_FREEZE,
+    ThermalModel as _MpfTM,
+    ThermalParameters as _MpfTP,
+    ThermalState as _MpfTS,
+    declared_modulation as _mpf_declared,
+    InstallCapability as _MpfCap,
+    learner_unmetered as _mpf_unmetered,
+    probe_install as _mpf_probe,
+    project_planned_levels as _mpf_project,
+    project_space_against as _mpf_against,
+)
+
+# The #1955 block's two surfaces, restated so this block runs alone
+# (``tools/audit/seat/features_block.py``): switch plus setpoint, and that
+# surface with a power entity and a frequency write.
+_MPF_UNMETERED = {_MPF_SWITCH: "switch.hp", _MPF_SETPOINT: "number.flow"}
+_MPF_METERED = {**_MPF_UNMETERED, _MPF_POWER: "sensor.hp_power", _MPF_FREQ: "number.hz"}
+
+_MPF_SETPOINT_ONLY = {_MPF_SETPOINT: "number.flow"}
+_MPF_FREQ_ONLY = {_MPF_FREQ_SENSOR: "sensor.hz"}
+
+
+def _mpf_on_off(cfg):
+    return {**cfg, _MPF_KEY: _MPF_ON_OFF}
+
+
+R.check(
+    "a declared on/off compressor clamps on every write surface, metered or not",
+    all(
+        _MpfCfg.from_mapping(_mpf_on_off(m)).clamp_planned_levels is True
+        for m in (_MPF_METERED, _MPF_SETPOINT_ONLY, _MPF_FREQ_ONLY, {})
+    )
+    and _mpf_probe(_mpf_on_off(_MPF_METERED)).fully_metered() is False,
+    f"{[_MpfCfg.from_mapping(_mpf_on_off(m)).clamp_planned_levels for m in (_MPF_METERED, _MPF_SETPOINT_ONLY, _MPF_FREQ_ONLY, {})]}",
+)
+_mpf_bare_cap = _MpfCap(writes=frozenset({"setpoint"}), measured_power=False, frequency=False)
+R.check(
+    "null control: a capability built without the declaration is not on/off, and a "
+    "setpoint-only surface it describes can duty-cycle",
+    _mpf_bare_cap.on_off is False and _mpf_bare_cap.can_duty_cycle() is True
+    and _mpf_probe(_MPF_SETPOINT_ONLY).on_off is False,
+    f"{_mpf_bare_cap}",
+)
+_mpf_base_rows = (_MPF_UNMETERED, _MPF_METERED, {}, _MPF_SETPOINT_ONLY, _MPF_FREQ_ONLY)
+R.check(
+    "null control: auto and an absent key keep the probe's clamp on every surface, "
+    "legacy false and modulating opt out, legacy true clamps",
+    all(
+        _MpfCfg.from_mapping({**m, _MPF_KEY: _MPF_AUTO}).clamp_planned_levels
+        is _MpfCfg.from_mapping(m).clamp_planned_levels
+        for m in _mpf_base_rows
+    )
+    and [_MpfCfg.from_mapping(m).clamp_planned_levels for m in _mpf_base_rows]
+    == [True, False, False, False, False]
+    and _MpfCfg.from_mapping({**_MPF_UNMETERED, _MPF_KEY: _MPF_MOD}).clamp_planned_levels is False
+    and _MpfCfg.from_mapping({**_MPF_UNMETERED, _MPF_CLAMP_KEY: False}).clamp_planned_levels is False
+    and _MpfCfg.from_mapping({**_MPF_METERED, _MPF_CLAMP_KEY: True}).clamp_planned_levels is True
+    and _MpfCfg.from_mapping(
+        {**_MPF_UNMETERED, _MPF_KEY: _MPF_AUTO, _MPF_CLAMP_KEY: False}
+    ).clamp_planned_levels is False,
+)
+R.check(
+    "declared_modulation reads the select first, the legacy key only under auto or absent, "
+    "and anything else as undeclared",
+    _mpf_declared({}) is None
+    and _mpf_declared({_MPF_KEY: _MPF_ON_OFF, _MPF_CLAMP_KEY: False}) is False
+    and _mpf_declared({_MPF_KEY: _MPF_MOD, _MPF_CLAMP_KEY: True}) is True
+    and _mpf_declared({_MPF_KEY: _MPF_AUTO, _MPF_CLAMP_KEY: True}) is False
+    and _mpf_declared({_MPF_CLAMP_KEY: False}) is True
+    and _mpf_declared({_MPF_KEY: "bogus"}) is None
+    and _mpf_declared({_MPF_CLAMP_KEY: "false"}) is None,
+)
+R.check(
+    "an unmetered on/off install freezes the house learner; a metered one, or a "
+    "declared modulating one, learns",
+    _mpf_unmetered(_mpf_on_off(_MPF_SETPOINT_ONLY)) == _MPF_FREEZE
+    and _mpf_unmetered(_MPF_SETPOINT_ONLY) is None
+    and _mpf_unmetered(_mpf_on_off(_MPF_METERED)) is None
+    and _mpf_unmetered({**_MPF_UNMETERED, _MPF_KEY: _MPF_MOD}) is None
+    and _mpf_unmetered(_MPF_UNMETERED) == _MPF_FREEZE,
+)
+
+_mpf_space = np.array([0.0, 0.3, 2.8, 4.0, 1.0, 2.8, 0.05, -0.2])
+_mpf_dhw = np.array([0.0, 0.0, 2.5, 0.0, 3.5, 0.0, 2.5, 0.0])
+_mpf_proj = _mpf_against(_mpf_space, _mpf_dhw, 2.5, 3.5)
+_mpf_rows = _mpf_against(np.vstack([_mpf_space, _mpf_space[::-1]]), _mpf_dhw, 2.5, 3.5)
+R.check(
+    "space projects against the DHW in its step: capped at p_max - dhw, a sub-minimum "
+    "level raised to p_min only where DHW is off, identity where the total already fits",
+    np.allclose(_mpf_proj, [0.0, 2.5, 1.0, 3.5, 0.0, 2.8, 0.05, 0.0])
+    and np.array_equal(_mpf_against(_mpf_space, np.zeros(8), 2.5, 3.5),
+                       _mpf_project(_mpf_space, 2.5, 3.5))
+    and np.array_equal(_mpf_rows[0], _mpf_proj)
+    and np.array_equal(_mpf_rows[1], _mpf_against(_mpf_space[::-1], _mpf_dhw, 2.5, 3.5)),
+    f"{_mpf_proj.tolist()}",
+)
+_mpf_r_space, _mpf_r_dhw = _mpf_realize(True, _mpf_space, np.array([0.0, 1.0, 2.5, 4.0, 0, 0, 0, 0]), 2.5, 3.5)
+R.check(
+    "a clamped install realizes DHW as its own projection and space against it; "
+    "unclamped and DHW-less draws are unchanged",
+    np.allclose(_mpf_r_dhw, [0.0, 2.5, 2.5, 3.5, 0, 0, 0, 0])
+    and np.allclose(_mpf_r_space, [0.0, 0.3, 1.0, 0.0, 2.5, 2.8, 2.5, 0.0])
+    and _mpf_realize(False, _mpf_space, _mpf_dhw, 2.5, 3.5)[0] is _mpf_space
+    and _mpf_realize(False, _mpf_space, _mpf_dhw, 2.5, 3.5)[1] is _mpf_dhw
+    and _mpf_realize(True, _mpf_space, None, 2.5, 3.5)[1] is None
+    and np.array_equal(_mpf_realize(True, _mpf_space, None, 2.5, 3.5)[0],
+                       _mpf_project(_mpf_space, 2.5, 3.5)),
+    f"space {_mpf_r_space.tolist()} dhw {_mpf_r_dhw.tolist()}",
+)
+
+_MPF_STEPS = np.arange(96)
+_MPF_SPREAD = 1.3 + 0.9 * np.sin(2 * np.pi * (_MPF_STEPS - 30) / 96.0)
+
+
+def _mpf_totals(cfg):
+    """Per-step space+DHW of the finder's spread/DHW/-4 degC cell under ``cfg``."""
+    params = _MpfTP()
+    params.mixing_valve_mode, params.buffer_tank_volume = "none", 0.0
+    params.min_electrical_power, params.max_electrical_power = 2.5, 3.5
+    params.dhw_enabled = True
+    out = -4.0 + 3 * np.sin(2 * np.pi * (_MPF_STEPS - 50) / 96)
+    opt = _MpfOpt(_MpfTM(params), _MpfCfg(
+        clamp_planned_levels=_MpfCfg.from_mapping(cfg).clamp_planned_levels,
+    ))
+    res = opt.optimize(inputs=solve_inputs(
+        initial_state=_MpfTS(
+            room_temperature=20.5, upper_floor_temperature=20.5,
+            lower_floor_temperature=20.5, slab_temperature=21.0,
+            outdoor_temperature=float(out[0]), dhw_temperature=50.0,
+        ),
+        prices=_MPF_SPREAD, outdoor_temps=out,
+        start_time=datetime(2026, 1, 10, tzinfo=UTC),
+    ))
+    return (np.asarray(res.power_schedule, float)
+            + np.asarray(res.dhw_power_schedule or np.zeros(96), float))
+
+
+def _mpf_off_or_band(tot):
+    return bool(np.all((tot == 0.0) | ((tot >= 2.5 - 1e-9) & (tot <= 3.5 + 1e-9))))
+
+
+_mpf_declared_tot = _mpf_totals(_mpf_on_off(_MPF_METERED))
+_mpf_probed_tot = _mpf_totals(_MPF_UNMETERED)
+R.check(
+    "per step, a declared on/off pump on a fully metered install plans every step off "
+    "or between min and max power (#3289)",
+    _mpf_off_or_band(_mpf_declared_tot),
+    f"steps below 2.5 {int(np.sum((_mpf_declared_tot > 0) & (_mpf_declared_tot < 2.5 - 1e-9)))}, "
+    f"max {_mpf_declared_tot.max():.2f}",
+)
+R.check(
+    "per step, a probed switch-plus-setpoint pump with DHW never plans space plus DHW "
+    "above max power, nor a running step below min power",
+    _mpf_off_or_band(_mpf_probed_tot),
+    f"max {_mpf_probed_tot.max():.2f}, steps below 2.5 "
+    f"{int(np.sum((_mpf_probed_tot > 0) & (_mpf_probed_tot < 2.5 - 1e-9)))}",
+)
+
 # --- R10-SETPOINT-POWER: the set-point is a power command (tvofi, 2026-10-19)
 # The modulation floor's flow sits FLOW_MIN_LIFT_K above the measured water
 # the pump heats, read from whichever sensors are configured, in the
@@ -69236,7 +69422,9 @@ R.check(
 # moved between arm64 and CI's x86_64. So the checks pin what the mechanism
 # guarantees on every platform -- a strictly lower objective where it wins,
 # never a higher one, and a plan that books above the floor -- not a cell's
-# basin.
+# basin. In the hot-water cells space ships projected against the DHW plan
+# (#3289, ``project_space_against``): before that, two cells shipped space
+# plus DHW above their 5.5 kW p_max; the checks' predicates hold either way.
 import heatpump_optimizer.optimizer as _sp_opt_mod  # noqa: E402
 from heatpump_optimizer.optimizer import (  # noqa: E402
     HeatPumpOptimizer as _SpOpt,
@@ -70819,6 +71007,21 @@ R.check(
     "S4 where the install can duty-cycle: the min end stays configured",
     _dr.planned_range(_dr_live, _dr_params(), _DR_DUTY) == (_DR_MIN, _dr_live_seen[1]),
 )
+_dr_duty_cfg = {_MPF_SETPOINT: "number.flow", _MPF_POWER: "sensor.hp_power"}
+R.check(
+    "S4 on a setpoint-only install declared on/off: the metered floor raises the min "
+    "end, as on a switch-plus-setpoint one (#3289); undeclared it stays configured",
+    _dr.planned_range(_dr_live, _dr_params(), _dr_probe(_mpf_on_off(_dr_duty_cfg)))
+    == _dr_live_seen
+    and _dr.planned_range(_dr_live, _dr_params(), _dr_probe(_dr_duty_cfg))
+    == (_DR_MIN, _dr_live_seen[1]),
+)
+R.check(
+    "S4 a declared on/off install whose plan writes the frequency still reads None",
+    _dr.planned_range(_dr_live, _dr_params(), _dr_probe(_mpf_on_off(
+        {_MPF_SWITCH: "switch.hp", _MPF_FREQ: "number.hz", _MPF_FREQ_MODE: _MPF_FREQ_CONTROL}
+    ))) is None,
+)
 _dr_below_min = _dr_learner("live", cfg=(2.0, _DR_MAX))
 _dr_below_seen = _dr_below_min.observed()
 R.check(
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index 0613eac7c..af32aba9b 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -67,6 +67,7 @@
 # v7.1.6: Round 10 fixes since v7.1.5. The stamp empties the list; the
 # next branch restates its own footprint, claims included.
 #
+config_flow # R10-MIN-POWER-FLOOR (#3289): the thermal_model options page gains the compressor_modulation select (auto/on_off/modulating, pre-filled auto); ADD-ONLY, one 10-line field leaf in the plain and one in the seeded render (git diff --numstat 20 insertions, 0 deletions), no existing leaf moves; re-recorded with --record --only config_flow because env_drift compares config_flow exactly
 # may-drift: flat_prices -- #1208 polish-every-candidate, owner ruling #1208 comment 208bed25
 # (option (a)): the move's margin is inside the noise band (objective rel
 # -1.2171e-03, deterministic on one box), so which runner sees it move is the
diff --git a/tests/golden/config_flow.json b/tests/golden/config_flow.json
index 9f3b6bf9d..eae019575 100644
--- a/tests/golden/config_flow.json
+++ b/tests/golden/config_flow.json
@@ -3468,6 +3468,16 @@
     "required": "Optional",
     "selector": "SelectSelector"
    },
+   "compressor_modulation": {
+    "config": {
+     "mode": "'dropdown'",
+     "options": "['auto', 'on_off', 'modulating']",
+     "translation_key": "'compressor_modulation'"
+    },
+    "default": "'auto'",
+    "required": "Optional",
+    "selector": "SelectSelector"
+   },
    "heat_pump_cop_nominal": {
     "config": {
      "max": "6.0",
@@ -5993,6 +6003,16 @@
    "required": "Optional",
    "selector": "SelectSelector"
   },
+  "compressor_modulation": {
+   "config": {
+    "mode": "'dropdown'",
+    "options": "['auto', 'on_off', 'modulating']",
+    "translation_key": "'compressor_modulation'"
+   },
+   "default": "'auto'",
+   "required": "Optional",
+   "selector": "SelectSelector"
+  },
   "heat_pump_cop_nominal": {
    "config": {
     "max": "6.0",
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_realize_draw.GUARD_OFF.bcb6002f.json b/tests/mutation_ledger/killed_by/optimizer.py/_realize_draw.GUARD_OFF.bcb6002f.json
new file mode 100644
index 000000000..bd6a4a5a9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_realize_draw.GUARD_OFF.bcb6002f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_realize_draw GUARD_OFF bcb6002f",
+  "killed_by": "tests/features.py",
+  "old": "    if dhw is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_realize_draw.RETURN_DEL.fb58784b.json b/tests/mutation_ledger/killed_by/optimizer.py/_realize_draw.RETURN_DEL.fb58784b.json
new file mode 100644
index 000000000..f5270324c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_realize_draw.RETURN_DEL.fb58784b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_realize_draw RETURN_DEL fb58784b",
+  "killed_by": "tests/plan_view.py",
+  "old": "    return _realize_joint(clamp, space, dhw, p_min, p_max)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_realize_joint.GUARD_OFF.55b8330e.json b/tests/mutation_ledger/killed_by/optimizer.py/_realize_joint.GUARD_OFF.55b8330e.json
new file mode 100644
index 000000000..724ee290d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_realize_joint.GUARD_OFF.55b8330e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_realize_joint GUARD_OFF 55b8330e",
+  "killed_by": "tests/doc_claims.py",
+  "old": "    if not clamp:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/doc_claims.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_realize_joint.RETURN_DEL.ca8c2e8b.json b/tests/mutation_ledger/killed_by/optimizer.py/_realize_joint.RETURN_DEL.ca8c2e8b.json
new file mode 100644
index 000000000..40f6cacfa
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_realize_joint.RETURN_DEL.ca8c2e8b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_realize_joint RETURN_DEL ca8c2e8b",
+  "killed_by": "tests/features.py",
+  "old": "    return project_space_against(space, tank, p_min, p_max), tank",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.can_duty_cycle.GUARD_OFF.1329ac75.json b/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.can_duty_cycle.GUARD_OFF.1329ac75.json
new file mode 100644
index 000000000..242383a5d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.can_duty_cycle.GUARD_OFF.1329ac75.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:InstallCapability.can_duty_cycle GUARD_OFF 1329ac75",
+  "killed_by": "tests/features.py",
+  "old": "        if self.on_off:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/project_planned_levels.RETURN_DEL.920a8da2.json b/tests/mutation_ledger/killed_by/thermal_model.py/project_planned_levels.RETURN_DEL.920a8da2.json
new file mode 100644
index 000000000..76b3e42a8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/project_planned_levels.RETURN_DEL.920a8da2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:project_planned_levels RETURN_DEL 920a8da2",
+  "killed_by": "tests/features.py",
+  "old": "    return _onto_band(np.asarray(power, dtype=float), float(p_min), float(p_max))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index b09de8666..0c48efaa2 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17560,
+ "class_excess_loc": 17558,
  "const_modules_over_50": 3,
  "coordinator_attrs": 141,
  "coordinator_multiassigned_attrs": 108,
@@ -16,6 +16,6 @@
  "methods_over_150": 15,
  "methods_over_200": 8,
  "name_kept_members": 38,
- "recorded_at": "28482eceeb6b9809e44b12d80fc994282cc21645",
+ "recorded_at": "dee8b413fd7da7b07f13e28a93d7d49b4a9e978a",
  "seam_cut_total": 423
 }

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
