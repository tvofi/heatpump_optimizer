#!/usr/bin/env python3
"""R10-COP-GATE-E (#3106): the unsensed slab across a mode switch, through ``_propagated_slab``.

Two coordinator cycles 30 min apart through ``_update_current_state`` on an
install with a power meter, a live mode entity and no floor sensor; the plan
asks 4 kW of space heat and none of hot water. The first cycle reads the mode
of the interval's start, the second reads ``DRAWN_KW`` and the mode at the
close, its ``last_changed`` at the switch. ``_replay_interval`` is wrapped to
record the kW the slab is advanced by.

Arms:

  * ``all_space`` (the null control): heating at both reads. The dwell is all
    space, so the booked kW is the draw at both ends of any fix.
  * ``switch_back``: hot water for the first half, heating at the close.
  * ``switch_out``: heating for the first half, hot water at the close.
  * ``truth``: ``all_space`` drawing ``DRAWN_KW`` x the switch arms' space
    share, the same space energy spread over the interval (a pump drawing a
    constant kW while on space heat). Its slab is the reference the two
    candidate rules are scored against.

Per arm one ``RESULT`` line: ``booked_kw`` (``None`` when nothing was
replayed and the plan's trajectory stands), ``space_share`` (the dwell's
space hours over the interval's), ``over_kw`` = booked minus ``DRAWN_KW`` x
the share, and ``slab``. ``plan`` is the plan's trajectory at the close,
the fall-back rule's value.

    PYTHONPATH=tests/hastub:custom_components:tests \\
        python3 dev/audit/harnesses/r10_cop_gate_slab.py [--drawn KW]

Perturbation: ``--drawn`` scales the draw; ``over_kw`` on ``switch_back``
scales with it at the base (direction: up with the draw) and stays 0 at
the head, and ``all_space`` reads ``over_kw=0`` at both ends.
"""
from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timedelta, timezone

DRAWN_KW = 4.0
T0 = datetime(2026, 10, 5, 3, 0, tzinfo=timezone.utc)
STEP = timedelta(minutes=30)
HEAT, DHW = "Heating", "DHW (Hot Water)"


def arm(start_mode: str, close_mode: str, drawn_kw: float) -> tuple[float | None, float | None, float]:
    import homeassistant.util.dt as dt_mod
    from harness import FakeEntry, FakeHass, FakeState

    import heatpump_optimizer.coordinator as C
    from heatpump_optimizer import heat_energy
    from heatpump_optimizer.thermal_model import ThermalState

    cfg = {
        "tibber_token": "x", "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
        "optimization_interval": 30.0, "heat_pump_power_entity": "sensor.hp_power",
        "heat_pump_mode_entity": "select.pump_mode",
    }
    coord = C.HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
    coord._snapshots_loaded = True
    ctx = getattr(coord, "_ctx", coord)
    ctx._thermal_params.dhw_enabled = False
    booked: list[float] = []
    replay = C._replay_interval

    async def recording(c, prior, kw, *rest):
        booked.append(kw)
        return await replay(c, prior, kw, *rest)

    C._replay_interval = recording
    t1 = T0 + STEP
    switch = T0 + STEP / 2
    try:
        for at, mode, changed, kw in ((T0, start_mode, T0 - STEP, 0.0), (t1, close_mode, switch, drawn_kw)):
            ctx.publish(coord, ThermalState(room_temperature=21.0, outdoor_temperature=5.0, slab_temperature=23.0))
            coord._last_house_sample_time = at - STEP
            coord._optimization_result = type("R", (), {
                "slab_temp_trajectory": [25.0, 25.5, 26.0],
                "timestamps": [at + STEP * i for i in range(3)],
            })()
            coord._current_action = {"power": 4.0, "dhw_power": 0.0, "mode": "auto", "heat_pump_on": True}
            dt_mod.freeze(at)
            for entity, value, unit in (("sensor.indoor", "21.0", "°C"), ("sensor.outdoor", "5.0", "°C"),
                                        ("sensor.hp_power", f"{kw}", "kW")):
                coord.hass.states.set(entity, FakeState(value, last_updated=at, unit=unit))
            state = FakeState(mode, last_updated=at, attributes={"options": [HEAT, DHW]})
            state.last_changed = changed if start_mode != close_mode or at == T0 else T0 - STEP
            coord.hass.states.set("select.pump_mode", state)
            booked.clear()
            asyncio.run(coord._update_current_state())
    finally:
        dt_mod.freeze(None)
        C._replay_interval = replay
    a = heat_energy.meter_of(coord).attribution((4.0, 0.0))
    share = a.space / (a.space + a.dhw) if a.observed and a.space + a.dhw > 0 else None
    slab = float(getattr(coord, "_ctx", coord)._current_state.slab_temperature)
    return (booked[-1] if booked else None), share, slab


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--drawn", type=float, default=DRAWN_KW)
    drawn = ap.parse_args().drawn
    shares = {}
    for name, (start, close) in (("all_space", (HEAT, HEAT)), ("switch_back", (DHW, HEAT)),
                                 ("switch_out", (HEAT, DHW))):
        kw, share, slab = arm(start, close, drawn)
        shares[name] = share
        over = None if kw is None or share is None else round(kw - drawn * share, 6)
        print(f"RESULT {name} booked_kw={kw} space_share={share} over_kw={over} slab={slab:.4f}")
    kw, _share, slab = arm(HEAT, HEAT, drawn * shares["switch_back"])
    print(f"RESULT truth booked_kw={kw} slab={slab:.4f} plan=25.0000")


if __name__ == "__main__":
    main()
