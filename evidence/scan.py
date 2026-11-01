import subprocess,collections
def g(*a): return subprocess.run(['git',*a],capture_output=True,text=True).stdout
refs=[l.split()[0] for l in g('for-each-ref','--format=%(refname)','refs/remotes/origin/verdict/').splitlines()]
pairs=0;prefs=set();le60=0;tipcopy=0;since=0
for r in refs:
    out=g('log','--first-parent','--format=%H %T %ct %P',r).splitlines()
    rows=[o.split() for o in out]
    byh={x[0]:x for x in rows}
    tp=False
    for i,x in enumerate(rows):
        if len(x)>3:
            p=byh.get(x[3])
            if p and p[1]==x[1]:
                pairs+=1;prefs.add(r)
                if int(x[2])-int(p[2])<=60: le60+=1
                if int(x[2])>=1793318400: since+=1  # 2026-10-30T00:00Z
                if i==0: tipcopy+=1
print(len(refs),pairs,len(prefs),le60,tipcopy,since)
