"""Class search: isolated CPU of per-step helpers at their measured per-solve call counts
(winter/tariff: effective_heat_loss_coefficient 298272, _stability_substeps 74496,
mixing_valve.is_throttling 112711, ThermalParameters.lower_floor_heat_loss_learned 149090).
Share = isolated CPU of N calls / the same solve's CPU measured in the same process."""
import os, sys, time, json
for k in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"): os.environ.setdefault(k,"1")
sys.path[:0]=["tests","custom_components"]
import stress
from heatpump_optimizer import optimizer as O, mixing_valve
from heatpump_optimizer.thermal_model import ThermalModel
cap={}
real=O.HeatPumpOptimizer.optimize
def grab(self,*a,**k):
    cap["m"]=self.model; return real(self,*a,**k)
O.HeatPumpOptimizer.optimize=grab
spec={c["label"]:c for c in stress.sweep_combinations()}["winter/tariff"]; spec={k:v for k,v in spec.items() if k!="label"}
t=time.process_time(); stress.build_case(**spec); solve=time.process_time()-t
m=cap["m"]; p=m.params
def bench(n, fn):
    t=time.process_time()
    for _ in range(n): fn()
    return time.process_time()-t
out={"solve_cpu_s":round(solve,3)}
out["effective_heat_loss_coefficient"]=bench(298272, lambda: m.effective_heat_loss_coefficient(0.25, 3.0, 0.0))
out["_stability_substeps"]=bench(74496, lambda: m._stability_substeps(3.0, 0.0, 0.25))
out["is_throttling"]=bench(112711, lambda: mixing_valve.is_throttling(p.mixing_valve_mode))
out["lower_floor_heat_loss_learned"]=bench(149090, lambda: p.lower_floor_heat_loss_learned)
print(json.dumps({k:(round(v,3) if k=="solve_cpu_s" else {"cpu_s":round(v,3),"share":round(v/solve,4)}) for k,v in out.items()}))
