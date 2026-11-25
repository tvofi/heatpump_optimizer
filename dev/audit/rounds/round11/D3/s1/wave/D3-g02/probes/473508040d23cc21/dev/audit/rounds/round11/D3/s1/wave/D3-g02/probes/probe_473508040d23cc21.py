#!/usr/bin/env python3
# Metric: the space circulation pump service call _async_drive_pumps issues 1.25 h into a plan that heats only in steps 4-7
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g02/probes/probe_473508040d23cc21.py
# Expected: RESULT step5_heat_only_4_7: baseline=turn_on mutant=turn_off (moved=1); step6 likewise; step10 with heat only in step 0: baseline=turn_off mutant=turn_on; nulls moved=0
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g02 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB);
#   counts and service names only, no timing (contention-immune).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_drive_pumps,
#   line 4528 `idx = int(max(0.0, since0 / 3600.0 / dt_hours))`.
# Perturbation: key 473508040d23cc21 (CLAMP_DROP), `idx = int(max(0.0, since0 / 3600.0 / dt_hours))` -> `idx = int((0.0))`, applied in memory: the method is recompiled from its own
#   source with that one line replaced and patched onto the class for the mutant arm only (never on disk).
#   Direction: idx pinned to 0, so mid-plan the pump follows the plan's first step instead of the current one.
# Null control: a tick inside step 0, a plan stamped 0.6 h in the future (the clamp's own case: idx 0 in both arms), an all-off plan, and a cold-room rail.
# Key of the count: the homeassistant.turn_on/turn_off service calls the coordinator itself issues for the configured
#   space circulation pump (FakeHass records every call), after one real _async_drive_pumps (dst_checks.py's
#   _pump_command fixture shape: plan stamped at t0, clock frozen later, warm zones, mild outdoor).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, sys, textwrap, time
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


def repo_root(start):
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))
_cpu0, _th0 = time.process_time(), time.thread_time()
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as co  # noqa: E402

CLS = co.HeatPumpOptimizerCoordinator
FN = "_async_drive_pumps"
OLD = 'idx = int(max(0.0, since0 / 3600.0 / dt_hours))'
NEW = 'idx = int((0.0))'
T0 = datetime(2026, 1, 15, 6, 0, tzinfo=timezone.utc)


def mutant_fn():
    src = textwrap.dedent(inspect.getsource(getattr(CLS, FN)))
    lines = src.splitlines(keepends=True)
    hits = [i for i, ln in enumerate(lines) if ln.strip() == OLD]
    assert len(hits) == 1, f"anchor {OLD!r} found {len(hits)} times"
    ln = lines[hits[0]]
    lines[hits[0]] = ln[: len(ln) - len(ln.lstrip())] + NEW + "\n"
    ns = dict(co.__dict__)
    exec(compile("".join(lines), co.__file__, "exec"), ns)
    return ns[FN]


MUT = mutant_fn()


def run(arm, schedule, elapsed_h, *, timestamps=True, two_zone=False, room=21.4, upper=None, lower=None, outdoor=5.0):
    """One pump tick `elapsed_h` after a plan stamped at T0; returns the space pump's service calls."""
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState(str(room)))
    hass.states.set("sensor.outdoor", FakeState(str(outdoor)))
    cfg = {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor", const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
           const.CONF_DHW_TANK_VOLUME: 180.0, const.CONF_SPACE_PUMP_ENTITY: "switch.space"}
    if two_zone:
        cfg.update({"upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 8.0})
    c = CLS(hass, FakeEntry(data=cfg))
    try:
        dt_util.freeze(T0)
        c._optimization_result = SimpleNamespace(
            timestamps=[dt_util.now()] if timestamps else [], power_schedule=list(schedule), dhw_power_schedule=[])
        dt_util.freeze(T0 + timedelta(hours=elapsed_h))
        st = c._current_state
        c._current_state = replace(
            st, room_temperature=room, outdoor_temperature=outdoor,
            upper_floor_temperature=room if upper is None else upper,
            lower_floor_temperature=room if lower is None else lower)
        if arm == "mutant":
            with mock.patch.object(CLS, FN, MUT):
                asyncio.run(c._async_drive_pumps())
        else:
            asyncio.run(c._async_drive_pumps())
    finally:
        dt_util.freeze(None)
    return tuple((svc, data.get("entity_id")) for dom, svc, data in c.hass.services.calls if dom == "homeassistant")


ON_4_7 = [1.0 if 4 <= i < 8 else 0.0 for i in range(96)]   # heat only in steps 4-7 of the quarter grid
OFF_ALL = [0.0] * 96
ON_0 = [1.0 if i == 0 else 0.0 for i in range(96)]           # heat only in step 0

INPUTS = [("step5_heat_only_4_7", (ON_4_7, 1.25), {}), ("step6_heat_only_4_7", (ON_4_7, 1.5), {}), ("step10_heat_only_step0", (ON_0, 2.5), {}), ("step0_null", (ON_4_7, 0.1), {}), ("plan_in_future_clamp", (ON_0, -0.6), {}), ("all_off_null", (OFF_ALL, 1.25), {}), ("cold_rail_null", (ON_0, 2.5), dict(room=15.0))]

moved = 0
for label, args, kw in INPUTS:
    b = run("baseline", *args, **kw)
    m = run("mutant", *args, **kw)
    d = int(b != m)
    moved += d
    print(f"RESULT {label}_baseline={'|'.join(s for s, _ in b) or 'none'}")
    print(f"RESULT {label}_mutant={'|'.join(s for s, _ in m) or 'none'}")
    print(f"RESULT {label}_moved={d} count")
print(f"RESULT inputs_moved={moved} count of {len(INPUTS)}")
_cpu, _th = time.process_time() - _cpu0, time.thread_time() - _th0
print(f"RESULT thread_factor={_cpu / max(_th, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _sw = sum(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
except OSError:
    _sw = -1
print(f"RESULT swapins={_sw}")
