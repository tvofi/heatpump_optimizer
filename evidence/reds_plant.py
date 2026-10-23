"""Reviewer-built: reds_at_head under plants the self-test does not carry (offline FakeGh)."""
import sys, json; sys.path.insert(0, sys.argv[1]); import ruleset_cutover as rc
H = "e" * 40
def runs(named):
    return {"total_count": len(named), "check_runs": [{"id": 910000+i, "name": n, "head_sha": H, "status": "completed",
        "conclusion": c, "app": {"id": 15368}, "check_suite": {"id": 710000+i}} for i, (n, c) in enumerate(named)]}
def gh_for(named):
    return lambda args, stdin=None: (0, json.dumps(runs(named)))
three = [("governance / policy-docs", "failure"), ("governance / env-matrix", "failure"), ("governance / wave-script", "failure"), ("gate", "failure")]
cases = {
 "null: the window (fast green, three base-pinned red, gate red)": [("tests / fast (3.14)", "success")] + three,
 "plant: the whole tests unit skipped (caller check skipped, no tests / * at all)": [("tests", "skipped")] + three,
 "plant: tests / closures skipped": [("tests / fast (3.14)", "success"), ("tests / closures", "skipped")] + three,
 "plant: only the three base-pinned and gate exist (every other unit absent)": three,
 "plant: codeql / Analyze (python) neutral": [("codeql / Analyze (python)", "neutral")] + three,
 "control: tests / closures cancelled": [("tests / closures", "cancelled")] + three,
}
for k, v in cases.items():
    ok, d = rc.reds_at_head(gh_for(v), H)
    print(f"RESULT reds-at-head {'PASS' if ok else 'FAIL'} :: {k} :: {d}")
