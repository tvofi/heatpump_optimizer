# Batch-1 intake, mechanical half: the same rules as audit-find.js lines 263-326 (origin/main 1936d5ca), ported
# because the Workflow gatherer could not carry the reports (classifier stop). Reads the box branches directly.
import json, re, subprocess, collections, sys
R='/home/claude/heatpump_optimizer'; OUT=sys.argv[1]
DEFER=['D3-s2','D3-s3']
g=lambda *a: subprocess.check_output(['git','-C',R,*a],text=True)
reports={}; srcs={}
for b in [f'B{i}' for i in range(1,11)]:
    br=f'origin/handoff/audit-r9-find-{b}'
    d=json.loads(g('show',f'{br}:tools/audit/round9/reports-{b}.json'))
    sha=g('rev-parse','--short',br).strip()
    for k,v in d['reports'].items():
        assert k not in reports, k; reports[k]=v; srcs[k]={'box':b,'sha':sha}
scopes=json.loads(g('show','origin/main:tools/audit/scopes.json')); rot=json.loads(g('show','origin/main:tools/audit/rotation.json'))
DIMS=[d for d in scopes if d.startswith('D')]
SEATS=[f'{d}-{k}' for d in DIMS for k in scopes[d]['seats']]
missing=[s for s in SEATS if s not in reports and s not in DEFER]
assert not missing, missing
REPORTED=[s for s in SEATS if s in reports]
CG=re.compile(r'^([PI][0-9]+|new)$')
rejected=[]; accepted=[]
for sid in REPORTED:
    for f in reports[sid].get('findings') or []:
        why=[]
        if f.get('scope')!=sid: why.append(f'scope {json.dumps(f.get("scope"))} is not the seat that returned it ({sid})')
        if not (isinstance(f.get('id'),str) and f['id'].startswith(sid+'-')): why.append(f'id {json.dumps(f.get("id"))} is not numbered under {sid}')
        if not CG.match(str(f.get('class_guess',''))): why.append(f'class_guess {json.dumps(f.get("class_guess"))} is neither a ledger id nor "new"')
        (rejected.append({'id':f.get('id') or sid+'-?','seat':sid,'reason':'; '.join(why)}) if why else accepted.append({**f,'seat':sid}))
leads=[{**l,'raised_by':sid} for sid in REPORTED for l in (reports[sid].get('leads') or [])]
byOwner=collections.defaultdict(list)
for l in leads: byOwner[l.get('owner_seat')].append(l)
RANK={'none':0,'spot':1,'deep':2}
ledger={}
for d in DIMS:
    mine=[s for s in SEATS if s.startswith(d+'-')]
    cov={}
    for m in rot[d]['steps']:
        seen=[c.get('depth') for s in mine for c in (reports.get(s,{}).get('coverage') or []) if c.get('step') in (f'{d}.{m}',m)]
        best='none'
        for x in seen:
            if RANK.get(x,0)>RANK[best]: best=x
        cov[m]=best
    unf=[{'step':str(u.get('step')).replace(d+'.',''),'what':u.get('what')} for s in mine for u in (reports.get(s,{}).get('unfinished') or [])]
    ret={s.split('-')[1]:sum(1 for f in accepted if f['seat']==s) for s in mine}
    seatsteps=[sorted({st for blk in scopes[d]['seats'][s.split('-')[1]] for st in blk['steps']}, key=lambda x:int(x[1:])) for s in mine]
    ledger[d]={'seats':seatsteps,'coverage':cov,'unfinished':unf,'returned':ret,'leads':{'raised':sum(1 for l in leads if l['raised_by'].startswith(d+'-')),'converted':None}}
provisional=[f['id'] for f in accepted if any(isinstance(x,dict) and x.get('provisional') for x in [f]+list((f.get('metrics') or []) if isinstance(f.get('metrics'),list) else []))]
json.dump({'reports':reports,'sources':srcs},open(f'{OUT}/reports.json','w'),indent=1)
json.dump(accepted,open(f'{OUT}/accepted.json','w'),indent=1)
json.dump(rejected,open(f'{OUT}/rejected.json','w'),indent=1)
json.dump(dict(byOwner),open(f'{OUT}/leads_by_owner.json','w'),indent=1)
json.dump(ledger,open(f'{OUT}/ledger_round9.json','w'),indent=1,sort_keys=True)
json.dump({s:reports[s].get('report_path') for s in REPORTED},open(f'{OUT}/report_paths.json','w'),indent=1)
sev=collections.Counter(str(f.get('severity')) for f in accepted)
print('seats',len(REPORTED),'of',len(SEATS),'deferred',DEFER,'accepted',len(accepted),'rejected',len(rejected),'leads',len(leads),'owners',len(byOwner),'severity',dict(sev),'provisional',len(provisional))
for r in rejected: print('REJ',r)
