"""The finder's closed loop with the early cut-off driven inside each interval.

Companion to the live-install overshoot harness (``closed_loop_overshoot.py``,
#201 comment 6067349704). That harness steps the plant in 15-minute blocks,
so it cannot see a listener acting inside an interval: it reads the same at
both ends of a cut-off fix. This one keeps its plant, plan and variants, but
steps the plant one minute at a time and hands every minute's room reading to
the production listener (``early_cutoff.on_room_event``) through the same
``arm`` call the coordinator's cycle makes. A cut sets the applied power to
zero until the next 30-minute solve, as the cycle's own switch write would.

Variants (the controller never learns them):
  NULL    plant == model: the null control. The cut-off should never fire.
  OWNMIN  switch-only pump: whenever the plan asks for any heat, the pump runs
          at max(plan, PUMP_OWN_KW). The finder's case: the room stays inside
          the margin, so the cut-off should not fire here either.
  HOT     the same pump at max(plan, HOT_OWN_KW) with a plant COP 1.4x the
          model's. Measured: the room still stays inside the margin.
  SUN     the plan's own power, with SUN_W_M2 of sun on the plant from 10:00
          to 15:00 that the controller's forecast does not carry: an
          overshoot past the margin. Measured on the mild day: the solve
          already plans the pump off in the warm hours, so nothing is on to cut.
  COLDSUN SUN on a COLD_OUT day. Measured: the 30-minute re-solve already has
          the pump off before the room passes the margin.
  LIGHT   a plant room LIGHT_MASS_SCALE x the model's thermal mass, with the
          OWNMIN pump on a COLD_OUT day: the room climbs past the margin
          inside one interval with the pump on, the one case the cut-off is for.

Each line also prints the minutes the room spent past target + margin with
the pump on, and why the listener held off (``last_held`` per reading).

CUTOFF_RULE=literal replaces the module's threshold with the decision's
literal rule, the active comfort target + MARGIN_K alone, for comparison.
CUTOFF_RULE=middle is literal, except that a step whose plan predicts the
room above the target is exempt (no cut at all). CUTOFF_ARMS=on runs only
the cut-off arm.
SIM_STEPS shortens the simulated day (15-minute steps, default 96).

    python3 tools/audit/harnesses/early_cutoff_closed_loop.py [VARIANT...]

Run from a worktree root with the CI venv and
PYTHONPATH=tests/hastub:custom_components:tests.
"""
from __future__ import annotations

import asyncio
import os
import sys
from collections import Counter
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import numpy as np
from harness import FakeHass, FakeState
from homeassistant.util import dt as dt_util
from profiles import house, prices, solve_inputs

from heatpump_optimizer import early_cutoff
from heatpump_optimizer.boost import BoostState
from heatpump_optimizer.const import MODE_AUTO
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.pump_arbiter import ArbiterInputs
from heatpump_optimizer.thermal_model import (
    MIN_RUNNING_DRAW_KW,
    ThermalModel,
    ThermalParameters,
    ThermalState,
    WeatherSeries,
)

OUT = 12.0
PUMP_OWN_KW = 3.0
HOT_OWN_KW = 6.0
SUN_W_M2 = 600.0
COLD_OUT = -2.0
LIGHT_MASS_SCALE = 0.15
SIM_STEPS = int(os.environ.get("SIM_STEPS", 96))
START = datetime(2026, 10, 9, 0, 0, tzinfo=UTC)
N = 96
SWITCH, ROOM = "switch.heat_pump", "sensor.indoor"


def params(cop_mult: float = 1.0, mass_scale: float = 1.0) -> ThermalParameters:
    p = ThermalParameters.from_config(house(dhw=False, heat_pump_min_power=1.0,
                                            heat_pump_max_power=6.0, min_temperature=18.0))
    p.dhw_enabled = False
    p.cop_scale = p.cop_scale * cop_mult
    p.room_thermal_mass = p.room_thermal_mass * mass_scale
    return p


def wx(n: int, sun: float = 0.0, out: float = OUT) -> WeatherSeries:
    z = np.zeros(n)
    return WeatherSeries(outdoor_temps=np.full(n, out), wind_speeds=z, precipitation=z,
                         solar_radiation=np.full(n, sun))


def _literal_threshold(inp: object, cfg: OptimizationConfig, now: datetime) -> float:
    local = dt_util.as_local(now)
    return float(cfg.get_comfort_temp(local.hour + local.minute / 60.0, when=local)) + early_cutoff.MARGIN_K


def _middle_threshold(inp: object, cfg: OptimizationConfig, now: datetime) -> float:
    base = _literal_threshold(inp, cfg, now) - early_cutoff.MARGIN_K
    planned = early_cutoff._planned_room(getattr(inp, "plan", None), now)
    return float("inf") if planned and max(planned) > base else base + early_cutoff.MARGIN_K


_RULES = {"literal": _literal_threshold, "middle": _middle_threshold}
if os.environ.get("CUTOFF_RULE") in _RULES:
    early_cutoff.threshold = _RULES[os.environ["CUTOFF_RULE"]]  # type: ignore[assignment]


