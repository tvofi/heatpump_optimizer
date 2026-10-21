"""Reviewer's own plants against roster_sync.py (reviewer-built, not the fixer's driver)."""
import subprocess, sys, pathlib
root = pathlib.Path(sys.argv[1]); f = root/"tools/audit/seat/roster_sync.py"
orig = f.read_text()
P = [
 ("R1_done_rerecorded", '        if stage != "done":\n            changes.append(Change(gid, "done"', '        if True:\n            changes.append(Change(gid, "done"'),
 ("R2_exact_match_only", 'if name == topic or name.startswith(topic + "-")]', 'if name == topic]'),
 ("R3_pr_number_not_written", '.setdefault("resume", {})["pr"] = c.pr', '.setdefault("resume", {})'),
 ("R4_no_reset_on_refused_push", "            if rc != 0:\n                _reset(made, base)", "            if rc != 0:\n                pass"),
 ("R5_closed_decides", '    merged = [p for p in hits if p.state == MERGED]', '    merged = [p for p in hits if p.state != OPEN]'),
 ("R6_carry_dedupe_dropped", 'if text in (g.get("carry") or []) or (dest, text) in appends:', 'if (dest, text) in appends:'),
 ("R7_open_beats_merged_flipped", '    if opened:\n        return max(opened', '    if False:\n        return max(opened'),
 ("R8_issue_dest_appended", '                if not carry_audit.GROUP_TOK.match(dest):\n                    continue', '                if False:\n                    continue'),
 ("R9_suffix_not_stripped", '    if name.endswith(PR_SUFFIX):', '    if False:'),
]
try:
  for name, a, b in [("NULL", "", "")] + P:
    if name != "NULL":
        assert orig.count(a) == 1, (name, orig.count(a))
        f.write_text(orig.replace(a, b, 1))
    r = subprocess.run([sys.executable, str(f), "--self-test"], capture_output=True, text=True, cwd=root)
    last = (r.stdout.strip().splitlines() or [""])[-1]
    fails = [l.strip() for l in r.stdout.splitlines() if "FAIL" in l][:2]
    print(f"RESULT mutant={name} rc={r.returncode} summary={last!r} fails={fails}")
    f.write_text(orig)
finally:
  f.write_text(orig)
