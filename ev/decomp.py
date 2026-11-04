import json,sys,statistics
sys.path.insert(0,'/root/wt')
from tests import ci_ratchet as cr
rr=json.load(open('/root/wt/dev/audit/harnesses/r10_hotfix_ci_critpath_4/runs.json'))['workflow_runs']
fl=json.load(open('/root/wt/dev/audit/harnesses/r10_hotfix_ci_critpath_4/fleet.json'))['workflow_runs']
def P(r):
    r=dict(r); r.pop('event',None); r['conclusion']='success'; return r
def decomp(runs):
    needs,counted,work,probed={},set(),{},{}
    for r in runs:
        w=cr._walk(r)
        if w is None: continue
        for j in w:
            needs.setdefault(j['name'],set())
            if j['pred'] is not None: needs[j['name']].add(w[j['pred']]['name'])
            if j['counted']: counted.add(j['name'])
            if j['priced']:
                work.setdefault(j['name'],[]).append(j['work'])
                if j['reference_work'] is not None: probed.setdefault(j['name'],[]).append(j['reference_work'])
    price={n:cr.job_price(s,probed.get(n)) for n,s in work.items()}
    end={};arg={}
    def pe(n,seen=()):
        if n not in end:
            c=[(pe(m,(*seen,n)),m) for m in needs[n] if m not in (*seen,n)]
            b=max(c,default=(0.0,None))
            end[n]=price.get(n,0)+b[0]; arg[n]=b[1]
        return end[n]
    top=max(counted,key=pe)
    path=[];n=top
    while n: path.append((n,round(price.get(n,0)/60,2), 'P' if n in probed else '')); n=arg[n]
    print(round(pe(top)/60,3), list(reversed(path)))
    return needs
which=sys.argv[1]
if which=='main': decomp(rr[:16])
if which=='p3': n=decomp([P(p) for p in fl]); print({k:sorted(v) for k,v in n.items() if v})
if which=='p1': decomp([P(fl[1])]+rr[:15])
if which=='p0': decomp([P(fl[0])]+rr[:15])
pushnames={j['name'] for r in rr[:16] for j in r['jobs']}
def Q(r):
    r=P(r); r['jobs']=[j for j in r['jobs'] if j['name'] in pushnames]; return r
if which=='c1': decomp([Q(fl[1])]*16)
if which=='c2': decomp([Q(fl[2])]*16)
if which=='mix': decomp([Q(fl[1]),Q(fl[2])]+rr[:14])
