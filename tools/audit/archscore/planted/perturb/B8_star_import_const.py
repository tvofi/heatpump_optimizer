"""B8 (BAD): replace coordinator.py's explicit 264-name ``from .const import (...)``
with ``from .const import *``. The coupling to const is unchanged (the same
264 names are used); the import is now implicit and unlintable.
"""
import ast, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import COORD, read, write

s = read(COORD)
t = ast.parse(s)
node = next(n for n in t.body if isinstance(n, ast.ImportFrom) and n.module == "const" and n.level == 1)
assert len(node.names) == 264
lines = s.splitlines(keepends=True)
s = "".join(lines[:node.lineno - 1] + ["from .const import *  # noqa: F403\n"] + lines[node.end_lineno:])
write(COORD, s)
