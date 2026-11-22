#!/usr/bin/env python3
# Probe for mutant 9aa50bd32847b4dd (box D3-g28, audit round 11, D3.M3/M4 full-gate survivor answer).
# Metric: the error a multi-start whose every candidate scores non-finite raises, and the `failed (<error>)` status HeatPumpOptimizer.optimize publishes from it (status_differs: 1 when the two status strings differ).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g28/probes/probe_9aa50bd32847b4dd.py
# Expected (exact; counts and values are deterministic, tolerance 0 unless a float is printed to fewer digits):
#   RESULT outcome_baseline=raise:ValueError: no usable starting point
#   RESULT outcome_mutant=raise:ValueError: all starting points failed
#   RESULT status_differs=1
#   RESULT null_x_max_abs_diff=0 (finite quadratic: the guard is not reached)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
# Machine: cloud box D3-g28, 4 vCPU Intel(R) Xeon(R) Processor @ 2.10GHz, 16 GB; run beside its own full gate
#   (load1 1.0-2.1), so any timing here is provisional; the metrics are counts and values, contention-immune.
# Instrumented symbol: heatpump_optimizer.optimizer:_multi_start_minimize (custom_components/heatpump_optimizer/optimizer.py:1948 `if not scored:`),
#   imported under the package name the suite uses (tests/golden.py puts custom_components on sys.path).
# Perturbation: `if not scored:` -> `if False:` (the mutant), applied in memory: the function is re-compiled from its
#   own source with that one line replaced and called directly, or attached with mock.patch.object for the mutant
#   arm of a caller. Direction: the published failure status text changes (no usable starting point -> all starting points failed).
# Inputs tried: two 4-dim candidates under an objective returning NaN everywhere; null: a finite quadratic.
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


OLD, NEW = "    if not scored:", "    if False:"
MUT = mutant("_multi_start_minimize", OLD, NEW)
bounds = [(0.0, 3.0)] * 4
cands = [np.full(4, 0.5), np.full(4, 1.5)]


def nan_obj(x, *a):
    return float("nan")          # every candidate scores non-finite


def quad(x, *a):
    return float(np.sum((np.asarray(x) - 1.0) ** 2))


b = outcome(O._multi_start_minimize, nan_obj, cands, bounds)
m = outcome(MUT, nan_obj, cands, bounds)
print(f"RESULT outcome_baseline={b[0]}:{b[1]!s}")
print(f"RESULT outcome_mutant={m[0]}:{m[1]!s}")
# The caller (HeatPumpOptimizer.optimize, the `except Exception as e` beside its
# _multi_start_minimize call) publishes `status = f"failed ({e})"`: the status text is the metric.
sb, sm = f"failed ({b[1].split(': ', 1)[1]})", f"failed ({m[1].split(': ', 1)[1]})"
print(f"RESULT status_baseline={sb!r}")
print(f"RESULT status_mutant={sm!r}")
print(f"RESULT status_differs={int(sb != sm)}")
nb, nm = outcome(O._multi_start_minimize, quad, cands, bounds), outcome(MUT, quad, cands, bounds)
print(f"RESULT null_x_max_abs_diff={float(np.max(np.abs(nb[1].x - nm[1].x))):.3g}")
tail()
