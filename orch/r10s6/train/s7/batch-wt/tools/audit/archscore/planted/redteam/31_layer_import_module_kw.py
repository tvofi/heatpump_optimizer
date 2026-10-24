"""Game layer_violations and private_cross_module with the dynamic import spelled by KEYWORD:
silent_mode's ``from .optimizer import _utc_step_starts`` becomes
``importlib.import_module(name=".optimizer", package=__package__)._utc_step_starts(..)``. Same constant
name, same static anchor -- ``import_module``'s first parameter is named ``name`` -- but the resolver
read the name from ``args[0]`` and returned None on a call with no positional argument, so the same
coupling read as gone. Counters C17 and C18 (attempt 31, #2320 round 3)."""
import re, sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
src = src.replace(line, "import importlib\n")
src, n = re.subn(r"(?<![.\w])_utc_step_starts\(",
                 'importlib.import_module(name=".optimizer", package=__package__)._utc_step_starts(', src)
assert n >= 1, n
p.write_text(src)
print("calls through the keyword-form import_module", n)
