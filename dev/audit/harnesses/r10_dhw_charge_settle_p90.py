"""R10-OUTSIDE-DHW-CHARGE-SETTLE: the heavy-day p90 a charge-start dip adds.

Drives one ``DhwProfileLearner`` per arm through 28 simulated days, the
tank integrated per minute and the learner sampled at each of
``CADENCES_MIN`` (the production refresh range and a 5-min null control),
and prints, per draw window, the folded occurrence
count and ``DrawStats.quantile(label, 0.9)`` -- the heavy-day statistic the
planner reads -- plus the usage-profile points learned. Arms:

  dip       a daily morning draw, then a 10-minute DHW charge whose start
            drops the reading 4 K, the dip peaking after the charge ends
  truth     the same trace with the dip removed: what the learner should see
  flat      the same draws and the same reheat, the DHW heating flag never
            set and no dip -- what a compressor start for space heating is
            to the learner, whose only heating input is the plan's DHW
            flag: the flat control, which the fix must leave bit-identical
  dip@max   ``dip`` and ``truth`` with the cooling rate pinned at
  truth@max DHW_COOLING_RATE_MAX, the clamp end of the learner's input
            range (every arm starts from a fresh learner: zero evidence)

Run from the tree under test, at both ends:

  PYTHONPATH=tests/hastub:custom_components python3 \
    dev/audit/harnesses/r10_dhw_charge_settle_p90.py [cadence_min ...]

Exit 0 always; it measures, the caller compares.
"""

from __future__ import annotations

import asyncio
import types
from datetime import datetime, timedelta

import numpy as np

from heatpump_optimizer import dhw_learning as dl
from heatpump_optimizer.const import DHW_COOLING_RATE_MAX
from heatpump_optimizer.dhw_draws import labels_for
from heatpump_optimizer.thermal_model import TANK_ROOM_AMBIENT_TEMP, ThermalParameters

STEP_MIN = 5
DAYS = 28
SEED = 3434
DIP_K = 4.0  # charge-start transient depth, the author's 3-5 K
DIP_PEAK_MIN = 15.0  # the dip bottoms 5 min after the 10-minute charge ends
SETPOINT_C = 55.0
CHARGE_START_MIN = 7 * 60 + 30  # every day's charge starts at 07:30
#: The learner's production cadence is the coordinator refresh,
#: ``optimization_interval``: 30 min by default, 10-120 min in 5-min steps.
#: 5 min is below every configurable interval: a sub-cadence null control.
CADENCES_MIN = (5, 10, 15, 30, 60)


def dip_at(minutes_since_start: float) -> float:
    """The reading's offset below the true tank temperature after a charge start."""
    if minutes_since_start < 0:
        return 0.0
    if minutes_since_start <= DIP_PEAK_MIN:
        return DIP_K * minutes_since_start / DIP_PEAK_MIN
    return max(0.0, DIP_K * (1.0 - (minutes_since_start - DIP_PEAK_MIN) / 20.0))


def run(
    arm: str, rate: float | None = None, draw_min: int = 7 * 60, charge_min: int = 10,
    step_min: int = STEP_MIN,
) -> dict:
    """One arm; the tank is integrated per minute, the learner sampled every ``step_min``.

    The physics is the same at every cadence, so arms at two cadences differ
    only in what the learner sees. The plan's DHW flag is read at each sample,
    as ``dhw_heating_active`` is (the plan's scheduled power, not a device state).
    """
    params = ThermalParameters()
    params.dhw_enabled = True
    cap = params.dhw_store.capacity_kwh_per_c
    clock = [datetime(2026, 11, 2, 0, 0)]
    heating = [False]
    usage_points = [0]

    learner = dl.DhwProfileLearner(
        None, "h", lambda: params,
        publish=lambda **k: usage_points.__setitem__(0, usage_points[0] + 1),
        frozen=lambda *a: None,
        heating_active=lambda: heating[0],
        external_heat_active=lambda: False,
    )

    async def _noop() -> None:
        return None

    learner.async_save_draws = _noop
    learner.async_save_profile = _noop
    true_rate = 0.3
    learner.cooling_rate = rate if rate is not None else true_rate
    dl.dt_util = types.SimpleNamespace(now=lambda: clock[0])

    rng = np.random.default_rng(SEED)
    draws_kwh = rng.lognormal(mean=1.0, sigma=0.5, size=DAYS)
    t_true = SETPOINT_C
    flagged = arm != "flat"  # flat: an unflagged reheat, no dip
    heat_per_min = 1.0 - 0.5 ** (1.0 / 5.0)  # halves the gap to the setpoint in 5 min
    loop = asyncio.new_event_loop()
    for i in range(DAYS * 24 * 60):
        day, minute = divmod(i, 24 * 60)
        t_true -= true_rate * (t_true - TANK_ROOM_AMBIENT_TEMP) / 25.0 / 60.0
        if draw_min <= minute < draw_min + 15:  # the morning draw, over 15 min
            t_true -= draws_kwh[day] / 15.0 / cap
        since_charge = minute - CHARGE_START_MIN
        if 0 <= since_charge < charge_min:
            t_true += (SETPOINT_C - t_true) * heat_per_min
        if i % step_min:
            continue
        now = clock[0] = datetime(2026, 11, 2) + timedelta(minutes=i)
        heating[0] = flagged and 0 <= since_charge < charge_min
        reading = t_true
        if arm.startswith("dip"):
            reading -= dip_at(since_charge)
        loop.run_until_complete(learner.async_learn_dynamics(round(reading, 2)))
    loop.close()
    stats = learner.draw_stats
    out = {
        "usage_points": usage_points[0],
        "profile_h7": round(learner.hourly_profile[7], 4),
        "cooling_rate": round(learner.cooling_rate, 4),
    }
    for label in labels_for(params.dhw_demand_windows):
        q = stats.quantile(label, 0.9)
        out[label] = (stats.count(label), None if q is None else round(q, 4))
    return out


#: (geometry name, draw start minute of the day, charge length in minutes);
#: the charge always starts at 07:30.
GEOMETRIES = (
    ("draw-0700", 7 * 60, 10),  # the draw ends before the charge
    ("draw-0720", 7 * 60 + 20, 10),  # the draw starts 10 min before the charge
    ("draw-0735", 7 * 60 + 35, 10),  # the draw starts during the charge
    ("draw-0745", 7 * 60 + 45, 10),  # 5 min after the last heated sample
    ("draw-0800", 8 * 60, 10),  # past the settle window (control)
    ("long-0700", 7 * 60, 40),  # a 40-min charge: the dip recovers while heated
    ("long-0745", 7 * 60 + 45, 40),  # a draw during the long charge
)


ARMS = (
    ("dip", None), ("truth", None), ("flat", None),
    ("dip@max", DHW_COOLING_RATE_MAX), ("truth@max", DHW_COOLING_RATE_MAX),
)


if __name__ == "__main__":
    import sys

    steps = [int(a) for a in sys.argv[1:]] or list(CADENCES_MIN)
    for step in steps:
        for geo, draw_min, charge_min in GEOMETRIES:
            for arm, rate in ARMS:
                print(f"{step:3d}min {geo} {arm:9s} {run(arm, rate, draw_min, charge_min, step)}")
