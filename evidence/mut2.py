"""Round-2 reviewer runner: the round-1 reviewer's ev/mut.py plants X1,X2,X6,X7,X8 (verbatim anchors)
plus this reviewer's apply_plan omission plants A1-A4; each in its OWN detached worktree at the head,
run under that file's own --self-test with env -u BASH_ENV python3 -I, restored after."""
import subprocess, sys, os
REPO="/home/user/heatpump_optimizer"; H="361be3cd6cdc6a594b542956403220efdd4f0803"
SY="tools/audit/seat/roster_sync.py"; ED="tools/audit/seat/roster_edit.py"
P = [
 ("X1_sync_writepath_rederive_no_legacy", SY, "changes, _, transitions = derive(roster, prs, legacy)", "changes, _, transitions = derive(roster, prs)"),
 ("X2_sync_unreadable_cutover_swallowed", SY, 'raise Refuse(f"the carry cut-over is unreadable: {e}")', "legacy = {}"),
 ("X6_edit_unreadable_cutover_swallowed", ED, 'raise Refuse(f"the carry cut-over is unreadable, so no "\n                                 f"stage is written: {e}")', "legacy = {}"),
 ("X7_moved_to_closed_allowed", ED, "if stage in roster_lib.CARRY_CLOSED:", "if False:"),
 ("X8_bracket_value_allowed", ED, 'if "]" in arg:', "if False:"),
 # reviewer's own: omit legacy inside apply_plan and at each call site
 ("A1_apply_plan_opsetstage_no_legacy", SY, "roster_edit.op_set_stage(roster, c.group, c.stage, c.merge_commit,\n                                 legacy=legacy)", "roster_edit.op_set_stage(roster, c.group, c.stage, c.merge_commit)"),
 ("A2_apply_plan_write_call_no_legacy", SY, "apply_plan(roster, changes, appends, legacy)", "apply_plan(roster, changes, appends)"),
 ("A4_dryrun_projection_no_legacy", SY, "        apply_plan(projected, changes, [], legacy)\n        appends, refusals", "        apply_plan(projected, changes, [])\n        appends, refusals"),
 ("A5_write_projection_no_legacy", SY, "            apply_plan(projected, changes, [], legacy)\n            appends, _", "            apply_plan(projected, changes, [])\n            appends, _"),
 ("A6_moved_closed_only_done", ED, "if stage in roster_lib.CARRY_CLOSED:", "if stage == 'done':"),
 ("A3_apply_plan_legacy_param_ignored", SY, "    for c in changes:\n        roster_edit.op_set_stage(", "    legacy = None\n    for c in changes:\n        roster_edit.op_set_stage("),
]
only=set(sys.argv[1:])
for name,f,a,b in P:
    if only and name not in only: continue
    wt=f"/home/user/wt-{name[:3]}"
    subprocess.run(["git","-C",REPO,"worktree","remove","--force",wt],capture_output=True)
    subprocess.run(["git","-C",REPO,"worktree","add","--detach",wt,H],capture_output=True,check=True)
    path=os.path.join(wt,f); s=open(path).read(); n=s.count(a)
    if n!=1: print(f"RESULT mutant={name} ANCHOR-COUNT={n} (not run)"); continue
    open(path,"w").write(s.replace(a,b))
    try:
        r=subprocess.run(["env","-u","BASH_ENV","python3","-I",f,"--self-test"],cwd=wt,capture_output=True,text=True,timeout=900)
        out=r.stdout+r.stderr
        fails=[l.strip() for l in out.splitlines() if "FAIL" in l][:3]
        summ=[l for l in out.splitlines() if "self-test:" in l][-1:]
        print(f"RESULT mutant={name} rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'} {summ} {fails}",flush=True)
    finally:
        open(path,"w").write(s)
    st=subprocess.run(["git","-C",wt,"status","--short"],capture_output=True,text=True).stdout.strip()
    print(f"  restored {wt}: {st or 'clean'}",flush=True)
