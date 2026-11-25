import json,sys,itertools
d=json.load(open(sys.argv[1]))['closures']
def prod(v):
    fs=v if isinstance(v,list) else v.get('files',v.get('closure',[]))
    return {f for f in fs if f.startswith('custom_components/')}
C={k:prod(v) for k,v in d.items()}
n=len(C);ne=[k for k in C if C[k]]
hi=[];allp=0
for a,b in itertools.combinations(sorted(C),2):
    allp+=1
    A,B=C[a],C[b]
    if A and B:
        j=len(A&B)/len(A|B)
        if j>=0.80: hi.append((a,b,round(j,3)))
print('scripts',n,'pairs',allp,'nonempty',len(ne),'comparable',len(ne)*(len(ne)-1)//2,'>=0.80',len(hi))
for p in hi:
    if 'manual_plan' in p[0]+p[1] or 'config_flow_steps' in p[0]+p[1]: print(p)
