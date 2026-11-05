# Review packet #3196
head: 18007245e681f4412de83458bee20fa54ae75ac7
base: 783d8dc72811ab75ae4ffca367456f44896f47d3

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arch-score / arch-score id=126914501022 queued
arm id=126907735204 skipped
budget-raise-gate / budget-raise-gate id=126914501474 queued
cancel-superseded id=126907739955 success
codeql / Analyze (actions) id=126914501328 queued
codeql / Analyze (javascript-typescript) id=126914501436 queued
codeql / Analyze (python) id=126914501360 queued
governance / delivery-status id=126914501411 queued
governance / delivery-status-publish id=126914504654 skipped
governance / env-matrix id=126914501320 queued
governance / instrument-self-tests id=126914501376 queued
governance / policy-docs id=126914501399 queued
governance / record id=126914504522 skipped
governance / wave-script id=126914501346 queued
hassfest / hassfest id=126914501622 queued
kernel-points id=126914503703 skipped
prelude id=126907740417 success
refresh id=126907740621 success
tests / briefs id=126914501248 queued
tests / closure-scope id=126914501490 queued
tests / mutation id=126914501201 queued
tests / nightly-status id=126914501601 queued
validate / validate-hacs id=126914501456 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         tools/audit/seat/cloud-setup.sh --check
             `tools/audit/seat/cloud-setup.sh` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_two_zone_hhl_inert.py
             `dev/audit/harnesses/r10_two_zone_hhl_inert.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/env_drift.py --all origin/main
             `tests/env_drift.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff origin/main
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main
             `tools/pr/ci_predict.py` is in the tree at this head

FIGURES: 8 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_single_zone.RETURN_DEL.6de1e154.json b/tests/mutation_ledger/killed_by/config_flow.py/_single_zone.RETURN_DEL.6de1e154.json
new file mode 100644
index 000000000..9eded8dfb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_single_zone.RETURN_DEL.6de1e154.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_single_zone RETURN_DEL 6de1e154",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    return not ThermalParameters.from_config(config).two_zone_enabled",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=2."
+}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/config_flow.py b/custom_components/heatpump_optimizer/config_flow.py
index f5d8ab932..acde818bf 100644
--- a/custom_components/heatpump_optimizer/config_flow.py
+++ b/custom_components/heatpump_optimizer/config_flow.py
@@ -1558,6 +1558,19 @@ _OPTION_PAGES: Final[tuple[_P, ...]] = (
     _P("factory_reset", "Reset to factory defaults", _ADVANCED),
 )
 
