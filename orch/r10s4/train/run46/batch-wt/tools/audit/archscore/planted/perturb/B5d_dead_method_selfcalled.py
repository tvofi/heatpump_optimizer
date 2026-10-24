"""B5d (BAD): two dead methods that only call each other -- an unreachable
island. Neither is reachable from production; each is "referenced".
"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import COORD, COORD_CLASS, read, write, insert_after_method, seam_set

s = read(COORD)
s = insert_after_method(s, COORD_CLASS, "_plan_age_minutes", '''    def _plan_age_hours_unused(self) -> float | None:
        """Plan age in hours (only the island below calls this)."""
        minutes = self._plan_age_minutes()
        return None if minutes is None else minutes / 60.0

    def _plan_age_label_unused(self) -> str:
        """Plan age as text (only the island above ... nothing calls this one either)."""
        hours = self._plan_age_hours_unused()
        return "never" if hours is None else f"{hours:.1f} h"
''')
write(COORD, s)
seam_set("_plan_age_hours_unused", "core")
seam_set("_plan_age_label_unused", "core")
