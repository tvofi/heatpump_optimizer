"""R10-COMBI-TANK: the combi-tank group's harness; PR 0 (R10-BUFFER-OPENLOOP) arms.

    PYTHONPATH=tests/hastub:custom_components:tests \\
        python3 dev/audit/harnesses/r10_combi_tank.py [no_probe|wood_seed|solve|all]

Synthetic installs only; no private data. Every arm drives the production
``HeatPumpOptimizerCoordinator._update_current_state`` (which runs the
external-heat detection) and reads the published state and the detector's
observation; run it at the merge base and at the head to read the defect
(D12-s1-01: the no-probe buffer is never advanced) at one end only.

``no_probe``: a 500 L buffer behind a manual (throttling) valve and no buffer
probe; a prior plan whose ``buffer_temp_trajectory`` moves 40 -> 47 degC in
15-minute steps; two cycles at +20 and +50 minutes (covering steps 1 and 3).
Printed per arm: the buffer level after each cycle and the observation's rise
inputs (buffer_temp, dhw_temp). Arms: ``seed`` (no probe), ``probe`` (a probe
reading 36.5 degC: the reading must win, the null control), ``empty`` (an
empty trajectory, which is what a plan without a throttling valve publishes:
the level must stay where it was, never fabricated).

``wood_seed``: the same install plus a wood furnace (wood tank top 70, bottom
60, valve outlet 55 degC, 1000 L, stove override on so the detector is
active). The throttling valve is what makes the plan publish a buffer
trajectory (optimizer.py, ``buffer_temp_trajectory``); without it this arm
collapses into its own ``empty`` control. Printed: ``hp_tank_temp`` per
cycle, and the detector's ``wood_energy_kwh`` and ``displacement``. Arms
``seed``, ``probe`` (38 degC) and ``empty``.

``solve``: four hourly ``async_refresh`` cycles with the real solver, no buffer
probe, a 500 L buffer, valve ``manual`` against valve ``none``. Printed: the
buffer level each solve started from, and whether the previous plan
published a buffer trajectory. Under ``none`` the plan publishes none, so the
level is never fabricated.

RESULT lines are printed for the head; at the merge base ``no_probe_seed``
reads 40.0,40.0 and ``wood_seed_hp`` reads 40.0,40.0.

EXPECTED RESULT no_probe_seed=41.0,43.0
EXPECTED RESULT no_probe_probe=36.5,36.5
EXPECTED RESULT no_probe_empty=40.0,40.0
EXPECTED RESULT no_probe_rise=None,None
EXPECTED RESULT wood_seed_hp=41.0,43.0
EXPECTED RESULT wood_seed_probe_hp=38.0,38.0
EXPECTED RESULT wood_seed_empty_hp=40.0,40.0
"""
from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

T0 = datetime(2026, 3, 2, 6, 0, tzinfo=timezone.utc)
TRAJ = [40.0 + i for i in range(8)]
AT = (T0 + timedelta(minutes=20), T0 + timedelta(minutes=50))
BASE_CFG = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
    "buffer_tank_volume": 500.0,
    "dhw_tank_volume": 200.0,
    "mixing_valve_mode": "manual",
}
WOOD_CFG = {
    "wood_furnace_enabled": True,
    "external_heat_detection_enabled": True,
    "external_heat_entity": "input_boolean.stove",
    "wood_tank_top_entity": "sensor.wood_top",
    "wood_tank_bottom_entity": "sensor.wood_bottom",
    "valve_outlet_temp_entity": "sensor.outlet",
    "wood_tank_volume": 1000.0,
}


def _fmt(values):
    return ",".join("None" if v is None else f"{v:.1f}" for v in values)


