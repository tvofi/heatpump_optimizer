#!/usr/bin/env python3
"""R10-FLY-RAISE-REVIEWABLE (#3073 round 1, class-open): approval_owed over-fire census.

Drives <checkout>/tools/audit/seat/merge_train.py's `classify --pr 3045` CLI over
#3045's shape (gate and budget-raise-gate failed, one unheld raise, the owner's
approval on an older head) plus one extra unit per case, with every read stubbed
the way the self-test's `owed_cli` stubs it. The fix reviewer's probe
(verdict/3073 evidence/overfire.py) planted the same runs; this companion also
answers the gate job's log with the reasons gate.py prints for that shape
(tools/ci/gate.py `gate()`: a non-success unit, ABSENT, PENDING), so a checkout
that reads why `gate` is red is measured on the same input as one that does not.

    python3 dev/audit/harnesses/r10_fly_raise_reviewable_overfire.py <checkout>

Prints one `RESULT <case>: rc=<n> <STATE>` line per case. Expected at a checkout
that reads the gate's reasons: the control and the two designed owed shapes
(an older approval; a red that is no gate unit) rc=4, every other case rc=1.
"""
import contextlib
import datetime
import io
import json
import sys

sys.path.insert(0, sys.argv[1] + "/tools/audit/seat")
import merge_train as mt  # noqa: E402

_g, owner_rv, mandate_c, _rv = mt.policy_fixture_builders()
OLD, BASE = "d" * 40, "e" * 40
now = datetime.datetime.now(datetime.timezone.utc)
G, R = mt.GATE, mt.RAISE_GATE
OWN = f"{R}: failure (this run)"


def cr(name, status="completed", conclusion="success"):
    return {"name": name, "status": status, "started_at": "1", "id": 1, "details_url": "",
            "conclusion": conclusion if status == "completed" else None}


def glog(reasons):
    ts = "2026-10-31T21:40:02.5110117Z "
    lines = ['##[group]Run python3 -I tools/ci/gate.py --pr "$PR" --base "$BASE" --kind "$KIND"', "##[endgroup]",
             *(("FAIL " if i == 0 else "") + r for i, r in enumerate(reasons)),
             "##[error]Process completed with exit code 1."]
    return "".join(ts + x + "\n" for x in lines)


def run(runs, files, why, budgets=mt.RAISE_FIXTURE, reviews=None, body="## Summary\n", flags=("--pr", "3045")):
    def fake_run(argv, cwd=mt.ROOT, stdin=None):
        a = " ".join(argv)
        if "/actions/jobs/" in a and a.endswith("/logs"):
            return 0, glog(why)
        if "check-runs" in a:
            return 0, "\n".join(json.dumps(c) for c in runs)
        if a.endswith("rulesets --jq " + argv[-1]):
            return 0, "7"
        if "rulesets/7" in a:
            return 0, "gate\n"
        if argv[:2] == ["git", "merge-base"]:
            return 0, BASE + "\n"
        if argv[:4] == ["git", "diff", "--no-renames", "--name-only"]:
            return 0, "".join(f + "\n" for f in files)
        got = mt.budget_fixture(budgets, argv, BASE)
        if got is not None:
            return got
        if "/reviews" in a:
            return 0, json.dumps([reviews if reviews is not None else [owner_rv(OLD, now)]])
        if argv[:3] == ["gh", "pr", "view"]:
            return 0, body
        if "issues/comments/" in a:
            return 0, json.dumps(mandate_c(now))
        if "/comments" in a:
            return 0, json.dumps([[]])
        return 1, "unexpected " + a
    saved, buf = mt.Train._run, io.StringIO()
    mt.Train._run = staticmethod(fake_run)
    try:
        with contextlib.redirect_stdout(buf):
            rc = mt.main(["classify", "a" * 40, *flags])
    finally:
        mt.Train._run = saved
    return rc, (buf.getvalue().split() or ["?"])[0]


base = [cr(G, conclusion="failure"), cr(R, conclusion="failure"), cr("tests / fast (3.14)"),
        cr("pr-contract / pr-contract")]
F = ["tests/structure_budgets.json", "tools/x.py"]
cases = [
    ("control #3045 shape", base, F, [OWN], {}),
    ("null: red head not a raise (no budget file)", base, ["tools/x.py"], [OWN], {"budgets": None}),
    ("null: raise + tests/fast red", base[:2] + [cr("tests / fast (3.14)", conclusion="failure")], F,
     [OWN, "tests / fast (3.14): failure (this run)"], {}),
    ("null: raise + tests/fast cancelled", base[:2] + [cr("tests / fast (3.14)", conclusion="cancelled")], F,
     [OWN, "tests / fast (3.14): cancelled (this run)"], {}),
    ("null: approval at the head (held)", base, F, [OWN], {"reviews": [owner_rv("a" * 40, now)], "body": mt.JUSTIFIED_BODY}),
    ("designed owed: approval at an older head", base, F, [OWN], {}),
    ("null: gate red, raise unit green", [base[0], cr(R), *base[2:]], F, ["pr-contract / pr-contract: failure (run 7)"], {}),
    ("designed owed: a non-gate red (governance / instrument-self-tests) + raise",
     base + [cr("governance / instrument-self-tests", conclusion="failure")], F, [OWN], {}),
    ("hidden: gate red because tests / browser SKIPPED", base + [cr("tests / browser", conclusion="skipped")], F,
     [OWN, "tests / browser: SKIPPED (this run)"], {}),
    ("hidden: gate red because a unit is ABSENT", base, F, [OWN, "tests / arch-instrument: ABSENT (this run)"], {}),
    ("hidden: gate red because a unit is still in_progress", base + [cr("tests / browser", "in_progress")], F,
     [OWN, "tests / browser: PENDING (this run)"], {}),
    ("hidden: gate red for a reason naming no unit (deferral)", base, F,
     ["run(s) [99] at this head are still being judged past the bound"], {}),
]
for label, runs, files, why, kw in cases:
    rc, state = run(runs, files, why, **kw)
    print(f"RESULT {label}: rc={rc} {state}")
rc, state = run(base, F, [OWN], flags=())
print(f"RESULT no --pr: rc={rc} {state}")
