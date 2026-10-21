import json,subprocess,sys
def load(rev,p): return json.loads(subprocess.check_output(['git','show',f'{rev}:{p}']))
b,h=sys.argv[1],sys.argv[2]
R='dev/programme/rosters/wave-r10-groups.json'
B={g['group']:g for g in load(b,R)['groups']}; H={g['group']:g for g in load(h,R)['groups']}
print('RESULT groups',len(B),'->',len(H))
st=lambda D:sum(1 for g in D.values() if g.get('stage')=='done')
print('RESULT stage-done',st(B),'->',st(H))
cc=lambda D:sum(len(g.get('carry') or []) for g in D.values())
print('RESULT carries',cc(B),'->',cc(H))
new=[k for k in H if k not in B]; print('RESULT new',len(new),[(k,H[k].get('stage')) for k in new])
print('RESULT removed',[k for k in B if k not in H])
ch=[(k,B[k].get('stage'),H[k].get('stage')) for k in B if k in H and B[k].get('stage')!=H[k].get('stage')]
print('RESULT stage-changes',len(ch)); [print('  ',*c) for c in ch]
ca=[(k,len(B[k].get('carry') or []),len(H[k].get('carry') or [])) for k in B if k in H and (B[k].get('carry') or [])!=(H[k].get('carry') or [])]
print('RESULT carry-changed-existing',len(ca),'appended',sum(c[2]-c[1] for c in ca),'new-group carries',sum(len(H[k].get('carry') or []) for k in new)); [print('  ',*c) for c in ca]
te=[k for k in B if k in H and any(B[k].get(f)!=H[k].get(f) for f in ('brief','issues','fixes','findings'))]
print('RESULT text-edits',len(te),te)
other=[k for k in B if k in H and any(B[k].get(f)!=H[k].get(f) for f in set(B[k])|set(H[k]) if f not in ('brief','issues','fixes','findings','stage','carry'))]
print('RESULT other-field-edits',len(other),other)
S=lambda g:(g.get('resume') or {}).get('stage')
print('RESULT resume.stage-done',sum(S(g)=='done' for g in B.values()),'->',sum(S(g)=='done' for g in H.values()))
print('RESULT new-stages',[(k,S(H[k])) for k in new])
ch=[(k,S(B[k]),S(H[k])) for k in B if k in H and S(B[k])!=S(H[k])]
print('RESULT resume.stage-changes',len(ch)); [print('  ',*c) for c in ch]
