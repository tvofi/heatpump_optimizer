"""Reviewer-built harness (not the finder's; none is committed): the #3248 gate-race
scene against a tree's Train.wait_ci. argv: <tree> <scene>. scene: race | null."""
import json, sys, tempfile
from pathlib import Path
tree = Path(sys.argv[1]); scene = sys.argv[2]
sys.path.insert(0, str(tree / "tests/hastub")); sys.path.insert(0, str(tree / "tools/audit/seat"))
import merge_train as m
H = "e" * 40
eg = {"name": "gate", "status": "completed", "conclusion": "failure", "started_at": "2026-11-06T14:55:00Z", "id": 1, "check_suite": {"id": 11}}
green = dict(eg, conclusion="success", started_at="2026-11-06T15:26:00Z", id=3)
cg = {"name": "gate", "status": "completed", "conclusion": "success", "started_at": "2026-11-06T15:25:00Z", "id": 2, "check_suite": {"id": 22}}
busy = "42237558473\tin_progress\n42237558635\tcompleted\n"; done = "42237558473\tcompleted\n42237558635\tcompleted\n"
if scene == "race":
    checks, sibs = [[eg], [eg], [green, cg]], [busy, done, done]
else:  # null: no sibling unfinished, the red is final
    checks, sibs = [[eg]], [done]
n = {"cr": 0, "sb": 0}
def run(argv, cwd=None, stdin=None, **kw):
    a = " ".join(argv)
    if "check-runs" in a:
        c = checks[min(n["cr"], len(checks) - 1)]; n["cr"] += 1
        return 0, "\n".join(json.dumps(x) for x in c)
    if "actions/runs?head_sha=" in a:
        s = sibs[min(n["sb"], len(sibs) - 1)]; n["sb"] += 1
        return 0, s
    return 0, ""
with tempfile.TemporaryDirectory() as d:
    t = m.Train("o/r", Path(d), None, "", (), 1, run=run, sleep=lambda s: None, log=lambda s: None, polls=5)
    red = t.wait_ci(H, only=[m.GATE])
print(f"RESULT scene={scene} red={red} checkrun_polls={n['cr']} sibling_reads={n['sb']}")
