# Plant an UNCHECKED_HASH pyc of the R10 mutant of tests/env_drift.py into
# tests/__pycache__: any reader of that cache loads the R10 mutant whatever
# the source on disk says. Run with cwd = a checkout.
import importlib.util, py_compile, sys, tempfile, os
src = open("tests/env_drift.py").read()
old, new = "if path.startswith(prefix) and shape.matches", "if shape.matches"
assert src.count(old) == 1
d = tempfile.mkdtemp(); p = os.path.join(d, "env_drift.py")
open(p, "w").write(src.replace(old, new))
cfile = importlib.util.cache_from_source(os.path.abspath("tests/env_drift.py"))
py_compile.compile(p, cfile=cfile, doraise=True,
                   invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH)
print("PLANTED", os.path.relpath(cfile))
