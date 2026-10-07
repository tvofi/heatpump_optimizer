"""Control for _P3_FILES gaining dhw_planner.py: the seam rule's own functions,
lifted from tests/features.py by AST, run with and without the module, on the
head's sources and on a copy with one planner call's humidity dropped."""
import ast, re
from pathlib import Path
src = Path("tests/features.py").read_text()
tree = ast.parse(src)
want = {"_p3_hum_pos", "_p3_is_none", "_p3_seams"}
ns = {"_p3_ast": ast}
for n in tree.body:
    if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in ("_P3_FUNCS", "_P3_FILES", "_P3_ALLOWED") for t in n.targets):
        exec(compile(ast.Module([n], []), "f", "exec"), ns)
for n in tree.body:
    if isinstance(n, ast.FunctionDef) and n.name in want:
        exec(compile(ast.Module([n], []), "f", "exec"), ns)
PKG = Path("custom_components/heatpump_optimizer")
files = ns["_P3_FILES"]
print("_P3_FILES:", files)
srcs = {f: (PKG / f).read_text() for f in files}
without = {f: s for f, s in srcs.items() if f != "dhw_planner.py"}
print("head, with dhw_planner.py:   open seams", len(ns["_p3_seams"](srcs)))
# perturb: drop the humidity keyword at the first planner call that passes it as a keyword
planner = srcs["dhw_planner.py"]
m = re.search(r"\n(\s+)humidity=humidity,\n", planner)
pert = planner[: m.start()] + "\n" + planner[m.end():]
print("perturbed line removed:", repr(m.group(0).strip()), "at dhw_planner.py line", planner[: m.start()].count("\n") + 2)
p_with = dict(srcs, **{"dhw_planner.py": pert})
print("perturbed, with dhw_planner.py:    open seams", ns["_p3_seams"](p_with))
p_without = {f: s for f, s in p_with.items() if f != "dhw_planner.py"}
print("perturbed, without dhw_planner.py: open seams", ns["_p3_seams"](p_without))
