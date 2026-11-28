import subprocess, sys, pathlib, shutil
wt = pathlib.Path("/root/wt")
H = "dev/audit/harnesses/features_freeze.py"; G = "tools/policy/budget_raise_gate.py"
muts = [
 ("M1", H, "        if sid not in known:", "        if False:"),
 ("M2", H, 'if got["lines"] > manifest["lines"]:', 'if False:'),
 ("M2b", H, 'if got["lines"] > manifest["lines"]:', 'if got["lines"] >= manifest["lines"]:'),
 ("M3", H, "if h != seam and sid not in pinned:", "if False:"),
 ("M4", H, "if h != seam and sid not in pinned:", "if h != seam:"),
 ("M5", H, "        if _names_frozen(text):", "        if False:"),
 ("M6", H, "if seam not in ALL_SEAMS:", "if False:"),
 ("R1", H, "    return next(p for p in ORDER if count.get(p) == best)", "    return next(p for p in reversed(ORDER) if count.get(p) == best)"),
 ("R2", H, 'seam = MOD2SEAM.get(m, "surface")', 'seam = MOD2SEAM.get(m, "cycle")'),
 ("R3", H, "        if isinstance(n, ast.Import) and any(a.name.split(\".\")[-1] == \"features\" for a in n.names):\n            return True", "        if False:\n            return True"),
 ("R4", H, '    return {"lines": source.count("\\n"), "spans"', '    return {"lines": source.count("\\n") - 1, "spans"'),
 ("M8", G, '        (("lines",), MAX),\n        (("spans",), FROZEN),', '        (("lines",), FROZEN),\n        (("spans",), FROZEN),'),
 ("M10", G, '        (("spans",), FROZEN),\n        (("seam_pins", "*"), FROZEN),', '        (("spans",), FREE),\n        (("seam_pins", "*"), FROZEN),'),
]
for name, f, a, b in muts:
    p = wt / f; orig = p.read_text()
    if orig.count(a) != 1:
        print(name, "NOT-APPLIED count", orig.count(a)); continue
    p.write_text(orig.replace(a, b))
    try:
        r = subprocess.run("PYTHONPATH=tests/hastub python3 tests/case_select.py run tests/entities.py --plan /root/plan.txt", shell=True, cwd=wt, capture_output=True, text=True, timeout=600)
        out = r.stdout + r.stderr
        fails = [l.strip()[:90] for l in out.splitlines() if l.strip().startswith("FAIL")]
        tail = [l for l in out.splitlines() if "ENTITY CHECKS" in l or "Error" in l][-1:]
        print(name, "KILLED" if r.returncode else "SURVIVED", tail, fails, flush=True)
    finally:
        p.write_text(orig)
print("DONE", subprocess.run("git status --porcelain", shell=True, cwd=wt, capture_output=True, text=True).stdout or "clean")
