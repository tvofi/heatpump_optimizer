"""Game layer_violations and private_cross_module with a constant-name dynamic import: silent_mode's
``from .optimizer import _utc_step_starts`` becomes ``importlib.import_module(".optimizer", __package__)
._utc_step_starts``. The same module is loaded at import time; a census of import statements read no edge
(#2320 round 1, p3). Counter C23."""
import sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
src = src.replace(line, "import importlib\n\n_utc_step_starts = importlib.import_module(\".optimizer\", __package__)._utc_step_starts\n")
p.write_text(src)
print("29_importlib_const")
