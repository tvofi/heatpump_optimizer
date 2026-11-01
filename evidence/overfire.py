# Reviewer's own over-fire probe for approval_owed (not the fixer's harness).
import contextlib, datetime, io, json, sys
sys.path.insert(0, sys.argv[1] + "/tools/audit/seat")
import merge_train as mt
_g, owner_rv, mandate_c, _rv = mt.policy_fixture_builders()
OLD, BASE = "d"*40, "e"*40
now = datetime.datetime.now(datetime.timezone.utc)
def cr(name, status="completed", conclusion="success"):
    return {"name": name, "status": status, "started_at": "1", "id": 1, "details_url": "",
            "conclusion": conclusion if status == "completed" else None}
def run(runs, files, budgets=mt.RAISE_FIXTURE, reviews=None, body="## Summary\n", merge_base=BASE, flags=("--pr","3045")):
    def fake_run(argv, cwd=mt.ROOT, stdin=None):
        a = " ".join(argv)
        if "check-runs" in a: return 0, "\n".join(json.dumps(c) for c in runs)
        if a.endswith("rulesets --jq " + argv[-1]): return 0, "7"
        if "rulesets/7" in a: return 0, "gate\n"
        if argv[:2] == ["git","merge-base"]: return 0, merge_base + "\n"
        if argv[:4] == ["git","diff","--no-renames","--name-only"]: return 0, "".join(f+"\n" for f in files)
        got = mt.budget_fixture(budgets, argv, BASE)
        if got is not None: return got
        if "/reviews" in a: return 0, json.dumps([reviews if reviews is not None else [owner_rv(OLD, now)]])
        if argv[:3] == ["gh","pr","view"]: return 0, body
        if "issues/comments/" in a: return 0, json.dumps(mandate_c(now))
        if "/comments" in a: return 0, json.dumps([[]])
        return 1, "unexpected " + a
    saved, buf = mt.Train._run, io.StringIO()
    mt.Train._run = staticmethod(fake_run)
    try:
        with contextlib.redirect_stdout(buf): rc = mt.main(["classify", "a"*40, *flags])
    finally: mt.Train._run = saved
    return rc, buf.getvalue().strip()
G, R = mt.GATE, mt.RAISE_GATE
base = [cr(G, conclusion="failure"), cr(R, conclusion="failure"), cr("tests / fast (3.14)"), cr("pr-contract / pr-contract")]
F = ["tests/structure_budgets.json", "tools/x.py"]
cases = [
 ("control #3045 shape", base, F, {}),
 ("null: red head not a raise (no budget file)", base, ["tools/x.py"], {"budgets": None}),
 ("null: raise + tests/fast red", base[:2]+[cr("tests / fast (3.14)", conclusion="failure")], F, {}),
 ("null: raise + another unit red (tests / browser)", base+[cr("tests / browser", conclusion="failure")], F, {}),
 ("null: raise + tests/fast cancelled", base[:2]+[cr("tests / fast (3.14)", conclusion="cancelled")], F, {}),
 ("null: approval at the head (held)", base, F, {"reviews":[owner_rv("a"*40, now)], "body": mt.JUSTIFIED_BODY}),
 ("null: approval at an older head", base, F, {"reviews":[owner_rv(OLD, now)]}),
 ("null: gate red, raise unit green", [cr(G, conclusion="failure"), cr(R)], F, {}),
 ("null: non-gate-unit red (governance / instrument-self-tests) + raise", base+[cr("governance / instrument-self-tests", conclusion="failure")], F, {}),
 ("hidden: gate red because tests / browser SKIPPED (gate.py fails skipped; merge_train reads skipped green)", base+[cr("tests / browser", conclusion="skipped")], F, {}),
 ("hidden: gate red because a unit is ABSENT (no check run)", base, F, {}),
 ("hidden: gate red because a unit still in_progress", base+[cr("tests / browser", status="in_progress")], F, {}),
 ("no --pr", base, F, {"flags": ()}),
]
for label, runs, files, kw in cases:
    rc, out = run(runs, files, **kw)
    print(f"RESULT {label}: rc={rc} {out.split(' ')[0]}")
