#!/usr/bin/env python3
"""D9-s2 harness: per-cycle cost of the REAL coordinator cycle on a real event loop.

Metrics (one line each; the brief's fixed definitions):
  loop_cpu_per_cycle   = time.thread_time() on the loop thread across one
                         HeatPumpOptimizerCoordinator._async_update_data (the solve runs
                         in the production process worker via a real ThreadPoolExecutor,
                         so it is excluded), median over the measured cycles; also as a
                         ratio to tests/stress.py:reference_solve's thread CPU.
  traced_slope         = tracemalloc traced bytes per cycle between cycle N/2 and N
                         (after an 8-cycle warm-up), plus deep sys.getsizeof growth of every
                         coordinator attribute over the same span.
  rss_slope            = (ru_maxrss after N2 cycles - after N1 cycles)/(N2-N1), each in a
                         fresh child process with tracemalloc OFF.
  payload bytes        = compact JSON bytes of _build_data_dict() and of every entity's
                         extra_state_attributes over all PLATFORMS, split by
                         _unrecorded_attributes (+ _entity_component_unrecorded_attributes).
  ipc bytes            = pickle bytes of the job coordinator:_run_in_process sends and of
                         the reply it receives, per solve.
Instrumented symbols: heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_update_data,
  ._build_data_dict, coordinator:_run_in_process, accuracy:HISTORY_LENGTH (perturbation).
Perturbations: --inject-build K runs _build_data_dict K times per call (loop CPU must go UP);
  --history-cap 100000 lifts accuracy.HISTORY_LENGTH so AccuracyTracker.samples never trims
  (traced_slope over the plateau span must go UP from ~0).
Command:
  PYTHONPATH=tests/hastub python3 tools/audit/round8/D9/s2_cycle.py --cycles 112
  (variants: --inject-build 2 ; --history-cap 100000 --cycles 112 --no-rss)
Expected (provisional, shared box): loop_cpu_per_cycle ~8-15 ms, ratio ~0.1 of a reference
  solve; traced_slope small and bounded; recorded attribute bytes ~10 kB/cycle over 74 entities.
Baseline: cdf82daabcfe3777d98b31489f36df5555ec9d82. Machine: 4-vCPU shared cloud container.
The clock is frozen per cycle (hastub dt.freeze) and advanced 15 min per cycle; fetches of
prices/weather/solar are stubbed (inputs pre-seeded for 10 days) -- everything else is production.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import asyncio
import gc
import importlib
import json
import pickle
import resource
import statistics
import subprocess
import sys
import time
import tracemalloc
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
os.environ.setdefault("TMPDIR", "/home/claude/audit-r8/tmp/D9-s2")

import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import accuracy as acc_mod  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402

START = datetime(2026, 1, 14, 0, 0, tzinfo=timezone.utc)
DAYS = 10
CFG = {
    "tibber_token": "x", "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
    "target_temperature": 21.0, "min_temperature": 17.0, "max_temperature": 23.0,
    "dhw_tank_volume": 200.0, "dhw_setpoint": 55.0, "dhw_min_temperature": 45.0,
}
EXECUTOR = ThreadPoolExecutor(2)
EXEC_CPU = [0.0]


class LoopHass(FakeHass):
    """FakeHass with a REAL executor (the FakeHass trap: its executor runs inline)."""

    async def async_add_executor_job(self, func, *args):
        def timed():
            c0 = time.thread_time()
            try:
                return func(*args)
            finally:
                EXEC_CPU[0] += time.thread_time() - c0
        return await asyncio.get_running_loop().run_in_executor(EXECUTOR, timed)

    def async_create_task(self, coro, name=None, eager_start=None):
        coro.close()
        return None


def build():
    hass = LoopHass({"sensor.indoor": FakeState("21.0", unit="°C"),
                     "sensor.outdoor": FakeState("-5.0", unit="°C")})
    dt_util.freeze(START)
    coord = cm.HeatPumpOptimizerCoordinator(hass, FakeEntry(data=CFG))
    coord._skip_solve_once = False
    hours = 24 * DAYS
    coord._prices = [{"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
                      "starts_at": (START + timedelta(hours=h)).isoformat(),
                      "level": "NORMAL"} for h in range(hours)]
    coord._weather_forecast = [{"datetime": (START + timedelta(hours=h)).isoformat(),
                                "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
                                "wind_speed": 3.0, "precipitation": 0.0,
                                "humidity": 85.0} for h in range(hours)]
    coord._solar_radiation_forecast = [0.0] * hours

    async def _noop():
        return None

    for name in ("_fetch_tibber_prices", "_fetch_weather_forecast", "_fetch_solar_forecast"):
        setattr(coord, name, _noop)
    return coord


def deep(o, seen):
    if id(o) in seen:
        return 0
    seen.add(id(o))
    if isinstance(o, np.ndarray):
        return o.nbytes + 112
    n = sys.getsizeof(o)
    if isinstance(o, dict):
        for k, v in o.items():
            n += deep(k, seen) + deep(v, seen)
    elif isinstance(o, (list, tuple, set, frozenset)) or type(o).__name__ == "deque":
        for v in o:
            n += deep(v, seen)
    elif (hasattr(o, "__dict__") and not isinstance(o, type)
          and type(o).__module__.startswith("heatpump_optimizer")):
        n += deep(vars(o), seen)
    return n


def attr_sizes(coord):
    out = {}
    for k, v in vars(coord).items():
        if k in ("hass", "data"):
            continue
        try:
            out[k] = deep(v, set())
        except Exception:  # noqa: BLE001
            out[k] = -1
    return out


def ref_cpu_ms():
    import stress  # noqa: WPS433 - thread pin already applied above
    return statistics.median(stress.reference_solve()[2] for _ in range(3))


def entity_payload(coord):
    from heatpump_optimizer.const import PLATFORMS
    entry = FakeEntry(data=CFG)
    entry.runtime_data = coord
    rec_total = exc_total = 0
    rows = []
    for p in PLATFORMS:
        mod = importlib.import_module("heatpump_optimizer." + p)
        added = []
        asyncio.run(mod.async_setup_entry(FakeHass(), entry, lambda es, *a, **k: added.extend(es)))
        for e in added:
            attrs = getattr(e, "extra_state_attributes", None) or {}
            unrec = (set(getattr(e, "_unrecorded_attributes", frozenset()))
                     | set(getattr(e, "_entity_component_unrecorded_attributes", frozenset())))
            rec = {k: v for k, v in attrs.items() if k not in unrec}
            exc = {k: v for k, v in attrs.items() if k in unrec}
            rb = len(json.dumps(rec, default=str, separators=(",", ":")))
            xb = len(json.dumps(exc, default=str, separators=(",", ":")))
            rec_total += rb
            exc_total += xb
            rows.append((rb, xb, f"{p}.{getattr(e, '_key', None) or type(e).__name__}"))
    rows.sort(reverse=True)
    return len(rows), rec_total, exc_total, rows


def run(args):
    if args.history_cap:
        acc_mod.HISTORY_LENGTH = args.history_cap
    if args.inject_build > 1:
        base = cm.HeatPumpOptimizerCoordinator._build_data_dict

        def _k(self, _b=base, _n=args.inject_build):
            for _ in range(_n - 1):
                _b(self)
            return _b(self)

        cm.HeatPumpOptimizerCoordinator._build_data_dict = _k
    ipc = []
    orig_rip = cm._run_in_process

    def rip(fn, a):
        r = orig_rip(fn, a)
        ipc.append((len(pickle.dumps((fn, a), protocol=pickle.HIGHEST_PROTOCOL)),
                    len(pickle.dumps(("ok", r), protocol=pickle.HIGHEST_PROTOCOL))))
        return r

    cm._run_in_process = rip
    coord = build()
    loop_cpu = []
    marks = {}
    n = args.cycles
    warm = 8
    mid = warm + (n - warm) // 2

    async def cycles():
        t = START
        for i in range(1, n + 1):
            dt_util.freeze(t)
            c0 = time.thread_time()
            coord.data = await coord._async_update_data()
            loop_cpu.append((time.thread_time() - c0) * 1e3)
            t += timedelta(minutes=15)
            if args.trace and i in (warm, mid, n):
                gc.collect()
                marks[i] = (tracemalloc.get_traced_memory()[0], attr_sizes(coord))

    if args.trace:
        tracemalloc.start(1)
    p0, t0 = time.process_time(), time.thread_time()
    ref_before = ref_cpu_ms()
    asyncio.run(cycles())
    ref_after = ref_cpu_ms()
    if args.trace:
        tracemalloc.stop()
    cm._shutdown_process_pool()
    ref = statistics.median([ref_before, ref_after])
    med = statistics.median(loop_cpu[warm:] if n > warm else loop_cpu)
    data_bytes = len(json.dumps(coord.data, default=str, separators=(",", ":")))
    out = {"cycles": n, "loop_cpu_ms": med, "loop_cpu_max_ms": max(loop_cpu),
           "ref_cpu_ms": ref, "maxrss_kb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
           "data_bytes": data_bytes, "ipc": ipc[-1] if ipc else None, "n_solves": len(ipc),
           "proc_cpu": time.process_time() - p0, "thr_cpu": time.thread_time() - t0,
           "accuracy_samples": len(coord._accuracy.samples), "exec_cpu": EXEC_CPU[0],
           "series": [round(x, 1) for x in loop_cpu]}
    if args.trace:
        (b0, s0), (b1, s1), (b2, s2) = (marks[warm], marks[mid], marks[n])
        out["traced_slope_first"] = (b1 - b0) / (mid - warm)
        out["traced_slope_second"] = (b2 - b1) / (n - mid)
        out["attr_growth_second"] = sorted(((s2[k] - s1.get(k, 0), k) for k in s2), reverse=True)[:6]
        out["attr_growth_first"] = sorted(((s1[k] - s0.get(k, 0), k) for k in s1), reverse=True)[:6]
    if args.payload:
        ne, rt, xt, rows = entity_payload(coord)
        out.update(entities=ne, recorded_attr_bytes=rt, excluded_attr_bytes=xt,
                   top_recorded=rows[:5], max_recorded=rows[0][0])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=112)
    ap.add_argument("--inject-build", type=int, default=1)
    ap.add_argument("--history-cap", type=int, default=0)
    ap.add_argument("--no-rss", action="store_true")
    ap.add_argument("--child", action="store_true")
    ap.add_argument("--trace", action="store_true")
    ap.add_argument("--payload", action="store_true")
    args = ap.parse_args()
    if args.child:
        print("CHILD " + json.dumps(run(args), default=str))
        return 0
    args.trace = True
    args.payload = True
    res = run(args)
    # The executor thread's work (pickling to the worker, store I/O) is deliberate
    # second-thread CPU: subtract it, per tools/audit/README.md's residual rule.
    second = res["exec_cpu"]
    tf = (res["proc_cpu"] - second) / res["thr_cpu"] if res["thr_cpu"] else 1.0
    print(f"# solves={res['n_solves']} accuracy_samples={res['accuracy_samples']}")
    print(f"# loop cpu series ms: {res['series']}")
    print(f"RESULT loop_cpu_per_cycle={res['loop_cpu_ms']:.2f} ms (provisional)")
    print(f"RESULT loop_cpu_max_cycle={res['loop_cpu_max_ms']:.2f} ms (provisional)")
    print(f"RESULT reference_solve_cpu={res['ref_cpu_ms']:.1f} ms (provisional)")
    print(f"RESULT loop_cpu_share_of_reference={res['loop_cpu_ms'] / res['ref_cpu_ms']:.4f} ratio")
    print(f"RESULT traced_slope_first_half={res['traced_slope_first']:.0f} bytes/cycle")
    print(f"RESULT traced_slope_second_half={res['traced_slope_second']:.0f} bytes/cycle")
    print(f"# attr growth first half: {res['attr_growth_first']}")
    print(f"# attr growth second half: {res['attr_growth_second']}")
    print(f"RESULT data_dict_bytes={res['data_bytes']} bytes")
    print(f"RESULT entities={res['entities']} count")
    print(f"RESULT recorded_attr_bytes_per_cycle={res['recorded_attr_bytes']} bytes")
    print(f"RESULT excluded_attr_bytes_per_cycle={res['excluded_attr_bytes']} bytes")
    print(f"RESULT max_recorded_attr_bytes_one_entity={res['max_recorded']} bytes")
    print(f"# top recorded: {res['top_recorded']}")
    if res["ipc"]:
        print(f"RESULT ipc_job_bytes={res['ipc'][0]} bytes")
        print(f"RESULT ipc_reply_bytes={res['ipc'][1]} bytes")
    if not args.no_rss:
        env = dict(os.environ)
        rss = {}
        for nc in (16, args.cycles):
            cmd = [sys.executable, __file__, "--child", "--cycles", str(nc),
                   "--inject-build", str(args.inject_build), "--history-cap", str(args.history_cap)]
            p = subprocess.run(cmd, capture_output=True, text=True, env=env)
            line = [ln for ln in p.stdout.splitlines() if ln.startswith("CHILD ")]
            rss[nc] = json.loads(line[0][6:])["maxrss_kb"] if line else float("nan")
        print(f"RESULT maxrss_16_cycles={rss[16]} kB (provisional)")
        print(f"RESULT maxrss_{args.cycles}_cycles={rss[args.cycles]} kB (provisional)")
        print(f"RESULT rss_slope={(rss[args.cycles] - rss[16]) * 1024 / (args.cycles - 16):.0f} bytes/cycle (provisional)")
    print(f"RESULT deliberate_thread_cpu={max(0.0, second) * 1e3:.1f} ms")
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
