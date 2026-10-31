"""Class enumerator for #1747: self.<method>(...) called from two or more sites in one
module, where a keyword the method defaults is passed at one site and omitted at another.
Usage: python kwarg_seams.py <file.py> ; prints one SEAM line per (method, omitted kw, site)."""
import ast, sys
src = open(sys.argv[1]).read(); tree = ast.parse(src)
defaults = {}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        a = node.args
        pos = a.args[len(a.args) - len(a.defaults):] if a.defaults else []
        kws = [k.arg for k, d in zip(a.kwonlyargs, a.kw_defaults) if d is not None]
        defaults.setdefault(node.name, set()).update([p.arg for p in pos] + kws)
calls = {}
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "self":
        if any(k.arg is None for k in node.keywords):
            continue
        calls.setdefault(node.func.attr, []).append((node.lineno, {k.arg for k in node.keywords}))
n = 0
for m, sites in sorted(calls.items()):
    if len(sites) < 2 or m not in defaults:
        continue
    union = set().union(*(s for _, s in sites)) & defaults[m]
    for line, s in sites:
        for kw in sorted(union - s):
            n += 1; print(f"SEAM {m} omits {kw} at line {line} (passed at {[l for l, t in sites if kw in t]})")
print(f"RESULT seams={n}")
