import sys, asyncio as _asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from harness import FakeHass, FakeState, FakeEntry, Results, UTC
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Coord
R = Results("Section")
_LC_DATA = {"price_source": "entity", "price_entity": "sensor.prices", "weather_entity": "weather.home"}
R.section("supply switch at step boundaries (#2492, R10-SAV-ACTUATION)")
# The cycle wrote the power switch once per interval, so a plan step's change
# reached the pump at the next cycle, and a step's duty verdict depended on
# where the cycle fell against the step grid. A synthetic install runs the
# REAL coordinator's ``_apply_action`` at cycle phase 0 and 14 min, every
# interval timer the arbiter arms fires each minute, the switch's writes are
# applied to its state, and the meter follows the switch. The cycle's own
# power sample is taken at the cycle, as ``_update_current_state`` takes it.
from homeassistant.util import dt as _sa_dt
from heatpump_optimizer import boost as _sa_boost
from heatpump_optimizer import pump_arbiter as _sa_pa
from heatpump_optimizer import store as _sa_store

_SA_T0 = datetime(2026, 1, 10, 6, 0, tzinfo=UTC)
_SA_DUTIES = "s-ss--s-s---ss-s"


def _sa_plan():
    n = len(_SA_DUTIES)
    return SimpleNamespace(
        timestamps=[_SA_T0 + timedelta(minutes=15 * i) for i in range(n)],
        power_schedule=[1.5 if c == "s" else 0.0 for c in _SA_DUTIES],
        dhw_power_schedule=[0.0] * n,
        optimal_setpoints=[21.0] * n,
    )


async def _sa_install(phase, room_cut_at=None):
    """Verdicts and switch writes of one synthetic install at cycle ``phase``."""
    ticks = []
    armed = _sa_pa.async_track_time_interval
    _sa_pa.async_track_time_interval = lambda _h, fn, _i: (ticks.append(fn), (lambda: None))[1]
    hass = FakeHass({
        "switch.hp": FakeState("off", last_updated=_SA_T0),
        "sensor.hp_power": FakeState("0.0", unit="kW", last_updated=_SA_T0),
    })
    coord = Coord(hass, FakeEntry(data={
        **_LC_DATA, "heat_pump_switch_entity": "switch.hp",
        "heat_pump_power_entity": "sensor.hp_power", "pump_duty_mode": "observe",
    }))
    coord._mode = "auto"
    plan = coord._optimization_result = _sa_plan()
    writes = []
    try:
        for m in range(15 * len(_SA_DUTIES) + 1):
            now = _SA_T0 + timedelta(minutes=m)
            _sa_dt.freeze(now)
            if m % 30 == phase:
                coord._last_optimization = now
                coord._measured_power = float(hass.states.get("sensor.hp_power").state)
                i = min(m // 15, len(_SA_DUTIES) - 1)
                _sa_boost.adopt_plan(coord, {"heat_pump_on": _SA_DUTIES[i] == "s", "power": plan.power_schedule[i]})
                await coord._apply_action()
            if m == room_cut_at:
                # An early cut-off, as ``early_cutoff.on_room_event`` writes it.
                await _sa_pa.switch_supply(hass, "switch.hp", False)
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
        verdicts = [r["verdict"] for r in _sa_pa.diagnostics_view(coord)["ledger"]["steps"]]
    finally:
        _sa_dt.freeze(None)
        _sa_pa.async_track_time_interval = armed
    return verdicts, writes


_sa_v0, _sa_w0 = _asyncio.run(_sa_install(0))
_sa_v14, _sa_w14 = _asyncio.run(_sa_install(14))
# Step 0 precedes the phase-14 install's first cycle, so it is the one step
# the two installs may book apart.
R.check(
    "a synthetic install at cycle phase 0 and at 14 min books identical duty verdicts (#2492)",
    len(_sa_v0) == len(_SA_DUTIES) and _sa_v0[1:] == _sa_v14[1:],
    f"phase 0: {_sa_v0}; phase 14: {_sa_v14}",
)
_sa_boundaries = [m for m, _s in _sa_w14 if m % 15 == 0]
R.check(
    "the step tick writes the switch at the boundary of each step whose command changes",
    [m // 15 for m in _sa_boundaries]
    == [i for i in range(1, len(_SA_DUTIES)) if (_SA_DUTIES[i] == "s") != (_SA_DUTIES[i - 1] == "s")],
    f"{_sa_w14}",
)
# A cut the cycle did not write holds across a step the plan keeps on: the
# tick writes a change, never the same command again (early_cutoff.py).
_sa_vc, _sa_wc = _asyncio.run(_sa_install(0, room_cut_at=34))
R.check(
    "an early cut-off holds across a step boundary the plan keeps on",
    [w for w in _sa_wc if 34 < w[0] < 60] == [],
    f"{_sa_wc}",
)
# The pump_duty record's held slots are declared, every one the arbiter can
# write: the silent switch (D15 L5) and the GCHV night registers (#1913).
_sa_record = {"written": {
    **{slot: [v, _SA_T0.isoformat()] for slot, v in (
        ("mode", "Heating"), ("dhw_setpoint", 50.0), ("space_setpoint", 35.0), ("silent", True),
        ("night_start_hour", 22), ("night_start_minute", 0), ("night_end_hour", 6), ("night_end_minute", 30),
    )},
}}
R.check(
    "every slot the pump arbiter persists is declared in the pump_duty store domain",
    sorted(_sa_record["written"]) == sorted(_sa_pa._SLOTS + _sa_pa._NIGHT_SLOTS)
    and _sa_store.off_domain("heatpump_optimizer_e_pump_duty", _sa_record) == []
    and _sa_store.off_domain(
        "heatpump_optimizer_e_pump_duty", {"written": {"silent": ["on", _SA_T0.isoformat()]}}
    ) == ["written/silent/0"],
    f"{_sa_store.off_domain('heatpump_optimizer_e_pump_duty', _sa_record)}",
)


sys.exit(R.close("FEATURE CHECKS"))
sys.exit(R.close("SECTION CHECKS"))
