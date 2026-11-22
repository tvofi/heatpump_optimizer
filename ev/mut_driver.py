import subprocess, sys, pathlib
W = pathlib.Path(sys.argv[1]); f = W/"tools/ci/prelude.py"; orig = f.read_text()
RB = 'out["machinery_rowblind"] = "true" if scoped != "pull_request" or machinery(changed, pr=pr) else "false"'
M = {
 "M7 rowblind reads ev": (RB, RB.replace("scoped !=", "ev !=")),
 "R1 rowblind always true": (RB, 'out["machinery_rowblind"] = "true"'),
 "R2 rowblind always false": (RB, 'out["machinery_rowblind"] = "false"'),
 "G rowblind guard dropped (body residual)": (RB, 'out["machinery_rowblind"] = "true" if machinery(changed, pr=pr) else "false"'),
 "M1 scoped never pull_request": ('scoped, changed, ctx = "pull_request",', 'scoped, changed, ctx = ev,'),
 "M2 if got": ("if got and got[1]:", "if got:"),
 "M3 and not why dropped": ('ctx.get("input_pr") and not why \\', 'ctx.get("input_pr") \\'),
 "M4 batch exclusion dropped": ('and not ctx.get("ref", "").startswith(codeql_scope.PROOF_REF):\n        got', 'and True:\n        got'),
 "M6 machinery reads ev": ('out["machinery"] = "true" if scoped !=', 'out["machinery"] = "true" if ev !='),
 "M8 legs read ev": ("codeql_scope.decide(leg, scoped,", "codeql_scope.decide(leg, ev,"),
 "M9 dispatch_diff always None": ("        got = dispatch_diff(ctx)\n", "        got = None\n"),
 "M11 base_sha not replaced": ('{**ctx, "base_sha": got[0]}', 'ctx'),
}
try:
  for name,(a,b) in M.items():
    assert orig.count(a)==1, (name, orig.count(a))
    f.write_text(orig.replace(a,b))
    r = subprocess.run([sys.executable, "tools/ci/prelude.py", "--self-test"], cwd=W, capture_output=True, text=True)
    lines=(r.stdout+r.stderr).splitlines()
    fails=[l for l in lines if "FAIL" in l][:4]
    print(f"{name}: rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'} | {lines[-1] if lines else ''}")
    for l in fails: print("    ", l[:220])
finally:
  f.write_text(orig)
