"""B6 (BAD): a module-level import cycle. boost.py already imports away.py;
away.py now imports boost.py at module level and uses it at runtime
(empty_override reports the boost channels) -- the package's first cycle.
"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import PKG, read, write, replace_once

rel = f"{PKG}/away.py"
s = read(rel)
s = replace_once(s, "from .drift import stored_instant\n", "from . import boost\nfrom .drift import stored_instant\n")
s = replace_once(s, '''def empty_override() -> dict[str, Any]:
    return {"active": False, "return_time": None, "migrated_helpers": False}''',
'''def empty_override() -> dict[str, Any]:
    return {"active": False, "return_time": None, "migrated_helpers": False,
            "boost_channels": list(boost.CHANNELS)}''')
write(rel, s)
