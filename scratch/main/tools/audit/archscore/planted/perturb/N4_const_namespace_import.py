"""N4 (NULL): the same 264 const names, reached as ``const.NAME`` through
``from . import const`` instead of a 264-name from-import. Identical
dependency, different spelling (tokenize-exact: only bare NAME tokens change).
"""
import ast, io, sys, tokenize
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import COORD, read, write

s = read(COORD)
t = ast.parse(s)
node = next(n for n in t.body if isinstance(n, ast.ImportFrom) and n.module == "const" and n.level == 1)
names = {a.asname or a.name for a in node.names}
assert all(a.asname is None for a in node.names) and len(names) == 264
lines = s.splitlines(keepends=True)
start, end = node.lineno, node.end_lineno
toks = list(tokenize.generate_tokens(io.StringIO(s).readline))
edits = []
prev = None
for tok in toks:
    if (tok.type == tokenize.NAME and tok.string in names and not (start <= tok.start[0] <= end)
            and not (prev is not None and prev.string == ".")):
        edits.append(tok.start)
    if tok.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.COMMENT, tokenize.INDENT, tokenize.DEDENT):
        prev = tok
for (row, col) in sorted(edits, reverse=True):
    ln = lines[row - 1]
    lines[row - 1] = ln[:col] + "const." + ln[col:]
# names used inside f-string expressions are not NAME tokens on 3.11: they keep a
# small residual from-import (well under the 50-name line)
fstring_names = sorted({n.id for js in ast.walk(t) if isinstance(js, ast.JoinedStr)
                        for n in ast.walk(js) if isinstance(n, ast.Name) and n.id in names})
residual = [f"from .const import {', '.join(fstring_names)}\n"] if fstring_names else []
out = lines[:start - 1] + ["from . import const\n"] + residual + lines[end:]
print("residual", fstring_names)
write(COORD, "".join(out))
print("qualified", len(edits), "uses")
