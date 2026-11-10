import subprocess,re,sys
def g(*a): return subprocess.run(["git",*a],capture_output=True,text=True).stdout
lo,hi="2026-11-06T00:00:00Z","2026-11-10T03:30:00Z"
import datetime
refs=g("for-each-ref","--format=%(refname) %(objectname) %(committerdate:iso-strict)","refs/remotes/origin/handoff-body/").split("\n")
def utc(s): return datetime.datetime.fromisoformat(s).astimezone(datetime.timezone.utc)
L=utc(lo.replace("Z","+00:00"));H=utc(hi.replace("Z","+00:00"))
res=0;tr=0;no=[];moved=0
for line in refs:
  if not line: continue
  r,sha,d=line.split(" ");t=utc(d)
  if t>H: moved+=1
  if not(L<=t<=H): continue
  b=g("log","-1","--format=%B",sha)
  if not re.search(r"^Code: ",b,re.M): res+=1;continue
  if re.search(r"^Prepr: ",b,re.M): tr+=1
  else: no.append((r,sha))
print(f"in-window unmoved tips: result={res} trailer={tr} none={len(no)} code={tr+len(no)}; refs with tip after 03:30Z={moved}")
# split for none
cat={"same":0,"ancestor_merge_only":0,"new_nonmerge":0,"never":0}
for r,sha in no:
  code=re.search(r"^Code: (\S+)",g("log","-1","--format=%B",sha),re.M).group(1)
  prev=None
  for c in g("rev-list",sha+"^").split():
    m=re.search(r"^Prepr: (\S+)",g("log","-1","--format=%B",c),re.M)
    if m: prev=m.group(1);break
  if not prev: cat["never"]+=1;continue
  full=g("rev-parse",prev).strip()
  if full==g("rev-parse",code).strip(): cat["same"]+=1;continue
  nm=g("rev-list","--no-merges",f"{prev}..{code}").split()
  # non-merge commits not on main
  own=[c for c in nm if subprocess.run(["git","merge-base","--is-ancestor",c,"origin/main"]).returncode!=0]
  cat["ancestor_merge_only" if not own else "new_nonmerge"]+=1
print(cat)
eq=conf=diff=0
for r,sha in no:
  code=re.search(r"^Code: (\S+)",g("log","-1","--format=%B",sha),re.M).group(1)
  prev=None
  for c in g("rev-list",sha+"^").split():
    m=re.search(r"^Prepr: (\S+)",g("log","-1","--format=%B",c),re.M)
    if m: prev=m.group(1);break
  if not prev or g("rev-parse",prev).strip()==g("rev-parse",code).strip(): continue
  mb=g("merge-base",code,"origin/main").strip()
  p=subprocess.run(["git","merge-tree","--write-tree",prev,mb],capture_output=True,text=True)
  if p.returncode: conf+=1; continue
  if p.stdout.split()[0]==g("rev-parse",code+"^{tree}").strip(): eq+=1
  else: diff+=1
print(f"earlier-trailer, different code: tree-equal={eq} conflict={conf} differ={diff}")
