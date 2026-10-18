"""Reviewer-built: a run stuck in flight for 10h on main, closures never queued; every MAIN line."""
import importlib.util, json, sys, datetime
root = sys.argv[1]
spec = importlib.util.spec_from_file_location("ot", f"{root}/tools/audit/seat/orchestrator_tick.py")
ot = importlib.util.module_from_spec(spec); sys.modules["ot"] = ot; spec.loader.exec_module(ot)
H = "a" * 40
old = ot.NOW - datetime.timedelta(hours=10)
rs = [ot.run_obj("tests"), ot.run_obj("mutation", status="in_progress", conclusion=None, started=old)]
gh = ot.Stub(); gh.on("commits/main", out=H)
gh.on(".[] | select(.name", out="42"); gh.on("rulesets/42", out="tests\nclosures\n")
gh.on(f"commits/{H}/check-runs", out="\n".join(json.dumps(r) for r in rs))
t = ot.Tick("o/r", root, gh=gh, git=ot.Stub(), proc=ot.Stub(), now=ot.NOW)
t.main()
for l in t.sections.get("MAIN", []):
    if "main " in l["text"][:5] or "required" in l["text"] or "mutation" in l["text"]:
        print(f"RESULT {'FLAG' if l.get('flag') else 'line'}: {l['text'][:150]}")
