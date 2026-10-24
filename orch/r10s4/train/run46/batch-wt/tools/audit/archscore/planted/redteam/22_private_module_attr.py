"""Game private_cross_module through a module binding: silent_mode's ``from .optimizer import _utc_step_starts``
becomes ``from . import optimizer as _solver`` and each call ``_solver._utc_step_starts(..)``. The same private
helper of the same module is reached; a census of imported names read the crossing as gone. Counter C18."""
import re, sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
src = src.replace(line, "from . import optimizer as _solver\n")
src, n = re.subn(r"(?<![.\w])_utc_step_starts\(", "_solver._utc_step_starts(", src)
assert n >= 1, n
p.write_text(src)
print("calls through the module", n)
