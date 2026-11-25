#!/usr/bin/env python3
# Metric: the survival fraction stored_heat_survival returns when its exponent 0.5*ua*span/demand exceeds 700, and that value's effect on a terminal cost it is added into.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_f062e0cc415ee33e.py [--reach]
#   (--reach also solves the 50 tests/golden.py scenarios with recording spies: reach_sweep.py beside this file)
# EXPECTED no arm raises (raises=0 both arms)
# EXPECTED exponent 720: baseline exp(-700)=9.86e-305, mutant ~2.0e-313: the float moves
# EXPECTED cost_delta_after_adding=0.0 (the buffer credit term mass*survival*deficit added to a 0.01 SEK plan cost: identical floats)
# EXPECTED null_delta=0 count (exponent <= 700)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g29 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:stored_heat_survival line 3186 `math.exp(-min(0.5 * ua * span / demand, 700.0))`.
# Perturbation: key f062e0cc415ee33e CLAMP_DROP `min(..., 700.0)` dropped, in memory. Direction: exp(-700) -> exp(-x) < 1e-304 (or 0.0).
# Null control: exponent 1, 100, 700 exactly: identical.
# Values are exact (deterministic); no timing is measured.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, math, sys, time
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

_CPU0, _THR0 = time.process_time(), time.thread_time()


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
for _p in (str(ROOT), str(ROOT / "tests"), str(ROOT / "custom_components")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import numpy as np  # noqa: E402
# The package as tests/golden.py imports it, so the reach sweep's spies and this probe share one module.
from heatpump_optimizer import optimizer as opt  # noqa: E402
from heatpump_optimizer import price_model as pm  # noqa: E402


def mutant(mod, name, lineno, old, new):
    """`name` re-compiled from its own source with line `lineno` (exactly `old`) replaced by `new`."""
    fn = getattr(mod, name)
    lines, start = inspect.getsourcelines(fn)
    i = lineno - start
    assert lines[i].rstrip("\n") == old, f"anchor moved: {lines[i]!r} != {old!r}"
    lines[i] = new + "\n"
    ns = dict(mod.__dict__)
    exec(compile("\n" * (start - 1) + "".join(lines), mod.__file__, "exec"), ns)
    return ns[name]


def call(fn, *a, **k):
    """The value, or the exception's type name: a raise is an observable outcome too."""
    try:
        return fn(*a, **k)
    except Exception as exc:  # noqa: BLE001
        return f"raises {type(exc).__name__}"


def same(a, b):
    if isinstance(a, float) and isinstance(b, float):
        return a == b or (math.isnan(a) and math.isnan(b))
    return a == b


def footer():
    cpu, thr = time.process_time() - _CPU0, time.thread_time() - _THR0
    print(f"RESULT thread_factor={cpu / thr if thr > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        swapins = int([l.split()[1] for l in open("/proc/vmstat") if l.startswith("pswpin")][0])
    except Exception:  # noqa: BLE001
        swapins = -1
    print(f"RESULT swapins={swapins} count")


def reach(symbol):
    """--reach: the shared golden-matrix sweep (reach_sweep.py beside this probe) for `symbol`."""
    if "--reach" not in sys.argv:
        print("RESULT reach=skipped (pass --reach to solve the 50 golden scenarios with spies)")
        return None
    import importlib.util
    spec = importlib.util.spec_from_file_location("reach_sweep", Path(__file__).resolve().parent / "reach_sweep.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rec = mod.sweep({symbol})
    mod.print_reach(rec)
    return rec

mut = mutant(opt, "stored_heat_survival", 3186, '    return float(math.exp(-min(0.5 * ua * span / demand, 700.0)))', '    return float(math.exp(-(0.5 * ua * span / demand)))')
amb = opt.DHW_COOLING_REFERENCE_AMBIENT_TEMP

ua, cap = 1.0, amb + 30.0           # span 30 K: exponent = 15 / demand
raises = [0, 0]; moved = 0; worst = 0.0; diffs = []
for x in (720.0, 745.0, 800.0, 1e6, 1e301):
    d = 15.0 / x
    b, m = call(opt.stored_heat_survival, ua, cap, d), call(mut, ua, cap, d)
    raises[0] += isinstance(b, str); raises[1] += isinstance(m, str)
    print(f"RESULT exponent{x:g}_baseline={b!r} mutant={m!r}")
    moved += not same(b, m)
    if not isinstance(b, str) and not isinstance(m, str):
        worst = max(worst, abs(b - m))
        # The consumer: the buffer's credit coefficient mass * survival times a deficit, summed into a plan cost.
        term_b, term_m = 30.0 * b * 40.0, 30.0 * m * 40.0
        diffs.append((0.01 + term_b) - (0.01 + term_m))
d = 5e-324                          # the smallest positive demand: 15 / 5e-324 overflows
b, m = call(opt.stored_heat_survival, ua, cap, d), call(mut, ua, cap, d)
print(f"RESULT exponent_overflow_baseline={b!r} mutant={m!r}")
raises[0] += isinstance(b, str); raises[1] += isinstance(m, str)
print(f"RESULT raises_baseline={raises[0]} raises_mutant={raises[1]} count")
print(f"RESULT moved={moved} count of 5 (the float, all below 1e-304)")
print(f"RESULT max_abs_survival_delta={worst:.3e}")
print(f"RESULT cost_delta_after_adding={max(abs(v) for v in diffs):.1f} (0.01 SEK plan cost + 30 kWh/K * survival * 40 K)")
nd = sum(not same(call(opt.stored_heat_survival, ua, cap, 15.0 / x), call(mut, ua, cap, 15.0 / x)) for x in (1.0, 100.0, 700.0))
print(f"RESULT null_delta={nd} count")

# Reach: the only caller (optimizer.py:3593) passes caps["buffer"], set at optimizer.py:6031 to
# min(buffer_max_temp, max(_buffer_charge_ceiling, initial)), where the ceiling bisects in
# [max(20, cop_flow_reference_temp), buffer_max_temp] and the config flow bounds buffer_max_temperature to 40..90 C.
from heatpump_optimizer.thermal_model import ThermalParameters
print(f"RESULT reach_ambient={amb} C reach_cop_flow_reference_default={ThermalParameters().cop_flow_reference_temp} C")
reach("stored_heat_survival")
footer()
