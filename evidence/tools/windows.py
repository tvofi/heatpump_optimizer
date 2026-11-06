"""Reviewer's own plants (not the finder's): deterministic hooks at each window
of _free_slot's broken-slot path. argv: <worktree>"""
import sys, os, importlib.util, tempfile
from pathlib import Path
wt = sys.argv[1]
spec = importlib.util.spec_from_file_location("gl_mod", os.path.join(wt, "tests/gate_lock.py"))
g = importlib.util.module_from_spec(spec); sys.modules["gl_mod"] = g; spec.loader.exec_module(g)
real_rt, real_rename, real_unlink = Path.read_text, os.rename, Path.unlink

def setup():
    d = Path(tempfile.mkdtemp()); pool = g.pool_dir(d); g._ensure_lock_dir(pool)
    path = g._slot_path(pool, 0); path.write_text("garbage\n"); return pool, path

def run(name, pool, path, after_read=None, after_rename=None, before_unlink=None):
    fired = []
    def rt(self, *a, **k):
        t = real_rt(self, *a, **k)
        if self == path and after_read and "r" not in fired:
            fired.append("r"); after_read()
        return t
    def rn(src, dst, *a, **k):
        r = real_rename(src, dst, *a, **k)
        if Path(src) == path and after_rename and "n" not in fired:
            fired.append("n"); after_rename()
        return r
    def ul(self, *a, **k):
        if self == path and before_unlink and "u" not in fired:
            fired.append("u"); before_unlink()
        return real_unlink(self, *a, **k)
    Path.read_text, Path.unlink = rt, ul; g.os.rename = rn
    try:
        free = g._free_slot(pool, 1)
    finally:
        Path.read_text, Path.unlink = real_rt, real_unlink; g.os.rename = real_rename
    kept = g._read_at(path)
    print(f"RESULT {name} wt={os.path.basename(wt)} fired={fired} free={free} slot_owner={kept.label if kept else None}")
    return kept

# baseline: broken slot is reclaimed (free index, file gone so a create wins)
pool, path = setup()
run("broken-reclaimed", pool, path)
print(f"   then create wins: {g._new_owner('x',60,os.getpid()).create(path)}")

# W2: valid owner C replaces the broken file between the read and the reap
pool, path = setup()
def c_lands():
    real_unlink(path); g._new_owner("C", 60, os.getpid()).create(path)
k = run("W2 valid-owner-lands-after-broken-read", pool, path, after_read=c_lands)
print(f"   C kept: {k is not None and k.label=='C'}")

# W3: C landed (as W2) and D creates in the gap between _steal's rename and its link-back
pool, path = setup()
def d_creates():
    print(f"   D create in gap: {g._new_owner('D', 60, os.getpid()).create(path)}")
k = run("W3 fourth-taker-in-rename-gap", pool, path, after_read=c_lands, after_rename=d_creates)
print(f"   C kept: {k is not None and k.label=='C'}  (C believes it holds slot 0)")

# W5: the broken slot is removed between read and reap
pool, path = setup()
run("W5 removed-after-broken-read", pool, path, after_read=lambda: real_unlink(path))
