"""Reviewer's argument-level mutants (the builder's instrument, not the finder's)."""
import pathlib, subprocess, sys
B = "custom_components/heatpump_optimizer/boost.py"
M = {
 "F1 mode exit start dropped": ("            self.settle(now, self.mode_since)\n", "            self.settle(now, None)\n"),
 "F2 expiry start dropped": ("                    self.settle(end, self.space_since)\n            elif utc_elapsed_seconds(end, now) > _MAX_LEAD", "                    self.settle(end, None)\n            elif utc_elapsed_seconds(end, now) > _MAX_LEAD"),
 "F3 sum sign flipped": ("timedelta(seconds=utc_elapsed_seconds(end, since))", "timedelta(seconds=utc_elapsed_seconds(since, end))"),
 "F7 ended-while-down anchored to restart": ("        held.settle(end, since)\n", "        held.settle(now, since)\n"),
 "F11 apply reads the tail after expiry": ("    tail = held.space_settle_until\n    held.expire(now)\n", "    held.expire(now)\n    tail = held.space_settle_until\n"),
 "F12 ended-while-down start is the restart": ("        held.settle(end, since)\n", "        held.settle(end, end)\n"),
}
p = pathlib.Path(B); orig = p.read_text()
for name, (a, b) in M.items():
    if orig.count(a) != 1:
        print(name, ": SITE NOT FOUND", orig.count(a), flush=True); continue
    p.write_text(orig.replace(a, b))
    try: r = subprocess.run([sys.argv[1]], capture_output=True, text=True, timeout=600)
    finally: p.write_text(orig)
    fails = [l.strip()[:140] for l in r.stdout.splitlines() if l.strip().startswith("FAIL")]
    print(f"{name}: exit {r.returncode}, {len(fails)} red" + ("" if r.returncode else "  <-- SURVIVED"), flush=True)
    for l in fails: print("   ", l, flush=True)
    if r.returncode and not fails: print("    raised:", (r.stderr.strip().splitlines() or ['-'])[-1][:160], flush=True)
