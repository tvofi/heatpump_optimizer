import sys, re, pathlib, types
root = pathlib.Path(sys.argv[1])
src = (root/"tests/entities.py").read_text()
s = src.index("# --- bare array expansion under set -u (R10-FLY-BUS-BASH32")
e = src.index("# --- record-autofix", s)
block = src[s:e]
class R:
    fails = 0
    @staticmethod
    def check(name, ok, msg=""):
        print(("ok   " if ok else "FAIL ") + name)
        if not ok: R.fails += 1
import os; os.chdir(root)
g = {"R": R, "_closure": types.SimpleNamespace(ROOT=root)}
exec(compile(block, "entities-block", "exec"), g)
print("ENTITY-ROWS:", "FAILED %d" % R.fails if R.fails else "ok")
