"""Per-scenario work rows incl. production interpreter calls, for the tree in cwd.
PYTHONPATH=tests/hastub python rows.py LABEL [LABEL...]   (or ALL)"""
import os, sys, time, json, types
for k in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"): os.environ.setdefault(k,"1")
sys.path[:0]=["tests","custom_components"]
import stress
from heatpump_optimizer import optimizer as O
PKG=os.path.dirname(O.__file__)
def prod_codes():
    seen=set(); out=[]
    def walk(co):
        if id(co) in seen: return
        seen.add(id(co)); out.append(co)
        for c in co.co_consts:
            if isinstance(c, types.CodeType): walk(c)
    for mod in list(sys.modules.values()):
        if not (getattr(mod,"__file__",None) or "").startswith(PKG): continue
        for obj in list(vars(mod).values()):
            for cand in ([obj]+(list(vars(obj).values()) if isinstance(obj,type) else [])):
                fn=getattr(cand,"fget",cand); fn=getattr(fn,"__func__",fn); co=getattr(fn,"__code__",None)
                if co is not None and co.co_filename.startswith(PKG): walk(co)
    return out
M=sys.monitoring; TID=5; M.use_tool_id(TID,"rows"); n=[0]
import collections
perfile=collections.Counter()
def cb(code,*a):
    n[0]+=1; perfile[code.co_filename]+=1
M.register_callback(TID,M.events.CALL,cb); M.register_callback(TID,M.events.PY_START,cb)
want=set(sys.argv[1:]); out={}
for combo in stress.sweep_combinations():
    combo=dict(combo); label=combo.pop("label")
    if "ALL" not in want and label not in want: continue
    codes=prod_codes()
    for co in codes: M.set_local_events(TID,co,M.events.CALL|M.events.PY_START)
    n[0]=0; perfile.clear(); t=time.process_time(); run=stress.build_case(**combo); cpu=time.process_time()-t
    for co in codes: M.set_local_events(TID,co,0)
    out[label]={"evals":int(run.get("solver_evals",0)),"simulate":int(run.get("solver_simulate_steps") or 0),"files":{os.path.basename(k):v for k,v in perfile.items()},"calls":n[0],
                "objective":float(run["result"].objective_value),"cpu_s":round(cpu,3)}
    print(label, json.dumps(out[label]), flush=True)
print("ROWS", json.dumps(out))
