# Reviewer's own instrument: run agreement_py's readers in-process and list every
# repo .py file actually loaded (sys.modules __file__), to compare with closure().
import sys, runpy, os, json, io, contextlib
root = os.path.realpath(sys.argv[1]); out = sys.argv[2]
sys.argv = [root + "/tools/policy/agreement_py.py", "--out", out]
try:
    with contextlib.redirect_stdout(io.StringIO()):
        runpy.run_path(sys.argv[0], run_name="__main__")
except SystemExit as e:
    print("exit", e.code, file=sys.stderr)
files = sorted({os.path.relpath(os.path.realpath(m.__file__), root) for m in list(sys.modules.values())
                if getattr(m, "__file__", None) and os.path.realpath(m.__file__).startswith(root + "/")})
print("\n".join(files))
