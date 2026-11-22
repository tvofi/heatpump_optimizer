#!/usr/bin/env python3
# Probe for mutant 09e80cfe3036223e (box D3-g28, audit round 11, D3.M3/M4 full-gate survivor answer).
# Metric: max abs difference of the start schedule over 20000 random (prices, energy, p_max, dt) draws, and of the solved plan on three golden scenarios.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g28/probes/probe_09e80cfe3036223e.py
# Expected (exact; counts and values are deterministic, tolerance 0 unless a float is printed to fewer digits):
#   RESULT inputs_tried=20000
#   RESULT inputs_moved=195
#   RESULT max_abs_diff=1.47e-15 kW (a negative residue written after the break point)
#   RESULT golden_plan_max_abs_diff=0 kW
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
# Machine: cloud box D3-g28, 4 vCPU Intel(R) Xeon(R) Processor @ 2.10GHz, 16 GB; run beside its own full gate
#   (load1 1.0-2.1), so any timing here is provisional; the metrics are counts and values, contention-immune.
# Instrumented symbol: heatpump_optimizer.optimizer:_price_ranked_start (custom_components/heatpump_optimizer/optimizer.py:2130 `if remaining <= 0:`),
#   imported under the package name the suite uses (tests/golden.py puts custom_components on sys.path).
# Perturbation: `if remaining <= 0:` -> `if False:` (the mutant), applied in memory: the function is re-compiled from its
#   own source with that one line replaced and called directly, or attached with mock.patch.object for the mutant
#   arm of a caller. Direction: down: a ~-1e-15 kW entry appears after a negative float residue; no golden plan moves.
# Inputs tried: 20000 seeded random draws (n 2..96, p_max 0.3..9 kW, dt 0.05..1 h, energy up to n*p_max*dt); golden winter_typical, summer_negative, shoulder.
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


OLD, NEW = "        if remaining <= 0:", "        if False:"
MUT = mutant("_price_ranked_start", OLD, NEW)
rng = np.random.default_rng(13)
tried = moved = 0
worst = 0.0
example = None
for _ in range(20000):
    n = int(rng.integers(2, 97))
    p = rng.normal(size=n)
    pm = float(rng.choice([1.0, 2.0, 3.5, 6.0, float(rng.uniform(0.3, 9.0))]))
    dt = float(rng.choice([0.25, 0.5, 1.0, 1 / 3, float(rng.uniform(0.05, 1.0))]))
    e = float(rng.uniform(0.0, pm * dt * n))
    b, m = O._price_ranked_start(p, e, pm, dt), MUT(p, e, pm, dt)
    tried += 1
    d = float(np.max(np.abs(b - m)))
    if d > 0:
        moved += 1
        if d > worst:
            worst, example = d, (n, pm, dt, e, float(np.min(m)))
print(f"RESULT inputs_tried={tried}")
print(f"RESULT inputs_moved={moved}")
print(f"RESULT max_abs_diff={worst:.3g} kW")
print(f"RESULT example_n_pmax_dt_energy_mutant_min={example}")
# The plan arm: every caller hands the start to L-BFGS-B under bounds [0, p_max], which clips x0.
diffs = []
for prof, w in (("winter_typical", "winter_cold"), ("summer_negative", "summer_warm"), ("shoulder", "shoulder")):
    r1 = golden_solve(prof, w)
    with mock.patch.object(O, "_price_ranked_start", MUT):
        r2 = golden_solve(prof, w)
    diffs.append(float(np.max(np.abs(np.subtract(r1.power_schedule, r2.power_schedule)))))
print(f"RESULT golden_plan_max_abs_diff={max(diffs):.3g} kW (winter_typical, summer_negative, shoulder)")
tail()
