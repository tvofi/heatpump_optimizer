"""Reviewer's own probe (not the finder's): planted cases the RO-1 self-test lacks,
run against layout.py as committed and against mutants M, N, C, G."""
import json, subprocess, sys, tempfile, types, shutil
from pathlib import Path
SRC = Path("/home/claude/wt-head/tests/layout.py").read_text()
MUT = {
 "head": (None, None),
 "M * crosses dirs": ('out += "[^/]*"\n            i += 1', 'out += ".*"\n            i += 1'),
 "N since!=null skipped": ('if not under(p, r["old"]):', 'if not under(p, r["old"]) or r.get("since"):'),
 "C dir-dot form dropped": (r'(?=/|\.(?!\w)|[^\w./-]|\Z)', r'(?=/|[^\w./-]|\Z)'),
}
def mod(name):
    a, b = MUT[name]; src = SRC if a is None else SRC.replace(a, b)
    m = types.ModuleType("layout"); m.__file__ = "/home/claude/wt-head/tests/layout.py"; exec(compile(src, "layout", "exec"), m.__dict__); return m
root = Path("/home/claude/wt-head")
manifest = json.loads((root / "tests/layout.json").read_text())
L0 = mod("head")
moved = next(r for r in manifest["retired"] if r["new"] and not r["old"].endswith("/"))
mdir = next(r for r in manifest["retired"] if r["new"] and r["old"].endswith("/"))
def run(L, files, m):
    tmp = Path(tempfile.mkdtemp())
    try:
        for p, t in files.items():
            (tmp / p).parent.mkdir(parents=True, exist_ok=True); (tmp / p).write_text(t)
        (tmp / "tests/layout.json").parent.mkdir(parents=True, exist_ok=True)
        (tmp / "tests/layout.json").write_text(json.dumps(m))
        subprocess.run(["git", "init", "-q"], cwd=tmp, check=True); subprocess.run(["git", "add", "-A"], cwd=tmp, check=True)
        f, n = L.check(tmp, m); return tuple(len(f[a]) for a in L.ARMS)
    finally: shutil.rmtree(tmp)
m_since = json.loads(json.dumps(manifest))
for r in m_since["retired"]:
    if r["old"] == moved["old"]: r["since"] = 9999
cases = [
 ("P1 reintroduced after its move (since set)", {moved["old"]: ""}, m_since),
 ("P2 one level below a single-star glob", {".claude/rules/sub/x.md": ""}, manifest),
 ("P3 directory cited with a trailing full stop", {"README.md": f"moved from {mdir['old'][:-1]}.\n"}, manifest),
]
for name in MUT:
    L = mod(name)
    print(name + ":", "; ".join(f"{c[0]} -> {run(L, c[1], c[2])}" for c in cases))
print("control: moved =", moved["old"], "; dir =", mdir["old"])
