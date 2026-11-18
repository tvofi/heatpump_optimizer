"""D12 verifier-2 independent harness for D12-01 (units).

METRIC (one line): for the same physical minimal plant (indoor 21.4 C,
outdoor -3.0 C, DHW tank 52.0 C, a wired on/off switch) driven through the
real coordinator, |adopted indoor temperature - 21.4| in K, the planned
heating energy over the published schedule in kWh, the switch service
commands _apply_action issues, repair issues raised and entities left
unavailable -- °C states vs the identical plant with every sensor natively
in °F (what a US-customary Home Assistant exposes for device_class
temperature, per developers.home-assistant.io/docs/core/entity/sensor).

RUN (from the repository root):

    PYTHONPATH=tests/hastub:tools/audit/round4/D12 \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D12/v2_units_verify.py

EXPECTED (counts and published values; not a timing):
  celsius_indoor_error_k=0.0, imperial_indoor_error_k=49.1 (70.5-21.4),
  celsius_plan_kwh>0, imperial_plan_kwh=0.0 with plan_steps=96,
  imperial_switch_off_commands=1, *_issues=0, *_unavailable=0 (the plant
  is fully healthy in both arms; nothing tells the user).
PERTURBATION: the arm differential itself (sensor states °F -> °C, a
  config change): imperial_plan_kwh must move 0.0 -> the celsius value.
INSTRUMENTED SYMBOL: none wrapped -- the number is taken from the
  coordinator's own adopted state (HeatPumpOptimizerCoordinator
  _update_current_state -> _build_data_dict) and from the service-call
  log (hass.services.calls) and issue list (hass.issues), not from a
  wrapper on the accused function.
BASELINE: measured at branch head 0855277edc49cb3cce3b1095fa1e5edcda7663c8
  (finding was measured at 7dd68dd327fe3dbfb09f3bd0fe38910c58877697).
MACHINE: verifier seat D12-2, same 8-core Apple M1 box, macOS 25.6.0.
"""
from __future__ import annotations

import asyncio
import os

# Thread pin (per the harness contract), before any numpy import.
for _var in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_var, "1")

import sys  # noqa: E402

import d12lib  # noqa: F401,E402  (path setup + thread pin)
import cells as cellmod  # noqa: E402
from harness import FakeState  # noqa: E402

from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import sensor as sensor_mod  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

START = d12lib.START
PHYSICAL = {"indoor": 21.4, "outdoor": -3.0, "dhw": 52.0}
SWITCH = "switch.us_pump"


def f_of_c(c):
    return round(c * 9.0 / 5.0 + 32.0, 1)


def plant(imperial: bool):
    """The smallest realistic install: house + DHW + one on/off switch."""
    unit = "°F" if imperial else "°C"

    def t(c):
        v = f_of_c(c) if imperial else c
        return FakeState(str(v), unit=unit)

    cfg = dict(cellmod.BASE)
    cfg.update(cellmod.DHW_ON)
    cfg["indoor_temp_entity"] = "sensor.us_indoor"
    cfg["outdoor_temp_entity"] = "sensor.us_outdoor"
    cfg["dhw_temp_entity"] = "sensor.us_tank"
    cfg["heat_pump_switch_entity"] = SWITCH
    states = {
        "sensor.us_indoor": t(PHYSICAL["indoor"]),
        "sensor.us_outdoor": t(PHYSICAL["outdoor"]),
        "sensor.us_tank": t(PHYSICAL["dhw"]),
        SWITCH: FakeState("on"),
        "weather.home": FakeState("cloudy", attributes={"temperature": -3.0,
                                                        "humidity": 85.0}),
    }
    return cfg, states


async def cycle(cfg, states):
    hass, entry, coord = d12lib.build(cfg, states)
    await coord._update_current_state()
    status = await coord.async_run_optimization()
    coord.data = coord._build_data_dict()
    await coord._apply_action()          # the actuation surface, really run
    switch_cmds = [(d, s) for (d, s, _data) in hass.services.calls
                   if d == "switch"]
    issues = list(getattr(hass, "issues", []))
    entry.runtime_data = coord
    added = []
    await sensor_mod.async_setup_entry(hass, entry, added.extend)
    unavailable = sum(1 for e in added if not e.available)
    return hass, coord, status, switch_cmds, issues, added, unavailable


def arm(label, imperial):
    cfg, states = plant(imperial)
    dt_util.freeze(START)
    try:
        hass, coord, status, switch_cmds, issues, added, unavailable = \
            asyncio.run(cycle(cfg, states))
    finally:
        dt_util.freeze(None)
    data = coord.data or {}
    sched = data.get("schedule") or []
    plan_kwh = sum(float(s.get("power", 0.0) or 0.0) * 0.25 for s in sched)
    indoor = data.get("indoor_temperature")
    err = None if indoor is None else round(abs(indoor - PHYSICAL["indoor"]), 3)
    print(f"RESULT {label}_indoor_temperature_c={indoor} degC")
    print(f"RESULT {label}_indoor_error_k={err} K")
    print(f"RESULT {label}_dhw_temperature_c={data.get('dhw_temperature')} degC")
    print(f"RESULT {label}_outdoor_temperature_c="
          f"{data.get('outdoor_temperature')} degC")
    print(f"RESULT {label}_solve_status={status}")
    print(f"RESULT {label}_plan_kwh={round(plan_kwh, 3)} kWh")
    print(f"RESULT {label}_plan_steps={len(sched)} count")
    print(f"RESULT {label}_max_step_kw="
          f"{max([float(s.get('power', 0.0) or 0.0) for s in sched] or [0.0])} kW")
    print(f"RESULT {label}_switch_off_commands="
          f"{sum(1 for d, s in switch_cmds if s == 'turn_off')} count")
    print(f"RESULT {label}_switch_on_commands="
          f"{sum(1 for d, s in switch_cmds if s == 'turn_on')} count")
    print(f"RESULT {label}_repair_issues={len(issues)} count")
    print(f"RESULT {label}_sensor_entities={len(added)} count")
    print(f"RESULT {label}_sensor_unavailable={unavailable} count")
    print()


def main(argv):
    arm("celsius", imperial=False)
    arm("imperial", imperial=True)
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={d12lib.load1()}")
    print(f"RESULT swapins={d12lib.swapins()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
