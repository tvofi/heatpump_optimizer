"""Reviewer's variant of the fixer's p90 harness: the draw moved relative to the charge.
Runs the harness's run() with the morning draw starting OFFSET minutes after 07:00
(charge at 07:30-07:40, settle window to 07:55). Usage: OFFSETS as argv."""
import sys, runpy, re
src = open(sys.argv[1]).read()
for off in [int(x) for x in sys.argv[2:]]:
    s = src.replace("if 7 * 60 <= minute < 7 * 60 + 15:", f"if 7 * 60 + {off} <= minute < 7 * 60 + {off} + 15:")
    s = s.split('if __name__ == "__main__":')[0]
    g = {"__name__": "x"}
    exec(compile(s, "p90", "exec"), g)
    for arm in ("dip", "truth", "flat"):
        print(f"draw@07:{off:02d} {arm:6s} {g['run'](arm)}")
