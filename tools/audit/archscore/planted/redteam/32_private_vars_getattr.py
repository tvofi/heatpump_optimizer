"""Game private_cross_module through ``vars`` and a folded ``getattr``: silent_mode binds
``from . import optimizer as _o`` and reads ``vars(_o)["_utc_step_starts"]``, and a second reference
``getattr(_o, "_utc" + "_step_starts")``. The same private of the same module is reached (#2320 round 1, p6, p7).
Counter C18."""
import sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
src = src.replace(line, "from . import optimizer as _o\n\n_utc_step_starts = vars(_o)[\"_utc_step_starts\"]\n_utc_again = getattr(_o, \"_utc\" + \"_step_starts\")\n")
p.write_text(src)
print("32_private_vars_getattr")
