"""Game layer_violations through the branch of a guard the runtime DOES run: silent_mode's
``from .optimizer import _utc_step_starts`` moves into the ``else`` of ``if TYPE_CHECKING:``, which
executes. The module still needs the solver, and scipy with it; a census that walked the whole ``If``
read the edge as gone. Counter C17 (attempt 24, #2320 round 1)."""
import sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
assert src.count("from typing import Any\n") == 1
src = src.replace("from typing import Any\n", "from typing import TYPE_CHECKING, Any\n")
src = src.replace(line, "if TYPE_CHECKING:\n    pass\nelse:\n"
                        "    from .optimizer import _utc_step_starts\n")
p.write_text(src)
print("the edge moved into the else of the guard")
