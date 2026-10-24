# Reviewer-built probe (not the finder's): does _unleased destroy a marker that
# mark_unleased is mid-writing (write_text truncates/creates before it writes)?
import sys, os, threading, tempfile
from pathlib import Path
sys.path.insert(0, sys.argv[1] + "/tests")
import gate_lock as g
d = Path(tempfile.mkdtemp())
pool = g.pool_dir(d)
lost, stop = [0], threading.Event()
def reader():
    while not stop.is_set():
        g._unleased(pool) if pool.exists() else None
t = threading.Thread(target=reader, daemon=True); t.start()
for _ in range(4000):
    p = g.mark_unleased("seat", lock_dir=d)
    if not p.exists():
        lost[0] += 1
stop.set(); t.join(20)
# deterministic arm: an empty marker (the write_text window) with nothing else
p = g._marker_path(pool, "seat2"); p.write_text("")
g._unleased(pool)
print(f"RESULT unleased-torn: markers lost right after mark_unleased={lost[0]} of 4000; empty marker survives _unleased={p.exists()}")
