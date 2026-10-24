import sys,time,inspect
sys.path[:0]=['tests/hastub','.']
import custom_components.heatpump_optimizer.away as A
from custom_components.heatpump_optimizer.thermal_model import ThermalModel,ThermalParameters,ThermalState
m=ThermalModel(ThermalParameters())
sig=inspect.signature(ThermalState); st=ThermalState(**{k:(18.0 if 'temp' in k else 0.0) for k,p in sig.parameters.items() if p.default is inspect._empty})
n=[0]; orig=m.simulate_step
def cnt(*a,**k): n[0]+=1; return orig(*a,**k)
m.simulate_step=cnt
for tgt in (18.0,20.0,40.0):
  n[0]=0; t=time.perf_counter(); h=A.estimate_recovery_hours(m,st,tgt,-5.0); dt=time.perf_counter()-t
  print(f'target={tgt} hours={h} calls={n[0]} wall_ms={dt*1e3:.2f}')
