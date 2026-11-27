import sys
sys.path[:0] = [sys.argv[1] + "/tests/hastub", sys.argv[1] + "/custom_components"]
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from heatpump_optimizer.dhw_schedule import hours_until_next_window
from heatpump_optimizer import pump_schedule as ps
for zn, d, hh, mm in [("Europe/Stockholm", (2026,10,25), 2, 30), ("Australia/Sydney", (2026,4,5), 2, 30), ("America/New_York",(2026,11,1),1,30)]:
    z = ZoneInfo(zn)
    for win in [[(hh+0.25, hh+1.0)], [(hh+0.75, hh+1.25)], [(hh-0.5+24, 24.0),(0.0, hh-0.25)] if hh>1 else [(23.0,24.0),(0.0,1.0)]]:
        for fold in (0, 1):
            now = datetime(*d, hh, mm, tzinfo=z, fold=fold)
            r = hours_until_next_window(now, win)
            print(zn, now.isoformat(), win, "->", r)
