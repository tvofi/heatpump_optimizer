import subprocess, sys, pathlib
F = pathlib.Path("tools/audit/seat/beat_jobs.py"); orig = F.read_text()
M = {
 "no_per_run_remember": ('            ctx.remember("darwin-selftest.json", mem)  # after every run', '            pass  # after every run'),
 "red_carried_to_next_cycle": ('mem = {"tip": tip, "done": [], "red": [], "complete": False}', 'mem = {"tip": tip, "done": [], "red": mem.get("red", []), "complete": False}'),
 "done_carried_to_next_cycle": ('mem = {"tip": tip, "done": [], "red": [], "complete": False}', 'mem = {"tip": tip, "done": mem.get("done", []), "red": [], "complete": False}'),
 "no_stale_wt_remove": ('        ctx.run(["git", "-C", str(ctx.repo), "worktree", "remove", "--force", str(wt)], ctx.repo, env)  # a killed', '        pass  # a killed'),
 "budget_gt": ("if ctx.clock() - start >= DARWIN_PASS_BUDGET_S:", "if ctx.clock() - start > DARWIN_PASS_BUDGET_S:"),
 "complete_default_false": ('if mem.get("complete", True):', 'if mem.get("complete", False):'),
 "no_final_remember": ('    ctx.remember("darwin-selftest.json", mem)\n    if mem["complete"]:', '    pass\n    if mem["complete"]:'),
}
for k,(a,b) in M.items():
    n = orig.count(a)
    if n != 1: print(k, "ANCHOR", n); continue
    F.write_text(orig.replace(a,b))
    p = subprocess.run([sys.executable,"-I",str(F),"--self-test","--no-mutants"],capture_output=True,text=True)
    fails=[l.strip() for l in p.stdout.splitlines() if l.strip().startswith("FAIL")]
    print(k, "rc=%d"%p.returncode, "KILLED" if p.returncode else "SURVIVED", fails[:2])
F.write_text(orig)
