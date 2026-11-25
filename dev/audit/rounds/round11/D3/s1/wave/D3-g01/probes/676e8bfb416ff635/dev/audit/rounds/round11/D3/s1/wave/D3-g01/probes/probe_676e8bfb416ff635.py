#!/usr/bin/env python3
# Metric: consecutive cycles _await_optimize carries with an in-process solve while the process worker is unusable
#   (ProcessWorkerUnavailable every cycle) before it raises UpdateFailed and keeps the last plan.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_676e8bfb416ff635.py
# EXPECTED RESULT inprocess_solves_before_skip_baseline=3 count ; _mutant=6 count
# EXPECTED RESULT null_delta=0 count  (a healthy worker: 0 fallbacks in 10 cycles either way)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g01 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:_await_optimize (reads WORKER_FALLBACK_CAP at
#   coordinator.py:2331; the constant is coordinator.py:829), with _await_process stubbed to raise
#   ProcessWorkerUnavailable and optimize_in_process stubbed to count the in-process solves; real FakeHass.data streak.
# Perturbation: key 676e8bfb416ff635, `WORKER_FALLBACK_CAP = 3` -> `= 6`, in memory (mock.patch.object on the module
#   global). Direction: 3 -> 6 GIL-holding in-process solves before the skip.
# Null control: a worker that answers every cycle, where the cap is never consulted.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, logging, sys, textwrap, time
logging.disable(logging.CRITICAL)
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

_T0 = (time.process_time(), time.thread_time())


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
sys.path.insert(0, str(ROOT / "tests"))
from harness import FakeEntry, FakeHass  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402

CFG = {"tibber_token": "x", "weather_entity": "weather.home",
       "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"}


def coord(states=None, **extra):
    return co.HeatPumpOptimizerCoordinator(FakeHass(dict(states or {})), FakeEntry(data={**CFG, **extra}))


def recompile(cls, name, old, new):
    """The method `name` of `cls` with its single line `old` replaced by `new`, compiled in the module namespace."""
    src = textwrap.dedent(inspect.getsource(getattr(cls, name)))
    assert src.count(old) == 1, f"anchor {old!r} moved"
    ns = dict(co.__dict__)
    exec(compile(src.replace(old, new, 1), co.__file__, "exec"), ns)
    return ns[name]


def tail():
    p, t = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={p / t if t > 0 else 1.0:.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = next(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin "))
    except (OSError, StopIteration):
        sw = 0
    print(f"RESULT swapins={sw} count")


def drive(cap, broken, cycles=10):
    hass = FakeHass({})
    solves = []

    async def unusable(*a, **k):
        raise co.ProcessWorkerUnavailable("probe: worker unusable")

    async def healthy(*a, **k):
        return "worker-plan"

    async def run():
        n = 0
        for _ in range(cycles):
            try:
                await co._await_optimize(hass, object(), object())
            except Exception as err:  # UpdateFailed: the skip
                return n, type(err).__name__
            n += 1
        return n, None

    with mock.patch.object(co, "WORKER_FALLBACK_CAP", cap), \
         mock.patch.object(co, "_await_process", unusable if broken else healthy), \
         mock.patch.object(co, "optimize_in_process", lambda *a: solves.append(1) or "inproc-plan"):
        carried, raised = asyncio.run(run())
    return len(solves), carried, raised


b, m = drive(3, True), drive(6, True)
print(f"RESULT inprocess_solves_before_skip_baseline={b[0]} count (then {b[2]})")
print(f"RESULT inprocess_solves_before_skip_mutant={m[0]} count (then {m[2]})")
nb, nm = drive(3, False), drive(6, False)
print(f"RESULT null_inprocess_baseline={nb[0]} mutant={nm[0]} count")
print(f"RESULT null_delta={abs(nb[0] - nm[0]) + abs(nb[1] - nm[1])} count")
tail()
