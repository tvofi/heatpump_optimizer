"""Reviewer's instrument (not the finder's): policy_refusal and classify readings of
a deferral gate red alone, and of a real red beside a deferral. Usage: --tree DIR"""
import argparse, importlib.util, json, sys
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument("--tree", required=True); a = ap.parse_args()
seat = Path(a.tree) / "tools/audit/seat"; sys.path.insert(0, str(seat))
spec = importlib.util.spec_from_file_location("mt", str(seat / "merge_train.py"))
mt = importlib.util.module_from_spec(spec); sys.modules["mt"] = mt; spec.loader.exec_module(mt)
H = "b" * 40
def jl(xs): return "\n".join(json.dumps(x) for x in xs)
def policy(rollup, runs, req):
    def run(argv, cwd=None, stdin=None):
        s = " ".join(argv)
        if "statusCheckRollup" in s:
            return 0, json.dumps({"mergeStateStatus": "BLOCKED", "reviewDecision": "APPROVED", "statusCheckRollup": rollup})
        if "actions/runs?head_sha=" in s:
            return 0, jl(runs)
        if "/reviews" in s: return 0, json.dumps([[]])
        return 0, ""
    t = mt.Train("o/r", Path("."), None, "", (), 1, run=run, sleep=lambda s: None, log=lambda s: None, polls=3, wall=lambda: 1e9)
    t.required = lambda pr_head=False: req
    return t.policy_refusal(1, H)
DEF = {"name": "gate", "conclusion": "FAILURE", "startedAt": "2026-11-12T09:55:01Z", "completedAt": "2026-11-12T09:55:49Z"}
REAL = {"name": "gate", "conclusion": "FAILURE", "startedAt": "2026-11-12T11:00:00Z", "completedAt": "2026-11-12T11:40:00Z"}
FAST = {"name": "tests / fast (3.14)", "conclusion": "FAILURE", "completedAt": "2026-11-12T10:10:00Z"}
CODE_Q = {"id": 43195308607, "name": "CI code", "status": "queued"}
CODE_IP = {"id": 43195308607, "name": "CI code", "status": "in_progress", "run_started_at": "2026-11-12T10:00:00Z"}
OTHER = {"id": 9, "name": "codeql", "status": "in_progress", "run_started_at": "2026-11-12T11:00:00Z"}
cases = [
 ("A deferral alone: gate FAILURE, code run queued", [DEF], [CODE_Q], ["gate"]),
 ("A deferral alone: gate FAILURE, code run in_progress", [DEF], [CODE_IP], ["gate"]),
 ("NULL deferral read with no unfinished run: gate FAILURE alone, no runs", [DEF], [], ["gate"]),
 ("B real red beside deferral: second gate FAILURE (code run's, newer), only an unrelated workflow (codeql) unfinished", [DEF, REAL], [OTHER], ["gate"]),
 ("B' real gate red alone, unrelated workflow unfinished", [REAL], [OTHER], ["gate"]),
 ("C real red of another required context beside a deferral, code run in_progress", [DEF, FAST], [CODE_IP], ["gate", "tests / fast (3.14)"]),
 ("C' real red of another context, gate green", [{"name": "gate", "conclusion": "SUCCESS"}, FAST], [], ["gate", "tests / fast (3.14)"]),
]
for name, rollup, runs, req in cases:
    r = policy(rollup, runs, req)
    print(f"RESULT policy {name}: wait={r[1]} reason={r[0][:110]!r}")
# classify (the pure reading; busy stands for gate.py's busy over ci.yml runs)
lat = lambda *xs: {x["name"]: x for x in xs}
cr = lambda n, c: {"name": n, "status": "completed", "conclusion": c}
print("RESULT classify deferral alone, busy=[code]:", mt.classify(lat(cr("gate", "failure")), ["gate"], [43195308607]))
print("RESULT classify deferral alone, busy=():", mt.classify(lat(cr("gate", "failure")), ["gate"], ()))
print("RESULT classify fast red beside deferral, busy=[code]:", mt.classify(lat(cr("gate", "failure"), cr("tests / fast (3.14)", "failure")), ["gate", "tests / fast (3.14)"], [43195308607]))
