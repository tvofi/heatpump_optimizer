#!/usr/bin/env python3
# Metric: repair-registry writes (ir.async_delete_issue + _create_issue calls) HeatPumpOptimizerCoordinator.
#   _check_pump_mode_expired makes over N=3 ticks whose expiry state does not change (mode entity readable).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g03/probes/probe_e880fd35.py
# EXPECTED RESULT steady_writes_baseline=0 count ; steady_writes_mutant=3 count (one delete per tick)
# EXPECTED RESULT null_delta=0 count  (a tick that flips the state: both arms write once)
# Key of the count: the registry calls the production method makes (spied at co.ir.async_delete_issue/co._create_issue).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g03 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._check_pump_mode_expired,
#   line 5986 `if expired == self._pump_mode_expired_notice:`.
# Perturbation: key e880fd3537006726 GUARD_OFF -> `if False:`, in memory (method recompiled from its source).
#   Direction: steady-state writes 0 -> 1 per tick.
# Null control: a tick where the state flips (readable -> expired): both arms create the issue once.
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

MUT = mutant(CLS._check_pump_mode_expired, 5986,
             "        if expired == self._pump_mode_expired_notice:", "        if False:")


def drive(fn, sources, notice=False):
    me = SimpleNamespace(_pump_signals=SimpleNamespace(mode_source=None), _pump_mode_expired_notice=notice,
                         hass=object(), _pump_mode_last_good=None)
    calls = []
    with mock.patch.object(co.ir, "async_delete_issue", lambda *a, **k: calls.append("delete")), \
         mock.patch.object(co, "_create_issue", lambda *a, **k: calls.append("create")):
        for s in sources:
            me._pump_signals.mode_source = s
            fn(me)
    return len(calls)


steady = ["sensor"] * 3
print(f"RESULT steady_writes_baseline={drive(CLS._check_pump_mode_expired, steady)} count")
print(f"RESULT steady_writes_mutant={drive(MUT, steady)} count")
flip = [co.pump_signals.MODE_SOURCE_EXPIRED]
print(f"RESULT null_delta={drive(MUT, flip) - drive(CLS._check_pump_mode_expired, flip)} count")
tail()
