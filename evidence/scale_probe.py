"""Reviewer's own probe (not the finder's, not the fixer's): MonthlyLedger.savings_months
scale/floor behaviour on the three terms. Run with cwd = a worktree, PYTHONPATH as the suite.

Books N intervals into one closed month, with a plan line (planned_kw) so the month is
calibrated, and reads the row. Prints RESULT lines.
"""
import inspect
import sys
from datetime import datetime, timezone

from heatpump_optimizer import ledger as L

ARGS = inspect.signature(L.MonthlyLedger.add_savings_settlement).parameters
HAS_STORED = "stored_kw_th" in ARGS
HAS_WOOD = "wood_configured" in inspect.signature(L.MonthlyLedger.savings_months).parameters


def row(cal, *, wood, stored=0.0, comfort=0.0, cop=3.0, prices=None, n=48, base_kw=2.0, plan_kw=2.0):
    """One closed month (2026-03), read in 2026-05. cal = metered over planned."""
    led = L.MonthlyLedger()
    prices = prices or [1.0] * n
    for i in range(n):
        when = datetime(2026, 3, 1 + i // 24, i % 24, tzinfo=timezone.utc)
        kw = dict(baseline_kw=base_kw, actual_kwh=plan_kw * cal * 1.0, spot=prices[i], dt=1.0,
                  planned_kw=plan_kw)
        if HAS_STORED:
            kw.update(stored_kw_th=stored, comfort_kw=comfort, steady_cop=cop)
        led.add_savings_settlement(when, **kw)
    kwargs = {"wood_configured": wood} if HAS_WOOD else {}
    rows = led.savings_months(datetime(2026, 5, 1, tzinfo=timezone.utc), **kwargs)
    return rows[0]


def fmt(r):
    keys = ("baseline_sek", "actual_sek", "savings_sek", "savings_pct", "meter_calibration",
            "stored_heat_sek", "comfort_sek", "old_basis")
    return " ".join(f"{k}={r.get(k)!r}" for k in keys)


def main():
    print(f"RESULT api has_stored={HAS_STORED} has_wood={HAS_WOOD}")
    # 1. Null control: flat price, calibration 1, no stored/comfort -> same before and after.
    print("RESULT null_flat", fmt(row(1.0, wood=False)))
    print("RESULT null_flat_wood", fmt(row(1.0, wood=True)))
    # 2. Floor boundary, wood configured and not: just below / at / above 1.0, zero, tiny.
    for cal in (0.0, 1e-9, 0.5, 0.999, 1.0, 1.001, 1.5):
        for wood in (False, True):
            r = row(cal, wood=wood, stored=0.6, comfort=0.3)
            print(f"RESULT floor cal={cal} wood={wood}", fmt(r))
    # 3. Each term's sign and units at cal 1: stored +/-; comfort +; cop scaling.
    for stored in (-0.6, 0.0, 0.6):
        print(f"RESULT stored={stored}", fmt(row(1.0, wood=False, stored=stored, cop=3.0)))
    for cop in (1.5, 3.0, 6.0):
        print(f"RESULT cop={cop}", fmt(row(1.0, wood=False, stored=0.6, cop=cop)))
    # 4. Varying price: stored priced at the month's metered kWh price (actual sek/kwh).
    prices = [0.5 if i % 2 else 1.5 for i in range(48)]
    print("RESULT vary", fmt(row(1.0, wood=False, stored=0.6, comfort=0.3, prices=prices)))
    print("RESULT vary_cal0.5_wood", fmt(row(0.5, wood=True, stored=0.6, comfort=0.3, prices=prices)))
    print("RESULT vary_cal0.5_nowood", fmt(row(0.5, wood=False, stored=0.6, comfort=0.3, prices=prices)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