def cycles(*, probe=None, trajectory=TRAJ, wood=False):
    """Two ``_update_current_state`` cycles over an injected prior plan."""
    cfg = dict(BASE_CFG)
    if probe is not None:
        cfg["buffer_tank_temp_entity"] = "sensor.buffer"
    if wood:
        cfg.update(WOOD_CFG)
    coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
    coord._snapshots_loaded = True
    coord._optimization_result = SimpleNamespace(
        buffer_temp_trajectory=list(trajectory),
        dhw_temp_trajectory=[],
        timestamps=[T0 + timedelta(minutes=15 * i) for i in range(8)],
    )
    seen = []
    real = coord._external_heat.update
    coord._external_heat.update = lambda obs: (seen.append(obs), real(obs))[1]
    levels = []
    try:
        for now in AT:
            dt_util.freeze(now)
            states = [("sensor.indoor", "21.0"), ("sensor.outdoor", "5.0")]
            if probe is not None:
                states.append(("sensor.buffer", f"{probe}"))
            if wood:
                states += [("sensor.wood_top", "70.0"), ("sensor.wood_bottom", "60.0"),
                           ("sensor.outlet", "55.0")]
                coord.hass.states.set("input_boolean.stove", FakeState("on", last_updated=now))
            for entity, value in states:
                coord.hass.states.set(entity, FakeState(value, last_updated=now, unit="°C"))
            asyncio.run(coord._update_current_state())
            levels.append(getattr(coord, "_ctx", coord)._current_state.buffer_tank_temperature)
    finally:
        dt_util.freeze(None)
    return levels, seen, coord._external_heat.state


def arm_no_probe() -> None:
    for name, kw in (("seed", {}), ("probe", {"probe": 36.5}), ("empty", {"trajectory": ()})):
        levels, seen, _ = cycles(**kw)
        rise = [(o.buffer_temp, o.dhw_temp) for o in seen]
        print(f"no_probe {name:5}: buffer levels {_fmt(levels)}  rise inputs {rise}")
        print(f"RESULT no_probe_{name}={_fmt(levels)}")
        if name == "seed":
            print(f"RESULT no_probe_rise={_fmt(o.buffer_temp for o in seen)}")


def arm_wood_seed() -> None:
    for name, kw in (("seed", {}), ("probe", {"probe": 38.0}), ("empty", {"trajectory": ()})):
        _, seen, st = cycles(wood=True, **kw)
        hp = [o.hp_tank_temp for o in seen]
        energy = "None" if st.wood_energy_kwh is None else f"{st.wood_energy_kwh:.4f}"
        print(f"wood_seed {name:5}: hp_tank_temp {_fmt(hp)}  wood_energy_kwh {energy}"
              f"  displacement {st.displacement:.4f}")
        key = "wood_seed_hp" if name == "seed" else f"wood_seed_{name}_hp"
        print(f"RESULT {key}={_fmt(hp)}")


def _prices(hass, now):
    now = now.replace(minute=0, second=0, microsecond=0)
    hass.states.set("sensor.prices", FakeState("0.5", attributes={"raw_today": [
        {"start": (now + timedelta(hours=h)).isoformat(), "value": round(0.5 + 0.1 * (h % 4), 3)}
        for h in range(48)]}))


def arm_solve() -> None:
    import heatpump_optimizer as integ

    for valve in ("manual", "none"):
        cfg = {k: v for k, v in BASE_CFG.items() if k != "tibber_token"}
        cfg.update({"price_source": "entity", "price_entity": "sensor.prices",
                    "mixing_valve_mode": valve, "dhw_enabled": False})
        dt_util.freeze(T0)
        hass = FakeHass()
        hass.states.set("sensor.indoor", FakeState("21.0", unit="°C"))
        hass.states.set("sensor.outdoor", FakeState("-3.0", unit="°C"))
        _prices(hass, T0)
        entry = FakeEntry(data=cfg, entry_id=f"r10ct_solve_{valve}")
        seeds, published = [], []
        try:
            asyncio.run(integ.async_setup_entry(hass, entry))
            coord = entry.runtime_data
            real = coord._solve_record

            def snap(*a, **k):
                record = real(*a, **k)
                seeds.append(record.inputs.state.buffer_tank_temperature)
                return record

            coord._solve_record = snap
            for hour in range(4):
                published.append(bool(getattr(coord._optimization_result, "buffer_temp_trajectory", None)))
                dt_util.freeze(T0 + timedelta(hours=hour))
                _prices(hass, T0 + timedelta(hours=hour))
                asyncio.run(coord.async_refresh())
        finally:
            dt_util.freeze(None)
        print(f"solve valve={valve:6}: solver buffer seeds {_fmt(seeds)}  "
              f"previous plan published a buffer trajectory {published}")


def main(argv: list[str]) -> int:
    which = argv[1] if len(argv) > 1 else "all"
    arms = {"no_probe": arm_no_probe, "wood_seed": arm_wood_seed, "solve": arm_solve}
    for name, fn in arms.items():
        if which in (name, "all"):
            fn()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
