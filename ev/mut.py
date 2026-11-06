import subprocess,sys
M=[("tests/ci_ratchet.py","if key in REPORT_ONLY:","if False:","tests/ci_ratchet.py --self-test"),
   ("tools/ci/gate.py","            bound = 0","            pass #","tools/ci/gate.py --self-test"),
   ("tools/ci/prelude.py","if defer_to(ctx, pr, get) is not None:","if False:","tools/ci/prelude.py --self-test"),
   ("tools/pr/codeql_scope.py","if not any(f.startswith(ANALYZED_PREFIXES) for f in files):","if False:","tools/pr/codeql_scope.py --self-test"),
   ("tools/ci/prelude.py","    return not files or is_product is None or not all(map(is_product, files))","    return True","tools/ci/prelude.py --self-test"),
   ("tools/ci/prelude.py",'    out["machinery"] = "true" if ev != "pull_request" or machinery(changed) else "false"','    out["machinery"] = "false"',"tools/ci/prelude.py --self-test"),
   (".github/workflows/tests.yml","  mutation-pins:\n","  mutation-pins:\n    if: inputs.machinery != 'false'\n","dev/audit/harnesses/r10_ci_slim/gate_satisfiable.py"),
   (".github/workflows/tests.yml","  mutation-autofix:\n","  mutation-autofix:\n    if: inputs.pins != 'false'\n","dev/audit/harnesses/r10_ci_slim/gate_satisfiable.py"),
]
for f,a,b,cmd in M:
    src=open(f).read(); n=src.count(a)
    if n<1: print("MUTANT NOT APPLIED",f,repr(a)); continue
    open(f,"w").write(src.replace(a,b,1))
    p=subprocess.run(["python3","-I",*cmd.split()],capture_output=True,text=True)
    open(f,"w").write(src)
    out=(p.stdout+p.stderr).strip().splitlines()
    fails=[l for l in out if l.lstrip().startswith("FAIL")][:4]
    print(f"MUTANT {f} [{a.strip()[:70]!r} -> {b.strip()[:50]!r}] (occurrences {n}): rc={p.returncode} :: {out[-1] if out else ''}")
    for l in fails: print("    ",l[:200])
print("clean:",subprocess.run(["git","status","--porcelain"],capture_output=True,text=True).stdout or "yes")
