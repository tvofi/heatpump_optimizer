#!/usr/bin/env python3
"""Tally round-9 panels from the 12 votes files, using audit-verify.js's PANEL rules."""
import json, subprocess, sys, collections
REPO=sys.argv[1]; OUT=sys.argv[2]
def git(*a): return subprocess.run(['git','-C',REPO,*a],capture_output=True,text=True).stdout
git('fetch','-q','origin',*[f'handoff/audit-r9-verify-g{g}-v{k}' for g in range(1,5) for k in range(1,4)])
def hasnum(v): x=v.get('value'); return x is not None and str(x).strip()!=''
def norm(v): return {**v,'vote':'unresolved','note':'refute without an executed number'} if v.get('vote')=='refute' and not hasnum(v) else v
votes=collections.defaultdict(dict); heads={}; missing=[]
for g in range(1,5):
  for k in range(1,4):
    br=f'origin/handoff/audit-r9-verify-g{g}-v{k}'
    heads[f'G{g}-V{k}']=git('rev-parse','--short',br).strip()
    raw=None
    for name in (f'votes-G{g}-v{k}.json',f'votes-G{g}-V{k}.json'):
      raw=git('show',f'{br}:tools/audit/round9/verify/{name}')
      if raw: break
    if not raw: missing.append(f'G{g}-V{k}'); continue
    d=json.loads(raw)
    units=d["votes"] if isinstance(d,dict) and isinstance(d.get("votes"),dict) else (d if isinstance(d,dict) else {"all":d})
    for unit,vs in units.items():
      if isinstance(vs,dict): vs=vs.get("votes",list(vs.values()))
      if not isinstance(vs,list): continue
      for v in vs:
        if isinstance(v,dict) and v.get('id'):
          votes[v['id']][f'V{k}']={**norm(v),'group':f'G{g}','unit':unit}
out={'heads':heads,'missing_files':missing,'findings':{}}
for fid,vs in sorted(votes.items()):
  cast=list(vs.values()); ref=sum(v['vote']=='refute' for v in cast)
  panel='killed' if ref>=2 else 'disputed' if ref==1 else ('unanimous' if len(cast)==3 and all(v['vote']=='verify' for v in cast) else 'split')
  out['findings'][fid]={'panel':panel,'n_votes':len(cast),'votes':vs}
c=collections.Counter(f['panel'] for f in out['findings'].values())
out['counts']=dict(c); out['incomplete']=[i for i,f in out['findings'].items() if f['n_votes']<3]
json.dump(out,open(OUT,'w'),indent=1)
print(heads); print('missing',missing); print(dict(c),'findings',len(out['findings']),'incomplete',len(out['incomplete']))
print('killed',[i for i,f in out['findings'].items() if f['panel']=='killed'])
print('disputed',[i for i,f in out['findings'].items() if f['panel']=='disputed'])
print('incomplete',out['incomplete'][:40])
