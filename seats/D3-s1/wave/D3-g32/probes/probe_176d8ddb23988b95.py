#!/usr/bin/env python3
# Box D3-g32 (round 11, seat D3-s1), D3 step 4 probe for full-gate survivor 176d8ddb23988b95.
# Metric: SystemIdentification state after _finish on a completed slab fit (phase, last_run, result, routing flag), plus INFO log records.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_176d8ddb23988b95.py   (from the repository root)
# EXPECTED: completed_state_moved=0; completed_info_logs_baseline=1 mutant=0; null_refused_state_moved=0.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g32, 4 vCPU Intel Xeon @ 2.10GHz, venv-ci CPython 3.14.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification._finish, line 1853 (identify_slab stubbed to a fixed result in both arms).
# Perturbation: key 176d8ddb23988b95 (GUARD_OFF) `if self.result.completed:` -> `if False:`. Direction: only the INFO 'System identification complete' record disappears; applied in memory (the function re-compiled from its own source with the one line swapped), never on disk.
# Null control: a refused fit, where the branch is not taken either way.
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


import logging
from datetime import datetime, timezone
from custom_components.heatpump_optimizer import sysid

mut = mutate(sysid.SystemIdentification, "_finish", "        if self.result.completed:", "        if False:")
now = datetime(2026, 1, 14, 3, 0, tzinfo=timezone.utc)
done = sysid.SysIdResult(completed=True, time_constant_hours=40.0, heat_loss_kw_per_c=0.2,
                         thermal_mass_kwh_per_c=8.0, internal_gains_kw=0.3, confidence=0.8, reason="ok")
refused = sysid.SysIdResult(completed=False, reason="fit failed")


class Count(logging.Handler):
    def __init__(self):
        super().__init__(logging.DEBUG)
        self.n = 0

    def emit(self, record):
        self.n += record.levelno >= logging.INFO


def finish(fn, outcome):
    s = sysid.SystemIdentification(sysid.SysIdConfig(enabled=True))
    s._slab_pair = (8.0, 0.5)
    h = Count()
    sysid._LOGGER.addHandler(h)
    old = sysid._LOGGER.level
    sysid._LOGGER.setLevel(logging.DEBUG)
    try:
        with mock.patch.object(sysid.SystemIdentification, "identify_slab", lambda self: outcome):
            fn(s, now)
    finally:
        sysid._LOGGER.removeHandler(h)
        sysid._LOGGER.setLevel(old)
    return (s.phase, s.last_run, s.result.as_dict(), s._slab_fit_used), h.n


b, bl = finish(sysid.SystemIdentification._finish, done)
m, ml = finish(mut, done)
print(f"RESULT completed_state_moved={int(b != m)} count  (phase, last_run, result, routing flag)")
print(f"RESULT completed_info_logs_baseline={bl} mutant={ml}")
b, bl = finish(sysid.SystemIdentification._finish, refused)
m, ml = finish(mut, refused)
print(f"RESULT null_refused_state_moved={int(b != m)} count  info_logs_baseline={bl} mutant={ml}")
tail()
