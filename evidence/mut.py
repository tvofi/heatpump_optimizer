import subprocess, sys, pathlib
p = pathlib.Path("tests/doc_claims.py"); orig = p.read_text()
M = [
 ("M1", 'None if any(word.search(read(h) or "") for h in hits) else', 'None if True else'),
 ("M2", 'None if k in kinds else f"is not a key of {LEDGER}\'s KINDS")\n            stack', 'None if True else f"is not a key of {LEDGER}\'s KINDS")\n            stack'),
 ("M3", '"due": all(v == "done" for v in st.values())', '"due": False'),
 ("M4", 'if sizes[n] != want:', 'if False:'),
 ("M5", 'else f"names no job of .github/workflows/{stem}.yml" if not block', 'else f"names no job of .github/workflows/{stem}.yml" if False'),
 ("M6", 'None if ms.group(2) in syms(', 'None if True or ms.group(2) in syms('),
 ("M7", 'if flows and _WORD.fullmatch(segs[0]):', 'if flows and False:'),
 ("M9-matrix", 'if matrix and matrix not in _matrix_values(block.group(1))', 'if False'),
 ("M10-service", 'None if svc in have else', 'None if True else'),
 ("M11-module", 'None if f"{PKG_REL}/{mod}.py" in tree', 'None if True or f"{PKG_REL}/{mod}.py" in tree'),
 ("M12-twin", 'recorded[n].get("structure") != recorded[twin].get("structure")', 'False'),
 ("M13-camel-method", 'else f"is no method of {cm.group(1)}" if cm.group(2) and cm.group(2) not in owner else None', 'else None'),
]
try:
    for name, a, b in M:
        n = orig.count(a)
        if n != 1: print(name, "SITE COUNT", n); continue
        p.write_text(orig.replace(a, b))
        r = subprocess.run([sys.executable, "tests/doc_claims.py"], capture_output=True, text=True,
                           env={**__import__("os").environ, "PYTHONPATH": "tests/hastub:tests:custom_components"})
        fails = [l.strip() for l in r.stdout.splitlines() if l.strip().startswith("FAIL")]
        print(f"RESULT {name} rc={r.returncode} fails={len(fails)}", fails[:3])
finally:
    p.write_text(orig)
