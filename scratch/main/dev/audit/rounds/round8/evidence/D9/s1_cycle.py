"""D9 round 8 seat s1 -- full solves per coordinator cycle by path, and the loop's GIL starvation.

Metrics (brief, fixed):
  * full solves per cycle = entries into optimizer._multi_start_minimize during ONE
    HeatPumpOptimizerCoordinator._async_update_data, split by the coordinator caller that
    submitted the solve through coordinator._await_optimize (main = async_run_optimization,
    whatif = async_simulate reached from _maybe_run_fuse_advisor / _maybe_refresh_price_tile).
  * longest contiguous GIL hold = max gap between 1 ms heartbeat ticks (asyncio.sleep(0.001))
    of a task on a REAL asyncio loop while the solve runs on a real ThreadPoolExecutor
    (hass.async_add_executor_job -> loop.run_in_executor); starvation share = sum of the
    gap time of gaps > 5 ms / the cycle's wall time. Never FakeHass's inline executor.
Routes (--route):
  process : shipped route -- coordinator._run_in_process drives the real process_worker.py
            child; msm entries are counted in the parent only (0 expected), solves counted at
            coordinator._await_optimize.
  inline  : the #511 fallback route (worker unusable -> optimize_in_process on the executor
            thread in THIS interpreter); coordinator._run_in_process is replaced by fn(*args)
            so the solve holds this interpreter's GIL.  msm entries counted directly.
Configs (--config): default (DHW tank, one zone), fuse_tiles (+ main_fuse_amperes=25,
  price_tiles_enabled=True).
Perturbations: --no-gil-yield replaces optimizer._gil_yield with a no-op (max gap must go UP on
  the inline route); --config default vs fuse_tiles moves whatif solves 0 -> 2 on the first cycle.
Command (repo root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 TMPDIR=/home/claude/audit-r8/tmp/D9-s1 \
  python3 tools/audit/round8/D9/s1_cycle.py --route inline --config fuse_tiles
Expected (baseline cdf82da): counts exact; gap/share numbers PROVISIONAL (shared 4-vCPU box).
Count key: _multi_start_minimize entries and _await_optimize submissions delivered by production.
"""
from __future__ import annotations

import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")

import argparse
import asyncio
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

sys.path.insert(0, "tests")
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402

import numpy as np  # noqa: E402,F401
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from heatpump_optimizer import optimizer as om  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

POOL = ThreadPoolExecutor(max_workers=4, thread_name_prefix="hass-exec")


class LoopHass(FakeHass):
    """FakeHass with a REAL executor and real tasks (the GIL trap in tools/audit/README.md)."""

    spawn_real = False

    def async_create_task(self, coro, name=None, eager_start=None):
        if not self.spawn_real:
            coro.close()
            return None
        return asyncio.get_running_loop().create_task(coro)

    async def async_add_executor_job(self, func, *args):
        return await asyncio.get_running_loop().run_in_executor(POOL, _tracked, func, args)


ACTIVE = {"n": 0}


def _tracked(func, args):
    ACTIVE["n"] += 1
    try:
        return func(*args)
    finally:
        ACTIVE["n"] -= 1


