import subprocess, sys, os
wt = sys.argv[1]
os.chdir(wt)
env = dict(os.environ, PYTHONPATH="tests/hastub")
M = [
 ("M1-unwire", "tools/plan/replan.py", '"carry_provenance", "phase_hours")', '"carry_provenance")'),
 ("M6-recursion", "tools/plan/replan.py", "bad += [f\"next round {plan['next_round']['round']}: {b}\" for b in check_plan(nxt)]", "pass"),
 ("M16-except", "tools/plan/replan.py", "    except PlanError as exc:\n        out[\"unavailable\"]", "    except ZeroDivisionError as exc:\n        out[\"unavailable\"]"),
 ("M15-beyond", "tools/plan/replan.py", '"beyond": len(later) - len(mine)}', '"beyond": 0}'),
 ("M17-page-handoff", "tools/audit/seat/plan_page.py", 'phase_hours=model.get("phase_hours")', 'phase_hours=None'),
]
cmds = [["python3","tools/audit/seat/plan_page.py","--self-test"],["python3","tools/plan/replan.py","--self-test"]]
for name, path, old, new in M:
    src = open(path).read()
    assert src.count(old) == 1, (name, src.count(old))
    open(path,"w").write(src.replace(old,new))
    try:
        res = []
        for c in cmds:
            p = subprocess.run(c, env=env, capture_output=True, text=True)
            fails = [l for l in (p.stdout+p.stderr).splitlines() if "FAIL" in l][:4]
            res.append((c[1], p.returncode, fails))
        killed = any(r[1] != 0 for r in res)
        print(f"{name}: {'KILLED' if killed else 'SURVIVED'}")
        for r in res: print("   ", r[0], "rc", r[1], *("\n      "+f for f in r[2]))
    finally:
        open(path,"w").write(src)
print("worktree diff after restore:", subprocess.run(["git","status","--porcelain"],capture_output=True,text=True).stdout or "clean")
