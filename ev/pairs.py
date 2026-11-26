import json,sys,subprocess,itertools
d=json.loads(subprocess.check_output(['git','show',sys.argv[1]+':tests/closures.json']))
c=d['closures']
def prod(v):
    if isinstance(v,dict): v=v.get('files') or v.get('closure') or v.get('reads') or []
    return {f for f in v if f.startswith('custom_components/')}
S={k:prod(v) for k,v in c.items()}
n=len(S); ne=[k for k in S if S[k]]
for name,fn in [('jacc',lambda a,b:len(a&b)/len(a|b)),('min',lambda a,b:len(a&b)/min(len(a),len(b))),('max',lambda a,b:len(a&b)/max(len(a),len(b)))]:
    cnt=sum(1 for a,b in itertools.combinations(ne,2) if fn(S[a],S[b])>=0.80)
    print(sys.argv[1][:8],name,cnt,'scripts',n,'pairs',n*(n-1)//2,'nonempty pairs',len(ne)*(len(ne)-1)//2,'empty',sorted(set(S)-set(ne)))
