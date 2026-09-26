"""D12-s1: omitted tank/slab probes and the solver's initial plant state (D12.M2).

Metric (per plant-state field F in {dhw, slab}): over N hourly
closed-loop coordinator cycles, the number of solves whose initial F (the
ThermalState that HeatPumpOptimizerCoordinator._solve_snapshot hands the
solver) differs by more than 1 K from the integration's OWN previous plan's
prediction of F for that instant (trajectory index 4 = +1 h of 15-min steps).
Count key: the value the solver seam receives, never a config attribute.
Also, for DHW: hours inside the configured demand windows that a model-truth
tank (advanced with ThermalModel.simulate_dhw_step from each plan's executed
first hour) spends below dhw_min_temperature.

Arms: A = probes omitted (dhw_temp_entity, floor_return_temp_entity): the config flow's default install with hot water.
B (null control and perturbation) = the same probes mapped, each reporting
the previous plan's prediction (the DHW probe reports the truth tank). The
mismatch counts must fall to ~0 in B.

Run:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D12/s1/state_seed.py [--hours 24] [--flat] [--grid]
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B6 container (4 CPU).
Expected (24 h, time-varying prices): A dhw mismatch 23-24, B 0; see REPORT.md.
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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matrix as m  # noqa: E402  (fetch patches, builders)
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

logging.disable(logging.CRITICAL)

HOURS = int(sys.argv[sys.argv.index("--hours") + 1]) if "--hours" in sys.argv else 24
FLAT = "--flat" in sys.argv
TRUTH0 = 50.0
WINDOWS = ((6.0, 8.5), (17.0, 22.0))
FIELDS = {  # field -> (ThermalState attr, OptimizationResult trajectory, probe key)
    "dhw": ("dhw_temperature", "dhw_temp_trajectory", "dhw_temp_entity"),
    "slab": ("slab_temperature", "slab_temp_trajectory", "floor_return_temp_entity"),
}


def in_window(hour):
    return any(a <= hour % 24 < b for a, b in WINDOWS)


GRID = [  # leave-one-out cells: (tank litres, daily litres)
    (200.0, 150.0), (150.0, 150.0), (300.0, 150.0), (200.0, 100.0), (200.0, 250.0)]


def run_arm(mapped: bool, volume: float = 200.0, daily: float = 150.0):
    cfg = dict(m.BASE)
    cfg.update({"dhw_tank_volume": volume, "dhw_setpoint": 55.0,
                "dhw_daily_consumption": daily,
                "dhw_min_temperature": 45.0,
                "dhw_windows": "06:00-08:30, 17:00-22:00"})
    if mapped:
        for _a, _t, key in FIELDS.values():
            cfg[key] = f"sensor.{key}"
    hass = FakeHass(m.states_for(cfg))
    entry = FakeEntry(data=cfg)
    orig_inject = m.inject
    if FLAT:
        def flat(c):
            orig_inject(c)
            for p in c._prices:
                p["total"] = 1.0
        m.inject = flat
    dt_util.freeze(m.START)
    try:
        asyncio.run(m.integ.async_setup_entry(hass, entry))
        coord = entry.runtime_data
        seen = []
        real_snap = coord._solve_snapshot

        def snap():
            state, opt = real_snap()
            seen.append({f: float(getattr(state, a)) for f, (a, _t, _k) in FIELDS.items()})
            return state, opt
        coord._solve_snapshot = snap
        model = coord._thermal_model
        truth = TRUTH0
        below_win = 0.0
        kwh = 0.0
        mins = []
        mismatch = {f: 0 for f in FIELDS}
        prev = None
        for h in range(HOURS):
            dt_util.freeze(m.START + timedelta(hours=h))
            if mapped:
                hass.states.set("sensor.dhw_temp_entity", FakeState(f"{truth:.2f}", unit="°C"))
                if prev is not None:
                    s = getattr(prev, "slab_temp_trajectory")[4]
                    # update_slab_from_return_temp reads return + 1 K as the slab
                    hass.states.set("sensor.floor_return_temp_entity", FakeState(f"{s - 1.0:.2f}", unit="°C"))
            n_before = len(seen)
            asyncio.run(coord.async_refresh())
            res = coord._optimization_result
            if len(seen) > n_before and prev is not None:
                for f, (_a, traj, _k) in FIELDS.items():
                    t = getattr(prev, traj) or []
                    want = truth if f == "dhw" else (t[4] if len(t) > 4 else None)
                    if want is not None and abs(seen[-1][f] - want) > 1.0:
                        mismatch[f] += 1
            prev = res
            sched = list(res.dhw_power_schedule or []) if res else []
            for j in range(4):
                p_el = float(sched[j]) if j < len(sched) else 0.0
                cop = model.compute_cop_dhw(-3.0, truth)
                kwh += p_el * 0.25
                hr = (h + j * 0.25) % 24.0
                truth = model.simulate_dhw_step(truth, cop * p_el, hr, dt_hours=0.25)
                mins.append(truth)
                if truth < 45.0 and in_window(hr):
                    below_win += 0.25
    finally:
        dt_util.freeze(None)
        m.inject = orig_inject
    distinct = {f: len({round(s[f], 2) for s in seen}) for f in FIELDS}
    return {"solves": len(seen), "mismatch": mismatch, "distinct_init": distinct,
            "window_hours_below_min": below_win, "dhw_kwh": round(kwh, 2),
            "truth_min": round(min(mins), 2)}


def main():
    t0, tt0 = time.process_time(), time.thread_time()
    if "--grid" in sys.argv:
        diffs = []
        for vol, daily in GRID:
            a = run_arm(False, vol, daily)
            b = run_arm(True, vol, daily)
            d = a["window_hours_below_min"] - b["window_hours_below_min"]
            diffs.append(d)
            print(f"CELL vol={vol} daily={daily} A={a['window_hours_below_min']} "
                  f"B={b['window_hours_below_min']} A_mismatch={a['mismatch']['dhw']} "
                  f"B_mismatch={b['mismatch']['dhw']}")
        best = max(diffs)
        rest = list(diffs)
        rest.remove(best)
        print(f"RESULT grid_cells={len(diffs)} count")
        print(f"RESULT grid_window_hours_excess_min={min(diffs)} h")
        print(f"RESULT grid_window_hours_excess_max={max(diffs)} h")
        print(f"RESULT grid_window_hours_excess_mean_drop_best={sum(rest) / len(rest):.3f} h")
        pc, tc = time.process_time() - t0, time.thread_time() - tt0
        print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
        print(f"RESULT load1={os.getloadavg()[0]:.2f}")
        return
    for name, mapped in (("A_omitted", False), ("B_mapped", True)):
        r = run_arm(mapped)
        print(f"ARM {name} {r}")
        print(f"RESULT {name}_solves={r['solves']} count")
        for f in FIELDS:
            print(f"RESULT {name}_{f}_init_mismatch_gt1K={r['mismatch'][f]} count")
            print(f"RESULT {name}_{f}_distinct_init_values={r['distinct_init'][f]} count")
        print(f"RESULT {name}_dhw_window_hours_below_min={r['window_hours_below_min']} h")
        print(f"RESULT {name}_dhw_kwh_executed={r['dhw_kwh']} kWh")
        print(f"RESULT {name}_dhw_truth_min={r['truth_min']} C")
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
