"""R10-SETPOINT-BOOST: the heating floor against the gate, the censored draw window, and the solver nulls.

    PYTHONPATH=tests/hastub:custom_components:tests \\
        python3 dev/audit/harnesses/r10_setpoint_boost.py [--no-solves]

Synthetic throughout; no private data. Three parts, each run on the tree the
harness runs in (a tree without a symbol falls back to what main does):

1. ``floor``: every inlet 10-40 degC on every entity minimum the gate can
   take (none, 20, 25, 28, 30): how many cells write a heating step at the
   floor at or below what a step that does not heat writes.
2. ``window``: an owner-shaped set-point-driven install, configured
   1.5-5.0 kW, whose synthetic pump truly runs up to 3.0 kW and idles at
   0.30 kW. Its draw is a function of the set-point the tree writes and the
   tank: idle below a 4 K lift, else ``min(3.0, 0.3 + 0.12 * lift)``. A day
   of the levels a plan books (p_min 70 %, 2 kW 20 %, 3 kW 10 %) over tanks
   18-34 degC is folded through ``draw_range.fold``; then a probe-shaped
   window where every sample was written at the ceiling. Printed: engaged,
   the learned (low, high), the idle draw.
3. ``solves`` (skipped with ``--no-solves``): 16 synthetic installs -- UA
   scale 0.6/1.7 x 750 L buffer or none x hot water off/on x set-point-driven
   (levels ship rounded) or duty-cycling -- each solved at one spread price
   day starting 21:00 and at its flat mean, with and without #2445's relaxed
   start. Printed per cell and price: the sha1 of the published plan (the
   byte-identity null across trees), the objective delta of the relaxed
   start, the share of space kWh at near-floor levels (<= 1.1 x p_min) in
   steps priced above the day's median, the cheapest quarter's share of
   space kWh, and ``predicted_savings``. The failure count is printed last.
"""
from __future__ import annotations

import hashlib
import inspect
import itertools
import sys
from datetime import datetime, timezone
from types import SimpleNamespace as NS

import numpy as np

from harness import FakeHass, FakeState
from heatpump_optimizer import draw_range, pump_arbiter
from heatpump_optimizer import optimizer as opt_mod
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from profiles import solve_inputs

T0 = datetime(2026, 1, 12, 20, 0, tzinfo=timezone.utc)
ENTITY = "number.flow"
CFG_MIN, CFG_MAX, TRUE_MAX, IDLE_KW = 1.5, 5.0, 3.0, 0.30


def write(kw: float, tank: float, entity_min: float | None = 20, duty: str = "space"):
    attrs = {"max": 70} if entity_min is None else {"min": entity_min, "max": 70}
    states = {ENTITY: FakeState("40", attributes=attrs),
              "sensor.tank": FakeState(str(tank), unit="°C")}
    return pump_arbiter._flow_target(NS(
        config={"space_setpoint_entity": ENTITY, "buffer_tank_temp_entity": "sensor.tank"},
        hass=FakeHass(states),
        state=NS(outdoor_temperature=0.0, buffer_tank_temperature=tank,
                 floor_return_temperature=None),
        thermal=NS(params=None, curve_flow_temp=lambda _o: None),
        params=NS(min_electrical_power=CFG_MIN, max_electrical_power=CFG_MAX),
        plan=NS(timestamps=[T0], power_schedule=[kw]),
    ), duty, T0)


def floor_census() -> None:
    cells = [(t, lo) for t in range(10, 41) for lo in (None, 20, 25, 28, 30)]
    bad = [c for c in cells if not write(CFG_MIN, *c) > write(0.0, *c, duty="idle")]
    print(f"floor: cells {len(cells)} heating floor at or below the gate {len(bad)} "
          f"(first {bad[:3]})")


def drawn(setpoint: float, tank: float) -> float:
    lift = setpoint - tank
    return IDLE_KW if lift < 4.0 else min(TRUE_MAX, 0.3 + 0.12 * lift)


def fold_window(probe: bool) -> draw_range.DrawRange:
    takes = "command" in inspect.signature(draw_range.fold).parameters
    d = draw_range.DrawRange()
    params = NS(min_electrical_power=CFG_MIN, max_electrical_power=CFG_MAX)
    levels = [CFG_MIN] * 7 + [2.0] * 2 + [3.0]
    gate = write(0.0, 20.0, duty="idle")
    ceiling = write(CFG_MAX, 20.0)
    for k in range(96):
        tank = 18.0 + 16.0 * ((k * 5) % 17) / 16.0
        if k % 4 == 0:  # an idle step at the gate
            sp, split = gate, (0.0, 0.0)
        else:
            sp = ceiling if probe else write(levels[k % len(levels)], tank)
            split = (CFG_MAX if probe else levels[k % len(levels)], 0.0)
        cmd = NS(written_c=sp, gate_c=gate, ceiling_c=ceiling)
        kw = {"command": cmd} if takes else {}
        draw_range.fold(d, drawn(sp, tank), split, params, frozen=False,
                        distorted=False, defrost=False, **kw)
    return d


