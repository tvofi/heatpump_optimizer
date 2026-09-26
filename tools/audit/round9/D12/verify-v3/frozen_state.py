"""D12 verify-v3 (round 9), own harness for D12-s1-01: which ThermalState fields
reach the solver as a never-advanced constant when their probe is omitted.

Metric (one line): per plant-state field F with a plan trajectory, over N hourly
coordinator cycles with F's probe omitted, frozen_F = 1 when every
_solve_snapshot input for F equals one value across all N solves while the
integration's own previous plan predicts F at +1 h more than 1 K away from it
in at least half of the cycles; RESULT frozen_fields = sum over F.
Origin proof (sentinel): before the first cycle the live
_current_state.<F> is overwritten with a sentinel (47.3 for dhw, 31.7 for
buffer); if every solve still receives exactly the sentinel, nothing in the
integration ever advances F -- it is whatever value was there (the dataclass
default in production).

Fields: dhw (dhw_temperature / dhw_temp_trajectory), slab
(slab_temperature / slab_temp_trajectory), buffer (buffer_tank_temperature /
buffer_temp_trajectory), lower (lower_floor_temperature / lower_temp_trajectory).
The finder's rule (state_seed.py FIELDS) lists dhw and slab only.

Arms: omitted (no dhw/floor-return/buffer probes; two-zone with no
lower-floor probe) and mapped (each probe reports the previous plan's +1 h
prediction; null control, frozen_fields must be 0).
Perturbation --advance: patch HeatPumpOptimizerCoordinator._solve_snapshot in
memory so omitted fields are propagated from the previous plan's +1 h value
(open-loop, the proposed fix shape); frozen_fields must fall to 0.

Run:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D12/verify-v3/frozen_state.py [--hours 12] [--advance]
Expected: omitted arm frozen_fields >= 2 (dhw, and buffer if modelled); mapped 0; --advance 0. Exact.
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round-9 evidence 6f51db2c).
Machine: G2-V3 cloud container, 4 vCPU, CPython 3.14.0rc2, numpy/OpenBLAS.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import copy
import logging
import sys
import time
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, "tools/audit/round9/D12/s1")

import matrix as m  # noqa: E402  (the finder's offline price/forecast injection; reused, not its metric)
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

logging.disable(logging.CRITICAL)
HOURS = int(sys.argv[sys.argv.index("--hours") + 1]) if "--hours" in sys.argv else 12
ADVANCE = "--advance" in sys.argv

FIELDS = {  # name: (state attr, result trajectory, probe key, sentinel)
    "dhw": ("dhw_temperature", "dhw_temp_trajectory", "dhw_temp_entity", 47.3),
    "slab": ("slab_temperature", "slab_temp_trajectory", "floor_return_temp_entity", None),
    "buffer": ("buffer_tank_temperature", "buffer_temp_trajectory", "buffer_tank_temp_entity", 31.7),
    "lower": ("lower_floor_temperature", "lower_temp_trajectory", "lower_floor_temp_entity", None),
}


def config(mapped):
    cfg = dict(m.BASE)
    cfg.update({"dhw_tank_volume": 200.0, "dhw_setpoint": 55.0, "dhw_daily_consumption": 150.0,
                "dhw_min_temperature": 45.0, "dhw_windows": "06:00-08:30, 17:00-22:00",
                "buffer_tank_volume": 300.0,
                "upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 8.0,
                "upper_floor_heat_loss": 0.08, "lower_floor_heat_loss": 0.07})
    if mapped:
        for _a, _t, key, _s in FIELDS.values():
            cfg[key] = f"sensor.{key}"
    return cfg


def run(mapped):
    cfg = config(mapped)
    hass = FakeHass(m.states_for(cfg))
    entry = FakeEntry(data=cfg)
    dt_util.freeze(m.START)
    seen = []
    try:
        asyncio.run(m.integ.async_setup_entry(hass, entry))
        coord = entry.runtime_data
        ctx = getattr(coord, "_ctx", coord)
        if not mapped:
            for name, (attr, _t, _k, sentinel) in FIELDS.items():
                if sentinel is not None:
                    setattr(ctx._current_state, attr, sentinel)
        real_snap = coord._solve_snapshot
        last = {"res": None}

        def snap():
            state, opt = real_snap()
            prev = last["res"]
            if ADVANCE and prev is not None and not mapped:
                for attr, traj, _k, _s in FIELDS.values():
                    t = getattr(prev, traj, None) or []
                    if len(t) > 4:
                        setattr(state, attr, float(t[4]))
            seen.append({n: float(getattr(state, a)) for n, (a, _t, _k, _s) in FIELDS.items()})
            return state, opt

        coord._solve_snapshot = snap
        preds = []
        enabled = {}
        for h in range(HOURS):
            dt_util.freeze(m.START + timedelta(hours=h))
            prev = last["res"]
            pred = {}
            for n, (attr, traj, key, _s) in FIELDS.items():
                t = (getattr(prev, traj, None) or []) if prev is not None else []
                pred[n] = float(t[4]) if len(t) > 4 else None
                if mapped and pred[n] is not None:
                    val = pred[n] - 1.0 if n == "slab" else pred[n]
                    hass.states.set(f"sensor.{key}", FakeState(f"{val:.2f}", unit="°C"))
            asyncio.run(coord.async_refresh())
            last["res"] = coord._optimization_result
            preds.append(pred)
            for n, (_a, traj, _k, _s) in FIELDS.items():
                enabled[n] = enabled.get(n, False) or bool(getattr(last["res"], traj, None))
    finally:
        dt_util.freeze(None)
    out = {}
    for n in FIELDS:
        vals = [s[n] for s in seen]
        far = sum(1 for s, p in zip(seen, preds) if p[n] is not None and abs(s[n] - p[n]) > 1.0)
        with_pred = sum(1 for p in preds if p[n] is not None)
        frozen = int(len(set(round(v, 4) for v in vals)) == 1 and with_pred > 0 and far * 2 >= with_pred)
        out[n] = {"modelled": enabled.get(n, False), "distinct": len(set(round(v, 4) for v in vals)),
                  "first": round(vals[0], 2) if vals else None, "far_gt1K": far, "cycles_with_pred": with_pred,
                  "frozen": frozen}
    return out


def main():
    t0, tt0 = time.process_time(), time.thread_time()
    for arm, mapped in (("omitted", False), ("mapped", True)):
        r = run(mapped)
        for n, d in r.items():
            print(f"FIELD arm={arm} {n}: {d}")
            print(f"RESULT {arm}_{n}_frozen={d['frozen']} flag")
        print(f"RESULT {arm}_frozen_fields={sum(d['frozen'] for d in r.values())} count")
    pc, tc = time.process_time() - t0, time.thread_time() - tt0
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
    except Exception:  # noqa: BLE001
        sw = "na"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
