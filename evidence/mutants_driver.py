import sys, pathlib, subprocess
f = pathlib.Path("tools/audit/check_scopes.py"); orig = f.read_text()
M = {
 "M1 swap min/max": ('read = {"min": lo, "max": hi,', 'read = {"min": hi, "max": lo,'),
 "M2 no const.py fallback": ('if found is None and const in tree:', 'if False:'),
 "M3 dict branch off": ('if isinstance(n, ast.Dict):', 'if False:'),
 "M4 call branch off": ('elif isinstance(n, ast.Call) and any(isinstance(a, ast.Name) and a.id == key for a in n.args):', 'elif False:'),
 "M5 starred not expanded": ('if isinstance(a, ast.Starred):', 'if False:'),
 "M6 field ignored": ('want = value.get(row["field"]) if "field" in row and isinstance(value, dict) else value', 'want = value'),
}
code = "import sys; sys.path.insert(0,'tools/audit'); import check_scopes as c; r=c.population_self_test(); bad=[k for k,v in r.items() if not v]; print(len(r)-len(bad),'/',len(r),'held; red:',bad)"
for name, (a, b) in M.items():
    assert orig.count(a) == 1, name
    f.write_text(orig.replace(a, b))
    try:
        out = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True, timeout=120)
        print(name, "->", (out.stdout.strip() or out.stderr.strip().splitlines()[-1]))
    finally:
        f.write_text(orig)
out = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True)
print("UNMUTATED ->", out.stdout.strip() or out.stderr.strip())
