"""Reviewer's harness: widen _free_slot's window between _read_at's is_file()
(False -> None) and its own `if not path.is_file()` re-check, with NO change to
gate_lock's logic, then count one_winner reds. argv: <worktree> <N>"""
import sys, os, importlib.util, time
wt, n = sys.argv[1], int(sys.argv[2])
spec = importlib.util.spec_from_file_location("gl_mod", os.path.join(wt, "tests/gate_lock.py"))
g = importlib.util.module_from_spec(spec); sys.modules["gl_mod"] = g; spec.loader.exec_module(g)
real = g._read_at
def widened(path):
    o = real(path)
    if o is None and path.name.startswith(g.SLOT_PREFIX):
        time.sleep(0.03)   # only a delay: the rival's link can land here
    return o
g._read_at = widened
bad, det = 0, []
for i in range(n):
    for name, ok, d in g._priority_cases(g):
        if name.startswith("concurrency control: two waiters") and not ok:
            bad += 1; det.append(d)
print(f"RESULT one_winner widened-TOCTOU wt={os.path.basename(wt)} red {bad} of {n}")
for d in det[:3]: print("  ", d)
