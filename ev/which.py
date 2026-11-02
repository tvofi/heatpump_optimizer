import subprocess, sys, pathlib
p = pathlib.Path("tools/pr/merge_main_bot.py"); orig = p.read_text()
M = {"wrong-line-drop-first": ('return "".join(f"\\n    {l}" for l in lines)', 'return "".join(f"\\n    {l}" for l in lines[1:])'),
 "append-on-other-conflict": ('return "skip-other-conflict " + ",".join(other)', 'return "skip-other-conflict " + ",".join(other) + claim_refusal(driver_err)')}
try:
  for k,(a,b) in M.items():
    p.write_text(orig.replace(a,b))
    r = subprocess.run([sys.executable,p,"--self-test"],capture_output=True,text=True)
    print(k, [l[:160] for l in r.stdout.splitlines() if "FAIL" in l])
finally: p.write_text(orig)
