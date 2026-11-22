#!/usr/bin/env python3
# Probe for mutant 57196c29f220bbc6 (box D3-g28, audit round 11, D3.M3/M4 full-gate survivor answer).
# Metric: max abs difference between baseline and mutant schedules over inputs whose remaining energy reaches exactly 0.0 (the only band the < opens).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g28/probes/probe_57196c29f220bbc6.py
# Expected (exact; counts and values are deterministic, tolerance 0 unless a float is printed to fewer digits):
#   RESULT inputs_tried=5144
#   RESULT inputs_reaching_remaining_exactly_zero=4875
#   RESULT max_abs_diff=0
#   RESULT signbit_only_diffs=0
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
# Machine: cloud box D3-g28, 4 vCPU Intel(R) Xeon(R) Processor @ 2.10GHz, 16 GB; run beside its own full gate
#   (load1 1.0-2.1), so any timing here is provisional; the metrics are counts and values, contention-immune.
# Instrumented symbol: heatpump_optimizer.optimizer:_price_ranked_start (custom_components/heatpump_optimizer/optimizer.py:2130 `if remaining <= 0:`),
#   imported under the package name the suite uses (tests/golden.py puts custom_components on sys.path).
# Perturbation: `if remaining <= 0:` -> `if remaining < 0:` (the mutant), applied in memory: the function is re-compiled from its
#   own source with that one line replaced and called directly, or attached with mock.patch.object for the mutant
#   arm of a caller. Direction: none found: equivalent-candidate.
# Inputs tried: exact multiples energy = k*p_max*dt (k 0..8, p_max {1,2,0.5,4}, dt {0.25,0.5,1,0.125}) and 5000 seeded random draws.
# Null control: the RESULT null_* lines, an input where the mutated line cannot matter.
# Writes nothing; no Node; no env_drift.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time
from pathlib import Path
from unittest import mock

_T0 = (time.process_time(), time.thread_time())


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))   # the package name the suite imports (tests/golden.py)
import numpy as np  # noqa: E402
from heatpump_optimizer import optimizer as O  # noqa: E402


def mutant(name, old, new):
    """The production function ``name`` re-compiled from its own source with the one-line mutant."""
    src = textwrap.dedent(inspect.getsource(getattr(O, name)))
    assert src.count(old) == 1, f"anchor line moved: {old!r}"
    ns = dict(O.__dict__)
    exec(compile(src.replace(old, new, 1), O.__file__, "exec"), ns)
    return ns[name]


def outcome(fn, *a, **k):
    """('ok', value) or ('raise', 'Type: message')."""
    try:
        return "ok", fn(*a, **k)
    except Exception as err:  # noqa: BLE001 - the probe reports any raise
        return "raise", f"{type(err).__name__}: {err}"


def golden_solve(price_profile="winter_typical", weather_profile="winter_cold", prices=None, **make_kw):
    """One golden.make scenario through HeatPumpOptimizer.optimize; returns the OptimizationResult."""
    import golden
    b = golden.make(price_profile=price_profile, weather_profile=weather_profile, **make_kw)
    p = b["prices"] if prices is None else np.asarray(prices, dtype=float)
    return b["optimizer"].optimize(inputs=golden.solve_inputs(
        initial_state=b["state"], prices=p, outdoor_temps=b["outdoor"], wind_speeds=b["wind"],
        precipitation=b["rain"], solar_radiation=b["solar"], start_time=golden.START))


def tail():
    pc, tc = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        swapins = next(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin "))
    except Exception:  # noqa: BLE001
        swapins = -1
    print(f"RESULT swapins={swapins}")


OLD, NEW = "        if remaining <= 0:", "        if remaining < 0:"
MUT = mutant("_price_ranked_start", OLD, NEW)
rng = np.random.default_rng(14)
tried, maxdiff, signdiff, exact_zero = 0, 0.0, 0, 0
cases = []
for pm in (1.0, 2.0, 0.5, 4.0):                      # energy an exact multiple of p_max*dt: remaining hits 0.0
    for dt in (0.25, 0.5, 1.0, 0.125):
        for k in range(0, 9):
            cases.append((pm, dt, pm * dt * k))
for _ in range(5000):
    pm, dt = float(rng.uniform(0.3, 9.0)), float(rng.uniform(0.05, 1.0))
    cases.append((pm, dt, float(rng.uniform(0.0, pm * dt * 40))))
for pm, dt, e in cases:
    p = rng.normal(size=40)
    b, m = O._price_ranked_start(p, e, pm, dt), MUT(p, e, pm, dt)
    tried += 1
    rem = e
    for _i in range(40):
        take = min(pm, rem / dt)
        rem -= take * dt
        if rem == 0.0:
            exact_zero += 1
            break
        if rem < 0:
            break
    maxdiff = max(maxdiff, float(np.max(np.abs(b - m))))
    signdiff += int(np.any(np.signbit(b) != np.signbit(m)))
print(f"RESULT inputs_tried={tried}")
print(f"RESULT inputs_reaching_remaining_exactly_zero={exact_zero}")
print(f"RESULT max_abs_diff={maxdiff:.3g}")
print(f"RESULT signbit_only_diffs={signdiff}")
tail()
