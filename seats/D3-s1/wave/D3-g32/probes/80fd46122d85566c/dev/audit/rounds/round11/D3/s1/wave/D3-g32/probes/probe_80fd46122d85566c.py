#!/usr/bin/env python3
# Box D3-g32 (round 11, seat D3-s1), D3 step 4 probe for full-gate survivor 80fd46122d85566c.
# Metric: reason string prices_from_entity_state returns for a None state.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_80fd46122d85566c.py   (from the repository root)
# EXPECTED: none_state_inputs_moved=0 (both 'Price entity is empty'); other_states_moved=0.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g32, 4 vCPU Intel Xeon @ 2.10GHz, venv-ci CPython 3.14.
# Instrumented symbol: custom_components.heatpump_optimizer.price_model:prices_from_entity_state, line 820.
# Perturbation: key 80fd46122d85566c (GUARD_OFF) `if state is None:` -> `if False:`. Direction: none found; the fall-through reads getattr(None,'state','') == '' and returns the same string; applied in memory (the function re-compiled from its own source with the one line swapped), never on disk.
# Null control: non-None states, where the guard is false either way.
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

mut = mutate(pm, "prices_from_entity_state", "    if state is None:", "    if False:")
moved = 0
for vat, sur in ((1.0, 0.0), (1.25, 0.3), (0.0, -1.0)):
    b = pm.prices_from_entity_state(None, vat, sur)
    m = mut(None, vat, sur)
    moved += b != m
    print(f"RESULT none_state_baseline_vat{vat}={b!r}")
    print(f"RESULT none_state_mutant_vat{vat}={m!r}")
print(f"RESULT none_state_inputs_moved={moved} count")
# the other inputs that reach line 820 (guard false either way): a non-None state
others = [NS(state="unknown", attributes={}), NS(state="", attributes=None), NS(state="1.2", attributes={"today": []}),
          NS(state="unavailable", attributes={"raw_today": [{"start": "2026-01-14T00:00:00+00:00", "value": 1.0}]})]
print(f"RESULT other_states_moved={sum(pm.prices_from_entity_state(s) != mut(s) for s in others)} count")
tail()
