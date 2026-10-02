import os,sys,json,subprocess,io,contextlib,re,collections
sys.path.insert(0,"tools/audit"); import merge_fastpath as m
reads=json.load(open("tests/closures.json")).get("inert_reads",{})
orig=m._git
def git(*a):
    o=orig(*a)
    if a[0]=="show" and a[1].endswith(":tests/closures.json"):
        t=json.loads(o); t["inert_reads"]=reads; return json.dumps(t)
    return o
m._git=git
c=collections.Counter()
for M in subprocess.run(["git","rev-list","--first-parent","--merges","-n","120","origin/main"],capture_output=True,text=True).stdout.split():
    b=io.StringIO()
    with contextlib.redirect_stdout(b):
        try:m.run(M+"^2",M+"^1",None)
        except Exception:pass
    for l in b.getvalue().splitlines():
        if l.startswith("REFUSE unrecorded"):
            f=re.search(r"changes (\S+),",l).group(1)
            c[re.sub(r"/\d+\.md$","/N.md",f) if "delivery" in f else ("/".join(f.split("/")[:2]))]+=1
print(c.most_common(15))
