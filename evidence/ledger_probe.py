"""Reviewer's own probe (not the finder's): old-basis rows, unclipped pct, calibration floor."""
import copy
from datetime import datetime, timezone
from heatpump_optimizer import ledger as L
def mk(month, base_kw, actual_kwh, plan_kw, n=40):
    led = L.MonthlyLedger()
    for i in range(n):
        led.add_savings_settlement(datetime(2026, month, 2, 0, tzinfo=timezone.utc), baseline_kw=base_kw,
            actual_kwh=actual_kwh, spot=1.0, dt=1.0, planned_kw=plan_kw)
    return led
# v1 document: three months booked before the stamp existed
v1 = L.MonthlyLedger()
for m, b in ((9, 3.0), (10, 1.0), (11, 0.2)):
    for i in range(40):
        v1.add(datetime(2026, m, 2, tzinfo=timezone.utc), "savings_baseline", kwh=b, sek=b)
        v1.add(datetime(2026, m, 2, tzinfo=timezone.utc), "savings_actual", kwh=1.1, sek=1.1)
doc = {"ledger": copy.deepcopy(v1.as_dict())}
before = copy.deepcopy(doc)
L.migrate_ledger_v1(doc)
led = L.MonthlyLedger.from_dict(doc["ledger"])
lines_same = all(before["ledger"]["months"][k]["lines"] == doc["ledger"]["months"][k]["lines"] for k in before["ledger"]["months"])
now = datetime(2026, 12, 20, tzinfo=timezone.utc)
for wood in (False, True):
    for r in led.savings_months(now, wood_configured=wood):
        print(f"RESULT old-basis wood={wood} {r['month']}: base {r['baseline_sek']} actual {r['actual_sek']} saving {r['savings_sek']} pct {r['savings_pct']} old {r['old_basis']}")
print("RESULT migration rewrites no line:", lines_same)
# November keeps booking after the upgrade: stays old
led.add_savings_settlement(datetime(2026, 11, 28, tzinfo=timezone.utc), baseline_kw=2.0, actual_kwh=1.0, spot=1.0, dt=1.0, planned_kw=1.0)
print("RESULT november after new booking old:", [r["old_basis"] for r in led.savings_months(now) if r["month"] == "2026-11"])
# December: new basis, a loss beyond -100 % is unclipped
led.add_savings_settlement(datetime(2026, 12, 3, tzinfo=timezone.utc), baseline_kw=1.0, actual_kwh=7.0, spot=1.0, dt=1.0)
r = [r for r in led.savings_months(datetime(2027, 1, 2, tzinfo=timezone.utc)) if r["month"] == "2026-12"][0]
print(f"RESULT december new basis: saving {r['savings_sek']} pct {r['savings_pct']} old {r['old_basis']}")
# calibration floor: metered/plan 1.0, 0.5, 0.25, and an under-reading model 1.5
for ratio in (1.0, 0.5, 0.25, 1.5):
    for wood in (False, True):
        led2 = mk(1, base_kw=2.0, actual_kwh=1.0 * ratio, plan_kw=1.0)
        r = led2.savings_months(datetime(2026, 2, 5, tzinfo=timezone.utc), wood_configured=wood)[0]
        print(f"RESULT calibration meter/plan {ratio} wood={wood}: pct {r['savings_pct']:.2f} calibration {r['meter_calibration']}")
