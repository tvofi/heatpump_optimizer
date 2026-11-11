import sys, numpy as np
sys.argv=["x"]
exec(open(sys.argv[0] if False else __import__("os").path.expanduser("~/svr_check.py")).read().split("_svr_lin, _svr_der")[0])
for d in (0.0, 0.2):
    opt,p=_svr_opt(d); prices,out=np.linspace(0.5,2.0,96),np.full(96,-5.0)
    for top in (21.0, 22.0, 24.0):
        X=_svr_state(top)
        for a,b in ((21.0,12.0),(21.0,20.0),(20.6,20.0)):
            if top<a: continue
            A,B=_svr_state(a),_svr_state(b)
            direct=opt._deferred_energy_cost(A,B,prices,out)
            via=opt._deferred_energy_cost(X,B,prices,out)-opt._deferred_energy_cost(X,A,prices,out)
            print(f"d={d} ref={a} plan={b} anchor={top}: f(gap)={direct:.4f} f(anchor-plan)-f(anchor-ref)={via:.4f} diff={via-direct:+.4f}")
