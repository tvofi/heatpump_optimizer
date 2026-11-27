# Seat-built oracle (reviewer's, not the finder's): first UTC minute after now at which the zone's wall clock
# goes from outside to inside the windows (hour_in_windows semantics, wrap included), tomorrow=None.
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from heatpump_optimizer.dhw_schedule import hours_until_next_window as h, hour_in_windows as hin
Z=("Europe/Stockholm","Australia/Sydney","Australia/Lord_Howe","America/Santiago")
def days(z,kind):
    out=[];d=datetime(2026,1,1)
    while d.year==2026:
        a=d.replace(tzinfo=z).utcoffset();b=(d+timedelta(days=1)).replace(tzinfo=z).utcoffset()
        if (b>a) if kind=="spring" else (b<a): out.append(d.replace(tzinfo=z))
        d+=timedelta(days=1)
    return out
cells=bad=0;shown=[]
for kind in ("spring","autumn"):
  for zn in Z:
    z=ZoneInfo(zn)
    for day in days(z,kind):
      t0=day.astimezone(timezone.utc)-timedelta(hours=3)
      clock=[t0+timedelta(minutes=m) for m in range(4*24*60)]
      walls=[t.astimezone(z) for t in clock]
      for s in range(0,1440,30):
        for w in (60,90,150):
          e=(s+w)%1440
          if e>=s: continue  # wrap windows only
          if e==0: continue
          win=[(s/60,24.0),(0.0,e/60)]
          ins=[hin(x.hour+x.minute/60,win) for x in walls]
          for i,t in enumerate(clock[:2*24*60]):
            x=walls[i]
            if x.date()!=day.date() or x.minute%15: continue
            now=walls[i]
            if ins[i]: want=0.0
            else:
              j=next((k for k in range(i+1,len(clock)) if ins[k] and not ins[k-1]),None)
              want=None if j is None else (clock[j]-t).total_seconds()/3600
            got=h(now,win); cells+=1
            if got is None or want is None or abs(got-want)>1e-9:
              bad+=1
              if len(shown)<6: shown.append(f"{zn} {kind} now={now.isoformat()} fold={now.fold} win={win}: got {got} want {want}")
print(f"wrap-oracle: {bad} of {cells} cells off");[print(" ",l) for l in shown]
