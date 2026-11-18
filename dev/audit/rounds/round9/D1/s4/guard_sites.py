#!/usr/bin/env python3
"""D1-s4 M5: the optimizer's degrading guards, each driven by an injected exception.

Metric (one line): per guard site, whether optimize() completes with a finite schedule
and trajectory and a non-"failed" status after the injected fault (1 = degrades cleanly).
Key: the OptimizationResult the production optimize() returns.

Command:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D1/s4/guard_sites.py
          [--perturb]  also inject into the main L-BFGS-B (every _scoped_minimize call):
                       the linprog site then reports 0 (status "failed", 1 ERROR log).
Expected (baseline): linprog_dhw.degrades_cleanly=1, error_logs=0 (DEBUG only).
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1  Machine: box B6
Instrumented: custom_components.heatpump_optimizer.optimizer:linprog (the
              HeatPumpOptimizer._plan_dhw_min_cost LP guard, falls back to the greedy plan)
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import logging
import sys
import time
from unittest import mock

sys.path[:0] = [".", "tests", "tests/hastub", "custom_components"]
t_proc0, t_thr0 = time.process_time(), time.thread_time()
import numpy as np  # noqa: E402
import golden  # noqa: E402
from heatpump_optimizer import optimizer as O  # the module golden.make builds from  # noqa: E402

PERTURB = "--perturb" in sys.argv


class _Sink(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.ERROR)
        self.n = 0

    def emit(self, record):
        self.n += 1


sink = _Sink()
lg = logging.getLogger(O.__name__)
lg.addHandler(sink)
lg.setLevel(logging.ERROR)
lg.propagate = False


def boom(*_a, **_k):
    raise RuntimeError("injected")


def run(target, attr):
    b = golden.make(dhw=True, hours=12)
    ps = [mock.patch.object(target, attr, boom)]
    if PERTURB:
        ps.append(mock.patch.object(O, "_scoped_minimize", boom))
    for p in ps:
        p.start()
    try:
        r = b["optimizer"].optimize(b["state"], b["prices"], b["outdoor"], b["wind"],
                                    b["rain"], b["solar"], golden.START)
    except Exception:  # noqa: BLE001
        return 0, "raised"
    finally:
        for p in reversed(ps):
            p.stop()
    ok = (np.isfinite(np.asarray(r.power_schedule, float)).all()
          and np.isfinite(np.asarray(r.room_temp_trajectory, float)).all()
          and not str(r.status).startswith("failed"))
    return int(ok), r.status


sites = [("linprog_dhw", O, "linprog")]
print(f"MODE perturb={PERTURB}")
for name, tgt, attr in sites:
    before = sink.n
    ok, status = run(tgt, attr)
    print(f"RESULT {name}.degrades_cleanly={ok} count")
    print(f"RESULT {name}.error_logs={sink.n - before} count")
    print(f"# {name}: status={str(status)[:60]}")
pc, tc = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=" + next((ln.split()[1] for ln in open("/proc/vmstat") if ln.startswith("pswpin")), "unknown"))
