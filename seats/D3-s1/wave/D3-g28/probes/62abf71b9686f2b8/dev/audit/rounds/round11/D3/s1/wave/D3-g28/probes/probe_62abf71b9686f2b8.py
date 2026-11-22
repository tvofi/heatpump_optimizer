#!/usr/bin/env python3
# Probe for mutant 62abf71b9686f2b8 (box D3-g28, audit round 11, D3.M3/M4 full-gate survivor answer).
# Metric: the max abs difference of the initial power-weight guess, and of the solved plan (golden winter_typical house), for a 96-step price day whose float mean is exactly PRICE_MEAN_GUESS_EPS.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g28/probes/probe_62abf71b9686f2b8.py
# Expected (exact; counts and values are deterministic, tolerance 0 unless a float is printed to fewer digits):
#   RESULT mean_is_exactly_eps=1
#   RESULT guess_max_abs_diff=0.2358
#   RESULT null_ordinary_prices_diff=0
#   RESULT golden_plan_max_abs_diff=0.3127 kW
#   RESULT golden_cost_rel_diff=0.000161
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
# Machine: cloud box D3-g28, 4 vCPU Intel(R) Xeon(R) Processor @ 2.10GHz, 16 GB; run beside its own full gate
#   (load1 1.0-2.1), so any timing here is provisional; the metrics are counts and values, contention-immune.
# Instrumented symbol: heatpump_optimizer.optimizer:_price_guess_weights (custom_components/heatpump_optimizer/optimizer.py:2082 `if float(np.mean(prices)) > PRICE_MEAN_GUESS_EPS:`),
#   imported under the package name the suite uses (tests/golden.py puts custom_components on sys.path).
# Perturbation: `if float(np.mean(prices)) > PRICE_MEAN_GUESS_EPS:` -> `if float(np.mean(prices)) >= PRICE_MEAN_GUESS_EPS:` (the mutant), applied in memory: the function is re-compiled from its
#   own source with that one line replaced and called directly, or attached with mock.patch.object for the mutant
#   arm of a caller. Direction: the guess switches from the rank branch to the smooth branch; the solved plan moves by up to 0.31 kW.
# Inputs tried: a sinusoidal day scaled to mean exactly 1e-3 (last step nudged until the float mean equals it); null: linspace(0.5, 2.0).
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


OLD = "    if float(np.mean(prices)) > PRICE_MEAN_GUESS_EPS:"
NEW = "    if float(np.mean(prices)) >= PRICE_MEAN_GUESS_EPS:"
MUT = mutant("_price_guess_weights", OLD, NEW)
EPS = O.PRICE_MEAN_GUESS_EPS
n = 96
p = EPS * (1.0 + 0.5 * np.sin(np.arange(n) * 2.0 * np.pi / n))   # a shaped day whose mean is the threshold
for _ in range(100):                                              # nudge one step until the float mean is exact
    m = float(np.mean(p))
    if m == EPS:
        break
    p[-1] += (EPS - m) * n if abs((EPS - m) * n) > 0 else 0.0
    if float(np.mean(p)) == m:
        p[-1] = np.nextafter(p[-1], np.inf if m < EPS else -np.inf)
print(f"RESULT mean_is_exactly_eps={int(float(np.mean(p)) == EPS)}")
b, m = O._price_guess_weights(p), MUT(p)
print(f"RESULT guess_baseline_range={float(b.min()):.4f}..{float(b.max()):.4f}")
print(f"RESULT guess_mutant_range={float(m.min()):.4f}..{float(m.max()):.4f}")
print(f"RESULT guess_max_abs_diff={float(np.max(np.abs(b - m))):.4f}")
q = np.linspace(0.5, 2.0, n)
print(f"RESULT null_ordinary_prices_diff={float(np.max(np.abs(O._price_guess_weights(q) - MUT(q)))):.3g}")
# The plan arm: the same threshold-mean price day through HeatPumpOptimizer.optimize.
r1 = golden_solve(prices=p)
with mock.patch.object(O, "_price_guess_weights", MUT):
    r2 = golden_solve(prices=p)
print(f"RESULT golden_plan_max_abs_diff={float(np.max(np.abs(np.subtract(r1.power_schedule, r2.power_schedule)))):.4g} kW")
print(f"RESULT golden_cost_rel_diff={abs(r1.predicted_cost - r2.predicted_cost) / max(abs(r1.predicted_cost), 1e-12):.4g}")
tail()
