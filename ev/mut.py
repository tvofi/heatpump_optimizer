import subprocess, sys, pathlib
M = [
 ("M1 proof arm off", "tools/pr/codeql_scope.py", 'proof = event == "workflow_dispatch" and ref.startswith(PROOF_REF)', 'proof = False'),
 ("M2 skip on any push", "tools/pr/codeql_scope.py", 'proof = event == "workflow_dispatch" and ref.startswith(PROOF_REF)', 'proof = event != "pull_request"'),
 ("M3 .github force deleted", "tools/pr/codeql_scope.py", '        if forced:\n            return "analyze", f"{forced[0]} changes the analysis itself"\n', ''),
 ("M4 bare check deleted", "tools/pr/codeql_scope.py", '        if bare:\n            return "analyze", f"entry head(s) {\', \'.join(bare)} carry no {language} analysis"\n', ''),
 ("M5 not proven -> is None", "tools/pr/codeql_scope.py", 'if not proven:', 'if proven is None:'),
 ("M6 tree re-merge deleted", "tools/pr/codeql_scope.py", '            if git("merge-tree", "--write-tree", ps[0], ps[1]).split()[0] != git("rev-parse", f"{sha}^{{tree}}").strip():\n                return None\n', ''),
 ("M7 parent2 naming deleted", "tools/pr/codeql_scope.py", 'not ps[1].startswith(m.group(2)) or ', ''),
 ("A1 parent1 'onto' naming deleted", "tools/pr/codeql_scope.py", ' or not ps[0].startswith(m.group(3))', ''),
 ("A2 two-parent check deleted", "tools/pr/codeql_scope.py", 'len(ps) != 2 or ', ''),
 ("M8 any job state counts", "tools/pr/codeql_scope.py", '== ("completed", "success")', 'is not None'),
 ("M9 event filter deleted", "tools/ci/prelude.py", 'if r.get("event") == "pull_request" and r.get("head_sha") == head:', 'if True:'),
 ("A3 head_sha filter deleted", "tools/ci/prelude.py", 'if r.get("event") == "pull_request" and r.get("head_sha") == head:', 'if r.get("event") == "pull_request":'),
 ("M10 pr-naming dispatch is a proof", "tools/ci/prelude.py", 'ref, proven = ("" if ctx.get("input_pr") else ctx.get("ref", "")), None', 'ref, proven = ctx.get("ref", ""), None'),
 ("A4 ApiError not caught", "tools/ci/prelude.py", 'except (ghapi.ApiError, cq.subprocess.CalledProcessError):', 'except (cq.subprocess.CalledProcessError,):'),
 ("A5 unverifiable chain -> proven={}", "tools/ci/prelude.py", '    if not chain:\n        return [], None\n', '    if not chain:\n        return ["x.py"], {"h": frozenset({"actions","javascript-typescript","python"})}\n'),
]
for name, f, a, b in M:
    p = pathlib.Path(f); src = p.read_text()
    assert src.count(a) == 1, (name, src.count(a))
    p.write_text(src.replace(a, b))
    try:
        out = ""
        for t in ("tools/pr/codeql_scope.py", "tools/ci/prelude.py"):
            r = subprocess.run([sys.executable, "-I", t, "--self-test"], capture_output=True, text=True)
            fl = [l for l in r.stdout.splitlines() if l.lstrip().startswith("FAIL")]
            tail = (r.stdout.strip().splitlines() or [""])[-1] if r.returncode == 0 or fl else (r.stderr.strip().splitlines() or [""])[-1]
            out += f" | {t.split('/')[-1]}: rc={r.returncode} fails={len(fl)} {tail[:90]}"
        print(f"RESULT {name}:{out}")
    finally:
        p.write_text(src)
print("restored:", subprocess.run(["git","status","--porcelain"],capture_output=True,text=True).stdout or "clean")
