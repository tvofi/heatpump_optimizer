"""Reviewer's own extra mutants (not the fixer's list), run through the fixer harness's one()."""
import importlib.util, sys, concurrent.futures
spec = importlib.util.spec_from_file_location("h", "dev/audit/harnesses/r10_train_overlap_grade_p2_mutants.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
X = [
 ("X1", "fallback: an old-code train's queue.pending.json read as pending",
  '        return {str(int(n)): {"state": "pending"} for n in json.loads((state / QUEUE_PENDING).read_text())}',
  '        return {}'),
 ("X2", "_batch overlap recarry filter: this batch's skips only",
  '                todo = [a for a in serial if a["pr"] not in {s["pr"] for s in self.skipped[mine:]}',
  '                todo = [a for a in serial if a["pr"] not in {s["pr"] for s in self.skipped}'),
 ("X3", "a completed batch's unmerged/unskipped entries marked ran",
  '                        self.seen_mark(int(e["pr"]), "ran")', '                        pass'),
 ("X4", "skip row carries the verdict",
  '"verdict": (getattr(self, "_seen", {}).get(str(pr)) or {}).get("verdict")}', '"verdict": None}'),
 ("X5", "queue.pending.json lists pending only",
  'for n, r in seen.items() if r.get("state") == "pending")', 'for n, r in seen.items())'),
 ("X6", "seen_mark only writes for the owning pid",
  '            if read_pid(self.state / QUEUE_OPEN) == os.getpid():\n                queue_seen_write(self.state, self._seen)',
  '            if True:\n                queue_seen_write(self.state, self._seen)'),
 ("X7", "queue_take adds fresh entry to the record as pending",
  '                self._seen[str(int(e["pr"]))] = {"verdict": e.get("verdict"), "state": "pending"}', '                pass'),
]
h.MUTANTS += X
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
    for mid, state, fails in ex.map(h.one, X):
        print(f"{mid} {state}: {next(a for i,a,_o,_n in X if i==mid)}")
        for f in fails[:4]: print("    " + f[:200])
