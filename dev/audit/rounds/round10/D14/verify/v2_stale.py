# V2: from fixture rows alone, cycles (every 30 min over window) where age since last CHANGE > limit
import json,sys
from datetime import datetime,timedelta
d=json.load(open('tests/replay/synthetic-dhw-only.json'))
w0=datetime.fromisoformat(d['window']['start']);w1=datetime.fromisoformat(d['window']['end'])
for ent,lim in [('sensor.heat_pump_power',30),('select.heat_pump_operating_mode',60),('sensor.outdoor_temperature',180)]:
  rows=d['states'][ent]; ch=[];last=None
  for r in rows:
    if r[1]!=last: ch.append(datetime.fromisoformat(r[0])); last=r[1]
  n=0;tot=0;t=w0
  while t<w1:
    prev=[c for c in ch if c<=t]
    if prev and (t-prev[-1])>timedelta(minutes=lim): n+=1
    tot+=1; t+=timedelta(minutes=30)
  print(ent,'changes',len(ch),'stale_cycles',n,'of',tot, 'perturb(lim*100):', sum(1 for _ in []))
