#!/usr/bin/env python3
# Box D3-g32 (round 11, seat D3-s1), D3 step 4 probe for full-gate survivor de399cdbe79053ea.
# Metric: _over_excursion verdict at |room - baseline| == max_excursion_c (0.8 C, not configurable).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_de399cdbe79053ea.py   (from the repository root)
# EXPECTED: readings_moved=0 of 202 (0.1 C readings 15-25 C); random_indoor_moved=0 of 600000; tie_base0.2_room1.0 baseline=False mutant=True; null_delta=0.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g32, 4 vCPU Intel Xeon @ 2.10GHz, venv-ci CPython 3.14.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification._over_excursion, line 1640.
# Perturbation: key de399cdbe79053ea (CMP_BOUND) `> self.config.max_excursion_c` -> `>=`. Direction: False -> True at an exact float tie only; applied in memory (the function re-compiled from its own source with the one line swapped), never on disk.
# Null control: excursions clearly inside/outside the bound.
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

mut = mutate(sysid.SystemIdentification, "_over_excursion",
             "            and abs(room_temp - base) > self.config.max_excursion_c",
             "            and abs(room_temp - base) >= self.config.max_excursion_c")
s = sysid.SystemIdentification(sysid.SysIdConfig(enabled=True))
lim = s.config.max_excursion_c
ties = moved = 0
# sensor-resolution readings: baselines 15.0..25.0 in 0.1 steps, rooms at baseline +- the bound, rounded to 0.1
for i in range(150, 251):
    base = i / 10.0
    s._baseline_temp = base
    for room in (round(base + lim, 1), round(base - lim, 1)):
        if abs(room - base) == lim:
            ties += 1
        moved += sysid.SystemIdentification._over_excursion(s, room) != mut(s, room)
print(f"RESULT readings_scanned=202 count")
print(f"RESULT exact_float_ties={ties} count")
print(f"RESULT readings_moved={moved} count  (baseline False -> mutant True: the experiment aborts)")
s._baseline_temp = 0.2
print(f"RESULT tie_base0.2_room1.0_baseline={sysid.SystemIdentification._over_excursion(s, 1.0)} mutant={mut(s, 1.0)}")
# null control: an excursion clearly inside / outside the bound
s._baseline_temp = 20.0
print(f"RESULT null_delta={sum(sysid.SystemIdentification._over_excursion(s, r) != mut(s, r) for r in (20.3, 19.5, 21.5, 18.0))} count")
# exact ties need |room|,|base| < 1 C (0.8 is not a multiple of ulp(x) for x >= 1): a random scan of indoor floats
import random
rng = random.Random(11)
ties = 0
for _ in range(200000):
    base = rng.uniform(5.0, 30.0)
    s._baseline_temp = base
    room = base + rng.choice((-lim, lim))
    for r in (room, float(np.nextafter(room, 0)), float(np.nextafter(room, 99))):
        ties += sysid.SystemIdentification._over_excursion(s, r) != mut(s, r)
print(f"RESULT random_indoor_moved={ties} count  (600000 readings, base uniform in [5, 30] C, room base+-0.8 and both float neighbours)")
tail()
