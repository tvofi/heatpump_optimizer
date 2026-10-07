"""D1.M6 consequence: a finite-but-absurd value in a weather.get_forecasts row
reaches the real solve through ``coordinator._fetch_weather_forecast`` /
``_forecast_arrays``. How long does the cycle's solve then take?

Metric (one line): wall seconds of one real ``_async_update_data`` cycle
(real process-worker solve) per case, and its ratio to the healthy-forecast
cycle measured in the same session (``ratio_<case>``); a case still running
at --cap seconds is recorded at the cap (``capped=1``).
Count key: the production cycle's own completion, timed around
``_async_update_data``; each case runs in a fresh interpreter so a runaway
solve is killed by the cap rather than wedging the harness.

Command (from the export root):
    PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python \
        tools/audit/round9/D1/s2/solve_poison.py [--cap 60] [--perturb clip]
Expected at baseline: ratio_healthy=1; see RESULT lines. Wall/ratio numbers
provisional (re-take on a quiet box); the capped flag is load-robust.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: B4.

Perturbation ``clip``: the forecast rows are bounded where they are stored
(``_forecast_in_model_units`` wrapped in memory to clip temperature to
[-60, 60] degC, wind to [0, 60] m/s, precipitation to [0, 200] mm); the
poisoned cases' ratio must fall to ~1 and capped to 0.
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")

import argparse
import json
import subprocess
import sys
import time

CASES = {
    "healthy": [],
    "temp_minus_1e308_one_row": [(3, "temperature", -1e308)],
    "temp_plus_1e308_8_rows": [(i, "temperature", 1e308) for i in range(8)],
    "temp_minus_300_one_row": [(3, "temperature", -300.0)],
    "wind_1e308_one_row": [(2, "wind_speed", 1e308)],
    "rain_minus_1e6_one_row": [(2, "precipitation", -1e6)],
    "wind_500_one_row": [(2, "wind_speed", 500.0)],
    "wind_1e6_one_row": [(2, "wind_speed", 1e6)],
    "wind_1e12_one_row": [(2, "wind_speed", 1e12)],
    "wind_1e20_one_row": [(2, "wind_speed", 1e20)],
}


def child(case, perturb):
    import asyncio
    import logging
    from unittest import mock
    sys.argv = ["x"]
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import parsers as P
    from harness import FakeEntry, FakeHass
    logging.basicConfig(level=logging.CRITICAL)
    fc = P.healthy_forecast()
    for i, k, v in CASES[case]:
        fc[i][k] = v
    hass = FakeHass(P._states())

    async def h(call):
        return {"weather.home": {"forecast": fc}}
    hass.services.async_register("weather", "get_forecasts", h)
    patches = []
    if perturb == "clip":
        orig = P.cm._forecast_in_model_units

        def clipped(state, forecast):
            rows = orig(state, forecast)
            out = []
            for r in rows:
                r = dict(r)
                for key, lo, hi in (("temperature", -60, 60), ("wind_speed", 0, 60),
                                    ("precipitation", 0, 200)):
                    v = r.get(key)
                    if isinstance(v, (int, float)) and not isinstance(v, bool):
                        r[key] = min(max(float(v), lo), hi)
                out.append(r)
            return out
        patches.append(mock.patch.object(P.cm, "_forecast_in_model_units", clipped))
    for p in patches:
        p.start()
    c = P.cm.HeatPumpOptimizerCoordinator(hass, FakeEntry(data=dict(P.CFG)))
    t0 = time.monotonic()
    ok = True
    try:
        asyncio.run(c._async_update_data())
    except Exception:  # noqa: BLE001
        ok = False
    wall = time.monotonic() - t0
    r = c._optimization_result
    P.cm._shutdown_process_pool()
    print(json.dumps({"wall": wall, "ok": ok, "planned": r is not None,
                      "status": getattr(r, "status", None)}), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=float, default=60.0)
    ap.add_argument("--perturb", default="")
    ap.add_argument("--child", default="")
    ap.add_argument("--only", action="append")
    args = ap.parse_args()
    if args.child:
        child(args.child, args.perturb)
        return
    res = {}
    for case in (["healthy"] + [c for c in args.only if c != "healthy"] if args.only else CASES):
        cmd = [sys.executable, __file__, "--child", case, "--perturb", args.perturb]
        t0 = time.monotonic()
        # own session, so the cap kills the solve worker grandchild too
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                env=os.environ, start_new_session=True)
        try:
            out, _ = proc.communicate(timeout=args.cap)
            line = [l for l in out.decode().splitlines() if l.startswith("{")][-1]
            res[case] = {**json.loads(line), "capped": 0}
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, 9)
            proc.wait()
            res[case] = {"wall": time.monotonic() - t0, "ok": None, "planned": None,
                         "status": None, "capped": 1}
    base = res["healthy"]["wall"]
    for case, r in res.items():
        print(f"RESULT {case}.wall_s={r['wall']:.2f} s provisional capped={r['capped']} "
              f"cycle_ok={r['ok']} status={r['status']}")
        print(f"RESULT ratio_{case}={r['wall'] / base:.1f} ratio provisional")
    print(f"RESULT capped_cases={sum(r['capped'] for r in res.values())} of {len(res)}")
    print("RESULT thread_factor=1.000 (solve runs in the worker process)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")]
        print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")
    except OSError:
        print("RESULT swapins=0")


if __name__ == "__main__":
    main()
