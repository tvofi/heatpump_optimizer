"""Class search: per-production-function interpreter calls in one solve.
PYTHONPATH=tests/hastub python callmap.py '<build_case spec json>' [topN]
Prints, per production qualname: py_start (entries) and calls made from its bytecode.
"""
import os, sys, time, json, types, collections
for k in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"):
    os.environ.setdefault(k, "1")
sys.path[:0] = ["tests", "custom_components"]
import stress
from heatpump_optimizer import optimizer as opt_mod
PKG = os.path.dirname(opt_mod.__file__)
spec = json.loads(sys.argv[1]); top = int(sys.argv[2]) if len(sys.argv) > 2 else 25

def prod_codes():
    seen=set(); out=[]
    def walk(co):
        if id(co) in seen: return
        seen.add(id(co)); out.append(co)
        for c in co.co_consts:
            if isinstance(c, types.CodeType): walk(c)
    for name, mod in list(sys.modules.items()):
        f = getattr(mod, "__file__", None) or ""
        if not f.startswith(PKG): continue
        for obj in list(vars(mod).values()):
            for cand in ([obj] + (list(vars(obj).values()) if isinstance(obj, type) else [])):
                fn = getattr(cand, "fget", cand); fn = getattr(fn, "__func__", fn)
                co = getattr(fn, "__code__", None)
                if co is not None and co.co_filename.startswith(PKG): walk(co)
    return out

M=sys.monitoring; T=4
M.use_tool_id(T,"map")
made=collections.Counter(); starts=collections.Counter()
def on_call(code, off, c, a): made[code] += 1
def on_start(code, off): starts[code] += 1
M.register_callback(T, M.events.CALL, on_call); M.register_callback(T, M.events.PY_START, on_start)
codes=prod_codes()
for co in codes: M.set_local_events(T, co, M.events.CALL|M.events.PY_START)
t=time.process_time(); run=stress.build_case(**spec); dt=time.process_time()-t
for co in codes: M.set_local_events(T, co, 0)
tot_made=sum(made.values()); tot_start=sum(starts.values())
name=lambda co: f"{os.path.basename(co.co_filename)[:-3]}:{co.co_qualname}:{co.co_firstlineno}"
print(json.dumps({"spec":spec,"cpu_s":round(dt,2),"calls_made":tot_made,"py_starts":tot_start,
  "objective":float(run['result'].objective_value),"evals":run.get('solver_evals'),"simulate":run.get('solver_simulate_steps')}))
print("-- top by calls made from bytecode (share of total)")
for co,n in made.most_common(top): print(f"{n:>9} {n/tot_made:6.1%}  starts={starts[co]:>7}  {name(co)}")
print("-- top by entries (py_start)")
for co,n in starts.most_common(top): print(f"{n:>9} {n/tot_start:6.1%}  made={made[co]:>8}  {name(co)}")
