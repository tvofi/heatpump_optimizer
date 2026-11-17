import subprocess, sys, pathlib
wt = pathlib.Path(sys.argv[1])
M = [
 ("M6", "tools/plan/replan.py", "        bad += [f\"next round {plan['next_round']['round']}: {b}\" for b in check_plan(nxt)]", "        pass"),
 ("M15", "tools/plan/replan.py", '"beyond": len(later) - len(mine)}', '"beyond": 0}'),
 ("M16", "tools/plan/replan.py", "    except PlanError as exc:\n        out[\"unavailable\"] = str(exc)", "    except ZeroDivisionError as exc:\n        out[\"unavailable\"] = str(exc)"),
 ("MW", "tools/plan/replan.py", '"carry_provenance", "phase_hours")', '"carry_provenance")'),
 ("MP1", "tools/audit/seat/plan_page.py", 'phase_hours=model.get("phase_hours")', 'phase_hours=None'),
 ("MD", "tools/plan/replan.py", "**{k: durations[k] for k in MODEL_FIELDS if k in durations},", "**{k: durations[k] for k in MODEL_FIELDS if k in durations and k != 'phase_hours'},"),
]
for name, f, a, b in M:
    p = wt / f; src = p.read_text()
    n = src.count(a)
    if n != 1:
        print(f"{name}: SITE-COUNT {n} (not applied)"); continue
    p.write_text(src.replace(a, b))
    try:
        res = []
        for s in ("tools/audit/seat/plan_page.py", "tools/plan/replan.py"):
            r = subprocess.run(["python3", s, "--self-test"], cwd=wt, capture_output=True, text=True,
                               env={"PYTHONPATH": "tests/hastub", "PATH": "/opt/hpo/venv-ci/bin:/usr/bin:/bin"}, timeout=600)
            out = r.stdout + r.stderr
            fails = [l for l in out.splitlines() if "FAIL" in l][:3]
            res.append(f"{s} rc={r.returncode} {out.strip().splitlines()[-1] if out.strip() else ''} {fails}")
        killed = any(" rc=0 " not in x for x in res)
        print(f"{name}: {'KILLED' if killed else 'SURVIVED'}"); [print("   ", x) for x in res]
    finally:
        p.write_text(src)
