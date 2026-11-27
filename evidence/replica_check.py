import sys
from datetime import datetime
from zoneinfo import ZoneInfo as _p7_zone
from heatpump_optimizer.dhw_schedule import hours_until_next_window as _hunw
from heatpump_optimizer.pump_schedule import vvc_should_run as _p7_vvc
_p7_tz=_p7_zone("Europe/Stockholm")
_p7_days={"spring":datetime(2026,3,29,tzinfo=_p7_tz),"autumn":datetime(2026,10,25,tzinfo=_p7_tz),"plain":datetime(2026,6,10,tzinfo=_p7_tz)}
_p7_fold = {
    k: (_hunw(d.replace(hour=2, minute=30), [(2.75, 3.5)]),
        _hunw(d.replace(hour=2, minute=30, fold=1), [(2.75, 3.5)]),
        _hunw(d.replace(hour=2, minute=30), [(2.25, 2.4)]),
        _hunw(d.replace(hour=2, minute=30, fold=1), [(2.25, 2.4)]),
        _hunw(d.replace(hour=2, minute=30), [(1.5, 2.25)]))
    for k, d in _p7_days.items() if k != "spring"
}
_p7_gap = (_hunw(_p7_days["spring"].replace(minute=30), [(2.5, 4.0)]),
           _hunw(_p7_days["spring"].replace(minute=30), [(2.25, 2.4)]),
           _hunw(_p7_days["plain"].replace(minute=30), [(2.25, 2.4)]))
a = _p7_fold == {"autumn": (0.25, 0.25, 0.75, 23.75, 0.5),"plain": (0.25, 0.25, 23.75, 23.75, 23.0)} and _p7_gap == (1.5, 24.75, 1.75)
_p7_lead = {(k, f): _p7_vvc(d.replace(hour=2, minute=30, fold=f), [(2.75, 3.5)], 30.0)[0] for k, d in _p7_days.items() if k != "spring" for f in (0, 1)}
b = all(_p7_lead.values()) and len(_p7_lead) == 4
print(f"countdown-check={'PASS' if a else 'FAIL'} lead-check={'PASS' if b else 'FAIL'} :: {_p7_fold} gap {_p7_gap}")
sys.exit(0 if a and b else 1)
