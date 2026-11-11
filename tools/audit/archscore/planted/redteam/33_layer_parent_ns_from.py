"""Game layer_violations and private_cross_module through a from-import of the namespace ABOVE the
package: silent_mode's ``from .optimizer import _utc_step_starts`` becomes ``from custom_components
import heatpump_optimizer`` and each call ``heatpump_optimizer.optimizer._utc_step_starts(..)``. The
source is a strict PREFIX of the package, so the from-import resolved to no edge and bound no module,
and the dotted read off the bound name reached nothing. Counters C17 and C18 (attempt 33, #2320 round
3)."""
import re, sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
src = src.replace(line, "from custom_components import heatpump_optimizer\n")
src, n = re.subn(r"(?<![.\w])_utc_step_starts\(",
                 "heatpump_optimizer.optimizer._utc_step_starts(", src)
assert n >= 1, n
p.write_text(src)
print("calls through the parent namespace's from-import", n)
