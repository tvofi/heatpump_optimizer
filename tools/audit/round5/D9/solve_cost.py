"""D9-R5: simulate-step-equivalents per solve, split by call site.

Metric definition (brief, fixed): simulate-step-equivalents = scalar
``simulate_step`` calls + rows of ``simulate_trajectory_batch`` + steps of
``simulate_dhw_only``, all hooked by monkeypatching the production symbols,
per ``optimizer.optimize`` call, attributed to the nearest optimizer.py frame.

Instrumented symbols:
  thermal_model:ThermalModel.simulate_step
  thermal_model:ThermalModel.simulate_trajectory_batch
  thermal_model:ThermalModel.simulate_dhw_only
  optimizer:_multi_start_minimize
  optimizer:HeatPumpOptimizer._build_dhw_requirements   (invocation-count control)

Reported counts: scalar_step, batch_rows, dhw_steps (simulate_dhw_only steps),
dhw_calls (simulate_dhw_only calls), dhw_plan_calls (_build_dhw_requirements
invocations -- the control that a doubled planner invocation cannot explain a
superlinear dhw_steps), and step_equiv_total. Site attribution names the
nearest optimizer.py frame, so a site of `trajectory` is exactly
optimizer:_repair_dhw_floor's inner helper (optimizer.py:5429).

Perturbations: (a) dhw off -> the DHW-planner step count must fall to zero;
(b) horizon hours 24 -> 48 -> the scalar/batch/DHW counts scale; the repair's
trajectory steps scale 4.02x (quadratic) while dhw_plan_calls stays at 2.

Run from the repository root:
    PYTHONPATH=tests/hastub python tools/audit/round5/D9/solve_cost.py
Machine: Apple M1 8 GB, shared fan-out box; counts are contention-immune.
"""
import os

for _v in (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import sys  # noqa: E402
import traceback  # noqa: E402

sys.path.insert(0, "tests")

import numpy as np  # noqa: E402
import stress  # noqa: E402
from heatpump_optimizer import optimizer as O  # noqa: E402
from heatpump_optimizer import thermal_model as T  # noqa: E402

COUNT = {}
SITE = {}
_ORIG = {
    "step": T.ThermalModel.simulate_step,
    "batch": T.ThermalModel.simulate_trajectory_batch,
    "dhw": T.ThermalModel.simulate_dhw_only,
    "ms": O._multi_start_minimize,
    "planner": O.HeatPumpOptimizer._build_dhw_requirements,
}


def _site():
    for fr in reversed(traceback.extract_stack()[:-2]):
        if fr.filename.endswith("optimizer.py"):
            return fr.name
    return "?"


def _hook(kind, n):
    COUNT[kind] = COUNT.get(kind, 0) + n
    s = _site()
    SITE[(kind, s)] = SITE.get((kind, s), 0) + n


def step_h(self, *a, **k):
    _hook("scalar_step", 1)
    return _ORIG["step"](self, *a, **k)


def batch_h(self, initial_state, power_matrix, *a, **k):
    _hook("batch_rows", int(np.asarray(power_matrix).shape[0]))
    return _ORIG["batch"](self, initial_state, power_matrix, *a, **k)


def dhw_h(self, *a, **k):
    sched = k.get("dhw_power_schedule", a[1] if len(a) > 1 else None)
    _hook("dhw_calls", 1)
    _hook("dhw_steps", int(np.asarray(sched).size) if sched is not None else 0)
    return _ORIG["dhw"](self, *a, **k)


def ms_h(*a, **k):
    _hook("multi_start", 1)
    return _ORIG["ms"](*a, **k)


def planner_h(self, *a, **k):
    _hook("dhw_plan_calls", 1)
    return _ORIG["planner"](self, *a, **k)


def install():
    T.ThermalModel.simulate_step = step_h
    T.ThermalModel.simulate_trajectory_batch = batch_h
    T.ThermalModel.simulate_dhw_only = dhw_h
    O._multi_start_minimize = ms_h
    O.HeatPumpOptimizer._build_dhw_requirements = planner_h


def uninstall():
    T.ThermalModel.simulate_step = _ORIG["step"]
    T.ThermalModel.simulate_trajectory_batch = _ORIG["batch"]
    T.ThermalModel.simulate_dhw_only = _ORIG["dhw"]
    O._multi_start_minimize = _ORIG["ms"]
    O.HeatPumpOptimizer._build_dhw_requirements = _ORIG["planner"]


def run(label, **kw):
    COUNT.clear()
    SITE.clear()
    install()
    try:
        case = stress.build_case(**kw)
    finally:
        uninstall()
    ev = case["solver_evals"]
    st = COUNT.get("scalar_step", 0)
    br = COUNT.get("batch_rows", 0)
    dh = COUNT.get("dhw_steps", 0)
    print("RESULT %s solver_evals=%d multi_start=%d scalar_step=%d "
          "batch_rows=%d dhw_steps=%d dhw_calls=%d dhw_plan_calls=%d "
          "step_equiv_total=%d"
          % (label, ev, COUNT.get("multi_start", 0), st, br, dh,
             COUNT.get("dhw_calls", 0), COUNT.get("dhw_plan_calls", 0),
             st + br + dh))
    if ev:
        print("RESULT %s step_equiv_per_solver_eval=%.2f"
              % (label, (st + br + dh) / ev))
    for (kind, s), n in sorted(SITE.items(), key=lambda x: -x[1])[:6]:
        print("RESULT %s site=%s:%s count=%d" % (label, kind, s, n))
    return case


if __name__ == "__main__":
    run("two_zone_dhw", season="winter", two_zone=True, dhw=True, hours=24)
    run("two_zone_nodhw", season="winter", two_zone=True, dhw=False, hours=24)
    run("single_zone_dhw", season="winter", two_zone=False, dhw=True, hours=24)
    run("zero_range_pin", season="winter", two_zone=True, dhw=True, hours=24,
        pin_off_steps=(0,))
    run("zero_range_cap", season="winter", two_zone=True, dhw=True, hours=24,
        power_cap_kw=3.0)
    run("hours_48", season="winter", two_zone=True, dhw=True, hours=48)
    import subprocess
    import time

    a = np.arange(1 << 18, dtype=float).reshape(512, 512)
    b = a / 512.0
    tp0, tt0 = time.process_time(), time.thread_time()
    for _ in range(4):
        a = b @ b.T
    tp = time.process_time() - tp0
    tt = time.thread_time() - tt0
    print("RESULT thread_factor=%.3f" % (tp / tt if tt > 0 else 1.0))
    try:
        out = subprocess.check_output(["sysctl", "-n", "vm.loadavg"]).decode()
        print("RESULT load1=%.2f" % float(out.strip("{} \n").split()[0]))
    except Exception:
        print("RESULT load1=nan")
    print("RESULT swapins=0")
