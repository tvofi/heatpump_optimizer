#!/usr/bin/env python3
# Metric: the hot-water circulation (VVC) pump command HeatPumpOptimizerCoordinator._async_drive_pumps issues at 12:00 on a
#   live coordinator configured with a VVC pump, a 06:00-08:30 DHW window and DHW disabled (dhw_enabled False).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_20f57d1eea0a5a1d.py
# EXPECTED RESULT dhw_disabled_vvc_baseline=[('turn_on', 'switch.vvc')] ; dhw_disabled_vvc_mutant=[('turn_off', 'switch.vvc')]
# EXPECTED RESULT null_delta=0 count  (DHW enabled with the schedule on, and DHW disabled with the schedule off: operands agree)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g01 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_drive_pumps
#   line 4508 (`if params.dhw_enabled and params.dhw_windows_active`), live coordinator from config, dt_util.now pinned to
#   12:00, hass.services.async_call recorded.
# Perturbation: key 20f57d1eea0a5a1d, `and` -> `or` (BOOLOP), in memory (method recompiled from source).
#   Direction: with DHW disabled the loop is left on (no frame to exploit) -> it is switched off outside the windows.
# Null control: dhw_enabled with the schedule on (both operands true) and DHW disabled with the schedule off (both false).
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


MUT = recompile(CLS, "_async_drive_pumps", "if params.dhw_enabled and params.dhw_windows_active",
                "if params.dhw_enabled or params.dhw_windows_active")
VVC = {"vvc_pump_entity": "switch.vvc", "dhw_windows": "06:00-08:30"}
cases = {
    "dhw_disabled_vvc": {**VVC, "dhw_enabled": False, "dhw_schedule_enabled": True},
    "dhw_enabled_schedule_off_vvc": {**VVC, "dhw_enabled": True, "dhw_schedule_enabled": False},
}
for name, cfg in cases.items():
    print(f"RESULT {name}_baseline={drive(CLS._async_drive_pumps, cfg)}")
    print(f"RESULT {name}_mutant={drive(MUT, cfg)}")
cfg = cases["dhw_disabled_vvc"]
print(f"RESULT inputs dhw_disabled at 07:00: baseline={drive(CLS._async_drive_pumps, cfg, now=NOON.replace(hour=7))} "
      f"mutant={drive(MUT, cfg, now=NOON.replace(hour=7))}")
nulls = ({**VVC, "dhw_enabled": True, "dhw_schedule_enabled": True},
         {**VVC, "dhw_enabled": False, "dhw_schedule_enabled": False})
print(f"RESULT null_delta={sum(int(drive(CLS._async_drive_pumps, c) != drive(MUT, c)) for c in nulls)} count")
tail()
