#!/usr/bin/env python3
"""Failing probes for three more sweep-confirmed instances of the class
"persisted future instant trusted without bound", beyond D1-s1-04 and
D1-s3-05 and beyond probe_fuse_advisor.py's coordinator.py:8007/8024.

Each guard expression below is copied verbatim from the cited production
line. All three share the mechanism: a `datetime.fromisoformat` restore
from a persistent store, then a bare `(now - restored).total_seconds()`
comparison with no check that `restored` is not implausibly ahead of the
moment it was read back.

Run: python3 tools/audit/round9/D14/sweep/persisted_future_instant_unbounded/probe_more_instances.py
"""
import sys
from datetime import datetime, timedelta, timezone

NOW0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
CLOCK_AHEAD = NOW0 + timedelta(days=400)  # a bogus future write
LATER = NOW0 + timedelta(days=30)         # real time, 30 days on


def clamp_at_restore(restored, restore_time_now):
    if restored is not None and restored > restore_time_now:
        return restore_time_now
    return restored


# --- coordinator.py:2953/6306 -- heavy-snow damping never re-arms ----------
def snow_damping_active(last_heavy_snow, now, window_hours=48.0) -> bool:
    """Verbatim from coordinator.py:6306: `(now - self._last_heavy_snow)
    .total_seconds() < window_hours * 3600`."""
    if last_heavy_snow is None:
        return False
    return (now - last_heavy_snow).total_seconds() < window_hours * 3600.0


def check_snow_damping():
    null_ok = not snow_damping_active(NOW0, NOW0 + timedelta(hours=49))
    positive = snow_damping_active(CLOCK_AHEAD, LATER)
    fixed = snow_damping_active(clamp_at_restore(CLOCK_AHEAD, NOW0), LATER)
    print(f"RESULT snow_damping null_control_cleared={null_ok} "
          f"positive_control_stuck_at_day30={positive} perturbation_clamped={fixed}")
    assert null_ok
    assert positive is True
    assert fixed is False


# --- coordinator.py:7343/8108 -- outage recovery window never opens -------
def outage_gap_minutes(last_tick, now) -> float:
    """Verbatim shape from coordinator.py:8105-8114 (`_detect_outage`)."""
    return (now - last_tick).total_seconds() / 60.0


def outage_missed(last_tick, now, outage_gap_minutes_threshold=10.0) -> bool:
    """True means the real gap that occurred is masked (recovery window
    does not open) because the restored `last_tick` sits ahead of `now`."""
    gap = outage_gap_minutes(last_tick, now)
    return gap <= outage_gap_minutes_threshold


def check_outage_detection():
    # Null control: an honest last_tick correctly flags a real 6-hour gap.
    honest_last_tick = NOW0
    real_gap_flagged = not outage_missed(honest_last_tick, NOW0 + timedelta(hours=6))
    # Positive control: last_tick was persisted while the clock ran ahead;
    # a real 6-hour outage at restart is masked because now - last_tick < 0.
    masked = outage_missed(CLOCK_AHEAD, NOW0 + timedelta(hours=6))
    fixed = not outage_missed(clamp_at_restore(CLOCK_AHEAD, NOW0), NOW0 + timedelta(hours=6))
    print(f"RESULT outage_detection null_control_flagged={real_gap_flagged} "
          f"positive_control_masked={masked} perturbation_clamped_flagged={fixed}")
    assert real_gap_flagged
    assert masked is True
    assert fixed is True


# --- pump_arbiter.py:629/405-407 -- echo grace never expires --------------
ECHO_GRACE_S = 120.0


def in_echo_grace(written_at, now) -> bool:
    """Verbatim from pump_arbiter.py:406: `(now - at).total_seconds() <
    ECHO_GRACE_S`. While true, `hold()` skips comparing the observed
    setpoint to what the optimizer wrote, so a real mismatch (the pump
    ignored the write) goes unflagged."""
    return (now - written_at).total_seconds() < ECHO_GRACE_S


def check_echo_grace():
    null_ok = not in_echo_grace(NOW0, NOW0 + timedelta(seconds=121))
    stuck = in_echo_grace(CLOCK_AHEAD, LATER)
    fixed = not in_echo_grace(clamp_at_restore(CLOCK_AHEAD, NOW0), LATER)
    print(f"RESULT echo_grace null_control_cleared={null_ok} "
          f"positive_control_stuck_at_day30={stuck} perturbation_clamped={fixed}")
    assert null_ok
    assert stuck is True
    assert fixed is True


def main() -> int:
    check_snow_damping()
    check_outage_detection()
    check_echo_grace()
    print("PROBE OK: coordinator.py:2953/6306, coordinator.py:7343/8108, "
          "pump_arbiter.py:629/405-407 are instances of the class")
    return 0


if __name__ == "__main__":
    sys.exit(main())
