"""D12-H3 -- every registered service, on every plant cell that is not the
reference plant.

METRIC (one line): over (plant cell x registered service) pairs, the number
that raise something other than a named Home Assistant refusal
(HomeAssistantError / ServiceValidationError / vol.Invalid).

RUN (from the repository root):

    PYTHONPATH=tests/hastub:tools/audit/round4/D12 \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D12/services_cells.py

BASELINE: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697
MACHINE: MacBookAir10,1 (8-core Apple M1, 8 GB), macOS 25.6.0
INSTRUMENTED SYMBOL: heatpump_optimizer.services:async_register_services and
  every handler it binds, driven through hass.services.async_call.
PERTURBATION: --shrink drops DHW / wood / PV / one zone from every cell.
NULL CONTROL: the NULL_fully_mapped cell's row, printed separately.
"""
from __future__ import annotations

import asyncio
import sys
from collections import Counter

import d12lib
import cells as cellmod
import voluptuous as vol

from heatpump_optimizer import const, services as services_mod
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from harness import FakeEntry, FakeHass

try:
    from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
except Exception:  # noqa: BLE001
    class HomeAssistantError(Exception):
        pass
    ServiceValidationError = HomeAssistantError

NAMED_REFUSALS = (HomeAssistantError, ServiceValidationError, vol.Invalid)

# One minimal, schema-valid payload per registered service.
PAYLOADS = {
    const.SERVICE_RUN_OPTIMIZATION: {},
    const.SERVICE_SET_MODE: {"mode": "economy"},
    const.SERVICE_SET_AWAY: {"active": True},
    const.SERVICE_SET_THERMAL_PARAMS: {"heat_pump_cop_nominal": 3.9},
    const.SERVICE_SIMULATE_PLAN: {"target_temp": 20.0},
    const.SERVICE_APPLY_SCHEDULE: None,       # filled per cell from the plan
    const.SERVICE_ASSIGN_ENTITY: {"field": "indoor_temp_entity",
                                  "entity_id": "sensor.hpo_indoor_temp"},
    const.SERVICE_APPLY_TOPOLOGY: {"layout": "no_valve"},
    const.SERVICE_APPLY_MANUAL_PLAN: None,    # filled per cell from the plan
    const.SERVICE_CLEAR_MANUAL_PLAN: {},
    const.SERVICE_RESTORE_SNAPSHOT: {"component": "heat_curve"},
    const.SERVICE_DIAGNOSE_INTERVAL: {},
}


def _cell_pairs(shrink):
    matrix = [c for c in cellmod.enumerate_cells()
              if c[0] in ("T", "P", "L", "NULL")]
    if shrink:
        drop = ("dhw_tank_volume", "dhw_setpoint", "dhw_min_temperature",
                "dhw_windows", "wood_tank_top_entity", "wood_tank_volume",
                "pv_enabled", "pv_peak_kw", "pv_export_price",
                "upper_floor_thermal_mass", "lower_floor_thermal_mass",
                "upper_floor_heat_loss", "lower_floor_heat_loss")
        out = []
        for group, name, cfg, states in matrix:
            cfg = {k: v for k, v in cfg.items() if k not in drop}
            out.append((group, name, cfg, states))
        matrix = out
    return matrix


def main(argv):
    shrink = "--shrink" in argv
    matrix = _cell_pairs(shrink)
    crashes = []
    refusals = Counter()
    pairs = 0
    null_row = None

    for group, name, cfg, states in matrix:
        hass = FakeHass()
        for eid, st in (states or {}).items():
            hass.states.set(eid, st)
        entry = FakeEntry(data=dict(cfg))
        coord = HeatPumpOptimizerCoordinator(hass, entry)
        coord._prices = d12lib._prices()
        coord._weather_forecast = d12lib._weather()
        coord._solar_radiation_forecast = d12lib._solar()
        entry.runtime_data = coord
        # The entry roster the service handlers resolve their targets from
        # (harness.FakeConfigEntries.async_entries). Without this every call
        # is refused with "No loaded ... config entry matched this call",
        # which is a named refusal and would read as a clean pass.
        hass.config_entries.entries.append(entry)
        # ...and LOADED, or every handler answers with the same named refusal
        # ("No loaded Heat Pump Optimizer config entry matched this call") and
        # a harness that only counts crashes reads a clean 0 off a run in
        # which no handler body executed.
        from homeassistant.config_entries import ConfigEntryState
        entry.state = ConfigEntryState.LOADED
        from homeassistant.util import dt as dt_util
        dt_util.freeze(d12lib.START)
        try:
            asyncio.run(coord._update_current_state())
            asyncio.run(coord.async_run_optimization())
            coord.data = coord._build_data_dict()
            services_mod.async_register_services(hass)
            schedule = (coord.data.get("schedule") or [])[:4]
            local = dict(PAYLOADS)
            local[const.SERVICE_APPLY_SCHEDULE] = {
                "entries": [{"start": s.get("time") or s.get("timestamp"),
                             "power": s.get("power", 0.0)} for s in schedule]
            } if schedule else {"entries": []}
            local[const.SERVICE_APPLY_MANUAL_PLAN] = {
                "plan": [{"start": s.get("time") or s.get("timestamp"),
                          "power": s.get("power", 0.0)} for s in schedule]
            } if schedule else {"plan": []}
            cell_crashes = 0
            for service, payload in local.items():
                pairs += 1
                try:
                    asyncio.run(hass.services.async_call(
                        const.DOMAIN, service, payload or {}))
                except NAMED_REFUSALS as err:
                    refusals[f"{service}:{type(err).__name__}"] += 1
                except Exception as err:  # noqa: BLE001
                    cell_crashes += 1
                    crashes.append((group, name, service,
                                    f"{type(err).__name__}: {err}"))
            if group == "NULL":
                null_row = cell_crashes
        finally:
            dt_util.freeze(None)

    print(f"RESULT service_cell_pairs={pairs} count")
    print(f"RESULT service_cell_crashes={len(crashes)} count")
    print(f"RESULT service_named_refusals={sum(refusals.values())} count")
    if null_row is not None:
        print(f"RESULT null_control_fully_mapped_crashes={null_row} count")
    by_service = Counter(s for _, _, s, _ in crashes)
    for service, n in sorted(by_service.items()):
        print(f"RESULT crashes_{service}={n} count")
    print()
    seen = set()
    for group, name, service, detail in crashes:
        sig = (service, detail.split("\n")[0][:120])
        if sig in seen:
            continue
        seen.add(sig)
        print(f"CRASH {group:5s} {name:34s} {service:22s} {detail[:160]}")
    print()
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={d12lib.load1()}")
    print(f"RESULT swapins={d12lib.swapins()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
