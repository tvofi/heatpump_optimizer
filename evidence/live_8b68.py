import ast, sys, re, pathlib
from collections import Counter
src = open(sys.argv[1]).read(); tree = ast.parse(src)
ns = {"ast": ast, "Counter": Counter, "re": re}
want = {"_r10_unlatched_logs", "_r11_logger_aliases", "_R10_LATCH_WORD", "_r11_alias_verdict", "_R11_LOGGER_HANDOVERS"}
for n in tree.body:
    names = [n.name] if isinstance(n, ast.FunctionDef) else [t.id for t in getattr(n, "targets", []) if isinstance(t, ast.Name)]
    if set(names) & want: exec(compile(ast.Module([n], []), "e", "exec"), ns)
pkg = pathlib.Path(sys.argv[2])
srcs = {p.name: p.read_text() for p in pkg.glob("*.py")}
for a in ns["_r11_logger_aliases"](srcs): print(a)
