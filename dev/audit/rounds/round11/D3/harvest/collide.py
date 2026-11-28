#!/usr/bin/env python3
"""Split the candidates: deferred to a D3 fold group (same anchor as one of its findings),
deferred to an open PR (its diff rewrites a line of the site, or touches the site's row file),
else drivable. A PR rewrites a site when its diff removes, in that file, a line equal to a line of the site's old text."""
import json,re,subprocess,sys,glob,collections
cand=json.load(open(sys.argv[1])); U=json.load(open(sys.argv[2])); fold=json.load(open(sys.argv[3])); prs=sys.argv[4].split(',')
bykey={}
for p in glob.glob('dev/audit/rounds/round11/D3/s1/state/results/*/*.json'):
    a=(json.load(open(p)).get('mutant') or {}).get('anchor')
    if a: bykey.setdefault(p.rsplit('/',1)[1][:-5],a)
foldA={}
for g,v in fold['groups'].items():
    for f in v['findings']:
        a=bykey.get(f['id'].split('-')[-1])
        if a: foldA.setdefault(a,g)
olds=collections.defaultdict(set)
for x in U:
    for t in x['old'].splitlines():
        if t.strip(): olds[x['anchor']].add((x['file'],t))
def rowpath(a):
    f,rest=a.split(':',1); scope,kind,dig=rest.rsplit(' ',2); dig=dig.replace('#','.')
    return f"tests/mutation_ledger/killed_by/{f.rsplit('/',1)[1]}/{scope}.{kind}.{dig}.json"
hunks=collections.defaultdict(list); rows=collections.defaultdict(set)
for n in prs:
    mb=subprocess.run(['git','merge-base','origin/main',f'pr/{n}'],capture_output=True,text=True).stdout.strip()
    out=subprocess.run(['git','diff','-U0',f'{mb}...pr/{n}'],capture_output=True,text=True).stdout
    cur=None
    for l in out.splitlines():
        if l.startswith('--- '): cur=l[6:] if l.startswith('--- a/') else None
        elif l.startswith('+++ b/') and 'mutation_ledger' in l: rows[n].add(l[6:])
        elif l.startswith('-') and not l.startswith('--- ') and cur:
            hunks[(n,cur)].append(l[1:])
res={'fold':{},'pr':{},'drive':[]}
for a in sorted(cand):
    if a in foldA: res['fold'][a]=foldA[a]; continue
    hit=[n for n in prs if rowpath(a) in rows[n] or any(t in hunks.get((n,f),()) for f,t in olds[a])]
    if hit: res['pr'][a]=hit; continue
    res['drive'].append(a)
print('candidates',len(cand),'deferred-fold',len(res['fold']),'deferred-pr',len(res['pr']),'drive',len(res['drive']))
print(collections.Counter(res['fold'].values())); print(collections.Counter(n for v in res['pr'].values() for n in v))
json.dump(res,open(sys.argv[5],'w'),indent=1)
