"""Same delay-only plant at the head's equivalent point: after the slot's one
read finds it missing (read_text raises FileNotFoundError), sleep 30 ms, no
logic changed. Also keeps the original _read_at plant. argv: <worktree> <N>"""
import sys, os, importlib.util, time
from pathlib import Path
wt, n = sys.argv[1], int(sys.argv[2])
spec = importlib.util.spec_from_file_location("gl_mod", os.path.join(wt, "tests/gate_lock.py"))
g = importlib.util.module_from_spec(spec); sys.modules["gl_mod"] = g; spec.loader.exec_module(g)
real_rt, real_at = Path.read_text, g._read_at
def rt(self, *a, **k):
    try:
        return real_rt(self, *a, **k)
    except FileNotFoundError:
        if self.name.startswith(g.SLOT_PREFIX):
            time.sleep(0.03)
        raise
def at(path):
    o = real_at(path)
    if o is None and path.name.startswith(g.SLOT_PREFIX):
        time.sleep(0.03)
    return o
Path.read_text = rt; g._read_at = at
bad, det = 0, []
for i in range(n):
    for name, ok, d in g._priority_cases(g):
        if name.startswith("concurrency control: two waiters") and not ok:
            bad += 1; det.append(d)
print(f"RESULT one_winner widened-TOCTOU(head-point) wt={os.path.basename(wt)} red {bad} of {n}")
for d in det[:3]: print("  ", d)
