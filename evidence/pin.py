# Reviewer-built: executes tests/entities.py's own friction-trailer pin source
# (from def _friction_trailer_fixture to the second R.check) with a stub R.
import sys, json, subprocess, re
from pathlib import Path
root = Path(sys.argv[1]); sys.path.insert(0, str(root / "tests")); import os; os.chdir(root)
src = (root / "tests/entities.py").read_text().splitlines(keepends=True)
a = next(i for i, l in enumerate(src) if l.startswith("def _friction_trailer_fixture"))
b = next(i for i, l in enumerate(src[a:], a) if l.startswith('    "and the drop buys no amnesty'))
seg = "".join(src[a:b-1])
class R_:
    fails = 0
    def check(self, name, ok, msg=""):
        print(("  ok   " if ok else "  FAIL ") + name + ("" if ok else "  :: " + msg[:300]))
        R_.fails += (not ok)
from layout import locate as _layout_locate
g = {"R": R_(), "Path": Path, "json": json, "subprocess": subprocess,
     "_PL_IMPORT": "import('./" + _layout_locate(".claude/workflows/policy_lint.mjs") + "')"}
exec(compile(seg, "entities-pin", "exec"), g)
print("RESULT pin_fails=%d" % R_.fails)
