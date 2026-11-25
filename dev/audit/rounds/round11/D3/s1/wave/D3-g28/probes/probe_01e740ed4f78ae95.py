#!/usr/bin/env python3
# Probe for mutant 01e740ed4f78ae95 (box D3-g28, audit round 11, D3.M3/M4 full-gate survivor answer).
# Metric: what _price_ranked_start delivers at dt = 0 (energy 1 kWh, p_max 2 kW): a schedule or a raise.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g28/probes/probe_01e740ed4f78ae95.py
# Expected (exact; counts and values are deterministic, tolerance 0 unless a float is printed to fewer digits):
#   RESULT dt0_baseline=ok:[0.0, 0.0, 0.0, 0.0]
#   RESULT dt0_mutant=raise:ZeroDivisionError: division by zero
#   RESULT dt0_mutant_raises=1
#   RESULT null_dt_quarter_diff=0
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
# Machine: cloud box D3-g28, 4 vCPU Intel(R) Xeon(R) Processor @ 2.10GHz, 16 GB; run beside its own full gate
#   (load1 1.0-2.1), so any timing here is provisional; the metrics are counts and values, contention-immune.
# Instrumented symbol: heatpump_optimizer.optimizer:_price_ranked_start (custom_components/heatpump_optimizer/optimizer.py:2126 `if energy_kwh <= 0 or p_max <= 0 or dt <= 0:`),
#   imported under the package name the suite uses (tests/golden.py puts custom_components on sys.path).
# Perturbation: `if energy_kwh <= 0 or p_max <= 0 or dt <= 0:` -> `if energy_kwh <= 0 or p_max <= 0 or dt < 0:` (the mutant), applied in memory: the function is re-compiled from its
#   own source with that one line replaced and called directly, or attached with mock.patch.object for the mutant
#   arm of a caller. Direction: zero schedule -> ZeroDivisionError.
# Inputs tried: dt 0 on a 4-step day; null: dt 0.25.
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


OLD = "    if energy_kwh <= 0 or p_max <= 0 or dt <= 0:"
NEW = "    if energy_kwh <= 0 or p_max <= 0 or dt < 0:"
MUT = mutant("_price_ranked_start", OLD, NEW)
p = np.array([0.3, 0.1, 0.2, 0.4])
b, m = outcome(O._price_ranked_start, p, 1.0, 2.0, 0.0), outcome(MUT, p, 1.0, 2.0, 0.0)
print(f"RESULT dt0_baseline={b[0]}:{b[1] if b[0] == 'raise' else b[1].tolist()}")
print(f"RESULT dt0_mutant={m[0]}:{m[1] if m[0] == 'raise' else m[1].tolist()}")
print(f"RESULT dt0_mutant_raises={int(m[0] == 'raise')}")
print(f"RESULT null_dt_quarter_diff={float(np.max(np.abs(O._price_ranked_start(p, 1.0, 2.0, 0.25) - MUT(p, 1.0, 2.0, 0.25)))):.3g}")
tail()
