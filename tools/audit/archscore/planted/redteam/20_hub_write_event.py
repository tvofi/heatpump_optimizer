"""Game hub_solve_writes by moving a solve-scoped hub write into an event callback: the solve's
``ctx._opt_config.peak_offpeak_factor = tariff.offpeak_factor`` moves into ``_on_power_event``, which Home Assistant
calls back with the same live config. The write is the same; the census rooted only at the cycle and the solves, so
the site read as removed (ARCH2-s2 P4: an event callback's hub writes were counted by no score metric). Counter C16."""
import sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "coordinator.py"
src = p.read_text()
cut = "            ctx._opt_config.peak_offpeak_factor = tariff.offpeak_factor\n"
at = "        if self._peak_guard.throttled(now):\n            return\n"
assert src.count(cut) == 1 and src.count(at) == 1
src = src.replace(cut, "")
src = src.replace(at, at + "        ctx._opt_config.peak_offpeak_factor = self._capacity_tariff().offpeak_factor\n")
p.write_text(src)
print("solve write moved into the meter event")
