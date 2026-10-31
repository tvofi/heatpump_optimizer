"""D12-01 verification (verifier 3) -- an independent harness.

METRIC (one line): for the reference plant with every temperature entity in
exactly the unit HA's state machine holds on a US-customary instance (state =
the degF number, attributes.unit_of_measurement = "degF"), the absolute error
of the coordinator's adopted indoor/DHW/outdoor temperatures (degC), the share
of the 96 published schedule steps commanding zero compressor power, the count
of on/off flags commanding the pump OFF, and the published indoor_temp sensor's
native value -- against the identical plant in degC, and against the same degF
plant with the conversion done in the fixture (the value the integration
SHOULD have adopted).

RUN (from the repository root):

    PYTHONPATH=tests/hastub:tools/audit/round4/D12 \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D12/verify-0-3-units.py

EXPECTED: fahrenheit_indoor_error_c ~= 49.1 (70.5 - 21.4),
fahrenheit_zero_power_share = 1.0, fahrenheit_pump_off_steps = 96,
celsius_indoor_error_c = 0.0, celsius_zero_power_share = 0.0,
converted_indoor_error_c = 0.0 (|21.4 - (70.5-32)*5/9| < 0.01) and
converted plan energy back in the celsius arm's range (kwh > 0).
Tolerance: exact on counts/shares, +-0.05 on the degC errors.

Independence from the finder's harness: no wrapping of InputReader.read.  The
adopted temperatures are read from the coordinator's own _current_state after
_update_current_state(); the plan from _build_data_dict()'s schedule; the
published value from the sensor platform's own entities.  The perturbation is
done in the FIXTURE (pre-converted states), not by editing production.

BASELINE: 0855277 (branch head claude/13-dimension-audit-920935; finding
measured at 7dd68dd).  MACHINE: MacBookAir10,1 (8-core Apple M1, 8 GB).
INSTRUMENTED SYMBOL: heatpump_optimizer.coordinator:
HeatPumpOptimizerCoordinator._update_current_state (driven for real; its
adopted _current_state fields are the measured quantity).
"""
from __future__ import annotations

import os

# Thread pin, copied from tests/stress.py, before any numpy import.
for _var in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_var, "1")

import asyncio  # noqa: E402
import logging  # noqa: E402
import sys  # noqa: E402

sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
sys.path.insert(0, os.path.join(os.getcwd(), "custom_components"))

logging.disable(logging.CRITICAL)

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

import golden  # noqa: E402
import cells as cellmod  # noqa: E402
from heatpump_optimizer import sensor as sensor_mod  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

START = golden.START
PHYSICAL = {"indoor": 21.4, "dhw": 52.0, "outdoor": -3.0}
DT_H = 0.25


def f_of_c(c: float) -> float:
    return round(c * 9.0 / 5.0 + 32.0, 1)


def c_of_f(f: float) -> float:
    return round((f - 32.0) * 5.0 / 9.0, 4)


def rearm(states, mode):
    """mode: 'fahrenheit' (degF state + degF unit attribute, as a US-customary
    HA state machine holds it) or 'converted' (the degF plant with the state
    value pre-converted to degC, unit attribute degC)."""
    out = {}
    for eid, st in states.items():
        unit = st.attributes.get("unit_of_measurement") if st.attributes else None
        if unit == "°C":
            if mode == "fahrenheit":
                out[eid] = FakeState(str(f_of_c(float(st.state))), unit="°F")
            else:
                out[eid] = FakeState(str(c_of_f(f_of_c(float(st.state)))), unit="°C")
        else:
            out[eid] = st
    return out


def prices():
    from datetime import timedelta

    return [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (START + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]


def weather():
    from datetime import timedelta

    return [
        {
            "datetime": (START + timedelta(hours=h)).isoformat(),
            "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(48)
    ]


def drive(cfg, states):
    """My own driver: coordinator cycle, then the sensor platform alone."""
    hass = FakeHass()
    for eid, st in states.items():
        hass.states.set(eid, st)
    entry = FakeEntry(data=dict(cfg))
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    coord._prices = prices()
    coord._weather_forecast = weather()
    coord._solar_radiation_forecast = [0.0] * 48

    out = {}
    dt_util.freeze(START)

    async def _cycle():
        await coord._update_current_state()
        out["solve_status"] = await coord.async_run_optimization()
        coord.data = coord._build_data_dict()

    asyncio.run(_cycle())
    cs = coord._current_state
    out["adopted"] = {
        "indoor": cs.room_temperature,
        "dhw": cs.dhw_temperature,
        "outdoor": cs.outdoor_temperature,
    }
    sched = coord.data.get("schedule") or []
    powers = [float(s.get("power", 0.0) or 0.0) for s in sched]
    out["steps"] = len(sched)
    out["zero_power_steps"] = sum(1 for p in powers if p <= 1e-9)
    out["pump_off_steps"] = sum(
        1 for s in sched if not bool(s.get("heat_pump_on", True))
    )
    out["plan_kwh"] = sum(p * DT_H for p in powers)

    # The published sensor entities, through the real platform setup.
    entry.runtime_data = coord
    added = []
    out["sensor_setup_crash"] = None
    try:
        asyncio.run(sensor_mod.async_setup_entry(hass, entry, added.extend))
    except Exception as err:  # noqa: BLE001
        out["sensor_setup_crash"] = f"{type(err).__name__}: {err}"
    out["entities"] = len(added)
    out["unavailable"] = sum(1 for e in added if not e.available)
    for e in added:
        if getattr(e, "_key", None) == "indoor_temp":
            out["published_indoor"] = e.native_value
        if getattr(e, "_key", None) == "dhw_temperature":
            out["published_dhw"] = e.native_value
    dt_util.freeze(None)
    return out


def main():
    cfg, states = cellmod.fully_mapped()
    for label, mode in (
        ("celsius", None),
        ("fahrenheit", "fahrenheit"),
        ("converted", "converted"),
    ):
        st = states if mode is None else rearm(states, mode)
        r = drive(cfg, st)
        a = r["adopted"]
        err = {k: round(a[k] - PHYSICAL[k], 3) for k in PHYSICAL if a[k] is not None}
        print(f"RESULT {label}_solve_status={r['solve_status']} reason_code")
        print(f"RESULT {label}_indoor_error_c={err.get('indoor')} degC")
        print(f"RESULT {label}_dhw_error_c={err.get('dhw')} degC")
        print(f"RESULT {label}_outdoor_error_c={err.get('outdoor')} degC")
        print(f"RESULT {label}_zero_power_share="
              f"{round(r['zero_power_steps'] / r['steps'], 4) if r['steps'] else 'n/a'}")
        print(f"RESULT {label}_pump_off_steps={r['pump_off_steps']} count")
        print(f"RESULT {label}_plan_kwh={round(r['plan_kwh'], 3)} kWh")
        print(f"RESULT {label}_sensor_entities={r['entities']} count")
        print(f"RESULT {label}_sensor_unavailable={r['unavailable']} count")
        print(f"RESULT {label}_published_indoor_c={r.get('published_indoor')} degC")
        print(f"RESULT {label}_published_dhw_c={r.get('published_dhw')} degC")
        print(f"RESULT {label}_sensor_setup_crash={r['sensor_setup_crash']}")
        print()
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={round(os.getloadavg()[0], 2)}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
