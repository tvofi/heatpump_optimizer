import json,subprocess,sys
R,MB=sys.argv[1:3]
def show(rev,p): return subprocess.run(['git','show',f'{rev}:{p}'],capture_output=True,text=True,check=True).stdout
ro=json.loads(show(R,'dev/programme/rosters/wave-r10-groups.json'))
groups=ro['groups'] if isinstance(ro,dict) else ro
g={x['group']:x for x in groups}
answered={('carry-201.json',13),('carry-201.json',18),('carry-201.json',22)}
ok=bad=0
for f in ['carry-1922.json','carry-201.json','carry-2065.json','carry-2066.json','carry-2075.json']:
  d=json.loads(show(MB,'dev/programme/carries/'+f))
  for i,e in enumerate(d['carries']):
    if (f,i) in answered: continue
    dest='R10-OUTSIDE-CONTRIBUTOR-CYCLE' if f=='carry-2075.json' else 'R11-INTAKE-R10-RESIDUE'
    grp=g.get(dest)
    if grp is None: print('NOGROUP',dest); bad+=1; continue
    cs=grp.get('carry',[])
    txt=[c if isinstance(c,str) else json.dumps(c) for c in cs]
    b=e['brief'][:200]
    hit=[t for t in txt if b in t or b.replace('"','\\"') in t]
    print(('OK ' if hit else 'MISS'),f,i,dest,len(hit)); ok+=bool(hit); bad+=not hit
print('RESULT readback ok=%d miss=%d'%(ok,bad))
