import sys, json, subprocess, tempfile, os
from pathlib import Path
_PL_IMPORT = "import('./tools/policy/policy_lint.mjs')"
class _R:
    def __init__(s): s.f=0
    def check(s, name, ok, detail=""):
        print(("ok   " if ok else "FAIL ")+name[:70], "" if ok else detail); s.f += (not ok)
R=_R()
exec(open(sys.argv[1]).read())
sys.exit(1 if R.f else 0)
