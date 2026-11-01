import subprocess, sys, pathlib
p = pathlib.Path("tools/pr/merge_main_bot.py"); orig = p.read_text()
M = {
 "append-on-other-conflict": ('return "skip-other-conflict " + ",".join(other)', 'return "skip-other-conflict " + ",".join(other) + claim_refusal(driver_err)'),
 "body-M3-refused-anywhere": ('if not any(l.startswith(CLAIM_REFUSED) for l in lines)', 'if not any("refused" in l for l in lines)'),
}
try:
  for k,(a,b) in M.items():
    assert orig.count(a)==1, k
    p.write_text(orig.replace(a,b))
    r = subprocess.run([sys.executable,"tools/pr/merge_main_bot.py","--self-test"],capture_output=True,text=True)
    print(f"RESULT mutant={k} selftest_rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'} :: {r.stdout.strip().splitlines()[-1]}")
finally:
  p.write_text(orig)
