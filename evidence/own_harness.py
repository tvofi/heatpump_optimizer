"""Reviewer's own harness for #3201 (not the fixer's replay.py)."""
import copy, json, sys, importlib.util
from datetime import datetime, timedelta, timezone
W=sys.argv[1]; D='dev/audit/harnesses/r10_hotfix_ci_critpath_4'
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
M=load('cm',f'{W}/main/ci_ratchet_main.py'); H=load('ch',f'{W}/main/ci_ratchet_head.py')
runs=json.load(open(f'{D}/runs.json'))['workflow_runs']
fleet=json.load(open(f'{D}/fleet.json'))['workflow_runs']
at=lambda s:datetime.fromisoformat(s.replace('Z','+00:00'))
iso=lambda d:d.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
runs.sort(key=lambda r:r.get('created_at') or r.get('run_started_at') or '', reverse=True)
# A: unprobed null control, every 16-window, main vs head grader
diffs=[]; 
for i in range(len(runs)-15):
    w=runs[i:i+16]
    try: a=M.window_work_minutes(w); b=H.window_work_minutes(w)
    except Exception as e: print('A err',i,e); continue
    diffs.append((i,a,b,round(b-a,3)))
nz=[d for d in diffs if d[3]!=0]
print(f'RESULT A unprobed windows={len(diffs)} nonzero_diff={len(nz)} newest main={diffs[0][1]} head={diffs[0][2]}')
for d in nz[:5]: print('  A nz',d)
# B: probed windows built from fleet's two all-success runs
ok=[r for r in fleet if all(j.get('conclusion') in ('success','skipped') or not j['name'].startswith('tests /') for j in r['jobs'])]
print('fleet all-success runs', [r['id'] for r in ok])
def scale(r, f, probe_f=None, only=None, add=None):
    """scale every job's timeline (and its steps) by f relative to run start; probe step by probe_f"""
    r=copy.deepcopy(r); t0=min(at(j['created_at']) for j in r['jobs'])
    S=lambda s:iso(t0+(at(s)-t0)*f)
    for j in r['jobs']:
        for k in ('created_at','started_at','completed_at'):
            if j.get(k): j[k]=S(j[k])
        for s in j.get('steps') or []:
            st=at(s['started_at']); dur=(at(s['completed_at'])-st).total_seconds()
            s['started_at']=S(s['started_at'])
            pf = probe_f if (probe_f and s['name'].startswith('Probe')) else f
            s['completed_at']=iso(at(s['started_at'])+timedelta(seconds=round(dur*pf)))
    return r
def addwork(r, job, secs):
    """+secs of work on `job`, and on every job after it in time (shift later jobs)"""
    r=copy.deepcopy(r); jj=[j for j in r['jobs'] if j['name']==job][0]; end=at(jj['completed_at'])
    for j in r['jobs']:
        if j is jj: j['completed_at']=iso(end+timedelta(seconds=secs)); continue
        for k in ('created_at','started_at','completed_at'):
            if j.get(k) and at(j[k])>=end: j[k]=iso(at(j[k])+timedelta(seconds=secs))
    return r
def g(w): return H.window_work_minutes(w)
for base in ok:
    w=[base]*16; g0=g(w)
    slow=g([scale(base,1.9)]*16)
    mixed=g([scale(base,1.9) if i%2 else base for i in range(16)])
    probe_noise=g([scale(base,1.0,probe_f=2.0) if i==0 else base for i in range(16)])
    unp=M.window_work_minutes(w); unp_slow=M.window_work_minutes([scale(base,1.9)]*16)
    print(f"RESULT B run={base['id']} probed={g0} fleet1.9x={slow} (d={round(slow-g0,3)}) half-slow={mixed} (d={round(mixed-g0,3)}) one-probe-2x={probe_noise} | main-grader {unp} -> 1.9x {unp_slow}")
    for k in (1,4,8,9,12,16):
        gr=g([addwork(base,'tests / closures',300) if i<k else base for i in range(16)])
        gm=M.window_work_minutes([addwork(base,'tests / closures',300) if i<k else base for i in range(16)])
        print(f"   +300s closures in {k:2d}/16: probed d={round(gr-g0,3)} main d={round(gm-unp,3)}")
    # growth on slow hosts only (work grows exactly when the fleet slows): must still read
    gr=g([addwork(scale(base,1.9),'tests / closures',570) if i<9 else base for i in range(16)])
    print(f"   +300s ref-work closures in 9/16 runs, those runs also on 1.9x hosts: probed d={round(gr-g0,3)}")
