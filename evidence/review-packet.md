# Review packet #3268
head: d95f6b7a88e6c2d960ee897b915d4c7941b45de9
base: 80016a71f567d936450d8708abcbb79d9e8071d7

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=128234114468 neutral
arch-score / arch-score id=128233933163 success
arm id=128233741029 skipped
budget-raise-gate / budget-raise-gate id=128233933328 success
cancel-superseded id=128233744353 success
codeql id=128233935245 skipped
codeql / Analyze (actions) id=128233877361 success
codeql / Analyze (javascript-typescript) id=128233877334 success
codeql / Analyze (python) id=128233877346 in_progress
gate id=128234307691 failure
governance id=128233935531 skipped
governance / delivery-status id=128233877599 success
governance / delivery-status-publish id=128233878828 skipped
governance / env-matrix id=128233877705 success
governance / instrument-self-tests id=128233877434 in_progress
governance / policy-docs id=128233877595 success
governance / record id=128233879047 skipped
governance / wave-script id=128233877456 success
hassfest id=128233934999 skipped
hassfest / hassfest id=128233877648 success
kernel-points id=128233935467 skipped
pr-contract id=128234308517 skipped
prelude id=128233744826 success
refresh id=128233744708 success
tests id=128233935483 skipped
tests / arch-instrument id=128234057344 success
tests / briefs id=128233877377 success
tests / browser id=128234057115 success
tests / closure-scope id=128233877429 success
tests / closures id=128234057317 in_progress
tests / coverage id=128234057084 in_progress
tests / fast (3.14) id=128234057110 in_progress
tests / mutation id=128233877269 failure
tests / mutation-pins (1) id=128234121079 in_progress
tests / nightly-ha id=128234059384 skipped
tests / nightly-status id=128233877452 success
tests / replay id=128234057254 in_progress
tests / typing id=128234057182 success
validate id=128233935292 skipped
validate / validate-hacs id=128233877636 success

