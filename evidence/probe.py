#!/usr/bin/env python3
"""review-2071's own probe (reviewer-built; the finding has no committed harness).

    <venv-ci python> probe.py <tree> [diag|floor|all]

Runs inside <tree> (a checkout of the repository) with the features.py header
loaded, prints RESULT lines. Synthetic data only.
"""
import asyncio
import json
import os
import sys
from datetime import timedelta

tree = os.path.abspath(sys.argv[1])
mode = sys.argv[2] if len(sys.argv) > 2 else "all"
os.chdir(tree)
sys.path[:0] = [os.path.join(tree, p) for p in ("tests/hastub", "custom_components", "tests")]
path = os.path.join(tree, "tests/features.py")
src = open(path, encoding="utf-8").read()
ns = {"__file__": path, "__name__": "probe"}
exec(compile(src[: src.index('R = Results("Feature modules")')], path, "exec"), ns)

from homeassistant.util import dt as dtu  # noqa: E402
from heatpump_optimizer import const, diagnostics  # noqa: E402
import heatpump_optimizer as integration  # noqa: E402

FakeState, FakeHass, Coord = ns["FakeState"], ns["FakeHass"], ns["Coord"]
from harness import FakeEntry  # noqa: E402


def diag():
    token = "SYNTHTOKEN-abc123-options"
    name = "Synthetic Household Name 42"
    data = {
        "tibber_token": "SYNTHTOKEN-setup-xyz",
        "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        const.CONF_HEAT_PUMP_MIN_POWER: 3.0,
        const.CONF_HEAT_PUMP_MAX_POWER: 14.0,
        const.CONF_SOLAR_LOCATION: {"latitude": 59.312345, "longitude": 18.012345},
    }
    options = {
        const.CONF_HEAT_PUMP_MIN_POWER: 1.2,
        const.CONF_HEAT_PUMP_MAX_POWER: 6.0,
        "tibber_token": token,
        "name": name,
        const.CONF_SOLAR_LOCATION: {"latitude": 61.876543, "longitude": 15.234567},
    }
    hass = FakeHass()
    entry = FakeEntry(data=dict(data), options=dict(options))
    entry.runtime_data = integration.HeatPumpOptimizerCoordinator(
        hass, FakeEntry(data=dict(data), options=dict(options)))
    out = asyncio.run(diagnostics.async_get_config_entry_diagnostics(hass, entry))
    blob = json.dumps(out, default=str)
    cfg = out.get("config", {})
    print(f"RESULT diag config.min_kw={cfg.get(const.CONF_HEAT_PUMP_MIN_POWER)} "
          f"config.max_kw={cfg.get(const.CONF_HEAT_PUMP_MAX_POWER)} (live 1.2/6.0, setup 3.0/14.0)")
    print(f"RESULT diag config_setup.min_kw={out.get('config_setup', {}).get(const.CONF_HEAT_PUMP_MIN_POWER) if isinstance(out.get('config_setup'), dict) else out.get('config_setup')} "
          f"overridden={out.get('config_overridden_by_options')}")
    print(f"RESULT diag config.location={cfg.get(const.CONF_SOLAR_LOCATION)}")
    leaks = [s for s in (token, "SYNTHTOKEN-setup-xyz", name, "61.876543", "59.312345",
                         "61.87", "59.31", "15.234567", "18.012345") if s in blob]
    print(f"RESULT diag leaks={leaks}")
    print(f"RESULT diag token_fields={[cfg.get('tibber_token'), (out.get('config_setup') or {}).get('tibber_token') if isinstance(out.get('config_setup'), dict) else None]} name={cfg.get('name')}")


def floor():
    from heatpump_optimizer import notifier
    ent = "sensor.floor_return_synthetic"
    now = dtu.utcnow()

    def payload(state):
        states = {"sensor.indoor": FakeState("21.0", unit="°C"),
                  "sensor.outdoor": FakeState("-5.0", unit="°C")}
        if state is not None:
            states[ent] = state
        cfg = {"tibber_token": "x", "weather_entity": "weather.home",
               "indoor_temp_entity": "sensor.indoor",
               "outdoor_temp_entity": "sensor.outdoor",
               const.CONF_FLOOR_RETURN_TEMP_ENTITY: ent}
        c = Coord(FakeHass(states), FakeEntry(data=cfg))
        asyncio.run(c._update_current_state())
        return {"input_problems": c._input_health_view()["input_problems"]}, c

    lim = notifier.FLOOR_RETURN_SILENT_MINUTES
    cases = {
        "stale_7h": FakeState("31.5", unit="°C", last_reported=now - timedelta(hours=7)),
        "fresh_5min": FakeState("31.5", unit="°C", last_reported=now - timedelta(minutes=5)),
        "fresh_5h_under_limit": FakeState("31.5", unit="°C", last_reported=now - timedelta(hours=5)),
        "implausible_85C": FakeState("85.0", unit="°C", last_reported=now - timedelta(minutes=5)),
        "unknown": FakeState("unknown", unit="°C"),
    }
    for label, st in cases.items():
        p, c = payload(st)
        hass = FakeHass()
        w = notifier.FloorReturnWatch(hass)
        counts = []
        for m in (0, lim - 1, lim, lim * 10):
            w.handle(p, now + timedelta(minutes=m))
            counts.append(len([i for i in getattr(hass, "issues", [])
                               if i[1] == notifier.ISSUE_FLOOR_RETURN_SILENT]))
        probs = [(q["input"], q["problem"]) for q in p["input_problems"]]
        print(f"RESULT floor {label}: problems={probs} floor_return_temp={c._floor_return_temp} "
              f"issues_at[0,lim-1,lim,10lim]={counts}")


if mode in ("diag", "all"):
    diag()
if mode in ("floor", "all"):
    floor()
