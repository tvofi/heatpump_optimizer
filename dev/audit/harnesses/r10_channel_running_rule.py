"""R10-ARCH-SHAPES census: every reader of a channel's heating state against the plan's running rule.

D8-s1-01 (``dev/audit/rounds/round10/D8/s1/REPORT.md``): a plan step the plan's
own on schedule calls off (``thermal_model.planned_draws_run``: space plus DHW
not above ``MIN_RUNNING_DRAW_KW``) was still counted as a channel heating, by
any reader comparing that channel's own draw against 0.05 kW. The finder's
``f1_active_now.py`` reads the slot arm only where the solve happens to emit
such a step, which is per machine/BLAS (5 on Linux, 0 on macOS arm64 at the
same tree), so this drives the readers directly with the same plan.

It hands every reader one synthetic plan whose steps straddle both lines and
counts, per reader, the steps (or periods) it calls heating on a step
``planned_draws_run`` calls off:

- ``plan_slots.plan_slots``, space and DHW (the
  published slot lists; ``slot_steps_declared_off``);
- ``optimizer.classify_space_steps`` / ``classify_dhw_steps`` (a non-idle
  reason on such a step; ``reason_steps_declared_off``);
- ``sensor.DHWScheduleSensor.native_value`` on a payload carrying only
  ``dhw_schedule`` (a period counted from a raw draw; ``sensor_periods_declared_off``).

    PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r10_channel_running_rule.py [--perturb]

``--perturb`` lifts every step the plan calls off to 0.2 kW, so every step the
readers see runs: every count must read 0 at any tree (the null control: the
counts are of the defect, not of the readers' existence). ``steps_running``
and ``steps_declared_off`` print the plan's own split for that check.
"""
from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta

import numpy as np

from heatpump_optimizer import optimizer, sensor
from heatpump_optimizer.plan_slots import plan_slots
from heatpump_optimizer.thermal_model import planned_draws_run

# Each pair is (space kW, DHW kW): over and under 0.05 on each channel, with a
# total over and under 0.1, so every combination of the two lines is present.
STEPS = [
    (2.0, 0.0), (0.07, 0.0), (0.0, 0.07), (0.07, 0.07), (0.04, 0.04),
    (0.06, 0.03), (0.0, 0.0), (0.09, 0.0), (0.04, 2.0), (0.0, 0.08),
]


class _Coord:
    def __init__(self, data):
        self.data = data


def main() -> None:
    space = np.array([s for s, _ in STEPS])
    dhw = np.array([d for _, d in STEPS])
    if "--perturb" in sys.argv:
        off = ~np.array(planned_draws_run(space, dhw))
        space = np.where(off, 0.2, space)
    runs = planned_draws_run(space, dhw)
    n = len(STEPS)
    off = [i for i in range(n) if not runs[i]]
    ts = [datetime(2026, 1, 15, tzinfo=UTC) + timedelta(minutes=15 * i) for i in range(n)]
    prices = [1.0] * n

    slot_hits = 0
    for mine, other in ((space, dhw), (dhw, space)):
        for slot in plan_slots(
            ts, list(mine), prices, 0.25, other_powers=list(other)
        ):
            slot_hits += sum(
                1 for i in off
                if slot["start"] <= ts[i].isoformat() < slot["end"]
            )

    room = np.full(n + 1, 21.0)
    floor = np.full(n, 19.0)
    sp_reasons = optimizer.classify_space_steps(
        space, np.array(prices), room, floor, np.ones(n), None, n, other=dhw,
    )
    dhw_reasons = optimizer.classify_dhw_steps(
        dhw, np.zeros(n, dtype=bool), np.zeros(n), None, n,
        idle=optimizer.IdleContext(other=space),
    )
    idle_codes = {
        optimizer.REASON_IDLE, optimizer.REASON_IDLE_COASTING,
        optimizer.REASON_IDLE_DEARER, optimizer.REASON_IDLE_SOLAR,
        optimizer.REASON_IDLE_FUSE, optimizer.REASON_IDLE_OTHER,
    }
    reason_hits = sum(
        1 for i in off for codes in (sp_reasons, dhw_reasons)
        if codes[i] not in idle_codes
    )

    # A schedule of only the off steps: any period counted is a counted off step.
    sched = [{"dhw_power": float(dhw[i])} for i in off]
    sens = sensor.DHWScheduleSensor.__new__(sensor.DHWScheduleSensor)
    sens.coordinator = _Coord({"dhw_schedule": sched})
    value = sens.native_value if sched else None
    sensor_hits = int(str(value).split()[0]) if value and value[0].isdigit() else 0

    print(f"RESULT steps={n} steps_running={n - len(off)} steps_declared_off={len(off)}")
    print(f"RESULT slot_steps_declared_off={slot_hits}")
    print(f"RESULT reason_steps_declared_off={reason_hits}")
    print(f"RESULT sensor_periods_declared_off={sensor_hits} sensor_state={value!r}")
    print(f"RESULT perturbed={int('--perturb' in sys.argv)}")


if __name__ == "__main__":
    main()
