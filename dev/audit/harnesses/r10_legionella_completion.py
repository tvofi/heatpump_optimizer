#!/usr/bin/env python3
"""R10-LEGIONELLA-COMPLETION (D15 lead L8): does an overdue cycle complete, and is it loud?

WHY IT EXISTS. The owner's diagnostics export (2026-10-25) showed the last
completed anti-legionella cycle about 66 days old against a 7-day interval,
and the last attempt, 4 days before the export, peaking below the configured
temperature. This closed loop is the instrument for that, so a later seat can
re-take it at its own merge base.

The loop: a 300 L tank on the golden house (``tests/golden.py``'s ``make``),
the real ``HeatPumpOptimizer`` re-solved every 30 min from the real tank's
reading and the guard's ``hours_since``, and the real ``LegionellaGuard`` fed
every 15 min with the plan's current ``dhw_reason`` and the real tank. The
"real" tank follows the plan's own per-step temperature change, clipped to
the pump's physical ceiling, which the model does not know: that is the
owner's case, where the plan believes the target reachable and the pump stops
short. The last completed cycle starts 66 days old; the interval is 7 days.

Arms (``CEILINGS``), each over ``DAYS`` simulated days:
  reach      the pump reaches 65 °C: the null control, a cycle completes.
  short      the pump tops out at 57 °C, below 60 - 1.
  marginal   the pump tops out at 59.3 °C with free disinfection on, whose
             credit needs 59.5 °C held for ``DHW_LEGIONELLA_HOLD_MINUTES``.
  blind      ``short`` with the tank probe configured but never reporting.

Per arm it prints: commanded steps, completions, attempts and the gap between
consecutive attempts, the largest ``hours_since`` the planner was handed,
the age of the last completion at the end, and every repair notice raised
(``hass.issues``), with the overdue notice's placeholders when one stands.

    PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_legionella_completion.py [arm ...] [--days N]
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import timedelta, timezone

sys.path[:0] = ["tests", "custom_components"]

import numpy as np  # noqa: E402

from golden import START, make  # noqa: E402
from harness import FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from profiles import solve_inputs  # noqa: E402

from heatpump_optimizer.disinfection import DisinfectionSwitch  # noqa: E402
from heatpump_optimizer.legionella import LegionellaGuard  # noqa: E402
from heatpump_optimizer.payload import REASON_LEGIONELLA  # noqa: E402

#: arm -> (pump ceiling °C, free disinfection, probe reports)
CEILINGS = {
    "reach": (65.0, False, True),
    "short": (57.0, False, True),
    "marginal": (59.3, True, True),
    "blind": (57.0, False, False),
}
STEP = timedelta(minutes=15)
SOLVE_EVERY = 2  # steps: the 30 min default optimization interval


def run(arm: str, days: int) -> dict:
    ceiling, free, reports = CEILINGS[arm]
    built = make(config_overrides={"dhw_setpoint": 52.0})
    opt = built["optimizer"]
    params = opt.model.params
    params.dhw_legionella_interval_days = 7.0
    config = {
        "dhw_temp_entity": "sensor.tank",
        "dhw_free_disinfection_enabled": free,
    }
    hass = FakeHass()
    action: dict = {"dhw_reason": "idle"}
    guard = LegionellaGuard(
        hass, f"r10-leg-{arm}", params, config,
        action=lambda: action,
        disinfect=DisinfectionSwitch({}, lambda *a, **k: None, lambda e: None),
        dhw_blocked=lambda: False,
    )

    async def _no_save() -> None:
        return None

    guard.async_save = _no_save
    t0 = START.replace(tzinfo=timezone.utc)
    guard.last_cycle = t0 - timedelta(days=66)
    tank = 48.0
    n_steps = len(built["prices"])
    reasons: list = []
    traj = np.zeros(1)
    commanded = completions = 0
    attempts: list = []
    max_since = 0.0
    raised: set[str] = set()
    last_attempt = None
    steps = days * 96
    for i in range(steps):
        now = t0 + i * STEP
        dt_util.freeze(now)
        if i % SOLVE_EVERY == 0:
            state = built["state"]
            state.dhw_temperature = tank
            since = guard.hours_since()
            state.dhw_hours_since_legionella = since
            max_since = max(max_since, since or 0.0)
            shift = i % n_steps
            res = opt.optimize(inputs=solve_inputs(
                initial_state=state,
                prices=np.roll(built["prices"], -shift),
                outdoor_temps=np.roll(built["outdoor"], -shift),
                wind_speeds=np.roll(built["wind"], -shift),
                precipitation=np.roll(built["rain"], -shift),
                solar_radiation=np.roll(built["solar"], -shift),
                start_time=(START + i * STEP),
            ))
            reasons = list(res.dhw_reasons or [])
            traj = np.asarray(res.dhw_temp_trajectory, dtype=float)
        k = i % SOLVE_EVERY
        action["dhw_reason"] = reasons[k] if k < len(reasons) else "idle"
        if action["dhw_reason"] == REASON_LEGIONELLA:
            commanded += 1
        before = guard.last_cycle
        asyncio.run(guard.async_observe(tank if reports else None, None))
        if guard.last_cycle != before:
            completions += 1
        if guard.attempt is not None and guard.attempt != last_attempt:
            attempts.append((now - t0).total_seconds() / 3600.0)
            last_attempt = guard.attempt
        raised |= {iss[1] for iss in getattr(hass, "issues", [])}
        delta = float(traj[k + 1] - traj[k]) if k + 1 < traj.size else 0.0
        tank = min(ceiling, tank + delta) if delta > 0 else tank + delta
    dt_util.freeze(t0 + steps * STEP)
    end = dt_util.now()
    standing = {iss[1]: iss[2].get("translation_placeholders")
                for iss in getattr(hass, "issues", [])}
    due_end = guard.due_in_hours()
    dt_util.freeze(None)
    gaps = [round(b - a, 1) for a, b in zip(attempts, attempts[1:])]
    return {
        "commanded_steps": commanded,
        "completions": completions,
        "attempt_hours": [round(a, 1) for a in attempts],
        "attempt_gaps_h": gaps,
        "max_hours_since_planned": round(max_since, 1),
        "completion_age_days_end": round(
            (end - guard.last_cycle).total_seconds() / 86400.0, 1
        ),
        "due_in_hours_end": due_end,
        "notices_ever": sorted(raised),
        "notices_standing": standing,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("arms", nargs="*", default=list(CEILINGS))
    ap.add_argument("--days", type=int, default=21)
    a = ap.parse_args()
    for arm in a.arms:
        out = run(arm, a.days)
        for key, value in out.items():
            print(f"RESULT {arm} {key} {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
