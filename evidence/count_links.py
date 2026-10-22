import re,subprocess,sys,pathlib,json
ref=sys.argv[1]
def sh(*a): return subprocess.run(["git",*a],capture_output=True,text=True).stdout
exec(open("dev/audit/rounds/round4/D6/claims.py").read().split("\nDOCS")[0][:0])
names=[l for l in sh("ls-tree","--name-only",ref,"docs/").split() if l.endswith(".md")]
files=["README.md","DISCLAIMER.md"]+names
links=[];imgs=[]
for f in files:
    t=sh("show",f"{ref}:{f}")
    t=re.sub(r"^```.*?^```","",t,flags=re.M|re.S)
    for m in re.finditer(r"\[[^\]]*\]\(([^)\s]+)\)",t):
        x=m.group(1)
        if x.startswith("http") or x.startswith("#"): continue
        if not x.split("#")[0]: continue
        links.append((f,x))
    for m in re.finditer(r"!\[[^\]]*?\]\(([^)\s]+)\)",t):
        if m.group(1).startswith("http"): continue
        imgs.append((f,m.group(1)))
json.dump({"links":links,"imgs":imgs},open(sys.argv[2],"w"))
print(ref,len(links),len(imgs))
