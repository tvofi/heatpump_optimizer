#!/usr/bin/env python3
# Metric: the value HeatPumpOptimizerCoordinator._async_load_energy_totals adopts as `_energy_totals_since` (published
#   as data["energy_totals_counting_since"]) after a restart whose energy-totals store holds a corrupt, truthy,
#   non-string `since` (the document is written to the stub Store's disk and read through the real QuarantiningStore
#   and store.load_mapping), on a real coordinator from tests/harness.py.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g03/probes/probe_16f76653.py
# EXPECTED RESULT since_<form>_baseline=None (ignored; the payload then stamps today) ; since_<form>_mutant=the corrupt value
# EXPECTED RESULT forms_moved=4 count (int 12345, list ["2026-01-01"], dict {"d": 1}, empty string "")
# EXPECTED RESULT null_delta=0 count (since "2026-01-01" and since null: both arms agree)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g03 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_load_energy_totals,
#   line 8419 `if isinstance(since, str) and since:`.
# Perturbation: key 16f7665306eebdf3 BOOLOP `and` -> `or`, in memory. Direction: None -> the corrupt value.
# Null control: a valid ISO date string and a null `since`.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, sys, textwrap, time, types
from types import SimpleNamespace
from unittest import mock

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
sys.path.insert(0, str(ROOT))
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402

CLS = co.HeatPumpOptimizerCoordinator
_T0 = (time.process_time(), time.thread_time())


def mutant(fn, line, old, new):
    """`fn` recompiled from its own source with production line `line` replaced (in memory only)."""
    lines, start = inspect.getsourcelines(fn)
    i = line - start
    assert lines[i].rstrip("\n") == old, f"anchor moved: {lines[i]!r}"
    lines[i] = new + "\n"
    ns = dict(co.__dict__)
    exec(compile(textwrap.dedent("".join(lines)), co.__file__, "exec"), ns)
    f = ns[fn.__name__]
    # rebound onto the module's own globals, so a patch of a module name reaches both arms alike
    return types.FunctionType(f.__code__, co.__dict__, f.__name__, f.__defaults__, f.__closure__)


def run(coro):
    return asyncio.run(coro)


def tail():
    p, t = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={p / t if t > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = sum(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
    except OSError:
        sw = -1
    print(f"RESULT swapins={sw} count")

import json  # noqa: E402
sys.path.insert(0, str(ROOT / "tests"))
from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.helpers import storage as stub_storage  # noqa: E402

MUT = mutant(CLS._async_load_energy_totals, 8419, "        if isinstance(since, str) and since:",
             "        if isinstance(since, str) or since:")


def restored_since(fn, since):
    stub_storage._DISK.clear()
    stub_storage._VERSIONS.clear()
    coord = CLS(FakeHass(), FakeEntry(data={}))
    stub_storage._DISK[coord._energy_store._key] = json.dumps({"since": since})
    run(fn(coord))
    return coord._energy_totals_since


moved = 0
for name, v in (("int", 12345), ("list", ["2026-01-01"]), ("dict", {"d": 1}), ("empty_str", "")):
    b, m = restored_since(CLS._async_load_energy_totals, v), restored_since(MUT, v)
    print(f"RESULT since_{name}_baseline={b!r}")
    print(f"RESULT since_{name}_mutant={m!r}")
    moved += b != m
print(f"RESULT forms_moved={moved} count")
print(f"RESULT null_delta={sum(int(restored_since(CLS._async_load_energy_totals, v) != restored_since(MUT, v)) for v in ('2026-01-01', None))} count")
tail()
