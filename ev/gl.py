"""Reviewer's harness: repeat gate_lock's _priority_cases N times; count one_winner reds.
argv: <worktree> <N> [planted]  planted = O_EXCL-then-write create (pre-fab4a07c1 shape)."""
import sys, os, importlib.util, time
wt, n = sys.argv[1], int(sys.argv[2]); planted = len(sys.argv) > 3
sys.path.insert(0, os.path.join(wt, "tests"))
spec = importlib.util.spec_from_file_location("gl_mod", os.path.join(wt, "tests/gate_lock.py"))
g = importlib.util.module_from_spec(spec); sys.modules["gl_mod"] = g; spec.loader.exec_module(g)
if planted:
    def create(self, path):
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except (FileExistsError, FileNotFoundError):
            return False
        time.sleep(0.002)  # widen the torn window (the planted defect)
        with os.fdopen(fd, "w") as f:
            f.write(self._text())
        return True
    g.Owner.create = create
bad, details, t0 = 0, [], time.time()
for i in range(n):
    for name, ok, det in g._priority_cases(g):
        if name.startswith("concurrency control: two waiters"):
            if not ok:
                bad += 1; details.append(det)
print(f"RESULT one_winner wt={os.path.basename(wt)} planted={planted} red {bad} of {n} wall={time.time()-t0:.0f}s")
for d in details[:5]: print("  ", d)
