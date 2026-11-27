from datetime import datetime
from zoneinfo import ZoneInfo
from heatpump_optimizer.dhw_schedule import hours_until_next_window as h
from heatpump_optimizer.pump_schedule import vvc_should_run as v
z=ZoneInfo("Europe/Stockholm")
for f in (0,1):
    n=datetime(2026,10,25,2,30,tzinfo=z).replace(fold=f)
    print(f"fold={f} now={n.isoformat()} 02:45-03:30 -> {h(n,[(2.75,3.5)])} {v(n,[(2.75,3.5)],30.0)}")
# other zones: Sydney autumn 2026-04-05 03:00->02:00; Lord_Howe 02:00->01:30
for zn,d,hh,mm,win in (("Australia/Sydney",(2026,4,5),2,30,(2.75,3.5)),("Australia/Lord_Howe",(2026,4,5),1,40,(1.75,2.5))):
    z=ZoneInfo(zn)
    for f in (0,1):
        n=datetime(*d,hh,mm,tzinfo=z).replace(fold=f)
        print(f"{zn} fold={f} now={n.isoformat()} {win} -> {h(n,[win])} {v(n,[win],30.0)[0]}")
# naive now, None tz
print("naive", h(datetime(2026,10,25,0,30),[(2.75,3.5)]))
