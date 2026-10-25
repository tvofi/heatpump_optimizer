"""Reviewer's driver: head's tests/finite_boundary.py::_finite_float_coercers over a tree; --wide drops the module-level, arity and return-annotation filters."""
import ast, sys, pathlib
head, tree = map(pathlib.Path, sys.argv[1:3]); wide = "--wide" in sys.argv
src = (head/"tests/finite_boundary.py").read_text()
fn = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "_finite_float_coercers")
ns = {"ast": ast}; exec(compile(ast.Module(body=[fn], type_ignores=[]), "rule", "exec"), ns)
sources = {p.name: p.read_text() for p in sorted((tree/"custom_components/heatpump_optimizer").glob("*.py"))}
if not wide:
    r = ns["_finite_float_coercers"](sources)
else:
    r = set()
    for name, text in sources.items():
        for f in ast.walk(ast.parse(text)):
            if not isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)): continue
            cf = lambda node: any(isinstance(c, ast.Call) and getattr(c.func, "id", None) == "float" for c in ast.walk(node))
            g = any(isinstance(n, ast.Try) and cf(ast.Module(body=n.body, type_ignores=[])) and any(h.type is not None and any(e in ast.unparse(h.type) for e in ("ValueError","TypeError")) for h in n.handlers) for n in ast.walk(f))
            t = any(isinstance(n,(ast.If,ast.IfExp)) and "isinstance(" in ast.unparse(n.test) and cf(n) for n in ast.walk(f))
            small = len(f.args.args) - (1 if f.args.args and f.args.args[0].arg in ("self","cls") else 0) <= 2
            if (g or t) and small and len([n for n in ast.walk(f)]) < 120:
                r.add(f"{name}::{f.name}")
print(f"RESULT coercers={len(r)}"); [print("  ", x) for x in sorted(r)]
