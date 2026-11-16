"""D9-s1 gil_hold / loop_thread_work: model work a steady what-if runs ON the
event loop thread (whatif.schedule_days -> HeatPumpOptimizer.reference_day).

Metric: per async_simulate(steady=True) call, (a) ThermalModel.simulate_step
calls made on the loop thread, (b) time.thread_time() on the loop thread
inside whatif.schedule_days (one synchronous call: the loop runs nothing
else meanwhile, so it is a contiguous loop block), and (c) the longest gap of
a 1 ms heartbeat on the same real asyncio loop across the whole what-if,
the solves on the SHIPPED route (real process worker), so the gap is the
loop's own work, not a solve's GIL. Keyed on calls/CPU on the loop thread
(threading.get_ident() of the loop), never on the inputs.

Command (from the export root):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
        dev/audit/rounds/round11/D9/s1/h_whatif_loop_block.py

Cells: fuse what-if (power_cap_kw, the cycle's background caller), card
target_temp what-if, card comfort day/night what-if, card weekend-comfort
what-if, card holiday-comfort what-if -- on the two-zone DHW house; and the
card target_temp what-if on a single-zone house.
Perturbation (in memory): whatif.schedule_days replaced by a twin that runs
both reference_day calls through coordinator._await_off_loop (the worker)
-> loop simulate_step calls must go TO ZERO and the schedule_days loop CPU
DOWN; second lever: distinct day types (weekend comfort set) -> UP.
Null control: async_simulate(steady=False) (the degree tiles' call) ->
0 loop simulate_step.
Pi: x F (5, an assumption). CPU/wall provisional; call counts exact.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B1 container.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import statistics  # noqa: E402
import sys  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402
from datetime import timedelta  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d9s1lib as L  # noqa: E402

F_PI = 5.0
REPS = 3

CELLS = {
    "fuse_cap": ({"power_cap_kw": 3.5}, True),
    "card_target": ({"target_temp": 20.0}, True),
    "card_daynight": ({"comfort_temp_day": 21.5, "comfort_temp_night": 18.5}, True),
    "card_weekend": ({"comfort_temp_day_weekend": 22.0, "comfort_temp_night_weekend": 20.0}, True),
    "card_holiday": ({"holiday_comfort_day": 22.5, "holiday_comfort_night": 20.5}, True),
    "null_steady_false": ({"target_temp": 20.0}, False),
}


async def heartbeat(stop, stamps):
    while not stop.is_set():
        stamps.append(time.perf_counter())
        await asyncio.sleep(0.001)


async def run_house(house_kw, cells, perturb=False):
    from heatpump_optimizer import coordinator as cm
    from heatpump_optimizer import thermal_model as tm
    from heatpump_optimizer import whatif
    from homeassistant.util import dt as dtu
    from profiles import house

    loop = asyncio.get_running_loop()
    loop_id = threading.get_ident()
    pool = ThreadPoolExecutor(max_workers=4)
    hass = L.make_loop_hass(loop, pool)
    dtu.freeze(L.CYCLE_NOW)
    coord = L.make_coordinator(hass, dict(house(**house_kw)), entry_id=f"wl_{len(house_kw)}_{perturb}")
    for i in range(2):
        now = L.CYCLE_NOW + timedelta(minutes=30 * i)
        dtu.freeze(now)
        L.feed(coord, now)
        coord.data = await coord._async_update_data()
    cnt = {"steps": 0}
    real_step = tm.ThermalModel.simulate_step

    def step(self, *a, **k):
        if threading.get_ident() == loop_id:
            cnt["steps"] += 1
        return real_step(self, *a, **k)

    tm.ThermalModel.simulate_step = step
    sd_cpu = []
    real_sd = whatif.schedule_days

    sd_wall = []

    def timed_sd(live, sim):
        t = time.thread_time()
        w = time.perf_counter()
        try:
            return real_sd(live, sim)
        finally:
            if threading.get_ident() == loop_id:
                sd_cpu.append(time.thread_time() - t)
                sd_wall.append(time.perf_counter() - w)

    whatif.schedule_days = timed_sd
    if perturb:
        # the twin: both reference_day calls off the loop, in the worker
        from heatpump_optimizer.optimizer import HeatPumpOptimizer
        offloaded = {}

        async def pre(pairs):
            out = []
            for o, i in pairs:
                out.append(await cm._await_off_loop(hass, HeatPumpOptimizer.reference_day, o, i))
            return out

        def off_sd(live, sim):
            (lt, lk), (st, sk) = offloaded.pop("v")
            return None if lt == st else (lk, sk)

        whatif.schedule_days = off_sd
    rows = {}
    try:
        for name, (ov, steady) in cells.items():
            res = []
            for r in range(REPS):
                now = L.CYCLE_NOW + timedelta(minutes=31, seconds=10 * (r + 1) + 100 * len(rows))
                dtu.freeze(now)
                whatif.state_for(coord).live_steady = None
                if perturb:
                    # compute the pair off the loop first, as the fixed code would
                    horizon = coord._forecast_arrays(now)
                    config, params, state = coord._solve_hubs(len(horizon.prices), banded=False)
                    from heatpump_optimizer.plan_step import plan_step_start
                    solve_at = plan_step_start(now)
                    a = coord._whatif_solve({}, config, params, state, horizon, solve_at, False)[:2]
                    b = coord._whatif_solve(ov, config, params, state, horizon, solve_at, False)[:2]
                    offloaded["v"] = await pre([a, b])
                c0 = cnt["steps"]
                n0 = len(sd_cpu)
                stop = asyncio.Event()
                stamps: list = []
                hb = asyncio.create_task(heartbeat(stop, stamps))
                await asyncio.sleep(0.02)
                t0 = time.perf_counter()
                await coord.async_simulate(dict(ov), limited=False, steady=steady)
                t1 = time.perf_counter()
                # let the heartbeat stamp once more: a block at the very end of
                # the what-if (schedule_days is its last synchronous step) is
                # only seen as a gap if the stamp after it is in the window
                await asyncio.sleep(0.003)
                stop.set()
                await hb
                after = [s for s in stamps if s > t1]
                win = [s for s in stamps if t0 <= s <= t1] + after[:1]
                gaps = [b - a for a, b in zip(win, win[1:])]
                res.append({"steps": cnt["steps"] - c0,
                            "sd_ms": sum(sd_cpu[n0:]) * 1e3,
                            "sd_wall_ms": sum(sd_wall[n0:]) * 1e3,
                            "gap_ms": max(gaps) * 1e3 if gaps else 0.0})
            rows[name] = res
    finally:
        tm.ThermalModel.simulate_step = real_step
        whatif.schedule_days = real_sd
        cm._shutdown_process_pool()
        pool.shutdown()
    return rows


def main():
    swap0 = L.swapins()
    L.result("load1_start", L.load1(), "1")
    out = {}
    for hk, cells, tag in (({"two_zone": True, "dhw": True}, CELLS, "two_zone_dhw"),
                           ({"two_zone": False, "dhw": True},
                            {"card_target": CELLS["card_target"]}, "single_zone_dhw")):
        rows = asyncio.run(run_house(hk, cells))
        for name, res in rows.items():
            key = f"{tag}.{name}"
            out[key] = res
            L.result(f"{key}.loop_simulate_step_calls", res[0]["steps"], "count")
            L.result(f"{key}.schedule_days_loop_cpu_ms_median",
                     statistics.median(r["sd_ms"] for r in res), "ms")
            L.result(f"{key}.schedule_days_loop_cpu_ms_max", max(r["sd_ms"] for r in res), "ms")
            L.result(f"{key}.schedule_days_pi_ms_median",
                     statistics.median(r["sd_ms"] for r in res) * F_PI, "ms")
            L.result(f"{key}.schedule_days_loop_wall_ms_median",
                     statistics.median(r["sd_wall_ms"] for r in res), "ms")
            L.result(f"{key}.longest_loop_gap_ms_median",
                     statistics.median(r["gap_ms"] for r in res), "ms")
    prow = asyncio.run(run_house({"two_zone": True, "dhw": True},
                                 {k: CELLS[k] for k in ("card_target", "card_weekend")},
                                 perturb=True))
    for name, res in prow.items():
        key = f"perturbed_offloop.two_zone_dhw.{name}"
        L.result(f"{key}.loop_simulate_step_calls", res[0]["steps"], "count")
        L.result(f"{key}.schedule_days_loop_cpu_ms_median",
                 statistics.median(r["sd_ms"] for r in res), "ms")
        L.result(f"{key}.longest_loop_gap_ms_median",
                 statistics.median(r["gap_ms"] for r in res), "ms")
    cells = [statistics.median(r["sd_ms"] for r in v) for k, v in out.items()
             if not k.endswith("null_steady_false")]
    L.result("cells", len(cells), "count")
    L.result("schedule_days_loop_cpu_ms_min", min(cells), "ms")
    L.result("schedule_days_loop_cpu_ms_max", max(cells), "ms")
    L.result("schedule_days_loop_cpu_ms_max_drop1", sorted(cells)[-2], "ms")
    rclock = L.Clock()
    L.result("reference_solve_cpu_ms", L.ref_ms(), "ms")
    L.result("F_assumed", F_PI, "1")
    L.tail(rclock, swap0=swap0)


if __name__ == "__main__":
    main()
