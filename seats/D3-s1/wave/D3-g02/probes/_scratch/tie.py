import numpy as np
from datetime import timedelta
def obs(p,e,s): return float(-np.log((e-20.0)/(p-20.0))/(s/3600.0)*25.0)
rs=np.random.default_rng(1).uniform(0.08,3.16,4000)
found=[]
for r in rs:
    r=float(r)
    if (1-0.25)*r+0.25*r == (1-0.02)*r+0.02*r: continue
    for i in range(20000):
        s=timedelta(seconds=3600,microseconds=i).total_seconds()
        g=20+30*float(np.exp(-r*(s/3600)/25)); lo=hi=g; ok=None
        for _ in range(3):
            for c in (lo,hi):
                if obs(50.0,c,s)==r: ok=(50.0,c,s)
            lo,hi=float(np.nextafter(lo,-np.inf)),float(np.nextafter(hi,np.inf))
        if ok: found.append((r,ok)); break
    if len(found)>=3: break
print(found)
