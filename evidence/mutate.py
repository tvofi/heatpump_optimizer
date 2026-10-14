"""Reviewer's own mutants on tools/replay/export.py; restores via git checkout and asserts clean."""
import subprocess, sys
from pathlib import Path
wt = Path(sys.argv[1]); runner = sys.argv[2]
f = wt / "tools/replay/export.py"
orig = f.read_text()
M = {
 "M1_platform": ('if e.get("platform") == TIBBER_PLATFORM\n        and str(', 'if True\n        and str('),
 "M2_sensor_prefix": ('and str(e.get("entity_id", "")).startswith("sensor.")', 'and True'),
 "M3_disabled": ('and not e.get("disabled_by")\n        and "_"', 'and True\n        and "_"'),
 "M4_bare_uid": ('and "_" not in str(e.get("unique_id") or "_")', 'and True'),
 "M5_translation_key": ('and e.get("translation_key") in (None, TIBBER_PRICE_KEY)', 'and True'),
 "M6_recorder": ('live = [c for c in candidates if recorded(c)]', 'live = list(candidates)'),
 "M7_entry_pref": ('if config.get("price_entity") in live:', 'if False:'),
 "M8_flag_wins": ('if not price_entity and config.get("price_source") != PRICE_SOURCE_ENTITY:', 'if config.get("price_source") != PRICE_SOURCE_ENTITY:'),
 "M9_entity_source": ('if not price_entity and config.get("price_source") != PRICE_SOURCE_ENTITY:', 'if not price_entity:'),
 "M10_uid_none_default": ('str(e.get("unique_id") or "_")', 'str(e.get("unique_id") or "")'),
 "M11_numeric": ('any(_numeric(row[1]) for row', 'any(True for row'),
 "M12_one_to_first": ('if len(live) == 1:', 'if len(live) >= 1:'),
}
try:
    for name, (a, b) in M.items():
        assert orig.count(a) == 1, (name, orig.count(a))
        f.write_text(orig.replace(a, b))
        r = subprocess.run([sys.executable, runner, str(wt)], capture_output=True, text=True)
        red = [l.split()[2] for l in r.stdout.splitlines() if l.startswith("RESULT FAIL")]
        print(f"RESULT {name} rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'} red={red}"
              + ("" if r.returncode in (0, 1) else " ERR " + r.stderr[-300:]))
finally:
    f.write_text(orig)
    subprocess.run(["git", "-C", str(wt), "checkout", "--", "tools/replay/export.py"])
    st = subprocess.run(["git", "-C", str(wt), "status", "--porcelain"], capture_output=True, text=True).stdout
    print("RESULT restore clean:", st == "")
