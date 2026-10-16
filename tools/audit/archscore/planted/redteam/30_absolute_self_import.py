"""Game layer_violations and private_cross_module with an absolute self-import: silent_mode's
``from .optimizer import _utc_step_starts`` becomes ``from custom_components.heatpump_optimizer.optimizer import
_utc_step_starts``. The same module is imported; a census that filed every absolute import as an external root read
no edge (#2320 round 1, p4). Counter C23."""
import sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
src = src.replace(line, "from custom_components.heatpump_optimizer.optimizer import _utc_step_starts\n")
p.write_text(src)
print("30_absolute_self_import")
