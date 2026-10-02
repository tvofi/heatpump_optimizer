import sys, os, json
tree = os.getcwd()
sys.argv = [f"{tree}/tests/stress.py"]
src = open("tests/stress.py").read()
cut = src.index('if "--memory-probe" in sys.argv:')
g = {"__name__": "stress_ab", "__file__": f"{tree}/tests/stress.py"}
exec(compile(src[:cut], "tests/stress.py", "exec"), g)
spec = dict(season="shoulder", two_zone=True, dhw=True, tariff=True, pv=True, cycling=1.0)
ref = g["reference_solve"]()
case = g["build_case"](**spec)
r = case["result"]
import hashlib, numpy as np
sha = hashlib.sha1(np.asarray(r.power_schedule, float).tobytes() + np.asarray(r.dhw_power_schedule or [], float).tobytes()).hexdigest()[:12]
print(json.dumps({"ref_ms": ref[1], "solve_cpu_ms": case["solve_cpu_ms"], "plan": sha, "obj": float(r.objective_value)}))
