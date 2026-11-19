#!/usr/bin/env python3
"""D5-s4 instrument check: does text_ledger.py's `line` column point at the unit it names?

Metric: units of text_ledger.units_of(...,"D5") over the card (www/*.js in D5-s4's cells) whose
reported line is not the line where the unit's first text line actually sits in the file;
plus the largest such offset (lines). Count key: the line scan_c_like reports vs the line
found by locating the unit's own first line in the file at or after the previous unit.
Run:  PYTHONPATH=tests/hastub /root/venv-ci/bin/python3 dev/audit/rounds/round11/D5/s4/ledger_lines.py [--patched]
  --patched applies the perturbation in memory: text_ledger.scan_c_like counts the newline an
  unterminated quote stops at (the one-line fix), and the count must go to zero (or down).
Expected at baseline 92d38ecb: RESULT misplaced_units=737 count (exact; card units 892), max_offset=11;
  --patched: misplaced_units=1, max_offset=1 (one locator tie, not a scan error).
Machine: box B11. No timing.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, time
sys.path.insert(0, "tools/audit")
import text_ledger as TL  # noqa: E402

FILES = ["custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"]


def patch():
    src = inspect.getsource(TL.scan_c_like)
    old = "                    if c != \"`\" and not hash_comments:\n                        break\n"
    assert old in src, "perturbation target moved"
    new = "                    if c != \"`\" and not hash_comments:\n                        line += 1; break\n"
    ns = {}
    exec(compile(src.replace(old, new), TL.__file__, "exec"), TL.__dict__, ns)  # in-memory one-line edit
    TL.scan_c_like = ns["scan_c_like"]


def main():
    t0 = time.process_time()
    if "--patched" in sys.argv:
        patch()
    bad, worst, total = 0, 0, 0
    for f in FILES:
        lines = TL.read(".", f).splitlines()
        cursor = 0
        for uid, line, kind, text in TL.units_of(f, TL.read(".", f), "D5"):
            total += 1
            first = text.splitlines()[0].strip()
            real = next((i + 1 for i in range(cursor, len(lines)) if first and first in lines[i]), None)
            if real is None:
                real = next((i + 1 for i in range(len(lines)) if first in lines[i]), line)
            cursor = max(cursor, real - 1)
            if real != line:
                bad += 1; worst = max(worst, abs(real - line))
    print(f"RESULT units={total} count")
    print(f"RESULT misplaced_units={bad} count")
    print(f"RESULT max_offset={worst} lines")
    tf = time.process_time() / max(time.thread_time(), 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=" + next((l.split()[1] for l in open('/proc/vmstat') if l.startswith('pswpin')), 'na'))


if __name__ == "__main__":
    main()
