#!/usr/bin/env python3
"""The room lift through the production solver (#3616, R11-OUTSIDE-ROOMS-P2's fixer's instrument).

Owner report, no finder harness. Drives ``rooms.resolve`` and ``rooms.lifted`` with the
design note's fixture (room A 18.0 under a 21.0 target, B and C at theirs, D
colder but switched off) and hands the array it returns to
``HeatPumpOptimizer.optimize`` as ``SolveLimits.min_temp_margins``: 24 h at
15 min from 12:00, floor 19.5, target 20.0 day and night, ceiling 23.0, the
house at 19.6 (the reporter's figure) with the slab one kelvin above, on
``weather("shoulder")`` and ``prices("winter_typical")``. Run it from a
worktree root:

    PYTHONPATH=tests/hastub:custom_components:tests \
        OPENBLAS_NUM_THREADS=1 python3 dev/audit/harnesses/room_lift_solve.py

Rows, each ``kWh space, lowest and mean planned temperature over hours 3 to
24, highest planned temperature less the comfort target, sha1 of the space
power schedule``:
  * ``none`` -- no margins: the plan an install with no room list gets.
  * ``zeros`` -- an all-zero margin array: the null control, the same sha1.
  * ``gated_<name>`` -- the fixture under each gate: ``rooms.lifted`` hands
    back None, so the sha1 is ``none``'s.
  * ``lift`` -- the fixture's lift (ramped from the house's 0.1 K margin, to
    the 0.5 K day band, 1.0 K at night). Expect more space energy, a higher
    lowest temperature, and a lifted floor (the configuration's floor plus
    the array) at or under the comfort target at every step, and at it once
    the ramp has caught up. The highest planned temperature may rise above
    ``none``'s: a floor held at the target leaves the plan's stored heat above
    it, and that rise is accepted (round-11 ruling of 2026-11-18, option A:
    no clip and no headroom under the target), so it is printed and its
    direction checked, never bounded.
  * ``lift_cap_removed`` / ``lift_cap_zero`` -- the null control for the
    peak: ``rooms.ROOM_LIFT_CAP_C`` set to infinity and to zero around
    ``rooms.resolve``. With the cap removed the peak still rises over
    ``none``'s (the rise is the floor's, not the cap's); at zero no lift is
    held and the plan is ``none``'s.
  * ``lift_pinned_off`` / ``none_pinned_off`` -- a forced-off space pin for
    hours 1 to 3 with the lifted array forced in (the coordinator never
    builds this: a pin gates the lift) against the same pin unlifted: the
    released-pin count each plan reports, what the manual-pin gate protects.

Solve time is not printed: it moves inside the run-to-run spread
(``tests/stress.py`` is the instrument for it).
"""
from __future__ import annotations

import hashlib
import sys
from datetime import UTC, datetime, timedelta

import numpy as np

from heatpump_optimizer import rooms
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from profiles import DT, N, house, prices, solve_inputs, weather

START = datetime(2026, 4, 15, 12, 0, tzinfo=UTC)
HOUSE_C, FLOOR_C, TARGET_C = 19.6, 19.5, 20.0
OPEN = dict(enabled=True, economy=False, open_window=False, away=False,
            manual_pin=False, two_zone=False)


class _Owner:
    """What the side tables key on in place of a coordinator."""


def _room(entity: str, temp: float, target: float, mode: str = "heat") -> rooms.RoomReading:
    return rooms.RoomReading(entity_id=entity, temperature_c=temp, target_c=target, hvac_mode=mode)


FIXTURE = (_room("climate.a", 18.0, 21.0), _room("climate.b", 20.4, 20.0),
           _room("climate.c", 20.4, 16.0), _room("climate.d", 17.0, 22.0, mode="off"))


def _config() -> OptimizationConfig:
    return OptimizationConfig(
        horizon_hours=24, time_step_minutes=15, target_temp=TARGET_C, min_temp=FLOOR_C,
        max_temp=23.0, comfort_temp_day=TARGET_C, comfort_temp_night=TARGET_C)


def margins(**signals: bool) -> np.ndarray | None:
    owner = _Owner()
    rooms.record(owner, FIXTURE)
    held = rooms.resolve(rooms.readings_of(owner), None, rooms.gate(**dict(OPEN, **signals)),
                         _config(), HOUSE_C, START)
    return rooms.lifted(held, None, _config(), START, N)


