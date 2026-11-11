"""Game layer_violations and private_cross_module through ``importlib.import_module``: the static
import becomes a call under a constant name, so the same module is still loaded and the same private
still read off it. A census with no ``import_module`` arm read the coupling as gone. Counters C17 and
C18 (attempt 26, #2320 round 1)."""
import sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
src = src.replace(line, "import importlib\n\n"
                        'importlib.import_module(".optimizer", __package__)._utc_step_starts\n')
p.write_text(src)
print("the edge moved into a constant-name import_module call")
