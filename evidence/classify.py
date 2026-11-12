import ast, re, sys
src = open(sys.argv[1]).read()
tree = ast.parse(src)
sys.path.insert(0, "tools/audit/seat")
ns = {}
m = re.search(r"QUIET_CHATTER = \(.*?\n\)\n", src, re.S)
exec("import re\n" + m.group(0), ns)
RX = re.compile("|".join(f"(?:{p})" for p, _ in ns["QUIET_CHATTER"]))
# self-test functions: names containing self_test
skip = set()
for n in ast.walk(tree):
    if isinstance(n, ast.FunctionDef) and ("self_test" in n.name or n.name.startswith("_selftest")):
        for c in ast.walk(n): skip.add(id(c))
def render(a):
    if isinstance(a, ast.Constant) and isinstance(a.value, str): return a.value
    if isinstance(a, ast.JoinedStr):
        return "".join(v.value if isinstance(v, ast.Constant) else "12" for v in a.values)
    if isinstance(a, ast.BinOp) and isinstance(a.op, ast.Add):
        l, r = render(a.left), render(a.right)
        return (l or "12") + (r or "12") if (l is not None or r is not None) else None
    return None
rows = []
for n in ast.walk(tree):
    if id(n) in skip or not isinstance(n, ast.Call) or not n.args: continue
    f = n.func
    name = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)
    if name not in ("log", "logline", "_log"): continue
    s = render(n.args[0])
    if s is None: rows.append((n.lineno, "UNRENDERED", ast.unparse(n.args[0])[:100])); continue
    first = s.splitlines()[0] if s else s
    if RX.match(s): rows.append((n.lineno, "HIDDEN", s[:160]))
for r in sorted(rows): print(*r, sep="\t")
