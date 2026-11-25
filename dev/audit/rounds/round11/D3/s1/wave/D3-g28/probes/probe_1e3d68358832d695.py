#!/usr/bin/env python3
# Probe for mutant 1e3d68358832d695 (box D3-g28, audit round 11, D3.M3/M4 full-gate survivor answer).
# Metric: calls of time.sleep(0.002), the GIL yield between consecutive L-BFGS-B starts, during one multi-start (direct: 3 starts) and during one golden winter_typical HeatPumpOptimizer.optimize.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g28/probes/probe_1e3d68358832d695.py
# Expected (exact; counts and values are deterministic, tolerance 0 unless a float is printed to fewer digits):
#   RESULT yields_baseline=5 calls
#   RESULT yields_mutant=3 calls (the 2 between-start yields gone)
#   RESULT x_max_abs_diff=0
#   RESULT null_one_start_yields_delta=0
#   RESULT golden_yields_baseline=8 calls
#   RESULT golden_yields_mutant=5 calls
#   RESULT golden_plan_max_abs_diff=0 kW
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
# Machine: cloud box D3-g28, 4 vCPU Intel(R) Xeon(R) Processor @ 2.10GHz, 16 GB; run beside its own full gate
#   (load1 1.0-2.1), so any timing here is provisional; the metrics are counts and values, contention-immune.
# Instrumented symbol: heatpump_optimizer.optimizer:_multi_start_minimize (custom_components/heatpump_optimizer/optimizer.py:1957 `if solve_index:`),
#   imported under the package name the suite uses (tests/golden.py puts custom_components on sys.path).
# Perturbation: `if solve_index:` -> `if False:` (the mutant), applied in memory: the function is re-compiled from its
#   own source with that one line replaced and called directly, or attached with mock.patch.object for the mutant
#   arm of a caller. Direction: down: between-start yields 2 -> 0 per multi-start (8 -> 5 in one golden solve); plan unchanged.
# Inputs tried: a 4-dim quadratic with 3 starts; 1 start (null); golden winter_typical solve.
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


OLD, NEW = "        if solve_index:", "        if False:"
MUT = mutant("_multi_start_minimize", OLD, NEW)
bounds = [(0.0, 3.0)] * 4
three = [np.full(4, 0.2), np.full(4, 1.5), np.full(4, 2.8)]


def quad(x, *a):
    return float(np.sum((np.asarray(x) - 1.0) ** 2))


real_sleep = time.sleep


def count_yields(fn, *a, **k):
    """Calls of time.sleep(0.002), the between-starts GIL yield, during fn."""
    n = [0]

    def spy(s):
        if s == 0.002:
            n[0] += 1
        return real_sleep(s)
    with mock.patch.object(O._time_mod, "sleep", spy):
        out = fn(*a, **k)
    return n[0], out


nb, rb = count_yields(O._multi_start_minimize, quad, three, bounds)
nm, rm = count_yields(MUT, quad, three, bounds)
print(f"RESULT yields_baseline={nb} calls")
print(f"RESULT yields_mutant={nm} calls")
print(f"RESULT x_max_abs_diff={float(np.max(np.abs(rb.x - rm.x))):.3g}")
n1b, _ = count_yields(O._multi_start_minimize, quad, three[:1], bounds)
n1m, _ = count_yields(MUT, quad, three[:1], bounds)
print(f"RESULT null_one_start_yields_delta={n1b - n1m} calls")
# The realistic arm: one golden winter_typical solve through HeatPumpOptimizer.optimize.
gb, r1 = count_yields(golden_solve)
with mock.patch.object(O, "_multi_start_minimize", MUT):
    gm, r2 = count_yields(golden_solve)
print(f"RESULT golden_yields_baseline={gb} calls")
print(f"RESULT golden_yields_mutant={gm} calls")
print(f"RESULT golden_plan_max_abs_diff={float(np.max(np.abs(np.subtract(r1.power_schedule, r2.power_schedule)))):.3g} kW")
tail()
