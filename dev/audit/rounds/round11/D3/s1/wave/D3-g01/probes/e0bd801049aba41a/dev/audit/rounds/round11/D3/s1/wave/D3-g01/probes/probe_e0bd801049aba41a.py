#!/usr/bin/env python3
# Metric: space-pump service calls (or the exception) HeatPumpOptimizerCoordinator._async_drive_pumps makes in one tick
#   with a configured space circulation pump and a fresh plan started 2 h ago, across plan step lengths.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_e0bd801049aba41a.py
# EXPECTED RESULT production_step_calls_baseline=[('turn_on', 'switch.space')] ; _mutant identical (moved 0)
# EXPECTED RESULT production_dt_hours=0.25 for every config tried (time_step_minutes is never read from config)
# EXPECTED RESULT dt0_direct_baseline=turn_on ; dt0_direct_mutant=ZeroDivisionError  (only by writing the frozen ctx)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g01 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_drive_pumps
#   line 4524 (`dt_hours = max(ctx._opt_config.dt_hours, 1e-6)`); OptimizationConfig.dt_hours (optimizer.py:2745) =
#   time_step_minutes / 60, time_step_minutes defaults to 15.0 (optimizer.py:2667) and no config key sets it.
# Perturbation: key e0bd801049aba41a, the max(.., 1e-6) clamp dropped (CLAMP_DROP), in memory (method recompiled).
#   Direction: none at any production step length (equivalent-candidate); dt 0, reachable only by an out-of-band write
#   to the frozen context, raises ZeroDivisionError.
# Null control: the production 15-minute step.
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


CLS = co.HeatPumpOptimizerCoordinator
NOON = co.dt_util.now().replace(hour=12, minute=0, second=0, microsecond=0)


def drive(fn, cfg, mode="auto", now=NOON, dt_minutes=None, plan=False, stale=None):
    """One _async_drive_pumps tick on a live coordinator; returns the pump service calls it made."""
    c = coord(**cfg)
    c._mode = mode
    if dt_minutes is not None:
        object.__setattr__(c._ctx, "_opt_config", co.replace(c._ctx._opt_config, time_step_minutes=dt_minutes))
    if plan:  # a fresh plan that started 2 h ago, heating every step
        stamps = [now - co.timedelta(hours=2) + co.timedelta(minutes=15 * i) for i in range(96)]
        c._optimization_result = SimpleNamespace(power_schedule=[2.0] * 96, dhw_power_schedule=[0.0] * 96, timestamps=stamps)
    if stale is not None:
        c._plan_is_stale = lambda: stale
    calls = []

    async def call(domain, service, data, *a, **k):
        calls.append((service, data["entity_id"]))

    c.hass.services.async_call = call
    with mock.patch.object(co.dt_util, "now", lambda: now):
        try:
            asyncio.run(fn(c))
        except Exception as err:
            calls.append(("raised", type(err).__name__))
    return calls


MUT = recompile(CLS, "_async_drive_pumps", "dt_hours = max(ctx._opt_config.dt_hours, 1e-6)",
                "dt_hours = (ctx._opt_config.dt_hours)")
cfg = {"space_circulation_pump_entity": "switch.space"}
b, m = drive(CLS._async_drive_pumps, cfg, plan=True, stale=False), drive(MUT, cfg, plan=True, stale=False)
print(f"RESULT production_step_calls_baseline={b}")
print(f"RESULT production_step_calls_mutant={m}")
for extra in ({}, {"time_step_minutes": 0}, {"time_step_minutes": 5}, {"horizon_hours": 48}):
    print(f"RESULT production_dt_hours config={extra}: {coord(**cfg, **extra)._ctx._opt_config.dt_hours}")
moved = 0
for dtm in (15.0, 5.0, 1.0, 1e-5, 6e-5, 1e-6, 0.0):
    bb = drive(CLS._async_drive_pumps, cfg, plan=True, stale=False, dt_minutes=dtm)
    mm = drive(MUT, cfg, plan=True, stale=False, dt_minutes=dtm)
    moved += bb != mm
    print(f"RESULT inputs step_minutes={dtm}: baseline={bb} mutant={mm}")
print(f"RESULT moved_direct_inputs={moved} count  (dt 0 only)")
print(f"RESULT null_delta={int(b != m)} count")
tail()
