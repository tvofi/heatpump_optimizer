import subprocess, sys, pathlib
F = pathlib.Path("custom_components/heatpump_optimizer/fault_log.py")
W = sys.argv[1]
orig = F.read_text()
M = {
 "F code_text drops empty-item filter": ("        if part.strip()\n", "        if True\n"),
 "K loaded drops [-EPISODES_MAX:]": ('if len(row) == 4][-EPISODES_MAX:]', 'if len(row) == 4]'),
 "L note end_s = now_s": ("end_s = max(now_s, start_s)", "end_s = now_s"),
 "X1 _ended not registered": ("    entry.async_on_unload(_ended)\n", "    pass\n"),
 "X2 setup does not await old.ending": ("        await old.ending  #", "        pass  #"),
 "X3 _ended releases but does not save": ("            rec.ending = hass.async_create_task(_save(rec))", "            rec.ending = None"),
 "X4 _release ignores closed flag": ("    if rec.closed:\n        return False\n", "    if False:\n        return False\n"),
 "X5 async_close skips save": ("    if rec is not None and _release(rec):\n        await _save(rec)", "    if rec is not None and _release(rec):\n        pass"),
 "X6 _release skips timer": ("    for release in (*rec.releases, rec.timer):", "    for release in (*rec.releases,):"),
}
cmd = [sys.executable, "tools/audit/seat/features_block.py", "--prelude", f"exec(open('{W}/prelude.py').read())", "R11-OWNER-FAULT-TEXT (#3857): the pump"]
try:
    for name, (a, b) in M.items():
        n = orig.count(a)
        if n != 1:
            print(f"SKIP {name}: anchor count {n}"); continue
        F.write_text(orig.replace(a, b))
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=200)
        out = r.stdout + r.stderr
        killed = r.returncode != 0 or "ALL 26 FEATURES BLOCK PASSED" not in out
        fails = [l.strip()[:140] for l in out.splitlines() if l.strip().startswith("FAIL")][:2]
        print(f"{'KILLED' if killed else 'SURVIVED'} {name} rc={r.returncode} {fails}")
finally:
    F.write_text(orig)
