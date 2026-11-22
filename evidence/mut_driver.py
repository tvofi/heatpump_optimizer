import subprocess, sys, pathlib, os
wt = pathlib.Path(os.environ["HOME"]) / "wt"
f = wt / "custom_components/heatpump_optimizer/fault_log.py"
orig = f.read_text()
M = "R.section(\"The pump's fault record (R11-OWNER-FAULT-TEXT)\")"
muts = {
 "A close keeps releases": ("    for release in (*rec.releases, rec.timer):", "    for release in (rec.timer,):"),
 "B late never set": ("    late, rec.fresh = rec.fresh, False", "    late, rec.fresh = False, False"),
 "C no save on change": ("        _request_save(rec)\n\n\ndef _request_save", "        pass\n\n\ndef _request_save"),
 "D no ring cap": ("        if len(log.episodes) > EPISODES_MAX:", "        if False:"),
 "E no setup read": ("    _apply(rec, [(e, s) for e in entities if (s := hass.states.get(e)) is not None])", "    pass"),
 "F empty items kept": ("        if part.strip()\n    ]", "    ]"),
 "G no unread": ('_UNREAD = ("unavailable", "unknown")', "_UNREAD = ()"),
 "H strict off": ("strict=not is_flag_domain(entity_id)", "strict=False"),
 "I view empty dict": ("    if rec is None:\n        return None", "    if rec is None:\n        return {}"),
 "J no code cap": ("len(log.codes) < CODES_MAX", "True"),
 "K loaded no tail cap": ("if len(row) == 4][-EPISODES_MAX:]", "if len(row) == 4]"),
 "L end unclamped": ("        end_s = max(now_s, start_s)", "        end_s = now_s"),
 "N close no save": ("            release()\n    await _save(rec)", "            release()"),
 "O timer kept": ("        rec.timer = None\n        rec.hass", "        rec.hass"),
 "P closed guard off in listener": ("        if not rec.closed:\n            _apply", "        if True:\n            _apply"),
 "Q tally no last end": ("    row[2] = end_s", "    pass"),
 "R save_at not set": ("    rec.saved_at = time.monotonic()\n", ""),
}
pre = f"exec(open('{os.environ['HOME']}/prelude.py').read())"
env = dict(os.environ, PYTHONPATH="tools/devices")
for name, (a, b) in muts.items():
    assert orig.count(a) == 1, name
    f.write_text(orig.replace(a, b))
    try:
        p = subprocess.run([sys.executable, "tools/audit/seat/features_block.py", "--prelude", pre, M], cwd=wt, env=env, capture_output=True, text=True, timeout=200)
        fails = [l for l in p.stdout.splitlines() if l.lstrip().startswith("FAIL")]
        print(f"{name}: rc={p.returncode} {'KILLED' if p.returncode else 'SURVIVED'} fails={len(fails)} {fails[:1]}")
    finally:
        f.write_text(orig)
    sys.stdout.flush()