+
+def _single_zone(config: Mapping[str, Any]) -> bool:
+    """Whether the model runs one zone, the only one reading the whole-house loss.
+
+    On two zones every reader takes the zones' loss instead
+    (``ThermalParameters.house_heat_loss_base``, ``sysid.HousePlant.of_params``),
+    so the thermal page does not offer the whole-house figure there
+    (R10-TWO-ZONE-HHL). The model's own resolution of the mode, so an "auto"
+    entry follows the zone keys exactly as the solve does.
+    """
+    return not ThermalParameters.from_config(config).two_zone_enabled
+
+
 #: Every field the options flow presents, in the order each page renders them.
 _OPTION_FIELDS: Final[tuple[_F, ...]] = (
     # -- entities
@@ -1700,7 +1713,7 @@ _OPTION_FIELDS: Final[tuple[_F, ...]] = (
     _F("building", CONF_SPACE_PUMP_ENTITY, _STORED, _entity_of(['switch', 'input_boolean']), group="circulation"),
     # -- thermal_model
     _F("thermal_model", CONF_HOUSE_THERMAL_MASS, _SUGGESTED, _number(*RANGE_HOUSE_THERMAL_MASS, 0.5, 'kWh/°C')),
-    _F("thermal_model", CONF_HOUSE_HEAT_LOSS_COEFFICIENT, _SUGGESTED, _number(*RANGE_HOUSE_HEAT_LOSS, 0.01, 'kW/°C')),
+    _F("thermal_model", CONF_HOUSE_HEAT_LOSS_COEFFICIENT, _SUGGESTED, _number(*RANGE_HOUSE_HEAT_LOSS, 0.01, 'kW/°C'), when=_single_zone),
     _F("thermal_model", CONF_SLAB_THERMAL_MASS, _SUGGESTED, _number(*RANGE_SLAB_THERMAL_MASS, 0.5, 'kWh/°C')),
     _F("thermal_model", CONF_SLAB_HEAT_TRANSFER, _SUGGESTED, _number(*RANGE_SLAB_HEAT_TRANSFER, 0.1, 'kW/°C')),
     _F("thermal_model", CONF_HEAT_PUMP_COP_NOMINAL, _SUGGESTED, _number(1.5, 6.0, 0.1)),
diff --git a/custom_components/heatpump_optimizer/sysid.py b/custom_components/heatpump_optimizer/sysid.py
index 353677cdc..6f1bee8b2 100644
--- a/custom_components/heatpump_optimizer/sysid.py
+++ b/custom_components/heatpump_optimizer/sysid.py
@@ -354,10 +354,20 @@ class HousePlant:
     def of_params(cls, p: ThermalParameters) -> "HousePlant":
         """The coordinator's configured plant: the learned heat-loss scale
         folded into ``ua``, and the slab pair the sizing needs (#943). One
-        construction, so the wiring cannot drop a field."""
+        construction, so the wiring cannot drop a field.
+
+        On two zones the house is the zones (R10-TWO-ZONE-HHL): ``ua`` is
+        their loss as the dynamics use it (``house_heat_loss_base``) and
+        ``capacity`` their mass, as :meth:`SystemIdentification.arm` seeds the
+        fit -- the whole-house figures are a single-zone model's, which a
+        two-zone install neither runs nor is offered."""
+        two_zone = p.two_zone_enabled
         return cls(
-            ua=p.heat_loss_coefficient * p.house_heat_loss_scale,
-            capacity=p.room_thermal_mass,
+            ua=p.house_heat_loss_base * p.house_heat_loss_scale,
+            capacity=(
+                p.upper_floor_thermal_mass + p.lower_floor_thermal_mass
+                if two_zone else p.room_thermal_mass
+            ),
             gains=p.internal_gains,
             slab_mass=p.slab_thermal_mass,
             slab_transfer=p.slab_heat_transfer,
diff --git a/dev/audit/harnesses/r10_two_zone_hhl_inert.py b/dev/audit/harnesses/r10_two_zone_hhl_inert.py
index 9cad89b70..2cf788cd7 100644
--- a/dev/audit/harnesses/r10_two_zone_hhl_inert.py
+++ b/dev/audit/harnesses/r10_two_zone_hhl_inert.py
@@ -10,10 +10,13 @@ probe's owner-like two-zone config through two production paths:
 
 * the solve -- ``OptimizationConfig.from_mapping`` ->
   ``ThermalParameters.from_config`` -> ``HeatPumpOptimizer.optimize``;
-* system identification's step sizer -- ``HousePlant.of_params`` ->
-  ``SystemIdentification._size_step_power``, the call the coordinator's
-  sysid tick makes, which reads ``heat_loss_coefficient`` with no two-zone
-  branch.
+* system identification's step sizer -- ``SystemIdentification.arm`` with
+  the plant (which hands a two-zone plant to the sizer, as
+  ``arm_from_config`` does) -> ``HousePlant.of_params`` ->
+  ``SystemIdentification._size_step_power``, the calls the coordinator's
+  sysid arm and tick make. R10-TWO-ZONE-HHL: the first cut of this harness
+  skipped ``arm`` and so measured the single-zone sizing path in two-zone
+  mode; the armed sizer already sized on the zones (#1524).
 
 The null control for both is the same sweep in single-zone mode, where the
 coefficient must move each output (a harness that reads zero there is blind).
@@ -25,6 +28,11 @@ until then the UI must keep offering it.
   single_zone_max_dkw    the solve's null control, must be > 0
   two_zone_sysid_steps   the sysid step sizes across the sweep, kW (``None``:
                          no step fits); one distinct value means inert
+  two_zone_heavy_sysid_steps  the same on zones heavy enough for a step to
+                         fit (``HEAVY``), so one distinct value is not a
+                         uniform ``None``
+  two_zone_plant         the distinct (ua, capacity) ``HousePlant.of_params``
+                         hands the sizer across the sweep; one means inert
   single_zone_sysid_steps  the sizer's null control
 
     PYTHONPATH=tests/hastub:custom_components:tests \\
@@ -38,7 +46,7 @@ import numpy as np
 
 from heatpump_optimizer import const as C
 from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
-from heatpump_optimizer.sysid import HousePlant, SystemIdentification
+from heatpump_optimizer.sysid import HousePlant, SysIdConfig, SystemIdentification
 from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
 from profiles import solve_inputs
 
@@ -57,6 +65,8 @@ CFG = {
     "slab_thermal_mass": 1.0, "slab_heat_transfer": 1.5,
 }
 SWEEP = (0.1, 0.4, 1.0)
+HEAVY = {"upper_floor_thermal_mass": 4.0, "lower_floor_thermal_mass": 4.0}
+ARM_AT = datetime(2026, 11, 1, 1, 0)
 
 
 def _solve(mode: str, hhl: float) -> tuple[np.ndarray, float]:
@@ -70,18 +80,27 @@ def _solve(mode: str, hhl: float) -> tuple[np.ndarray, float]:
     return np.asarray(result.power_schedule, float), float(result.predicted_cost)
 
 
-def _sysid_steps(mode: str) -> list[float | None]:
+def _params(mode: str, hhl: float, extra: dict | None = None) -> ThermalParameters:
+    return ThermalParameters.from_config(
+        {**CFG, **(extra or {}), C.CONF_TWO_ZONE_MODE: mode, C.CONF_HOUSE_HEAT_LOSS_COEFFICIENT: hhl})
+
+
+def _sysid_steps(mode: str, extra: dict | None = None) -> list[float | None]:
     steps = []
     for hhl in SWEEP:
-        params = ThermalParameters.from_config(
-            {**CFG, C.CONF_TWO_ZONE_MODE: mode, C.CONF_HOUSE_HEAT_LOSS_COEFFICIENT: hhl})
-        plant = HousePlant.of_params(params)
-        kw = SystemIdentification()._size_step_power(
-            5.0, 3.0, 20.0, 5.0, plant.ua, plant.capacity, plant.gains, plant.slab_mass, plant.slab_transfer)
-        steps.append(None if kw is None else round(kw, 3))
+        params = _params(mode, hhl, extra)
+        ident = SystemIdentification(SysIdConfig(enabled=True))
+        if not ident.arm(ARM_AT, plant=params):
+            raise SystemExit(f"not armed: {ident.result}")
+        kw = ident._size_step_power(5.0, 3.0, 20.0, 5.0, HousePlant.of_params(params))
+        steps.append(None if kw is None else round(float(kw), 3))
     return steps
 
 
+def _plants(mode: str) -> set[tuple[float | None, float | None]]:
+    return {(p.ua, p.capacity) for p in (HousePlant.of_params(_params(mode, h)) for h in SWEEP)}
+
+
 def _spread(mode: str) -> tuple[float, float]:
     runs = [_solve(mode, hhl) for hhl in SWEEP]
     dkw = max(float(np.max(np.abs(p - runs[0][0]))) for p, _ in runs)
@@ -96,4 +115,6 @@ if __name__ == "__main__":
     print(f"RESULT two_zone_max_dcost={two_dcost:.6f}")
     print(f"RESULT single_zone_max_dkw={one_dkw:.6f}")
     print(f"RESULT two_zone_sysid_steps={','.join(map(str, _sysid_steps(C.TWO_ZONE_MODE_ON)))}")
+    print(f"RESULT two_zone_heavy_sysid_steps={','.join(map(str, _sysid_steps(C.TWO_ZONE_MODE_ON, HEAVY)))}")
+    print(f"RESULT two_zone_plant={sorted(_plants(C.TWO_ZONE_MODE_ON))}")
     print(f"RESULT single_zone_sysid_steps={','.join(map(str, _sysid_steps(C.TWO_ZONE_MODE_OFF)))}")
diff --git a/dev/programme/delivery/3196.md b/dev/programme/delivery/3196.md
new file mode 100644
index 000000000..7900c821b
--- /dev/null
+++ b/dev/programme/delivery/3196.md
@@ -0,0 +1 @@
+- [#3196](https://github.com/tvofi/heatpump_optimizer/pull/3196) — **open**, R10-TWO-ZONE-HHL: two zone hhl (R10-TWO-ZONE-HHL)
diff --git a/tests/config_flow_steps.py b/tests/config_flow_steps.py
index 6b0b58a37..df8f9f0bb 100644
--- a/tests/config_flow_steps.py
+++ b/tests/config_flow_steps.py
@@ -2186,6 +2186,45 @@ async def options_advanced_pages():
         f"options={entry.options.get(const.CONF_MIXING_VALVE_WRITE_TARGET_KIND)!r}",
     )
 
+    # R10-TWO-ZONE-HHL: on a two-zone house every reader of the whole-house
+    # heat loss takes the zones' loss instead, so the thermal page does not
+    # offer it as a setting there. Null control: single zone still shows it.
+    flow, entry, _ = fresh_options(
+        pre_options={const.CONF_TWO_ZONE_MODE: const.TWO_ZONE_MODE_ON}
+    )
+    two_zone_keys = schema_keys(await flow.async_step_thermal_model(None))
+    flow, entry, _ = fresh_options(
+        pre_options={const.CONF_TWO_ZONE_MODE: const.TWO_ZONE_MODE_OFF}
+    )
+    one_zone_keys = schema_keys(await flow.async_step_thermal_model(None))
+    check(
+        "opt_thermal_model",
+        "happy",
+        "a two-zone entry is not offered the whole-house heat loss; a "
+        "single-zone one is (R10-TWO-ZONE-HHL)",
+        const.CONF_HOUSE_HEAT_LOSS_COEFFICIENT not in two_zone_keys
+        and const.CONF_HOUSE_HEAT_LOSS_COEFFICIENT in one_zone_keys
+        and const.CONF_HOUSE_THERMAL_MASS in two_zone_keys,
+        f"two={sorted(two_zone_keys)} one={sorted(one_zone_keys)}",
+    )
+    # Hidden, not cleared: a two-zone save keeps the stored figure, so an
+    # entry switched back to one zone finds its own value again.
+    flow, entry, _ = fresh_options(pre_options={
+        const.CONF_TWO_ZONE_MODE: const.TWO_ZONE_MODE_ON,
+        const.CONF_HOUSE_HEAT_LOSS_COEFFICIENT: 0.31,
+    })
+    await flow.async_step_thermal_model(None)
+    await submit(flow, "thermal_model", {const.CONF_HOUSE_THERMAL_MASS: 12.0})
+    check(
+        "opt_thermal_model",
+        "happy",
+        "a two-zone thermal-page save keeps the hidden whole-house heat loss "
+        "(R10-TWO-ZONE-HHL)",
+        entry.options.get(const.CONF_HOUSE_HEAT_LOSS_COEFFICIENT) == 0.31
+        and entry.options.get(const.CONF_HOUSE_THERMAL_MASS) == 12.0,
+        f"options={dict(entry.options)}",
+    )
+
     # #1067: pricing the curve lift is for a direct plant. Behind a
     # throttling valve the tank temperature already is the priced flow, so
     # the page refuses the pair rather than saving a switch that does nothing.
diff --git a/tests/entities.py b/tests/entities.py
index d87040eba..0f09376cb 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -9526,8 +9526,16 @@ for _case in _matrix(_EXTREME_AREAS, (0.1, 0.5, 0.9)):
     except Exception as err:  # noqa: BLE001 - any rejection is the bug
         _unsubmittable.append(f"{_case}: {type(err).__name__}: {err}")
         continue
+    # A row its ``when`` hides for this house is not on the page to submit
+    # (R10-TWO-ZONE-HHL: the whole-house heat loss on two zones); keyed on
+    # the registry's own predicate, so only a row the page hides is skipped.
+    _hidden = {
+        row.key for row in config_flow._OPTION_FIELDS
+        if row.step in ("thermal_model", "thermal_model_zones")
+        and row.when is not None and not row.when(_stored)
+    }
     for _key, _value in _stored.items():
-        if _accepted.get(_key) != _value:
+        if _key not in _hidden and _accepted.get(_key) != _value:
             _unsubmittable.append(
                 f"{_case}: {_key} came back {_accepted.get(_key)!r}, stored {_value!r}"
             )
diff --git a/tests/features.py b/tests/features.py
index 27a67b98a..88a0f5d87 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -76834,6 +76834,40 @@ R.check(
 )
 
 
+# R10-TWO-ZONE-HHL: the plant system identification sizes its step on is the
+# zone model it is given. On two zones that is the zones' loss and mass, so the
+# whole-house coefficient the options flow hides there moves nothing.
+from heatpump_optimizer import const as _tzh_const  # noqa: E402
+from heatpump_optimizer.thermal_model import ThermalParameters as _tzh_tp  # noqa: E402
+
+
+def _tzh_plant(mode: str, hhl: float) -> HousePlant:
+    return HousePlant.of_params(_tzh_tp.from_config({
+        _tzh_const.CONF_TWO_ZONE_MODE: mode, _tzh_const.CONF_HOUSE_HEAT_LOSS_COEFFICIENT: hhl,
+        _tzh_const.CONF_HOUSE_THERMAL_MASS: 10.0,
+        _tzh_const.CONF_UPPER_FLOOR_HEAT_LOSS: 0.13, _tzh_const.CONF_LOWER_FLOOR_HEAT_LOSS: 0.2,
+        _tzh_const.CONF_UPPER_FLOOR_THERMAL_MASS: 1.26, _tzh_const.CONF_LOWER_FLOOR_THERMAL_MASS: 1.0,
+    }))
+
+
+_tzh_two = {_tzh_plant(_tzh_const.TWO_ZONE_MODE_ON, hhl) for hhl in (0.1, 0.4, 1.0)}
+_tzh_one = {_tzh_plant(_tzh_const.TWO_ZONE_MODE_OFF, hhl).ua for hhl in (0.1, 0.4, 1.0)}
+R.check(
+    "R10-TWO-ZONE-HHL a two-zone HousePlant is the zones' loss and mass, "
+    "whatever the whole-house coefficient",
+    len(_tzh_two) == 1
+    and abs(next(iter(_tzh_two)).ua - 0.33) < 1e-9
+    and abs(next(iter(_tzh_two)).capacity - 2.26) < 1e-9,
+    str(_tzh_two),
+)
+R.check(
+    "R10-TWO-ZONE-HHL null control: a single-zone HousePlant still follows "
+    "the whole-house coefficient",
+    len(_tzh_one) == 3,
+    str(_tzh_one),
+)
+
+
 R.section("R10-PROD-RESIDUE-PINS: one plan step width in the arbiter; shutdown re-arms the hass latches")
 
 # #2365: _share and the decision log take the step width from plan_step's
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_single_zone.RETURN_DEL.6de1e154.json b/tests/mutation_ledger/killed_by/config_flow.py/_single_zone.RETURN_DEL.6de1e154.json
new file mode 100644
index 000000000..9eded8dfb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_single_zone.RETURN_DEL.6de1e154.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_single_zone RETURN_DEL 6de1e154",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    return not ThermalParameters.from_config(config).two_zone_enabled",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=2."
+}

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
