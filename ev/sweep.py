"""Reviewer's own sweep (not the finder's, not the fixer's): drive the
production ledger through store histories and print the open-month factor."""
from datetime import datetime, timedelta
import math
from heatpump_optimizer.ledger import MonthlyLedger, pro_rata_factor, month_hours

def run(name, now, start, end, step_h=0.25, legacy_until=None, unpriced=lambda t: False, gap=lambda t: False):
    L = MonthlyLedger(); t = start
    while t < end:
        if not gap(t):
            spot = float('nan') if unpriced(t) else 1.0
            if legacy_until and t < legacy_until:
                L.observe_meta_mean(t, "spot_price", spot)
                L.add_savings_settlement(t, baseline_kw=0.75, actual_kwh=step_h, spot=spot, dt=step_h)
            else:
                L.observe_spot_and_settle_savings(t, spot, {"baseline_kw": 0.75}, step_h, step_h)
            L.add(t, "spot", kwh=step_h, sek=step_h)
        t += timedelta(hours=step_h)
    f = L._coverage_factor(now)
    rows = L.savings_months(now); r = rows[-1] if rows else {}
    print(f"{name:34s} factor={f:9.3f} pro_rata={pro_rata_factor(now):7.3f} hours_scale={month_hours(now)/max(1e-9,(L.as_dict()['months'].get(now.strftime('%Y-%m'),{}).get('meta',{}).get('settled_hours',{}).get('sum',0) or 1e-9)):9.3f} savings_sek={r.get('savings_sek')} pct={r.get('savings_pct')}")

now = datetime(2026, 2, 10, 15, 0)
run("full-coverage-from-1st", now, datetime(2026,2,1), now)
run("fresh-install-mid-month(v7.0.1)", now, datetime(2026,2,9,12), now)
run("upgrade-mid-month", now, datetime(2026,2,1), now, legacy_until=datetime(2026,2,10,14,0))
run("upgrade-1st-settlement-of-month", now, datetime(2026,2,1), now, legacy_until=datetime(2026,2,1))
run("gaps (every 3rd day down)", now, datetime(2026,2,1), now, gap=lambda t: t.day % 3 == 0)
run("unpriced 30% of intervals", now, datetime(2026,2,1), now, unpriced=lambda t: t.hour < 7)
run("upgrade, legacy all unpriced", now, datetime(2026,2,1), now, legacy_until=datetime(2026,2,10,14,0), unpriced=lambda t: t < datetime(2026,2,10,14,0))
nm = datetime(2026, 3, 31, 12, 0)
run("DST March full", nm, datetime(2026,3,1), nm)
run("DST March upgrade 30th", nm, datetime(2026,3,1), nm, legacy_until=datetime(2026,3,30))
no = datetime(2026, 10, 26, 12, 0)
run("DST October full", no, datetime(2026,10,1), no)
run("DST October upgrade 19th", no, datetime(2026,10,1), no, legacy_until=datetime(2026,10,19,22))
