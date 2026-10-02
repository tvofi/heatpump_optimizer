# Reviewer's own harness (not the fixer's): exec tests/entities.py lines
# [_edited_listing_jobs .. merge-queue null control] with a stub R, in a tree.
import sys, json, re, os, subprocess, tempfile
from pathlib import Path
import yaml as _yaml
tree, mut = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "none"
os.chdir(tree)
src = Path("tests/entities.py").read_text().splitlines()
a = next(i for i, l in enumerate(src) if l.startswith("def _edited_listing_jobs"))
b = next(i for i, l in enumerate(src) if l.startswith("# --- the coverage cache restores"))
code = "\n".join(src[a:b])
if mut == "ifunder-drop":
    code = code.replace('.replace("!cancelled()", " True ")', "")
elif mut == "ifunder-false":
    code = code.replace('.replace("!cancelled()", " True ")', '.replace("!cancelled()", " False ")')
class _R:
    fails = 0
    def check(self, name, ok, detail=""):
        print(("  ok   " if ok else "  FAIL ") + name + ("" if ok else f"  -- {str(detail)[:300]}"))
        if not ok: _R.fails += 1
R = _R()
g = dict(globals()); g["R"] = R
exec(compile(code, "entities-region", "exec"), g)
print(f"RESULT mut={mut} fails={_R.fails}")
