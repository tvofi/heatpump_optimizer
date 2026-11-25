#!/usr/bin/env python3
# Probe for mutant 8206a42b98c8dd86 (box D3-g28, audit round 11, D3.M3/M4 full-gate survivor answer).
# Metric: the savings percentage _savings_percentage returns for savings 0.005 on a baseline cost of exactly 0.01.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g28/probes/probe_8206a42b98c8dd86.py
# Expected (exact; counts and values are deterministic, tolerance 0 unless a float is printed to fewer digits):
#   RESULT pct_baseline=0.000 %
#   RESULT pct_mutant=50.000 %
#   RESULT pct_abs_diff=50.000 %
#   RESULT null_baseline_cost_0p02_diff=0
#   RESULT null_baseline_cost_0p009_diff=0
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
# Machine: cloud box D3-g28, 4 vCPU Intel(R) Xeon(R) Processor @ 2.10GHz, 16 GB; run beside its own full gate
#   (load1 1.0-2.1), so any timing here is provisional; the metrics are counts and values, contention-immune.
# Instrumented symbol: heatpump_optimizer.optimizer:_savings_percentage (custom_components/heatpump_optimizer/optimizer.py:2144 `if baseline_cost <= 0.01:`),
#   imported under the package name the suite uses (tests/golden.py puts custom_components on sys.path).
# Perturbation: `if baseline_cost <= 0.01:` -> `if baseline_cost < 0.01:` (the mutant), applied in memory: the function is re-compiled from its
#   own source with that one line replaced and called directly, or attached with mock.patch.object for the mutant
#   arm of a caller. Direction: up: 0 -> 50 %.
# Inputs tried: baseline 0.01 (the boundary); null: 0.02 and 0.009.
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


OLD, NEW = "    if baseline_cost <= 0.01:", "    if baseline_cost < 0.01:"
MUT = mutant("_savings_percentage", OLD, NEW)
b, m = O._savings_percentage(0.005, 0.01), MUT(0.005, 0.01)
print(f"RESULT pct_baseline={b:.3f} %")
print(f"RESULT pct_mutant={m:.3f} %")
print(f"RESULT pct_abs_diff={abs(b - m):.3f} %")
print(f"RESULT null_baseline_cost_0p02_diff={abs(O._savings_percentage(0.005, 0.02) - MUT(0.005, 0.02)):.3f} %")
print(f"RESULT null_baseline_cost_0p009_diff={abs(O._savings_percentage(0.005, 0.009) - MUT(0.005, 0.009)):.3f} %")
tail()
