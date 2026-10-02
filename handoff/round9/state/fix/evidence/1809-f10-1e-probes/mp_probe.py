import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
sys.path.insert(0,"tests")
from homeassistant.util import dt as dt_util
from heatpump_optimizer.manual_plan import ManualOverride, build_override, ManualPlanError
S=ZoneInfo("Europe/Stockholm")
now=datetime(2026,10,24,6,30,tzinfo=S)
exp=datetime(2026,10,25,2,15,tzinfo=S,fold=1)
dt_util.freeze(now)
o=build_override(dhw_slots=[],space_slots=[],expires_at=exp,now=now)
print("expires true h:",(o.expires_at.timestamp()-now.timestamp())/3600)
slot=[{"start":"2026-10-25T02:15:00+01:00","end":"2026-10-25T03:00:00+01:00"}]
try:
    build_override(dhw_slots=slot,space_slots=[],expires_at=now+timedelta(hours=10),now=now); print("slot accepted")
except ManualPlanError as e: print("slot refused",e)
slot=[{"start":exp.isoformat(),"end":(exp+timedelta(hours=1)).isoformat()}]
import heatpump_optimizer.manual_plan as m
print(m.parse_channel(slot,now))
e1=datetime(2026,10,25,2,30,tzinfo=S,fold=1)
mo=ManualOverride(space_slots=[],dhw_slots=[],expires_at=e1,created_at=now)
print("expired at 02:45 CEST (want False):",mo.is_expired(datetime(2026,10,25,2,45,tzinfo=S)))
