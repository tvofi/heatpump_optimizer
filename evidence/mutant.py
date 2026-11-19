# Mutation: 2d99ad5c tests/entities.py with _r11_logger_aliases reverted to 8b68ba21,
# then evaluate the reach check planted-set equality verbatim.
import ast, sys, re
from collections import Counter
def seg(path, name):
    s = open(path).read(); t = ast.parse(s)
    for n in t.body:
        if isinstance(n, ast.FunctionDef) and n.name == name:
            return s, ast.get_source_segment(s, n)
new_s, new_f = seg(sys.argv[2], "_r11_logger_aliases")
_, old_f = seg(sys.argv[3], "_r11_logger_aliases")
mode = sys.argv[1]
src = new_s if mode == "fixed" else new_s.replace(new_f, old_f)
t = ast.parse(src)
ns = {"ast": ast, "Counter": Counter, "re": re}
want = {"_r10_unlatched_logs", "_r11_logger_aliases", "_R10_LATCH_WORD", "_r11_aliases_planted"}
for n in t.body:
    names = [n.name] if isinstance(n, ast.FunctionDef) else [x.id for x in getattr(n, "targets", []) if isinstance(x, ast.Name)]
    if set(names) & want:
        exec(compile(ast.Module([n], []), "e", "exec"), ns)
exp = None
for n in ast.walk(t):
    if isinstance(n, ast.Compare) and isinstance(n.left, ast.Name) and n.left.id == "_r11_aliases_planted":
        exp = eval(compile(ast.Expression(n.comparators[0]), "x", "eval"))
got = ns["_r11_aliases_planted"]
print(mode, "planted==expected:", got == exp, "missing:", len(exp - got), "extra:", len(got - exp))
