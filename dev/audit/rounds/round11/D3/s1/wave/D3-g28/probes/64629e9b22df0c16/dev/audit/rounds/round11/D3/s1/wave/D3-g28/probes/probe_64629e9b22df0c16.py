#!/usr/bin/env python3
# Probe for mutant 64629e9b22df0c16 (box D3-g28, audit round 11, D3.M3/M4 full-gate survivor answer).
# Metric: the modulation fraction _power_fraction returns for a 0.15 kW step on a pump whose band is exactly the 0.1 kW threshold (min 0.1, max 0.2 kW).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g28/probes/probe_64629e9b22df0c16.py
# Expected (exact; counts and values are deterministic, tolerance 0 unless a float is printed to fewer digits):
#   RESULT band_is_exactly_threshold=1
#   RESULT fraction_baseline=0.500000
#   RESULT fraction_mutant=0.750000
#   RESULT fraction_abs_diff=0.250000
#   RESULT null_zero_floor_diff=0
#   RESULT null_ordinary_band_diff=0
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
# Machine: cloud box D3-g28, 4 vCPU Intel(R) Xeon(R) Processor @ 2.10GHz, 16 GB; run beside its own full gate
#   (load1 1.0-2.1), so any timing here is provisional; the metrics are counts and values, contention-immune.
# Instrumented symbol: heatpump_optimizer.optimizer:_power_fraction (custom_components/heatpump_optimizer/optimizer.py:2170 `if p_max - p_min >= _MIN_MODULATION_BAND_KW:`),
#   imported under the package name the suite uses (tests/golden.py puts custom_components on sys.path).
# Perturbation: `if p_max - p_min >= _MIN_MODULATION_BAND_KW:` -> `if p_max - p_min > _MIN_MODULATION_BAND_KW:` (the mutant), applied in memory: the function is re-compiled from its
#   own source with that one line replaced and called directly, or attached with mock.patch.object for the mutant
#   arm of a caller. Direction: up: 0.5 -> 0.75 (graded against max power instead of the band).
# Inputs tried: min/max 0.1/0.2 kW at 0.15 kW; null: 0.0/0.1 kW at 0.05 kW (both branches agree) and 0.6/3.0 kW at 1.2 kW.
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


from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402
OLD = "    if p_max - p_min >= _MIN_MODULATION_BAND_KW:"
NEW = "    if p_max - p_min > _MIN_MODULATION_BAND_KW:"
MUT = mutant("_power_fraction", OLD, NEW)


def pf(fn, lo, hi, power):
    return fn(power, ThermalParameters(min_electrical_power=lo, max_electrical_power=hi))


print(f"RESULT band_is_exactly_threshold={int(0.2 - 0.1 == O._MIN_MODULATION_BAND_KW)}")
b, m = pf(O._power_fraction, 0.1, 0.2, 0.15), pf(MUT, 0.1, 0.2, 0.15)
print(f"RESULT fraction_baseline={b:.6f}")
print(f"RESULT fraction_mutant={m:.6f}")
print(f"RESULT fraction_abs_diff={abs(b - m):.6f}")
# Null: a 0.1 kW band that starts at 0 grades identically on both branches; an ordinary band never
# reaches the boundary.
print(f"RESULT null_zero_floor_diff={abs(pf(O._power_fraction, 0.0, 0.1, 0.05) - pf(MUT, 0.0, 0.1, 0.05)):.6f}")
print(f"RESULT null_ordinary_band_diff={abs(pf(O._power_fraction, 0.6, 3.0, 1.2) - pf(MUT, 0.6, 3.0, 1.2)):.6f}")
tail()
