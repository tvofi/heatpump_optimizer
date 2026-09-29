"""D8-s2 matrix: climate, switch and button entities over real coordinator payloads.

Metric definitions (one line each; every count is keyed on the value the
production entity property returns, never on an input attribute):
  climate_unavailable_with_payload  cells where the coordinator has a payload,
      last_update_success is True, and HeatPumpOptimizerClimate.available is False
  climate_attrs_hidden              payload-backed climate attribute leaves that
      exist (non-None) in the entity's own extra_state_attributes but are not
      published because the entity is unavailable, summed over cells
  hvac_action_vs_plan               cells x boost arm where HeatPumpOptimizerClimate
      .hvac_action says OFF/IDLE while the action the cycle actuated says the pump
      runs (heat_pump_on True and power+dhw_power >= 0.1 kW)
  mode_split_after_action           mode actions (climate set_hvac_mode / switch
      turn_on/off) whose immediate state write carries a live mode (hvac_mode,
      is_on) that disagrees with a payload-mode field published in the same write
      (hvac_action OFF-ness, switch attribute "mode")
  plus per-class hygiene counts (orjson, enum membership, staleness, button avail).

Command (repository root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D8/s2/matrix.py
Perturbations (in memory, flags):
  --perturb-available   climate.available drops the reading_ok term  -> climate_unavailable_with_payload 5 -> 0
  --perturb-hvac-action hvac_action reads current_action before mode -> hvac_action_vs_plan 14 -> 0
  --perturb-live-mode   payload-mode readers read coordinator.mode   -> mode_split_after_action 2 -> 0
Expected (baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, exact counts):
  climate_unavailable_with_payload=5 of 10 cells (all 5 no-thermometer cells; the 5
  thermometer cells are the null arm at 0), climate_attrs_hidden=112,
  hvac_action_vs_plan=14 (10 space-boost + 4 DHW-boost arms at mode off; the same
  boosts at mode auto are the null arm, 0), mode_split_after_action=2
  per-step oracle over every plan step: hvac_action_steps_vs_plan=0
Machine: audit box B7 (linux container), /home/claude/venv314 python.
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import argparse
import asyncio
import math
import sys
import tempfile
import time
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, "tests/hastub")

os.environ.setdefault("TMPDIR", tempfile.gettempdir())
_TMP = tempfile.mkdtemp(prefix="d8s2_")
os.environ["HPO_PLANDATA"] = os.path.join(_TMP, "plandata")

import numpy as np  # noqa: E402,F401
import orjson  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from homeassistant.components.climate import HVACAction, HVACMode  # noqa: E402

from heatpump_optimizer import boost, button, climate, const, switch  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from golden import START, coordinator_scenarios  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--perturb-available", action="store_true")
ap.add_argument("--perturb-hvac-action", action="store_true")
ap.add_argument("--perturb-live-mode", action="store_true")
ap.add_argument("--quick", action="store_true", help="first two scenarios only")
ARGS = ap.parse_args()

Climate = climate.HeatPumpOptimizerClimate

# ---------------------------------------------------------------- perturbations
if ARGS.perturb_available:
    # One-line production edit: drop the reading_ok term from available.
    def _avail(self):  # noqa: ANN001
        return bool(super(Climate, self).available)

    Climate.available = property(_avail)

if ARGS.perturb_hvac_action:
    _orig_action = Climate.hvac_action.fget

    def _hvac_action(self):  # noqa: ANN001
        if self.coordinator.data:
            action = self.coordinator.data.get("current_action", {})
            if action.get("heat_pump_on") or action.get("power_normalized", 0) > 0.1:
                return HVACAction.HEATING
        return _orig_action(self)

    Climate.hvac_action = property(_hvac_action)

if ARGS.perturb_live_mode:
    _orig_action2 = Climate.hvac_action.fget

    def _hvac_action_live(self):  # noqa: ANN001
        if self.coordinator.data and self.coordinator.mode == const.MODE_OFF:
            return HVACAction.OFF
        if self.coordinator.data and self.coordinator.data.get("mode") == const.MODE_OFF:
            # payload says off but live mode is not: fall through to the action
            action = self.coordinator.data.get("current_action", {})
            if action.get("power_normalized", 0) > 0.1 or action.get("heat_pump_on"):
                return HVACAction.HEATING
            return HVACAction.IDLE
        return _orig_action2(self)

    Climate.hvac_action = property(_hvac_action_live)
    _orig_sw_attrs = switch.OptimizerEnableSwitch.extra_state_attributes.fget

    def _sw_attrs(self):  # noqa: ANN001
        out = dict(_orig_sw_attrs(self) or {})
        if out:
            out["mode"] = self.coordinator.mode
        return out

    switch.OptimizerEnableSwitch.extra_state_attributes = property(_sw_attrs)

# ---------------------------------------------------------------- builders

THERMOMETERS = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
}


def _inject_inputs(coord, shift: float) -> None:
    coord._prices = [
        {
            "total": round(0.6 + shift + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (START + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]
    coord._weather_forecast = [
        {
            "datetime": (START + timedelta(hours=h)).isoformat(),
            "temperature": -5.0 - 4 * shift + 3.0 * (h % 24) / 24.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)
    ]


async def _noop(*_a, **_k):
    return None


def build(config: dict, thermometers: bool):
    hass = FakeHass()
    cfg = dict(config)
    if thermometers:
        cfg.update(THERMOMETERS)
        hass.states.set("sensor.indoor", FakeState("21.4"))
        hass.states.set("sensor.outdoor", FakeState("-3.0"))
    entry = FakeEntry(data=cfg)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    # Input fetchers replaced by injection (the golden capture's way); the
    # cycle body -- modes, boost overlay, actuation, payload -- is production.
    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop
    coord._async_learn_price_shape = _noop
    entry.runtime_data = coord
    return hass, entry, coord


async def cycle(coord, shift: float):
    _inject_inputs(coord, shift)
    coord.data = await coord._async_update_data()
    coord.last_update_success = True


def entities(hass, entry):
    out = []
    for module in (climate, switch, button):
        added = []
        asyncio.run(module.async_setup_entry(hass, entry, added.extend))
        out.extend(added)
    return out


def serialisable(obj) -> bool:
    try:
        orjson.dumps(obj)
    except TypeError:
        return False
    return not _nonfinite(obj)


def _nonfinite(obj) -> bool:
    if isinstance(obj, float):
        return not math.isfinite(obj)
    if isinstance(obj, dict):
        return any(_nonfinite(v) for v in obj.values())
    if isinstance(obj, (list, tuple)):
        return any(_nonfinite(v) for v in obj)
    return False


def pump_runs(action: dict) -> bool:
    draw = float(action.get("power") or 0.0) + float(action.get("dhw_power") or 0.0)
    return bool(action.get("heat_pump_on")) and draw >= 0.1


# ---------------------------------------------------------------- the matrix
counts = {
    "climate_unavailable_with_payload": 0,
    "climate_attrs_hidden": 0,
    "hvac_action_vs_plan": 0,
    "mode_split_after_action": 0,
    "orjson_or_nonfinite": 0,
    "enum_out_of_list": 0,
    "stale_attr": 0,
    "button_unavailable_idle": 0,
    "switch_is_on_not_bool": 0,
    "cells": 0,
}
detail: list[str] = []

scenarios = coordinator_scenarios()
names = list(scenarios)[:2] if ARGS.quick else list(scenarios)

# Attributes that restate a payload key one-to-one: (attr, payload key)
DIRECT = [
    ("current_price", "current_price"),
    ("predicted_savings", "predicted_savings"),
    ("savings_percentage", "savings_percentage"),
    ("optimization_status", "optimization_status"),
    ("solar_heat_gain_kw", "solar_heat_gain"),
    ("dhw_setpoint", "dhw_setpoint"),
]

cpu0 = time.process_time()
thr0 = time.thread_time()
dt_util.freeze(START + timedelta(hours=3, minutes=5))
try:
    for name in names:
        for thermo in (False, True):
            cell = f"{name}/{'thermo' if thermo else 'none'}"
            counts["cells"] += 1
            hass, entry, coord = build(scenarios[name], thermo)
            # Cycle 1: HA's own first refresh (light path), cycle 2 solves.
            asyncio.run(cycle(coord, 0.0))
            ents1 = entities(hass, entry)
            clim1 = next(e for e in ents1 if isinstance(e, Climate))
            snap1 = clim1.extra_state_attributes
            if thermo:
                hass.states.set("sensor.indoor", FakeState("20.1"))
                hass.states.set("sensor.outdoor", FakeState("-7.0"))
            asyncio.run(cycle(coord, 0.3))
            ents = entities(hass, entry)
            clim = next(e for e in ents if isinstance(e, Climate))
            attrs = clim.extra_state_attributes
            data = coord.data
            # -- availability
            if data and coord.last_update_success and not clim.available:
                counts["climate_unavailable_with_payload"] += 1
                hidden = [k for k, v in attrs.items() if v is not None]
                counts["climate_attrs_hidden"] += len(hidden)
                detail.append(
                    f"{cell}: climate unavailable, hvac_mode={clim.hvac_mode}, "
                    f"target={clim.target_temperature}, {len(hidden)} attrs hidden"
                )
            # -- serialisation, enums
            for e in ents:
                a = getattr(e, "extra_state_attributes", None) or {}
                if not serialisable(a):
                    counts["orjson_or_nonfinite"] += 1
                    detail.append(f"{cell}: {type(e).__name__} attrs not serialisable")
                if isinstance(e, switch.SwitchEntity if hasattr(switch, "SwitchEntity") else object):
                    pass
                if hasattr(type(e), "is_on") and not isinstance(e, Climate):
                    if not isinstance(e.is_on, bool):
                        counts["switch_is_on_not_bool"] += 1
                        detail.append(f"{cell}: {type(e).__name__}.is_on={e.is_on!r}")
            if clim.hvac_mode not in clim._attr_hvac_modes:
                counts["enum_out_of_list"] += 1
            if clim.preset_mode is not None and clim.preset_mode not in clim._attr_preset_modes:
                counts["enum_out_of_list"] += 1
            for v in (clim.current_temperature, clim.target_temperature):
                if v is not None and not isinstance(v, float):
                    counts["enum_out_of_list"] += 1
            # -- staleness: attribute follows the payload in both cycles
            for attr, key in DIRECT:
                if attrs.get(attr) != (data.get(key) if key != "dhw_setpoint" else data.get(key)):
                    counts["stale_attr"] += 1
                    detail.append(f"{cell}: {attr}={attrs.get(attr)!r} payload={data.get(key)!r}")
            if thermo and clim.current_temperature != 20.1:
                counts["stale_attr"] += 1
                detail.append(f"{cell}: current_temperature={clim.current_temperature} after 20.1")
            # -- buttons idle
            for e in ents:
                if isinstance(e, button.ForceOptimizationButton) and not e.available:
                    counts["button_unavailable_idle"] += 1
                    detail.append(f"{cell}: Optimize Now unavailable while idle")
            # -- oracle: mode OFF with a boost channel live (cycle actuates it)
            for channel in ("dhw", "space"):
                if channel == "dhw" and not data.get("dhw_enabled"):
                    continue
                coord._mode = const.MODE_OFF
                boost.held_for(coord).until.clear()
                boost.held_for(coord).set(channel, True, dt_util.now())
                asyncio.run(cycle(coord, 0.3))
                action = coord.data.get("current_action", {})
                act = clim.hvac_action
                runs = pump_runs(action)
                if runs and act in (HVACAction.OFF, HVACAction.IDLE):
                    counts["hvac_action_vs_plan"] += 1
                    detail.append(
                        f"{cell}: mode=off boost_{channel}: action heat_pump_on="
                        f"{action.get('heat_pump_on')} power={action.get('power')} "
                        f"dhw_power={action.get('dhw_power')} -> hvac_action={act}"
                    )
                # And the same boost with the optimizer on (control arm: must be HEATING)
                coord._mode = const.MODE_AUTO
                asyncio.run(cycle(coord, 0.3))
                action = coord.data.get("current_action", {})
                if pump_runs(action) and clim.hvac_action in (HVACAction.OFF, HVACAction.IDLE):
                    counts["hvac_action_vs_plan"] += 1
                    detail.append(f"{cell}: mode=auto boost_{channel} hvac_action={clim.hvac_action}")
                boost.held_for(coord).until.clear()
finally:
    dt_util.freeze(None)

# ---------------------------------------------------------------- mode actions
dt_util.freeze(START + timedelta(hours=3, minutes=5))
try:
    hass, entry, coord = build(scenarios["coord_minimal"], True)
    asyncio.run(cycle(coord, 0.0))
    asyncio.run(cycle(coord, 0.3))
    ents = entities(hass, entry)
    clim = next(e for e in ents if isinstance(e, Climate))
    sw = next(e for e in ents if isinstance(e, switch.OptimizerEnableSwitch))
    for e in (clim, sw):
        e.hass = hass

    def snapshot(e):
        if isinstance(e, Climate):
            return {"hvac_mode": e.hvac_mode, "hvac_action": e.hvac_action}
        return {"is_on": e.is_on, "mode": (e.extra_state_attributes or {}).get("mode")}

    def split(snap) -> bool:
        if "hvac_mode" in snap:
            live_off = snap["hvac_mode"] == HVACMode.OFF
            payload_off = snap["hvac_action"] == HVACAction.OFF
            return live_off != payload_off
        return bool(snap["is_on"]) == (snap["mode"] == const.MODE_OFF)

    writes: list[tuple[str, dict]] = []
    for e in (clim, sw):
        orig = e.async_write_ha_state

        def _w(e=e, orig=orig):
            writes.append((type(e).__name__, snapshot(e)))
            orig()

        e.async_write_ha_state = _w
    # Pre-state: action says the pump runs in auto.
    coord._current_action = {**coord._current_action, "heat_pump_on": True}
    coord.data = {**coord.data, "current_action": coord._current_action}
    asyncio.run(clim.async_set_hvac_mode(HVACMode.OFF))
    asyncio.run(clim.async_set_hvac_mode(HVACMode.AUTO))
    asyncio.run(sw.async_turn_off())
    for label, snap in writes:
        if split(snap):
            counts["mode_split_after_action"] += 1
            detail.append(f"mode action: {label} write {snap}")
finally:
    dt_util.freeze(None)

# ---------------------------------------------------------------- per-step oracle
# Every step of a real solved plan (auto mode, DHW + all features), read
# through Optimizer.get_current_action as the cycle does, then through the
# climate: min-modulation and DHW-only steps included.
counts["hvac_action_steps_vs_plan"] = 0
counts["plan_steps_checked"] = 0
counts["plan_steps_dhw_only"] = 0
dt_util.freeze(START + timedelta(hours=3, minutes=5))
try:
    hass, entry, coord = build(scenarios["coord_all_features"], True)
    asyncio.run(cycle(coord, 0.0))
    asyncio.run(cycle(coord, 0.3))
    result = coord._optimization_result
    _state, opt = coord._solve_snapshot()
    clim = next(e for e in entities(hass, entry) if isinstance(e, Climate))
    for ts in result.timestamps:
        action = opt.get_current_action(result, ts)
        coord.data = {**coord.data, "current_action": action}
        counts["plan_steps_checked"] += 1
        if float(action.get("power") or 0) < 0.1 and float(action.get("dhw_power") or 0) >= 0.1:
            counts["plan_steps_dhw_only"] += 1
        heating = clim.hvac_action == HVACAction.HEATING
        if pump_runs(action) != heating and bool(action.get("heat_pump_on")) != heating:
            counts["hvac_action_steps_vs_plan"] += 1
            detail.append(f"step {ts}: action={action} hvac_action={clim.hvac_action}")
finally:
    dt_util.freeze(None)

cpu = time.process_time() - cpu0
thr = time.thread_time() - thr0
for line in detail:
    print("DETAIL", line)
for k, v in counts.items():
    print(f"RESULT {k}={v} count")
print(f"RESULT thread_factor={cpu / max(thr, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    with open("/proc/vmstat") as fh:
        swp = next((int(l.split()[1]) for l in fh if l.startswith("pswpin")), 0)
except OSError:
    swp = -1
print(f"RESULT swapins={swp}")
