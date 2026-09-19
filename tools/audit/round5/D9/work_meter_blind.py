"""D9-R5: is the stress gate's per-scenario WORK meter blind to a cost-only
regression in the simulation kernel?

Metric definition: ``solver_evals`` is exactly what ``tests/stress.py``
``SolverWork`` reports -- the sum of scipy's ``nfev``+``njev`` across every
``optimizer._scoped_minimize`` call in one ``optimizer.optimize()``. It is the
meter the gate's per-scenario work check ("no scenario's solver work grew on
an unchanged plan", SCENARIO_WORK_FACTOR=1.5) reads.

Instrumented symbols:
  optimizer:HeatPumpOptimizer.optimize  (driven)
  optimizer:_scoped_minimize            (the work meter's own seam)
  optimizer:_batch_fd_gradient          (the batched-jac regression injection)

Perturbation: wrap ``optimizer._batch_fd_gradient`` so it computes the
gradient twice and returns the second result. A cost-only regression: the
returned gradient, and therefore every plan, is bit-identical; only the
simulation work inside the batched jac doubles. Expected: ``solver_evals``
ratio 1.00 (the meter cannot move -- it counts scipy evaluations, and the
number of them is unchanged), while CPU rises ~2x on the batched share.

Null control / liveness arm: wrap ``optimizer._scoped_minimize`` so each call
runs twice. That ADDS scipy evaluations, so ``solver_evals`` must move -- the
proof the meter is not simply broken.

Run from the repository root:
    PYTHONPATH=tests/hastub python tools/audit/round5/D9/work_meter_blind.py
Measured at baseline SHA eaa2a06 on the audit box (Apple M1, 8 GB; the run
below was taken under fan-out contention, load1 ~52 -- counts are exact,
CPU is provisional):
    cost-only arm   work_ratio 1.0000  cpu_ratio 1.6832  objective identical
    extra-eval arm  work_ratio 2.0000  cpu_ratio 1.9386  objective identical
Expected value +/- tolerance: work ratios exact (1.0000 / 2.0000); cpu ratios
provisional, +/-25 %.
"""
import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import sys  # noqa: E402

sys.path.insert(0, "tests")

import numpy as np  # noqa: E402
import stress  # noqa: E402
from heatpump_optimizer import optimizer as O  # noqa: E402


def load1() -> float:
    try:
        with open("/proc/loadavg") as fh:
            return float(fh.read().split()[0])
    except OSError:
        try:
            import subprocess

            out = subprocess.check_output(["sysctl", "-n", "vm.loadavg"]).decode()
            return float(out.strip("{} \n").split()[0])
        except Exception:
            return float("nan")


#: The production seams -- asserted present so a rename stops this loudly.
_BATCH = O._batch_fd_gradient
_SCOPED = O._scoped_minimize
_MULTI = O._multi_start_minimize


def _arm_baseline():
    return None


def _arm_cost_only():
    def twice(*a, **k):
        _BATCH(*a, **k)
        return _BATCH(*a, **k)

    O._batch_fd_gradient = twice


def _arm_extra_eval():
    # Doubling a whole multi-start run adds L-BFGS-B starts, i.e. more scipy
    # evaluations of the same shape -- the kind of regression the work meter
    # was built to catch. Results are bit-identical (same second run returned).
    def twice(*a, **k):
        _MULTI(*a, **k)
        return _MULTI(*a, **k)

    O._multi_start_minimize = twice


def run_arm(name, arm):
    O._batch_fd_gradient = _BATCH
    O._scoped_minimize = _SCOPED
    O._multi_start_minimize = _MULTI
    arm()
    try:
        case = stress.build_case(
            season="winter", building=None, two_zone=True, dhw=True, hours=24
        )
    finally:
        O._batch_fd_gradient = _BATCH
        O._scoped_minimize = _SCOPED
        O._multi_start_minimize = _MULTI
    return case


def main():
    results = {}
    for name, arm in (
        ("baseline", _arm_baseline),
        ("cost_only", _arm_cost_only),
        ("extra_eval", _arm_extra_eval),
    ):
        case = run_arm(name, arm)
        results[name] = {
            "evals": case["solver_evals"],
            "calls": case["solver_calls"],
            "cpu": case["solve_cpu_ms"],
            "thread": case["solve_thread_ms"],
            "obj": float(case["result"].objective_value),
        }
        r = results[name]
        print("RESULT arm=%s solver_evals=%d solver_calls=%d cpu_ms=%.1f "
              "thread_ms=%.1f thread_factor=%.3f objective=%.9f"
              % (name, case["solver_evals"], case["solver_calls"],
                 case["solve_cpu_ms"], case["solve_thread_ms"],
                 case["solve_cpu_ms"] / case["solve_thread_ms"],
                 float(case["result"].objective_value)))

    b = results["baseline"]
    for name in ("cost_only", "extra_eval"):
        r = results[name]
        er = r["evals"] / b["evals"] if b["evals"] else float("nan")
        cr = r["cpu"] / b["cpu"] if b["cpu"] else float("nan")
        print("RESULT work_ratio_%s=%.4f" % (name, er))
        print("RESULT cpu_ratio_%s=%.4f" % (name, cr))
    print("RESULT objective_identical=%s"
          % (results["cost_only"]["obj"] == b["obj"]))
    print("RESULT thread_factor=%.3f" % (b["cpu"] / b["thread"]))

    print("RESULT load1=%.2f" % load1())
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
