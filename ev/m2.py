import subprocess,sys,pathlib
wt=pathlib.Path(sys.argv[1]); f=wt/'tools/plan/replan.py'; orig=f.read_text()
M=[
("credit-lane-r2","if n in G and lane[n] in PRODUCTION and n in done]","if n in G and n in done]"),
("credit-done-r2","if n in G and lane[n] in PRODUCTION and n in done]","if n in G and lane[n] in PRODUCTION]"),
("merge-topic-lastseg",'return m.group(1).rsplit("/", 1)[-1].lower() if m else None','return m.group(1).lower() if m else None'),
("merge-topic-lower",'return m.group(1).rsplit("/", 1)[-1].lower() if m else None','return m.group(1).rsplit("/", 1)[-1] if m else None'),
("merge-re-anchor",'MERGE_BRANCH_RE = re.compile(r"^Merge pull request #\\d+ from \\S+/(\\S+)\\s*$")','MERGE_BRANCH_RE = re.compile(r"Merge pull request #\\d+ from (\\S+)")'),
("squash-fallback-dropped","        if n is None:\n            named = [g for g in G if g in c[\"subject\"]]\n            n = max(named, key=len) if named else None\n","\n"),
("squash-longest",'            n = max(named, key=len) if named else None\n        if n and roster_lane','            n = min(named, key=len) if named else None\n        if n and roster_lane'),
("topic-only-no-subject-fallback-when-topic","        n = by_topic.get(topic) if topic else None","        n = None"),
("since-prod-lane","if n and roster_lane(G[n]) in PRODUCTION and substantive","if n and substantive"),
("since-substantive",'and substantive(c.get("diff") or ""):','and True:'),
("design-subtract","live = (live - demoted - ev_design) | ev_live","live = (live - demoted) | ev_live"),
("first-parent-diff",'"diff", "-U0", f"{sha}^1", sha,','"diff", "-U0", f"{sha}~0", sha,'),
]
for name,a,b in M:
  if orig.count(a)!=1: print(name,'ANCHOR',orig.count(a)); continue
  f.write_text(orig.replace(a,b))
  try:
    r=subprocess.run([sys.executable,'tools/plan/replan.py','--self-test'],cwd=wt,capture_output=True,text=True,timeout=900)
    fails=[l[:160] for l in r.stdout.splitlines() if l.startswith('FAIL')]
    print(name,'rc=',r.returncode,'KILLED' if r.returncode else 'SURVIVED',fails[:1],flush=True)
  finally: f.write_text(orig)
