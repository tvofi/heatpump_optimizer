"""Game layer_violations and private_cross_module through ``if not TYPE_CHECKING:``: silent_mode's
``from .optimizer import _utc_step_starts`` moves under it. The import runs at runtime; a census matching the test's
text by suffix read it as type-checking-only (#2320 round 1, p2). Counter C23."""
import sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
src = src.replace(line, "from typing import TYPE_CHECKING\n\nif not TYPE_CHECKING:\n    " + line)
p.write_text(src)
print("28_not_tc_import")
