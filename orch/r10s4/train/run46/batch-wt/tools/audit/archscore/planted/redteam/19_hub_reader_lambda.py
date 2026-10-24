"""Game hub_solve_writes by handing a collaborator the hub as a zero-argument reader: the DHW learner gets
``lambda: ctx._thermal_params`` instead of the hub, and each ``self._params.X`` becomes ``self._params().X``. The
same live object is written in place by the same methods; the role engine read a constructor argument only when it
was a path, and a call as nothing, so every learner write vanished (D7-s1-83: ARCH2-s1's P1 prototype hid three
spellings this way). Counter C15."""
import re, sys
from rt_lib import pkg
root = sys.argv[1]
c = pkg(root) / "coordinator.py"
src = c.read_text()
arg = "            ctx._thermal_params,\n            frozen=self._learning_frozen,\n"
assert src.count(arg) == 1
c.write_text(src.replace(arg, "            lambda: ctx._thermal_params,\n            frozen=self._learning_frozen,\n"))
d = pkg(root) / "dhw_learning.py"
src, n = re.subn(r"\bself\._params\b(?! = params)", "self._params()", d.read_text())
assert n >= 6, n
d.write_text(src)
print("reader spellings", n)
