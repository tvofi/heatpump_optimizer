#!/usr/bin/env python3
# Box D3-g32 (round 11, seat D3-s1), D3 step 4 probe for full-gate survivor b539d4504385a139.
# Metric: reason string prices_from_entity_state returns for an unknown/unavailable/blank state with empty-dict or non-dict attributes.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_b539d4504385a139.py   (from the repository root)
# EXPECTED: inputs_moved=4 of 5 ('Price entity is empty' -> 'Price entity published no today/tomorrow series'); null_delta=0.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g32, 4 vCPU Intel Xeon @ 2.10GHz, venv-ci CPython 3.14.
# Instrumented symbol: custom_components.heatpump_optimizer.price_model:prices_from_entity_state, line 825.
# Perturbation: key b539d4504385a139 (BOOLOP) `isinstance(attrs, dict) and attrs` -> `or attrs`. Direction: empty-entity reason -> no-series reason; applied in memory (the function re-compiled from its own source with the one line swapped), never on disk.
# Null control: a numeric state with a populated series, where the guard is not consulted.
# Counts are exact (no timing); thread_factor/load1/swapins are printed per the harness contract.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time
from pathlib import Path
from unittest import mock


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
_T0 = (time.process_time(), time.thread_time())


def mutate(owner, name, old, new):
    """Re-compile ``owner.name`` from its own source with the one-line mutant applied (in memory)."""
    fn = getattr(owner, name)
    mod = sys.modules[fn.__module__]
    src = inspect.getsource(fn)  # the anchor carries the file's own indentation
    assert src.count(old) == 1, f"anchor moved: {old!r}"
    ns = dict(mod.__dict__)
    exec(compile(textwrap.dedent(src.replace(old, new, 1)), mod.__file__, "exec"), ns)
    return ns[name]


def tail():
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


from types import SimpleNamespace as NS
from custom_components.heatpump_optimizer import price_model as pm

mut = mutate(pm, "prices_from_entity_state", "        isinstance(attrs, dict) and attrs", "        isinstance(attrs, dict) or attrs")
cases = {
    "unknown_empty_dict": NS(state="unknown", attributes={}),
    "unavailable_empty_dict": NS(state="unavailable", attributes={}),
    "blank_empty_dict": NS(state="", attributes={}),
    "unknown_none_attrs": NS(state="unknown", attributes=None),
    "unknown_tuple_attrs": NS(state="unknown", attributes=(("today", []),)),
}
moved = 0
for name, st in cases.items():
    b, m = pm.prices_from_entity_state(st), mut(st)
    moved += b != m
    print(f"RESULT reason_baseline_{name}={b!r}")
    print(f"RESULT reason_mutant_{name}={m!r}")
print(f"RESULT inputs_moved={moved} count")
# null control: a numeric state with a populated series, where the guard is not consulted
ok = NS(state="1.2", attributes={"today": [1.0] * 24})
print(f"RESULT null_delta={int(pm.prices_from_entity_state(ok) != mut(ok))} count")
tail()
