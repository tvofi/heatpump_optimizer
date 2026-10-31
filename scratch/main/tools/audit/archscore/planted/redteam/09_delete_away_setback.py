"""Known limit: delete working functionality. The away setback envelope is gutted:
apply_setback no longer lowers any target (it returns the originals), lower_floor
(economy / open-window relax) and restore_setback do nothing. Every away entity, option
and service still exists and still reports "away" -- the house just is not set back."""
import ast, sys
from rt_lib import pkg, replace_nodes
root = sys.argv[1]
p = pkg(root) / "away.py"
src = p.read_text()
tree = ast.parse(src)
new_body = {
    "apply_setback": ["original = SetbackRecord(_setback_fields(opt_config, thermal_params))",
                      "original.written = dict(original)", "return original"],
    "lower_floor": ["return None"],
    "restore_setback": ["return None"],
}
edits = []
for fn in tree.body:
    if isinstance(fn, ast.FunctionDef) and fn.name in new_body:
        body = [s for s in fn.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
        first, last = body[0], body[-1]
        span = ast.Module(body=[], type_ignores=[])
        node = type("S", (), {"lineno": first.lineno, "col_offset": first.col_offset,
                              "end_lineno": last.end_lineno, "end_col_offset": last.end_col_offset})
        ind = " " * first.col_offset
        edits.append((node, ("\n" + ind).join(new_body[fn.name])))
print("gutted", replace_nodes(p, edits))
