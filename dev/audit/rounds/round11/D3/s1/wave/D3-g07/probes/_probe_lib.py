"""Shared plumbing for box D3-g07's probes (round 11, D3-s1 wave): no measurement of its own.

Each probe_<key>.py imports this, builds the baseline symbol and the one-line mutant of it in
memory (the mutated method's source re-compiled in a copy of coordinator.py's globals, never an
on-disk edit), drives both on the same input and prints RESULT lines. Run from the repository
root with PYTHONPATH=tests/hastub.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect
import sys
import textwrap
import time
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
for p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components", ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

_T0_PROC = time.process_time()
_T0_THREAD = time.thread_time()

from heatpump_optimizer import coordinator as co  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402

Coord = co.HeatPumpOptimizerCoordinator
BASE_CFG = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
    "target_temperature": 21.0,
    "min_temperature": 17.0,
    "max_temperature": 23.0,
}


def coord(states=None, **cfg):
    """A live coordinator over the fake bus (golden.py's coordinator_scenarios base config)."""
    return Coord(FakeHass(states or {}), FakeEntry(data=dict(BASE_CFG, **cfg)))


def mutant(method: str, old: str, new: str):
    """HeatPumpOptimizerCoordinator.<method> with the one line whose text is `old` replaced by `new`."""
    fn = getattr(Coord, method)
    fn = getattr(fn, "__wrapped__", fn)
    lines = inspect.getsource(fn).splitlines(keepends=True)
    hits = [i for i, ln in enumerate(lines) if ln.strip() == old.strip()]
    assert len(hits) == 1, f"anchor {old!r} found {len(hits)} times in {method}"
    i = hits[0]
    indent = lines[i][: len(lines[i]) - len(lines[i].lstrip())]
    lines[i] = indent + new.strip() + "\n"
    src = textwrap.dedent("".join(lines))
    ns = dict(co.__dict__)
    exec(compile(src, co.__file__, "exec"), ns)
    return ns[fn.__name__]


def baseline(method: str):
    fn = getattr(Coord, method)
    return getattr(fn, "__wrapped__", fn)


def footer():
    """thread_factor, load1 and swapins, as the harness contract requires."""
    proc = time.process_time() - _T0_PROC
    thr = time.thread_time() - _T0_THREAD
    print(f"RESULT thread_factor={proc / max(thr, 1e-9):.3f}")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    except OSError:
        print("RESULT load1=nan")
    swap = "nan"
    try:
        for ln in Path("/proc/vmstat").read_text().splitlines():
            if ln.startswith("pswpin "):
                swap = ln.split()[1]
    except OSError:
        pass
    print(f"RESULT swapins={swap}")
