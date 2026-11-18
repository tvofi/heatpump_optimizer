"""Game a1_params_over_10: every function over 10 parameters whose surplus is keyword-only gets
its keyword-only parameters replaced by ``**kw: Any`` and a prologue ``name = kw.get("name"[, default])``.
Callers are unchanged; the signature, its types and the unexpected-keyword check are gone."""
import ast, sys
from rt_lib import pkg, replace_nodes, seg
root = sys.argv[1]
n_fn = 0
for p in sorted(pkg(root).glob("*.py")):
    src = p.read_text()
    edits = []
    for fn in ast.walk(ast.parse(src)):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        a = fn.args
        pos = [x for x in a.posonlyargs + a.args if x.arg not in ("self", "cls")]
        if len(pos) + len(a.kwonlyargs) <= 10 or len(pos) > 10 or not a.kwonlyargs or a.kwarg or a.vararg:
            continue
        # signature: from the '*' marker's first kw-only param to the last one -> '**kw: Any'
        first, last = a.kwonlyargs[0], a.kwonlyargs[-1]
        lastd = a.kw_defaults[-1]
        end = lastd if lastd is not None else last
        span = type("S", (), {"lineno": first.lineno, "col_offset": first.col_offset,
                              "end_lineno": end.end_lineno, "end_col_offset": end.end_col_offset})
        body0 = fn.body[1] if (isinstance(fn.body[0], ast.Expr) and isinstance(fn.body[0].value, ast.Constant)
                               and len(fn.body) > 1) else fn.body[0]
        ind = " " * body0.col_offset
        pro = "".join(
            f'{ind}{k.arg} = kw.get("{k.arg}")\n' if d is None else f'{ind}{k.arg} = kw.get("{k.arg}", {seg(src, d)})\n'
            for k, d in zip(a.kwonlyargs, a.kw_defaults))
        at = type("S", (), {"lineno": body0.lineno, "col_offset": 0, "end_lineno": body0.lineno, "end_col_offset": 0})
        edits += [(span, "**kw: Any"), (at, pro)]
        n_fn += 1
    if edits:
        s = src
        replace_nodes(p, edits)
        import re
        p.write_text(re.sub(r"\*,\s*\*\*kw: Any", "**kw: Any", p.read_text()))
        if "Any" not in s.split("\nclass ")[0] and "import Any" not in s and ", Any" not in s:
            t = p.read_text()
            p.write_text(t.replace("from __future__ import annotations\n", "from __future__ import annotations\n\nfrom typing import Any\n", 1))
print("functions", n_fn)
