#!/usr/bin/env python3
# Metric: (DHW lead predictions filed, note_promise calls, kept promises) from _file_dhw_lead_predictions per dhw_temp_trajectory.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g05/probes/probe_894b4e70a336f8fa.py
# Expected: reachable inputs ([], [x], the solved 97-point list) identical; None raises TypeError under the mutant but OptimizationResult's one constructor (optimizer.py:3899) delivers a list; tolerance exact (counts and values, no timing).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g05 cloud (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._file_dhw_lead_predictions (line 10188 `if not trajectory:`).
# Perturbation: `if not trajectory:` -> `if False:` (mutant 894b4e70a336f8fa), applied in memory: the method is recompiled from its own source with the one
#   line replaced, in the coordinator module's namespace, and called on the same coordinator as the baseline arm.
# Null control: the solved 97-point trajectory: 5 leads in both arms.
# Count key: the value the production method returns or files (never an input attribute). Writes nothing.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, logging, sys, textwrap, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
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
sys.path.insert(0, str(ROOT / "tests"))
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402

CLS = co.HeatPumpOptimizerCoordinator
_T0 = time.process_time(), time.thread_time()


def mutant_method(name, old, new):
    """The coordinator method recompiled from its own source with the one-line mutant, in memory."""
    src = textwrap.dedent(inspect.getsource(getattr(CLS, name)))
    assert src.count(old) == 1, f"anchor {old!r} not unique in {name}"
    ns = dict(co.__dict__)
    exec(compile(src.replace(old, new, 1), co.__file__, "exec"), ns)
    return ns[name]


def coord(states=None, **extra):
    cfg = {"tibber_token": "x", "weather_entity": "weather.home",
           "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor", **extra}
    return CLS(FakeHass(dict(states or {})), FakeEntry(data=cfg))


def tail():
    pc, tc = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = sum(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
    except OSError:
        sw = -1
    print(f"RESULT swapins={sw} count")

from dataclasses import replace
from custom_components.heatpump_optimizer.optimizer import OptimizationResult
SOLVE = datetime(2026, 1, 15, 0, 0, tzinfo=timezone.utc)  # accuracy.PROMISE_HOUR (as_local patched to UTC)


def lead_coord():
    c = coord({"sensor.dhw": FakeState("50.0", unit="°C", last_updated=SOLVE)}, dhw_temp_entity="sensor.dhw")
    c._mode = co.MODE_AUTO
    return c


_SOLVED = []


def solved():
    """One real 24 h, 15-min solve (tests/golden.py:make's default scenario), cached."""
    if not _SOLVED:
        import golden
        from profiles import solve_inputs
        s = golden.make()
        _SOLVED.append(s["optimizer"].optimize(inputs=solve_inputs(
            initial_state=s["state"], prices=s["prices"], outdoor_temps=s["outdoor"], wind_speeds=s["wind"],
            precipitation=s["rain"], solar_radiation=s["solar"], start_time=golden.START)))
    return _SOLVED[0]


def counted(fn, traj, dt_h, room=False):
    """Promises filed: (lead predictions noted, note_promise calls, day promises kept)."""
    c = lead_coord()
    leads, promises = [], []
    target = c._accuracy if room else c._dhw_accuracy
    real_promise = c._accuracy.note_promise
    with mock.patch.object(target, "note_lead_prediction", lambda *a: leads.append(a)), \
         mock.patch.object(c._accuracy, "note_promise", lambda *a: (promises.append(a), real_promise(*a))), \
         mock.patch.object(c, "_dhw_probe_temperature", lambda: 50.0), \
         mock.patch.object(co.dt_util, "as_local", lambda t: t):
        if room:
            fn(c, replace(solved(), room_temp_trajectory=list(traj), upper_temp_trajectory=[]), SOLVE)
        else:
            fn(c, replace(solved(), dhw_temp_trajectory=traj), SOLVE, dt_h)
    return len(leads), len(promises), len(c._accuracy.promises)


def solved_lengths():
    """Trajectory lengths a real 24 h, 15-min solve hands these methods."""
    res = solved()
    return len(res.room_temp_trajectory), len(res.dhw_temp_trajectory)


OLD, NEW = "if not trajectory:", "if False:"
MUT = mutant_method("_file_dhw_lead_predictions", OLD, NEW)
moved = 0
for name, traj in (("empty_list", []), ("none", None), ("one_step", [50.0]), ("solve_length_97", [50.0] * 97)):
    def run(fn):
        try:
            return counted(fn, traj, 0.25)
        except Exception as e:  # noqa: BLE001
            return f"raised {type(e).__name__}"
    b, m = run(CLS._file_dhw_lead_predictions), run(MUT)
    if traj is not None:  # None is not a value OptimizationResult carries (optimizer.py:3899: [] or tolist())
        moved += int(b != m)
    print(f"RESULT {name} baseline(leads,promise_calls,promises)={b} mutant={m}")
room_len, dhw_len = solved_lengths()
print(f"RESULT solved_trajectory_lengths room={room_len} dhw={dhw_len} count  (OptimizationResult.dhw_temp_trajectory is a list: [] or tolist())")
print(f"RESULT moved_reachable_inputs={moved} count")
tail()
