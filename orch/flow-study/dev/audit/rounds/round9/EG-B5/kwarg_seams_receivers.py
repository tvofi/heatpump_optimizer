"""#1747's kwarg-seam enumerator (tools/audit/round9/rca/1747/kwarg_seams.py) with the
receiver widened from `self` to `self` and `planner`: after #1743 the two DHW builds are
`planner._build_dhw_requirements(...)`, which the original no longer sees. Run over one or more
files; a method is keyed by name across them. Usage: python kwarg_seams_receivers.py <file.py>..."""
import ast, sys
RECEIVERS = ("self", "planner")
trees = [ast.parse(open(f).read()) for f in sys.argv[1:]]
defaults = {}
for node in (n for tree in trees for n in ast.walk(tree)):
    if isinstance(node, ast.FunctionDef):
        a = node.args
        pos = a.args[len(a.args) - len(a.defaults):] if a.defaults else []
        kws = [k.arg for k, d in zip(a.kwonlyargs, a.kw_defaults) if d is not None]
        defaults.setdefault(node.name, set()).update([p.arg for p in pos] + kws)
calls = {}
for node in (n for tree in trees for n in ast.walk(tree)):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id in RECEIVERS:
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
