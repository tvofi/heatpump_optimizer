import json,sys,statistics as st,math
sys.path.insert(0,'/root/wt3045/tests')
import ci_ratchet as c
runs=json.load(open(sys.argv[1]))['workflow_runs']
runs=sorted(runs,key=lambda r:r['created_at'])
m=[(r['created_at'],r['head_sha'][:9],c.run_minutes(r)) for r in runs]
m=[x for x in m if x[2] is not None]
v=[x[2] for x in m]; n=len(v)
med=st.median(v); s=sorted(v)
print(f"RESULT n={n} span={m[0][0]}..{m[-1][0]} median={med:.3f} sigma={st.stdev(v):.3f} p90={s[math.ceil(0.9*n)-1]:.3f}")
w=[st.median(v[i:i+8]) for i in range(n-7)]
print(f"RESULT sliding8 min={min(w):.3f} max={max(w):.3f} max|dev|={max(abs(x-med) for x in w):.3f}")
print(f"RESULT first20 median={st.median(v[:20]):.3f} last20 median={st.median(v[-20:]):.3f} newest8 median={st.median(v[-8:]):.3f}")
if len(sys.argv)>2:
  for x in m[-12:]: print(*x)
