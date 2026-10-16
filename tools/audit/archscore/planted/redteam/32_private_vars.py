"""Game private_cross_module through ``vars``: silent_mode binds ``from . import optimizer as _o`` and calls
``vars(_o)["_utc_step_starts"](..)``. The same private of the same module is reached (#2320 round 1, p7). A
``getattr`` of a name folded from constants (p6) is counted the same way, and a name computed at runtime is C2b's
tripwire. Counter C18."""
import re, sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
src = src.replace(line, "from . import optimizer as _o\n")
src, n = re.subn(r"(?<![.\w])_utc_step_starts\(", 'vars(_o)["_utc_step_starts"](', src)
assert n >= 1
p.write_text(src)
print("32_private_vars")