def build(config_name: str):
    hass = LoopHass({
        "sensor.indoor": FakeState("21.0", unit="°C"),
        "sensor.outdoor": FakeState("-5.0", unit="°C"),
    })
    data = {
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        "dhw_tank_volume": 180.0,
    }
    if config_name == "fuse_tiles":
        data.update({"main_fuse_amperes": 25, "price_tiles_enabled": True})
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=data))
    hass.spawn_real = True
    coord._skip_solve_once = False
    t0 = dt_util.now().replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
    coord._prices = [
        {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
         "starts_at": (t0 + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
        for h in range(48)
    ]
    coord._weather_forecast = [
        {"datetime": (t0 + timedelta(hours=h)).isoformat(), "temperature": -5.0,
         "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0}
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [0.0] * 48

    async def _noop():
        return None
    for name in ("_fetch_tibber_prices", "_fetch_weather_forecast",
                 "_fetch_solar_forecast", "_async_learn_price_shape"):
        setattr(coord, name, _noop)
    return hass, coord


async def run_cycle(coord, counts, null_seconds=0.0):
    gaps = []
    busy = []
    stop = asyncio.Event()

    async def heartbeat():
        last = time.perf_counter()
        was_busy = ACTIVE["n"] > 0
        while not stop.is_set():
            await asyncio.sleep(0.001)
            now = time.perf_counter()
            gaps.append(now - last)
            # a gap is charged to the executor only if a job was running at both ends
            is_busy = ACTIVE["n"] > 0
            busy.append(was_busy and is_busy)
            was_busy = is_busy
            last = now

    hb = asyncio.get_running_loop().create_task(heartbeat())
    await asyncio.sleep(0.01)
    gaps.clear()
    busy.clear()
    w0 = time.perf_counter()
    loop_cpu0 = time.thread_time()
    if null_seconds:
        await asyncio.sleep(null_seconds)
    else:
        await coord._async_update_data()
    wall = time.perf_counter() - w0
    loop_cpu = time.thread_time() - loop_cpu0
    stop.set()
    await hb
    return gaps, busy, wall, loop_cpu


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--route", choices=("process", "inline"), default="inline")
    ap.add_argument("--config", choices=("default", "fuse_tiles"), default="default")
    ap.add_argument("--cycles", type=int, default=1)
    ap.add_argument("--no-gil-yield", action="store_true")
    ap.add_argument("--null-seconds", type=float, default=0.0,
                    help="NULL CONTROL: heartbeat on an idle loop for this long, no cycle")
    args = ap.parse_args()

    counts = {"msm": {}, "submit": {}}
    label = {"path": "other"}
    saved = []

    def put(obj, name, new):
        saved.append((obj, name, getattr(obj, name)))
        setattr(obj, name, new)

    msm0 = om._multi_start_minimize

    def msm(*a, **k):
        counts["msm"][label["path"]] = counts["msm"].get(label["path"], 0) + 1
        return msm0(*a, **k)

    ao0 = cm._await_optimize

    async def ao(*a, **k):
        caller = sys._getframe(1).f_code.co_name
        path = {"async_run_optimization": "main", "async_simulate": "whatif"}.get(caller, caller)
        counts["submit"][path] = counts["submit"].get(path, 0) + 1
        label["path"] = path
        try:
            return await ao0(*a, **k)
        finally:
            label["path"] = "other"

    worker_cpu = {"s": 0.0}
    rip0 = cm._run_in_process

    def rip_inline(fn, fargs):
        t0 = time.thread_time()
        try:
            return fn(*fargs)
        finally:
            worker_cpu["s"] += time.thread_time() - t0

    put(om, "_multi_start_minimize", msm)
    put(cm, "_await_optimize", ao)
    if args.route == "inline":
        put(cm, "_run_in_process", rip_inline)
    if args.no_gil_yield:
        put(om, "_gil_yield", lambda: None)
    cpu0, th0 = time.process_time(), time.thread_time()
    try:
        hass, coord = build(args.config)
        loop = asyncio.new_event_loop()
        try:
            for c in range(args.cycles):
                counts["msm"].clear()
                counts["submit"].clear()
                gaps, busy, wall, loop_cpu = loop.run_until_complete(
                    run_cycle(coord, counts, args.null_seconds))
                g = np.array(gaps) * 1000.0
                b = np.array(busy, dtype=bool)
                over = g[g > 5.0]
                tag = ("null" if args.null_seconds else args.route) + f".{args.config}.cycle{c}"
                gb = g[b]
                gi = g[~b]
                print(f"RESULT {tag}.executor_busy_wall_ms={gb.sum():.0f} ms-wall (provisional)")
                print(f"RESULT {tag}.max_gap_executor_busy_ms={gb.max() if gb.size else 0:.1f} ms-wall (provisional)")
                print(f"RESULT {tag}.max_gap_executor_idle_ms={gi.max() if gi.size else 0:.1f} ms-wall (provisional)")
                print(f"RESULT {tag}.starvation_share_executor_busy={gb[gb > 5.0].sum() / max(gb.sum(), 1e-9):.4f} ratio (provisional)")
                print(f"RESULT {tag}.starvation_share_executor_idle={gi[gi > 5.0].sum() / max(gi.sum(), 1e-9):.4f} ratio (provisional)")
                print(f"RESULT {tag}.median_gap_executor_busy_ms={np.median(gb) if gb.size else 0:.2f} ms-wall (provisional)")
                print(f"RESULT {tag}.median_gap_executor_idle_ms={np.median(gi) if gi.size else 0:.2f} ms-wall (provisional)")
                print(f"RESULT {tag}.solves_submitted_main={counts['submit'].get('main', 0)} count")
                print(f"RESULT {tag}.solves_submitted_whatif={counts['submit'].get('whatif', 0)} count")
                others = {k: v for k, v in counts['submit'].items() if k not in ('main', 'whatif')}
                print(f"RESULT {tag}.solves_submitted_other={sum(others.values())} count {others}")
                for p in sorted(set(counts["msm"]) | {"main", "whatif"}):
                    print(f"RESULT {tag}.msm_entries_{p}={counts['msm'].get(p, 0)} count")
                print(f"RESULT {tag}.plan_status={getattr(coord._optimization_result, 'status', None)!r}")
                print(f"RESULT {tag}.heartbeat_ticks={g.size} count")
                print(f"RESULT {tag}.max_gap_ms={g.max() if g.size else float('nan'):.1f} ms-wall (provisional)")
                print(f"RESULT {tag}.p99_gap_ms={np.percentile(g, 99) if g.size else float('nan'):.1f} ms-wall (provisional)")
                print(f"RESULT {tag}.gaps_over_5ms={over.size} count (provisional)")
                print(f"RESULT {tag}.starvation_share={over.sum() / max(wall * 1000.0, 1e-9):.4f} ratio (provisional)")
                print(f"RESULT {tag}.cycle_wall_ms={wall * 1000:.0f} ms-wall (provisional)")
                print(f"RESULT {tag}.loop_thread_cpu_ms={loop_cpu * 1000:.0f} ms-cpu (provisional)")
        finally:
            loop.run_until_complete(asyncio.sleep(0))
            loop.close()
            cm._shutdown_process_pool()
    finally:
        for obj, name, val in reversed(saved):
            setattr(obj, name, val)
        POOL.shutdown(wait=True)
    cpu, th = time.process_time() - cpu0, time.thread_time() - th0
    # The executor thread's solve CPU is deliberate second-thread work (README): subtract it.
    print(f"RESULT deliberate_executor_cpu_ms={worker_cpu['s'] * 1000:.0f} ms-cpu")
    print(f"RESULT thread_factor={(cpu - worker_cpu['s']) / max(th, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT active_threads_end={threading.active_count()}")
    try:
        with open("/proc/vmstat") as fh:
            sw = [ln.split()[1] for ln in fh if ln.startswith("pswpin")]
        print(f"RESULT swapins={sw[0] if sw else 0}")
    except OSError:
        print("RESULT swapins=0")


if __name__ == "__main__":
    main()
