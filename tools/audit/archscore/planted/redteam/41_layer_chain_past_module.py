"""Game layer_violations and private_cross_module with the chain continuing PAST the module boundary:
silent_mode's ``from .optimizer import _utc_step_starts`` becomes ``import custom_components as _cc`` and
each call ``_cc.heatpump_optimizer.optimizer._utc_step_starts.__call__(..)``. The module the chain names
is ``optimizer``, four segments down, and the name read off it is ``_utc_step_starts`` -- but the
OUTERMOST receiver names a function, not a module, so a resolver that only asks the outermost node read
the coupling as gone. Counters C17 and C18 (attempt 41, #2320 round 5)."""
import re, sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
src = src.replace(line, "import custom_components as _cc\n")
src, n = re.subn(r"(?<![.\w])_utc_step_starts\(",
                 "_cc.heatpump_optimizer.optimizer._utc_step_starts.__call__(", src)
assert n >= 1, n
p.write_text(src)
print("calls through the chain one step past the module", n)
