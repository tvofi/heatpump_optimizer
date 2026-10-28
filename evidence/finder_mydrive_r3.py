import re, subprocess, sys
from pathlib import Path
F = Path(sys.argv[1]).resolve() / "tools/audit/seat/cloud_dispatch.py"
orig = F.read_text()
M = [
 ("cli-pr-dropped", 'head=args.head or "", pr=args.pr,', 'head=args.head or "", pr="",'),
 ("cli-nonce-dropped", "nonce=args.nonce, overlay=args.overlay))", 'nonce="", overlay=args.overlay))'),
 ("cli-overlay-dropped", "nonce=args.nonce, overlay=args.overlay))", "nonce=args.nonce, overlay=None))"),
 ("cli-role-fixed", "print(dispatch_group(args.role,", 'print(dispatch_group("fixer",'),
 ("pr-dropped-api", "                     pr=pr, topic=topic, nonce=nonce, brief=", "                     pr=\"\", topic=topic, nonce=nonce, brief="),
 ("nonce-dropped-api", "                     pr=pr, topic=topic, nonce=nonce, brief=", "                     pr=pr, topic=topic, nonce=\"\", brief="),
]
S = re.compile(r"self-test: (\d+) checks, (\d+) failed")
surv = 0
try:
  for n, a, b in M:
    c = orig.count(a)
    if c != 1: print(f"RESULT mutant={n} ABORT count={c}"); continue
    F.write_text(orig.replace(a, b))
    r = subprocess.run([sys.executable, "-I", str(F), "--self-test"], capture_output=True, text=True, cwd=F.parents[3])
    m = S.search(r.stdout); f = int(m.group(2)) if m else -1
    v = "killed" if f > 0 else "CRASHED" if f < 0 else "SURVIVED"; surv += v == "SURVIVED"
    print(f"RESULT mutant={n} failed={f} verdict={v}")
    for ln in r.stdout.splitlines():
      if "FAIL" in ln: print("   ", ln.strip())
finally:
  F.write_text(orig)
print(f"RESULT mutants={len(M)} survived={surv}")
