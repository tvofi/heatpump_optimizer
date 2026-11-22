#!/usr/bin/env python3
# Box D3-g32 (round 11, seat D3-s1), D3 step 4 probe for full-gate survivor 1f4a10ae90bbf2d9.
# Metric: _unadoptable outcome for 0/1/2/4 settling rows, and the settling-row count step() hands it.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_1f4a10ae90bbf2d9.py   (from the repository root)
# EXPECTED: rows1 baseline=refusal string, mutant=raised IndexError; rows0/2/4 moved=0; step_driven min_settling_rows=2 (15/30/60/90-min cadence).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g32, 4 vCPU Intel Xeon @ 2.10GHz, venv-ci CPython 3.14.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification._unadoptable, line 1705.
# Perturbation: key 1f4a10ae90bbf2d9 (CMP_BOUND) `len(rows) > 1` -> `>= 1`. Direction: one settling row raises IndexError (rows[-2]); applied in memory (the function re-compiled from its own source with the one line swapped), never on disk.
# Null control: 0, 2 and 4 rows, where both arms agree.
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


from datetime import datetime, timedelta, timezone
from custom_components.heatpump_optimizer import sysid

OLD = "        dt = utc_elapsed_seconds(rows[-1].when, rows[-2].when) / 3600.0 if len(rows) > 1 else 0.25"
NEW = "        dt = utc_elapsed_seconds(rows[-1].when, rows[-2].when) / 3600.0 if len(rows) >= 1 else 0.25"
mut = mutate(sysid.SystemIdentification, "_unadoptable", OLD, NEW)
t0 = datetime(2026, 1, 14, 2, 0, tzinfo=timezone.utc)


def outcome(fn, n_rows):
    s = sysid.SystemIdentification(sysid.SysIdConfig(enabled=True))
    s.samples = [sysid.SysIdSample(t0 + timedelta(minutes=15 * i), 20.0, -2.0, 0.0, sysid.PHASE_SETTLING)
                 for i in range(n_rows)]
    s._slab_pair, s._slab_prior, s._baseline_temp = (8.0, 0.5), (0.2, 6.0), 20.0
    try:
        return repr(fn(s, 1.0, -2.0))
    except Exception as err:  # noqa: BLE001
        return f"raised {type(err).__name__}"


for n in (0, 1, 2, 4):
    b, m = outcome(sysid.SystemIdentification._unadoptable, n), outcome(mut, n)
    print(f"RESULT rows{n}_baseline={b}")
    print(f"RESULT rows{n}_mutant={m}")
    print(f"RESULT rows{n}_moved={int(b != m)} count")
# reach: drive the state machine through step() from SETTLING, at 15-min and 60-min cadence, and count the
# settling rows _unadoptable sees when _begin_step_phase calls it
seen = []
real = sysid.SystemIdentification._unadoptable


def spy(self, step_kw, outdoor):
    seen.append(sum(1 for r in self.samples if r.phase == sysid.PHASE_SETTLING))
    return real(self, step_kw, outdoor)


import numpy as np
for minutes in (15, 30, 60, 90):
    s = sysid.SystemIdentification(sysid.SysIdConfig(enabled=True))
    s.phase, s.phase_started, s._baseline_temp = sysid.PHASE_SETTLING, t0, 20.0
    s._slab_pair, s._slab_prior = (8.0, 0.5), (0.2, 6.0)
    with mock.patch.object(sysid.SystemIdentification, "_unadoptable", spy):
        for i in range(8):
            s.step(t0 + timedelta(minutes=minutes * i), 20.0, -2.0, 0.5, np.array([0.5, 1.0, 2.0]), 100, 6.0, 3.0,
                   0.5, sysid.HousePlant(ua=0.2, capacity=6.0, gains=0.3, slab_mass=8.0, slab_transfer=0.5))
            if s.phase != sysid.PHASE_SETTLING:
                break
print(f"RESULT step_driven_unadoptable_calls={len(seen)} count  min_settling_rows={min(seen) if seen else None}")
tail()
