#!/usr/bin/env python3
# Probe for mutant b53efc6448b724e4 (box D3-g28, audit round 11, D3.M3/M4 full-gate survivor answer).
# Metric: the x the multi-start returns when two starts end at distinct points of exactly equal score (the tie the strict < keeps on the first).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g28/probes/probe_b53efc6448b724e4.py
# Expected (exact; counts and values are deterministic, tolerance 0 unless a float is printed to fewer digits):
#   RESULT score_tie=1
#   RESULT x_baseline=0.500000
#   RESULT x_mutant=1.500000
#   RESULT x_max_abs_diff=1.000000
#   RESULT null_tilted_x_max_abs_diff=0.000000
#   RESULT golden_plan_max_abs_diff=0 kW (winter_typical, summer_negative, flat)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
# Machine: cloud box D3-g28, 4 vCPU Intel(R) Xeon(R) Processor @ 2.10GHz, 16 GB; run beside its own full gate
#   (load1 1.0-2.1), so any timing here is provisional; the metrics are counts and values, contention-immune.
# Instrumented symbol: heatpump_optimizer.optimizer:_multi_start_minimize (custom_components/heatpump_optimizer/optimizer.py:1994 `if np.isfinite(score) and score < best_score:`),
#   imported under the package name the suite uses (tests/golden.py puts custom_components on sys.path).
# Perturbation: `if np.isfinite(score) and score < best_score:` -> `if np.isfinite(score) and score <= best_score:` (the mutant), applied in memory: the function is re-compiled from its
#   own source with that one line replaced and called directly, or attached with mock.patch.object for the mutant
#   arm of a caller. Direction: the tie goes to the last-scored start instead of the first (x 0.5 -> 1.5); no golden plan moves.
# Inputs tried: a plateau objective (zero on [0,2]^4) with starts 0.5 and 1.5; null: the plateau tilted by 0.01*sum(x); golden winter_typical, summer_negative, flat.
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


OLD = "        if np.isfinite(score) and score < best_score:"
NEW = "        if np.isfinite(score) and score <= best_score:"
MUT = mutant("_multi_start_minimize", OLD, NEW)
bounds = [(0.0, 3.0)] * 4


def plateau(x, *a):
    """Zero on [0, 2]^4, rising past 2: every start inside the plateau is its own minimum, all scoring 0."""
    return float(np.sum(np.maximum(np.asarray(x) - 2.0, 0.0) ** 2))


def tilted(x, *a):
    return plateau(x) + 0.01 * float(np.sum(x))


cands = [np.full(4, 0.5), np.full(4, 1.5)]
rb, rm = O._multi_start_minimize(plateau, cands, bounds), MUT(plateau, cands, bounds)
print(f"RESULT score_tie={int(plateau(rb.x) == plateau(rm.x))}")
print(f"RESULT x_baseline={float(rb.x[0]):.6f}")
print(f"RESULT x_mutant={float(rm.x[0]):.6f}")
print(f"RESULT x_max_abs_diff={float(np.max(np.abs(rb.x - rm.x))):.6f}")
nb, nm = O._multi_start_minimize(tilted, cands, bounds), MUT(tilted, cands, bounds)
print(f"RESULT null_tilted_x_max_abs_diff={float(np.max(np.abs(nb.x - nm.x))):.6f}")
diffs = []
for prof, w in (("winter_typical", "winter_cold"), ("summer_negative", "summer_warm"), ("flat", "winter_mild")):
    r1 = golden_solve(prof, w)
    with mock.patch.object(O, "_multi_start_minimize", MUT):
        r2 = golden_solve(prof, w)
    diffs.append(float(np.max(np.abs(np.subtract(r1.power_schedule, r2.power_schedule)))))
print(f"RESULT golden_plan_max_abs_diff={max(diffs):.3g} kW (winter_typical, summer_negative, flat)")
tail()
