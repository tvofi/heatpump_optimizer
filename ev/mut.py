import subprocess, sys, pathlib
p = pathlib.Path("tools/pr/merge_main_bot.py"); orig = p.read_text()
M = {
 "prefix-mismatch": ('CLAIM_REFUSED = "MERGE-CLAIM: refused "', 'CLAIM_REFUSED = "MERGE-CLAIM: refuse: "'),
 "indent-dropped": ('return "".join(f"\\n    {l}" for l in lines)', 'return "".join(f"\\n{l}" for l in lines)'),
 "always-append": ('    if not any(l.startswith(CLAIM_REFUSED) for l in lines):\n        return ""\n', ''),
 "never-append": ('    if not any(l.startswith(CLAIM_REFUSED) for l in lines):\n        return ""\n', '    return ""\n'),
 "append-on-non-refusal": ('        return "skip-pins-unread"', '        return "skip-pins-unread" + claim_refusal(driver_err)'),
 "wrong-line-first-only": ('return "".join(f"\\n    {l}" for l in lines)', 'return "".join(f"\\n    {l}" for l in lines[:1])'),
 "wrong-line-drop-first": ('return "".join(f"\\n    {l}" for l in lines)', 'return "".join(f"\\n    {l}" for l in lines[1:])'),
 "decide-no-call": ('                + claim_refusal(driver_err))', '                )'),
 "any-to-all": ('if not any(l.startswith', 'if not all(l.startswith'),
}
try:
  for k,(a,b) in M.items():
    assert orig.count(a)==1, k
    p.write_text(orig.replace(a,b))
    r = subprocess.run([sys.executable,"tools/pr/merge_main_bot.py","--self-test"],capture_output=True,text=True)
    print(f"RESULT mutant={k} selftest_rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'} :: {r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:]}")
finally:
  p.write_text(orig)
