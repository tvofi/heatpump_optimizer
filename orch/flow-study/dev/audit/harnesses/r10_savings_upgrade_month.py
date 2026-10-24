#!/usr/bin/env python3
"""R10-SAVINGS-NEGATIVE: the open month's savings row across an upgrade mid-month.

WHY IT EXISTS. v7.0.1 (#2411) scales the open month by the month's hours over
the hours its coverage meta settled. A store written by v7.0.0 has no such
meta; the first v7.0.1 settlement starts one, minutes long, beside weeks of
lines. Every figure below is synthetic: a February with nine days booked the
v7.0.0 way (a spot sample and the savings lines, thermostat 0.75 kW against a
metered 1.0 kW), then one six-minute settlement through the production
``observe_spot_and_settle_savings``. The row is read at 10 February 15:00.

  upgrade  the upgraded month: the defect reads ``factor`` near 672 / 0.1,
           the fix reads the calendar-day ratio 28 / 10.
  null     the same negative booking with its coverage from the month's
           first settlement (24 hourly settlements on 9 February): the
           hours' scale 672 / 24 at both ends. A fix that reads it moved
           took the coverage away from a month that owns it.
  fresh    a month with no coverage meta at all: the calendar-day ratio at
           both ends.

    PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r10_savings_upgrade_month.py
"""
from datetime import datetime

from heatpump_optimizer.ledger import MonthlyLedger

NOW = datetime(2026, 2, 10, 15, 0)


def _legacy_days(ledger: MonthlyLedger, days: int, baseline_kw: float) -> None:
    """Hourly v7.0.0 bookings: a spot sample and the savings lines, no hours."""
    for h in range(days * 24):
        t = datetime(2026, 2, 1 + h // 24, h % 24, 0)
        ledger.observe_meta_mean(t, "spot_price", 1.0)
        ledger.add_savings_settlement(t, baseline_kw=baseline_kw, actual_kwh=1.0, spot=1.0, dt=1.0)
        ledger.add(t, "spot", kwh=1.0, sek=1.0)


def upgrade() -> MonthlyLedger:
    ledger = MonthlyLedger()
    _legacy_days(ledger, 9, 0.75)
    ledger.observe_spot_and_settle_savings(NOW, 1.0, {"baseline_kw": 0.75}, 0.1, 0.1)
    ledger.add(NOW, "spot", kwh=0.1, sek=0.1)
    return ledger


def null() -> MonthlyLedger:
    ledger = MonthlyLedger()
    for h in range(24):
        t = datetime(2026, 2, 9, h, 0)
        ledger.observe_spot_and_settle_savings(t, 1.0, {"baseline_kw": 0.75}, 1.0, 1.0)
        ledger.add(t, "spot", kwh=1.0, sek=1.0)
    return ledger


def fresh() -> MonthlyLedger:
    ledger = MonthlyLedger()
    _legacy_days(ledger, 9, 0.75)
    return ledger


def main() -> int:
    for name, build in (("upgrade", upgrade), ("null", null), ("fresh", fresh)):
        ledger = build()
        row = ledger.savings_months(NOW)[0]
        print(
            f"{name:8s} factor={ledger._coverage_factor(NOW):10.3f} "
            f"savings_sek={row['savings_sek']:12.2f} actual_sek={row['actual_sek']:12.2f} "
            f"savings_pct={row['savings_pct']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
