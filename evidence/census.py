"""Reviewer's wide census of OffStepNotice.check: prints one line per row (inputs -> placeholders)."""
import sys, itertools
sys.argv = ["guard_pins"]
import guard_pins as gp
for lo, hi, step, everyday, d, hold in itertools.product(
        (30, 60, 61), (55, 58, 60, 62, 64, 65, 66, 67.5, 68, 68.3, 69, 70, 71, 72, 75, 80),
        (0.5, 1, 2.5, 3, 5), (55.0, 65.0, 72.0), [x / 2 for x in range(110, 151)], (False, True)):
    if hi <= lo:
        continue
    got = gp._step_notice(everyday, d, step, hold=hold, attrs={"min": lo, "max": hi, "step": step})
    print(lo, hi, step, everyday, d, hold, None if got is None else tuple(sorted(got.items())))
