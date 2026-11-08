# Reviewer's own mutants on the carry-16 production lines (round 4, resolution delta).
import subprocess,sys,pathlib
f=pathlib.Path(sys.argv[1])/'tools/plan/replan.py'; orig=f.read_text()
M=[
("pending-ignores-legacy","pending = roster_lib.pending_carries(group, legacy or {})","pending = roster_lib.pending_carries(group, {})"),
("pending-all","pending = roster_lib.pending_carries(group, legacy or {})","pending = list(range(len(group.get(\"carry\") or [])))"),
("left-count-zero","left = len(group.get(\"carry\") or []) - len(pending)","left = 0"),
("added-gt","added = sum(1 for i in pending if i >= cut)","added = sum(1 for i in pending if i > cut)"),
("then-le","sum(1 for i in pending if i < cut))","sum(1 for i in pending if i <= cut))"),
("then-max","then = min(int(rec[\"open\"]),","then = max(int(rec[\"open\"]),"),
("then-no-pending","then = min(int(rec[\"open\"]), sum(1 for i in pending if i < cut))","then = min(int(rec[\"open\"]), cut)"),
("added-unmarked-all","added = sum(1 for i in pending if i >= cut)","added = max(0, len(group.get(\"carry\") or []) - cut)"),
("absorbed-left-out-dropped","        why += left_out\n","\n"),
("held-left-out-dropped","f\"{how}: {parts} part(s){left_out}\")","f\"{how}: {parts} part(s)\")"),
("build-legacy-none",'roster_path or roster_ref or "<fixture>", legacy)','roster_path or roster_ref or "<fixture>", None)'),
("main-legacy-none","                      legacy=legacy)","                      legacy=None)"),
("main-legacy-path","f\"{roster_lib.ROSTERS_DIR}/{src.rsplit('/', 1)[-1]}\")","src)"),
]
for name,a,b in M:
    if orig.count(a)!=1: print(name,'ANCHOR',orig.count(a)); continue
    f.write_text(orig.replace(a,b))
    try:
        r=subprocess.run([sys.executable,'-I','tools/plan/replan.py','--self-test'],cwd=sys.argv[1],capture_output=True,text=True,timeout=900,env={'PATH':'/opt/hpo/venv-ci/bin:/usr/bin:/bin','REPLAN_MUTATION_CHILD':'1','HOME':'/root'})
        fails=[l for l in r.stdout.splitlines() if l.startswith('FAIL')]
        print(name,'rc=',r.returncode,'KILLED' if r.returncode else 'SURVIVED',fails[:2],flush=True)
    finally: f.write_text(orig)
