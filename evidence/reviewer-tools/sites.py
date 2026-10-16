import sys
from pathlib import Path
root = Path(sys.argv[1]); sys.path.insert(0, str(root / "tools/audit"))
from archscore.metrics import common as C, hub_solve_writes as H
def run(ev):
    H.EVENT_ROOTS = ev; C.reset_caches() if hasattr(C,"reset_caches") else None; C.load.cache_clear()
    pkg = C.load(root); eng = C.engine(pkg); s=set()
    for q in H.roots(pkg): s |= {x[:4] for x in H._sites(eng, q)}
    return s, H.event_roots(pkg)
on, er = run(True); off, _ = run(False)
print("event_roots:", [q.rsplit(".",1)[-1] for q in er])
print("RESULT sites on", len(on), "off", len(off))
for x in sorted(on - off): print("DELTA", x)
print("removed", sorted(off - on))
