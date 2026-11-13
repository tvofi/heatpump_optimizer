import sys,pathlib
M={
"cwd_repo":("            rc, out, err = ctx.run(argv, wt, env)","            rc, out, err = ctx.run(argv, ctx.repo, env)"),
"no_remember":('    ctx.remember("darwin-selftest.json", {"tip": tip})\n',""),
"keep_state_dir":('if k != "HPO_STATE_DIR"}','if True}'),
"wired_filter_dropped":(' and p in wired]',']'),
"no_final_remove":('    finally:\n        ctx.run(["git", "-C", str(ctx.repo), "worktree", "remove", "--force", str(wt)], ctx.repo, env)\n','    finally:\n'),
"no_detach":('"add", "--detach", str(wt)','"add", str(wt)'),
"no_prepr":('        runs = [("tools/pr/prepr.sh", ["bash", "tools/pr/prepr.sh", "--self-test"])]\n','        runs = []\n'),
"remember_on_wt_fail":('        if rc != 0:\n            return write_job(ctx, "darwin-selftest",\n                             [f"darwin-selftest: UNREADABLE worktree','        if rc != 0:\n            ctx.remember("darwin-selftest.json", {"tip": tip})\n            return write_job(ctx, "darwin-selftest",\n                             [f"darwin-selftest: UNREADABLE worktree'),
"no_take":('    rc, _, err = ctx.run([*gate, "slot-take"','    rc, _, err = (lambda *a: (0,"",""))([*gate, "slot-take"'),
"slot_rc_ignored":('    if rc != 0:  # no lease','    if False:  # no lease'),
}
name=sys.argv[1]; p=pathlib.Path(sys.argv[2]); s=p.read_text(); a,b=M[name]
assert s.count(a)==1,(name,s.count(a)); p.write_text(s.replace(a,b))
