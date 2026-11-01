import ast, re, sys, os
from pathlib import Path
lines = open("tests/entities.py").read().splitlines(True)
s = "".join(lines[40234:40404])  # from 'from collections import Counter' to _r10_log_found
s = s[s.index("from collections import Counter"):]
class _R:
    def check(self, *a, **k): pass
g = {"R": _R(), "Path": Path, "ast": ast, "re": re}
exec(s, g)
plant = os.environ.get("R3_PLANT")
src = dict(g["_r10_sources"])
if plant:
    src["coordinator.py"] = src["coordinator.py"].replace(
        '    _LOGGER.warning("Factory reset (%s) applied; restore_learned_snapshot undoes it", scope)\n',
        '    _LOGGER.warning("Factory reset (%s) applied; restore_learned_snapshot undoes it", scope)\n    _LOGGER.warning("planted second")\n', 1)
if os.environ.get("R3_DROP"):
    for grp in g["_R10_LOG_ALLOWED_BY_REASON"].values(): grp.pop(("coordinator.py","async_factory_reset"), None)
    g["_R10_LOG_ALLOWED"].pop(("coordinator.py","async_factory_reset"), None)
found = g["_r10_unlatched_logs"](src)
print("RESULT verdict", g["_r10_log_verdict"](found), "sites", sum(found.values()), "modules", len(src))
