"""Game layer_violations with a negated guard: ``if not TYPE_CHECKING:`` runs at runtime -- away from
a type checker it is true -- and the census matched any test whose unparsed text ends in
``TYPE_CHECKING``. silent_mode's ``from .optimizer import _utc_step_starts`` moves under it and reads
as gone. Counter C17 (attempt 25, #2320 round 1)."""
import sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
assert src.count("from typing import Any\n") == 1
src = src.replace("from typing import Any\n", "from typing import TYPE_CHECKING, Any\n")
src = src.replace(line, "if not TYPE_CHECKING:\n"
                        "    from .optimizer import _utc_step_starts\n")
p.write_text(src)
print("the edge moved under the negated guard")
