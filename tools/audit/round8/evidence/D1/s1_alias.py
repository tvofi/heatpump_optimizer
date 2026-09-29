"""D1 s1: executor-boundary aliasing census (round 8, baseline cdf82daa, 4-vCPU cloud container).

Metric: number of mutable objects (ndarray / list / dict / dataclass instance)
handed to the solve thread by coordinator._run_in_process -- the job the
executor thread pickles into the process worker -- that are the SAME object as,
or share ndarray memory with, an object reachable from the live coordinator
(coord.__dict__, coord._ctx fields, and one attribute level below each), counted
at the instant the executor thread starts the job, across the scheduled cycle's
optimize + every shadow solve in that cycle, for 3 configurations.
Count key: identity / np.shares_memory of what production passes to the thread.

Command (tree root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D1/s1_alias.py [--perturb]
--perturb: harness-side equivalent of the one-line production edit in
coordinator.py:_solve_snapshot `state = copy.deepcopy(ctx._current_state)` ->
`state = ctx._current_state` (restored in finally); aliases must go UP (>=1 per job).
Expected baseline: aliased_objects=0 (exact).
Instrumented: heatpump_optimizer.coordinator:_run_in_process, :HeatPumpOptimizerCoordinator._solve_snapshot.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import copy  # noqa: E402
import dataclasses  # noqa: E402
import sys  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402

sys.path.insert(0, "tools/audit/round8/D1")
from s1_realloop import (  # noqa: E402
    RealEntry, RealLoopHass, base_config, base_states, load1, swapins,
)

import heatpump_optimizer as integration  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402

PERTURB = "--perturb" in sys.argv
MUTABLE = (np.ndarray, list, dict, set)

CONFIGS = {
    "base": {},
    "fuse_manual_pv": {
        "fuse_guard_enabled": True, "main_fuse_amperes": 16,
        "pv_enabled": True, "pv_peak_kw": 8.0, "away_enabled": True,
        "peak_tariff_enabled": True, "peak_tariff_price_per_kw": 45.0,
    },
    "two_zone": {
        "upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 8.0,
        "upper_floor_heat_loss": 0.08, "lower_floor_heat_loss": 0.07,
    },
}


def _is_mut(o):
    return isinstance(o, MUTABLE) or (dataclasses.is_dataclass(o) and not isinstance(o, type))


def live_objects(coord):
    out = []
    roots = list(vars(coord).items())
    ctx = getattr(coord, "_ctx", None)
    if ctx is not None:
        roots += [(f"_ctx.{f.name}", getattr(ctx, f.name)) for f in dataclasses.fields(ctx)]
    for name, v in roots:
        if _is_mut(v):
            out.append((name, v))
        d = getattr(v, "__dict__", None)
        if isinstance(d, dict) and not isinstance(v, type):
            for k2, v2 in d.items():
                if _is_mut(v2):
                    out.append((f"{name}.{k2}", v2))
    return out


def job_objects(args):
    out = []

    def add(label, o, depth=0):
        if _is_mut(o):
            out.append((label, o))
        if depth >= 2:
            return
        if isinstance(o, (list, tuple)) and not isinstance(o, np.ndarray):
            for i, x in enumerate(o[:64]):
                add(f"{label}[{i}]", x, depth + 1)
        elif isinstance(o, dict):
            for k, x in list(o.items())[:64]:
                add(f"{label}.{k}", x, depth + 1)
        elif hasattr(o, "__dict__") and not isinstance(o, type):
            for k, x in vars(o).items():
                add(f"{label}.{k}", x, depth + 1)
    add("args", args)
    return out


def aliases(job, live):
    hits = []
    for jl, jo in job:
        for ll, lo in live:
            same = jo is lo
            if not same and isinstance(jo, np.ndarray) and isinstance(lo, np.ndarray):
                try:
                    same = np.shares_memory(jo, lo)
                except Exception:  # noqa: BLE001
                    same = False
            if same:
                hits.append((jl, ll))
                break
    return hits


async def wait_for(pred, timeout):
    t0 = time.monotonic()
    while not pred():
        if time.monotonic() - t0 > timeout:
            return False
        await asyncio.sleep(0.02)
    return True


async def run_config(name, extra):
    current = {}
    records = []
    orig_run = cm._run_in_process

    def hooked(fn, a):
        coord = current.get("c")
        if coord is not None:
            live = live_objects(coord)
            job = job_objects(a)
            records.append((getattr(fn, "__name__", "?"), len(job), aliases(job, live)))
        return orig_run(fn, a)

    orig_snap = cm.HeatPumpOptimizerCoordinator._solve_snapshot

    def snap_perturbed(self):
        state, opt = orig_snap(self)
        return self._ctx._current_state, opt  # the one-line edit's effect

    cm._run_in_process = hooked
    if PERTURB:
        cm.HeatPumpOptimizerCoordinator._solve_snapshot = snap_perturbed
    try:
        hass = RealLoopHass(base_states())
        hass.config_entries.integration = integration
        entry = RealEntry(data={**base_config(const), **extra}, entry_id=f"e_{name}")
        hass.config_entries.entries.append(entry)
        await integration.async_setup(hass, {})
        await hass.config_entries.async_setup(entry.entry_id)
        coord = entry.runtime_data
        current["c"] = coord
        await wait_for(lambda: coord._optimization_result is not None, 240)
        await wait_for(lambda: not coord._optimization_running, 240)
        await coord.async_refresh()
        # a what-if solve as the card issues it
        try:
            await coord.async_simulate({"target_temp": 20.0})

        except Exception as err:  # noqa: BLE001
            print("  simulate skipped:", err)
        await hass.config_entries.async_unload(entry.entry_id)
        hass.executor.shutdown(wait=True)
    finally:
        cm._run_in_process = orig_run
        cm.HeatPumpOptimizerCoordinator._solve_snapshot = orig_snap
    return records


async def main():
    total_jobs = total_alias = 0
    try:
        for name, extra in CONFIGS.items():
            recs = await run_config(name, extra)
            for fn, n, hits in recs:
                print(f"  {name}: job={fn} objects={n} aliases={hits[:4]}")
                total_jobs += 1
                total_alias += len(hits)
    finally:
        cm._shutdown_process_pool()
    return {"jobs_inspected": total_jobs, "aliased_objects": total_alias}


if __name__ == "__main__":
    t_cpu, t_thr = time.process_time(), time.thread_time()
    out = asyncio.run(main())
    for k, v in out.items():
        print(f"RESULT {k}={v} count")
    pc, tc = time.process_time() - t_cpu, time.thread_time() - t_thr
    print(f"RESULT thread_factor={pc / tc if tc else float('nan'):.3f}")
    print(f"RESULT load1={load1()}")
    print(f"RESULT swapins={swapins()}")
    print(f"RESULT perturbed={int(PERTURB)}")
