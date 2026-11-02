"""Reviewer's own harness: main's `add --front` (P112) against this PR's drain_order (P312).
Spool [3 (critical), 1, 2]; `add --front 1` writes 1 first; then the train drains."""
import sys, tempfile, json
from pathlib import Path
sys.path.insert(0, "tools/audit/seat")
import merge_train as mt
heads = {1: "plain", 2: "plain", 3: "cp"}
def run(argv, cwd=None, stdin=None):
    return 0, heads[int(argv[3])] + "\n"
with tempfile.TemporaryDirectory() as dd:
    st = Path(dd)
    t = mt.Train("o/r", st, None, "", (), 1, run=run, log=lambda m: print("LOG", m), critical=lambda it: it["branch"] == "cp")
    mt.spool_rewrite(st, [json.dumps({"pr": n, "verdict": v*40}) for n, v in ((3,"a"),(1,"b"),(2,"c"))])
    rc = mt.spool_edit_locked(t, 1, "front")
    spooled, _ = mt.spool_read(st)
    print("RESULT front_rc", rc, "spool_after_front", [e["pr"] for e in spooled])
    print("RESULT drained", [e["pr"] for e in t.drain_order(spooled)])
    # null control: nothing critical -> --front holds
    t2 = mt.Train("o/r", st, None, "", (), 1, run=run, log=lambda m: None, critical=lambda it: False)
    print("RESULT null_drained", [e["pr"] for e in t2.drain_order(spooled)])
