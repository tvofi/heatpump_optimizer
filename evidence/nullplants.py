"""N1/N2 are equivalent (closing_stage never downgrades carries-open, L5), kept as recorded. N3/N4 force the projection to done.
Round-3 reviewer's own null-direction plants (not the finder's): each makes a projection over-close
(every carry read as legacy), so the guard over-refuses; the null controls must go red. Same protocol:
own detached worktree at the head, single-occurrence replacement, --self-test under env -u BASH_ENV python3 -I, restored."""
import subprocess, sys, os
REPO="/home/user/heatpump_optimizer"; H=sys.argv[1]
SY="tools/audit/seat/roster_sync.py"
ALL='{gid: frozenset(g.get("carry") or []) for gid, g in roster_lib.groups_of(projected).items()}'
DONE='[c._replace(stage="done") if c.stage == "carries-open" else c for c in changes]'
P=[
 ("N3_dryrun_projection_overcloses", SY, "        apply_plan(projected, changes, [], legacy)\n        appends, refusals", f"        apply_plan(projected, {DONE}, [], {ALL})\n        appends, refusals"),
 ("N4_write_projection_overcloses", SY, "            apply_plan(projected, changes, [], legacy)\n            appends, _", f"            apply_plan(projected, {DONE}, [], {ALL})\n            appends, _"),
 ("N1_dryrun_projection_all_legacy", SY, "        apply_plan(projected, changes, [], legacy)\n        appends, refusals", f"        apply_plan(projected, changes, [], {ALL})\n        appends, refusals"),
 ("N2_write_projection_all_legacy", SY, "            apply_plan(projected, changes, [], legacy)\n            appends, _", f"            apply_plan(projected, changes, [], {ALL})\n            appends, _"),
]
for name,f,a,b in P:
    wt=f"/home/user/wt3n-{name[:2]}"
    subprocess.run(["git","-C",REPO,"worktree","remove","--force",wt],capture_output=True)
    subprocess.run(["git","-C",REPO,"worktree","add","--detach",wt,H],capture_output=True,check=True)
    path=os.path.join(wt,f); s=open(path).read(); n=s.count(a)
    if n!=1: print(f"RESULT mutant={name} ANCHOR-COUNT={n}"); continue
    open(path,"w").write(s.replace(a,b))
    try:
        r=subprocess.run(["env","-u","BASH_ENV","python3","-I",f,"--self-test"],cwd=wt,capture_output=True,text=True,timeout=900)
        out=r.stdout+r.stderr
        fails=[l.strip()[:160] for l in out.splitlines() if "FAIL" in l][:4]
        summ=[l for l in out.splitlines() if "self-test:" in l][-1:]
        print(f"RESULT head={H[:9]} mutant={name} rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'} {summ} {fails}",flush=True)
    finally: open(path,"w").write(s)
    st=subprocess.run(["git","-C",wt,"status","--short"],capture_output=True,text=True).stdout.strip()
    print(f"  restored {wt}: {st or 'clean'}"); subprocess.run(["git","-C",REPO,"worktree","remove","--force",wt],capture_output=True)
