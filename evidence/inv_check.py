import sys, numpy as np, itertools
sys.path[:0]=["tests/hastub","custom_components","tests"]
from heatpump_optimizer.thermal_model import (ThermalParameters, heat_per_cop_kw as F,
    power_for_heat_per_cop_kw as I, partload_derate_limit)
worst=0.0; worst_cfg=None; n=0; nonexact_edges=[]
with np.errstate(all="raise"):
  for pmin,pmax in [(0.0,3.0),(1.5,5.0),(2.0,6.0),(0.5,12.0),(3.0,3.0),(1.0,1.2)]:
    lim=partload_derate_limit(pmin,pmax)
    for d in [0.0,1e-9,0.05,0.112,0.2,0.3,min(0.49,lim*0.999),lim*0.999999]:
      if d>=lim and pmax>pmin: continue
      p=ThermalParameters(min_electrical_power=pmin,max_electrical_power=pmax,cop_partload_derate=d)
      for hours in [1.0,0.25,24.0]:
        P=np.concatenate([np.linspace(0,pmax*1.6,4001),[pmin,pmax,np.nextafter(pmin,0),np.nextafter(pmax,99)]])
        Ph=P*hours
        # forward at hours: energy = hours * F(P)
        Eh=hours*F(p,P)
        back=I(p,Eh,hours=hours)
        err=float(np.max(np.abs(back-Ph)/np.maximum(Ph,1e-12)*(Ph>1e-9)))
        # also residual in heat space
        herr=float(np.max(np.abs(hours*F(p,back/hours)-Eh)))
        n+=1
        if herr>worst: worst=herr; worst_cfg=(pmin,pmax,d,hours,err)
        # scalar path agrees with array path
        for x in [0.0,pmin,pmax*(1-d) if d else pmax, 2.5, 50.0]:
          s=I(p,x*hours,hours=hours); a=I(p,np.array([x*hours]),hours=hours)[0]
          assert (s==a) or (np.isnan(s) and np.isnan(a)), (pmin,pmax,d,hours,x,s,a)
          assert isinstance(s,float) or s is x*hours
print(f"RESULT inverse round-trip: {n} configs, worst heat-space residual {worst:.3e} at {worst_cfg}")
# monotone & continuous
p=ThermalParameters(min_electrical_power=1.5,max_electrical_power=5.0,cop_partload_derate=0.2)
h=np.linspace(0,10,200001); P=I(p,h)
print("RESULT inverse monotone non-decreasing:",bool(np.all(np.diff(P)>=0)), "max jump", float(np.max(np.diff(P))))
# null control: zero derate returns same object / bit-identical float for each site expression
import random
rng=np.random.default_rng(1)
p0=ThermalParameters(min_electrical_power=1.5,max_electrical_power=5.0,cop_partload_derate=0.0)
bad=0
for _ in range(20000):
  heat=float(rng.uniform(0,40)); cop=float(rng.uniform(1,6)); dt=float(rng.choice([0.25,0.5,1.0]))
  q=heat/cop
  bad+= I(p0,q) is not q
  bad+= I(p0,q,hours=24.0) is not q
  E=rng.uniform(0,10,8); c=rng.uniform(1,6,8)
  bad+= not np.array_equal(I(p0,E/(c*dt)), E/(c*dt))
  bad+= not np.array_equal(c*F(p0,4.0)*dt, 4.0*c*dt) # LP ceiling: p_dhw_max*cop*dt reordered
print("RESULT null control zero-derate mismatches:",bad)
