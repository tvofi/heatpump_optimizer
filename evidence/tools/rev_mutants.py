#!/usr/bin/env python3
"""Reviewer-built (not the finder's): one-occurrence plants in roster_sync.py, run its self-test, restore."""
import subprocess, sys, re
from pathlib import Path
wt = Path(sys.argv[1]); f = wt / "tools/audit/seat/roster_sync.py"
orig = f.read_text()
P = {
 "NULL": None,
 "RA_unreadable_ancestry_is_valid": ("on_main = {0: True, 1: False}.get(rc)", "on_main = {0: True, 1: False}.get(rc, True)"),
 "RB_non_commit_objects_counted": ('if ln.split()[1:2] == ["commit"]]', 'if ln.split()]'),
 "RC_sha_re_dropped": ("if not SHA_RE.match(sha):", "if False:"),
 "RD_dangling_open_branch_ok": ('if not commits:\n        return f"{prefix} does not resolve to a commit"', 'if not commits:\n        return None'),
 "RE_chosen_open_loses": ("if opened:\n        return max(opened", "if False:\n        return max(opened"),
 "RF_equal_topic_one_group": ("if n == longest:", "if n == longest and gid not in [x for x,_ in out.items() if pr in _]:"),
 "RG_not_done_guard_dropped": ('if stage != "done":\n            changes.append', 'if True:\n            changes.append'),
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
