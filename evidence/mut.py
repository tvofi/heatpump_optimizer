import subprocess, sys, os, pathlib
wt = pathlib.Path(sys.argv[1]); out = pathlib.Path(sys.argv[2])
M = [
 ("closed-no-refused-deferred","tools/audit/seat/roster_lib.py",'CLOSED_STAGES = DONE_STAGES + ("absorbed", "refused", "deferred")','CLOSED_STAGES = DONE_STAGES + ("absorbed",)'),
 ("closed-add-refuted","tools/audit/seat/roster_lib.py",'CLOSED_STAGES = DONE_STAGES + ("absorbed", "refused", "deferred")','CLOSED_STAGES = DONE_STAGES + ("absorbed", "refused", "deferred", "refuted")'),
 ("closed-only-refused","tools/audit/seat/roster_lib.py",'CLOSED_STAGES = DONE_STAGES + ("absorbed", "refused", "deferred")','CLOSED_STAGES = DONE_STAGES + ("absorbed", "refused")'),
 ("stem-plain-prefix","tools/plan/replan.py",'g == p or g.startswith(p + "-") for p in INSTRUMENT_NAME_STEMS','g.startswith(p) for p in INSTRUMENT_NAME_STEMS'),
 ("stem-no-exact","tools/plan/replan.py",'g == p or g.startswith(p + "-") for p in INSTRUMENT_NAME_STEMS','g.startswith(p + "-") for p in INSTRUMENT_NAME_STEMS'),
 ("cp-not-exempt","tools/plan/replan.py","and cc >= coord_cap and not cap_exempt:","and cc >= coord_cap:"),
 ("cp-call-no-exempt","tools/plan/replan.py","if x in crit), t, cap_exempt=True)","if x in crit), t)"),
 ("flag-gt","tools/plan/replan.py","if coord[n] and in_flight_coord() >= coord_cap:","if coord[n] and in_flight_coord() > coord_cap:"),
 ("flag-never","tools/plan/replan.py","                exempt_coord.add(n)","                pass"),
 ("check-ignores-flag","tools/plan/replan.py",'if g.get("coordinator") and not g.get("exempt_coordinator")]','if g.get("coordinator")]'),
 ("output-no-flag","tools/plan/replan.py",'            groups_out[n]["exempt_coordinator"] = True','            pass'),
 ("tick-skip-deferred","tools/audit/seat/orchestrator_tick.py","if gid not in open_g and stage not in DEFERRED_STAGES:","if gid not in open_g:"),
]
tests = [["tools/plan/replan.py","--self-test"],["tools/audit/seat/roster_lib.py","--self-test"],["tools/audit/seat/orchestrator_tick.py","--self-test"]]
env = dict(os.environ, REPLAN_MUTATION_CHILD="1")
with out.open("w") as fo:
  for name, f, a, b in M:
    p = wt/f; src = p.read_text()
    assert src.count(a)>=1, (name, src.count(a))
    if name.startswith("closed-"): continue
    p.write_text(src.replace(a,b,1))
    try:
      res=[]
      for t in tests:
        r = subprocess.run([sys.executable,"-I",*t],cwd=wt,env=env,capture_output=True,text=True,timeout=230)
        fails=[l for l in r.stdout.splitlines() if l.lstrip().startswith("FAIL")]
        res.append(f"{pathlib.Path(t[0]).stem} rc={r.returncode} fails={len(fails)} {fails[:2]}")
      killed = any(" rc=0 " not in x or "fails=0" not in x for x in res)
      fo.write(f"RESULT mutant {name}: {'KILLED' if killed else 'SURVIVED'} | " + " ; ".join(res)+"\n"); fo.flush()
    finally:
      p.write_text(src)
