#!/usr/bin/env python3
"""R10-SAV-ACTUATION (#2492 carry 5, seam 2): do duty verdicts depend on the cycle's phase?

WHY IT EXISTS. The carry's owed control: a synthetic install with the cycle
phase at 0 and at 14 min must book identical duty verdicts. This drives the
REAL coordinator's ``_apply_action`` once per 30-minute cycle at each phase,
fires every one-minute interval timer ``pump_arbiter`` arms, applies each
switch write to the switch's state and lets the meter follow the switch; the
cycle's own power sample is taken at the cycle, as ``_update_current_state``
takes it. It uses no symbol the fix added, so it runs at the merge base (the
null) and at the head alike. ``tests/features.py`` (section "supply switch at
step boundaries") pins the same install as checks.

Prints, per phase, the ledger's verdict per step and the minutes at which the
switch was written, then ``AGREE: yes`` or ``AGREE: no`` over steps 1.. (step 0
precedes the phase-14 install's first cycle).

    PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_actuation_phase.py
"""
import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from harness import FakeEntry, FakeHass, FakeState
from homeassistant.util import dt as dt_util
from heatpump_optimizer import boost
from heatpump_optimizer import pump_arbiter as pa
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

T0 = datetime(2026, 1, 10, 6, 0, tzinfo=timezone.utc)
#: The plan: 's' a space-heating step, '-' an idle one.
DUTIES = "s-ss--s-s---ss-s"
CYCLE_MIN = 30


def plan():
    n = len(DUTIES)
    return SimpleNamespace(
        timestamps=[T0 + timedelta(minutes=15 * i) for i in range(n)],
        power_schedule=[1.5 if c == "s" else 0.0 for c in DUTIES],
        dhw_power_schedule=[0.0] * n,
        optimal_setpoints=[21.0] * n,
    )


async def install(phase):
    ticks = []
    armed = pa.async_track_time_interval
    pa.async_track_time_interval = lambda _h, fn, _i: (ticks.append(fn), (lambda: None))[1]
    hass = FakeHass({
        "switch.hp": FakeState("off", last_updated=T0),
        "sensor.hp_power": FakeState("0.0", unit="kW", last_updated=T0),
    })
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data={
        "price_source": "entity", "price_entity": "sensor.prices", "weather_entity": "weather.home",
        "heat_pump_switch_entity": "switch.hp", "heat_pump_power_entity": "sensor.hp_power",
        "pump_duty_mode": "observe",
    }))
    coord._mode = "auto"
    p = coord._optimization_result = plan()
    writes = []
    try:
        for m in range(15 * len(DUTIES) + 1):
            now = T0 + timedelta(minutes=m)
            dt_util.freeze(now)
            if m % CYCLE_MIN == phase:
                coord._last_optimization = now
                coord._measured_power = float(hass.states.get("sensor.hp_power").state)
                i = min(m // 15, len(DUTIES) - 1)
                boost.adopt_plan(coord, {"heat_pump_on": DUTIES[i] == "s", "power": p.power_schedule[i]})
                await coord._apply_action()
            for tick in list(ticks):
                await tick(now)
            for domain, service, _data in hass.services.calls:
                if domain == "switch":
                    writes.append((m, service))
                    hass.states.set("switch.hp", FakeState(
                        "on" if service == "turn_on" else "off", last_updated=now))
            hass.services.calls.clear()
            on = hass.states.get("switch.hp").state == "on"
            hass.states.set("sensor.hp_power", FakeState("1.5" if on else "0.0", unit="kW", last_updated=now))
        return [r["verdict"] for r in pa.diagnostics_view(coord)["ledger"]["steps"]], writes
    finally:
        dt_util.freeze(None)
        pa.async_track_time_interval = armed


def main():
    runs = {phase: asyncio.run(install(phase)) for phase in (0, 14)}
    for phase, (verdicts, writes) in runs.items():
        print(f"phase {phase:2d} verdicts: {verdicts}")
        print(f"phase {phase:2d} writes:   {writes}")
    print("AGREE:", "yes" if runs[0][0][1:] == runs[14][0][1:] else "no")


if __name__ == "__main__":
    main()
