"""D1 s1: live-coordinator attribute access from executor threads (round 8).

Baseline cdf82daa, 4-vCPU cloud container (not the audit box).
Metric: number of distinct private coordinator attributes (name starts with a
single "_") read or written from a thread other than the event-loop thread,
across: setup through the entry state machine, the first background solve,
one scheduled cycle, one simulate (what-if) solve, the diagnose_interval
service, and the Diagnose-button path (async_diagnose_interval).
Count key: HeatPumpOptimizerCoordinator.__getattribute__/__setattr__ observed on
a non-loop thread (the production call site delivers the access; nothing is
keyed on the harness's own input).

Command (tree root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D1/s1_thread_reads.py [--perturb]
--perturb: harness-side equivalent of the one-line production edit in
services.py:handle_diagnose_interval, `await hass.async_add_executor_job(coord.diagnose_last_interval)`
-> the snapshot route the button already uses (`await coord.async_diagnose_interval()`,
report read back from coord._last_diagnosis); the count must go to 0.
Expected baseline: offloop_attrs=3 (_ctx, _last_interval_record, _last_diagnosis
when a record exists; exact), service_offloop_attrs=offloop_attrs, button_offloop_attrs=0.
Instrumented: heatpump_optimizer.services:handle_diagnose_interval,
heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator.diagnose_last_interval.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import collections  # noqa: E402
import sys  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402

sys.path.insert(0, "tools/audit/round8/D1")
from s1_realloop import (  # noqa: E402
    RealEntry, RealLoopHass, base_config, base_states, load1, swapins,
)

import heatpump_optimizer as integration  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from heatpump_optimizer import services as sv  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

PERTURB = "--perturb" in sys.argv
Cls = cm.HeatPumpOptimizerCoordinator


async def perturbed_handler(hass, call):
    target_entry = dict(call.data).get("entry_id")
    reports = {}
    for entry_id, coord in sv._manual_targets(hass, target_entry):
        await coord.async_diagnose_interval()
        reports[entry_id] = coord._last_diagnosis
    return {"diagnosis": reports}


async def wait_for(pred, timeout):
    t0 = time.monotonic()
    while not pred():
        if time.monotonic() - t0 > timeout:
            return False
        await asyncio.sleep(0.02)
    return True


async def main():
    loop_tid = threading.get_ident()
    phase = {"name": "setup"}
    seen = collections.defaultdict(set)
    g0, s0 = Cls.__getattribute__, Cls.__setattr__

    def ga(self, name):
        if name[:1] == "_" and name[:2] != "__" and threading.get_ident() != loop_tid:
            seen[phase["name"]].add(name)
        return g0(self, name)

    def sa(self, name, value):
        if name[:1] == "_" and name[:2] != "__" and threading.get_ident() != loop_tid:
            seen[phase["name"]].add(name)
        return s0(self, name, value)

    orig_handler = sv.handle_diagnose_interval
    Cls.__getattribute__, Cls.__setattr__ = ga, sa
    if PERTURB:
        sv.handle_diagnose_interval = perturbed_handler
    try:
        hass = RealLoopHass(base_states())
        hass.config_entries.integration = integration
        entry = RealEntry(data=base_config(const), entry_id="e_tr")
        hass.config_entries.entries.append(entry)
        await integration.async_setup(hass, {})
        await hass.config_entries.async_setup(entry.entry_id)
        coord = entry.runtime_data
        await wait_for(lambda: coord._optimization_result is not None, 240)
        await wait_for(lambda: not coord._optimization_running, 240)
        phase["name"] = "cycle"
        await coord.async_refresh()
        phase["name"] = "simulate"
        await coord.async_simulate({"target_temp": 20.0})
        # a settled interval record, shaped as the accuracy pairing writes it
        st = coord._ctx._current_state
        coord._last_interval_record = {
            "when": dt_util.now().isoformat(timespec="seconds"),
            "state": st, "planned": {"electrical_power": 1.0, "outdoor_temp": -3.0,
                                     "solar_radiation": 0.0},
            "dt_hours": 0.25,
            "realised": {"electrical_power": 1.4, "outdoor_temp": -5.0,
                         "solar_radiation": 0.0},
            "actual": 21.1,
        }
        phase["name"] = "service"
        await hass.services.async_call(const.DOMAIN, const.SERVICE_DIAGNOSE_INTERVAL, {})
        phase["name"] = "button"
        await coord.async_diagnose_interval()
        phase["name"] = "teardown"
        await hass.config_entries.async_unload(entry.entry_id)
        hass.executor.shutdown(wait=True)
    finally:
        Cls.__getattribute__, Cls.__setattr__ = g0, s0
        sv.handle_diagnose_interval = orig_handler
        cm._shutdown_process_pool()
    for k, v in seen.items():
        print(f"  phase={k} offloop={sorted(v)}")
    allnames = set().union(*seen.values()) if seen else set()
    return {
        "offloop_attrs": len(allnames),
        "service_offloop_attrs": len(seen.get("service", ())),
        "button_offloop_attrs": len(seen.get("button", ())),
        "cycle_offloop_attrs": len(seen.get("cycle", ())) + len(seen.get("simulate", ())),
    }


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