def run(label: str, plant_kind: str, cutoff: bool) -> None:
    ctrl, plant = ThermalModel(params()), ThermalModel(params(
        1.4 if plant_kind == "HOT" else 1.0, LIGHT_MASS_SCALE if plant_kind == "LIGHT" else 1.0))
    cfg = OptimizationConfig(horizon_hours=24, time_step_minutes=15, target_temp=21.0,
                             min_temp=18.0, max_temp=23.0, comfort_temp_day=21.0,
                             comfort_temp_night=19.5)
    opt = HeatPumpOptimizer(ctrl, cfg)
    pr2 = np.concatenate([prices("winter_typical", START),
                          prices("winter_typical", START + timedelta(days=1))])
    hass = FakeHass({SWITCH: FakeState("off", last_updated=START), ROOM: FakeState("21.0")})
    hass.async_create_task = lambda coro: asyncio.run(coro)  # the switch write, at once
    held, unloads = early_cutoff.CutoffState(), []
    room, slab, ctrl_slab = 21.0, 22.0, 22.0
    rooms, plant_e, cuts, over_on, held_why = [], 0.0, 0, 0, Counter()
    out = COLD_OUT if plant_kind in ("COLDSUN", "LIGHT") else OUT
    for k in range(0, SIM_STEPS, 2):
        t0 = START + timedelta(minutes=15 * k)
        st = ThermalState(room_temperature=room, slab_temperature=ctrl_slab, outdoor_temperature=out,
                          upper_floor_temperature=room, lower_floor_temperature=room,
                          buffer_tank_temperature=35.0)
        z = np.zeros(N)
        r = opt.optimize(inputs=solve_inputs(initial_state=st, prices=pr2[k:k + N],
                                             outdoor_temps=np.full(N, out), wind_speeds=z,
                                             precipitation=z, solar_radiation=z, start_time=t0))
        plan = np.asarray(r.power_schedule[:2], dtype=float)
        ctrl_slab = float(r.slab_temp_trajectory[2]) if len(r.slab_temp_trajectory) > 2 else ctrl_slab
        on = bool(plan[0] > MIN_RUNNING_DRAW_KW)
        prior = hass.states.get(SWITCH)
        if (prior.state == "on") != on:  # the cycle's own switch write
            hass.states.set(SWITCH, FakeState("on" if on else "off", last_updated=t0))
        inp = ArbiterInputs(hass=hass, config={"indoor_temp_entity": ROOM,
                                               "heat_pump_switch_entity": SWITCH,
                                               "optimization_interval": 30},
                            mode=MODE_AUTO, plan=r, plan_stale=False, entry_released=False,
                            state=st, thermal=ctrl, params=ctrl.params,
                            action={"heat_pump_on": on}, measured_power_kw=None,
                            disinfecting=False)
        wiring = early_cutoff.CutoffInputs(lambda inp=inp: inp, BoostState(), cfg)
        if cutoff:
            dt_util.freeze(t0)
            asyncio.run(early_cutoff.arm(held, wiring, unloads.append, t0))
        for m in range(30):
            level = plan[m // 15]
            if plant_kind in ("OWNMIN", "HOT", "LIGHT") and level > MIN_RUNNING_DRAW_KW:
                level = max(level, HOT_OWN_KW if plant_kind == "HOT" else PUMP_OWN_KW)
            if hass.states.get(SWITCH).state != "on":
                level = 0.0
            pst = ThermalState(room_temperature=room, slab_temperature=slab, outdoor_temperature=out,
                               upper_floor_temperature=room, lower_floor_temperature=room,
                               buffer_tank_temperature=35.0)
            minute = t0 + timedelta(minutes=m)
            sun = SUN_W_M2 if plant_kind in ("SUN", "COLDSUN") and 10 <= minute.hour < 15 else 0.0
            traj = plant.simulate_trajectory(pst, np.array([level]), wx(1, sun, out), dt_hours=1 / 60)
            room, slab = float(traj[0][-1]), float(traj[1][-1])
            rooms.append(room)
            plant_e += level / 60
            over_on += int(level > 0.0 and room > 21.0 + early_cutoff.MARGIN_K)
            if cutoff:
                now = t0 + timedelta(minutes=m + 1)
                dt_util.freeze(now)
                before, held.last_held = held.count, None
                early_cutoff.on_room_event(held, wiring, SimpleNamespace(
                    data={"new_state": FakeState(f"{room:.2f}")}))
                held_why[held.last_held] += held.last_held is not None
                if held.count > before:
                    cuts += 1
                    hass.states.set(SWITCH, FakeState("off", last_updated=now))
    dt_util.freeze(None)
    a = np.array(rooms)
    print(f"{label:30s} room {a.min():5.2f}-{a.max():5.2f}  >21.5: {np.sum(a > 21.5) / 60:5.2f} h  "
          f">22.0: {np.sum(a > 22.0) / 60:5.2f} h  pump {plant_e:5.1f} kWh  cuts {cuts}  "
          f"warm+on {over_on} min  held {dict(+held_why)}")


print(f"mild day {OUT} degC, model p_min 1.0, comfort 21 day / 19.5 night; slab open-loop; "
      "plant stepped per minute")
for kind in sys.argv[1:] or ("NULL", "OWNMIN", "HOT", "SUN", "COLDSUN", "LIGHT"):
    for on in (True,) if os.environ.get("CUTOFF_ARMS") == "on" else (False, True):
        run(f"{kind:6s} cut-off {'on ' if on else 'off'}", kind, on)
