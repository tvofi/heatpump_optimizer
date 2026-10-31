"""Game hub_solve_writes by handing the peak-guard meter callback to Home Assistant through a package
helper that returns it: ``async_track_state_change_event(self.hass, [entity], _pkg_wrap(self._on_power_event))``
with ``def _pkg_wrap(cb): return cb``. The subscription and its hub writes are the same; a census that skipped
every callback handed to a package function read the callback's writes as gone (#2311 round-1 review, F1).
Counter C16b."""
import sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "coordinator.py"
src = p.read_text()
cut = "            self.hass, [entity], self._on_power_event\n"
assert src.count(cut) == 1, src.count(cut)
src = src.replace(cut, "            self.hass, [entity], _pkg_wrap(self._on_power_event)\n")
anchor = "\ndef _plain_types("
assert src.count(anchor) == 1
src = src.replace(anchor, "\ndef _pkg_wrap(cb):\n    return cb\n\n" + anchor, 1)
p.write_text(src)
print("meter callback wrapped by a package helper")
