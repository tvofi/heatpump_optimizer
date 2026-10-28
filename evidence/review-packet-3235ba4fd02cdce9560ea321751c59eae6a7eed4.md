# Review packet #2876
head: 3235ba4fd02cdce9560ea321751c59eae6a7eed4
base: 07295d4ea1471048ee2a76a6776b5cd364dcf141

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=122583207948 neutral
arch-score / arch-score id=122582935245 success
arm id=122582827520 skipped
budget-raise-gate / budget-raise-gate id=122582935362 success
cancel-superseded id=122582828867 success
codeql / Analyze (actions) id=122582935134 success
codeql / Analyze (javascript-typescript) id=122582935166 success
codeql / Analyze (python) id=122582935106 in_progress
governance / delivery-status id=122582935458 success
governance / delivery-status-publish id=122582936855 skipped
governance / env-matrix id=122582935338 in_progress
governance / instrument-self-tests id=122582935439 in_progress
governance / policy-docs id=122582935378 in_progress
governance / record id=122582936441 skipped
governance / wave-script id=122582935242 success
hassfest / hassfest id=122582934920 success
kernel-points id=122582935953 skipped
prelude id=122582828825 in_progress
refresh id=122582828619 success
tests / arch-instrument id=122583047775 success
tests / briefs id=122582935139 success
tests / browser id=122583048004 in_progress
tests / closure-scope id=122582935219 success
tests / closures id=122583047972 in_progress
tests / coverage id=122583047892 in_progress
tests / fast (3.14) id=122583047877 in_progress
tests / mutation id=122582935144 in_progress
tests / nightly-ha id=122583049370 skipped
tests / nightly-status id=122582935181 success
tests / replay id=122583048060 success
tests / typing id=122583047867 success
validate / validate-hacs id=122582934965 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 679ffd42: R10-COP-GATE
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_house_grade.py
             `dev/audit/harnesses/r10_house_grade.py` is in the tree at this head
  unverified git archive 3b4180dcc | tar -x -C .scratch/base-3b4180dcc
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_house_grade.py --era-blind
             `dev/audit/harnesses/r10_house_grade.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_scores_envelope.py
             `dev/audit/harnesses/r10_scores_envelope.py` is in the tree at this head
  ok         python3 tests/plan_view.py
             `tests/plan_view.py` is in the tree at this head
  ok         node tests/card_drift.mjs
             `tests/card_drift.mjs` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/env_drift.py --all $(git merge-base origin/main HEAD)
             `tests/env_drift.py` is in the tree at this head
  ok         python3 tests/env_drift.py --claims-only $(git merge-base origin/main HEAD)
             `tests/env_drift.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  unverified python3 -I -c "import sys; sys.path.insert(0,'tests'); import env_drift as E; c=E._claimed_at('.','HEAD',E.CLAIM_FILE); print(sorted(E.excusing_claims('.','origin/main',c)))"
             python3 runs an inline script rather than a file
  unverified git diff $(git merge-base origin/main HEAD)...HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git diff --name-only
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 9 resolved, 4 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/envelope_score.CLAMP_DROP.85c51bc5.json b/tests/mutation_ledger/killed_by/coordinator.py/envelope_score.CLAMP_DROP.85c51bc5.json
deleted file mode 100644
index 80377a993..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/envelope_score.CLAMP_DROP.85c51bc5.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:envelope_score CLAMP_DROP 85c51bc5",
-  "killed_by": "tests/features.py",
-  "old": "    return float(np.clip(np.log(tau_h / low_h) / np.log(high_h / low_h), 0.0, 1.0)) * 100.0, None",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return float((np.log(tau_h / low_h) / np.log(high_h / low_h))) * 100.0, None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/envelope_score.RETURN_DEL.85c51bc5.json b/tests/mutation_ledger/killed_by/coordinator.py/envelope_score.RETURN_DEL.63a529d6.json
similarity index 62%
rename from tests/mutation_ledger/killed_by/coordinator.py/envelope_score.RETURN_DEL.85c51bc5.json
rename to tests/mutation_ledger/killed_by/coordinator.py/envelope_score.RETURN_DEL.63a529d6.json
index 482521919..1613b0c51 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/envelope_score.RETURN_DEL.85c51bc5.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/envelope_score.RETURN_DEL.63a529d6.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:envelope_score RETURN_DEL 85c51bc5",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:envelope_score RETURN_DEL 63a529d6",
   "killed_by": "tests/features.py",
-  "old": "    return float(np.clip(np.log(tau_h / low_h) / np.log(high_h / low_h), 0.0, 1.0)) * 100.0, None",
+  "old": "    return grade, None, drivers",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
 }
