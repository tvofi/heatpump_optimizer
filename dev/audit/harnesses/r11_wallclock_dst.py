"""Round-11 class P7 (issue 3786): wall-clock hour arithmetic across a DST day.

Usage (repository root):

    PYTHONPATH=tests/hastub:custom_components python3 \
        dev/audit/harnesses/r11_wallclock_dst.py <instance> --day spring|autumn|plain

Exit 1 when the instance disagrees with the zone's real clock on that day,
0 when it agrees, 2 when a precondition of the probe itself fails (the probe
refuses rather than reading a skipped arm as agreement).

Instances, and the clock each is measured against:

* ``hours_until_next_window``: the hours it returns from 00:30 local until a
  04:00 window against the real elapsed hours between those two local wall
  times in Europe/Stockholm (2.5 on the spring day, 4.5 on the autumn day).
* ``simulate_trajectory``, ``simulate_trajectory_batch``,
  ``simulate_trajectory_with_dhw``: the hour of day each of 96 quarter-hour
  steps from local midnight reads its learned internal-gains profile at (and,
  for the DHW twin, its draw pattern at), recorded through the model's own
  ``internal_gains_at`` / ``dhw_draw_rates``, against the step clock the
  optimizer builds (``optimizer._step_clock``) for the same start.

Each trajectory instance is driven with whatever hour argument its signature
takes: ``step_hours`` (the step clock itself) where the signature has it, else
``start_hour`` (the clock's first hour).
"""

from __future__ import annotations

import argparse
import inspect
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np

from heatpump_optimizer.dhw_schedule import hours_until_next_window
from heatpump_optimizer.optimizer import _step_clock
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
    WeatherSeries,
)

ZONE = ZoneInfo("Europe/Stockholm")
DAYS = {
    "spring": datetime(2026, 3, 29, tzinfo=ZONE),
    "autumn": datetime(2026, 10, 25, tzinfo=ZONE),
    "plain": datetime(2026, 6, 10, tzinfo=ZONE),
}
N_STEPS = 96
DT_H = 0.25


def _refuse(msg: str) -> int:
    print(f"PRECONDITION FAILED: {msg}")
    return 2


def probe_next_window(day: datetime) -> int:
    now = day.replace(hour=0, minute=30)
    window_start = day.replace(hour=4)
    real_h = (
        window_start.astimezone(ZONE).timestamp() - now.timestamp()
    ) / 3600.0
    signature = inspect.signature(hours_until_next_window)
    if "now" in signature.parameters:
        got = hours_until_next_window(now=now, windows=[(4.0, 6.0)])
    else:
        got = hours_until_next_window(0.5, [(4.0, 6.0)])
    print(f"real hours 00:30 -> 04:00: {real_h}; returned: {got}")
    return 0 if got is not None and abs(got - real_h) < 1e-9 else 1


def probe_trajectory(name: str, day: datetime) -> int:
    _, step_hours = _step_clock(day, N_STEPS, DT_H)
    # A distinct gain for every hour of the day, so a one-hour slip reads.
    model = ThermalModel(
        ThermalParameters(internal_gains_profile=[0.05 * h for h in range(24)])
    )
    seen: list[float] = []
    draws: list[np.ndarray] = []
    real_gains = model.internal_gains_at
    real_draws = model.dhw_draw_rates

    def gains(hour_of_day):  # noqa: ANN001
        if hour_of_day is not None:
            seen.append(float(hour_of_day))
        return real_gains(hour_of_day)

    def draw_rates(hours):  # noqa: ANN001
        draws.append(np.asarray(hours, dtype=float).copy())
        return real_draws(hours)

    model.internal_gains_at = gains  # type: ignore[method-assign]
    model.dhw_draw_rates = draw_rates  # type: ignore[method-assign]
    state = ThermalState(room_temperature=20.0, outdoor_temperature=0.0)
    weather = WeatherSeries(outdoor_temps=np.zeros(N_STEPS))
    power = np.full(N_STEPS, 2.0)
    method = getattr(model, name)
    params = inspect.signature(method).parameters
    clock = (
        {"step_hours": step_hours}
        if "step_hours" in params
        else {"start_hour": float(step_hours[0])}
    )
    if name == "simulate_trajectory":
        method(state, power, weather, dt_hours=DT_H, **clock)
    elif name == "simulate_trajectory_batch":
        method(state, power[None, :], weather, dt_hours=DT_H, **clock)
    else:
        method(state, power, np.zeros(N_STEPS), weather, dt_hours=DT_H, **clock)

    # The gains hour is read once per step or once per substep; the probe
    # needs at least one read per step and keys each read to its step.
    if len(seen) < N_STEPS or len(seen) % N_STEPS:
        return _refuse(f"{len(seen)} gains reads for {N_STEPS} steps")
    per = len(seen) // N_STEPS
    read = np.array(seen).reshape(N_STEPS, per)
    want = np.floor(step_hours % 24.0)
    slips = [
        i for i in range(N_STEPS)
        if not np.all(np.floor(read[i] % 24.0) == want[i])
    ]
    if name == "simulate_trajectory_with_dhw":
        if len(draws) != 1 or len(draws[0]) != N_STEPS:
            return _refuse(f"draw-pattern reads {[len(d) for d in draws]}")
        slips += [
            N_STEPS + i for i in range(N_STEPS)
            if np.floor(draws[0][i] % 24.0) != want[i]
        ]
    reads = N_STEPS * (2 if name == "simulate_trajectory_with_dhw" else 1)
    print(
        f"{name}: {len(slips)} of {reads} step-hour reads off the step clock "
        f"(first: {slips[:3]})"
    )
    return 1 if slips else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "instance",
        choices=(
            "hours_until_next_window",
            "simulate_trajectory",
            "simulate_trajectory_batch",
            "simulate_trajectory_with_dhw",
        ),
    )
    ap.add_argument("--day", choices=tuple(DAYS), required=True)
    args = ap.parse_args()
    day = DAYS[args.day]
    if args.instance == "hours_until_next_window":
        return probe_next_window(day)
    return probe_trajectory(args.instance, day)


if __name__ == "__main__":
    sys.exit(main())
