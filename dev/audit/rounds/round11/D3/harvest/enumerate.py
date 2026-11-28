#!/usr/bin/env python3
"""Every mutant a round-11 D3 box reports KILLED, keyed by ledger anchor.
Family B: dev/audit/rounds/round11/D3/s1/state/results/*/*.json on origin/main, verdict == KILLED.
Family S2: dev/audit/rounds/round11/D3/s2/drive/pairs.jsonl, hit is true.
Family A: refs/d3/<name>, the refs handoff/audit-r11-find-D3-<name>
  (git fetch origin '+refs/heads/handoff/audit-r11-find-D3-g06:refs/d3/11-find-D3-g06' and so on, every ref ls-remote lists), s1/wave/*/results/*.json, gate.verdict == KILLED,
  key mapped to its anchor through the family-B record of the same key."""
import json,glob,subprocess,sys,re
# argv: UNPINNED.json (anchor list of main's unpinned sites) CANDIDATES_OUT.json DECLINED_OUT.json
U={x['anchor'] for x in json.load(open(sys.argv[1]))}
ANCH=re.compile(r'^custom_components/\S+\.py:\S+ [A-Z_]+ [0-9a-f]{8}(#\d+)?$')
bykey={}; rep={}
for p in sorted(glob.glob('dev/audit/rounds/round11/D3/s1/state/results/*/*.json')):
    r=json.load(open(p)); a=(r.get('mutant') or {}).get('anchor'); k=p.rsplit('/',1)[1][:-5]
    if a: bykey.setdefault(k,a)
    if r.get('verdict')=='KILLED':
        rep.setdefault(a,[]).append(dict(src=p.split('/')[-2],key=k,killed_by=r.get('killed_by')))
refs=subprocess.run(['git','for-each-ref','--format=%(refname)','refs/d3'],capture_output=True,text=True).stdout.split()
nA=0
for ref in refs:
    for path in subprocess.run(['git','ls-tree','-r','--name-only',ref,'--','dev/audit/rounds/round11/D3/s1/wave/'],capture_output=True,text=True).stdout.split():
        if not re.search(r'/results/[0-9a-f]{16}\.json$',path): continue
        r=json.loads(subprocess.run(['git','show',f'{ref}:{path}'],capture_output=True,text=True).stdout)
        if (r.get('gate') or {}).get('verdict')!='KILLED': continue
        nA+=1; k=r['key']; a=bykey.get(k)
        rep.setdefault(a or f'UNMAPPED {k}',[]).append(dict(src=ref.split('/')[-1],key=k,killed_by=r['gate'].get('killed_by')))
for l in open('dev/audit/rounds/round11/D3/s2/drive/pairs.jsonl'):
    x=json.loads(l)
    if x.get('hit') is True: rep.setdefault(x['anchor'],[]).append(dict(src='s2-pairs',key=x['item'],killed_by=[x['script']]))
nonledger=[a for a in rep if not (a and ANCH.match(a))]
led=[a for a in rep if a and ANCH.match(a)]
un=sorted(a for a in led if a in U)
print(f'family-A KILLED records {nA}; KILLED identities {len(rep)}: ledger anchors {len(led)}, non-ledger {len(nonledger)}; unpinned at main {len(un)}; already disposed at main {len(led)-len(un)}')
json.dump({a:rep[a] for a in un},open(sys.argv[2],'w'),indent=1)
json.dump({'nonledger':nonledger,'disposed':sorted(set(led)-set(un))},open(sys.argv[3],'w'),indent=1)
