"""Game layer_violations and private_cross_module with a ``getattr`` chain rooted at the namespace ABOVE
the package: silent_mode's ``from .optimizer import _utc_step_starts`` becomes ``import custom_components
as _cc`` and each call ``getattr(getattr(_cc, "heatpump_optimizer"), "optimizer")._utc_step_starts(..)``.
The same module is still loaded and the same private still read, through a receiver no attribute arm
resolved. Counters C17 and C18 (attempt 36, #2320 round 3)."""
import re, sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
src = src.replace(line, "import custom_components as _cc\n")
src, n = re.subn(r"(?<![.\w])_utc_step_starts\(",
                 'getattr(getattr(_cc, "heatpump_optimizer"), "optimizer")._utc_step_starts(', src)
assert n >= 1, n
p.write_text(src)
print("calls through the getattr chain", n)
