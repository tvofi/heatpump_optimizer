"""Game layer_violations and private_cross_module with the dynamic import's name held by a module-level
string constant: silent_mode's ``from .optimizer import _utc_step_starts`` becomes ``_MOD = ".optimizer"``
plus ``importlib.import_module(_MOD, __package__)._utc_step_starts(..)``. The name is a ``ast.Name``, not
a literal, but the constant it holds is statically readable, so the same module is still loaded and the
same private still read. Counters C17 and C18 (attempt 37, #2320 round 3)."""
import re, sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
src = src.replace(line, 'import importlib\n\n_MOD = ".optimizer"\n')
src, n = re.subn(r"(?<![.\w])_utc_step_starts\(",
                 "importlib.import_module(_MOD, __package__)._utc_step_starts(", src)
assert n >= 1, n
p.write_text(src)
print("calls through the module-level constant name", n)