## Refusals
red-unanswered: concluded red check `gate` is not named in ## Red checks
red-unanswered: concluded red check `tests / mutation` is not named in ## Red checks
required-red: required context `gate` concluded failure at d95f6b7a88e6c2d960ee897b915d4c7941b45de9

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         dev/audit/harnesses/r10_combi_tank.py
             `dev/audit/harnesses/r10_combi_tank.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_combi_tank.py all
             `dev/audit/harnesses/r10_combi_tank.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  unverified git grep -n "_open_loop_plan_value(\|_seed_store(" -- custom_components
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -n "ExternalHeatObservation(" -- custom_components
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 5 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._update_current_state.GUARD_OFF.12569471.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._update_current_state.GUARD_OFF.12569471.json
deleted file mode 100644
index db5ad4875..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._update_current_state.GUARD_OFF.12569471.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._update_current_state GUARD_OFF 12569471",
-  "killed_by": "tests/entities.py",
-  "old": "        if buffer_reading.ok:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
-}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index 09c3beb21..b162e2aa2 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -198,6 +198,7 @@ from .inputs import (
     UNBOUNDED,
     InputHealth,
     InputReader,
+    InputReading,
     age_of,
     normalize_price_per_kwh,
     parse_bool,
@@ -2341,6 +2342,22 @@ def _open_loop_plan_value(
     return None if index is None else float(trajectory[index])
 
 
+def _seed_store(
+    reading: InputReading,
+    result: OptimizationResult | None,
+    trajectory_attr: str,
+    now: datetime,
+) -> float | None:
+    """A tank's level for this cycle: the probe, else the plan's own estimate.
+
+    One seed path for every store (R10-BUFFER-OPENLOOP, D12-s1-01): an ok
+    reading wins; without one the previous plan's ``trajectory_attr`` at the
+    step covering ``now``; ``None`` when neither exists, and the caller then
+    leaves its field as it is rather than fabricate a level.
+    """
+    return reading.value if reading.ok else _open_loop_plan_value(result, trajectory_attr, now)
+
+
 def _diagnose_payload(coord: "HeatPumpOptimizerCoordinator") -> tuple[Any, ...]:
     """Picklable diagnose args; the coordinator itself is not picklable."""
     record = coord._last_interval_record
@@ -5023,10 +5040,15 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         outlet = reader.read(CONF_VALVE_OUTLET_TEMP_ENTITY)
         wood_top = reader.read(CONF_WOOD_TANK_TOP_ENTITY)
         wood_bottom = reader.read(CONF_WOOD_TANK_BOTTOM_ENTITY)
+        # The rise inputs take the probes alone: the published levels may be
+        # the plan's own open-loop seed, whose planned rise is no evidence of
+        # outside heat. ``hp_tank_temp`` is a level, so it keeps the estimate.
+        dhw = reader.read(CONF_DHW_TEMP_ENTITY)
+        buffer = reader.read(CONF_BUFFER_TANK_TEMP_ENTITY)
         observation = ExternalHeatObservation(
             now=dt_util.now(),
-            dhw_temp=ctx._current_state.dhw_temperature,
-            buffer_temp=ctx._current_state.buffer_tank_temperature,
+            dhw_temp=dhw.value if dhw.ok else None,
+            buffer_temp=buffer.value if buffer.ok else None,
             commanded_power_kw=self._commanded_power(),
             measured_power_kw=self._measured_power,
             dhw_max_rise_c_per_h=self._max_pump_rise("dhw"),
@@ -6547,25 +6569,19 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
                 self._solar_radiation = observed
                 state.solar_radiation = observed
 
-        # DHW temperature sensor. Without an ok reading the tank is seeded
-        # from the previous plan's own trajectory (open-loop propagation,
-        # R9 D12-s1-01); the 55 °C dataclass default reached every solve
-        # otherwise, so every plan believed the tank was just charged.
+        # The tank levels. Without an ok reading each tank is seeded from the
+        # previous plan's own trajectory (open-loop propagation, D12-s1-01):
+        # a never-advanced default (55 °C DHW, 40 °C buffer) reached every
+        # solve otherwise. No reading and no plan leaves the field as it is.
         dhw = reader.read(CONF_DHW_TEMP_ENTITY)
+        buffer_reading = reader.read(CONF_BUFFER_TANK_TEMP_ENTITY)
+        plan, seeded_at = self._optimization_result, dt_util.now()
         if dhw.ok:
             self._dhw_temperature = dhw.value
-            state.dhw_temperature = self._dhw_temperature
-        elif (
-            seed := _open_loop_plan_value(
-                self._optimization_result, "dhw_temp_trajectory", dt_util.now()
-            )
-        ) is not None:
-            state.dhw_temperature = seed
-
-        # Buffer tank temperature sensor (optional; enables cooling learning)
-        buffer_reading = reader.read(CONF_BUFFER_TANK_TEMP_ENTITY)
-        if buffer_reading.ok:
-            state.buffer_tank_temperature = buffer_reading.value
+        if (level := _seed_store(dhw, plan, "dhw_temp_trajectory", seeded_at)) is not None:
+            state.dhw_temperature = level
+        if (level := _seed_store(buffer_reading, plan, "buffer_temp_trajectory", seeded_at)) is not None:
+            state.buffer_tank_temperature = level
 
         # Wood tank temperature (issue #40): re-read from the physical tank
         # each cycle through the same stale-aware reader — the model never
diff --git a/dev/audit/harnesses/r10_combi_tank.py b/dev/audit/harnesses/r10_combi_tank.py
new file mode 100644
index 000000000..47deb5d88
--- /dev/null
+++ b/dev/audit/harnesses/r10_combi_tank.py
@@ -0,0 +1,196 @@
+"""R10-COMBI-TANK: the combi-tank group's harness; PR 0 (R10-BUFFER-OPENLOOP) arms.
+
+    PYTHONPATH=tests/hastub:custom_components:tests \\
+        python3 dev/audit/harnesses/r10_combi_tank.py [no_probe|wood_seed|solve|all]
+
+Synthetic installs only; no private data. Every arm drives the production
+``HeatPumpOptimizerCoordinator._update_current_state`` (which runs the
+external-heat detection) and reads the published state and the detector's
+observation; run it at the merge base and at the head to read the defect
+(D12-s1-01: the no-probe buffer is never advanced) at one end only.
+
+``no_probe``: a 500 L buffer behind a manual (throttling) valve and no buffer
+probe; a prior plan whose ``buffer_temp_trajectory`` moves 40 -> 47 degC in
+15-minute steps; two cycles at +20 and +50 minutes (covering steps 1 and 3).
+Printed per arm: the buffer level after each cycle and the observation's rise
+inputs (buffer_temp, dhw_temp). Arms: ``seed`` (no probe), ``probe`` (a probe
+reading 36.5 degC: the reading must win, the null control), ``empty`` (an
+empty trajectory, which is what a plan without a throttling valve publishes:
+the level must stay where it was, never fabricated).
+
+``wood_seed``: the same install plus a wood furnace (wood tank top 70, bottom
+60, valve outlet 55 degC, 1000 L, stove override on so the detector is
+active). The throttling valve is what makes the plan publish a buffer
+trajectory (optimizer.py, ``buffer_temp_trajectory``); without it this arm
+collapses into its own ``empty`` control. Printed: ``hp_tank_temp`` per
+cycle, and the detector's ``wood_energy_kwh`` and ``displacement``. Arms
+``seed``, ``probe`` (38 degC) and ``empty``.
+
+``solve``: four hourly ``async_refresh`` cycles with the real solver, no buffer
+probe, a 500 L buffer, valve ``manual`` against valve ``none``. Printed: the
+buffer level each solve started from, and whether the previous plan
+published a buffer trajectory. Under ``none`` the plan publishes none, so the
+level is never fabricated.
+
+RESULT lines are printed for the head; at the merge base ``no_probe_seed``
+reads 40.0,40.0 and ``wood_seed_hp`` reads 40.0,40.0.
+
+EXPECTED RESULT no_probe_seed=41.0,43.0
+EXPECTED RESULT no_probe_probe=36.5,36.5
+EXPECTED RESULT no_probe_empty=40.0,40.0
+EXPECTED RESULT no_probe_rise=None,None
+EXPECTED RESULT wood_seed_hp=41.0,43.0
+EXPECTED RESULT wood_seed_probe_hp=38.0,38.0
+EXPECTED RESULT wood_seed_empty_hp=40.0,40.0
+"""
+from __future__ import annotations
+
+import asyncio
+import sys
+from datetime import datetime, timedelta, timezone
+from types import SimpleNamespace
+
+from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
+from homeassistant.util import dt as dt_util  # noqa: E402
+
+from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
+
+T0 = datetime(2026, 3, 2, 6, 0, tzinfo=timezone.utc)
+TRAJ = [40.0 + i for i in range(8)]
+AT = (T0 + timedelta(minutes=20), T0 + timedelta(minutes=50))
+BASE_CFG = {
+    "tibber_token": "x",
+    "weather_entity": "weather.home",
+    "indoor_temp_entity": "sensor.indoor",
+    "outdoor_temp_entity": "sensor.outdoor",
+    "buffer_tank_volume": 500.0,
+    "dhw_tank_volume": 200.0,
+    "mixing_valve_mode": "manual",
+}
+WOOD_CFG = {
+    "wood_furnace_enabled": True,
+    "external_heat_detection_enabled": True,
+    "external_heat_entity": "input_boolean.stove",
+    "wood_tank_top_entity": "sensor.wood_top",
+    "wood_tank_bottom_entity": "sensor.wood_bottom",
+    "valve_outlet_temp_entity": "sensor.outlet",
+    "wood_tank_volume": 1000.0,
+}
+
+
+def _fmt(values):
+    return ",".join("None" if v is None else f"{v:.1f}" for v in values)
+
+
+def cycles(*, probe=None, trajectory=TRAJ, wood=False):
+    """Two ``_update_current_state`` cycles over an injected prior plan."""
+    cfg = dict(BASE_CFG)
+    if probe is not None:
+        cfg["buffer_tank_temp_entity"] = "sensor.buffer"
+    if wood:
+        cfg.update(WOOD_CFG)
+    coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
+    coord._snapshots_loaded = True
+    coord._optimization_result = SimpleNamespace(
+        buffer_temp_trajectory=list(trajectory),
+        dhw_temp_trajectory=[],
+        timestamps=[T0 + timedelta(minutes=15 * i) for i in range(8)],
+    )
+    seen = []
+    real = coord._external_heat.update
+    coord._external_heat.update = lambda obs: (seen.append(obs), real(obs))[1]
+    levels = []
+    try:
+        for now in AT:
+            dt_util.freeze(now)
+            states = [("sensor.indoor", "21.0"), ("sensor.outdoor", "5.0")]
+            if probe is not None:
+                states.append(("sensor.buffer", f"{probe}"))
+            if wood:
+                states += [("sensor.wood_top", "70.0"), ("sensor.wood_bottom", "60.0"),
+                           ("sensor.outlet", "55.0")]
+                coord.hass.states.set("input_boolean.stove", FakeState("on", last_updated=now))
+            for entity, value in states:
+                coord.hass.states.set(entity, FakeState(value, last_updated=now, unit="°C"))
+            asyncio.run(coord._update_current_state())
+            levels.append(getattr(coord, "_ctx", coord)._current_state.buffer_tank_temperature)
+    finally:
+        dt_util.freeze(None)
+    return levels, seen, coord._external_heat.state
+
+
+def arm_no_probe() -> None:
+    for name, kw in (("seed", {}), ("probe", {"probe": 36.5}), ("empty", {"trajectory": ()})):
+        levels, seen, _ = cycles(**kw)
+        rise = [(o.buffer_temp, o.dhw_temp) for o in seen]
+        print(f"no_probe {name:5}: buffer levels {_fmt(levels)}  rise inputs {rise}")
+        print(f"RESULT no_probe_{name}={_fmt(levels)}")
+        if name == "seed":
+            print(f"RESULT no_probe_rise={_fmt(o.buffer_temp for o in seen)}")
+
+
+def arm_wood_seed() -> None:
+    for name, kw in (("seed", {}), ("probe", {"probe": 38.0}), ("empty", {"trajectory": ()})):
+        _, seen, st = cycles(wood=True, **kw)
+        hp = [o.hp_tank_temp for o in seen]
+        energy = "None" if st.wood_energy_kwh is None else f"{st.wood_energy_kwh:.4f}"
+        print(f"wood_seed {name:5}: hp_tank_temp {_fmt(hp)}  wood_energy_kwh {energy}"
+              f"  displacement {st.displacement:.4f}")
+        key = "wood_seed_hp" if name == "seed" else f"wood_seed_{name}_hp"
+        print(f"RESULT {key}={_fmt(hp)}")
+
+
+def _prices(hass, now):
+    now = now.replace(minute=0, second=0, microsecond=0)
+    hass.states.set("sensor.prices", FakeState("0.5", attributes={"raw_today": [
+        {"start": (now + timedelta(hours=h)).isoformat(), "value": round(0.5 + 0.1 * (h % 4), 3)}
+        for h in range(48)]}))
+
+
+def arm_solve() -> None:
+    import heatpump_optimizer as integ
+
+    for valve in ("manual", "none"):
+        cfg = {k: v for k, v in BASE_CFG.items() if k != "tibber_token"}
+        cfg.update({"price_source": "entity", "price_entity": "sensor.prices",
+                    "mixing_valve_mode": valve, "dhw_enabled": False})
+        dt_util.freeze(T0)
+        hass = FakeHass()
+        hass.states.set("sensor.indoor", FakeState("21.0", unit="°C"))
+        hass.states.set("sensor.outdoor", FakeState("-3.0", unit="°C"))
+        _prices(hass, T0)
+        entry = FakeEntry(data=cfg, entry_id=f"r10ct_solve_{valve}")
+        seeds, published = [], []
+        try:
+            asyncio.run(integ.async_setup_entry(hass, entry))
+            coord = entry.runtime_data
+            real = coord._solve_record
+
+            def snap(*a, **k):
+                record = real(*a, **k)
+                seeds.append(record.inputs.state.buffer_tank_temperature)
+                return record
+
+            coord._solve_record = snap
+            for hour in range(4):
+                published.append(bool(getattr(coord._optimization_result, "buffer_temp_trajectory", None)))
+                dt_util.freeze(T0 + timedelta(hours=hour))
+                _prices(hass, T0 + timedelta(hours=hour))
+                asyncio.run(coord.async_refresh())
+        finally:
+            dt_util.freeze(None)
+        print(f"solve valve={valve:6}: solver buffer seeds {_fmt(seeds)}  "
+              f"previous plan published a buffer trajectory {published}")
+
+
+def main(argv: list[str]) -> int:
+    which = argv[1] if len(argv) > 1 else "all"
+    arms = {"no_probe": arm_no_probe, "wood_seed": arm_wood_seed, "solve": arm_solve}
+    for name, fn in arms.items():
+        if which in (name, "all"):
+            fn()
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv))
diff --git a/dev/programme/delivery/3268.md b/dev/programme/delivery/3268.md
new file mode 100644
index 000000000..faf34e8aa
--- /dev/null
+++ b/dev/programme/delivery/3268.md
@@ -0,0 +1 @@
+- [#3268](https://github.com/tvofi/heatpump_optimizer/pull/3268) — **open**, R10-COMBI-TANK (PR 0, buffer open-loop): R10-BUFFER-OPENLOOP (R10-COMBI-TANK PR 0, S; design `a605014bff4478f470853109060f4ff7ef605 (R10-COMBI-TANK)
diff --git a/tests/closures.json b/tests/closures.json
index c71959796..7a265992c 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3996,6 +3996,7 @@
    "dev/audit/harnesses/r10_cloud_setup_mutants.py",
    "dev/audit/harnesses/r10_cloud_setup_toolchain.py",
    "dev/audit/harnesses/r10_codescan_wait_race.py",
+   "dev/audit/harnesses/r10_combi_tank.py",
    "dev/audit/harnesses/r10_configflow_pages.py",
    "dev/audit/harnesses/r10_cop_conversions.py",
    "dev/audit/harnesses/r10_cop_gate.py",
diff --git a/tests/features.py b/tests/features.py
index 22bb32fca..d85c4f8a4 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -2010,6 +2010,181 @@ R.check(
     "the 55 degC default must not be replaced by a plan that has not started",
 )
 
+# --- R10-BUFFER-OPENLOOP (D12-s1-01): the no-probe buffer is advanced ------
+# Without a buffer probe ``state.buffer_tank_temperature`` kept the 40 degC
+# dataclass default (or its last value) cycle after cycle, and every solve
+# started the buffer from it. The fix seeds it from the previous plan's
+# ``buffer_temp_trajectory`` at the step covering now, through the same
+# ``_seed_store`` primitive the DHW seed now uses. Each arm drives the
+# production ``_update_current_state`` (which calls the external-heat
+# detection) and reads the published state and the detector's observation.
+R.section("R10-BUFFER-OPENLOOP: the no-probe buffer follows the previous plan")
+from heatpump_optimizer import external_heat as _r10bo_eh  # noqa: E402
+from heatpump_optimizer.coordinator import (  # noqa: E402
+    HeatPumpOptimizerCoordinator as _r10bo_Coord,
+)
+
+_r10bo_t0 = datetime(2026, 3, 2, 6, 0, tzinfo=UTC)
+#: Planned buffer 40 -> 47 degC over eight 15-minute steps: cycles at +20 and
+#: +50 minutes are covered by steps 1 and 3 (41.0 and 43.0).
+_r10bo_traj = [40.0 + i for i in range(8)]
+_r10bo_at = (_r10bo_t0 + timedelta(minutes=20), _r10bo_t0 + timedelta(minutes=50))
+
+
+def _r10bo_run(*, probe=None, dhw_probe=None, trajectory=_r10bo_traj, wood=False,
+               dhw_trajectory=()):
+    """Two cycles; returns ([buffer level per cycle], [dhw level], [observation])."""
+    cfg = {
+        "tibber_token": "x",
+        "weather_entity": "weather.home",
+        "indoor_temp_entity": "sensor.indoor",
+        "outdoor_temp_entity": "sensor.outdoor",
+        "buffer_tank_volume": 500.0,
+        "dhw_tank_volume": 200.0,
+        # The plan publishes a buffer trajectory only under a throttling valve
+        # (optimizer.py, ``buffer_temp_trajectory``); the injected plan below
+        # stands for that plan, so the valve is configured to match it.
+        "mixing_valve_mode": "manual",
+    }
+    if probe is not None:
+        cfg["buffer_tank_temp_entity"] = "sensor.buffer"
+    if dhw_probe is not None:
+        cfg["dhw_temp_entity"] = "sensor.tank"
+    if wood:
+        cfg.update({
+            "wood_furnace_enabled": True,
+            "external_heat_detection_enabled": True,
+            "external_heat_entity": "input_boolean.stove",
+            "wood_tank_top_entity": "sensor.wood_top",
+            "wood_tank_bottom_entity": "sensor.wood_bottom",
+            "valve_outlet_temp_entity": "sensor.outlet",
+            "wood_tank_volume": 1000.0,
+        })
+    coord = _r10bo_Coord(FakeHass(), _r9f12_entry(data=cfg))
+    coord._snapshots_loaded = True
+    coord._optimization_result = _r9f12_ns(
+        buffer_temp_trajectory=list(trajectory),
+        dhw_temp_trajectory=list(dhw_trajectory),
+        timestamps=[_r10bo_t0 + timedelta(minutes=15 * i) for i in range(8)],
+    )
+    seen = []
+    real_update = coord._external_heat.update
+
+    def _r10bo_spy(obs):
+        seen.append(obs)
+        return real_update(obs)
+
+    coord._external_heat.update = _r10bo_spy
+    levels, dhw_levels = [], []
+    try:
+        for now in _r10bo_at:
+            _r9f12_dt.freeze(now)
+            states = [("sensor.indoor", "21.0"), ("sensor.outdoor", "5.0")]
+            if probe is not None:
+                states.append(("sensor.buffer", f"{probe}"))
+            if dhw_probe is not None:
+                states.append(("sensor.tank", f"{dhw_probe}"))
+            if wood:
+                states += [("sensor.wood_top", "70.0"), ("sensor.wood_bottom", "60.0"),
+                           ("sensor.outlet", "55.0")]
+            for entity, value in states:
+                coord.hass.states.set(entity, FakeState(value, last_updated=now, unit="°C"))
+            if wood:
+                coord.hass.states.set("input_boolean.stove", FakeState("on", last_updated=now))
+            _r9f12_aio.run(coord._update_current_state())
+            state = getattr(coord, "_ctx", coord)._current_state
+            levels.append(state.buffer_tank_temperature)
+            dhw_levels.append(state.dhw_temperature)
+    finally:
+        _r9f12_dt.freeze(None)
+    return levels, dhw_levels, seen, coord
+
+
+_r10bo_lv, _r10bo_dlv, _r10bo_obs, _ = _r10bo_run()
+R.check(
+    "R10-BUFFER-OPENLOOP: with no buffer probe the buffer level follows the "
+    "previous plan's trajectory, not the 40 degC default",
+    _r10bo_lv == [41.0, 43.0],
+    "buffer levels=%r (plan at covering steps 41.0, 43.0)" % (_r10bo_lv,),
+)
+R.check(
+    "R10-BUFFER-OPENLOOP: the observation's rise inputs carry no seed: with no "
+    "probe buffer_temp and dhw_temp are None while the state holds the seed",
+    [(o.buffer_temp, o.dhw_temp) for o in _r10bo_obs] == [(None, None)] * 2,
+    "rise inputs=%r" % ([(o.buffer_temp, o.dhw_temp) for o in _r10bo_obs],),
+)
+_r10bo_plv, _, _r10bo_pobs, _ = _r10bo_run(probe=36.5, dhw_probe=48.0)
+R.check(
+    "R10-BUFFER-OPENLOOP: a buffer probe reading ok wins over the plan (null control)",
+    _r10bo_plv == [36.5, 36.5],
+    "buffer levels=%r" % (_r10bo_plv,),
+)
+R.check(
+    "R10-BUFFER-OPENLOOP: with probes the rise inputs carry the readings",
+    [(o.buffer_temp, o.dhw_temp) for o in _r10bo_pobs] == [(36.5, 48.0)] * 2,
+    "rise inputs=%r" % ([(o.buffer_temp, o.dhw_temp) for o in _r10bo_pobs],),
+)
+_r10bo_elv, _, _, _r10bo_ecoord = _r10bo_run(trajectory=())
+_r10bo_default = type(getattr(_r10bo_ecoord, "_ctx", _r10bo_ecoord)._current_state)(
+).buffer_tank_temperature
+R.check(
+    "R10-BUFFER-OPENLOOP: an empty buffer trajectory (no throttling valve) "
+    "leaves the level as it is, never fabricated",
+    _r10bo_elv == [_r10bo_default, _r10bo_default] == [40.0, 40.0],
+    "buffer levels=%r default=%r" % (_r10bo_elv, _r10bo_default),
+)
+# The DHW seed re-expressed through ``_seed_store`` (behaviour unchanged; the
+# R9 D12-s1-01 checks above are its end-to-end control): the seed reaches the
+# state, and is not read back as a rise.
+_, _r10bo_dd, _r10bo_dobs, _ = _r10bo_run(dhw_trajectory=[50.0 + i for i in range(8)])
+R.check(
+    "R10-BUFFER-OPENLOOP: the open-loop DHW seed reaches the state but not the "
+    "detector's rise input",
+    _r10bo_dd == [51.0, 53.0] and [o.dhw_temp for o in _r10bo_dobs] == [None, None],
+    "dhw levels=%r rise inputs=%r" % (_r10bo_dd, [o.dhw_temp for o in _r10bo_dobs]),
+)
+
+
+# The wood arm: the level input ``hp_tank_temp`` is the useful floor of the
+# wood energy and the reference of the displacement, so it reads the best
+# level estimate (the seed), never None. Wood 70/60 degC (mean 65), outlet 55.
+def _r10bo_wood_expect(hp):
+    energy = (max(0.0, 65.0 - (hp + _r10bo_eh.WOOD_TANK_MIN_MARGIN))
+              * 1000.0 * _r10bo_eh.WATER_SPECIFIC_HEAT)
+    return round(energy, 6), round(min(1.0, max(0.0, (55.0 - hp) / (70.0 - hp))), 6)
+
+
+def _r10bo_wood(**kw):
+    _, _, _, coord = _r10bo_run(wood=True, **kw)
+    st = coord._external_heat.state
+    return (None if st.wood_energy_kwh is None else round(st.wood_energy_kwh, 6),
+            round(st.displacement, 6))
+
+
+_r10bo_wlv, _, _r10bo_wobs, _ = _r10bo_run(wood=True)
+_r10bo_w = _r10bo_wood()
+R.check(
+    "R10-BUFFER-OPENLOOP (wood_seed): with no buffer probe the wood reference "
+    "hp_tank_temp is the plan's seed, and wood energy and displacement follow it",
+    [o.hp_tank_temp for o in _r10bo_wobs] == [41.0, 43.0]
+    and _r10bo_w == _r10bo_wood_expect(43.0) != _r10bo_wood_expect(40.0),
+    "hp_tank_temp=%r outputs=%r expect(43)=%r expect(40)=%r"
+    % ([o.hp_tank_temp for o in _r10bo_wobs], _r10bo_w,
+       _r10bo_wood_expect(43.0), _r10bo_wood_expect(40.0)),
+)
+R.check(
+    "R10-BUFFER-OPENLOOP (wood_seed): a buffer probe wins and the wood outputs "
+    "follow the reading (null control)",
+    _r10bo_wood(probe=38.0) == _r10bo_wood_expect(38.0),
+    "outputs=%r expect=%r" % (_r10bo_wood(probe=38.0), _r10bo_wood_expect(38.0)),
+)
+R.check(
+    "R10-BUFFER-OPENLOOP (wood_seed): no seed and no reading keeps today's 40 degC "
+    "level, so wood energy and displacement stay on, as at base",
+    _r10bo_wood(trajectory=()) == _r10bo_wood_expect(40.0),
+    "outputs=%r expect=%r" % (_r10bo_wood(trajectory=()), _r10bo_wood_expect(40.0)),
+)
+
 # --- R10-DEMAND-OVERBOOK (#2499): the slab advances by the heat delivered ----
 R.section("R10-DEMAND-OVERBOOK: the unsensed slab advances by metered heat (#2499)")
 
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._update_current_state.GUARD_OFF.12569471.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._update_current_state.GUARD_OFF.12569471.json
deleted file mode 100644
index db5ad4875..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._update_current_state.GUARD_OFF.12569471.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._update_current_state GUARD_OFF 12569471",
-  "killed_by": "tests/entities.py",
-  "old": "        if buffer_reading.ok:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 4d4e78df8..cb78068d9 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17585,
+ "class_excess_loc": 17584,
  "const_modules_over_50": 3,
  "coordinator_attrs": 141,
  "coordinator_multiassigned_attrs": 108,
@@ -11,11 +11,11 @@
  "functions_cc_over_25": 8,
  "import_cycle_modules": 0,
  "max_cc": 44,
- "max_class_loc": 7955,
+ "max_class_loc": 7954,
  "max_method_loc": 373,
  "methods_over_150": 15,
  "methods_over_200": 8,
  "name_kept_members": 38,
- "recorded_at": "2a9cd3476dae9f45d3091b546fdd2723bcb0ce4e",
+ "recorded_at": "28482eceeb6b9809e44b12d80fc994282cc21645",
  "seam_cut_total": 423
 }

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
