"""Reviewer's own driver: runs entities.py's R10-FLY-CI-RATCHET-WINDOW block (lines given)
verbatim against a supplied tests.yml text, printing PASS/FAIL per check."""
import os, sys, subprocess, tempfile, pathlib, yaml
wt, yml, lo, hi = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
sys.path.insert(0, os.path.join(wt, "tests"))
import ci_ratchet
src = "".join(open(os.path.join(wt, "tests/entities.py")).readlines()[lo-1:hi])
class R:
    fails = 0
    @staticmethod
    def check(name, ok, detail=""):
        print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  :: " + detail[:600]))
        if not ok: R.fails += 1
ns = dict(_yaml=yaml, _TESTS_YML=open(yml).read(), _cir=ci_ratchet, _tempfile=tempfile,
          _subprocess=subprocess, _os=os, Path=pathlib.Path, R=R)
exec(compile(src, "entities-block", "exec"), ns)
print("FAILS", R.fails)
