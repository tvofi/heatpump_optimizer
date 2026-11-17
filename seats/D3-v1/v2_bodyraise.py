#!/usr/bin/env python3
"""V2 (D3-v1): independent measure of D3-s2-01.
Metric: for a cell file, insert `raise RuntimeError("V2-BODY")` as the first
statement of EVERY function body (module-level code untouched: a pure
function-body-only edit); a script whose run still exits 0 cannot have its run
changed by any function-body edit of that cell (empirical over-approximation),
and `closure.py select --files CELL` must still select it.
Null control: the same scripts unmutated must exit 0.
Positive control: the same mutation on a cell the script does execute must fail it.
Run from a baseline worktree: PYTHONPATH=tests/hastub python3 v2_bodyraise.py CELL SCRIPT...
"""
import ast, os, subprocess, sys, shutil
from pathlib import Path
cell = Path(sys.argv[1]); scripts = sys.argv[2:]
src = cell.read_text(); tree = ast.parse(src); lines = src.splitlines(True)
ins = []
for n in ast.walk(tree):
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
        b = n.body[0]
        if isinstance(b, ast.Expr) and isinstance(getattr(b, "value", None), ast.Constant) and isinstance(b.value.value, str) and len(n.body) > 1:
            b = n.body[1]
        ins.append((b.lineno, b.col_offset))
for ln, col in sorted(ins, reverse=True):
    lines.insert(ln - 1, " " * col + "raise RuntimeError('V2-BODY')\n")
print(f"RESULT functions_mutated={len(ins)}")
env = dict(os.environ, PYTHONPATH="tests/hastub")
sel = subprocess.run([sys.executable, "tests/closure.py", "select", "--files", str(cell), "--json"], capture_output=True, text=True, env=env).stdout
def run(tag):
    out = {}
    for s in scripts:
        cmd = ["node", s] if s.endswith(".mjs") else [sys.executable, s]
        r = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=1800)
        out[s] = r.returncode
        print(f"{tag}\t{s}\trc={r.returncode}\tselected={s in sel}", flush=True)
    return out
if "--null" in sys.argv: scripts.remove("--null"); run("NULL"); sys.exit()
bak = src
try:
    cell.write_text("".join(lines)); m = run("MUT")
finally:
    cell.write_text(bak)
print(f"RESULT survive={sum(1 for v in m.values() if v == 0)} of {len(m)}")
print(f"RESULT load1={os.getloadavg()[0]:.2f} thread_factor=1.00")
