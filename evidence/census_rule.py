import ast, sys, pathlib
root = pathlib.Path(sys.argv[1]); c = root / "custom_components/heatpump_optimizer"
tree = ast.parse((c / "payload.py").read_text())
keys = []
for n in tree.body:
    if isinstance(n, ast.ClassDef) and n.name == "LearningView":
        keys = [s.target.id for s in n.body if isinstance(s, ast.AnnAssign)]
src = "".join((c / f).read_text() for f in ("sensor.py", "binary_sensor.py", "button.py", "climate.py", "switch.py") if (c / f).exists())
miss = [k for k in keys if f'"{k}"' not in src]
print(f"CENSUS {len(miss)} of {len(keys)} keys unread: {miss}")
