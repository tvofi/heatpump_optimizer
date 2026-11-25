#!/usr/bin/env python3
# Probe for mutant e670e7e026a9f4ec (box D3-g28, audit round 11, D3.M3/M4 full-gate survivor answer).
# Metric: the savings percentage for savings outside [-baseline, baseline], and the published savings_percentage of six golden HeatPumpOptimizer.optimize cells.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g28/probes/probe_e670e7e026a9f4ec.py
# Expected (exact; counts and values are deterministic, tolerance 0 unless a float is printed to fewer digits):
#   RESULT over_pct_baseline=100.000 %
#   RESULT over_pct_mutant=200.000 %
#   RESULT under_pct_baseline=-100.000 %
#   RESULT under_pct_mutant=-300.000 %
#   RESULT null_inside_band_diff=0
#   RESULT golden_cells_moved=0 of 6
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
# Machine: cloud box D3-g28, 4 vCPU Intel(R) Xeon(R) Processor @ 2.10GHz, 16 GB; run beside its own full gate
#   (load1 1.0-2.1), so any timing here is provisional; the metrics are counts and values, contention-immune.
# Instrumented symbol: heatpump_optimizer.optimizer:_savings_percentage (custom_components/heatpump_optimizer/optimizer.py:2146 `return float(np.clip(savings / baseline_cost * 100.0, -100.0, 100.0))`),
#   imported under the package name the suite uses (tests/golden.py puts custom_components on sys.path).
# Perturbation: `return float(np.clip(savings / baseline_cost * 100.0, -100.0, 100.0))` -> `return float((savings / baseline_cost * 100.0))` (the mutant), applied in memory: the function is re-compiled from its
#   own source with that one line replaced and called directly, or attached with mock.patch.object for the mutant
#   arm of a caller. Direction: out of the [-100, 100] band (100 -> 200 %, -100 -> -300 %); no golden cell reaches it.
# Inputs tried: (savings, baseline) (2, 1), (-3, 1); null (0.4, 1); golden summer_typical +/-dhw, summer_negative +/-dhw, shoulder, winter_typical.
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


OLD = "    return float(np.clip(savings / baseline_cost * 100.0, -100.0, 100.0))"
NEW = "    return float((savings / baseline_cost * 100.0))"
MUT = mutant("_savings_percentage", OLD, NEW)
for tag, s, c in (("over", 2.0, 1.0), ("under", -3.0, 1.0)):
    print(f"RESULT {tag}_pct_baseline={O._savings_percentage(s, c):.3f} %")
    print(f"RESULT {tag}_pct_mutant={MUT(s, c):.3f} %")
print(f"RESULT null_inside_band_diff={abs(O._savings_percentage(0.4, 1.0) - MUT(0.4, 1.0)):.3f} %")
# The plan arm: HeatPumpOptimizer.optimize on six golden.make cells; savings_percentage is what the
# plan_savings_percentage sensor publishes.
cells = [("summer_typical", "summer_warm", True), ("summer_typical", "summer_warm", False),
         ("summer_negative", "summer_warm", True), ("summer_negative", "summer_warm", False),
         ("shoulder", "shoulder", False), ("winter_typical", "winter_cold", True)]
moved = []
for prof, w, dhw in cells:
    r1 = golden_solve(prof, w, dhw=dhw)
    with mock.patch.object(O, "_savings_percentage", MUT):
        r2 = golden_solve(prof, w, dhw=dhw)
    print(f"RESULT cell_{prof}_{'dhw' if dhw else 'nodhw'}_pct_baseline_mutant={r1.savings_percentage:.2f},{r2.savings_percentage:.2f}")
    if abs(r1.savings_percentage - r2.savings_percentage) > 1e-9:
        moved.append(prof + ("_dhw" if dhw else "_nodhw"))
print(f"RESULT golden_cells={len(cells)}")
print(f"RESULT golden_cells_moved={len(moved)} {moved}")
tail()