def solve(min_temp_margins: np.ndarray | None, space_pins: np.ndarray | None = None):
    cfg = house(target_temperature=TARGET_C, min_temperature=FLOOR_C)
    params = ThermalParameters.from_config(cfg)
    outdoor, wind, rain, solar = weather("shoulder", START)
    state = ThermalState(
        room_temperature=HOUSE_C, slab_temperature=HOUSE_C + 1.0,
        outdoor_temperature=float(outdoor[0]), dhw_temperature=50.0,
        dhw_hours_since_legionella=20.0, upper_floor_temperature=HOUSE_C,
        lower_floor_temperature=HOUSE_C, buffer_tank_temperature=40.0)
    return HeatPumpOptimizer(ThermalModel(params), _config()).optimize(inputs=solve_inputs(
        initial_state=state, prices=prices("winter_typical", START), outdoor_temps=outdoor,
        wind_speeds=wind, precipitation=rain, solar_radiation=solar, start_time=START,
        min_temp_margins=min_temp_margins, space_pins=space_pins))


def row(name: str, result) -> tuple[float, float, float, str]:
    power = np.asarray(result.power_schedule, dtype=float)
    temps = np.asarray(result.room_temp_trajectory[1:], dtype=float)
    late = temps[int(3 / DT):]
    sha = hashlib.sha1(np.round(power, 6).tobytes()).hexdigest()[:12]
    over = float(temps.max() - TARGET_C)
    print(f"{name:<18} space_kwh={power.sum() * DT:6.2f} min_c={late.min():6.3f} "
          f"mean_c={late.mean():6.3f} max_over_target_c={over:+.3f} sha1={sha} "
          f"status={result.status}")
    return float(power.sum() * DT), float(late.min()), over, sha


def main() -> int:
    none = row("none", solve(None))
    zeros = row("zeros", solve(np.zeros(N)))
    gated = {}
    for name in ("enabled", "economy", "open_window", "away", "manual_pin", "two_zone"):
        got = margins(**{name: name != "enabled"})
        gated[name] = got is None and row(f"gated_{name}", solve(got))[3] == none[3]
    lift_margins = margins()
    assert lift_margins is not None
    print("lift margins, first 8 steps and the largest:",
          np.round(lift_margins[:8], 4).tolist(), float(lift_margins.max()))
    lift = row("lift", solve(lift_margins))
    capped = {}
    for name, cap in (("lift_cap_removed", float("inf")), ("lift_cap_zero", 0.0)):
        saved, rooms.ROOM_LIFT_CAP_C = rooms.ROOM_LIFT_CAP_C, cap
        try:
            got = margins()
        finally:
            rooms.ROOM_LIFT_CAP_C = saved
        capped[name] = (got, row(name, solve(got)))
    config = _config()
    clock = [START + timedelta(hours=DT * i) for i in range(N)]
    lifted_floor_ok = all(
        config.get_temp_bounds(t.hour + t.minute / 60.0, when=t)[0] + lift_margins[i]
        <= config.get_comfort_temp(t.hour + t.minute / 60.0, when=t) + 1e-9
        for i, t in enumerate(clock))
    ramped = int(np.argmax(lift_margins >= 0.5))
    lifted_floor_at_target = ramped > 0 and all(
        abs(config.get_temp_bounds(t.hour + t.minute / 60.0, when=t)[0] + lift_margins[i]
            - config.get_comfort_temp(t.hour + t.minute / 60.0, when=t)) < 1e-9
        for i, t in enumerate(clock) if i >= ramped)
    pins = np.full(N, np.nan)
    pins[int(1 / DT):int(3 / DT)] = 0.0
    pinned_none, pinned_lift = solve(None, pins), solve(lift_margins, pins)
    row("none_pinned_off", pinned_none)
    row("lift_pinned_off", pinned_lift)
    released = [len(r.manual_released_space) for r in (pinned_none, pinned_lift)]
    print(f"released space pins: unlifted={released[0]} lifted={released[1]}")
    checks = {
        "zeros reproduce none": zeros[3] == none[3],
        "every gate reproduces none": all(gated.values()),
        "the lift changes the plan": lift[3] != none[3],
        "the lift plans more space energy": lift[0] > none[0],
        "the lift raises the lowest planned temperature": lift[1] > none[1],
        "the lifted floor is at or under the comfort target at every step": lifted_floor_ok,
        "the lifted floor is at the comfort target at every step past the ramp": lifted_floor_at_target,
        "the lift may raise the plan peak over the unlifted plan's (accepted)": lift[2] > none[2],
        "the zeros control leaves the peak at the unlifted plan's": zeros[2] == none[2],
        "null control: with the cap removed the peak still rises":
            capped["lift_cap_removed"][1][2] > none[2],
        "null control: at a zero cap nothing is lifted and the plan is none's":
            capped["lift_cap_zero"][0] is None and capped["lift_cap_zero"][1][3] == none[3],
    }
    for name, ok in checks.items():
        print(f"{'ok  ' if ok else 'FAIL'} {name}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
