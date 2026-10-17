"""Game layer_violations and private_cross_module on the plain dotted ``import``, with no alias:
silent_mode's ``from .optimizer import _utc_step_starts`` becomes ``import <pkg>.optimizer`` and each
call the full dotted read ``custom_components.heatpump_optimizer.optimizer._utc_step_starts(..)``. The
same module is still loaded and the same private still read; the statement binds only the root name,
so both the edge and the crossing the read makes were invisible. Counters C17 and C18 (attempt 29,
#2320 round 3)."""
import re, sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
src = src.replace(line, "import custom_components.heatpump_optimizer.optimizer\n")
src, n = re.subn(r"(?<![.\w])_utc_step_starts\(",
                 "custom_components.heatpump_optimizer.optimizer._utc_step_starts(", src)
assert n >= 1, n
p.write_text(src)
print("calls through the full dotted read", n)
