"""L4 lead (raised by D1-s2) for D5-s2 / D5.M4 -- does the diagnose worker get copies, as the docstring says?

Claim under test: coordinator.async_diagnose_interval's docstring, "the worker gets copies, never
  this object (#1529)", while _diagnose_payload hands coord._last_interval_record over by reference.
Metric (one line): leaked_writes = keys a job run through coordinator._await_process adds to the
  record _diagnose_payload returned, as seen on the LIVE coordinator's record after the job returns.
  Count key: coord._last_interval_record itself (the object the docstring says the worker never gets).
Run:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D5/leads/l4_diag_copy.py [--perturb]
Job: dict.setdefault(record, "__l4_probe__") -- a picklable stdlib callable that writes into what
  it is handed, sent through the production transport (_await_process -> _run_in_process -> the
  real process_worker.py child, pickled both ways).
Perturbation (--perturb): _run_in_process replaced in memory by an in-thread call fn(*args) (what a
  thread-executor transport would do). Expected: leaked_writes 0 -> 1 (direction: up).
Expected: leaked_writes=0 (payload_is_live_record=1); --perturb 1. Exact.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; box: 4-vCPU Linux container.
Instrumented: coordinator:_diagnose_payload, coordinator:_await_process, coordinator:_run_in_process.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import sys
import time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from harness import FakeHass  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

if "--perturb" in sys.argv:
    cm._run_in_process = lambda fn, args: fn(*args)


def main():
    t0, th0 = time.process_time(), time.thread_time()
    coord = object.__new__(cm.HeatPumpOptimizerCoordinator)
    coord._last_interval_record = {"interval_start": "2026-01-15T00:00:00", "room_temp": 21.0}
    coord._thermal_params = ThermalParameters()
    before = set(coord._last_interval_record)
    record, params = cm._diagnose_payload(coord)
    same_object = record is coord._last_interval_record
    asyncio.run(cm._await_process(FakeHass({}), dict.setdefault, record, "__l4_probe__"))
    leaked = len(set(coord._last_interval_record) - before)
    cm._shutdown_process_pool()
    print(f"RESULT payload_is_live_record={int(same_object)} bool")
    print(f"RESULT params_is_live_params={int(params is coord._thermal_params)} bool")
    print(f"RESULT leaked_writes={leaked} count")
    print(f"RESULT perturbed={int('--perturb' in sys.argv)}")
    print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "n/a"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
