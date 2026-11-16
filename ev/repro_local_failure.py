"""Reviewer's reproduction, round 2: a failure of the LOCAL file system during one extraction (stood in for by
one ENOSPC from Path.write_bytes) against a healthy archive, then a second, healthy pass."""
import errno, importlib, sys, tempfile
from pathlib import Path
sys.path.insert(0, "tools/audit/seat")
cm = importlib.import_module("corpus_mirror")
def mirror(root, s):
    mi = cm.Mirror(root, run=s.run, run_bytes=s.run_bytes, git=s.git, http=s.http, new_bare=s.new_bare, sleep=s.sleeps.append,
                   now=lambda: s.clock, repo="o/r", say=[].append)
    return mi, mi.scan(["S5"], "https://example.invalid/o/r", {})
for fail in (False, True):
    td, s = Path(tempfile.mkdtemp()), cm.Stub()
    real, state = Path.write_bytes, {"left": 1 if fail else 0}
    def wb(self, data, _real=real, _state=state):
        if _state["left"] and "/logs/901/" in str(self):
            _state["left"] -= 1
            raise OSError(errno.ENOSPC, "No space left on device")
        return _real(self, data)
    Path.write_bytes = wb
    try:
        m1, rc1 = mirror(td / "p", s)
        n1 = sum(1 for d in s.downloads if d.endswith("runs/901/logs"))
        m2, rc2 = mirror(td / "p", s)
        n2 = sum(1 for d in s.downloads if d.endswith("runs/901/logs"))
    finally:
        Path.write_bytes = real
    u = m2.man["sources"]["S5"]["units"]["run logs"]
    print(f"{'one ENOSPC while writing run 901' if fail else 'null control (no failure)'}: pass 1 rc {rc1}, pass 2 rc {rc2}; run 901 state after pass 2 "
          f"{m2.cur['items']['run logs']['901']!r}; downloads of its archive after pass 1 and 2: {n1}, {n2}; "
          f"pass 2 universe/examined {u['universe']}/{u['examined']}, not_reached lines naming it: {sum(1 for x in m2.man['sources']['S5']['not_reached'] if 'run logs 901' in x)}")
