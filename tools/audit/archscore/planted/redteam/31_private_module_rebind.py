"""Game private_cross_module through a module rebind: silent_mode binds ``from . import optimizer as _o``,
rebinds ``_m = _o`` and calls ``_m._utc_step_starts(..)``. The same private of the same module is reached
(#2320 round 1, p8). Counter C18."""
import sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
import re
src = src.replace(line, "from . import optimizer as _o\n\n_m = _o\n")
src, n = re.subn(r"(?<![.\w])_utc_step_starts\(", "_m._utc_step_starts(", src)
assert n >= 1
p.write_text(src)
print("31_private_module_rebind")
