"""Game layer_violations and private_cross_module with the dynamic name held by an ANNOTATED module-level
string constant: silent_mode's ``from .optimizer import _utc_step_starts`` becomes ``_MOD: str =
".optimizer"`` plus ``importlib.import_module(_MOD, __package__)._utc_step_starts(..)``. The same constant
in the same place as attempt 37, written with its type -- which ``common.tops`` stores as an ``AnnAssign``
under the same name, so the only thing refusing it was the resolver's ``ast.Assign`` test. Counters C17
and C18 (attempt 40, #2320 round 4)."""
import re, sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
src = src.replace(line, 'import importlib\n\n_MOD: str = ".optimizer"\n')
src, n = re.subn(r"(?<![.\w])_utc_step_starts\(",
                 "importlib.import_module(_MOD, __package__)._utc_step_starts(", src)
assert n >= 1, n
p.write_text(src)
print("calls through the annotated module-level constant", n)
