#!/usr/bin/env python3
"""Enumerator for class N-move-stale-path (round 10, D14 steps 3-4).

A seam is an executable reference from a tracked .py/.sh/.mjs file to a
repository path: (a) a sibling-module import enabled by
sys.path.insert(dirname(__file__)), and (b) a string literal spelling a
repo-relative file path under a top-level tracked directory. The seam is an
INSTANCE when the referenced module/file does not exist in the tree.

Usage: enumerate.py [ROOT]  (ROOT defaults to git toplevel; a fixture dir works)
Prints one TSV line per broken seam, then `seams=<N> broken=<M>`.
Comments and docstring-only lines (prose) are excluded: prose drift is I5.
"""
import ast, os, re, subprocess, sys

root = sys.argv[1] if len(sys.argv) > 1 else subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True).strip()
try:
    files = subprocess.check_output(["git", "-C", root, "ls-files"], text=True).split()
except subprocess.CalledProcessError:
    files = [os.path.relpath(os.path.join(d, f), root)
             for d, _, fs in os.walk(root) for f in fs]
files = [f for f in files if f.endswith((".py", ".sh", ".mjs"))
         and not f.startswith("dev/audit/rounds/round10/D14/sweep-")]
tops = {f.split("/")[0] for f in files} | {"tools", "dev", "tests", "custom_components", ".claude", ".github"}
PATH_RE = re.compile(r"""["']((?:%s)/[A-Za-z0-9_./-]+\.(?:py|sh|mjs|json|md|txt|yml|yaml|tsv))["']"""
                     % "|".join(re.escape(t) for t in sorted(tops) if t and not t.startswith(".git")))
stdlib = set(sys.stdlib_module_names)
seams, broken = 0, []
try:
    _all = subprocess.check_output(["git", "-C", root, "ls-files"], text=True).split()
except subprocess.CalledProcessError:
    _all = [os.path.relpath(os.path.join(d, f), root) for d, _, fs in os.walk(root) for f in fs]
BASES = {}
for _p in _all:
    BASES.setdefault(os.path.basename(_p), []).append(_p)


def moved(name):
    """A seam is in this class only when its target's basename lives elsewhere."""
    return BASES.get(name, [])


def exists(p):
    return os.path.exists(os.path.join(root, p))


for f in files:
    try:
        src = open(os.path.join(root, f), encoding="utf-8").read()
    except (OSError, UnicodeDecodeError):
        continue
    code_lines = src.splitlines()
    if f.endswith(".py"):
        try:
            tree = ast.parse(src)
        except SyntaxError:
            tree = None
        if tree is not None and re.search(r"sys\.path\.insert\(0,\s*os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\)", src):
            here = os.path.dirname(f)
            for node in ast.walk(tree):
                mods = []
                if isinstance(node, ast.Import):
                    mods = [a.name.split(".")[0] for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    mods = [node.module.split(".")[0]]
                for m in mods:
                    if m in stdlib:
                        continue
                    seams += 1
                    cand = [os.path.join(here, m + ".py"), os.path.join(here, m, "__init__.py")]
                    if any(exists(c) for c in cand):
                        continue
                    if moved(m + ".py"):
                        broken.append((f, node.lineno, "import", m, ",".join(moved(m + ".py"))))
        # string literals in code (skip docstrings/comments via ast)
        if tree is not None:
            doc_ids = set()
            for n in ast.walk(tree):
                if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    d = n.body[0] if n.body else None
                    if isinstance(d, ast.Expr) and isinstance(getattr(d, "value", None), ast.Constant):
                        doc_ids.add(id(d.value))
            for n in ast.walk(tree):
                if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in doc_ids:
                    for m in PATH_RE.finditer(repr(n.value) if "'" not in n.value else '"%s"' % n.value):
                        p = m.group(1)
                        if any(c in p for c in "*{<"):
                            continue
                        seams += 1
                        if not exists(p) and moved(os.path.basename(p)):
                            broken.append((f, n.lineno, "path", p, ",".join(moved(os.path.basename(p)))))
    else:
        for i, line in enumerate(code_lines, 1):
            s = line.strip()
            if s.startswith(("#", "//", "*")):
                continue
            for m in PATH_RE.finditer(line):
                p = m.group(1)
                if any(c in p for c in "*{<$"):
                    continue
                seams += 1
                if not exists(p) and moved(os.path.basename(p)):
                    broken.append((f, i, "path", p, ",".join(moved(os.path.basename(p)))))

for b in broken:
    print("\t".join(map(str, b)))
print(f"seams={seams} broken={len(broken)}")
