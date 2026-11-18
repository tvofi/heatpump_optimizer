"""N1c (NULL): reformat the worst function: explode every single-line call with >= 2 arguments
in optimizer._optimize_with_dhw (the max_method_loc holder)
to one argument per line, black's magic-trailing-comma style. AST identical.
"""
import ast, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import PKG, read, write, find_method

rel = f"{PKG}/optimizer.py"
s = read(rel)
before = ast.dump(ast.parse(s))
fn = find_method(s, "HeatPumpOptimizer", "_optimize_with_dhw")
lines = s.splitlines(keepends=True)
calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call) and n.lineno == n.end_lineno
         and len(n.args) + len(n.keywords) >= 2 and not any(isinstance(a, ast.Starred) for a in n.args)
         and not any(k.arg is None for k in n.keywords)]
# outermost-first on each line, one per line, bottom-up so offsets stay valid
seen = set(); chosen = []
for c in sorted(calls, key=lambda c: (c.lineno, c.col_offset)):
    if c.lineno in seen: continue
    seen.add(c.lineno); chosen.append(c)
for c in sorted(chosen, key=lambda c: -c.lineno):
    ln = lines[c.lineno - 1]
    indent = " " * (len(ln) - len(ln.lstrip()))
    func_src = ast.get_source_segment(s, c.func)
    parts = [ast.get_source_segment(s, a) for a in c.args] + [f"{k.arg}={ast.get_source_segment(s, k.value)}" for k in c.keywords]
    new_call = func_src + "(\n" + "".join(f"{indent}    {p},\n" for p in parts) + indent + ")"
    lines[c.lineno - 1] = ln[:c.col_offset] + new_call + ln[c.end_col_offset:]
s2 = "".join(lines)
assert ast.dump(ast.parse(s2)) == before
write(rel, s2)
print("exploded", len(chosen), "calls")
