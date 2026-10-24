"""KNOWN-OPEN: a copy split across blocks, each statement in its own always-true if (the R9-EG-A2 round-3 review's probe). Every statement of every block of each
clone after the first is wrapped in its own `if <fid>:` (always true, distinct per function), so no two
statements of a copy share a block. Same owners as 04 (coordinator and footprint-charged skipped)."""
import ast, sys
from collections import defaultdict
from rt_lib import pkg, structure, metric
root = sys.argv[1]
CHARGED = {c.rsplit(":", 1)[0] for c in metric("footprint", root)["charged"]}
S = structure(root)
import hashlib
win = defaultdict(set)
fnode = {}
for path, tree in S.module_trees():
    mname = path.stem
    modalias = S._module_aliases(tree)
    for fn in S.all_functions(tree):
        local = S._local_names(fn)
        for node in ast.walk(fn):
            if node is not fn and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
                continue
            for f in ("body", "orelse", "finalbody"):
                b = getattr(node, f, None)
                if not (isinstance(b, list) and b and isinstance(b[0], ast.stmt)): continue
                b = [s for s in b if not S._is_docstring(s)]
                for i in range(len(b) - 1):
                    w = b[i:i + 2]
                    if any(isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) for s in w): continue
                    if sum(1 for s in w for _ in ast.walk(s)) < S.DUP_MIN_NODES: continue
                    key = hashlib.sha1(S.normalized_window(w, local, modalias).encode()).hexdigest()
                    owner = (mname, fn.name, fn.lineno)
                    win[key].add(owner); fnode[owner] = fn
targets = {}
for key, owners in win.items():
    for owner in sorted(owners)[1:]:
        if owner[0].startswith("coordinator") or f"{owner[0]}.{owner[1]}" in CHARGED: continue
        targets[owner] = fnode[owner]
fid = 0
wraps = defaultdict(list)  # module -> [(lineno, end_lineno, col, fid)]
for owner, fn in targets.items():
    fid += 1
    lines_seen = set()
    for node in ast.walk(fn):
        if node is not fn and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)): continue
        for f in ("body", "orelse", "finalbody"):
            b = getattr(node, f, None)
            if not (isinstance(b, list) and b and isinstance(b[0], ast.stmt)): continue
            if f == "orelse" and isinstance(node, ast.If) and len(b) == 1 and isinstance(b[0], ast.If) \
                    and b[0].col_offset == node.col_offset:
                continue  # an elif
            for s in b:
                if S._is_docstring(s) or isinstance(s, ast.Match) or isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Global, ast.Nonlocal)):
                    continue
                wraps[owner[0]].append((s.lineno, s.end_lineno, s.col_offset, fid))
n = 0
for mname, ws in wraps.items():
    p = pkg(root) / (mname + ".py")
    lines = p.read_text().splitlines(keepends=True)
    src = "".join(lines)
    # indent innermost-first is unnecessary: indent every line of each wrapped statement once per wrap
    add = defaultdict(int); ins = defaultdict(list)
    for lo, hi, col, f in ws:
        seg = "".join(lines[lo - 1:hi])
        if '"""' in seg or "'''" in seg: continue
        for k in range(lo, hi + 1): add[k] += 1
        ins[lo].append((col, f))
    out = []
    for k, line in enumerate(lines, 1):
        for col, f in sorted(ins.get(k, []), key=lambda t: t[0]):
            depth = sum(1 for c2, _ in ins[k] if c2 < col)
            out.append(" " * (col + 4 * (add[k] - len(ins[k]) + depth)) + f"if {f}:\n")
            n += 1
        out.append((" " * (4 * add[k]) + line) if line.strip() else line)
    p.write_text("".join(out))
print("functions wrapped", len(targets), "wraps", n)
