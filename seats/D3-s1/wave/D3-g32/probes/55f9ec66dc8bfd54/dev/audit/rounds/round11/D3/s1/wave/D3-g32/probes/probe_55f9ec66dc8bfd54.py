#!/usr/bin/env python3
# Box D3-g32 (round 11, seat D3-s1), D3 step 4 probe for full-gate survivor 55f9ec66dc8bfd54.
# Metric: pull_prices verdict for an entity price source with no entity configured, through the coordinator's composition _price_entity_state + pull_prices.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_55f9ec66dc8bfd54.py   (from the repository root)
# EXPECTED: caller_inputs_moved=0 (absent/''/None all ('fail','Price entity is empty')); direct_moved=1 (a state handed in with no entity configured: reason changes).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g32, 4 vCPU Intel Xeon @ 2.10GHz, venv-ci CPython 3.14.
# Instrumented symbol: custom_components.heatpump_optimizer.price_model:pull_prices, line 855; caller coordinator:_fetch_tibber_prices via _price_entity_state.
# Perturbation: key 55f9ec66dc8bfd54 (GUARD_OFF) `if not config.get(CONF_PRICE_ENTITY):` -> `if False:`; applied in memory (the function re-compiled from its own source with the one line swapped), never on disk.
# Null control: the caller arm is its own control: _price_entity_state returns None whenever the entity is unset.
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


import asyncio
from types import SimpleNamespace as NS
from custom_components.heatpump_optimizer import coordinator as co, price_model as pm
from custom_components.heatpump_optimizer.const import CONF_PRICE_ENTITY, CONF_PRICE_SOURCE, PRICE_SOURCE_ENTITY

mut = mutate(pm, "pull_prices", "        if not config.get(CONF_PRICE_ENTITY):", "        if False:")
good = NS(state="1.2", attributes={"today": [1.0] * 24})


class States:
    def get(self, entity_id):
        return good  # every lookup that is made would find a valid sensor


hass = NS(states=States())
run = lambda fn, cfg, st: asyncio.run(fn(None, cfg, st))
moved_caller = 0
forms = {"absent": {}, "empty": {CONF_PRICE_ENTITY: ""}, "none": {CONF_PRICE_ENTITY: None}}
for name, extra in forms.items():
    cfg = {CONF_PRICE_SOURCE: PRICE_SOURCE_ENTITY, **extra}
    st = co._price_entity_state(hass, cfg)  # the coordinator's one call site composes these two
    b, m = run(pm.pull_prices, cfg, st), run(mut, cfg, st)
    moved_caller += b != m
    print(f"RESULT caller_state_{name}={st!r}")
    print(f"RESULT caller_verdict_baseline_{name}={b!r}")
    print(f"RESULT caller_verdict_mutant_{name}={m!r}")
print(f"RESULT caller_inputs_moved={moved_caller} count")
# outside the coordinator's composition: an entity state handed in with no entity configured
cfg = {CONF_PRICE_SOURCE: PRICE_SOURCE_ENTITY}
b, m = run(pm.pull_prices, cfg, good), run(mut, cfg, good)
print(f"RESULT direct_verdict_baseline={b!r}")
print(f"RESULT direct_verdict_mutant={m!r}")
print(f"RESULT direct_moved={int(b != m)} count")
tail()
