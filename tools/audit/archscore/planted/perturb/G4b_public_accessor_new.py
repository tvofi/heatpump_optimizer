"""G4b (GOOD): add the missing public accessor and use it: a read-only
``current_state`` property on the coordinator, and pump_arbiter.py's four
``coord._current_state`` reaches go through it.
"""
import re, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import COORD, PKG, read, write, replace_once

rel = f"{PKG}/pump_arbiter.py"
src = read(rel)
assert len(re.findall(r"coord\._current_state\b", src)) == 4
write(rel, re.sub(r"coord\._current_state\b", "coord.current_state", src))
c = read(COORD)
c = replace_once(c, '''    @property
    def current_action(self) -> dict[str, Any]:
        return self._current_action
''', '''    @property
    def current_action(self) -> dict[str, Any]:
        return self._current_action

    @property
    def current_state(self) -> ThermalState:
        return getattr(self, "_ctx", self)._current_state
''')
write(COORD, c)
from _lib import seam_set
seam_set("current_state", "core")
