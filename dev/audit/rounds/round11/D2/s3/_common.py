"""Shared plumbing for the D2-s3 harnesses (round 11): the harness-contract
thread pin, a golden-scenario solve that keeps the production objects, and the
RESULT footer. Not a harness itself; imported by the m3_/m4_/m5_ scripts.

Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine: box B6 (shared).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys
import time

sys.path.insert(0, "tests")
sys.path.insert(0, ".")

import numpy as np  # noqa: E402

_T0 = (time.process_time(), time.thread_time())


def footer():
    pc = time.process_time() - _T0[0]
    tc = time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.4f}")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    except OSError:
        print("RESULT load1=nan")
    swap = "nan"
    try:
        with open("/proc/vmstat") as fh:
            for line in fh:
                if line.startswith("pswpin "):
                    swap = line.split()[1]
    except OSError:
        pass
    print(f"RESULT swapins={swap}")


def golden_names():
    import golden
    return list(golden.SCENARIOS)


def solve_golden(name, spec=None, *, state=None, start=None, keep=True,
                 opt_patch=None):
    """Run tests/golden.py:capture's exact input assembly for one scenario,
    returning the production optimizer, its inputs, its result and the
    horizon/closures the last ``_solve_objectives`` call built.

    ``state`` replaces the initial ThermalState (for continuations);
    ``opt_patch`` is applied to the OptimizationConfig before the solve.
    """
    import golden
    from heatpump_optimizer import optimizer as om

    spec = dict(golden.SCENARIOS[name] if spec is None else spec)
    rec = {"horizons": [], "settle": [], "runs": []}
    orig_make = golden.make
    orig_so = om.HeatPumpOptimizer._solve_objectives
    orig_settle = om.HeatPumpOptimizer._settle_horizon
    orig_opt = om.HeatPumpOptimizer.optimize
    orig_run = om._lbfgsb_run

    def make_hook(**kw):
        built = orig_make(**kw)
        if state is not None:
            built["state"] = state
        if opt_patch is not None:
            opt_patch(built["optimizer"])
        rec["built"] = built
        return built

    def so_hook(self, h):
        out = orig_so(self, h)
        if keep:
            rec["horizons"].append((h, out))
        return out

    def settle_hook(self, h, weather, comfort, baseline_end, optimized_end, *a, **k):
        import copy as _c
        rec["settle"].append((_c.copy(baseline_end), _c.copy(optimized_end)))
        return orig_settle(self, h, weather, comfort, baseline_end, optimized_end, *a, **k)

    def opt_hook(self, *, inputs):
        if start is not None:
            from dataclasses import replace
            inputs = replace(inputs, start_time=start)
        rec["inputs"] = inputs
        res = orig_opt(self, inputs=inputs)
        rec["result"] = res
        rec["opt"] = self
        return res

    def run_hook(objective, batch_objective, x0, bounds, args, maxiter, memo=None):
        if keep and batch_objective is not None:
            rec["runs"].append((objective, batch_objective, np.array(x0), list(bounds), args))
        return orig_run(objective, batch_objective, x0, bounds, args, maxiter, memo)

    golden.make = make_hook
    om.HeatPumpOptimizer._solve_objectives = so_hook
    om.HeatPumpOptimizer._settle_horizon = settle_hook
    om.HeatPumpOptimizer.optimize = opt_hook
    om._lbfgsb_run = run_hook
    try:
        payload = golden.capture(name, spec)
    finally:
        golden.make = orig_make
        om.HeatPumpOptimizer._solve_objectives = orig_so
        om.HeatPumpOptimizer._settle_horizon = orig_settle
        om.HeatPumpOptimizer.optimize = orig_opt
        om._lbfgsb_run = orig_run
    rec["payload"] = payload
    return rec
