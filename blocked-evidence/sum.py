import sys
from collections import defaultdict
for fn in sys.argv[1:]:
    r=defaultdict(lambda:[0,0]); wrong=[]
    for l in open(fn):
        if not l.startswith('SWEEP'): continue
        f=l.split(); kind,kw,amp,per,seed,phase,s0,noise,v,sc=f[1:]
        good=(v!='follows') if kind=='selfset' else (v=='follows')
        k=(kind,'scale0='+s0); r[k][0]+=1; r[k][1]+=not good
        if not good: wrong.append(l.strip())
    print(fn, {f"{a} {b}":f"{w}/{n} wrong" for (a,b),(n,w) in sorted(r.items())})
    for w in wrong[:12]: print("  ",w)
