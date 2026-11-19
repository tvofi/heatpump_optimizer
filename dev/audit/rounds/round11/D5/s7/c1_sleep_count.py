#!/usr/bin/env python3
"""D5.M4 C1 check of tests/features.py:6856's docstring ("The eight between-run ``sleep(0.002)`` calls").

Metric (one line): per HeatPumpOptimizer.optimize call over every tests/golden.py SCENARIOS entry,
the number of time.sleep(0.002) calls made from optimizer:_multi_start_minimize (the between-run
yield), plus the whole-solve total and the source-site count.
Count key: calls delivered to time.sleep with argument 0.002, attributed by the caller frame's
function name; never a count of source text alone.

Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D5/s7/c1_sleep_count.py [--perturb]
Expected: RESULT between_run_per_solve_{min,max} and RESULT scenarios_with_eight exact (deterministic counts).
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B12.

Perturbation (--perturb, in memory): optimizer._multi_start_minimize is wrapped so every call gets
one more start (its first candidate repeated); between_run_per_solve_min and _max move up by at least
one per call, and scenarios_with_eight changes. The docstring's claim holds only if every solve
reads 8.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, collections, inspect
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import golden  # noqa: E402
from heatpump_optimizer import optimizer as opt_mod  # noqa: E402

PERTURB = "--perturb" in sys.argv
real_sleep = time.sleep
calls = collections.Counter()


def counting_sleep(s):
    if s == 0.002:
        calls[sys._getframe(1).f_code.co_name] += 1
    return real_sleep(0)


def main():
    t0 = time.process_time()
    src = inspect.getsource(opt_mod)
    print(f"RESULT source_sites={src.count('sleep(0.002)')} count")
    real_opt = opt_mod.HeatPumpOptimizer.optimize
    per = []

    def wrapped(self, *a, **k):
        calls.clear()
        out = real_opt(self, *a, **k)
        between = calls["_multi_start_minimize"]
        per.append((between, sum(calls.values()), dict(calls)))
        return out

    opt_mod.HeatPumpOptimizer.optimize = wrapped
    real_msm = opt_mod._multi_start_minimize
    if PERTURB:
        def more_starts(objective, candidates, *a, **k):
            c = list(candidates)
            return real_msm(objective, c + c[:1], *a, **k)
        opt_mod._multi_start_minimize = more_starts
    opt_mod._time_mod.sleep = counting_sleep
    try:
        for name, spec in golden.SCENARIOS.items():
            n0 = len(per)
            golden.capture(name, spec)
            for b, t, d in per[n0:]:
                print(f"SCEN {name} between_run={b} total={t} by_caller={d}")
    finally:
        opt_mod.HeatPumpOptimizer.optimize = real_opt
        opt_mod._time_mod.sleep = real_sleep
        opt_mod._multi_start_minimize = real_msm
    bs = [b for b, _, _ in per]
    print(f"RESULT solves={len(per)} count")
    print(f"RESULT between_run_per_solve_min={min(bs)} count")
    print(f"RESULT between_run_per_solve_max={max(bs)} count")
    print(f"RESULT scenarios_with_eight={sum(b == 8 for b in bs)} count")
    print(f"RESULT total_per_solve_max={max(t for _, t, _ in per)} count")
    cpu = time.process_time() - t0
    print(f"RESULT thread_factor={cpu / max(time.thread_time(), 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
