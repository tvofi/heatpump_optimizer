"""D1 s1: a set_thermal_parameters write that lands during a solve is reverted (round 8).

Baseline cdf82daa, 4-vCPU cloud container (not the audit box).
Metric: of the two fields the service writes that away.apply_setback snapshots
(thermal_params.dhw_min_temp, thermal_params.dhw_idle_min_temp), how many hold
a value != the service's value once the in-flight solve's cycle has returned;
counted on the live ctx._thermal_params AND on the published coordinator.data
("dhw_min_temperature", "dhw_idle_min_temperature").
Count key: the value production delivers (the live params object the next solve
snapshots, and the published data dict) -- never the service call's own input.

Arms (each a fresh real-loop hass, entry set up through the state machine,
solve in the production process worker, away mode INACTIVE):
  race    - the service is called while coordinator._run_in_process is executing
            the scheduled cycle's solve;
  control - the same call after that cycle has returned (null control: 0).
Command (tree root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D1/s1_setback_race.py [--perturb]
--perturb applies, in-process and restored in finally, the equivalent of the
one-line production edit away.py:302 `return original` -> `return None`
(no setback applied => nothing to unwind); race_reverted must go to 0.
Expected baseline: race_reverted_live=2, race_reverted_published=2,
control_reverted_live=0, control_reverted_published=0 (exact counts).
Instrumented: heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator.async_run_optimization
(its finally -> heatpump_optimizer.away:restore_setback), services:handle_set_thermal_params.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import sys  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402

sys.path.insert(0, "tools/audit/round8/D1")
from s1_realloop import (  # noqa: E402
    RealEntry, RealLoopHass, base_config, base_states, load1, swapins,
)

import heatpump_optimizer as integration  # noqa: E402
from heatpump_optimizer import away as away_mod  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402

PERTURB = "--perturb" in sys.argv
WANT = {"dhw_min_temperature": 38.0, "dhw_idle_min_temperature": 31.0}
LIVE = {"dhw_min_temperature": "dhw_min_temp", "dhw_idle_min_temperature": "dhw_idle_min_temp"}


async def wait_for(pred, timeout):
    t0 = time.monotonic()
    while not pred():
        if time.monotonic() - t0 > timeout:
            return False
        await asyncio.sleep(0.02)
    return True


async def arm(race: bool, in_solve: threading.Event, spans: list):
    hass = RealLoopHass(base_states())
    hass.config_entries.integration = integration
    entry = RealEntry(data=base_config(const), entry_id=f"e_{int(race)}")
    hass.config_entries.entries.append(entry)
    await integration.async_setup(hass, {})
    await hass.config_entries.async_setup(entry.entry_id)
    coord = entry.runtime_data
    await wait_for(lambda: coord._optimization_result is not None, 240)
    await wait_for(lambda: not coord._optimization_running, 240)
    # the scheduled cycle, as the interval timer runs it
    cycle = hass.async_create_task(coord.async_refresh(), name="interval_refresh")
    if race:
        await wait_for(in_solve.is_set, 120)
        was_in_solve = int(in_solve.is_set())
    else:
        await cycle
        was_in_solve = int(in_solve.is_set())
    svc = hass.async_create_task(hass.services.async_call(
        const.DOMAIN, const.SERVICE_SET_THERMAL_PARAMS, dict(WANT)))
    # the value the service wrote, observed before anything else runs
    await asyncio.sleep(0)
    await wait_for(lambda: coord._ctx._thermal_params.dhw_min_temp == 38.0 or svc.done(), 60)
    applied = sum(
        1 for k, a in LIVE.items() if getattr(coord._ctx._thermal_params, a) == WANT[k])
    await cycle
    await svc
    await wait_for(lambda: not coord._optimization_running and not in_solve.is_set(), 240)
    await asyncio.sleep(0.2)
    params = coord._ctx._thermal_params
    live = sum(1 for k, a in LIVE.items() if getattr(params, a) != WANT[k])
    pub = sum(1 for k in LIVE if (coord.data or {}).get(k) != WANT[k])
    print(f"  arm={'race' if race else 'control'} in_solve_at_call={was_in_solve} "
          f"applied_at_call={applied} live=({params.dhw_min_temp},{params.dhw_idle_min_temp}) "
          f"published=({coord.data.get('dhw_min_temperature')},{coord.data.get('dhw_idle_min_temperature')})")
    await hass.config_entries.async_unload(entry.entry_id)
    hass.executor.shutdown(wait=True)
    return live, pub, applied, was_in_solve


async def main():
    in_solve = threading.Event()
    spans: list = []
    orig_run = cm._run_in_process

    def hooked(fn, args):
        t0 = time.monotonic()
        in_solve.set()
        try:
            return orig_run(fn, args)
        finally:
            in_solve.clear()
            spans.append(time.monotonic() - t0)

    orig_apply = away_mod.apply_setback
    orig_restore = away_mod.restore_setback
    marks: list = []

    def timed_apply(state, opt_config, thermal_params):
        marks.append(("apply", time.monotonic()))
        return orig_apply(state, opt_config, thermal_params)

    def timed_restore(original, opt_config, thermal_params):
        marks.append(("restore", time.monotonic()))
        return orig_restore(original, opt_config, thermal_params)

    def perturbed_apply(state, opt_config, thermal_params):
        if not state.active or state.recovery_active:
            return None  # the one-line edit: nothing applied, nothing to unwind
        return timed_apply(state, opt_config, thermal_params)

    cm._run_in_process = hooked
    cm.away_mode.apply_setback = timed_apply
    cm.away_mode.restore_setback = timed_restore
    if PERTURB:
        cm.away_mode.apply_setback = perturbed_apply
    res = {}
    try:
        r = await arm(True, in_solve, spans)
        res.update(race_reverted_live=r[0], race_reverted_published=r[1],
                   race_applied_at_call=r[2], race_in_solve_at_call=r[3])
        c = await arm(False, in_solve, spans)
        res.update(control_reverted_live=c[0], control_reverted_published=c[1],
                   control_applied_at_call=c[2], control_in_solve_at_call=c[3])
    finally:
        cm._run_in_process = orig_run
        cm.away_mode.apply_setback = orig_apply
        cm.away_mode.restore_setback = orig_restore
        cm._shutdown_process_pool()
    wins, t_apply = [], None
    for kind, t in marks:
        if kind == "apply":
            t_apply = t
        elif t_apply is not None:
            wins.append(t - t_apply)
            t_apply = None
    res["setback_window_max_s_provisional"] = round(max(wins), 3) if wins else float("nan")
    res["setback_windows_counted"] = len(wins)
    res["solve_span_max_s_provisional"] = round(max(spans), 3) if spans else float("nan")
    return res


if __name__ == "__main__":
    t_cpu, t_thr = time.process_time(), time.thread_time()
    out = asyncio.run(main())
    for k, v in out.items():
        print(f"RESULT {k}={v} {'s' if k.endswith('_s_provisional') else 'count'}")
    pc, tc = time.process_time() - t_cpu, time.thread_time() - t_thr
    print(f"RESULT thread_factor={pc / tc if tc else float('nan'):.3f}")
    print(f"RESULT load1={load1()}")
    print(f"RESULT swapins={swapins()}")
    print(f"RESULT perturbed={int(PERTURB)}")
