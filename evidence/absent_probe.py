"""Reviewer-built probe (not the finder's; the finding has no committed harness
beyond --self-test). Drives the PRS and MAIN arms with stubbed check runs.
usage: absent_probe.py <checkout>"""
import importlib.util, json, sys
root = sys.argv[1]
spec = importlib.util.spec_from_file_location("ot", f"{root}/tools/audit/seat/orchestrator_tick.py")
ot = importlib.util.module_from_spec(spec); sys.modules["ot"] = ot; spec.loader.exec_module(ot)
H = "a" * 40
def runs(*rs): return "\n".join(json.dumps(r) for r in rs)
def main_arm(rs):
    gh = ot.Stub(); gh.on("commits/main", out=H)
    gh.on(".[] | select(.name", out="42"); gh.on("rulesets/42", out="tests\nclosures\n")
    gh.on(f"commits/{H}/check-runs", out=runs(*rs))
    t = ot.Tick("o/r", root, gh=gh, git=ot.Stub(), proc=ot.Stub(), now=ot.NOW)
    try: t.main()
    except Exception as e: print("  (main raised", type(e).__name__, str(e)[:80], ")")
    return [(l["text"], bool(l.get("flag"))) for l in t.sections.get("MAIN", []) if "required contexts" in l["text"]]
def pr_arm(rs):
    gh = ot.Stub(); gh.on(f"commits/{H}/check-runs", out=runs(*rs))
    t = ot.Tick("o/r", root, gh=gh, git=ot.Stub(), proc=ot.Stub(), now=ot.NOW)
    t.sections.setdefault("PRS", [])
    try: t.one_pr("PRS", ot.pr_obj(17, H), None, ["tests", "closures"])
    except Exception as e: print("  (one_pr raised", type(e).__name__, str(e)[:80], ")")
    return [(l["text"], bool(l.get("flag"))) for l in t.sections.get("PRS", []) if "required contexts" in l["text"]]
R = ot.run_obj
cases = {
 "A unrelated lane in flight, closures never queued": [R("tests"), R("mutation", status="in_progress", conclusion=None)],
 "B everything settled, closures never queued":       [R("tests"), R("mutation")],
 "C needs-gated: coverage queued, closures no run":   [R("tests"), R("coverage", status="queued", conclusion=None)],
 "D closures itself queued (has a check run)":        [R("tests"), R("closures", status="queued", conclusion=None)],
}
for k, rs in cases.items():
    for arm, fn in (("PRS", pr_arm), ("MAIN", main_arm)):
        out = fn(rs)
        verdict = ("ABSENT" if any("ABSENT" in t for t, _ in out) else
                   "WAITING" if any("WAITING" in t for t, _ in out) else "none")
        flag = any(f for _, f in out)
        print(f"RESULT {arm:4} {k}: {verdict} flag={flag}")
