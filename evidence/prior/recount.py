# independent: per-file line of last non-blank, non-comment-only line, past 2000, by text not ast
import sys, pathlib, subprocess
def tot(rev):
    files = subprocess.run(["git","ls-tree","-r","--name-only",rev,"custom_components/"],capture_output=True,text=True).stdout.split()
    s=0; per={}
    for f in files:
        if not f.endswith(".py"): continue
        lines = subprocess.run(["git","show",f"{rev}:{f}"],capture_output=True,text=True).stdout.splitlines()
        last=0
        for i,l in enumerate(lines,1):
            t=l.strip()
            if t and not t.startswith("#"): last=i
        per[f]=max(0,last-2000); s+=per[f]
    return s,per
for r in sys.argv[1:]:
    s,per=tot(r); print(r[:10], "total", s, {k.split('/')[-1]:v for k,v in per.items() if v})
