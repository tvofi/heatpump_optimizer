# census.py <entities.py>: what the payload arm reads over the live package, from a checkout's cwd.
# Prints the module, constant, identifier and shipped-file counts, and every refusal before the allowance.
import ast, subprocess, sys
from pathlib import Path

class R:
    check = staticmethod(lambda *a: None)


src = open(sys.argv[1]).read()
lines = src.splitlines(keepends=True)
start = next(i for i, l in enumerate(lines) if l.startswith("from collections import Counter  # noqa: E402"))
end = next(i for i, l in enumerate(lines) if l.startswith("_R10_LOG_ALLOWED_BY_REASON"))
g = {"ast": ast, "re": __import__("re"), "subprocess": subprocess, "Path": Path, "R": R, "__name__": "census"}
exec(compile("".join(lines[start:end]), "entities-block", "exec"), g)
srcs, files = g["_r10_sources"], g["_r11_files"]
consts = sum(isinstance(n, ast.Constant) and isinstance(n.value, (str, bytes))
             for s in srcs.values() for n in ast.walk(ast.parse(s)))
print("modules", len(srcs), "str/bytes constants", consts, "shipped non-module files", len(files))
for row in g["_r11_logger_aliases"](srcs, files):
    print("refused", row)
