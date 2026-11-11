"""Game layer_violations and private_cross_module off the bare namespace import, with no alias:
silent_mode's ``from .optimizer import _utc_step_starts`` becomes ``import custom_components`` and each
call the full dotted read ``custom_components.heatpump_optimizer.optimizer._utc_step_starts(..)``. The
statement binds only a strict PREFIX of the package, so no edge was taken and the whole path was
invisible. Counters C17 and C18 (attempt 35, #2320 round 3)."""
import re, sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
src = src.replace(line, "import custom_components\n")
src, n = re.subn(r"(?<![.\w])_utc_step_starts\(",
                 "custom_components.heatpump_optimizer.optimizer._utc_step_starts(", src)
assert n >= 1, n
p.write_text(src)
print("calls through the bare namespace import", n)
