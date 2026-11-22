import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, sys, textwrap, time
from pathlib import Path
from unittest import mock

# The repository root is the working directory (the harness contract): the probe imports
# production from there, so a gate mutating the tree it is stored in never leaks into it.
ROOT = Path.cwd()
assert (ROOT / "custom_components" / "heatpump_optimizer" / "manifest.json").is_file(), "run from the repository root"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
_T0, _C0 = time.thread_time(), time.process_time()
from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402
C = co.HeatPumpOptimizerCoordinator


def mutant(name, old, new):
    """The method recompiled from its own source with the one-line mutant applied."""
    src = textwrap.dedent(inspect.getsource(getattr(C, name)))
    old, new = old.strip(), new.strip()
    assert src.count(old) == 1, f"anchor moved: {old!r}"
    ns = dict(co.__dict__)
    exec(compile(src.replace(old, new, 1), co.__file__, "exec"), ns)
    return ns[name]


BASE_CFG = {"tibber_token": "x", "weather_entity": "weather.home",
            "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"}


def coord(states=None, **extra):
    return C(FakeHass(dict(states or {})), FakeEntry(data={**BASE_CFG, **extra}))


def both(name, old, new, fn):
    """fn() on the baseline and under the mutant; an exception is the value (its type name)."""
    def run():
        try:
            return fn()
        except Exception as err:  # noqa: BLE001 - a raise is an observable outcome
            return f"raises {type(err).__name__}"
    base = run()
    with mock.patch.object(C, name, mutant(name, old, new)):
        mut = run()
    return base, mut


def tail():
    thread = time.thread_time() - _T0
    proc = time.process_time() - _C0
    print(f"RESULT thread_factor={proc / thread if thread > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        swap = [l for l in open("/proc/vmstat") if l.startswith("pswpin ")][0].split()[1]
    except Exception:  # noqa: BLE001
        swap = "na"
    print(f"RESULT swapins={swap}")
