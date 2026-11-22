# Equivalence of _build_comfort_bounds' floor arithmetic: 48d28b55 (old) vs 8800ed7c (new).
import numpy as np, sys
def pn(v,n):
    h=np.clip(np.asarray(v,dtype=float),0.0,None)[:n]; return np.pad(h,(0,n-h.size))
def rf_old(low,high,m,f,n):
    comfort,mold=low,None
    if m is None and f is None: return low,comfort,mold
    if m is not None: low=comfort=low+pn(m,n)
    if f is not None:
        ff=np.asarray(f,dtype=float)[:n]; mold=np.full(n,-np.inf); mold[:ff.size]=ff; low=np.maximum(low,mold)
    return np.minimum(low,high-0.5),comfort,mold
def rf_new(low,high,m,f,n):
    comfort,mold=low,None
    if m is None and f is None: return low,comfort,mold
    if m is not None: low=comfort=low+m
    if f is not None:
        ff=np.asarray(f,dtype=float)[:n]; mold=np.full(n,-np.inf); mold[:ff.size]=ff; low=np.maximum(low,mold)
    return np.minimum(low,high-0.5),comfort,mold
def old(low,high,mtm,fl,rl,n):
    t,c,mo=rf_old(low,high,mtm,fl,n); lifts=None
    if rl is not None:
        mg=pn(np.zeros(n) if mtm is None else mtm,n)
        un=rf_old(low,high,mg-pn(rl,n),fl,n)[0]; lifts=np.maximum(t-un,0.0)
    return t,c,mo,lifts
def new(low,high,mtm,fl,rl,n):
    mg=None if mtm is None else pn(mtm,n)
    t,c,mo=rf_new(low,high,mg,fl,n); lifts=None
    if rl is not None:
        un=rf_new(low,high,(0.0 if mg is None else mg)-pn(rl,n),fl,n)[0]; lifts=np.maximum(t-un,0.0)
    return t,c,mo,lifts
rng=np.random.default_rng(7); n=48; diffs_fl=0; diffs_adv=0; N=20000
def eq(a,b):
    return all((x is None and y is None) or (x is not None and y is not None and np.array_equal(x,y)) for x,y in zip(a,b))
for k in range(N):
    low=rng.uniform(17,21,n); high=low+rng.uniform(0.3,4,n)
    base=None if k%3==0 else rng.uniform(-0.2,1.0,rng.integers(10,60))
    fl=None if k%2 else rng.uniform(10,22,rng.integers(5,60))
    # floor_limits shape: total = clip(base)+lift, lift >= 0, length m
    m=rng.integers(10,60); lift=np.clip(rng.uniform(-0.5,1.5,m),0,None)*(rng.random(m)<0.6)
    bm=np.zeros(m)
    if base is not None:
        h=np.clip(base[:m],0,None); bm[:h.size]=h
    tot=bm+lift
    if not eq(old(low,high,tot,fl,lift,n),new(low,high,tot,fl,lift,n)): diffs_fl+=1
    # adversarial: lifts larger than margins (not producible by floor_limits)
    mt=None if k%4==0 else rng.uniform(0,0.5,n); rl=rng.uniform(0,1.5,n)
    if not eq(old(low,high,mt,fl,rl,n),new(low,high,mt,fl,rl,n)): diffs_adv+=1
    # no lift
    assert eq(old(low,high,tot,fl,None,n),new(low,high,tot,fl,None,n))
print(f"floor_limits-shaped inputs: {diffs_fl}/{N} differ; lifts>margins inputs: {diffs_adv}/{N} differ; no-lift: 0/{N} differ")
