#!/usr/bin/env python3
# Probe for D3.M3 full-gate survivor d6023ebc83ac4317 (box D3-g41, round 11, seat D3-s1).
# Metric: count of inputs on which ThermalModel._batch_cop's COP differs between `T_buf > ref` and `T_buf >= ref`,
#   with tanks exactly at, and one ulp around, cop_flow_reference_temp.
# Command (from the tree root): PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g41/probes/probe_d6023ebc83ac4317.py
# EXPECTED RESULT moved_inputs=0 count (at T_buf == ref, carnot_flow == carnot_ref, so max(0.25, 1.0) == 1.0)
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel._batch_cop, line 4482 `T_buf > ref,`.
# Perturbation: key d6023ebc83ac4317 CMP_BOUND `T_buf > ref,` -> `T_buf >= ref,`, in memory. Direction if it moved: the
#   tie tank's multiplier 1.0 -> carnot_flow / carnot_ref.
# Null control: baseline against itself.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g41 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB).
# Each RESULT is computed by calling the production symbol on the stated inputs, both arms in one process.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time, types
from pathlib import Path
from unittest import mock

_T0W, _T0C = time.perf_counter(), time.process_time()


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
import numpy as np  # noqa: E402


def mutant(fn, old, new):
    """``fn`` re-compiled from its own source with the one-line mutant applied, bound to the live module globals."""
    src = textwrap.dedent(inspect.getsource(fn))
    o, n = old.strip(), new.strip()
    assert src.count(o) == 1, f"anchor moved: {o!r}"
    mod = sys.modules[fn.__module__]
    ns = {}
    exec(compile(src.replace(o, n, 1), mod.__file__, "exec"), dict(mod.__dict__), ns)
    f = ns[fn.__name__]
    g = types.FunctionType(f.__code__, mod.__dict__, f.__name__, f.__defaults__, f.__closure__)
    g.__kwdefaults__ = f.__kwdefaults__
    return g


def outcome(fn, *a, **k):
    """('ok', value) or ('raise', exception type name)."""
    try:
        return ("ok", fn(*a, **k))
    except Exception as e:  # noqa: BLE001 - the exception type IS the measured outcome
        return ("raise", type(e).__name__)


def same(a, b):
    if a[0] != b[0]:
        return False
    if a[0] == "raise":
        return a[1] == b[1]
    x, y = a[1], b[1]
    if x is None or y is None:
        return x is None and y is None
    if hasattr(x, "__dataclass_fields__"):
        import dataclasses
        return all(same(("ok", getattr(x, f.name)), ("ok", getattr(y, f.name))) for f in dataclasses.fields(x))
    xa, ya = np.asarray(x), np.asarray(y)
    if xa.dtype == object or ya.dtype == object:
        return bool(x == y)
    return xa.shape == ya.shape and bool(np.array_equal(xa, ya, equal_nan=True))


def show(o):
    if o[0] == "raise":
        return f"raise:{o[1]}"
    v = o[1]
    if v is None:
        return "None"
    if isinstance(v, np.ndarray):
        return np.array2string(v, precision=6, separator=",").replace(" ", "")
    return repr(v)


def tail():
    w, c = time.perf_counter() - _T0W, time.process_time() - _T0C
    print(f"RESULT thread_factor={c / w if w > 0 else 0.0:.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = "na"
    try:
        for line in open("/proc/vmstat"):
            if line.startswith("pswpin "):
                sw = line.split()[1]
    except OSError:
        pass
    print(f"RESULT swapins={sw} count")

from custom_components.heatpump_optimizer import thermal_model as tm, defrost as dfr  # noqa: E402
TM = tm.ThermalModel
T_BUF = np.array([25.0, 35.0, 40.0, 50.0, 60.0])
OUTS = (-25.0, -10.0, -2.0, 0.0, 7.0, 15.0, 20.0, 26.9, 27.0, 27.5, 30.0, 35.0)


def batch(model, fn, out, hum, tb, elig):
    with mock.patch.object(TM, "_batch_cop", fn):
        return outcome(model._batch_cop, out, hum, tb, elig)


def derate(grid_fn, n=100):
    d = dfr.DefrostDerate(factors=dfr._grid(1.0), counts=dfr._grid(n))
    for i in range(len(d.factors)):
        for j in range(len(d.factors[i])):
            d.factors[i][j] = grid_fn(i, j)
    return d

mut = mutant(TM._batch_cop, "                    T_buf > ref,", "                    T_buf >= ref,")
tried = moved = 0
for ref in (35.0, 20.0, 50.0, 7.0, 7.3):
    tb = np.array([ref, np.nextafter(ref, -np.inf), np.nextafter(ref, np.inf), ref - 10.0, ref + 10.0])
    model = TM(tm.ThermalParameters(two_zone_enabled=True, cop_flow_carnot=True, cop_flow_reference_temp=ref))
    for o in OUTS:
        tried += 1
        moved += not same(batch(model, TM._batch_cop, o, None, tb, True), batch(model, mut, o, None, tb, True))
print(f"RESULT inputs_tried={tried} count (each a 5-tank row with the tie)")
print(f"RESULT moved_inputs={moved} count")
tail()
