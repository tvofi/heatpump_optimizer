"""Verifier V2 (independent) check on D9-s2-71.

Metric (own): (a) valve coverage of tests/stress.py's sweep, counted by directly inspecting the
built ThermalParameters' mixing_valve_mode attribute after stress.build_case(**spec) (no sentinel
exception, unlike the finder's harness -- this drives build_case only, never calls optimize());
(b) CPU ratio of one golden valve plant vs its mixing_valve_mode='none' twin, measured with
cProfile cumulative time in HeatPumpOptimizer.optimize (an independent CPU instrument from the
finder's SolverWork step counter).

Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python \
  tools/audit/round9/D9/verify-v2-leads/v2_valve_coverage.py
Instrumented symbol: tests/stress.py:sweep_combinations/build_case (coverage count);
  heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize (profiled CPU).
Perturbation: mixing_valve_mode='none' on golden scenario valve_storage (config change); ratio
  must fall toward 1.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import copy
import cProfile
import pstats
import sys
import time
sys.path[:0] = ["tests", "custom_components"]
import golden  # noqa: E402
import stress  # noqa: E402
from heatpump_optimizer import mixing_valve  # noqa: E402

t0, th0 = time.process_time(), time.thread_time()

# (a) coverage: build every sweep case, look at the resulting plant directly (no exception trick)
combos = stress.sweep_combinations()
valve_cases = 0
for spec in combos:
    plant = stress.build_case(**{k: v for k, v in spec.items() if k != "label"})
    mode = getattr(plant, "mixing_valve_mode", None)
    if mode is not None and mixing_valve.is_throttling(mode):
        valve_cases += 1
print(f"RESULT stress_sweep_valve_cases={valve_cases} of {len(combos)} count")

# (b) CPU: cProfile cumulative time inside HeatPumpOptimizer.optimize, valve vs no-valve
NAME = "valve_storage"


def profiled_cpu(mode_override):
    spec = copy.deepcopy(golden.SCENARIOS[NAME])
    if mode_override is not None:
        spec.setdefault("config_overrides", {})["mixing_valve_mode"] = mode_override
    pr = cProfile.Profile()
    pr.enable()
    golden.capture(NAME, spec)
    pr.disable()
    st = pstats.Stats(pr)
    total = 0.0
    for (file, line, func), (cc, nc, tt, ct, callers) in st.stats.items():
        if func == "optimize" and "optimizer.py" in file:
            total += ct
    return total


valve_cpu = profiled_cpu(None)
novalve_cpu = profiled_cpu("none")
ratio = valve_cpu / novalve_cpu if novalve_cpu else float("nan")
print(f"RESULT valve_optimize_cumtime={valve_cpu:.3f}s")
print(f"RESULT novalve_optimize_cumtime={novalve_cpu:.3f}s")
print(f"RESULT valve_cpu_ratio={ratio:.2f} ratio")
print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
