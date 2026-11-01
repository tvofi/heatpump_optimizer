# Round-2 reviewer's extension of the round-1 finder's overfire.py (verdict/3073 evidence/overfire.py):
# the same cases, plus a gate job log carrying the reasons tools/ci/gate.py prints for each shape,
# plus every other gate.py FAIL path. Reviewer-built; not the fixer's harness.
import contextlib, datetime, io, json, sys
sys.path.insert(0, sys.argv[1] + "/tools/audit/seat")
import merge_train as mt
_g, owner_rv, mandate_c, _rv = mt.policy_fixture_builders()
OLD, BASE = "d"*40, "e"*40
now = datetime.datetime.now(datetime.timezone.utc)
def cr(name, status="completed", conclusion="success"):
    return {"name": name, "status": status, "started_at": "1", "id": 1, "details_url": "",
            "conclusion": conclusion if status == "completed" else None}
def glog(reasons, rate=False):
    ts = "2026-11-01T10:00:00.1234567Z "
    L = ["##[group]Run python3 -I tools/ci/gate.py --pr 1", "##[endgroup]"]
    L += ([f"RATE-LIMITED reset_epoch=1 x", "::error title=RATE-LIMITED::reset_epoch=1"] if rate else [("FAIL " if i == 0 else "") + r for i, r in enumerate(reasons)])
    L += ["##[error]Process completed with exit code 1."]
    return "".join(ts + x + "\n" for x in L)
RR = "budget-raise-gate / budget-raise-gate: failure (this run)"
def run(runs, files, budgets=mt.RAISE_FIXTURE, reviews=None, body="## Summary\n", merge_base=BASE, flags=("--pr","3045"), why=(RR,), rate=False, log_rc=0):
    def fake_run(argv, cwd=mt.ROOT, stdin=None):
        a = " ".join(argv)
        if "/actions/jobs/" in a and a.endswith("/logs"): return (log_rc, glog(why, rate)) if log_rc == 0 else (log_rc, "HTTP 410")
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
RB = "tests / browser: SKIPPED (this run)"
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
 ("hidden: gate red because tests / browser SKIPPED (gate.py fails skipped; merge_train reads skipped green)", base+[cr("tests / browser", conclusion="skipped")], F, {"why": (RR, "tests / browser: SKIPPED (this run)")}),
 ("hidden: gate red because a unit is ABSENT (no check run)", base, F, {"why": (RR, "tests / arch-instrument: ABSENT (this run)")}),
 ("hidden: gate red because a unit still in_progress", base+[cr("tests / browser", status="in_progress")], F, {"why": (RR, "tests / browser: PENDING (this run)")}),
 ("no --pr", base, F, {"flags": ()}),
 ("gate.py: prelude not success", base, F, {"why": ("prelude: failure",)}),
 ("gate.py: prelude cross-check", base, F, {"why": ("prelude says kind=code pr='', the event says kind=code pr='3045'",)}),
 ("gate.py: attempt cap", base, F, {"why": ("attempt 45 of this run is at the cap (45): push a new commit",)}),
 ("gate.py: dispatch pr mismatch", base, F, {"why": ("dispatch pr=3045 does not name the open PR headed by this SHA",)}),
 ("gate.py: dispatch open-PR head", base, F, {"why": ("this SHA heads an open PR: dispatch with -f pr=N -f base=REF",)}),
 ("gate.py: PR unreadable", base, F, {"why": ("PR 3045 could not be read",)}),
 ("gate.py: fork head", base, F, {"why": ("PR 3045: its head is not in this repository (a fork PR is not gated here)",)}),
 ("gate.py: deferral bound", base, F, {"why": ("run(s) [99] at this head are still being judged; their gate decides",)}),
 ("gate.py: unreadable title + raise", base, F, {"why": (RR, "run 5: unreadable title 'x'")}),
 ("gate.py: unit no run judged base + raise", base, F, {"why": (RR, "tests: no run at this head judged base 'main'")}),
 ("gate.py: ApiError", base, F, {"why": ("repos/x/pulls/1: HTTP 502",)}),
 ("gate.py: raise unit cancelled", base, F, {"why": ("budget-raise-gate / budget-raise-gate: cancelled (this run)",)}),
 ("gate.py: raise unit SKIPPED", base, F, {"why": ("budget-raise-gate / budget-raise-gate: SKIPPED (this run)",)}),
 ("gate.py: raise first, other unit failure later run", base, F, {"why": (RR, "tests / fast: failure (run 7)")}),
 ("gate.py: other first, raise second", base, F, {"why": ("tests / fast: failure (run 7)", RR)}),
 ("gate.py: RATE-LIMITED", base, F, {"rate": True}),
 ("gate log unreadable (410)", base, F, {"log_rc": 1}),
 ("gate log: raise in earlier run id", base, F, {"why": ("budget-raise-gate / budget-raise-gate: failure (run 123)",)}),
 ("gate log: reason with trailing junk", base, F, {"why": (RR + " x",)}),
]
for label, runs, files, kw in cases:
    rc, out = run(runs, files, **kw)
    print(f"RESULT {label}: rc={rc} {out.split(' ')[0]}")
