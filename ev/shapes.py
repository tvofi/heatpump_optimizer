"""Reviewer's own harness (round 2): ordering shapes on a LIVE train's spool, read-back vs drain.
Spool [#3 critical, #1, #2]; queue.open holds this pid so train_add takes the live path."""
import sys, tempfile, json, os, io, contextlib
from pathlib import Path
sys.path.insert(0, "tools/audit/seat")
import merge_train as mt
def run(argv, cwd=None, stdin=None):
    return 0, ("cp" if argv[3] == "3" else "plain") + "\n"
def world():
    st = Path(tempfile.mkdtemp())
    t = mt.Train("o/r", st, None, "", (), 1, run=run, log=lambda m: None, critical=lambda it: it["branch"] == "cp")
    t.admit_add = lambda item: None
    (st / mt.QUEUE_OPEN).write_text(f"{os.getpid()}\n")
    mt.spool_rewrite(st, [json.dumps({"pr": n, "verdict": str(n) * 40}) for n in (3, 1, 2)])
    return st, t
def show(name, st, t):
    sp = [e["pr"] for e in mt.spool_read(st)[0]]
    print(f"RESULT {name}: spool_read_back={sp} drained={[e['pr'] for e in t.drain_order(mt.spool_read(st)[0])]}")
st, t = world(); mt.spool_edit_locked(t, 1, "front"); mt.spool_edit_locked(t, 2, "front"); show("two fronted (1 then 2)", st, t)
st, t = world(); mt.train_add(t, {"pr": 5, "verdict": "5"*40, "priority": True}, ["x"], front=True); show("new #5 --front --priority", st, t)
st, t = world(); mt.spool_edit_locked(t, 1, "front"); mt.spool_edit_locked(t, 1, "remove"); show("front 1 then remove 1", st, t)
st, t = world(); mt.spool_edit_locked(t, 1, "front"); mt.train_add(t, {"pr": 5, "verdict": "5"*40, "priority": True}, ["x"]); show("front 1 then add #5 --priority", st, t)
st, t = world(); mt.train_add(t, {"pr": 5, "verdict": "5"*40}, ["x"], front=True); mt.spool_edit_locked(t, 2, "front"); show("new #5 --front then front 2", st, t)
st, t = world(); show("null: nothing fronted", st, t)
