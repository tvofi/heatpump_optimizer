"""Reviewer round 3 (own harness): start-path shapes beyond the finder's start_path.py.
Each case: leftover spool, new entry flags; prints the start queue and drain_order of the same entries."""
import sys, tempfile, json
from pathlib import Path
sys.path.insert(0, "tools/audit/seat")
import merge_train as mt
CRIT = {3, 6}
def run(argv, cwd=None, stdin=None):
    return 0, ("cp" if int(argv[3]) in CRIT else "plain") + "\n"
def case(name, left, new, front=False):
    with tempfile.TemporaryDirectory() as dd:
        st = Path(dd)
        t = mt.Train("o/r", st, None, "", (), 1, run=run, log=lambda m: None, critical=lambda it: it["branch"] == "cp")
        t.admit_add = lambda item: None
        mt.spool_rewrite(st, [json.dumps(e) for e in left])
        got = {}
        def launch(argv, state):
            got["q"] = json.loads(Path(argv[argv.index("--queue") + 1]).read_text()); return 4242, ""
        rc = mt.train_add(t, new, ["train.sh"], launch=launch, settle=0, front=front)
        q = got.get("q", [])
        print(f"RESULT {name}: rc={rc} start={[e['pr'] for e in q]} drain_of_same={[e['pr'] for e in t.drain_order(q)]} spool_after={[e['pr'] for e in mt.spool_read(st)[0]]}")
v = lambda n, **k: {"pr": n, "verdict": str(n % 10) * 40, **k}
case("several leftovers, plain add", [v(1), v(3), v(2), v(6)], v(4))
case("several leftovers, --priority add", [v(1), v(3), v(2), v(6)], v(4, priority=True))
case("leftover HOTFIX + --priority add (arrival within tier)", [v(1), v(5, priority=True), v(3)], v(4, priority=True))
case("leftover fronted + --priority add", [v(1, front=True), v(3), v(2)], v(4, priority=True))
case("--front --priority over leftover HOTFIX", [v(1), v(5, priority=True), v(3)], v(4, priority=True), front=True)
case("--front over leftover fronted", [v(1, front=True), v(3)], v(4), front=True)
case("--front of a leftover entry (no live train)", [v(1), v(3), v(2)], v(2), front=True)
case("empty spool, --priority", [], v(4, priority=True))
