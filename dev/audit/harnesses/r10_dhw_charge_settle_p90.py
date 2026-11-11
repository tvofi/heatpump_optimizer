"""R10-OUTSIDE-DHW-CHARGE-SETTLE: the heavy-day p90 a charge-start dip adds.

Drives one ``DhwProfileLearner`` per arm through 28 simulated days at a
5-minute sample cadence and prints, per draw window, the folded occurrence
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
    dev/audit/harnesses/r10_dhw_charge_settle_p90.py

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


def dip_at(minutes_since_start: float) -> float:
    """The reading's offset below the true tank temperature after a charge start."""
    if minutes_since_start < 0:
        return 0.0
    if minutes_since_start <= DIP_PEAK_MIN:
        return DIP_K * minutes_since_start / DIP_PEAK_MIN
    return max(0.0, DIP_K * (1.0 - (minutes_since_start - DIP_PEAK_MIN) / 20.0))


def run(arm: str, rate: float | None = None) -> dict:
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
    charge_start: datetime | None = None
    loop = asyncio.new_event_loop()
    for i in range(DAYS * 24 * 60 // STEP_MIN):
        now = clock[0] = datetime(2026, 11, 2) + timedelta(minutes=i * STEP_MIN)
        day, minute = divmod(i * STEP_MIN, 24 * 60)
        dt_h = STEP_MIN / 60.0
        t_true -= true_rate * (t_true - TANK_ROOM_AMBIENT_TEMP) / 25.0 * dt_h
        if 7 * 60 <= minute < 7 * 60 + 15:  # the morning draw, three samples
            t_true -= draws_kwh[day] / 3.0 / cap
        flagged = arm != "flat"  # flat: an unflagged reheat, no dip
        if minute == 7 * 60 + 30:
            charge_start = now
        in_charge = charge_start is not None and 0 <= (now - charge_start).total_seconds() < 600
        heating[0] = flagged and in_charge
        if in_charge:
            t_true += (SETPOINT_C - t_true) / 2.0
        reading = t_true
        if arm.startswith("dip") and charge_start is not None:
            reading -= dip_at((now - charge_start).total_seconds() / 60.0)
        loop.run_until_complete(learner.async_learn_dynamics(round(reading, 2)))
    loop.close()
    stats = learner.draw_stats
    out = {"usage_points": usage_points[0]}
    for label in labels_for(params.dhw_demand_windows):
        q = stats.quantile(label, 0.9)
        out[label] = (stats.count(label), None if q is None else round(q, 4))
    return out


if __name__ == "__main__":
    for arm, rate in (("dip", None), ("truth", None), ("flat", None), ("dip@max", DHW_COOLING_RATE_MAX), ("truth@max", DHW_COOLING_RATE_MAX)):
        print(f"{arm:8s} {run(arm, rate)}")
