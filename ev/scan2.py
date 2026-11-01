import subprocess
def g(*a): return subprocess.run(['git',*a],capture_output=True,text=True).stdout
refs=g('for-each-ref','--format=%(refname)','refs/remotes/origin/verdict/').split()
n=0;pr=set();tc=0;l60=0;s=0;seen=set()
for r in refs:
    rows=[o.split() for o in g('log','--format=%H %T %ct %P',r).splitlines()]
    byh={x[0]:x for x in rows}
    for i,x in enumerate(rows):
        for ph in x[3:]:
            p=byh.get(ph)
            if p and p[1]==x[1]:
                n+=1;pr.add(r)
                if int(x[2])-int(p[2])<=60:l60+=1
                if int(x[2])>=1793318400:s+=1
                if i==0:tc+=1
print(n,len(pr),l60,tc,s)
