"""Reviewer attempt (not the fixer's): rt_04 with `pass` in place of id(N); is_noop only drops ast.Expr.
first a no-op call statement id(<distinct int per function>) is inserted
between the window's two statements, so no window hashes equal any more.
The duplicated logic is untouched; only junk is added."""
import ast, hashlib, sys
from collections import defaultdict
from pathlib import Path
from rt_lib import pkg, structure
root = sys.argv[1]
S = structure(root)
win = defaultdict(set)
node_of = {}
for path, tree in S.module_trees():
    mname = path.stem
    modalias = S._module_aliases(tree)
    for fn in S.all_functions(tree):
        local = S._local_names(fn)
        for node in ast.walk(fn):
            if node is not fn and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
                continue
            blocks = [getattr(node, f) for f in ("body", "orelse", "finalbody")
                      if isinstance(getattr(node, f, None), list) and getattr(node, f)
                      and isinstance(getattr(node, f)[0], ast.stmt)]
            blocks += [h.body for h in getattr(node, "handlers", []) or []]
            for b in blocks:
                b = [s for s in b if not S._is_docstring(s)]
                for i in range(len(b) - S.DUP_WINDOW_STATEMENTS + 1):
                    w = b[i:i + S.DUP_WINDOW_STATEMENTS]
                    if any(isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) for s in w):
                        continue
                    if sum(1 for s in w for _ in ast.walk(s)) < S.DUP_MIN_NODES:
                        continue
                    key = hashlib.sha1(S.normalized_window(w, local, modalias).encode()).hexdigest()
                    owner = (mname, fn.name, fn.lineno)
                    win[key].add(owner)
                    node_of[(key, owner)] = w[0]
fn_ids: dict = {}
inserts = defaultdict(dict)  # module -> {line_after: (indent, owner)}
for key, owners in win.items():
    o = sorted(owners)
    for owner in o[1:]:
        s0 = node_of[(key, owner)]
        fid = fn_ids.setdefault(owner, len(fn_ids) + 1)
        inserts[owner[0]][s0.end_lineno] = (s0.col_offset, fid)
n = 0
for mname, ins in inserts.items():
    p = pkg(root) / (mname + ".py")
    lines = p.read_text().splitlines(keepends=True)
    for ln in sorted(ins, reverse=True):
        col, fid = ins[ln]
        lines.insert(ln, " " * col + "pass\n")
        n += 1
    p.write_text("".join(lines))
print("functions perturbed", len(fn_ids), "no-ops inserted", n)
