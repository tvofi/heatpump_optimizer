import subprocess, sys, pathlib
W = pathlib.Path(sys.argv[1])
PP = "tools/audit/seat/plan_page.py"; RL="tools/audit/seat/roster_lib.py"; RP="tools/plan/replan.py"; PH="tools/audit/seat/plan_phases.py"; BJ="tools/audit/seat/beat_jobs.py"
M = [
 ("M1 round_roster dropped", PP, "roster = roster_lib.round_roster(roster, round_n) if later else roster", "roster = roster", [PP]),
 ("M2 part predicate", PP, "part = [] if g in done else sorted(delivered.get(g) or [])", "part = sorted(delivered.get(g) or [])", [PP]),
 ("M3 later-edge refusal", RP, "if n not in later and a:", "if False:", [PP, RP]),
 ("M4 model_duration guard", PH, "if isinstance(h, bool) or not isinstance(h, (int, float)) or h <= 0:", "if False:", [PP, PH]),
 ("M5 evidence flags", BJ, "            evidence += [flag, str(ctx.overlay[key])]", "            pass", [BJ]),
 ("M6 check_plan recursion", RP, "        bad += [f\"next round {plan['next_round']['round']}: {b}\" for b in check_plan(nxt)]", "        pass", [PP, RP]),
 ("M7 after filter kept all", RP, "\"after\": [a for a in g.get(\"after\") or [] if a in mine]}", "\"after\": list(g.get(\"after\") or [])}", [PP, RP]),
 ("M8 next starts at plan start", RP, "out[\"plan\"] = build_plan(sub, durations, caps, at,", "out[\"plan\"] = build_plan(sub, durations, caps, dt.datetime.strptime(plan[\"generated\"][\"start\"], \"%Y-%m-%dT%H:%M:%SZ\"),", [PP, RP]),
 ("M9 later uses >=", RL, "if (r := group_round(n)) is not None and r > round_n}", "if (r := group_round(n)) is not None and r >= round_n}", [PP, RP]),
 ("M10 list marker not stripped", RL, "    text = re.sub(r\"\\A\\s*(?:\\d+[.)]|[-*])[ \\t]+\", \"\", text)\n", "", [PP]),
 ("M11 heading not cut to line", RL, "text = re.sub(r\"\\A\\s*#{1,6}[ \\t]*\", \"\", text).split(\"\\n\", 1)[0]", "text = re.sub(r\"\\A\\s*#{1,6}[ \\t]*\", \"\", text)", [PP]),
 ("M12 snap issues not filtered", PP, "    if theirs - mine:\n        snap =", "    if False:\n        snap =", [PP]),
 ("M13 part flag false", PP, "\"part\": bool(part),", "\"part\": False,", [PP]),
 ("M14 tabbed ignores next_round", PP, "tabbed = bool(later and plan.get(\"next_round\"))", "tabbed = bool(later)", [PP]),
 ("M15 beyond zero", RP, "\"beyond\": len(later) - len(mine)}", "\"beyond\": 0}", [PP, RP]),
 ("M16 unavailable not caught", RP, "    except PlanError as exc:\n        out[\"unavailable\"] = str(exc)", "    except ZeroDivisionError as exc:\n        out[\"unavailable\"] = str(exc)", [PP, RP]),
]
for name, f, old, new, tests in M:
    p = W / f; src = p.read_text()
    if src.count(old) != 1:
        print(f"{name}: ANCHOR {src.count(old)} -- not applied"); continue
    p.write_text(src.replace(old, new))
    try:
        res = []
        for t in tests:
            r = subprocess.run(["python3", t, "--self-test"], cwd=W, env={"PYTHONPATH": "tests/hastub", "PATH": "/opt/hpo/venv-ci/bin:/usr/bin:/bin"}, capture_output=True, text=True, timeout=600)
            out = (r.stdout + r.stderr)
            fails = [l for l in out.splitlines() if "FAIL" in l or "Error" in l][:2]
            res.append(f"{t.split('/')[-1]} rc={r.returncode} {out.strip().splitlines()[-1][:120] if out.strip() else ''} | {' / '.join(x[:160] for x in fails)}")
        killed = any(" rc=0 " not in x for x in res)
        print(f"{name}: {'KILLED' if killed else 'SURVIVED'} :: " + " ;; ".join(res), flush=True)
    finally:
        p.write_text(src)
