import subprocess, sys, pathlib
f = pathlib.Path(sys.argv[1]) / "tools/audit/seat/roster_edit.py"
orig = f.read_text()
M = {
 "M1": ("if not tip or tip == base_sha:", "if True:"),
 "M2": ("if old != discard and not run(", "if not run("),
 "M3": ("range(1, PUSH_ATTEMPTS + 1)", "range(1, PUSH_ATTEMPTS + 2)"),
 "M5": ("\"checkout\", \"-q\", \"--detach\", base_sha", "\"checkout\", \"-q\", \"-B\", branch, base_sha"),
 "M6": ("    elif op == \"drop-carry\":\n        op_drop_carry(roster, group, value, match)\n", ""),
 "M7": ("apply_op(roster, a.op, a.group, value, a.field, a.at_sha,\n                     a.match)", "apply_op(roster, a.op, a.group, value, a.field, a.at_sha)"),
 "R1_push_by_name": ("\"origin\", refspec],", "\"origin\", branch],"),
 "R2_no_refetch": ("            fetch_origin(a.checkout)\n            tip =", "            tip ="),
 "R3_no_discard": ("            discard = head\n", ""),
 "R4_exhaust_rc0": ("        raise Refuse(f\"lost the race for {branch}", "        return 0\n        raise Refuse(f\"lost the race for {branch}"),
 "R5_pushed_ignores_rc": ("            if r.returncode == 0:\n", "            if True:\n"),
 "R6_set_after_dropped": ("    elif op == \"set-after\":\n        op_set_after(roster, group, value)\n", ""),
 "R7_no_lint_on_retry": ("            ok, detail = lint_gate(a.checkout, a.lint_cwd, path)\n", "            ok, detail = (True, '') if attempt > 1 else lint_gate(a.checkout, a.lint_cwd, path)\n"),
}
try:
  for k,(a,b) in M.items():
    assert orig.count(a)==1, (k, orig.count(a))
    f.write_text(orig.replace(a,b))
    r = subprocess.run([sys.executable, str(f), "--self-test"], capture_output=True, text=True, timeout=600)
    out = r.stdout + r.stderr
    tally = [l for l in out.splitlines() if "self-test:" in l and "checks" in l]
    fails = [l for l in out.splitlines() if l.startswith("FAIL")]
    err = [l for l in out.splitlines() if "Error" in l][-1:]
    print(f"RESULT mutant={k} rc={r.returncode} tally={tally} fails={len(fails)} {fails[:2]} {err}")
finally:
  f.write_text(orig)
