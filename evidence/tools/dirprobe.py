"""Reviewer-built: directory/symlink slot plants against _steal's rmtree branch. argv: <worktree>"""
import sys, os, importlib.util, tempfile
from pathlib import Path
wt = sys.argv[1]
spec = importlib.util.spec_from_file_location("gl_mod", os.path.join(wt, "tests/gate_lock.py"))
g = importlib.util.module_from_spec(spec); sys.modules["gl_mod"] = g; spec.loader.exec_module(g)
real_rt = Path.read_text
def pool():
    d = Path(tempfile.mkdtemp()); p = g.pool_dir(d); g._ensure_lock_dir(p); return p, g._slot_path(p, 0)
def free(p):
    try: return g._free_slot(p, 1)
    except Exception as e: return f"raised {e!r}"
def tag(): return os.getpid()
# D1 empty dir
p, s = pool(); s.mkdir(); f = free(p)
print(f"RESULT D1 empty-dir wt={os.path.basename(wt)} free={f} create={g._new_owner('t',60,tag()).create(s)} graves={len(list(p.glob('stale-*')))}")
# D2 non-empty dir (hand-made, with a file inside)
p, s = pool(); s.mkdir(); (s/'x').write_text('data'); f = free(p)
print(f"RESULT D2 nonempty-dir wt={os.path.basename(wt)} free={f} create={g._new_owner('t',60,tag()).create(s)} graves={len(list(p.glob('stale-*')))}")
# D3 symlink at slot -> outside dir with content: target must survive
p, s = pool(); tgt = Path(tempfile.mkdtemp()); (tgt/'keep').write_text('precious'); s.symlink_to(tgt); f = free(p)
print(f"RESULT D3 symlink-to-dir wt={os.path.basename(wt)} free={f} target_intact={(tgt/'keep').exists()} create={g._new_owner('t',60,tag()).create(s)} graves={[x.name[:5]+('(link)' if x.is_symlink() else '') for x in p.glob('stale-*')]}")
# D4 dir replaced by valid owner C between the read and the reap: C must survive
p, s = pool(); s.mkdir(); fired=[]
def rt(self, *a, **k):
    try: return real_rt(self, *a, **k)
    finally:
        if self == s and not fired:
            fired.append(1); s.rmdir(); g._new_owner('C',60,tag()).create(s)
Path.read_text = rt
try: f = free(p)
finally: Path.read_text = real_rt
k = g._read_at(s)
print(f"RESULT D4 dir-replaced-by-owner wt={os.path.basename(wt)} fired={bool(fired)} free={f} owner={k.label if k else None} graves={len(list(p.glob('stale-*')))}")
# D5 orphaned-owner steal (seen=Owner) unaffected: a dead-pid owner is reaped as file
p, s = pool(); g._new_owner('dead',60,2**22-3).create(s); f = free(p)
print(f"RESULT D5 orphan-file-steal wt={os.path.basename(wt)} free={f} gone={not s.exists()} graves={len(list(p.glob('stale-*')))}")
