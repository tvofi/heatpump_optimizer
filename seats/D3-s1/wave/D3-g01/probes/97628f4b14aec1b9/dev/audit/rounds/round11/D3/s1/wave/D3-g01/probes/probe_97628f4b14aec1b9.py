#!/usr/bin/env python3
# Metric: pump service calls (and any exception) HeatPumpOptimizerCoordinator._async_drive_pumps makes in one tick when
#   neither a VVC pump nor a drivable space pump exists, on a live coordinator.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_97628f4b14aec1b9.py
# EXPECTED RESULT no_pumps_calls_baseline=[] ; no_pumps_calls_mutant=[]  (equivalent: both branches below are gated
#   on the same two entities, so dropping the early return only adds a dt_util.now() read)
# EXPECTED RESULT moved_inputs=0 count
# EXPECTED RESULT positive_control_calls=1 count  (a configured VVC pump: the harness does see a command)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g01 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_drive_pumps
#   line 4497 (`if not vvc_entity and not space_entity:`), hass.services.async_call recorded, dt_util.now pinned.
# Perturbation: key 97628f4b14aec1b9, `if not vvc_entity and not space_entity:` -> `if False:` (GUARD_OFF), in memory.
#   Direction: none found (equivalent-candidate): every input below gives identical calls.
# Null control: the inputs are themselves the null; positive control: a configured VVC pump issues one command.
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


MUT = recompile(CLS, "_async_drive_pumps", "if not vvc_entity and not space_entity:", "if False:")
inputs = {
    "no_pumps": ({}, {}),
    "no_pumps_mode_off": ({}, {"mode": "off"}),
    "no_pumps_with_plan": ({}, {"plan": True, "stale": False}),
    "space_pump_held_stale": ({"space_circulation_pump_entity": "switch.space"}, {"plan": True, "stale": True}),
    "no_pumps_dhw_windows": ({"dhw_enabled": True, "dhw_schedule_enabled": True, "dhw_windows": "06:00-08:30"}, {}),
    "no_pumps_midnight": ({}, {"now": NOON.replace(hour=0)}),
}
moved = 0
for name, (cfg, kw) in inputs.items():
    b, m = drive(CLS._async_drive_pumps, cfg, **kw), drive(MUT, cfg, **kw)
    moved += b != m
    print(f"RESULT {name}_calls_baseline={b} mutant={m}")
print(f"RESULT moved_inputs={moved} count")
print(f"RESULT positive_control_calls={len(drive(MUT, {'vvc_pump_entity': 'switch.vvc'}))} count")
tail()
