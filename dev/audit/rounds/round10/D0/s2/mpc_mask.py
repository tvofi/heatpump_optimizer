"""D0-s2 MPC masking (D0.M6): does the one-shot gap survive the receding horizon?

Metric: realised closed-loop cost over 1 day (SEK, energy at price) and
comfort (min room, degree-steps below 17 C) for production vs a loop whose every
optimizer:_multi_start_minimize call is replaced by the augmented challenger
(production starts + bang-bang starts, maxiter 1500, L-BFGS-B polish), using
tests/rolling.py:run_rolling (exec'd up to its test body), REPLAN 2 h, plant_error 1.0.
Key: history['cost'] summed. Gap_pct = (prod - chal)/prod.
--arm ftol: the 'chal' arm is production with ftol 1e-10 (the D0-s2-01 fix candidate).
Command: PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python dev/audit/rounds/round10/D0/s2/mpc_mask.py [--maxiter N]
Baseline 17f1c55fad1b, macOS arm64 box B2. Expected: see REPORT.md, tolerance +-0.5 pp.
"""
import os
for v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v,"1")
import sys, time, argparse
sys.path.insert(0,"tests"); sys.path.insert(0,"custom_components")
import numpy as np
from unittest import mock
from scipy.optimize import minimize
src=open("tests/rolling.py").read().split('R.section("Stability over three days")')[0]
G={"__name__":"rolling_cut"}; exec(compile(src,"tests/rolling.py","exec"),G)
run_rolling=G["run_rolling"]
from heatpump_optimizer import optimizer as OM
REAL=OM._multi_start_minimize
ap=argparse.ArgumentParser(); ap.add_argument("--maxiter",type=int,default=0)
ap.add_argument("--arm",default="chal",help="chal | ftol (production with ftol 1e-10 via optimizer:_scoped_minimize)")
ap.add_argument("--cells",default="winter_typical:winter_cold:1:1,winter_typical:winter_mild:1:0,winter_extreme:winter_cold:1:1,winter_narrow:winter_cold:1:1,winter_moderate:winter_cold:1:1,flat:winter_cold:1:1,flat:winter_mild:1:0")
A=ap.parse_args()
t0p,t0t=time.process_time(),time.thread_time()

def prod(objective,candidates,bounds,args=(),maxiter=300,**kw):
    if A.maxiter: maxiter=A.maxiter
    return REAL(objective,candidates,bounds,args,maxiter,**kw)

def chal(objective,candidates,bounds,args=(),maxiter=300,**kw):
    r=prod(objective,candidates,bounds,args,maxiter,**kw)
    f=lambda x: float(objective(x,*args))
    hi=np.array([b[1] for b in bounds]); lo=np.array([b[0] for b in bounds])
    # bang-bang on the objective's own cheapest steps is unknown here; use fractions of upper bound
    extra=[np.array(r.x)]+[lo+(hi-lo)*fr for fr in (0.25,0.5,0.75)]
    kw2=dict(kw); kw2.pop("move_starts",None)
    r2=REAL(objective,[np.array(c) for c in candidates]+extra,bounds,args,1500,**kw2)
    pol=minimize(f,np.array(r2.x),method="L-BFGS-B",bounds=bounds,options=dict(maxiter=5000,maxfun=100000,ftol=1e-12))
    best=r2 if f(r2.x)<=pol.fun else pol
    if f(best.x) < f(r.x):
        r.x=np.array(best.x); r.fun=f(best.x)
    return r

for cell in A.cells.split(","):
    pp,wp,tz,dh=cell.split(":"); tz=bool(int(tz)); dh=bool(int(dh))
    out={}
    RSM=OM._scoped_minimize
    def sm(*a,**kw):
        if "options" in kw: kw["options"]=dict(kw["options"],ftol=1e-10)
        return RSM(*a,**kw)
    for name,fn in (("prod",prod),("chal",chal)):
        tgt,repl=(("_scoped_minimize",sm) if (A.arm=="ftol" and name=="chal") else ("_multi_start_minimize",fn))
        with mock.patch.object(OM,tgt,repl):
            h=run_rolling(days=1,dhw=dh,two_zone=tz,plant_error=1.0,price_profile=pp,weather_profile=wp)["history"]
        room=h["room"]; out[name]=(float(h["cost"].sum()),float(room.min()),float(np.maximum(0,17.0-room).sum()),float(h["dhw"].min()))
    gp=(out["prod"][0]-out["chal"][0])/out["prod"][0]
    print(f"RESULT closedloop_gap[{cell}]={100*gp:.4f} pct prodSEK={out['prod'][0]:.3f} chalSEK={out['chal'][0]:.3f} minroom prod={out['prod'][1]:.2f} chal={out['chal'][1]:.2f} below17 prod={out['prod'][2]:.3f} chal={out['chal'][2]:.3f} dhwmin prod={out['prod'][3]:.1f} chal={out['chal'][3]:.1f}",flush=True)
pc,tc=time.process_time()-t0p,time.thread_time()-t0t
print(f"RESULT thread_factor={pc/tc:.3f}"); print(f"RESULT load1={os.getloadavg()[0]:.2f}"); print("RESULT swapins=n/a")
