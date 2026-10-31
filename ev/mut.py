"""Reviewer's own plants (not the fixer's drivers): one exact replacement each, run the file's self-test, restore."""
import subprocess, sys, os
WT = "/home/user/wt-mut"
P = [
 ("X1_sync_writepath_rederive_no_legacy", "tools/audit/seat/roster_sync.py",
  "changes, _, transitions = derive(roster, prs, legacy)", "changes, _, transitions = derive(roster, prs)", "tools/audit/seat/roster_sync.py"),
 ("X2_sync_unreadable_cutover_swallowed", "tools/audit/seat/roster_sync.py",
  'raise Refuse(f"the carry cut-over is unreadable: {e}")', "legacy = {}", "tools/audit/seat/roster_sync.py"),
 ("X3_roster_report_reports_201", "tools/audit/carry_audit.py",
  "for n in sorted(open_issues - {LOG_ISSUE}):", "for n in sorted(open_issues):", "tools/audit/carry_audit.py"),
 ("X4_mark_not_anchored_at_end", "tools/audit/seat/roster_lib.py",
  r'([^\]\n]+)\]\Z")', r'([^\]\n]+)\]")', "tools/audit/seat/roster_lib.py"),
 ("X5_legacy_reads_every_stage", "tools/audit/seat/roster_lib.py",
  'if (g.get("resume") or {}).get("stage") in CARRY_CLOSED}', "}", "tools/audit/seat/roster_lib.py"),
 ("X6_edit_unreadable_cutover_swallowed", "tools/audit/seat/roster_edit.py",
  'raise Refuse(f"the carry cut-over is unreadable, so no "\n                                 f"stage is written: {e}")', "legacy = {}", "tools/audit/seat/roster_edit.py"),
 ("X7_moved_to_closed_allowed", "tools/audit/seat/roster_edit.py",
  "if stage in roster_lib.CARRY_CLOSED:", "if False:", "tools/audit/seat/roster_edit.py"),
 ("X8_bracket_value_allowed", "tools/audit/seat/roster_edit.py",
  'if "]" in arg:', "if False:", "tools/audit/seat/roster_edit.py"),
]
only = set(sys.argv[1:])
for name, f, a, b, test in P:
    if only and name not in only: continue
    path = os.path.join(WT, f); s = open(path).read()
    n = s.count(a)
    if n != 1: print(f"RESULT mutant={name} ANCHOR-COUNT={n} (not run)"); continue
    open(path, "w").write(s.replace(a, b))
    try:
        r = subprocess.run(["env", "-u", "BASH_ENV", "python3", "-I", test, "--self-test"], cwd=WT, capture_output=True, text=True, timeout=900)
        out = r.stdout + r.stderr
        fails = [l.strip() for l in out.splitlines() if "FAIL" in l][:2]
        summ = [l for l in out.splitlines() if "self-test:" in l][-1:]
        print(f"RESULT mutant={name} rc={r.returncode} {summ} {fails}")
    finally:
        open(path, "w").write(s)
print("restored", subprocess.run(["git","-C",WT,"status","--short"],capture_output=True,text=True).stdout.strip() or "clean")
