import json,subprocess
def load(r): return json.loads(subprocess.check_output(['git','show',f'{r}:tools/ci/selftest_closures.json']))
def flat(o,p=''):
    out={}
    if isinstance(o,dict):
        for k,v in o.items(): out.update(flat(v,p+'/'+k))
    else: out[p]=o
    return out
def delta(a,b):
    A,B=flat(load(a)),flat(load(b)); d={}
    for k in set(A)|set(B):
        x,y=A.get(k),B.get(k)
        if x==y: continue
        if isinstance(x,list) and isinstance(y,list):
            sx={json.dumps(i,sort_keys=True) for i in x}; sy={json.dumps(i,sort_keys=True) for i in y}
            d[k]=('list',tuple(sorted(sy-sx)),tuple(sorted(sx-sy)))
        else: d[k]=('val',json.dumps(x,sort_keys=True),json.dumps(y,sort_keys=True))
    return d
d1=delta('e23124ff6e45bac1d48b4a775dad555a37965355','6a0a3a4d96c757c5d576fbce394c324452339b15')
d2=delta('009643687b47bc51bda9b3fd98a99f0ece5307cc','99c3c1625923adaae044b8f1940344196a9b30af')
print('prev',len(d1),'head',len(d2))
for k in sorted(set(d1)|set(d2)):
    a,b=d1.get(k),d2.get(k)
    if a==b: print('SAME',k,str(a)[:150])
    else: print('DIFFER',k,'\n  prev',str(a)[:400],'\n  head',str(b)[:400])
