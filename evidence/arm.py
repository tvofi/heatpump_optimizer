"""Reviewer's own driver (revstale): exec tests/entities.py's #2227 arm block alone."""
import ast, json, os, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, "tests")
from layout import canon as _layout_canon, locate as _layout_locate
_PL_IMPORT = "import('./" + _layout_locate(".claude/workflows/policy_lint.mjs") + "')"
class _R:
    def __init__(self): self.res = []
    def check(self, name, ok, detail=""):
        self.res.append(bool(ok)); print(("PASS " if ok else "FAIL ") + name[:90] + (" :: " + detail if not ok else ""))
R = _R()
src = Path("tests/entities.py").read_text()
a = src.index("# --- N-move-stale-path (#2227)"); b = src.index("# --- D11-04 (#1194)")
g = dict(globals()); exec(compile(src[a:b], "entities_arm", "exec"), g)
extra = os.environ.get("ARM_EXTRA")
if extra: exec(extra, g)
print("ARM", "PASS" if all(R.res) else "FAIL", R.res)
