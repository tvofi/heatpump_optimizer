import json,subprocess,sys,copy
sys.path.insert(0,'tools/audit/seat'); import roster_lib as rl
R='dev/programme/rosters/wave-r10-groups.json'
base=json.loads(subprocess.check_output(['git','show','origin/main:'+R]))
head=json.load(open(sys.argv[1] if len(sys.argv)>1 else R))
drops=json.load(open('dev/programme/round10/rechain/rechain-drops.json'))
adds=json.load(open('dev/programme/round10/rechain/rechain-adds.json'))
exp={g['group']:list(g['after'] or []) for g in base['groups']}
for d in drops:
  for a in d['drop_after']: exp[d['group']].remove(a)
for k in ('required','recommended'):
  for x in adds[k]:
    for a in x['add_after']: exp[x['group']].append(a)
exp['R10-HEAT-METER'].append('R10-THERMAL-POWER-OPTION')  # orchestrator addition per brief/body
fail=0
H=rl.groups_of(head)
for g,lst in exp.items():
  got=H[g].get('after') or []
  if set(got)!=set(lst) or len(got)!=len(set(got)): print('MISMATCH',g,'expected',sorted(lst),'got',sorted(got)); fail+=1
for g,l in adds['resulting_after_lists'].items():
  extra={'R10-HEAT-METER':['R10-THERMAL-POWER-OPTION']}.get(g,[])
  if set(H[g].get('after') or [])!=set(l+extra): print('RESULTING-LIST MISMATCH',g); fail+=1
for d in drops:
  for a in d['drop_after']:
    print('DROP',d['group'],'after',a,'gone' if a not in (H[d['group']].get('after') or []) else 'PRESENT'); 
for k in ('required','recommended'):
  for x in adds[k]:
    for a in x['add_after']: print('ADD',k,x['group'],'after',a,'present' if a in (H[x['group']].get('after') or []) else 'MISSING')
changed=[g for g in exp if (rl.groups_of(base)[g].get('after') or [])!=(H[g].get('after') or [])]
print('groups whose after changed:',len(changed),sorted(changed))
try:
  db=rl.depth_of(base); dh=rl.depth_of(head); print('no cycle')
except ValueError as e: print('CYCLE',e); fail+=1; sys.exit(1)
cb=rl.critical_path(base); ch=rl.critical_path(head)
print('depth before',len(cb),cb); print('depth after',len(ch),ch)
print('max depth before',max(db[k] for k in rl.open_groups(base)),'after',max(dh[k] for k in rl.open_groups(head)))
for k in sorted(rl.open_groups(head)):
  if db.get(k)!=dh.get(k): print('  depth',k,db.get(k),'->',dh.get(k))
print('RESULT edgecheck', 'PASS' if fail==0 and len(ch)==8 and len(cb)==11 else 'FAIL', 'fail=%d'%fail)
