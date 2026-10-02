"""Every package .py compiles and imports (hastub on sys.path)."""
import importlib, pathlib, py_compile, sys
wt = pathlib.Path(sys.argv[1]); pkg = wt / "custom_components/heatpump_optimizer"
sys.path[:0] = [str(wt / "tests/hastub"), str(wt)]
bad = []
for p in sorted(pkg.glob("*.py")):
    py_compile.compile(str(p), doraise=True)
    name = "custom_components.heatpump_optimizer" + ("" if p.stem == "__init__" else "." + p.stem)
    try:
        importlib.import_module(name)
    except Exception as e:
        bad.append((name, repr(e)[:200]))
print("import_check:", "OK" if not bad else bad)
if bad: sys.exit(1)
