"""B5b (BAD): a dead @property on the coordinator (nothing reads it)."""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import COORD, COORD_CLASS, read, write, insert_after_method, seam_set

s = read(COORD)
s = insert_after_method(s, COORD_CLASS, "_plan_age_minutes", '''    @property
    def plan_age_hours_unused(self) -> float | None:
        """Plan age in hours (nothing reads this)."""
        minutes = self._plan_age_minutes()
        return None if minutes is None else minutes / 60.0
''')
write(COORD, s)
seam_set("plan_age_hours_unused", "core")
