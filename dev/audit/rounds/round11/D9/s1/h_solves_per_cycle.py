"""D9-s1 solves_per_cycle: full solves per coordinator cycle, split by path,
and the solver CPU they cost (B1).

Metric (D9.md): entries into optimizer._multi_start_minimize during one
HeatPumpOptimizerCoordinator._async_update_data, split by the coroutine
path that submitted the job (main solve, fuse advisor what-if + steady
pair, price tile, card what-if, debugger smoke, diagnose), plus
optimize_in_process jobs per path and their solver CPU (thread_time inside
the job). Keyed on what the production seam delivers: each count is an
entry into the production symbol, tagged at coordinator._await_process.

The solve runs in-process on a real ThreadPoolExecutor (coordinator.
_await_process replaced by a same-pickle-round-trip twin), so in-process
hooks see it; the coordinator, its steps and its gates are production.

Command (from the export root):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
        dev/audit/rounds/round11/D9/s1/h_solves_per_cycle.py [--cycles 12]

Arms: default (null: tiles off, no fuse), tiles_fuse (price_tiles_enabled +
main_fuse_amperes 20), tiles_fuse_duty (+ compressor_cycling_cost 2.0 and a
learned duty-switch stop, duty_switch.planner_fields patched); triggers on
tiles_fuse: card what-if (async_simulate steady=True, the simulate
service's call), debugger smoke (async_simulate({}, limited=False)),
async_diagnose_interval.

Perturbation: price_tiles_enabled False -> True (and a fuse): solves per
cycle must go UP from 1 (default arm). Pi seconds = host CPU x F, F = 5
(D9-criteria.md, an assumption). CPU numbers provisional; counts exact.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B1 container.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import asyncio  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from collections import defaultdict  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402
from datetime import timedelta  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d9s1lib as L  # noqa: E402

F_PI = 5.0
B1_PI_S = 60.0


def short(tag: str) -> str:
    t = tag.split("|")[0]
    for key, name in (("_maybe_run_fuse_advisor", "fuse_advisor"),
                      ("_maybe_refresh_price_tile", "price_tile"),
                      ("_solver_smoke", "debugger_smoke"),
                      ("async_diagnose_interval", "diagnose"),
                      ("card_whatif", "card_whatif"),
                      ("async_run_optimization", "main")):
        if key in t:
            sub = ".steady" if "steady_pair" in t else ""
            return name + sub
    return t or "?"


async def run_arm(name, extra, cycles, duty=False, triggers=False):
    from heatpump_optimizer import const, duty_switch
    from heatpump_optimizer import optimizer as om
    from homeassistant.util import dt as dtu
    from profiles import house

    loop = asyncio.get_running_loop()
    pool = ThreadPoolExecutor(max_workers=2)
    hass = L.make_loop_hass(loop, pool)
    dtu.freeze(L.CYCLE_NOW)
    cfg = dict(house(two_zone=True, dhw=True))
    cfg.update(extra)
    coord = L.make_coordinator(hass, cfg, entry_id=f"spc_{name}")
    tags: list = []
    undo = L.inline_worker(tags)
    real_pf = duty_switch.planner_fields
    if duty:
        duty_switch.planner_fields = lambda c: {
            "duty_switch_stop_probability": (0.5, 0.5),
            "duty_switch_off_seconds": (300.0, 300.0)}
    # per-job solver CPU and msm entries, tagged
    cpu = defaultdict(float)
    msm = defaultdict(int)
    jobs = defaultdict(int)
    real_oip = om.optimize_in_process
    real_msm = om._multi_start_minimize

    def msm_hook(*a, **k):
        msm[short(L.TAG[0])] += 1
        return real_msm(*a, **k)

    om._multi_start_minimize = msm_hook
    from heatpump_optimizer import coordinator as cm
    real_ap = cm._await_process  # the inline twin

    async def timed_ap(h, fn, *args):
        tag = L.caller_path()
        key = short(tag)
        jobs[key] += 1
        # keep the twin's pickle round trip and tag
        L.TAG[0] = tag
        return await real_ap(h, _Timed(fn, cpu, key), *args)

    cm._await_process = timed_ap
    per_cycle = []
    try:
        for i in range(cycles):
            now = L.CYCLE_NOW + timedelta(minutes=30 * i)
            dtu.freeze(now)
            L.feed(coord, now)
            m0, j0, c0 = dict(msm), dict(jobs), dict(cpu)
            await coord._async_update_data()
            row = {k: msm.get(k, 0) - m0.get(k, 0) for k in msm}
            jrow = {k: jobs.get(k, 0) - j0.get(k, 0) for k in jobs}
            crow = sum(cpu.values()) - sum(c0.values())
            main_cpu = cpu.get("main", 0.0) - c0.get("main", 0.0)
            per_cycle.append((sum(row.values()), main_cpu, crow, row, jrow))
        if triggers:
            for tname, coro in (
                ("card_whatif", lambda: _card_whatif(coord)),
                ("debugger_smoke", lambda: _smoke(coord)),
                ("diagnose", lambda: coord.async_diagnose_interval()),
            ):
                m0, j0, c0 = dict(msm), dict(jobs), dict(cpu)
                try:
                    await coro()
                except Exception as err:  # noqa: BLE001
                    L.result(f"{name}.trigger.{tname}.error", type(err).__name__, "enum")
                L.result(f"{name}.trigger.{tname}.msm_entries",
                         sum(msm.values()) - sum(m0.values()), "count")
                L.result(f"{name}.trigger.{tname}.worker_jobs",
                         sum(jobs.values()) - sum(j0.values()), "count")
                L.result(f"{name}.trigger.{tname}.solver_cpu_s",
                         sum(cpu.values()) - sum(c0.values()), "s")
    finally:
        cm._await_process = real_ap
        om._multi_start_minimize = real_msm
        duty_switch.planner_fields = real_pf
        undo()
        pool.shutdown()
    counts = [p[0] for p in per_cycle]
    cpus = [p[2] for p in per_cycle]
    L.result(f"{name}.cycles", cycles, "count")
    L.result(f"{name}.msm_per_cycle_max", max(counts), "count")
    L.result(f"{name}.msm_per_cycle_mean", sum(counts) / len(counts), "count")
    L.result(f"{name}.msm_per_cycle_series", ",".join(map(str, counts)), "list")
    for k in sorted(msm):
        L.result(f"{name}.msm_by_path.{k}", msm[k], "count")
    for k in sorted(jobs):
        L.result(f"{name}.jobs_by_path.{k}", jobs[k], "count")
        L.result(f"{name}.cpu_by_path.{k}", cpu[k], "s")
    L.result(f"{name}.solver_cpu_per_cycle_max_s", max(cpus), "s")
    L.result(f"{name}.solver_cpu_per_cycle_mean_s", sum(cpus) / len(cpus), "s")
    L.result(f"{name}.solver_cpu_per_cycle_max_pi_s", max(cpus) * F_PI, "s")
    L.result(f"{name}.b1_cycles_over_60_pi_s", sum(1 for c in cpus if c * F_PI > B1_PI_S), "count")
    L.result(f"{name}.cpu_series_s", ",".join(f"{c:.2f}" for c in cpus), "list")
    L.result(f"{name}.main_cpu_series_s", ",".join(f"{p[1]:.2f}" for p in per_cycle), "list")
    ranked = sorted(cpus)
    L.result(f"{name}.solver_cpu_per_cycle_max_drop1_s", ranked[-2] if len(ranked) > 1 else ranked[-1], "s")
    L.result(f"{name}.solver_cpu_per_cycle_min_s", ranked[0], "s")
    REF_SERIES[name] = cpus
    return per_cycle


class _Timed:
    """Picklable wrapper: runs fn and adds its thread CPU under key."""

    def __init__(self, fn, sink, key):
        self.fn, self.key = fn, key
        self.__qualname__ = getattr(fn, "__qualname__", "?")
        _SINKS[key] = sink

    def __call__(self, *args):
        t = time.thread_time()
        try:
            return self.fn(*args)
        finally:
            _SINKS[self.key][self.key] += time.thread_time() - t

    def __reduce__(self):
        return (_rebuild, (self.fn, self.key))


_SINKS: dict = {}
REF_SERIES: dict = {}


def _rebuild(fn, key):
    obj = _Timed.__new__(_Timed)
    obj.fn, obj.key = fn, key
    obj.__qualname__ = getattr(fn, "__qualname__", "?")
    return obj


async def _card_whatif(coord):
    # the simulate service's call (services.py: async_simulate(overrides, steady=True))
    async def card_whatif():
        return await coord.async_simulate({"target_temp": 20.0}, steady=True)
    return await card_whatif()


async def _smoke(coord):
    from heatpump_optimizer import debugger
    async def _solver_smoke():
        return await debugger._solver_smoke(coord, [])
    return await _solver_smoke()


def main():
    from heatpump_optimizer import const
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=12)
    ap.add_argument("--arms", default="default,tiles_fuse,duty,tiles_fuse_duty")
    a = ap.parse_args()
    L.PATH_FUNCS += ("card_whatif", "_solver_smoke")
    clock = L.Clock()
    swap0 = L.swapins()
    arms = {
        "default": ({}, False, False),
        "tiles_fuse": ({const.CONF_PRICE_TILES_ENABLED: True, const.CONF_MAIN_FUSE_A: 20}, False, True),
        "duty": ({const.CONF_CYCLING_COST: 2.0}, True, False),
        "tiles_fuse_duty": ({const.CONF_PRICE_TILES_ENABLED: True, const.CONF_MAIN_FUSE_A: 20,
                             const.CONF_CYCLING_COST: 2.0}, True, False),
    }
    for arm in a.arms.split(","):
        extra, duty, trig = arms[arm]
        asyncio.run(run_arm(arm, extra, a.cycles, duty=duty, triggers=trig))
    # executor threads carry deliberate solver work, so the BLAS signal is
    # taken over the single-threaded reference section alone
    rclock = L.Clock()
    ref = L.ref_ms()
    L.result("reference_solve_cpu_ms", ref, "ms")
    L.result("F_assumed", F_PI, "1")
    # the contention-robust form: cycle CPU in reference solves, against B1's
    # 60 Pi-s expressed in reference solves (60 / (F * ref))
    L.result("b1_budget_ref_solves", 60.0 / (F_PI * ref / 1e3), "ref_solves")
    for name, cpus in REF_SERIES.items():
        L.result(f"{name}.cycle_max_ref_solves", max(cpus) / (ref / 1e3), "ref_solves")
        L.result(f"{name}.cycle_max_drop1_ref_solves",
                 sorted(cpus)[-2] / (ref / 1e3), "ref_solves")
        L.result(f"{name}.cycles_over_b1_by_ref",
                 sum(1 for c in cpus if c / (ref / 1e3) > 60.0 / (F_PI * ref / 1e3)), "count")
    L.result("whole_run_process_over_main_thread", clock.factor(), "1")
    L.tail(rclock, swap0=swap0)


if __name__ == "__main__":
    main()
