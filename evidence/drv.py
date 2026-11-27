import sys, os, re, json, importlib.util
from pathlib import Path
import yaml as _yaml
SRC = Path("/root/wt/tests/entities.py").read_text().splitlines(keepends=True)
def blk(start, end):  # start: first line startswith; end: line startswith (exclusive)
    i = next(k for k, l in enumerate(SRC) if l.startswith(start))
    j = next(k for k in range(i + 1, len(SRC)) if SRC[k].startswith(end))
    return "".join(SRC[i:j])
wf = Path(sys.argv[1] if len(sys.argv) > 1 else "/root/wt/.github/workflows").resolve()
work = Path(__file__).parent / "cwd"
import shutil; shutil.rmtree(work, ignore_errors=True)
(work / ".github").mkdir(parents=True); (work / "tools/pr").mkdir(parents=True)
shutil.copytree(wf, work / ".github/workflows")
shutil.copy("/root/wt/tools/pr/cancel_superseded.py", work / "tools/pr/")
os.chdir(work)
class R:
    @staticmethod
    def check(title, cond, detail=""):
        print(("PASS " if cond else "FAIL ") + title[:70])
        if not cond: print("   detail:", str(detail)[:600])
code = (blk("_RC_DOCS = {", "\n") if False else "")
parts = [
    blk("_RC_DOCS = {", "# `contexts` is"),
    blk("def _if_under(", "_EDITED_EVENT"),
    blk("_CC_TWIN_SHA =", "# #3885: a superseded MAIN push"),
    blk("import fnmatch as _prw_fnmatch", "_PRW_UNDONE = "),
    blk("_PRW_UNDONE = ", "# The D-5 step's program"),
]
ns = {"R": R, "_yaml": _yaml, "re": re, "json": json, "Path": Path}
exec(compile("".join(parts), "extracted", "exec"), ns)
