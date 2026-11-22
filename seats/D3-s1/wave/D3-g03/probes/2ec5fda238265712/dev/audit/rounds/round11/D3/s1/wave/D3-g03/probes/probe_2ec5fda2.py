#!/usr/bin/env python3
# Metric: the day-health verdict HeatPumpOptimizerCoordinator._async_watch_learning_drift folds for day 3
#   (SnapshotRing.observe_health's return on day 3's first heartbeat), after a heartbeat sequence where only one
#   morning heartbeat of day 1 had an unhealthy input ("indoor_temp stale") and every heartbeat after it was healthy;
#   plus the ring's day_unhealthy accumulator after day 2's first heartbeat. Real snapshots.SnapshotRing.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g03/probes/probe_2ec5fda2.py
# EXPECTED RESULT day_unhealthy_after_day2_baseline=None ; day_unhealthy_after_day2_mutant='indoor_temp stale'
# EXPECTED RESULT day3_healthy_baseline=True ; day3_healthy_mutant=False (one bad morning poisons every later day)
# EXPECTED RESULT null_delta=0 count (all heartbeats healthy: the accumulator is None either way)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g03 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_watch_learning_drift,
#   line 9685 `if day_counted:` (the counted day's `start_day(reason_now)`).
# Perturbation: key 2ec5fda238265712 GUARD_OFF -> `if False:`, in memory. Direction: healthy -> unhealthy on day 3.
# Null control: the same calendar with every heartbeat healthy.
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

from datetime import datetime, timezone  # noqa: E402
from custom_components.heatpump_optimizer.snapshots import SnapshotRing  # noqa: E402

FN = CLS._async_watch_learning_drift


def drive(fn, ticks, ring=None, rollback_done=False):
    """Run the heartbeat once per (iso instant, freeze reason or None, bias) tick; returns (ring, me, issue calls)."""
    ring = ring or SnapshotRing()
    calls = []
    state = {"reason": None, "bias": 0.0}

    async def save():
        calls.append("save")

    me = SimpleNamespace(
        _snapshots_loaded=True, _vent_cusum=SimpleNamespace(release_if_starved=lambda now, h: False),
        _inputs_unhealthy=lambda: state["reason"], _snapshot_ring=ring, _learner_snapshot_payloads=lambda: {},
        _accuracy=SimpleNamespace(summary=lambda: {}, temperature_bias=lambda: state["bias"]),
        _async_save_snapshots=save, _rollback_done_for_alarm=rollback_done, hass=SimpleNamespace(),
        _apply_learner_payloads=lambda p: calls.append("apply"),
    )
    with mock.patch.object(co.ir, "async_delete_issue", lambda *a, **k: calls.append("delete")), \
         mock.patch.object(co, "_create_issue", lambda *a, **k: calls.append("create")):
        for iso, reason, bias in ticks:
            state["reason"], state["bias"] = reason, bias
            with mock.patch.object(co.dt_util, "now", lambda iso=iso: datetime.fromisoformat(iso)):
                run(fn(me))
    return ring, me, calls
MUT = mutant(FN, 9685, "        if day_counted:", "        if False:")
BAD = "indoor_temp stale"
seq = [("2026-01-10T08:00:00+00:00", BAD, 0.1), ("2026-01-10T12:00:00+00:00", None, 0.1),
       ("2026-01-11T00:30:00+00:00", None, 0.1)]
day3 = ("2026-01-12T00:30:00+00:00", None, 0.1)
for arm, fn in (("baseline", FN), ("mutant", MUT)):
    ring, _me, _c = drive(fn, seq)
    print(f"RESULT day_unhealthy_after_day2_{arm}={ring.day_unhealthy!r}")
    seen = []
    real = ring.observe_health
    ring.observe_health = lambda r, real=real: (seen.append(real(r)), seen[-1])[1]
    drive(fn, [day3], ring=ring)
    print(f"RESULT day3_healthy_{arm}={seen[0]}")
ok = [(t, None, b) for t, _r, b in seq + [day3]]
print(f"RESULT null_delta={int(drive(FN, ok)[0].day_unhealthy != drive(MUT, ok)[0].day_unhealthy)} count")
tail()
