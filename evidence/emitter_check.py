import re, subprocess as _subprocess
from pathlib import Path
class _R:
    fails=0
    def check(self,n,ok,d=""):
        print(("  ok   " if ok else "  FAIL ")+n+("" if ok else " -- "+d)); _R.fails+= (not ok)
R=_R()
# The class's seam rule: every tracked shell file naming the variable is an
# emitter, and each one unsets it from what it exports -- as a command line of
# its own, so an `unset` surviving only inside a comment does not pass.
_CIM_EMITTERS = _subprocess.run(
    ["git", "grep", "-l", "HPO_CI_METRICS", "--", "*.sh"],
    capture_output=True, text=True, check=True).stdout.split()
_CIM_LEAKY = [p for p in _CIM_EMITTERS
              if not re.search(r"(?m)^\s*unset HPO_CI_METRICS\s*$",
                               Path(p).read_text())]
R.check(
    "every HPO_CI_METRICS emitter keeps the file from the children it runs",
    len(_CIM_EMITTERS) >= 3 and not _CIM_LEAKY,
    f"emitters={_CIM_EMITTERS}, exporting it on={_CIM_LEAKY}",
)
print(f"RESULT fails={_R.fails}")
