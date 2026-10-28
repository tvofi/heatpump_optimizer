#!/usr/bin/env python3
"""Reviewer-built, round 3 (not the finder's): further one-occurrence plants in roster_sync.py, run its self-test, restore."""
import subprocess, sys
from pathlib import Path
wt = Path(sys.argv[1]); f = wt / "tools/audit/seat/roster_sync.py"
orig = f.read_text()
P = {
 "NULL": None,
 "RH_dash_dropped_from_prefix_arm": ('name.startswith(t + "-")', 'name.startswith(t)'),
 "RI_rc_ignored_on_disambiguate": ('objs = r.stdout.split() if r.returncode == 0 else []', 'objs = r.stdout.split()'),
 "RJ_off_main_maps_true": ('on_main = {0: True, 1: False}.get(rc)', 'on_main = {0: True, 1: True}.get(rc)'),
 "RK_open_group_ancestry_checked_noneonly": ('on_main = True  # an open group', 'on_main = None  # an open group'),
 "RL_unreadable_reads_valid_in_verdict": ('if on_main is None:\n        return f"{prefix}: ancestry', 'if False:\n        return f"{prefix}: ancestry'),
}
for name, rep in P.items():
    src = orig
    if rep:
        assert src.count(rep[0]) == 1, (name, src.count(rep[0]))
        src = src.replace(rep[0], rep[1])
    f.write_text(src)
    try:
        r = subprocess.run([sys.executable, str(f), "--self-test"], cwd=wt, capture_output=True, text=True, timeout=600)
        fails = [l for l in r.stdout.splitlines() if l.startswith("FAIL")]
        summ = [l for l in r.stdout.splitlines() if "self-test:" in l]
        print(f"RESULT mutant={name} rc={r.returncode} fails={len(fails)} summary={summ[-1] if summ else r.stderr.strip()[-120:]!r}")
        for l in fails[:3]: print("   ", l[:200])
    finally:
        f.write_text(orig)
print("restored" if f.read_text() == orig else "NOT RESTORED")
