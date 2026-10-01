"""Re-introduce each historical P7 member's seam shape into a copy of main and
run main's DST tracer (tests/dst_checks.py) against it.
Usage: python3 p7_mutants.py <tree-copy-root> <mutant>"""
import sys, pathlib
root = pathlib.Path(sys.argv[1]); m = sys.argv[2]
P = root / "custom_components/heatpump_optimizer"
MUT = {
 # R2 D2-03 (#?): the plan grid walked in wall time from local midnight
 "R2-D2-03": ("coordinator.py",
   "    if tz is None:\n        return [midnight + step * (step_offset + i) for i in range(n_steps)]",
   "    if True:\n        return [midnight + step * (step_offset + i) for i in range(n_steps)]"),
 # R3 D2-02 (#777): capacity-tariff window walk in wall time
 "R3-D2-02": ("tariff.py",
   "    base = slot0 if tz is None else slot0.astimezone(timezone.utc)\n    starts = [base + timedelta(minutes=window * i) for i in range(n_windows)]",
   "    base = slot0\n    starts = [base + timedelta(minutes=window * i) for i in range(n_windows)]"),
 # R5 D1-08 (#1299): plan age by wall subtraction of two shared-ZoneInfo stamps
 "R5-helper": ("coordinator.py",
   "    return (dt_util.as_utc(newer) - dt_util.as_utc(older)).total_seconds()",
   "    return (newer - older).total_seconds()"),
 "R5-D1-08": ("coordinator.py",
   "            0.0, _utc_age_seconds(dt_util.now(), self._last_optimization) / 60.0",
   "            0.0, (dt_util.now() - self._last_optimization).total_seconds() / 60.0"),
}
f, old, new = MUT[m]
p = P / f; s = p.read_text()
assert s.count(old) == 1, (m, s.count(old))
p.write_text(s.replace(old, new)); print("applied", m, f)
