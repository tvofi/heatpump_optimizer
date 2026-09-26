"""D12 verify-v2 for D12-s1-01: the solver's initial DHW tank temperature with no tank probe.

Metric (plan self-consistency, no external truth model): over N hourly
coordinator cycles, the number of solves k>=2 whose initial_state.dhw_temperature
(as handed to coordinator._await_optimize, the process-pool seam) differs by
more than 1 K from the PREVIOUS solve's own dhw_temp_trajectory at the elapsed
hour (index = steps per hour). Count key: the state object the solver seam
receives. Secondary: distinct initial DHW values; planned DHW kWh in each
plan's first hour (the part that would execute), summed.

Arms: omitted = coord_dhw-shaped config (tests/golden.py) plus indoor/outdoor
probes, no dhw_temp_entity. mapped (null control) = dhw_temp_entity mapped,
reporting the previous plan's own +1 h prediction (55.0 C on the first cycle,
equal to the ThermalState default, so the two arms start identical).
Prices roll with the clock (48 h from each cycle's hour), unlike the finder's
fixed START-anchored list.

Perturbation: --perturb patches coordinator._await_optimize so that, when the
tank probe is absent, the state's dhw_temperature is seeded from the previous
plan's +1 h trajectory (the finder's proposed fix, in memory). Expected: the
omitted-arm mismatch count falls to 0.

Run:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D12/verify-v2/v2_dhw_seed.py [--hours 24] [--perturb] [--flat]
Primary RESULT solves_init_gap_gt1K_vs_propagated: solves whose omitted-arm initial tank
differs >1 K from the mapped arm's open-loop-propagated tank at the same hour (the tank the
integration's own plans say it left, chained from the same 55 C start).
Expected (24 h): 19 of 24 (+-2), max gap 12.4 K (+-1); --flat 19 of 24; --perturb 2 of 24,
max gap 1.3 K; mapped arm per-step mismatch 0 (exact).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: G2-V2 cloud container, 4 vCPU, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import logging
import sys
import time
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
import heatpump_optimizer as integ  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from golden import START, coordinator_scenarios  # noqa: E402

logging.disable(logging.CRITICAL)
HOURS = int(sys.argv[sys.argv.index("--hours") + 1]) if "--hours" in sys.argv else 24
PERTURB = "--perturb" in sys.argv
FLAT = "--flat" in sys.argv
NOW = {"h": 0}


async def _prices(self):
    base = START + timedelta(hours=NOW["h"])
    self._prices = [{"total": 1.0 if FLAT else round(0.5 + 0.8 * ((NOW["h"] + h) % 24 in range(7, 10) or (NOW["h"] + h) % 24 in range(17, 21)), 3),
                     "starts_at": (base + timedelta(hours=h)).isoformat(), "level": "NORMAL"} for h in range(48)]
    self._weather_forecast = [{"datetime": (base + timedelta(hours=h)).isoformat(),
                               "temperature": 0.0, "wind_speed": 2.0, "precipitation": 0.0,
                               "humidity": 80.0} for h in range(48)]
    self._solar_radiation_forecast = [0.0] * 48


async def _noop(self):
    return None


cm.HeatPumpOptimizerCoordinator._fetch_tibber_prices = _prices
cm.HeatPumpOptimizerCoordinator._fetch_weather_forecast = _noop
cm.HeatPumpOptimizerCoordinator._fetch_solar_forecast = _noop


def run(mapped):
    cfg = dict(coordinator_scenarios()["coord_dhw"])
    cfg["indoor_temp_entity"] = "sensor.indoor"
    cfg["outdoor_temp_entity"] = "sensor.outdoor"
    states = {"sensor.indoor": FakeState("21.0", unit="°C"),
              "sensor.outdoor": FakeState("0.0", unit="°C")}
    if mapped:
        cfg["dhw_temp_entity"] = "sensor.tank"
        states["sensor.tank"] = FakeState("55.0", unit="°C")
    hass = FakeHass(states)
    entry = FakeEntry(data=cfg)
    calls = []
    real = cm._await_optimize
    prev = {"res": None}

    async def hook(hass_, optimizer, state, *a, **k):
        if PERTURB and not mapped and prev["res"] is not None:
            t = prev["res"].dhw_temp_trajectory
            if t and len(t) > 4:
                state.dhw_temperature = float(t[4])
        res = await real(hass_, optimizer, state, *a, **k)
        calls.append((float(state.dhw_temperature), res))
        return res

    cm._await_optimize = hook
    try:
        dt_util.freeze(START)
        asyncio.run(integ.async_setup_entry(hass, entry))
        coord = entry.runtime_data
        solves = []  # (init, result) of the main solve per cycle
        for h in range(HOURS):
            NOW["h"] = h
            dt_util.freeze(START + timedelta(hours=h))
            if mapped and solves:
                t = solves[-1][1].dhw_temp_trajectory
                hass.states.set("sensor.tank", FakeState(f"{t[4]:.2f}", unit="°C"))
            n0 = len(calls)
            asyncio.run(coord.async_refresh())
            main = [c for c in calls[n0:] if c[1] is coord._optimization_result]
            if main:
                solves.append(main[-1])
                prev["res"] = main[-1][1]
    finally:
        cm._await_optimize = real
        dt_util.freeze(None)
    spp = 4  # 15-min steps
    mism, comparable = 0, 0
    for (i0, r0), (i1, _r1) in zip(solves, solves[1:]):
        t = r0.dhw_temp_trajectory
        if t and len(t) > spp:
            comparable += 1
            if abs(i1 - float(t[spp])) > 1.0:
                mism += 1
    first_hour_kwh = sum(sum(float(x) for x in (r.dhw_power_schedule or [])[:spp]) * 0.25 for _i, r in solves)
    distinct = len({round(i, 2) for i, _r in solves})
    pred_min = min(float(r.dhw_temp_trajectory[spp]) for _i, r in solves if r.dhw_temp_trajectory)
    return dict(solves=len(solves), comparable=comparable, mismatch=mism, distinct=distinct,
                first_hour_kwh=round(first_hour_kwh, 2), min_pred_plus1h=round(pred_min, 2),
                init_min=round(min(i for i, _r in solves), 2)), [i for i, _r in solves]


def main():
    t0, tt0 = time.process_time(), time.thread_time()
    inits = {}
    for name, mapped in (("omitted", False), ("mapped", True)):
        r, inits[name] = run(mapped)
        print(f"ARM {name} {r}")
        for k, v in r.items():
            print(f"RESULT {name}_{k}={v}")
    gaps = [abs(a - b) for a, b in zip(inits["omitted"], inits["mapped"])]
    print("GAPS " + " ".join(f"{g:.2f}" for g in gaps))
    print(f"RESULT solves_init_gap_gt1K_vs_propagated={sum(g > 1.0 for g in gaps)} of {len(gaps)} solves")
    print(f"RESULT max_init_gap_vs_propagated={max(gaps):.2f} K")
    pc, tc = time.process_time() - t0, time.thread_time() - tt0
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [ln for ln in open('/proc/vmstat') if ln.startswith('pswpin')][0].split()[1]
    except Exception:  # noqa: BLE001
        sw = "na"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
