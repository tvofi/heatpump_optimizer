# Round-4 reviewer drive (reviewer-built, not the finder's): each --group CLI pass-through mutated
# independently of the fixer's spellings; run as python3 -I mydrive_r4.py <worktree>.
import re, subprocess, sys
from pathlib import Path
F = Path(sys.argv[1]).resolve() / "tools/audit/seat/cloud_dispatch.py"
orig = F.read_text()
CALL = 'print(dispatch_group(args.role, args.group, args.model, roster_ref=args.roster_ref,\n                                 head=args.head or "", pr=args.pr, nonce=args.nonce, overlay=args.overlay))'
def call(**kw):
    s = CALL
    for a, b in kw.items(): s = s.replace(a, b, 1)
    return s
M = [
 ("M0", CALL, CALL),
 ("role-probe", call(**{"args.role,": '"probe",'})),
 ("role-swap-fixer-if-reviewer", call(**{"args.role,": '("fixer" if args.role == "reviewer" else args.role),'})),
 ("group-first-roster", call(**{"args.group,": '"R10-X",'})),
 ("model-default", call(**{"args.model,": '(args.model if args.model == "m-1" else "m-1"),'})),
 ("pr-nonce-swapped", call(**{"pr=args.pr, nonce=args.nonce": "pr=args.nonce, nonce=args.pr"})),
 ("pr-truncated-1", call(**{"pr=args.pr,": "pr=(args.pr or '')[:1],"})),
 ("nonce-truncated-3", call(**{"nonce=args.nonce,": "nonce=(args.nonce or '')[:3],"})),
 ("pr-none", call(**{"pr=args.pr,": "pr=None,"})),
 ("nonce-none", call(**{"nonce=args.nonce,": "nonce=None,"})),
]
M = [(m[0], CALL, m[1]) if len(m) == 2 else m for m in M]
S = re.compile(r"self-test: (\d+) checks, (\d+) failed")
surv = 0
try:
  for n, a, b in M:
    c = orig.count(a)
    if c != 1: print(f"RESULT mutant={n} ABORT count={c}"); continue
    F.write_text(orig.replace(a, b))
    r = subprocess.run([sys.executable, "-I", str(F), "--self-test"], capture_output=True, text=True, cwd=F.parents[3])
    m = S.search(r.stdout); f = int(m.group(2)) if m else -1
    v = ("null-ok" if f == 0 else "NULL-BROKEN") if n == "M0" else "killed" if f > 0 else "CRASHED" if f < 0 else "SURVIVED"
    surv += v == "SURVIVED"
    print(f"RESULT mutant={n} failed={f} verdict={v}")
    for ln in r.stdout.splitlines():
      if "FAIL" in ln: print("   ", ln.strip())
finally:
  F.write_text(orig)
print(f"RESULT mutants={len(M)-1} survived={surv}")
