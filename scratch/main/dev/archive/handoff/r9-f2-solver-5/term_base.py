"""CPU share of the terminal cost's per-row batch closure (_terminal_cost_batch.<locals>.cost_batch),
wrapped at the closure the builder returns. Perturbation: --double runs it twice (share must rise)."""
import os, sys, time, json
for k in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"): os.environ.setdefault(k,"1")
sys.path[:0]=["tests","custom_components"]
from heatpump_optimizer import optimizer as O
acc=[0.0]; dbl="--double" in sys.argv
real=O.HeatPumpOptimizer.__dict__["_terminal_cost_batch"].__func__
def builder(*a,**k):
    f=real(*a,**k)
    def w(*x,**y):
        t=time.process_time(); r=f(*x,**y)
        if dbl: r=f(*x,**y)
        acc[0]+=time.process_time()-t; return r
    return w
O.HeatPumpOptimizer._terminal_cost_batch=staticmethod(builder)
import stress
spec={c["label"]:c for c in stress.sweep_combinations()}[sys.argv[1]]; spec={k:v for k,v in spec.items() if k!="label"}
t=time.process_time(); r=stress.build_case(**spec); s=time.process_time()-t
print(json.dumps({"label":sys.argv[1],"double":dbl,"solve_cpu_s":round(s,3),"terminal_batch_share":round(acc[0]/s,4)}))