diff --git a/tests/mutation_ledger/killed_by/presets.py/@module.CONST.00acd129.json b/tests/mutation_ledger/killed_by/presets.py/@module.CONST.00acd129.json
new file mode 100644
index 000000000..e373d822f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/presets.py/@module.CONST.00acd129.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/presets.py:<module> CONST 00acd129",
+  "killed_by": "tests/features.py",
+  "old": "_GRADE_FLOOR = 1.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`_GRADE_FLOOR = 2.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/presets.py/@module.CONST.33dc5605.json b/tests/mutation_ledger/killed_by/presets.py/@module.CONST.33dc5605.json
new file mode 100644
index 000000000..8c917e315
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/presets.py/@module.CONST.33dc5605.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/presets.py:<module> CONST 33dc5605",
+  "killed_by": "tests/features.py",
+  "old": "_GRADE_SLOPE = 1.5",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`_GRADE_SLOPE = 3.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/presets.py/envelope_band_hours.RETURN_DEL.1875d362.json b/tests/mutation_ledger/killed_by/presets.py/envelope_band_hours.RETURN_DEL.1875d362.json
deleted file mode 100644
index 3a66b46e9..000000000
--- a/tests/mutation_ledger/killed_by/presets.py/envelope_band_hours.RETURN_DEL.1875d362.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/presets.py:envelope_band_hours RETURN_DEL 1875d362",
-  "killed_by": "tests/features.py",
-  "old": "    return min(taus), max(taus)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/presets.py/house_grade.CLAMP_DROP.83e9daf2.json b/tests/mutation_ledger/killed_by/presets.py/house_grade.CLAMP_DROP.83e9daf2.json
new file mode 100644
index 000000000..d1258ce18
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/presets.py/house_grade.CLAMP_DROP.83e9daf2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/presets.py:house_grade CLAMP_DROP 83e9daf2",
+  "killed_by": "tests/features.py",
+  "old": "    grade = max(100.0 / (1.0 + math.exp(_GRADE_SLOPE * total)), _GRADE_FLOOR)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`grade = (100.0 / (1.0 + math.exp(_GRADE_SLOPE * total)))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/config_flow.py b/custom_components/heatpump_optimizer/config_flow.py
index fd62ae00a..bc51e5feb 100644
--- a/custom_components/heatpump_optimizer/config_flow.py
+++ b/custom_components/heatpump_optimizer/config_flow.py
@@ -1167,26 +1167,11 @@ def _questionnaire_fields(current: dict[str, Any]) -> dict[Any, Any]:
 def _derive_preset(answers: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
     """Turn questionnaire answers into thermal-parameter starting values.
 
-    ``two_zone`` is the canonical predicate's verdict on the configuration in
-    force (R9 D14-s2-01) — the same rule ``ThermalParameters.from_config``
-    applies — never a proxy read of one zone key, which ignored the mode
-    override, the other presence keys and a present-but-0.0 value. A fresh
-    setup has no zone keys, so the questionnaire derives a single-zone model
-    and never writes the keys whose presence would flip two-zone on.
+    A fresh setup has no zone keys, so the questionnaire derives a
+    single-zone model and never writes the keys whose presence would flip
+    two-zone on (``presets.preset_from_config``).
     """
-    preset = presets.BuildingPreset(
-        structure=answers.get(CONF_BUILDING_STRUCTURE, ""),
-        era=answers.get(CONF_BUILDING_ERA, ""),
-        foundation=answers.get(CONF_BUILDING_FOUNDATION, ""),
-        heated_area_m2=float(answers.get(CONF_HEATED_AREA, DEFAULT_HEATED_AREA)),
-        upper_emitter=answers.get(CONF_UPPER_EMITTER, ""),
-        lower_emitter=answers.get(CONF_LOWER_EMITTER, ""),
-        upper_area_ratio=float(
-            current.get(CONF_UPPER_FLOOR_AREA_RATIO, DEFAULT_UPPER_FLOOR_AREA_RATIO)
-        ),
-        two_zone=ThermalParameters.from_config(current).two_zone_enabled,
-    )
-    derived = presets.derive(preset)
+    derived = presets.derive(presets.preset_from_config(answers, current))
     # The derived response time is informational; it is not a thermal
     # parameter and would be rejected by the model.
     derived.pop("heating_response_hours", None)
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index f222cccea..5a499e928 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -2923,17 +2923,17 @@ def _refit_disagrees(advice: Mapping[str, Any], scale: float) -> bool:
 
 
 def envelope_score(
-    params: ThermalParameters, samples: int, advice: Mapping[str, Any]
-) -> tuple[float | None, str | None]:
-    """The house grade (#65) and, when it is None, the one code saying why.
-
-    The time constant ``envelope_thermal_mass / loss`` in hours, placed on a
-    log scale between the shortest and the longest any shipped preset
-    derives (``presets.envelope_band_hours``). ``loss`` is the model's own
-    whole-house figure, both zones with the learned split -- the one the
-    Health tab publishes (#2239) -- and the mass is the one the dynamics
-    store, slab and zones included, so the grade is the house the model
-    simulates, as measured. The codes, in precedence (#2258):
+    params: ThermalParameters,
+    samples: int,
+    advice: Mapping[str, Any],
+    config: Mapping[str, Any],
+) -> tuple[float | None, str | None, list[dict[str, Any]]]:
+    """The house grade (#65), the code saying why it is None, and its drivers.
+
+    ``presets.house_grade``: the model's own whole-house loss, both zones
+    with the learned split -- the one the Health tab publishes (#2239) --
+    and the mass the dynamics store, against the configured type and era
+    (#2816). The codes, in precedence (#2258):
     nothing to grade; the learner still walking from its prior; a refit
     of settled evidence outside its band of the learned scale.
     """
@@ -2943,14 +2943,13 @@ def envelope_score(
     # The loss is rounded to 1e-4 kW/K, so a house with no loss reads 0.0.
     loss = _effective_house_heat_loss(params, scale)
     if loss <= 0.0 or params.envelope_thermal_mass <= 0.0:
-        return None, "no_house_model"
+        return None, "no_house_model", []
     if not house_loss_converged(samples):
-        return None, "heat_loss_learning"
+        return None, "heat_loss_learning", []
     if _refit_disagrees(advice, scale):
-        return None, "heat_loss_refit_disagrees"
-    low_h, high_h = presets.envelope_band_hours()
-    tau_h = params.envelope_thermal_mass / loss
-    return float(np.clip(np.log(tau_h / low_h) / np.log(high_h / low_h), 0.0, 1.0)) * 100.0, None
+        return None, "heat_loss_refit_disagrees", []
+    grade, drivers = presets.house_grade(params, scale, config)
+    return grade, None, drivers
 
 
 def machine_score(
@@ -2973,7 +2972,7 @@ def operation_reason(score_day: Mapping[str, Any]) -> str:
 
 
 def compose_scores(
-    envelope: tuple[float | None, str | None],
+    envelope: tuple[float | None, str | None, list[dict[str, Any]]],
     machine: tuple[float | None, str | None],
     operation: tuple[float | None, str | None],
 ) -> Scores:
@@ -2982,19 +2981,24 @@ def compose_scores(
     Envelope is the house; it stays in the breakdown. Overall is machine and
     operation only -- averaging the house in is how a DHW-only cheap-hour plan
     reads as 5/100. None is no evidence and is never 0: each None carries one
-    code in ``reasons`` (#2258), and a grade carries none.
+    code in ``reasons`` (#2258), and a grade carries none. The house grade's
+    drivers ride ``envelope_drivers`` (#2816).
     """
-    parts = {"envelope": envelope, "machine": machine, "operation": operation}
+    house = envelope[:2]
+    parts = {"envelope": house, "machine": machine, "operation": operation}
     reasons = {key: why for key, (_grade, why) in parts.items() if why is not None}
     available = [g for g, _why in (machine, operation) if g is not None]
     if not available:
         reasons["overall"] = "first_scored_day"
     return {
-        "envelope": None if envelope[0] is None else round(envelope[0], 1),
+        "envelope": None if house[0] is None else round(house[0], 1),
         "machine": None if machine[0] is None else round(machine[0], 1),
         "operation": None if operation[0] is None else round(operation[0], 1),
         "overall": round(float(np.mean(available)), 1) if available else None,
         "reasons": reasons,
+        "envelope_drivers": [
+            {"code": d["code"], "points": round(d["points"], 1)} for d in envelope[2]
+        ],
     }
 
 
@@ -10458,8 +10462,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         return compose_scores(
             envelope_score(
                 getattr(self, "_ctx", self)._thermal_params,
-                self._house_heat_loss_samples,
-                advice,
+                self._house_heat_loss_samples, advice,
+                getattr(self, "_ctx", self)._config,
             ),
             machine_score(self._cop_baseline, self._cop_health_cusum.stat),
             (operation, None if operation is not None else operation_reason(self._score_day)),
diff --git a/custom_components/heatpump_optimizer/payload.py b/custom_components/heatpump_optimizer/payload.py
index c2b919bfa..987c5f557 100644
--- a/custom_components/heatpump_optimizer/payload.py
+++ b/custom_components/heatpump_optimizer/payload.py
@@ -41,7 +41,7 @@ mypy now checks. Values read through a coordinator's hubs are checked too:
 from __future__ import annotations
 
 from datetime import datetime
-from typing import TYPE_CHECKING, TypedDict
+from typing import TYPE_CHECKING, Any, TypedDict
 
 if TYPE_CHECKING:
     from .open_meteo import SolarDiagnostics  # standalone-loaded by a test: not imported at run time
@@ -266,6 +266,9 @@ class Scores(TypedDict, total=False):
     envelope: float | None
     #: One code per score that is None, and only for those (#2258).
     reasons: dict[str, str]
+    #: What moves the house grade off 50: ``code`` and signed ``points``,
+    #: summing to ``envelope - 50`` (#2816).
+    envelope_drivers: list[dict[str, Any]]
 
 
 class CompressorStarts(TypedDict, total=False):
diff --git a/custom_components/heatpump_optimizer/presets.py b/custom_components/heatpump_optimizer/presets.py
index eaa793f65..d4a40626c 100644
--- a/custom_components/heatpump_optimizer/presets.py
+++ b/custom_components/heatpump_optimizer/presets.py
@@ -23,11 +23,22 @@ shipped as absolute numbers per archetype.
 """
 from __future__ import annotations
 
-import functools
-import itertools
+import math
+from collections.abc import Mapping
 from dataclasses import dataclass
 from typing import Any
 
+from .const import (
+    CONF_BUILDING_ERA,
+    CONF_BUILDING_FOUNDATION,
+    CONF_BUILDING_STRUCTURE,
+    CONF_HEATED_AREA,
+    CONF_LOWER_EMITTER,
+    CONF_UPPER_EMITTER,
+    CONF_UPPER_FLOOR_AREA_RATIO,
+    DEFAULT_HEATED_AREA,
+    DEFAULT_UPPER_FLOOR_AREA_RATIO,
+)
 from .thermal_model import ThermalParameters
 
 # --- Structure -------------------------------------------------------------
@@ -279,26 +290,79 @@ def derive(preset: BuildingPreset) -> dict[str, Any]:
     return result
 
 
-@functools.cache
-def envelope_band_hours() -> tuple[float, float]:
-    """The shortest and longest envelope time constant the presets derive, h.
+def preset_from_config(
+    answers: Mapping[str, Any], current: Mapping[str, Any]
+) -> BuildingPreset:
+    """The questionnaire's preset for ``answers`` on the configuration ``current``.
 
-    Every structure, era, foundation and emitter, single- and two-zone, at
-    the configured prior (no learned scale), each ``envelope_thermal_mass``
-    over ``house_heat_loss_base``. The house grade (#65) places a house
-    between the two on a log scale -- a time constant is a ratio, and the
-    eras' losses step by ratios -- so the band moves with this table and is
-    never a second, uncalibrated pair of literals (R10-SCORES).
+    ``two_zone`` is the canonical predicate's verdict on the configuration in
+    force (R9 D14-s2-01) -- the rule ``ThermalParameters.from_config``
+    applies -- never a proxy read of one zone key. An unanswered question, or
+    one posted blank, falls to the preset's own default: named here rather
+    than left to ``validate``, because a reader outside ``config_flow`` has
+    to state what absence means. ``config_flow._ABSENT_FALLBACKS`` pairs each
+    key with the same value, and ``tests/config_flow_steps.py``'s absent-key
+    proof reads the two against each other.
     """
-    taus = []
-    for structure, era, foundation, emitter, two_zone in itertools.product(
-        STRUCTURES, ERAS, FOUNDATIONS, EMITTERS, (False, True)
-    ):
-        params = ThermalParameters.from_config(derive(BuildingPreset(
-            structure=structure, era=era, foundation=foundation,
-            lower_emitter=emitter, two_zone=two_zone)))
-        taus.append(params.envelope_thermal_mass / params.house_heat_loss_base)
-    return min(taus), max(taus)
+    return BuildingPreset(
+        structure=answers.get(CONF_BUILDING_STRUCTURE, STRUCTURE_TIMBER_SLAB),
+        era=answers.get(CONF_BUILDING_ERA, ERA_1980_2005),
+        foundation=answers.get(CONF_BUILDING_FOUNDATION, FOUNDATION_NONE),
+        heated_area_m2=float(answers.get(CONF_HEATED_AREA, DEFAULT_HEATED_AREA)),
+        upper_emitter=answers.get(CONF_UPPER_EMITTER, EMITTER_RADIATORS),
+        lower_emitter=answers.get(CONF_LOWER_EMITTER, EMITTER_FLOOR),
+        upper_area_ratio=float(
+            current.get(CONF_UPPER_FLOOR_AREA_RATIO, DEFAULT_UPPER_FLOOR_AREA_RATIO)
+        ),
+        two_zone=ThermalParameters.from_config(dict(current)).two_zone_enabled,
+    ).validate()
+
+
+#: The house grade's slope in log loss ratio: the owner's ~100-year-old house
+#: at 1.5x the typical pre-1960 loss grades 35, inside #2816's asked 30-40.
+_GRADE_SLOPE = 1.5
+#: 0 is reserved for no data (#2816), so a measured house never rounds onto it.
+_GRADE_FLOOR = 1.0
+
+
+def house_grade(
+    params: ThermalParameters, scale: float, config: Mapping[str, Any]
+) -> tuple[float, list[dict[str, Any]]]:
+    """The house grade (#65, #2816) and the drivers that account for it.
+
+    The loss ratio is the model's envelope loss (W/K) against the loss
+    ``derive`` gives the configured type, era, foundation and area,
+    corrected for thermal mass: the learner identifies the time constant
+    ``mass / loss``, so a loss read off a mass unlike the typical one is
+    rescaled by ``typical_mass / mass``. The ratio is therefore
+    ``typical_tau / tau``, and its log is the sum of three drivers: the
+    configured loss against typical, the learned correction (``scale``),
+    and the mass correction. The grade is ``100 / (1 + ratio ** slope)``:
+    50 at typical, above for tighter, below for leakier, never 0. Each
+    driver's ``points`` is its log share of the distance from 50, so the
+    points sum to ``grade - 50``.
+
+    There is deliberately no driver for an unconfigured building era: an
+    absent era grades exactly as the form's default era, which the entry's
+    absent-key contract states (``config_flow._ABSENT_FALLBACKS``) and
+    ``tests/config_flow_steps.py`` proves, so the two cases are one and
+    there is nothing to disclose. A read that told them apart would fail
+    that proof; the grade says so here rather than in a driver.
+    """
+    typical = ThermalParameters.from_config(derive(preset_from_config(config, config)))
+    logs = {
+        "loss_vs_typical": math.log(params.house_heat_loss_base / typical.house_heat_loss_base),
+        "learned_heat_loss": math.log(scale),
+        "thermal_mass": math.log(
+            typical.envelope_thermal_mass / params.envelope_thermal_mass
+        ),
+    }
+    total = sum(logs.values())
+    grade = max(100.0 / (1.0 + math.exp(_GRADE_SLOPE * total)), _GRADE_FLOOR)
+    return grade, [
+        {"code": code, "points": (grade - 50.0) * value / total if total else 0.0}
+        for code, value in logs.items()
+    ]
 
 
 def _radiator_fraction(preset: BuildingPreset) -> float:
diff --git a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
index 30bf0dd25..daa51197c 100644
--- a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
+++ b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
@@ -760,9 +760,10 @@ const STRINGS = {
       "The average of whichever scores below have evidence. " +
       "Not a score of its own.",
     "score.part_envelope":
-      "House: how long the building holds its stored heat " +
-      "(time constant). Low points at a leaky envelope — insulation, or a " +
-      "learned heat loss worse than configured.",
+      "House: the envelope's heat loss in W/K, corrected for thermal mass, " +
+      "against what is typical for the configured house type and building " +
+      "era. 50 is typical for that type and era; above is tighter, below " +
+      "leakier. Never 0 — that is only for no data.",
     "score.part_machine":
       "Machine: the heat pump's observed efficiency against its own " +
       "baseline. Low points at the pump drawing more electricity than its " +
@@ -786,6 +787,12 @@ const STRINGS = {
     "score.reason_first_scored_day": "Waiting for the first scored day.",
     // Short names for the breakdown rows; the explanations follow below.
     "score.label_envelope": "House",
+    // What moves the house grade off 50, one per code the coordinator
+    // publishes in `envelope_drivers` (#2816), with its signed points.
+    "score.driver_loss_vs_typical": "configured heat loss vs typical for the type and era",
+    "score.driver_learned_heat_loss": "learned heat loss vs configured",
+    "score.driver_thermal_mass": "thermal-mass correction",
+    "score.driver_typical": "typical for its type and era",
     "score.label_machine": "Heat pump",
     "score.label_operation": "Driving",
     // The percent is a template because the spacing is orthographic:
@@ -1483,9 +1490,10 @@ const STRINGS = {
       "Genomsnittet av de delbetyg nedan som har underlag. " +
       "Intet eget betyg.",
     "score.part_envelope":
-      "Huset: hur länge byggnaden håller kvar sin lagrade värme " +
-      "(tidskonstant). Lågt pekar på ett läckande klimatskal — isolering, " +
-      "eller en inlärd värmeförlust sämre än den konfigurerade.",
+      "Huset: klimatskalets värmeförlust i W/K, korrigerad för " +
+      "värmetröghet, mot det typiska för den inställda hustypen och " +
+      "byggperioden. 50 är typiskt för den typen och perioden; över är " +
+      "tätare, under läckigare. Aldrig 0 — det betyder bara inget underlag.",
     "score.part_machine":
       "Maskinen: värmepumpens uppmätta effektivitet mot sitt eget " +
       "baslinjevärde. Lågt pekar på att pumpen drar mer el än sitt eget " +
@@ -1506,6 +1514,10 @@ const STRINGS = {
       "Nollställd efter en rad dagar med gratis el; väntar på en dag med pris.",
     "score.reason_first_scored_day": "Väntar på den första bedömda dagen.",
     "score.label_envelope": "Huset",
+    "score.driver_loss_vs_typical": "inställd värmeförlust mot typisk för typ och period",
+    "score.driver_learned_heat_loss": "inlärd värmeförlust mot inställd",
+    "score.driver_thermal_mass": "korrigering för värmetröghet",
+    "score.driver_typical": "typiskt för sin typ och period",
     "score.label_machine": "Värmepumpen",
     "score.label_operation": "Körningen",
     "headline.savings_pct": "({pct} %)",
@@ -8694,10 +8706,25 @@ function scoreParts(plan) {
   return ["envelope", "machine", "operation"].map((key) => {
     const value = readNumber(attrs[key]);
     return { key, label: L(`score.label_${key}`), value,
-      reason: value === null ? scoreReasonText(reasons[key]) : null };
+      reason: value === null ? scoreReasonText(reasons[key]) : null,
+      drivers: key === "envelope" && value !== null
+        ? envelopeDrivers(attrs.envelope_drivers) : "" };
   });
 }
 
+/** What moves the house grade off 50 (#2816): each driver the coordinator
+ * published with its signed whole points, or "typical" when none moves it a
+ * point -- so every shown grade carries at least one reason. An unknown
+ * code is skipped rather than shown raw. */
+function envelopeDrivers(drivers) {
+  const shown = (Array.isArray(drivers) ? drivers : [])
+    .filter((d) => STRINGS.en[`score.driver_${d.code}`] !== undefined)
+    .map((d) => ({ code: d.code, pts: Math.round(Number(d.points) || 0) }))
+    .filter((d) => d.pts !== 0)
+    .map((d) => `${L(`score.driver_${d.code}`)}${d.pts ? ` ${d.pts > 0 ? "+" : "−"}${Math.abs(d.pts)}` : ""}`);
+  return shown.length ? shown.join("; ") : L("score.driver_typical");
+}
+
 /** The words for a score's no-grade code; an unknown code is no evidence. */
 function scoreReasonText(code) {
   const key = `score.reason_${code}`;
@@ -8722,6 +8749,7 @@ function scoreBreakdownHtml(plan) {
         `<div class="sb-row" data-part="${p.key}">` +
         `<div class="sb-head"><span class="sb-name">${esc(p.label)}</span>` +
         `${bar}${value}</div>` +
+        (p.drivers ? `<div class="sb-text sb-drivers">${esc(p.drivers)}</div>` : "") +
         `<div class="sb-text">${esc(L(`score.part_${p.key}`))}</div>` +
         `</div>`
       );
@@ -8821,7 +8849,7 @@ function headlineHtml(plan, cfg, scoreOpen) {
         (p) =>
           `${p.label}: ${
               p.value === null ? `— ${p.reason}` : `${Math.round(p.value)}/100`
-            }`
+            }${p.drivers ? ` (${p.drivers})` : ""}`
       )
       .join(" · ");
     items.push({
@@ -8829,6 +8857,7 @@ function headlineHtml(plan, cfg, scoreOpen) {
       title:
         L("headline.score_title") +
         (breakdown ? `\n${breakdown}` : "") +
+        (parts[0].drivers ? `\n${L("score.part_envelope")}` : "") +
         `\n${L("headline.score_click_hint")}`,
       label: L("headline.score"),
       value: `${Math.round(score)}/100`,
diff --git a/dev/audit/harnesses/r10_house_grade.py b/dev/audit/harnesses/r10_house_grade.py
new file mode 100644
index 000000000..8fe635566
--- /dev/null
+++ b/dev/audit/harnesses/r10_house_grade.py
@@ -0,0 +1,115 @@
+#!/usr/bin/env python3
+"""R10-HOUSE-GRADE (#2816): the house grade against the configured type and era.
+
+WHY IT EXISTS. The owner's house (about 100 years old, new windows and added
+insulation) graded near 0: ``envelope_score`` placed the time constant on one
+band spanning every shipped preset, so any pre-1960 house sat at its bottom
+whatever its envelope did against houses of its own era. The owner's spec
+(2026-10-25): envelope loss in W/K, thermal-mass corrected, against typical
+for the configured type and era; typical is mid-scale; the owner's case, at
+about 1.5x typical pre-1960 loss, lands low but clearly nonzero (30-40).
+This harness drives the tree's own ``envelope_score`` on preset houses, so a
+later seat can re-take it at its own base.
+
+Arms (each prints RESULT lines):
+
+  eras    Every structure x era preset house, single-zone, configured with
+          its own answers, at learned scale 1.0 (loss ratio 1.0). Per cell
+          the published grade; ``era_spread`` is max - min over the grid.
+          Null control: at ratio 1.0 every era is typical for itself, so the
+          spread is 0 and every cell grades 50.
+  owner   The pre-1960 houses of every structure at learned scale 1.5 (the
+          owner's measured ~1.5x typical). ``owner_min``/``owner_max``.
+  curve   One pre-1960 house over scales 0.25-8: ``monotone`` (strictly
+          decreasing), ``curve_min`` (> 0: 0 is no data).
+  drivers Over the eras and owner cells: ``drivers_max_gap``, the largest
+          |sum(points) - (grade - 50)| -- the drivers account for the grade.
+
+Metric (one line): era_spread at ratio 1.0, and owner_min/owner_max.
+Command (repository root):
+    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_house_grade.py
+Expected at the head:
+    EXPECTED RESULT era_spread=0.0
+    EXPECTED RESULT owner_min=35.2
+    EXPECTED RESULT monotone=True
+At the merge base (3b4180dcc): era_spread=67.7, owner_min=20.3,
+    owner_max=44.3 (the grade moved with structure, not envelope),
+    monotone=False and curve_min=0.0 (clipped to the band), no drivers.
+Baseline SHA: 3b4180dcc. Machine: Darwin arm64, CI venv; float arithmetic on
+    fixed inputs, not a solve.
+Perturbation: --era-blind -- each house is configured without its era, so it
+    is graded against the default era: era_spread rises to 50.5 at the head.
+Null control: ratio 1.0 itself (the eras arm), where a correct normalization
+    gives 50 for every era and a band-based grade does not.
+Instrumented symbols: coordinator:envelope_score, presets:house_grade,
+    presets:derive.
+"""
+import os
+
+for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
+           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
+    os.environ.setdefault(_v, "1")
+
+import argparse  # noqa: E402
+import inspect  # noqa: E402
+import sys  # noqa: E402
+
+sys.path.insert(0, "tests")
+sys.path.insert(0, "custom_components")
+
+from heatpump_optimizer import presets  # noqa: E402
+from heatpump_optimizer.coordinator import envelope_score  # noqa: E402
+from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402
+
+CONVERGED_SAMPLES = 10**6
+SCALES = (0.25, 0.5, 0.8, 1.0, 1.25, 1.5, 2.0, 4.0, 8.0)
+
+
+def grade(structure, era, scale, era_blind):
+    config = {"building_structure": structure, "heated_area_m2": 140.0}
+    if not era_blind:
+        config["building_era"] = era
+    derived = presets.derive(presets.BuildingPreset(structure=structure, era=era))
+    params = ThermalParameters.from_config(derived)
+    params.house_heat_loss_scale = scale
+    args = [params, CONVERGED_SAMPLES, {}]
+    if "config" in inspect.signature(envelope_score).parameters:
+        args.append(config)
+    out = envelope_score(*args)
+    drivers = out[2] if len(out) > 2 else []
+    return out[0], drivers
+
+
+def main():
+    ap = argparse.ArgumentParser()
+    ap.add_argument("--era-blind", action="store_true")
+    a = ap.parse_args()
+    gaps = []
+    eras = []
+    for structure in presets.STRUCTURES:
+        for era in presets.ERAS:
+            g, drivers = grade(structure, era, 1.0, a.era_blind)
+            print(f"eras {structure} {era}: grade={round(g, 1)}")
+            eras.append(g)
+            if drivers:
+                gaps.append(abs(sum(d["points"] for d in drivers) - (g - 50.0)))
+    print(f"RESULT era_spread={round(max(eras) - min(eras), 1)}")
+    owner = []
+    for structure in presets.STRUCTURES:
+        g, drivers = grade(structure, presets.ERA_PRE_1960, 1.5, a.era_blind)
+        print(f"owner {structure}: grade={round(g, 1)} drivers={drivers}")
+        owner.append(g)
+        if drivers:
+            gaps.append(abs(sum(d["points"] for d in drivers) - (g - 50.0)))
+    print(f"RESULT owner_min={round(min(owner), 1)}")
+    print(f"RESULT owner_max={round(max(owner), 1)}")
+    curve = [grade(presets.STRUCTURE_TIMBER_CRAWLSPACE, presets.ERA_PRE_1960, s,
+                   a.era_blind)[0] for s in SCALES]
+    print(f"curve {list(zip(SCALES, [round(c, 2) for c in curve]))}")
+    print(f"RESULT monotone={all(x > y for x, y in zip(curve, curve[1:]))}")
+    print(f"RESULT curve_min={round(min(curve), 2)}")
+    print(f"RESULT drivers_max_gap={round(max(gaps), 9) if gaps else None}")
+
+
+if __name__ == "__main__":
+    main()
diff --git a/dev/audit/harnesses/r10_scores_envelope.py b/dev/audit/harnesses/r10_scores_envelope.py
index abafea6a9..9d523788b 100644
--- a/dev/audit/harnesses/r10_scores_envelope.py
+++ b/dev/audit/harnesses/r10_scores_envelope.py
@@ -29,9 +29,11 @@ Arms (each prints RESULT lines):
          where the head publishes one, its reason.
   band   The tree's own presets, single-zone and two-zone, each era and
          structure at 140 m2: the room-mass time constant, the grade the
-         20-100 h band gives it, and the tree's own grade (``tree_grade``:
-         R10-PARAMS-OWNER's envelope mass and preset band where the tree has
-         them).
+         20-100 h band gives it, and the tree's own grade on the preset's own
+         answers -- R10-HOUSE-GRADE's loss ratio where the tree has it, so
+         every preset reads 50 and the 20-100 h column shows what the all-era
+         band graded it instead; R10-PARAMS-OWNER's envelope mass and preset
+         band where the tree has that; the room-mass band at the merge base.
   bundle (optional, ``--bundle PATH``) The owner's diagnostics bundle: the
          stored scale, split and sample count, and the grade on both bases.
          Never commit a bundle: it is a user's private data.
@@ -44,6 +46,10 @@ Expected: at the merge base the gap is non-zero wherever the split left 1
     head it is 0 everywhere; under --ratio-override 1.0, 0 at both:
     EXPECTED RESULT split_cells=10
     EXPECTED RESULT split_max_abs_gap=0.0
+The head's ``tree_grade`` is R10-HOUSE-GRADE's ``presets.house_grade`` (#2816),
+    applied to the Health tab's published loss; the merge base has only the
+    preset band, so the same arm reads a different rule at each end by design
+    and the numbers above are the band's.
 Baseline SHA: 86425b9ad. Machine: Linux x86_64, CI venv 3.14; the grid is
     float arithmetic on fixed inputs, not a solve.
 Perturbation: --ratio-override 1.0 -- the split arm's gap falls to 0.
@@ -51,7 +57,8 @@ Null control: the same flag at the merge base -- 0 there too, so the base's
     gap is the split's and not a scale-only drift.
 Instrumented symbols: coordinator:HeatPumpOptimizerCoordinator._scores_view,
     coordinator:HeatPumpOptimizerCoordinator._learning_view (via
-    house_heat_loss_effective), presets:derive.
+    house_heat_loss_effective), presets:derive, presets:house_grade where the
+    tree has it.
 """
 import os
 
@@ -86,10 +93,20 @@ def grade(tau_h):
     return round(max(0.0, min(1.0, (tau_h - 20.0) / 80.0)) * 100.0, 1)
 
 
-def tree_grade(params, loss_kw_per_k):
-    """The tree's own rule on the Health tab's loss: R10-PARAMS-OWNER's mass
-    basis and preset band where the tree has them, else the 20-100 h band on
-    the room mass (the merge base's rule), so the split arm reads either end."""
+def tree_grade(params, loss_kw_per_k, config=None):
+    """The tree's own rule on the Health tab's loss, at whichever stage it is.
+
+    R10-HOUSE-GRADE's ``presets.house_grade`` (#2816) where the tree has it,
+    else R10-PARAMS-OWNER's preset band on the envelope mass, else the 20-100 h
+    band on the room mass (the merge base's rule) -- so the split arm reads
+    either end. The Health tab's figure is driven in as the model's own loss,
+    which is the one ``house_grade`` reads, so the gap is that rule applied to
+    the published number rather than a second reading of the call that made it.
+    """
+    house = getattr(presets, "house_grade", None)
+    if house is not None:
+        return round(house(params, loss_kw_per_k / params.house_heat_loss_base,
+                           config or {})[0], 1)
     band = getattr(presets, "envelope_band_hours", None)
     if band is None:
         return grade(params.room_thermal_mass / loss_kw_per_k)
@@ -139,7 +156,8 @@ def arm_split(ratio_override):
             r = ratio if ratio_override is None else ratio_override
             params = params_from(derived, True)
             scores, eff = publish(coord, params, scale, r, CONVERGED_SAMPLES)
-            want = tree_grade(coord._thermal_params, eff)
+            want = tree_grade(coord._thermal_params, eff,
+                              getattr(coord, "_ctx", coord)._config)
             got = scores["envelope"]
             gap = None if got is None else round(abs(got - want), 1)
             print(f"split scale={scale} ratio={r}: envelope={got} health_grade={want} "
@@ -168,9 +186,14 @@ def arm_band():
                     structure=structure, era=era, two_zone=two_zone))
                 tau = d["house_thermal_mass"] / d["house_heat_loss_coefficient"]
                 p = ThermalParameters.from_config(d)
+                # The preset's own answers, so ``tree_grade`` grades this house
+                # against the type and era it was configured with (#2816).
+                cfg = dict(d, building_structure=structure, building_era=era)
+                loss = (p.heat_loss_coefficient if not p.two_zone_enabled
+                        else p.upper_floor_heat_loss + p.lower_floor_heat_loss_learned)
                 print(f"RESULT band two_zone={int(two_zone)} {structure} {era}: "
                       f"tau_h={tau:.1f} grade={grade(tau)} "
-                      f"tree_grade={tree_grade(p, p.heat_loss_coefficient if not p.two_zone_enabled else p.upper_floor_heat_loss + p.lower_floor_heat_loss_learned)}")
+                      f"tree_grade={tree_grade(p, loss, cfg)}")
 
 
 def arm_bundle(path):
diff --git a/dev/programme/delivery/2876.md b/dev/programme/delivery/2876.md
new file mode 100644
index 000000000..8861a2aa0
--- /dev/null
+++ b/dev/programme/delivery/2876.md
@@ -0,0 +1 @@
+- [#2876](https://github.com/tvofi/heatpump_optimizer/pull/2876) — **open**, R10-HOUSE-GRADE: derive the house grade from the delivered curve (R10-HOUSE-GRADE)
diff --git a/dev/programme/delivery/r10-house-grade.md b/dev/programme/delivery/r10-house-grade.md
new file mode 100644
index 000000000..d180bb6ee
--- /dev/null
+++ b/dev/programme/delivery/r10-house-grade.md
@@ -0,0 +1 @@
+- **R10-HOUSE-GRADE** — **handoff** `65ac142`, issues #2258 and #2816, roster: round-10 wave 2.
diff --git a/tests/card.mjs b/tests/card.mjs
index cd360180a..bf45e0158 100644
--- a/tests/card.mjs
+++ b/tests/card.mjs
@@ -5673,7 +5673,7 @@ function ctxL(card, key) {
   check("and the click does not open the expanded dialog",
     !clickOpenedDialog);
   check("each row carries its plain-language explanation",
-    /how long the building holds its stored heat/.test(openDump) &&
+    /corrected for thermal mass/.test(openDump) &&
     /against its own\s+baseline/.test(openDump) &&
     /buying at or above flat scores 0/.test(openDump),
     (openDump.match(/score-breakdown[\s\S]{0,900}/) || [""])[0]);
@@ -5737,7 +5737,7 @@ function ctxL(card, key) {
     if (tile) tile.dispatchEvent({ type: "click", stopPropagation() {} });
     const open = collect(card.shadowRoot).join("\n");
     const row = (key) => (open.match(new RegExp(`data-part="${key}"[\\s\\S]*?sb-text`)) || [""])[0];
-    return { closed, title, row, headline: (closed.match(/hl-score[\s\S]*?hl-value">([^<]*)</) || [null, null])[1] };
+    return { closed, open, title, row, headline: (closed.match(/hl-score[\s\S]*?hl-value">([^<]*)</) || [null, null])[1] };
   };
   const nullParts = surfaces(withScore("60", {
     envelope: null, machine: null, operation: 60, overall: 60,
@@ -5752,6 +5752,28 @@ function ctxL(card, key) {
     && !/0\/100/.test(nullParts.row("machine")) && !/sb-fill/.test(nullParts.row("machine")),
     nullParts.row("machine"));
 
+  // #2816: a house grade says on hover what moves it off 50 and what the
+  // metric is; one no driver moves a point is "typical", never reasonless.
+  const drivenHouse = surfaces(withScore("60", {
+    envelope: 35.2, machine: null, operation: 60, overall: 60,
+    reasons: { machine: "cop_watch_learning" },
+    envelope_drivers: [{ code: "loss_vs_typical", points: 0.0 },
+      { code: "learned_heat_loss", points: -14.8 }, { code: "thermal_mass", points: 0.0 },
+      { code: "not_a_code", points: 3.0 }] }));
+  check("#2816: the house hover names each driver with its signed points, and the metric",
+    /House: 35\/100 \(learned heat loss vs configured −15\)/.test(drivenHouse.title || "")
+    && drivenHouse.title.includes(fn("STRINGS.en")["score.part_envelope"])
+    && !/not_a_code|thermal-mass correction/.test(drivenHouse.title)
+    && /sb-drivers">learned heat loss vs configured −15</.test(drivenHouse.open),
+    drivenHouse.title);
+  const typicalHouse = surfaces(withScore("60", {
+    envelope: 50, machine: null, operation: 60, overall: 60,
+    reasons: { machine: "cop_watch_learning" },
+    envelope_drivers: [{ code: "loss_vs_typical", points: 0.2 }] }));
+  check("#2816: a house no driver moves a point reads typical, with a reason all the same",
+    /House: 50\/100 \(typical for its type and era\)/.test(typicalHouse.title || ""),
+    typicalHouse.title);
+
   // One message everywhere: for every score input -- a grade, or null with
   // each code the coordinator can publish for it -- the headline, the hover
   // and the breakdown say one number or one reason, never both and never a
diff --git a/tests/closures.json b/tests/closures.json
index fdec417fc..d216fe630 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3707,6 +3707,7 @@
    "dev/audit/harnesses/r10_gh_read_retry_mutants.py",
    "dev/audit/harnesses/r10_heat_meter.py",
    "dev/audit/harnesses/r10_heat_meter_mutants.py",
+   "dev/audit/harnesses/r10_house_grade.py",
    "dev/audit/harnesses/r10_i1_action_guards.py",
    "dev/audit/harnesses/r10_i1_solve_cpu_2x.py",
    "dev/audit/harnesses/r10_i1_sweep_guards.py",
diff --git a/tests/entities.py b/tests/entities.py
index 90677ef3c..5562214e6 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -4710,6 +4710,20 @@ _EC_RESIDUAL = {
                      "not declare the key",
     "grid_fee.py": "GridFeeSchedule.from_config is parsed once per EntryConfig, cached on identity",
     "price_model.py": "pull_prices resolves the price source from the merged mapping each pull",
+    # #2816 moved the questionnaire's own reads here from config_flow.py, which
+    # this census skips as a form-answer module. Every read of a building key
+    # in presets.py is inside preset_from_config: it takes the questionnaire's
+    # answers and the settings flow's current options (both config_flow's
+    # form), and house_grade hands it the coordinator's merged mapping to build
+    # the typical house the grade is measured against. EntryConfig declares no
+    # building structure, era, foundation, area or emitter key, so a parsed
+    # field cannot serve either call. The entry is module-wide because this
+    # table has no per-site arm; a read added elsewhere in presets.py would
+    # inherit it.
+    "presets.py": "preset_from_config reads the questionnaire's answers and the settings "
+                  "flow's current options into a BuildingPreset, and house_grade hands it "
+                  "the coordinator's merged config to build the typical house it measures "
+                  "against; EntryConfig declares none of the building keys",
     "quiet_windows.py": "the window readers also take the simulator's what-if mapping, which "
                         "overridden_config folds the call's quiet keys into",
     "thermal_model.py": "ThermalParameters.from_config, the solver's own parsed object, "
diff --git a/tests/features.py b/tests/features.py
index f29eb6ad9..2804239be 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -19476,72 +19476,103 @@ R.check(
     f"{_rs_d_view['model_restart']} {_rs_d_view['scores']}",
 )
 
-# R10-SCORES' forward carry, decided by R10-PARAMS-OWNER as the parameters'
-# owner: the grade's time constant reads every store the dynamics drain through
-# the house's loss (the zones, or the room, and the emitter slab), and its band
-# is the one the shipped presets derive, on a log scale -- the leakiest preset
-# grades 0 and the tightest 100, no other one clipped to either. The 20-100 h
-# band on the room mass clipped 78 of these 240 presets at the merge base.
+# #2816, the owner's spec: the house grade is the envelope's loss (W/K),
+# thermal-mass corrected, against typical for the configured type and era --
+# typical grades 50, leakier below but never 0 (no data), tighter above. The
+# one band over every preset graded an era, not an envelope: at the merge base
+# the twenty structure x era presets at their own typical loss spread 67.7
+# points (dev/audit/harnesses/r10_house_grade.py).
 import itertools as _env_it  # noqa: E402
 
 from heatpump_optimizer import presets as _env_presets  # noqa: E402
-from heatpump_optimizer.coordinator import _effective_house_heat_loss  # noqa: E402
 from heatpump_optimizer.coordinator import envelope_score as _env_score  # noqa: E402
 
+#: Config key -> ``BuildingPreset`` field.
+_ENV_FIELDS = {"building_structure": "structure", "building_era": "era",
+               "building_foundation": "foundation", "lower_floor_emitter": "lower_emitter"}
+_ENV_KEYS = tuple(_ENV_FIELDS)
 
-def _env_params(**kw):
-    return ThermalParameters.from_config(_env_presets.derive(_env_presets.BuildingPreset(**kw)))
 
+def _env_config(two_zone=False, **answers):
+    derived = _env_presets.derive(_env_presets.BuildingPreset(
+        two_zone=two_zone, **{_ENV_FIELDS[k]: v for k, v in answers.items()}))
+    return {**derived, **answers}
 
-def _env_grade(params):
-    return _env_score(params, 10**6, {})[0]
+
+def _env_grade(params, config, scale=1.0):
+    params = replace(params, house_heat_loss_scale=scale)
+    return _env_score(params, 10**6, {}, config)
 
 
 _env_cells = []
 for _env_key in _env_it.product(
         _env_presets.STRUCTURES, _env_presets.ERAS, _env_presets.FOUNDATIONS,
         _env_presets.EMITTERS, (False, True)):
-    _env_p = _env_params(**dict(zip(
-        ("structure", "era", "foundation", "lower_emitter", "two_zone"), _env_key)))
-    _env_tau = (getattr(_env_p, "envelope_thermal_mass", _env_p.room_thermal_mass)
-                / _effective_house_heat_loss(_env_p, 1.0))
-    _env_cells.append((round(_env_tau, 6), _env_grade(_env_p)))
-_env_lo, _env_hi = min(_env_cells)[0], max(_env_cells)[0]
-# Clipped: a preset at 0 or 100 that is not itself the band's end. Two presets
-# tie at each end where derive maps them to one house (timber on a slab over a
-# crawl space derives as the crawl-space structure, #93).
-_env_clipped = [c for c in _env_cells
-                if (c[1] == 0.0 and c[0] != _env_lo) or (c[1] == 100.0 and c[0] != _env_hi)]
-R.check(
-    "the house grade's band is the presets' own: the leakiest grades 0, the "
-    "tightest 100, and no other preset is clipped to either",
-    not _env_clipped and min(g for _t, g in _env_cells) == 0.0
-    and max(g for _t, g in _env_cells) == 100.0,
-    f"{len(_env_cells)} presets, {len(_env_clipped)} clipped",
-)
-_env_floor = _env_params(lower_emitter="floor")
-_env_zoned = _env_params(two_zone=True)
+    _env_cfg = _env_config(_env_key[4], **dict(zip(_ENV_KEYS, _env_key[:4])))
+    _env_cells.append(_env_grade(ThermalParameters.from_config(_env_cfg), _env_cfg))
+R.check(
+    "#2816 null control: every preset house at its own type and era's typical "
+    "loss grades 50, and its drivers say nothing moved it",
+    all(abs(g - 50.0) < 1e-9 and all(abs(d["points"]) < 1e-9 for d in dr)
+        for g, _why, dr in _env_cells),
+    f"{len(_env_cells)} presets, grades {sorted({round(c[0], 3) for c in _env_cells})}",
+)
+_env_old = _env_config(building_structure="timber_crawlspace", building_era="pre_1960")
+_env_old_p = ThermalParameters.from_config(_env_old)
+_env_owner = _env_grade(_env_old_p, _env_old, 1.5)
+R.check(
+    "#2816: the owner's house, a century old at 1.5x the typical pre-1960 "
+    "loss, grades low but clearly nonzero -- 30 to 40",
+    30.0 <= _env_owner[0] <= 40.0,
+    f"{_env_owner}",
+)
+_env_curve = [_env_grade(_env_old_p, _env_old, s)[0]
+              for s in (0.1, 0.5, 0.9, 1.0, 1.1, 2.0, 10.0, 1e6)]
+R.check(
+    "#2816: the grade falls strictly with the loss ratio until the floor, and "
+    "a measured house never grades 0",
+    all(x > y for x, y in zip(_env_curve[:-1], _env_curve[1:-1]))
+    and min(_env_curve) == 1.0 and _env_curve[0] > 50.0 > _env_curve[5],
+    f"{_env_curve}",
+)
+_env_new = dict(_env_old, building_era="post_2005")
+R.check(
+    "#2816: one envelope is graded against its own era: the same house reads "
+    "better configured as pre-1960 than as post-2005",
+    _env_grade(_env_old_p, _env_old)[0] > _env_grade(_env_old_p, _env_new)[0],
+)
+_env_drivers = [_env_owner, _env_grade(replace(
+    _env_old_p, room_thermal_mass=2 * _env_old_p.room_thermal_mass), _env_new, 0.7)]
+R.check(
+    "#2816: the drivers account for the grade: their points sum to its "
+    "distance from 50, the mass correction among them",
+    all(abs(sum(d["points"] for d in dr) - (g - 50.0)) < 1e-9
+        for g, _why, dr in _env_drivers)
+    and next(d for d in _env_drivers[1][2] if d["code"] == "thermal_mass")["points"] > 0,
+    f"{_env_drivers}",
+)
+_env_bare = {k: v for k, v in _env_old.items() if k != "building_era"}
+_env_default_era = dict(_env_old, building_era=_env_presets.ERA_1980_2005)
+R.check(
+    "#2816: a house with no configured era grades exactly as one configured with "
+    "the form's default era, driver for driver -- an absent answer is the default "
+    "house, not a different one",
+    _env_grade(_env_old_p, _env_bare)[0] == _env_grade(_env_old_p, _env_default_era)[0]
+    and _env_grade(_env_old_p, _env_bare)[2] == _env_grade(_env_old_p, _env_default_era)[2],
+    f"{_env_grade(_env_old_p, _env_bare)} vs "
+    f"{_env_grade(_env_old_p, _env_default_era)}",
+)
+_env_floor_cfg = _env_config(lower_floor_emitter="floor")
+_env_floor = ThermalParameters.from_config(_env_floor_cfg)
+_env_zoned_cfg = _env_config(True)
+_env_zoned = ThermalParameters.from_config(_env_zoned_cfg)
 R.check(
     "the house grade reads the mass the dynamics store: a floor-heated slab "
     "moves it, and a two-zone house's unused room mass does not",
-    _env_grade(replace(_env_floor, slab_thermal_mass=2 * _env_floor.slab_thermal_mass))
-    > _env_grade(_env_floor)
-    and _env_grade(replace(_env_zoned, room_thermal_mass=5 * _env_zoned.room_thermal_mass))
-    == _env_grade(_env_zoned),
-    f"floor {_env_grade(_env_floor)}, two-zone {_env_grade(_env_zoned)}",
-)
-
-# A time constant is a ratio, so the band is logarithmic: halving the loss --
-# doubling the time constant -- moves every unclipped house by the same points.
-_env_doubling = [
-    _env_grade(replace(_p, house_heat_loss_scale=0.5)) - _env_grade(_p)
-    for _p in (_env_params(), _env_params(era="pre_1960", structure="masonry"))
-]
-R.check(
-    "doubling the house's time constant moves its grade by the same points "
-    "wherever it starts",
-    abs(_env_doubling[0] - _env_doubling[1]) < 1e-6 and _env_doubling[0] > 0,
-    f"{_env_doubling}",
+    _env_grade(replace(_env_floor, slab_thermal_mass=2 * _env_floor.slab_thermal_mass),
+               _env_floor_cfg)[0] > _env_grade(_env_floor, _env_floor_cfg)[0]
+    and _env_grade(replace(_env_zoned, room_thermal_mass=5 * _env_zoned.room_thermal_mass),
+                   _env_zoned_cfg)[0] == _env_grade(_env_zoned, _env_zoned_cfg)[0],
 )
 
 # --- persistence: the detectors' memory rides the thermal store ----------------------
@@ -21489,13 +21520,15 @@ _ce._house_heat_loss_samples = 1000
 _ce._thermal_params.room_thermal_mass = 10.0
 _ce._thermal_params.heat_loss_coefficient = 0.1
 _ce._thermal_params.house_heat_loss_scale = 1.0
-# The band is the presets' own (R10-SCORES, decided by R10-PARAMS-OWNER):
-# a house at the longest time constant any preset derives grades 100, one at
-# the shortest 0. The mass is the envelope's, slab included.
+# The grade is against the configured type and era (#2816): ``_ce_typ`` is
+# the house ``derive`` gives this coordinator's answers.
 from heatpump_optimizer import presets as _ce_presets  # noqa: E402
 
-_ce_low_h, _ce_high_h = _ce_presets.envelope_band_hours()
+_ce_typ = ThermalParameters.from_config(_ce_presets.derive(
+    _ce_presets.preset_from_config(_ce._config, _ce._config)))
 _ce_mass = _ce._thermal_params.envelope_thermal_mass
+#: The loss at which this house's time constant is its typical one.
+_ce_mid = _ce_typ.house_heat_loss_base * _ce_mass / _ce_typ.envelope_thermal_mass
 
 
 def _ce_grade(loss, scale=1.0):
@@ -21505,25 +21538,13 @@ def _ce_grade(loss, scale=1.0):
 
 
 R.check(
-    "a house at the longest preset time constant grades 100 on the envelope",
-    abs(_ce_grade(_ce_mass / _ce_high_h) - 100.0) < 1e-6,
-    f"band {_ce_low_h:.1f}-{_ce_high_h:.1f} h, envelope mass {_ce_mass}",
-)
-R.check(
-    "a house at the shortest preset time constant grades 0 on the envelope",
-    abs(_ce_grade(_ce_mass / _ce_low_h)) < 1e-6,
-)
-R.check(
-    "#2258: a house past the longest time constant grades 100, not more",
-    _ce_grade(_ce_mass / (2.0 * _ce_high_h)) == 100.0,
+    "#2816: a house at its type and era's typical time constant grades 50",
+    abs(_ce_grade(_ce_mid) - 50.0) < 0.05,
+    f"typical {_ce_mid:.4f} kW/K at envelope mass {_ce_mass}",
 )
 R.check(
-    "#2258: a house under the shortest time constant grades 0, not less",
-    _ce_grade(_ce_mass / (0.5 * _ce_low_h)) == 0.0,
-)
-R.check(
-    "the band is a log scale: the geometric middle of the band grades 50",
-    abs(_ce_grade(_ce_mass / (_ce_low_h * _ce_high_h) ** 0.5) - 50.0) < 1e-6,
+    "#2816: twice the typical loss grades below 50, half of it above",
+    _ce_grade(2.0 * _ce_mid) < 50.0 < _ce_grade(0.5 * _ce_mid),
 )
 _ce_floored = _ce_grade(0.5, scale=0.1)
 R.check(
@@ -21539,6 +21560,55 @@ R.check(
     "0.25 kW/K configured at a learned scale of 0.5 grades as a 0.125 kW/K house",
 )
 _ce._thermal_params.house_heat_loss_scale = 1.0
+
+
+# #2816: the grade reads the entry's own answers and publishes the drivers that
+# explain it. At the merge base one band spanned every preset, so the same
+# house graded alike whatever its era; and the drivers are the seam
+# R10-COP-GATE mirrors, so their shape is pinned here, at the coordinator.
+def _ce_house(**cfg):
+    coord = _t2_coord(**cfg)
+    coord._house_heat_loss_samples = 1000
+    coord._thermal_params.room_thermal_mass = 10.0
+    coord._thermal_params.heat_loss_coefficient = 0.25
+    coord._thermal_params.house_heat_loss_scale = 1.0
+    return coord._scores_view(_rs_advice(coord))
+
+
+_ce_old = _ce_house(building_structure="timber", building_era="pre_1960")
+_ce_new = _ce_house(building_structure="timber", building_era="post_2005")
+R.check(
+    "#2816: the same house grades better as a pre-1960 house than as a "
+    "post-2005 one, so the grade reads the answers the entry was configured with",
+    _ce_old["envelope"] > _ce_new["envelope"],
+    f"pre-1960 {_ce_old['envelope']}, post-2005 {_ce_new['envelope']} "
+    "at 0.25 kW/K and 10 t",
+)
+R.check(
+    "#2816: the scores publish the grade's drivers, their points rounded to one "
+    "decimal and summing to its distance from 50",
+    {d["code"] for d in _ce_old["envelope_drivers"]}
+    == {"loss_vs_typical", "learned_heat_loss", "thermal_mass"}
+    and all(abs(round(d["points"], 1) - d["points"]) < 1e-9
+            for d in _ce_old["envelope_drivers"])
+    and abs(sum(d["points"] for d in _ce_old["envelope_drivers"])
+            - (_ce_old["envelope"] - 50.0)) < 0.25,
+    f"{_ce_old['envelope']} from {_ce_old['envelope_drivers']}",
+)
+_ce_blind = _ce_house(building_structure="timber")
+_ce_blind_era = _ce_house(building_structure="timber", building_era="1980_2005")
+R.check(
+    "#2816: a house with no configured era grades exactly as one configured with "
+    "the form's default era, drivers included, and the points still account for "
+    "the distance from 50",
+    _ce_blind["envelope"] == _ce_blind_era["envelope"]
+    and _ce_blind["envelope_drivers"] == _ce_blind_era["envelope_drivers"]
+    and abs(sum(d["points"] for d in _ce_blind["envelope_drivers"])
+            - (_ce_blind["envelope"] - 50.0)) < 0.25,
+    f"{_ce_blind['envelope']} vs {_ce_blind_era['envelope']} from "
+    f"{_ce_blind['envelope_drivers']}",
+)
+
 # The time constant needs both halves: a house with no thermal mass, or one
 # with no loss, has no envelope evidence -- None, never a grade of 0 and
 # never a division by zero.
@@ -21796,11 +21866,11 @@ R.check(
 )
 _ce._operation_score = None
 _ce._cop_baseline.clear()
-_ce._thermal_params.heat_loss_coefficient = _ce_mass / (1.05 * _ce_low_h)
+_ce._thermal_params.heat_loss_coefficient = 6.0 * _ce_mid
 _ce._thermal_params.house_heat_loss_scale = 1.0
 _leaky = _ce._scores_view(_rs_advice(_ce))
 R.check(
-    "a house near the leakiest preset is not 5/100 overall while nothing has been driven",
+    "a house six times its typical loss is not 5/100 overall while nothing has been driven",
     _leaky["overall"] is None
     and _leaky["envelope"] is not None
     and _leaky["envelope"] < 10.0,
diff --git a/tests/golden/card_claimed_drift.txt b/tests/golden/card_claimed_drift.txt
index 360c87621..1f470c06e 100644
--- a/tests/golden/card_claimed_drift.txt
+++ b/tests/golden/card_claimed_drift.txt
@@ -768,3 +768,16 @@
 # 1. the stylesheet alone:
 
 # 2. the redrawn Setup page, on top of the stylesheet:
+
+# R10-HOUSE-GRADE (#2816): the House score row explains the grade the way it is
+# now measured -- the envelope's heat loss in W/K, corrected for thermal mass,
+# against what is typical for the configured house type and building era -- and
+# the row and hover gain a line naming what moves it off 50, from the
+# `envelope_drivers` the coordinator publishes, each with its signed points.
+# Both languages move (score.part_envelope is rewritten and the score.driver_*
+# keys are new). score_open is the state that opens the score dialog, so it is
+# the one that renders either; its house row's explanation text changes
+# whatever the fixture publishes, and the driver line and the headline's
+# parenthetical follow the fixture's own scores. The other 44 states were
+# rendered and stayed identical.
+score_open  # R10-HOUSE-GRADE (#2816): the House row's explanation rewritten and its driver line added
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index 6d632da2d..c2ff77bbf 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -742,3 +742,23 @@
 # plan can land in another basin: valve_storage_low_target does, at a lower
 # plan cost here (predicted_cost 61.91 -> 61.05). The suspended fixtures'
 # plan leaves are their own machine-sensitive ones. No coord_* capture moves.
+# R10-HOUSE-GRADE (#2816): the scores publish `envelope_drivers` beside the
+# envelope grade, so every coord capture that publishes a grade gains
+# `data.insight.scores.envelope_drivers` and the same key under
+# `sensors.optimization_score.extra_state_attributes`. Those two leaves are the
+# whole diff in each fixture, both "present on one side only" and both ADDED at
+# this head (the direction); no price, cost, outdoor, price_known or
+# baseline_cost leaf moves. Claimed rather than re-recorded because the key is
+# the change: its points are the grade's own distance from 50 split by log
+# share, so the branch adds a published leaf rather than moving a recorded
+# value, and the fixtures stay the canonical environment's. The committed files
+# were patched in those two paths alone -- an empty list in each, because a
+# coord fixture publishes no grade (`envelope_score: null`) -- and no other leaf
+# was re-recorded: a claim excuses drift but not a structurally stale fixture
+# (`env_drift --all`'s `rot.failed`), which is the `tests / fast` red that
+# patch answers.
+coord_all_features  # R10-HOUSE-GRADE (#2816): data.insight.scores.envelope_drivers and sensors.optimization_score.extra_state_attributes.envelope_drivers added
+coord_dhw  # R10-HOUSE-GRADE (#2816): data.insight.scores.envelope_drivers and sensors.optimization_score.extra_state_attributes.envelope_drivers added
+coord_grid_fee  # R10-HOUSE-GRADE (#2816): data.insight.scores.envelope_drivers and sensors.optimization_score.extra_state_attributes.envelope_drivers added
+coord_minimal  # R10-HOUSE-GRADE (#2816): data.insight.scores.envelope_drivers and sensors.optimization_score.extra_state_attributes.envelope_drivers added
+coord_two_zone  # R10-HOUSE-GRADE (#2816): data.insight.scores.envelope_drivers and sensors.optimization_score.extra_state_attributes.envelope_drivers added
diff --git a/tests/golden/coord_all_features.json b/tests/golden/coord_all_features.json
index 6dec438e5..0545d231a 100644
--- a/tests/golden/coord_all_features.json
+++ b/tests/golden/coord_all_features.json
@@ -319,6 +319,7 @@
    "price_tiles": {},
    "scores": {
     "envelope": null,
+    "envelope_drivers": [],
     "machine": null,
     "operation": null,
     "overall": null,
@@ -2178,6 +2179,7 @@
   "optimization_score": {
    "extra_state_attributes": {
     "envelope": null,
+    "envelope_drivers": [],
     "machine": null,
     "operation": null,
     "overall": null,
diff --git a/tests/golden/coord_dhw.json b/tests/golden/coord_dhw.json
index bf010e0b9..84078c1fc 100644
--- a/tests/golden/coord_dhw.json
+++ b/tests/golden/coord_dhw.json
@@ -319,6 +319,7 @@
    "price_tiles": {},
    "scores": {
     "envelope": null,
+    "envelope_drivers": [],
     "machine": null,
     "operation": null,
     "overall": null,
@@ -2099,6 +2100,7 @@
   "optimization_score": {
    "extra_state_attributes": {
     "envelope": null,
+    "envelope_drivers": [],
     "machine": null,
     "operation": null,
     "overall": null,
diff --git a/tests/golden/coord_grid_fee.json b/tests/golden/coord_grid_fee.json
index 726a01cd6..74b69a15c 100644
--- a/tests/golden/coord_grid_fee.json
+++ b/tests/golden/coord_grid_fee.json
@@ -254,6 +254,7 @@
    "price_tiles": {},
    "scores": {
     "envelope": null,
+    "envelope_drivers": [],
     "machine": null,
     "operation": null,
     "overall": null,
@@ -1938,6 +1939,7 @@
   "optimization_score": {
    "extra_state_attributes": {
     "envelope": null,
+    "envelope_drivers": [],
     "machine": null,
     "operation": null,
     "overall": null,
diff --git a/tests/golden/coord_minimal.json b/tests/golden/coord_minimal.json
index 1cd74a20f..bc4938d73 100644
--- a/tests/golden/coord_minimal.json
+++ b/tests/golden/coord_minimal.json
@@ -254,6 +254,7 @@
    "price_tiles": {},
    "scores": {
     "envelope": null,
+    "envelope_drivers": [],
     "machine": null,
     "operation": null,
     "overall": null,
@@ -1938,6 +1939,7 @@
   "optimization_score": {
    "extra_state_attributes": {
     "envelope": null,
+    "envelope_drivers": [],
     "machine": null,
     "operation": null,
     "overall": null,
diff --git a/tests/golden/coord_two_zone.json b/tests/golden/coord_two_zone.json
index 19b78f7af..321cc5250 100644
--- a/tests/golden/coord_two_zone.json
+++ b/tests/golden/coord_two_zone.json
@@ -264,6 +264,7 @@
    "price_tiles": {},
    "scores": {
     "envelope": null,
+    "envelope_drivers": [],
     "machine": null,
     "operation": null,
     "overall": null,
@@ -1984,6 +1985,7 @@
   "optimization_score": {
    "extra_state_attributes": {
     "envelope": null,
+    "envelope_drivers": [],
     "machine": null,
     "operation": null,
     "overall": null,
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/envelope_score.CLAMP_DROP.85c51bc5.json b/tests/mutation_ledger/killed_by/coordinator.py/envelope_score.CLAMP_DROP.85c51bc5.json
deleted file mode 100644
index 80377a993..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/envelope_score.CLAMP_DROP.85c51bc5.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:envelope_score CLAMP_DROP 85c51bc5",
-  "killed_by": "tests/features.py",
-  "old": "    return float(np.clip(np.log(tau_h / low_h) / np.log(high_h / low_h), 0.0, 1.0)) * 100.0, None",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return float((np.log(tau_h / low_h) / np.log(high_h / low_h))) * 100.0, None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/envelope_score.RETURN_DEL.85c51bc5.json b/tests/mutation_ledger/killed_by/coordinator.py/envelope_score.RETURN_DEL.63a529d6.json
similarity index 62%
rename from tests/mutation_ledger/killed_by/coordinator.py/envelope_score.RETURN_DEL.85c51bc5.json
rename to tests/mutation_ledger/killed_by/coordinator.py/envelope_score.RETURN_DEL.63a529d6.json
index 482521919..1613b0c51 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/envelope_score.RETURN_DEL.85c51bc5.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/envelope_score.RETURN_DEL.63a529d6.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:envelope_score RETURN_DEL 85c51bc5",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:envelope_score RETURN_DEL 63a529d6",
   "killed_by": "tests/features.py",
-  "old": "    return float(np.clip(np.log(tau_h / low_h) / np.log(high_h / low_h), 0.0, 1.0)) * 100.0, None",
+  "old": "    return grade, None, drivers",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
 }
diff --git a/tests/mutation_ledger/killed_by/presets.py/@module.CONST.00acd129.json b/tests/mutation_ledger/killed_by/presets.py/@module.CONST.00acd129.json
new file mode 100644
index 000000000..e373d822f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/presets.py/@module.CONST.00acd129.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/presets.py:<module> CONST 00acd129",
+  "killed_by": "tests/features.py",
+  "old": "_GRADE_FLOOR = 1.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`_GRADE_FLOOR = 2.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/presets.py/@module.CONST.33dc5605.json b/tests/mutation_ledger/killed_by/presets.py/@module.CONST.33dc5605.json
new file mode 100644
index 000000000..8c917e315
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/presets.py/@module.CONST.33dc5605.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/presets.py:<module> CONST 33dc5605",
+  "killed_by": "tests/features.py",
+  "old": "_GRADE_SLOPE = 1.5",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`_GRADE_SLOPE = 3.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/presets.py/envelope_band_hours.RETURN_DEL.1875d362.json b/tests/mutation_ledger/killed_by/presets.py/envelope_band_hours.RETURN_DEL.1875d362.json
deleted file mode 100644
index 3a66b46e9..000000000
--- a/tests/mutation_ledger/killed_by/presets.py/envelope_band_hours.RETURN_DEL.1875d362.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/presets.py:envelope_band_hours RETURN_DEL 1875d362",
-  "killed_by": "tests/features.py",
-  "old": "    return min(taus), max(taus)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/presets.py/house_grade.CLAMP_DROP.83e9daf2.json b/tests/mutation_ledger/killed_by/presets.py/house_grade.CLAMP_DROP.83e9daf2.json
new file mode 100644
index 000000000..d1258ce18
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/presets.py/house_grade.CLAMP_DROP.83e9daf2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/presets.py:house_grade CLAMP_DROP 83e9daf2",
+  "killed_by": "tests/features.py",
+  "old": "    grade = max(100.0 / (1.0 + math.exp(_GRADE_SLOPE * total)), _GRADE_FLOOR)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`grade = (100.0 / (1.0 + math.exp(_GRADE_SLOPE * total)))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}

