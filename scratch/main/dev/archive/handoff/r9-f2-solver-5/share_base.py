"""Share of one solve's CPU spent in named per-row batch twins (wrapper timing, process_time).
PYTHONPATH=tests/hastub python share.py '<spec json>'
Perturbation: pass --double NAME to run that function twice per call; its share must ~double."""
import os, sys, time, json, functools
for k in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"): os.environ.setdefault(k,"1")
sys.path[:0]=["tests","custom_components"]
from heatpump_optimizer import optimizer as O, tariff as T
from heatpump_optimizer.thermal_model import ThermalModel as TM
spec=json.loads(sys.argv[1]); double = sys.argv[3] if len(sys.argv)>3 and sys.argv[2]=="--double" else None
acc={}
def wrap(owner, name, label):
    orig=getattr(owner,name)
    @functools.wraps(orig)
    def w(*a,**k):
        t=time.process_time(); r=orig(*a,**k)
        if label==double: r=orig(*a,**k)
        acc[label]=acc.get(label,0.0)+time.process_time()-t; return r
    setattr(owner,name,w)
wrap(O.HeatPumpOptimizer,"_comfort_terms_batch","comfort_terms_batch")
wrap(O,"cycling_penalty_batch","cycling_penalty_batch")
wrap(O,"peak_cost_batch","peak_cost_batch")
wrap(O,"_terminal_row_cost","terminal_row_cost_build")
wrap(TM,"simulate_trajectory_batch","simulate_trajectory_batch")
wrap(TM,"simulate_step","simulate_step")
wrap(TM,"simulate_dhw_step","simulate_dhw_step")
import stress
stress.build_case(**{**spec,"hours":6})
acc.clear()
t=time.process_time(); run=stress.build_case(**spec); tot=time.process_time()-t
print(json.dumps({"spec":spec,"double":double,"solve_cpu_s":round(tot,3),"objective":float(run["result"].objective_value),
 "shares":{k:round(v/tot,4) for k,v in sorted(acc.items())}}))
