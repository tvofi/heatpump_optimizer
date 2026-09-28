import subprocess, sys, pathlib, re
W = pathlib.Path(sys.argv[1]); quick = sys.argv[2]
C = W / "custom_components/heatpump_optimizer"
MUT = [
 ("MA apply: drop the released check", "pump_arbiter.py",
  '        if getattr(coord, "_entry_released", False):\n            return  # queued', '        if False:\n            return  # queued'),
 ("MB _writable: accept any value", "pump_arbiter.py",
  '    if slot == "mode":\n        return isinstance(value, str) and value in _OWN_MODES', '    if True:\n        return True'),
 ("MB2 _load: written not dict-checked", "pump_arbiter.py",
  'written.items() if isinstance(written, dict) else ()', 'written.items()'),
 ("MC _write: literal select domain", "pump_arbiter.py",
  '                domain,\n                "select_option",', '                "select",\n                "select_option",'),
 ("MC2 _write: sensor slot not refused", "pump_arbiter.py",
  '    if slot == "mode" and domain not in _MODE_DOMAINS:', '    if False:'),
 ("MD from_dict: decile range dropped", "freq_control.py",
  '            if 0 <= decile < FREQ_DECILES:', '            if True:'),
 ("MD2 from_dict: ratio cap dropped", "freq_control.py",
  'not 0 < ratio <= FREQ_MAX_KW_PER_HZ', 'not 0 < ratio'),
 ("MD3 observe: ratio cap dropped", "freq_control.py",
  '        if ratio > FREQ_MAX_KW_PER_HZ:\n            return', '        if False:\n            return'),
 ("ME store: naive leaf read as UTC", "store.py",
  'when.replace(tzinfo=naive_zone or bound.tzinfo)', 'when.replace(tzinfo=bound.tzinfo)'),
 ("ME2 arbiter store: no naive_zone", "pump_arbiter.py",
  '        naive_zone=dt_util.DEFAULT_TIME_ZONE,  # _load\'s zone\n', ''),
 ("ME3 legionella store: no naive_zone", "legionella.py",
  '            naive_zone=dt_util.DEFAULT_TIME_ZONE,  # async_load\'s zone\n', ''),
 ("ME4 boost store: no naive_zone", "boost.py",
  '        naive_zone=dt_util.DEFAULT_TIME_ZONE,  # _parse_until\'s zone\n', ''),
 ("ME5 store: clamp written aware for a naive leaf", "store.py",
  '        clamped = clamped.replace(tzinfo=None) if naive else clamped\n', ''),
 ("F6 store: clamp short of now+lead", "store.py",
  '        clamped = bound.astimezone(when.tzinfo)\n', '        clamped = (bound - timedelta(minutes=1)).astimezone(when.tzinfo)\n'),
]
only = sys.argv[3:] 
for name, f, old, new in MUT:
    if only and not any(name.startswith(o) for o in only): continue
    p = C / f; src = p.read_text()
    assert src.count(old) == 1, (name, src.count(old))
    p.write_text(src.replace(old, new))
    try:
        r = subprocess.run([sys.executable, quick], cwd=W, env={"PYTHONPATH": "tests/hastub:tests", "PATH": "/usr/bin:/bin"},
                           capture_output=True, text=True)
        out = r.stdout + r.stderr
        fails = [l.strip()[:170] for l in out.splitlines() if l.strip().startswith("FAIL") or "Error:" in l]
        tail = [l for l in out.splitlines() if "QUICK" in l]
        print(f"### {name} ({f})  rc={r.returncode} {tail[-1] if tail else ''}")
        for l in fails: print("   ", l)
    finally:
        p.write_text(src)
