"""Reviewer's own harness (not the fixer's features_block.py): run the charge-start
block of tests/features.py with the hastub wall clock frozen to a chosen instant,
print every check's pass/fail and the day-type counts the check asserts.
usage: python3 reviewer_clock.py <tree> <ISO instant> [<ISO instant> ...]"""
import os, sys, io, contextlib
from datetime import datetime
tree = os.path.abspath(sys.argv[1])
os.chdir(tree)
sys.path[:0] = [os.path.join(tree, p) for p in ("tests/hastub", "custom_components", "tests")]
src = open("tests/features.py", encoding="utf-8").read()
hdr_end = src.index('R = Results("Feature modules")')
a = src.rindex("\n", 0, src.index("def _chg_seq(")) + 1
b = src.index("# The cooling learner reads the same flag", a)
from homeassistant.util import dt as hdt
rc_all = 0
for iso in sys.argv[2:]:
    when = datetime.fromisoformat(iso)
    hdt.freeze(when)
    ns = {"__file__": os.path.join(tree, "tests/features.py"), "__name__": "revclock"}
    exec(compile(src[:hdr_end], "features.py", "exec"), ns)
    exec('R = Results("revclock")', ns)
    exec("import asyncio as _aio\nfrom homeassistant.util import dt as dt_util\nfrom harness import FakeEntry as _r7d203_entry", ns)
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        exec(compile(src[a:b], "features.py[block]", "exec"), ns)
        rc = ns["R"].close("REVCLOCK")
    hdt.freeze(None)
    fails = [l for l in out.getvalue().splitlines() if "FAIL" in l]
    print(f"RESULT clock={iso} weekday={when.weekday()} tz={hdt.DEFAULT_TIME_ZONE} rc={rc} "
          f"partial_daytype={ns['_chg_partial'][3]} sat_daytype={ns['_chg_partial_sat'][3]} "
          f"dip_open={ns['_chg_dip'][0]} draw_open={ns['_chg_draw'][0]} fails={len(fails)}")
    for l in fails: print("   ", l[:200])
    rc_all |= rc
sys.exit(rc_all)
