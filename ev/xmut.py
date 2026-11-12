import pathlib, subprocess, sys, tempfile
START = "# #1935 follow-up (R10-OUTSIDE-LEARNER-ROBUSTNESS-P2)"
END = "# A hot-water charge inside a counter span (the dwell saw it)"
B = "custom_components/heatpump_optimizer/boost.py"
C = "custom_components/heatpump_optimizer/coordinator.py"
M = {
 "X1 clear_spent ignores a live overlay": (B, "                and CHANNEL_SPACE not in self.until and self.mode_since is None):", "                and self.mode_since is None):"),
 "X2 clear_spent ignores a live mode": (B, "                and CHANNEL_SPACE not in self.until and self.mode_since is None):", "                and CHANNEL_SPACE not in self.until):"),
 "X3 re-press resets the start": (B, "            if channel == CHANNEL_SPACE and not self.active(channel, now):\n", "            if channel == CHANNEL_SPACE:\n"),
 "X4 mode exit not persisted": (B, "        if old == MODE_BOOST:\n            _schedule_persist(coord)\n", "        if False:\n            _schedule_persist(coord)\n"),
 "X5 apply persists only on release": (B, "    if released or held.space_settle_until != tail:\n", "    if released:\n"),
 "X6 ended-while-down owes nothing": (B, "        held.settle(end, since)\n        held._clear_spent(now)\n", "        pass\n"),
 "X7 settle may shorten a running tail": (B, "        if held is None or utc_elapsed_seconds(until, held) > 0:\n", "        if True:\n"),
 "X8 payload drops since": (B, "    if held.space_since is not None and CHANNEL_SPACE in held.until:\n        payload", "    if False:\n        payload"),
 "X9 restore drops since": (B, "    if since is not None and CHANNEL_SPACE in held.until:\n        held.space_since = since\n", "    if False:\n        held.space_since = since\n"),
 "X10 coordinator mode hook removed": (C, "        boost.note_mode_change(self, self._mode, mode)  # #1935: the mode's settling tail\n", "        pass\n"),
 "X11 negative boosted_h accepted": (B, "and not isinstance(hours, bool) and 0.0 <= hours < math.inf else None)", "and not isinstance(hours, bool) and hours < math.inf else None)"),
 "X12 spent tail restored": (B, "    if until is not None and dt_util.as_utc(until) > dt_util.as_utc(now):\n", "    if until is not None:\n"),
 "X13 mode entry does not clear spent": (B, "        if live:\n            self._clear_spent(now)\n", "        if live:\n            pass\n"),
}
def run(prelude):
    return subprocess.run([sys.executable,"tools/audit/seat/features_block.py",START,END,"--prelude",prelude],capture_output=True,text=True,timeout=900)
with tempfile.TemporaryDirectory() as d:
    o=pathlib.Path(d)/"p.py"; subprocess.run([sys.executable,"tools/audit/seat/features_block.py",START,END,"--emit-prelude",str(o)],check=True,capture_output=True)
    prelude=o.read_text()
sel = sys.argv[1:]
for name,(f,a,b) in M.items():
    if sel and name.split()[0] not in sel: continue
    p=pathlib.Path(f); orig=p.read_text()
    if orig.count(a)!=1: print(name,": SITE NOT FOUND", orig.count(a), flush=True); continue
    p.write_text(orig.replace(a,b))
    try: r=run(prelude)
    finally: p.write_text(orig)
    fails=[l.strip()[:150] for l in r.stdout.splitlines() if l.strip().startswith("FAIL")]
    print(f"{name}: exit {r.returncode}, {len(fails)} red", flush=True)
    for l in fails: print("   ",l, flush=True)
    if r.returncode and not fails: print("    tail:", r.stdout[-400:], r.stderr[-400:], flush=True)
