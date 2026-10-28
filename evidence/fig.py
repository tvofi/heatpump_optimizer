import json,sys,collections
def grp(p):
    d=json.load(open(p)); out={}
    def walk(x):
        if isinstance(x,dict):
            if 'group' in x and 'resume' in x: out[x['group']]=x; return
            for v in x.values(): walk(v)
        elif isinstance(x,list):
            for v in x: walk(v)
    walk(d); return out
m,h=grp(sys.argv[1]),grp(sys.argv[2])
print('groups main',len(m),'head',len(h),'removed',sorted(set(m)-set(h)),'new',sorted(set(h)-set(m)))
ch=[g for g in sorted(m) if g in h and m[g]!=h[g]]; print('changed',len(ch))
for g in ch:
    ks=sorted(k for k in set(m[g])|set(h[g]) if m[g].get(k)!=h[g].get(k)); e=''
    if 'resume' in ks: e+='stage %s->%s'%(m[g]['resume'].get('stage'),h[g]['resume'].get('stage'))
    if 'carry' in ks: e+='carry %d->%d'%(len(m[g].get('carry') or []),len(h[g].get('carry') or []))
    print(' ',g,ks,e)
for n,x in (('main',m),('head',h)): print('stages',n,dict(sorted(collections.Counter(v['resume'].get('stage') for v in x.values()).items())))
