"""N1 (NULL): rename a local variable across one function (tokenize-exact):
``reader`` -> ``input_reader`` throughout coordinator._update_current_state.
"""
import io, sys, tokenize
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import COORD, COORD_CLASS, read, write, find_method

s = read(COORD)
fn = find_method(s, COORD_CLASS, "_update_current_state")
lines = s.splitlines(keepends=True)
toks = list(tokenize.generate_tokens(io.StringIO(s).readline))
edits = []
prev = None
for tok in toks:
    if tok.type == tokenize.NAME and tok.string == "reader" and fn.lineno <= tok.start[0] <= fn.end_lineno \
            and not (prev is not None and prev.string == "."):
        edits.append(tok.start)
    if tok.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.COMMENT):
        prev = tok
assert len(edits) > 10, len(edits)
for (row, col) in sorted(edits, reverse=True):
    ln = lines[row - 1]
    lines[row - 1] = ln[:col] + "input_reader" + ln[col + len("reader"):]
write(COORD, "".join(lines))
print("renamed", len(edits))
