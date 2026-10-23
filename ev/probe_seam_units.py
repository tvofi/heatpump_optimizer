"""Reviewer's probe (my own instrument, not the finder's nor the fixer's):
per-unit crossings counted by tests/structure.py's seam_metrics rule, so a
base/head diff names which units carry seam_cut_total's movement. Run from a
checkout root: python seam_units.py > out.json"""
import ast, sys, json
from collections import Counter, defaultdict
sys.path.insert(0, "tests")
import structure as S
pkg = S.Package(S.module_trees())
roles = S.CoordinatorRoles(pkg)
helpers = roles.coordinator_helpers()
cls = pkg.classes[(S.COORDINATOR_MODULE, S.COORDINATOR_CLASS_NAME)]
methods = {m.name: m for m in cls.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))}
units = {n: (f, S.SELF_ROOT) for n, f in methods.items()}; units.update(helpers)
helper_names = {k.split(".", 1)[1]: k for k in helpers}
seams = S.load_seam_map(); b = {n: seams[n] for n in units}
refs = []; owners = defaultdict(set); calls = []
for name, (fn, roots) in units.items():
    al, hops = S.state_root_bindings(fn, roots)
    for node in ast.walk(fn):
        if isinstance(node, ast.Attribute) and id(node) not in hops and S.is_state_root(node.value, al, roots) and node.attr not in methods:
            refs.append((name, node.attr))
            if isinstance(node.ctx, ast.Store): owners[node.attr].add(b[name])
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id in roots and node.func.attr in methods:
            calls.append((name, node.func.attr))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in helper_names and any(S.is_state_root(a, al, roots) for a in [*node.args, *(k.value for k in node.keywords)]):
            calls.append((name, helper_names[node.func.id]))
per = Counter()
for L in S.SEAM_LABELS:
    for u, a in refs:
        if (L in owners[a]) and b[u] != L: per[(L, u, "attr:" + a)] += 1
        elif (L not in owners[a]) and b[u] == L: per[(L, u, "attr:" + a)] += 1
    for u, v in calls:
        if (b[u] == L) != (b[v] == L): per[(L, u, "call:" + v)] += 1
print(json.dumps({"total": sum(per.values()), "rows": sorted([[*k, c] for k, c in per.items()])}))
