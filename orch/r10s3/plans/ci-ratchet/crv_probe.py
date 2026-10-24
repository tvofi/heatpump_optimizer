"""Run entities.py's R10-CI-RATCHET-RED block alone, from the worktree root."""
import json, os as _os, re, subprocess as _subprocess, sys, tempfile as _tempfile
from pathlib import Path
sys.path.insert(0, "tests")
src = Path("tests/entities.py").read_text()
start = src.index("def _cir_window(")
end = src.index("_CIR_ROW = ", start)
block_start = src.index("# R10-CI-RATCHET-RED: main's ci-ratchet")
block_end = src.index("def _derive_join_arm()")
class R:
    fails = 0
    @staticmethod
    def check(name, ok, detail=""):
        print(("ok   " if ok else "FAIL ") + name + ("" if ok else f"\n     {detail}"))
        R.fails += not ok
import ci_ratchet as _cir
ns = dict(globals())
exec(src[start:end] + src[block_start:block_end], ns)
print("failures:", R.fails)
