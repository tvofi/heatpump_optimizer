import sys, shutil, tempfile
from pathlib import Path
root = Path(sys.argv[1]).resolve(); out = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(root / "tools/ci"))
import selftest_scope as s
s.ROOT = root
keep = []
orig_mk = tempfile.mkdtemp
def mk(*a, **k):
    d = orig_mk(*a, **k); keep.append(d); print("TRACE-TMP", d, flush=True); return d
s.tempfile.mkdtemp = mk
s.shutil.rmtree = lambda p, *a, **k: print("KEPT", p, flush=True)
rc = s.record(root, None, out)
print("RECORD-RC", rc, flush=True)