def window_census() -> None:
    for probe in (False, True):
        d = fold_window(probe)
        idle = getattr(d, "idle_kw", lambda: None)()
        print(f"window {'probe' if probe else 'plan'}: running samples {len(d.samples)} "
              f"engaged {d.engaged} observed {d.observed()} idle {idle} "
              f"planned {d.planned(CFG_MIN, CFG_MAX)}")


STEPS = np.arange(96)
HOUR = (21.0 + STEPS / 4.0) % 24.0
SPREAD = 1.6 * np.interp(
    HOUR, [0, 3, 5, 7, 9, 12, 15, 17, 19, 21, 23, 24],
    [0.65, 0.58, 0.62, 1.2, 1.35, 0.95, 0.9, 1.3, 1.5, 1.25, 0.85, 0.65],
)
FLAT = np.full(96, float(SPREAD.mean()))
CELLS = list(itertools.product((0.6, 1.7), (750.0, 0.0), (False, True), (True, False)))


def solve(cell, prices, relaxed: bool):
    loss, buffer_l, dhw, rounded = cell
    p = ThermalParameters()
    if buffer_l:
        p.mixing_valve_mode, p.buffer_tank_volume = "manual", buffer_l
    p.min_electrical_power, p.max_electrical_power = CFG_MIN, CFG_MAX
    p.dhw_enabled, p.house_heat_loss_scale = dhw, loss
    opt = HeatPumpOptimizer(ThermalModel(p), OptimizationConfig(clamp_planned_levels=rounded))
    kept = getattr(opt_mod, "_relaxed_starts", None)
    if not relaxed and kept is not None:
        opt_mod._relaxed_starts = lambda _opt, *args: args[-2]
    try:
        return opt.optimize(inputs=solve_inputs(
            initial_state=ThermalState(
                room_temperature=20.0, upper_floor_temperature=20.0,
                lower_floor_temperature=20.0, slab_temperature=20.5,
                outdoor_temperature=5.0, buffer_tank_temperature=24.0,
                dhw_temperature=48.0,
            ),
            prices=prices, outdoor_temps=np.full(96, 5.0), start_time=T0,
        ))
    finally:
        if kept is not None:
            opt_mod._relaxed_starts = kept


def shape(result, prices) -> tuple[float, float]:
    plan = np.asarray(result.power_schedule, float)
    kwh = plan.sum()
    dear = prices > np.median(SPREAD)
    near = (plan > 0) & (plan <= 1.1 * CFG_MIN) & dear
    cheap = np.argsort(SPREAD, kind="stable")[:24]
    return (float(plan[near].sum() / kwh) if kwh else 0.0,
            float(plan[cheap].sum() / kwh) if kwh else 0.0)


def solve_census() -> int:
    failures = 0
    for tag, prices in (("spread", SPREAD), ("flat", FLAT)):
        lower = higher = same = 0
        for cell in CELLS:
            try:
                fix, ctl = solve(cell, prices, True), solve(cell, prices, False)
            except Exception as err:  # counted, never dropped
                failures += 1
                print(f"  {tag} {cell} failed: {err!r}")
                continue
            sha = hashlib.sha1(np.asarray(
                fix.power_schedule + list(fix.dhw_power_schedule or []), float
            ).tobytes()).hexdigest()[:12]
            delta = float(fix.objective_value) - float(ctl.objective_value)
            lower += delta < -1e-9
            higher += delta > 1e-9
            same += fix.power_schedule == ctl.power_schedule
            near, cheap = shape(fix, prices)
            print(f"  {tag} {cell} plan {sha} relaxed-delta {delta:+.3f} "
                  f"near-floor-dear {near:.3f} cheap-quarter {cheap:.3f} "
                  f"savings {float(fix.predicted_savings):.2f}")
        print(f"{tag}: cells {len(CELLS)} relaxed start objective lower {lower} "
              f"higher {higher} identical plan {same}")
    return failures


def main(argv: list[str]) -> int:
    floor_census()
    window_census()
    failures = 0 if "--no-solves" in argv else solve_census()
    print(f"failures {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
