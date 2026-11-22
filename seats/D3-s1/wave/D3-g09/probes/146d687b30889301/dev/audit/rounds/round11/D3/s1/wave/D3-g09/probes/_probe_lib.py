"""Shared plumbing for box D3-g09's step-4 probes (audit round 11, seat D3-s1).

Not a harness on its own: each probe_<key>.py carries its own header (metric, command, expected,
baseline, machine, instrumented symbol, perturbation) and imports this for three things only:
the thread pin, a coordinator over tests/harness.py's FakeHass, and the in-memory mutant (the
method recompiled from its own source with the one mutated line swapped, attached with
mock.patch.object for the mutant arm only, so no file on disk changes).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time
from pathlib import Path


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
for _p in (str(ROOT / "tests"), str(ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
_T0 = (time.process_time(), time.thread_time())

from harness import FakeHass, FakeEntry  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from custom_components.heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

BASE_CFG = {"tibber_token": "x", "weather_entity": "weather.home"}


def coord(states=None, **cfg):
    """A live coordinator over the fake bus (tests/features.py:_t2_coord's two-liner)."""
    return HeatPumpOptimizerCoordinator(FakeHass(states), FakeEntry(data=dict(BASE_CFG, **cfg)))


def mutant(cls, name, old, new, module=coord_mod):
    """cls.<name> recompiled from its own source with the single line `old` replaced by `new`."""
    fn = inspect.unwrap(getattr(cls, name))
    src = textwrap.dedent(inspect.getsource(fn))
    assert src.count(old) == 1, f"anchor line moved: {old!r}"
    ns = dict(module.__dict__)
    exec(compile(src.replace(old, new, 1), module.__file__, "exec"), ns)
    return ns[fn.__name__]


def trailer():
    """The contract's closing RESULT lines: thread_factor, load1, swapins."""
    pc, tc = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        for line in open("/proc/vmstat"):
            if line.startswith("pswpin "):
                sw = int(line.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={sw}")
