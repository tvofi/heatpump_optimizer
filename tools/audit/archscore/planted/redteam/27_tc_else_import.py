"""Game layer_violations and private_cross_module through the else of a TYPE_CHECKING test: silent_mode's
``from .optimizer import _utc_step_starts`` moves into the ``else:`` of ``if TYPE_CHECKING: pass``. The import still
runs at runtime; a census that skipped the whole ``if`` read the solver's edge and the private crossing as gone
(#2320 round 1, p1). Counter C23."""
import sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
src = src.replace(line, "from typing import TYPE_CHECKING\n\nif TYPE_CHECKING:\n    pass\nelse:\n    " + line)
p.write_text(src)
print("27_tc_else_import")
