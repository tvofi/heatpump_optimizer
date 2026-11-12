"""Reviewer's extra mutants (the builder's instrument, not the finder's)."""
import pathlib, subprocess, sys
B = "custom_components/heatpump_optimizer/boost.py"
M = {
 "E1 clear_spent <=0 to <0": ("        if (tail is not None and utc_elapsed_seconds(tail, now) <= 0\n", "        if (tail is not None and utc_elapsed_seconds(tail, now) < 0\n"),
 "E2 leaving mode keeps mode_since": ("            self.settle(now, self.mode_since)\n            self.mode_since = None\n", "            self.settle(now, self.mode_since)\n"),
 "E3 ended-while-down start dropped": ("        held.settle(end, since)\n", "        held.settle(end, None)\n"),
 "E4 expiry anchored to now": ("                if channel == CHANNEL_SPACE:\n                    # Anchored to the window's own end, not to when this\n                    # expiry was observed: re-equilibration starts when the\n                    # heat stopped (#1935).\n                    self.settle(end, self.space_since)\n", "                if channel == CHANNEL_SPACE:\n                    self.settle(now, self.space_since)\n"),
 "E5 cancel start dropped": ("        self.settle(now, self.space_since)\n", "        self.settle(now, None)\n"),
 "E6 payload sum always null": ('"boosted_h": None if boosted is None else boosted.total_seconds() / 3600.0,', '"boosted_h": None,'),
 "E7 block press settles a dead overlay": ("            if channel == CHANNEL_SPACE and self.active(channel, now):\n                self._note_space_boost_ended(now)\n", "            if channel == CHANNEL_SPACE:\n                self._note_space_boost_ended(now)\n"),
 "E8 settle unknown or->and": ("        if since is None or self.space_boosted is None:\n", "        if since is None and self.space_boosted is None:\n"),
 "E9 settle held or->and": ("        if held is None or utc_elapsed_seconds(until, held) > 0:\n", "        if held is None and utc_elapsed_seconds(until, held) > 0:\n"),
 "E10 clear_spent first and->or": ("        if (tail is not None and utc_elapsed_seconds(tail, now) <= 0\n", "        if (tail is not None or utc_elapsed_seconds(tail, now) <= 0\n"),
 "E11 clear_spent last and->or": ("                and CHANNEL_SPACE not in self.until and self.mode_since is None):\n", "                and CHANNEL_SPACE not in self.until or self.mode_since is None):\n"),
 "E12 restore hours bool accepted": ("and not isinstance(hours, bool) and 0.0 <= hours < math.inf else None)", "and 0.0 <= hours < math.inf else None)"),
 "E13 cancel of a dead overlay settles": ("            if channel == CHANNEL_SPACE and was_live:\n", "            if channel == CHANNEL_SPACE:\n"),
 "E14 clear keeps sum": ("            self.space_settle_until, self.space_boosted = None, timedelta(0)\n", "            self.space_settle_until, self.space_boosted = None, self.space_boosted\n"),
 "E15 mode entry start not stamped": ("            self._clear_spent(now)\n            self.mode_since = now\n", "            self._clear_spent(now)\n"),
 "E16 restore since without live overlay": ("    if since is not None and CHANNEL_SPACE in held.until:\n        held.space_since = since\n", "    if since is not None:\n        held.space_since = since\n"),
 "E17 ended-while-down clear dropped": ("        held.settle(end, since)\n        held._clear_spent(now)\n", "        held.settle(end, since)\n"),
 "E18 expire's closing clear dropped": ("                self.blocked, channel, end, now, _BLOCK_LEAD, settle=False\n            )\n        self._clear_spent(now)\n", "                self.blocked, channel, end, now, _BLOCK_LEAD, settle=False\n            )\n"),
 "E19 press clear dropped": ("                self._clear_spent(now)\n                self.space_since = now\n", "                self.space_since = now\n"),
 "E20 payload since without live overlay": ("    if held.space_since is not None and CHANNEL_SPACE in held.until:\n        payload", "    if held.space_since is not None:\n        payload"),
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
