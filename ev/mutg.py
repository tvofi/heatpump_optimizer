import subprocess,sys,pathlib
wt=pathlib.Path('wt2'); f=wt/'tools/audit/seat/gantt_drift.py'; orig=f.read_text()
M=[
#("fired-filter",'[l for l in fired.splitlines() if "FIRED" in l]','fired.splitlines()'),
("cp-first","return idle + rest","return rest + idle"),
#,"horizon = now_t + dt.timedelta(minutes=grace_min)","horizon = now_t"),
("late-threshold","if d > late_h * 3600:","if d > 0:"),
("closure-threshold","if d > closure_h * 3600:","if d >= 0:"),
#,"if not a.get(\"until\") or now_t < ts(a[\"until\"]):","if True:"),
#,'if v.get("done") or not v.get("start"):','if not v.get("start"):'),
("word-boundary",'rf"(?<![\\w-]){re.escape(n)}(?![\\w-])"','re.escape(n)'),
#,"            out.append(b.lower())","            pass"),
]
for name,a,b in M:
  pass
  f.write_text(orig.replace(a,b,1))
  try:
    r=subprocess.run([sys.executable,'-I','tools/audit/seat/gantt_drift.py','--self-test'],cwd=wt,capture_output=True,text=True,timeout=300)
    print(name,'rc=',r.returncode,'KILLED' if r.returncode else 'SURVIVED', (r.stdout.strip().splitlines() or [''])[-1])
  finally: f.write_text(orig)
