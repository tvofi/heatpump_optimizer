import re, subprocess, sys
from pathlib import Path
F = Path(sys.argv[1]).resolve() / "tools/audit/seat/cloud_dispatch.py"
orig = F.read_text()
M = [
 ("explicit-roster-ref-ignored", "roster_ref = roster_lib.reader_ref(repo_dir, roster_ref)", "roster_ref = roster_lib.reader_ref(repo_dir, None)"),
 ("cli-head-dropped", 'head=args.head or "", pr=args.pr', 'head="", pr=args.pr'),
 ("cli-roster-ref-dropped", "roster_ref=args.roster_ref,\n", "roster_ref=None,\n"),
 ("privacy-checks-message-only", "why = ref_privacy.refusal(ref, ((", "why = ref_privacy.refusal(\"dispatch/x\", (("),
 ("reviewer-guard-any-role", 'if role == "reviewer" and not head:', 'if role == "fixer" and not head:'),
 ("head-ignored-reviewer-only", 'payload = render(role, head or _git(', 'payload = render(role, (head if role != "reviewer" else "") or _git('),
 ("fetch-skipped", '        _git(repo_dir, "fetch", "-q", "origin", f"refs/heads/{ref}")\n', "        pass\n"),
 ("group-missing-no-refuse", "    if group is None:\n        raise Refusal", "    if False:\n        raise Refusal"),
 ("cli-model-check-off", "if not args.model:\n                raise", "if False:\n                raise"),
 ("flagpath-head-required-off", 'if not args.head:\n            raise Refusal("--head is required', 'if False:\n            raise Refusal("--head is required'),
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
