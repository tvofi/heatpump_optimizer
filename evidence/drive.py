import sys, re, importlib.util, numpy as np
sys.path[:0]=['custom_components','tests/hastub','tests']
def load(path, name, subs=()):
    s=open(path).read()
    for a,b in subs:
        assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
    open(f'/tmp/_r2010_{name}.py','w').write(s)
    # package-relative imports: execute inside package namespace
    spec=importlib.util.spec_from_file_location('heatpump_optimizer.opt_'+name, f'/tmp/_r2010_{name}.py')
    m=importlib.util.module_from_spec(spec); m.__package__='heatpump_optimizer'; sys.modules[spec.name]=m
    spec.loader.exec_module(m); return m
import heatpump_optimizer  # package
P='custom_components/heatpump_optimizer/optimizer.py'
def checks(m):
    ic=m.idle_codes; thr=0.05; out=[]
    def call(*a):
        try: return True, ic(*a)
        except Exception as e: return False, type(e).__name__
    # check 1: surplus arriving with next run is not a wait
    ok,g=call(2,np.array([0.0,1.0]),None,None,None,np.array([0.0,2.0]),None,None,thr)
    out.append(('next-run bound', ok and g[0]!=m.REASON_IDLE_SOLAR, g))
    ok,g=call(-1,np.zeros(1),None,None,None,None,None,None,thr)
    out.append(('negative n', ok and g==[], g))
    return out
base=load(P,'new')
print('NEW', checks(base))
for name,a,b in [('bound_le','nxt_sun < nxt_run','nxt_sun <= nxt_run'),('bound_gt','nxt_sun < nxt_run','nxt_sun > nxt_run'),('guard_off','    if n <= 0:\n','    if False:\n'),('guard_lt','    if n <= 0:\n','    if n < 0:\n')]:
    m=load(P,name,[(a,b)]); print(name, checks(m))
# equivalence fuzz old vs new
old=load('/Users/timmalmstrom/hpo-seats/review-2010-delta/evidence/opt_old.py','old')
rng=np.random.default_rng(7); bad=0; N=60000
vals=[0.0,0.05,1e-6,1.0,np.nan,np.inf,-np.inf]
def arr(L):
    return None if rng.random()<0.15 else np.array([ (rng.choice(vals) if rng.random()<.7 else rng.random()) for _ in range(L)])
for _ in range(N):
    n=int(rng.integers(-2,7)); L=lambda: max(0,n+int(rng.integers(-2,4)))
    pw=np.array([rng.choice(vals) for _ in range(L())]); args=(n,pw,arr(L()),arr(L()),arr(L()),arr(L()),arr(L()),arr(L()),float(rng.choice([0,0.05,1])))
    def r(m):
        try: return repr(m.idle_codes(*args))
        except Exception as e: return type(e).__name__
    if r(old)!=r(base): bad+=1
print('fuzz old-vs-new mismatches',bad,'of',N)
# triage claim: n<0 mutant == new except nothing at n==0; control differs
mut=load(P,'lt',[('    if n <= 0:\n','    if n < 0:\n')])
ctl=load(P,'ctl',[('    if n <= 0:\n','    if n < 0:\n'),('    codes = np.full(n, REASON_IDLE, dtype=object)\n','    codes = np.full(n, REASON_IDLE, dtype=object)\n    if n == 0:\n        return ["n0"]\n')])
d=dc=n0=0
rng=np.random.default_rng(11)
for _ in range(20000):
    n=int(rng.integers(-2,4)); L=lambda: max(0,n+int(rng.integers(-2,4)))
    pw=np.array([rng.choice(vals) for _ in range(L())]); args=(n,pw,arr(L()),arr(L()),arr(L()),arr(L()),arr(L()),arr(L()),float(rng.choice([0,0.05,1])))
    def r(m):
        try: return repr(m.idle_codes(*args))
        except Exception as e: return type(e).__name__
    n0+= n==0; d+= r(mut)!=r(base); dc+= r(ctl)!=r(base)
print('n==0 cases',n0,'mutant-vs-new diffs',d,'control-vs-new diffs',dc)
