import ast, pathlib
n = 0
for f in sorted(pathlib.Path("custom_components/heatpump_optimizer").glob("*.py")):
    for fn in ast.walk(ast.parse(f.read_text())):
        if not isinstance(fn, ast.AsyncFunctionDef): continue
        b = {a.targets[0].id: a.lineno for a in ast.walk(fn) if isinstance(a, ast.Assign)
             and isinstance(a.targets[0], ast.Name) and "_ctx" in ast.unparse(a.value)}
        w = [a.end_lineno for a in ast.walk(fn) if isinstance(a, ast.Await)]
        for r in ast.walk(fn):
            if (isinstance(r, ast.Attribute) and r.attr == "_current_state" and isinstance(r.value, ast.Name)
                    and r.value.id in b and any(b[r.value.id] < x < r.lineno for x in w)):
                n += 1; print(f"{f.name}:{r.lineno} {fn.name}")
print(f"RESULT held-ctx-reads-after-await={n}")
