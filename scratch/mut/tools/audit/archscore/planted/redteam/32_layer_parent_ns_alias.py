"""Game layer_violations and private_cross_module through the namespace ABOVE the package: silent_mode's
``from .optimizer import _utc_step_starts`` becomes ``import custom_components as _cc`` and each call
``_cc.heatpump_optimizer.optimizer._utc_step_starts(..)``. The same module is still loaded and the same
private still read; the import names a strict PREFIX of the package, which resolved to no edge and
rooted no binding, so the read off the alias reached nothing. Counters C17 and C18 (attempt 32, #2320
round 3)."""
import re, sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
src = src.replace(line, "import custom_components as _cc\n")
src, n = re.subn(r"(?<![.\w])_utc_step_starts\(",
                 "_cc.heatpump_optimizer.optimizer._utc_step_starts(", src)
assert n >= 1, n
p.write_text(src)
print("calls through the namespace alias", n)
