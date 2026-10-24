"""Game layer_violations and private_cross_module with an absolute self-import: silent_mode's
``from .optimizer import _utc_step_starts`` is spelled through the package's full path. The same
module is still loaded and the same private still read; a census that filed ``custom_components`` as
an external root and never stripped the prefix read the edge as gone. Counters C17 and C18 (attempt
27, #2320 round 1)."""
import sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
src = src.replace(line, "from custom_components.heatpump_optimizer.optimizer import _utc_step_starts\n")
p.write_text(src)
print("the edge moved to the absolute self-import")
