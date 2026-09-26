"""Overhead and determinism of meter.production_calls on named sweep scenarios."""
import os, sys, time, json
for k in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"): os.environ.setdefault(k,"1")
sys.path[:0]=["tests","custom_components", os.path.dirname(os.path.abspath(__file__))]
import stress, meter
from heatpump_optimizer import optimizer as O
PKG=os.path.dirname(O.__file__)
combos={c["label"]:{k:v for k,v in c.items() if k!="label"} for c in stress.sweep_combinations()}
for label in sys.argv[1:]:
    spec=combos[label]
    t=time.process_time(); r=stress.build_case(**spec); p1=time.process_time()-t
    t=time.process_time(); r2,c1=meter.production_calls(lambda: stress.build_case(**spec), PKG); m1=time.process_time()-t
    t=time.process_time(); r3,c2=meter.production_calls(lambda: stress.build_case(**spec), PKG); m2=time.process_time()-t
    t=time.process_time(); r=stress.build_case(**spec); p2=time.process_time()-t
    print(json.dumps({"label":label,"plain_s":[round(p1,3),round(p2,3)],"metered_s":[round(m1,3),round(m2,3)],
      "overhead_x":round(min(m1,m2)/min(p1,p2),3),"total":sum(c1.values()),"repeat_identical":c1==c2,"files":c1}))
