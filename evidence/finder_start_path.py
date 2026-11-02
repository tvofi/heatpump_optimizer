"""Reviewer's own harness (round 2): the HOTFIX/--front rule on train_add's START path.
No live train; a stopped train left [#3 critical, #1] spooled; `add #4 --priority` starts a train.
Prints the queue file train.sh would be launched over, and what drain_order says for the same entries."""
import sys, tempfile, json
from pathlib import Path
sys.path.insert(0, "tools/audit/seat")
import merge_train as mt
def run(argv, cwd=None, stdin=None):
    return 0, ("cp" if argv[3] == "3" else "plain") + "\n"
for flag in ("priority", "front", "none"):
    with tempfile.TemporaryDirectory() as dd:
        st = Path(dd)
        t = mt.Train("o/r", st, None, "", (), 1, run=run, log=lambda m: print("LOG", m),
                     critical=lambda it: it["branch"] == "cp")
        t.admit_add = lambda item: None
        mt.spool_rewrite(st, [json.dumps({"pr": n, "verdict": str(n) * 40}) for n in (3, 1)])
        got = {}
        def launch(argv, state):
            got["q"] = json.loads(Path(argv[argv.index("--queue") + 1]).read_text()); return 4242, ""
        item = {"pr": 4, "verdict": "4" * 40, **({"priority": True} if flag == "priority" else {})}
        rc = mt.train_add(t, item, ["train.sh"], launch=launch, settle=0, front=(flag == "front"))
        q = [e["pr"] for e in got.get("q", [])]
        print(f"RESULT {flag}: rc={rc} start_queue={q} drain_order_of_same={[e['pr'] for e in t.drain_order(got.get('q', []))]}")
