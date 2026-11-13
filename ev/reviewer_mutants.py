import subprocess, sys, pathlib, os
W = pathlib.Path("/home/user/rev3"); os.chdir(W)
B = "custom_components/heatpump_optimizer/boost.py"; L = "custom_components/heatpump_optimizer/learner_progress.py"
MUT = [
 ("R0 null", B, "#: The decay constant the tail is two of.", "#: The decay constant the tail is two of. (null)"),
 ("R1 freeze_end projects scaled tail", B, "projected = None if end is None else utc_shift(end, SPACE_SETTLE_TAIL)", "projected = None if end is None else utc_shift(end, settle_tail(self.space_boosted))"),
 ("R2 freeze_end ignores held", B, "if projected is None or (held is not None and utc_elapsed_seconds(held, projected) > 0):", "if projected is None:"),
 ("R3 learning_freeze ignores global mode", B, "if raw != FREEZE_REASON or _mode_live(coord):", "if raw != FREEZE_REASON:"),
 ("R4 pauses not_configured", L, 'return bool(key) and problem != "not_configured"', "return bool(key)"),
 ("R5 note_freeze no reorder", L, "        self.pop(learner, None)\n        self[learner] = reason", "        self.setdefault(learner, reason)"),
 ("R6 settle_tail no floor", B, "return max(_SETTLE_FLOOR, SPACE_SETTLE_TAIL + _SETTLE_TAU * math.log(boosted / _BOOST_WINDOW))", "return max(timedelta(0), SPACE_SETTLE_TAIL + _SETTLE_TAU * math.log(boosted / _BOOST_WINDOW))"),
 ("R7 settle_tail tau halved", B, "_SETTLE_TAU = SPACE_SETTLE_TAIL / 2", "_SETTLE_TAU = SPACE_SETTLE_TAIL / 4"),
 ("R8 frozen ranked below waiting", L, "    if frozen is not None and pauses(frozen[0]):", "    if frozen is not None and pauses(frozen[0]) and learner.blocked_by is None:"),
]
env = dict(os.environ, PYTHONPATH="tests/hastub"); env.pop("BASH_ENV", None)
S = "/tmp/claude-0/-home-user-heatpump-optimizer/1e273609-a7ad-5b76-bdba-b88798ea97ca/scratchpad"
BLOCKS = [("P3", ["# R10-OUTSIDE-LEARNER-ROBUSTNESS-P3: the frozen learner phase"]),
          ("P2", ["# #1935 follow-up (R10-OUTSIDE-LEARNER-ROBUSTNESS-P2)", "# A hot-water charge inside a counter span (the dwell saw it)"])]
for tag, args in BLOCKS:
    r = subprocess.run([sys.executable, "tools/audit/seat/features_block.py", "--emit-prelude", f"{S}/prelude_{tag}.py", *args], env=env, capture_output=True, text=True)
    print("emit", tag, r.returncode, r.stdout[-200:], r.stderr[-300:], flush=True)
def run():
    out = ""
    for tag, args in BLOCKS:
        p = subprocess.run([sys.executable, "tools/audit/seat/features_block.py", "--prelude", f'exec(open("{S}/prelude_{tag}.py").read())', *args], env=env, capture_output=True, text=True, timeout=900)
        lines = (p.stdout+p.stderr).splitlines()
        fails = [l for l in lines if "FAIL" in l]
        out += f" | {tag}: rc={p.returncode} " + " ;; ".join(fails[-5:])[:700] + ("" if fails else " :: " + " / ".join(lines[-2:])[:300])
    return out
print("UNMUTATED", run(), flush=True)
for name, f, old, new in MUT:
    t = pathlib.Path(f).read_text()
    assert t.count(old) == 1, name
    pathlib.Path(f).write_text(t.replace(old, new))
    try: print(name, run(), flush=True)
    finally: pathlib.Path(f).write_text(t)
print("git status:", subprocess.run(["git","status","--short"],capture_output=True,text=True).stdout or "clean")
