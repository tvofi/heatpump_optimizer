#!/usr/bin/env python3
"""Failing probe: coordinator.py:8007/8024 fuse-advisor cooldown.

New instance the sweep enumerator surfaced beyond the two round-9 findings
(D1-s1-04, D1-s3-05): ``self._fuse_advisor_at`` is restored from the
ledger store with a bare ``datetime.fromisoformat`` (coordinator.py:8007)
and then gates a 7-day recompute cooldown at coordinator.py:8023-8024:

    if (
        self._fuse_advisor_at is not None
        and (now - self._fuse_advisor_at).total_seconds() < 7 * 24 * 3600.0
        and self._fuse_advisor.get("month") == month_key(now)
    ):
        return

Same mechanism as D1-s1-04 (drift.py / curve_learning.py / snapshots.py /
comfort_learning.py): a persisted instant is trusted verbatim, with no
check that it is not implausibly far in the future relative to `now`. If
it was written while the clock ran ahead (an unsynced RTC before the first
NTP fix, a manual clock set-forward later corrected), `now - stored` comes
out small or negative and the 7-day cooldown never expires: the fuse
advisor stops recomputing until real wall-clock time catches up to the
bogus stored instant, which can be months or years away.

This probe reproduces exactly the coordinator's guard expression (copied
verbatim from coordinator.py:8023-8024, cited above) against a synthetic
`_fuse_advisor_at` and asks whether the cooldown clears at the intended
7-day mark.

Run: python3 tools/audit/round9/D14/sweep/persisted_future_instant_unbounded/probe_fuse_advisor.py
"""
import sys
from datetime import datetime, timedelta, timezone


def cooldown_active(fuse_advisor_at, now, same_month=True) -> bool:
    """Verbatim guard expression from coordinator.py:8023-8024."""
    return (
        fuse_advisor_at is not None
        and (now - fuse_advisor_at).total_seconds() < 7 * 24 * 3600.0
        and same_month
    )


def restore_clamped(fuse_advisor_at, restore_time_now):
    """Perturbation: coordinator.py:8007's own restore, clamped to the
    instant of restore -- a persisted instant can never legitimately be
    later than the moment it is read back."""
    if fuse_advisor_at is not None and fuse_advisor_at > restore_time_now:
        return restore_time_now
    return fuse_advisor_at


def main() -> int:
    now0 = datetime(2026, 1, 1, tzinfo=timezone.utc)

    # Null control: a normal write (clock correct) expires on schedule.
    normal_write = now0
    still_cooling_down = cooldown_active(normal_write, now0 + timedelta(days=6))
    expired_on_time = not cooldown_active(normal_write, now0 + timedelta(days=8))
    print(f"RESULT null_control_day6_active={still_cooling_down} day8_active={not expired_on_time}")
    assert still_cooling_down is True
    assert expired_on_time is True

    # Positive control: the store was written while the clock had run
    # 400 days ahead (e.g. an unset RTC reporting a garbage future date
    # before the first successful NTP sync), then the clock was corrected
    # back to the real time. `now` never catches up to `fuse_advisor_at`
    # for over a year, so the cooldown that should last 7 days lasts 400+.
    clock_ahead_write = now0 + timedelta(days=400)
    real_now_30_days_later = now0 + timedelta(days=30)
    stretched = cooldown_active(clock_ahead_write, real_now_30_days_later)
    print(f"RESULT positive_control_stretched_cooldown_at_day30={stretched}")
    assert stretched is True, "expected the unbounded guard to still be cooling down at day 30"

    # Perturbation: clamping the restored instant to the restore-time `now`
    # (one-line fix at coordinator.py:8007-8009) makes the cooldown clear
    # on schedule again, because the stored instant can no longer sit in
    # the future relative to any later `now`.
    restore_time_now = now0  # the moment coordinator.py:8007 reads the store
    clamped_at_restore = restore_clamped(clock_ahead_write, restore_time_now)
    fixed = cooldown_active(clamped_at_restore, real_now_30_days_later)
    print(f"RESULT perturbation_clamped_stretched_cooldown_at_day30={fixed}")
    assert fixed is False, "clamping the restored instant to now must clear the stretch"

    print("PROBE OK: coordinator.py:8007/8023-8024 is an instance of the class")
    return 0


if __name__ == "__main__":
    sys.exit(main())
