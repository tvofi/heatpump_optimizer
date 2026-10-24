"""Reviewer-built probe (rebuild of round 1's out-of-tree ev/unleased_probe.py):
a writer re-marks one label N times while a reader polls _unleased; count polls
missing the live marker. --null: no rewrites, reader polls the same span."""
import os, sys, tempfile, threading, importlib.util
from pathlib import Path
tree, mode = Path(sys.argv[1]), sys.argv[2]
sys.path.insert(0, str(tree / "tests" / "hastub"))
spec = importlib.util.spec_from_file_location("gl", tree / "tests" / "gate_lock.py")
g = importlib.util.module_from_spec(spec); sys.modules["gl"] = g; spec.loader.exec_module(g)
d = Path(tempfile.mkdtemp()); pool = g.pool_dir(d)
g.mark_unleased("probe", lock_dir=d, pid=os.getpid())
stop, lost, polls = threading.Event(), [0], [0]
def reader():
    while not stop.is_set():
        polls[0] += 1
        if "probe" not in g._unleased(pool): lost[0] += 1
t = threading.Thread(target=reader, daemon=True); t.start()
N = 4000
for _ in range(N):
    if mode == "null":
        g._marker_path(pool, "probe").read_text()
    else:
        g.mark_unleased("probe", lock_dir=d, pid=os.getpid())
stop.set(); t.join(20)
print(f"RESULT tree={tree.name} mode={mode} lost={lost[0]} polls={polls[0]} rewrites={N if mode!='null' else 0}")
