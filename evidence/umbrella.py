"""Exec tests/entities.py top-level statements one by one (failures skipped) up to the CI umbrella check; print its lines."""
import ast, sys, os, io, contextlib
root = sys.argv[1]; os.chdir(root); sys.path.insert(0, root); sys.path.insert(0, root + "/tests")
src = open("tests/entities.py").read(); tree = ast.parse(src)
ns = {"__name__": "__main__", "__file__": root + "/tests/entities.py"}
buf = io.StringIO(); skipped = 0
for node in tree.body:
    if node.lineno > 21940: break
    code = compile(ast.Module([node], []), "tests/entities.py", "exec")
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            exec(code, ns)
    except BaseException:
        skipped += 1
    if node.lineno >= 21540: buf.write(out.getvalue())
print(buf.getvalue()); print("skipped-statements", skipped)
print("PLANT_MISSED", ns.get("_CI_PLANT_MISSED"))
