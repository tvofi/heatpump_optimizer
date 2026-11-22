#!/usr/bin/env python3
# Box D3-g32 (round 11, seat D3-s1), D3 step 4 probe for full-gate survivor 80cb9a8152f72e57.
# Metric: internal_gains_kw _slab_outcome publishes for a fitted gains value in [-0.5, 2.0].
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_80cb9a8152f72e57.py   (from the repository root)
# EXPECTED: inputs_moved=4/8 (fitted gains in [-0.5, 0): baseline 0.0, mutant the negative value).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g32, 4 vCPU Intel Xeon @ 2.10GHz, venv-ci CPython 3.14.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification._slab_outcome, line 2411 (helpers stubbed as for 4a189db92053760e).
# Perturbation: key 80cb9a8152f72e57 (CLAMP_DROP) `np.clip(gains_kw, 0.0, 2.0)` dropped. Direction: 0.0 -> negative gains; applied in memory (the function re-compiled from its own source with the one line swapped), never on disk.
# Null control: fitted gains in [0, 2].
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

import numpy as np
from custom_components.heatpump_optimizer import sysid

SID = sysid.SystemIdentification
# The interval and confidence helpers are stubbed to constants in BOTH arms: the metric reads only the fields the
# mutated lines decide (completed, reason, internal_gains_kw, heat_loss_kw_per_c), never the stubbed ones.
STUBS = {"_slab_ua_profile_halfwidth": lambda *a, **k: 0.01, "_slab_ua_prior_halfwidth": lambda *a, **k: 0.01,
         "_slab_ua_told_halfwidth": lambda *a, **k: 0.01, "_slab_confidence": lambda *a, **k: 0.9}
ROOMS = np.full(20, 20.0)


def outcome(fn, ua, room_cap, gains, slab_mass=8.0, slab_transfer=0.5):
    s = SID(sysid.SysIdConfig(enabled=True))
    x = np.array([np.log(ua), np.log(room_cap), gains])
    with mock.patch.dict(fn.__globals__, STUBS):
        r = fn(s, x, ROOMS, lambda v: np.zeros(ROOMS.size), slab_mass, slab_transfer, lambda a, b: None)
    return (r.completed, r.reason, None if r.internal_gains_kw is None else round(r.internal_gains_kw, 6))


GRID = [(ua, c, g) for ua in (0.005, 0.2, 6.0) for c in (-1.0, 4.0) for g in (-0.8, -0.5, -0.3, 0.0, 0.4, 2.0, 2.5)]

mut = mutate(SID, "_slab_outcome", "        gains_kw = float(np.clip(gains_kw, 0.0, 2.0))", "        gains_kw = float((gains_kw))")
moved = 0
for g in (-0.5, -0.3, -0.1, -1e-6, 0.0, 0.4, 1.99, 2.0):
    b, m = outcome(SID._slab_outcome, 0.2, 4.0, g), outcome(mut, 0.2, 4.0, g)
    moved += b != m
    print(f"RESULT gains_fit{g}: baseline={b} mutant={m}")
print(f"RESULT inputs_moved={moved}/8 count  (fitted gains in [-0.5, 0): published internal_gains_kw)")
tail()
