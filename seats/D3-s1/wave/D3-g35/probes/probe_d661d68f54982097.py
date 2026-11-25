#!/usr/bin/env python3
"""D3-s1 (box D3-g35), audit round 11: step-4 probe for full-gate survivor d661d68f54982097.

Metric (one line): differing_cases = how many inputs of this probe's case set give a different
published SystemIdentification.identify() result (completed, reason, UA, C, gains, drift,
confidence) under the mutant than at the baseline; the KEY case's completed is printed per arm.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_d661d68f54982097.py
Expected: (filled from the recorded run)
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (sysid.py read with git show, never the worktree file).
Machine: box D3-g35 cloud container, 4 cores, Intel Xeon @ 2.10GHz; counts exact, run time provisional.
Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.identify
(sysid.py:2223, CMP_BOUND), driven through synthetic exact first-order step tests (sysid_probe_common.py).
Perturbation: the one-line mutant d661d68f54982097, applied in memory to a copy of the module source:
  old: if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0):
  new: if not (0.1 <= tau < 200.0) or not (0.01 <= ua <= 5.0):
Key case: a slow plant whose fitted tau lands on exactly 200 h (hunted over UA and step power).
Count key: the value identify() returns (the production seam's output), not an input attribute.
A hunted case (HUNT) searches float inputs until the instrumentation arm (`_TAP.append` before
the mutated line, not the mutant) reads the boundary exactly; no hit means the case is absent.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sysid_probe_common as c  # noqa: E402

OLD = '        if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0):'
NEW = '        if not (0.1 <= tau < 200.0) or not (0.01 <= ua <= 5.0):'
L = '        if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0):'
FIELDS = ("completed", "reason", "heat_loss_kw_per_c", "thermal_mass_kwh_per_c",
          "internal_gains_kw", "sensor_drift_c_per_h", "confidence")


def fixed_point_case(m):
    """sensor_drift_prior_c_per_h iterated to the fitted |drift| until they are equal exactly."""
    tap = c.load_tap("        if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0):", "drift_c_per_h")
    s = c.plant_samples(m, drift=0.01, start_steady=False, t0=1.3)
    p = 0.02
    for it in range(80):
        d, _ = c.tapped(tap, s, tap.SysIdConfig(enabled=True, sensor_drift_prior_c_per_h=p))
        if d is None:
            break
        if abs(d) == p:
            print(f"RESULT fixed_point_iterations={it}")
            print(f"RESULT prior_equal_to_fitted_drift={p!r}")
            return [("KEY prior==|drift|", s, {"sensor_drift_prior_c_per_h": p})]
        p = abs(d)
    print("RESULT fixed_point_iterations=none")
    return []


def main() -> int:
    m = c.load()
    EXTRA = []
    HUNT = None
    MEASURE_KEY = 'completed'
    HUNT = (L, 'tau', lambda x, s: c.plant_samples(m, ua=x, cap=3.0, gains=0.0, q=s), 0.0145, 0.0155, 200.0, [3.0 + 0.05 * i for i in range(40)])
    # found by a random search (seed 1, 42394 evaluations) over cap, step power and UA
    s = c.plant_samples(m, ua=0.011370575082848609, cap=2.273167336967812, gains=0.0, q=4.770168220478481)
    print(f'RESULT key_tapped_tau={c.tapped(c.load_tap(L, "tau"), s)[0]!r}')
    EXTRA = [('KEY tau==200', s, None)]
    MEASURE_KEY = 'completed'
    if HUNT is not None:
        line, expr, make, lo, hi, target, seconds = HUNT
        x, s, tried = c.multi_hunt(line, expr, make, lo, hi, target, seconds)
        print(f"RESULT hunt_evaluations={tried}")
        print(f"RESULT hunt_hit={int(x is not None)}  # input x={x!r} secondary={s!r}")
        if x is not None:
            EXTRA = [("KEY hunted", make(x, s), None)]
    cases = EXTRA + c.std_cases(m)
    base, mut = c.load(), c.load(OLD, NEW)
    for label, samples, cfg in EXTRA:
        rb = c.run(base, samples, base.SysIdConfig(enabled=True, **(cfg or {})))
        rm = c.run(mut, samples, mut.SysIdConfig(enabled=True, **(cfg or {})))
        print(f"RESULT key_{MEASURE_KEY}.baseline={getattr(rb, MEASURE_KEY)!r}  # {c.fmt(rb)}")
        print(f"RESULT key_{MEASURE_KEY}.mutant={getattr(rm, MEASURE_KEY)!r}  # {c.fmt(rm)}")
    c.drive(OLD, NEW, c.outcome, cases)
    c.footer()
    return 0


if __name__ == "__main__":
    sys.exit(main())
