#!/usr/bin/env python3
# Metric: the space circulation pump service call in a two-zone house whose room average is warm but one floor sits below the comfort floor + margin, with the plan off now and next
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g02/probes/probe_ad8a02e5c07428ab.py
# Expected: RESULT upper_cold_room_warm: baseline=turn_on mutant=turn_off (moved=1); lower_cold_room_warm likewise; nulls moved=0
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g02 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB);
#   counts and service names only, no timing (contention-immune).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_drive_pumps,
#   line 4538 `if params.two_zone_enabled:`.
# Perturbation: key ad8a02e5c07428ab (GUARD_OFF), `if params.two_zone_enabled:` -> `if False:`, applied in memory: the method is recompiled from its own
#   source with that one line replaced and patched onto the class for the mutant arm only (never on disk).
#   Direction: with the two-zone branch off only the room average is checked, so a floor at 15 C under a 21.4 C average no longer forces the pump on (ON -> OFF).
# Null control: both floors warm (OFF in both), a single-zone house with a cold upper reading (OFF in both: the branch is two-zone only), and a cold room (ON in both).
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
OLD = 'if params.two_zone_enabled:'
NEW = 'if False:'
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

INPUTS = [("upper_cold_room_warm", (OFF_ALL, 1.25), dict(two_zone=True, room=21.4, upper=15.0)), ("lower_cold_room_warm", (OFF_ALL, 1.25), dict(two_zone=True, room=21.4, lower=15.0)), ("zones_warm_null", (OFF_ALL, 1.25), dict(two_zone=True)), ("single_zone_upper_cold_null", (OFF_ALL, 1.25), dict(two_zone=False, upper=15.0)), ("room_cold_null", (OFF_ALL, 1.25), dict(two_zone=True, room=15.0))]

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
