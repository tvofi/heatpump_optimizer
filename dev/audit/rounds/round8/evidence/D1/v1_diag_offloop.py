"""D1 verifier v1 (round 8), own harness for D1-s1-02.

Metric (one line): per diagnose path (diagnose_interval service, Diagnose
button = async_diagnose_interval), count the diagnosis.diagnose_record
invocations that run on a non-loop thread of THIS process while holding the
live ctx._thermal_params object (identity), and of those, how many computed on
a value the event loop wrote while the diagnosis was in flight (torn input).

Method, different from the finder's attribute tracer: the executor is a real
ThreadPoolExecutor (FakeHass runs executor jobs inline, which would hide the
defect); the diagnosis worker is wrapped where the coordinator module resolves
it (cm.diagnosis.diagnose_record). While it runs on the worker thread, the
wrapper asks the loop (call_soon_threadsafe) to write heat_loss_coefficient on
the live params, waits for that write, then lets the real worker copy its
input. The button path is observed at cm._await_process (its worker runs in the
process child, so only the argument identity is observable here).
The interval record is hand-built (no settled interval exists in a fresh
coordinator); it only has to be non-empty to pass diagnose_record's guard.
--perturb: the fix-shaped edit, in-process and restored in finally:
  services.handle_diagnose_interval routes through coord.async_diagnose_interval().
Command (tree root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D1/v1_diag_offloop.py [--perturb]
Expected: service_offloop_live=1 service_torn=1 button_offloop_live=0 (exact);
perturbed: all 0. Baseline cdf82daa; 4-vCPU shared cloud container.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import concurrent.futures  # noqa: E402
import sys  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, "tools/audit/round8/D1")

from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.config_entries import ConfigEntryState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from heatpump_optimizer import services as sv  # noqa: E402
from v1_setback_race import config, states  # noqa: E402

PERTURB = "--perturb" in sys.argv


class ThreadHass(FakeHass):
    def __init__(self, st):
        super().__init__(st)
        self.loop = asyncio.get_running_loop()
        self.pool = concurrent.futures.ThreadPoolExecutor(2, thread_name_prefix="SyncWorker")

    def async_add_executor_job(self, func, *args):
        return self.loop.run_in_executor(self.pool, func, *args)


class Call:
    def __init__(self, data):
        self.data = data
        self.domain, self.service = "heatpump_optimizer", "diagnose_interval"


async def perturbed_handler(hass, call):
    reports = {}
    for entry_id, coord in sv._manual_targets(hass, dict(call.data).get("entry_id")):
        await coord.async_diagnose_interval()
        reports[entry_id] = coord._last_diagnosis
    return {"diagnosis": reports}


async def main():
    loop = asyncio.get_running_loop()
    loop_tid = threading.get_ident()
    hass = ThreadHass(states())
    entry = FakeEntry(data=config())
    coord = cm.HeatPumpOptimizerCoordinator(hass, entry)
    await coord._update_current_state()
    entry.state = ConfigEntryState.LOADED
    entry.runtime_data = coord
    hass.config_entries.entries.append(entry)
    live = coord._ctx._thermal_params
    base_hlc = live.heat_loss_coefficient
    coord._last_interval_record = {
        "when": dt_util.now().isoformat(timespec="seconds"),
        "state": coord._ctx._current_state,
        "planned": {"electrical_power": 1.0, "outdoor_temp": -5.0, "solar_radiation": 0.0},
        "dt_hours": 0.25,
        "realised": {"electrical_power": 1.3, "outdoor_temp": -6.0, "solar_radiation": 0.0},
        "actual": 20.9,
    }
    tally = {"service": [0, 0], "button": [0, 0]}
    phase = {"n": "service"}
    orig_dr = cm.diagnosis.diagnose_record
    orig_ap = cm._await_process

    def wrapped_dr(record, params):
        if threading.get_ident() != loop_tid and params is coord._ctx._thermal_params:
            tally[phase["n"]][0] += 1
            done = threading.Event()

            def write():
                coord._ctx._thermal_params.heat_loss_coefficient = base_hlc * 1.5
                done.set()
            loop.call_soon_threadsafe(write)
            done.wait(5)
            from dataclasses import replace
            if replace(params).heat_loss_coefficient != base_hlc:
                tally[phase["n"]][1] += 1
        return orig_dr(record, params)

    async def wrapped_ap(h, fn, *args):
        if fn is cm.diagnosis.diagnose_record or fn is orig_dr:
            if any(a is coord._ctx._thermal_params for a in args):
                tally[phase["n"]][0] += 1
            cm.diagnosis.diagnose_record = orig_dr  # picklable by reference
            try:
                return await orig_ap(h, orig_dr, *args)
            finally:
                cm.diagnosis.diagnose_record = wrapped_dr
        return await orig_ap(h, fn, *args)

    orig_handler = sv.handle_diagnose_interval
    cm.diagnosis.diagnose_record = wrapped_dr
    cm._await_process = wrapped_ap
    handler = perturbed_handler if PERTURB else orig_handler
    try:
        r1 = await handler(hass, Call({}))
        live.heat_loss_coefficient = base_hlc
        phase["n"] = "button"
        await coord.async_diagnose_interval()
    finally:
        cm.diagnosis.diagnose_record = orig_dr
        cm._await_process = orig_ap
        sv.handle_diagnose_interval = orig_handler
        hass.pool.shutdown(wait=True)
        cm._shutdown_process_pool()
    print(f"  service report keys={sorted((list(r1['diagnosis'].values())[0] or {}).keys())[:5]}")
    return {
        "service_offloop_live": tally["service"][0],
        "service_torn": tally["service"][1],
        "button_offloop_live": tally["button"][0],
        "button_torn": tally["button"][1],
    }


if __name__ == "__main__":
    pc0, tc0 = time.process_time(), time.thread_time()
    res = asyncio.run(main())
    for k, v in res.items():
        print(f"RESULT {k}={v} count")
    pc, tc = time.process_time() - pc0, time.thread_time() - tc0
    print(f"RESULT thread_factor={pc / tc if tc else float('nan'):.3f} (includes the deliberate worker thread)")
    print(f"RESULT load1={open('/proc/loadavg').read().split()[0]}")
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')]
    print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")
    print(f"RESULT perturbed={int(PERTURB)}")
