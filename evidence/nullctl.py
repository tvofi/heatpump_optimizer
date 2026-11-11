import re,subprocess,sys
sys.path.insert(0,'dev/audit/harnesses')
from dependabot_stale_hash import parse
def g(*a):
    r=subprocess.run(["git",*a],capture_output=True,text=True); return r.stdout
tab={}
for n in sys.argv[1:]:
    c=g("rev-parse",f"pr/{n}").strip()
    files=[p for p in g("diff","--name-only",c+"^",c).split() if re.fullmatch(r"tests/requirements[^/]*\.txt",p)]
    for f in files:
        o,nw=g("show",f"{c}^:{f}"),g("show",f"{c}:{f}")
        b,a=parse(o),parse(nw)
        com="\n".join(l for l in o.splitlines() if l.lstrip().startswith("#")).lower()
        for k,(v,h) in a.items():
            if k not in b or b[k][0]==v: continue
            stale = bool(h) and h==b[k][1]
            # literal raw-name spelling variants: -,_ ; check name==oldver in comment
            pat=re.sub(r"-","[-_.]",re.escape(k).replace(r"\-","-"))
            incom=bool(re.search(pat+r"==" + re.escape(b[k][0]).lower(), com))
            tab[(incom,stale)]=tab.get((incom,stale),0)+1
            if incom or stale: print(n,f,k,b[k][0],"->",v,"comment" if incom else "-", "STALE" if stale else "fresh")
print(tab)
