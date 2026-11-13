import json,subprocess,sys
base,head=sys.argv[1],sys.argv[2]
F='tools/ci/selftest_closures.json'
ld=lambda r: json.loads(subprocess.check_output(['git','show',f'{r}:{F}']))
tree=set(subprocess.check_output(['git','ls-tree','-r','--name-only',head]).decode().split('\n'))
dirs={p.rsplit('/',1)[0] for p in tree if '/' in p}|{'.'}
B,H=ld(base),ld(head)
drops=[]
for k in B:
    if k not in H: drops.append(('top-key',k))
for st,e in B['steps'].items():
    if st not in H['steps']: drops.append(('step',st)); continue
    h=H['steps'][st]
    for f,v in e.items():
        if f not in h: drops.append(('field',st,f)); continue
        if isinstance(v,list):
            for p in v:
                if p in h[f]: continue
                gone = (f=='files' and p not in tree) or (f=='dirs' and p not in dirs)
                if f=='probes' and p not in tree and p not in dirs: gone=True
                if gone: print('excused (not in tree at head):',st,f,p); continue
                drops.append(('entry',st,f,p))
        elif v is True and h[f] is not True: drops.append(('flag',st,f))
for d in drops: print('DROPPED',*d)
print(f'dropped={len(drops)} base_steps={len(B["steps"])} head_steps={len(H["steps"])}')
