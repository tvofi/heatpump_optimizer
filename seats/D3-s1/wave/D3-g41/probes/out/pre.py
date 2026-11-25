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
