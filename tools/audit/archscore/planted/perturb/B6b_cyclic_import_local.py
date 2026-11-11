"""B6b (BAD, same cycle as B6): the identical away -> boost dependency, spelled
as a function-scope import (the usual way a cycle is made to load).
"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import PKG, read, write, replace_once

rel = f"{PKG}/away.py"
s = read(rel)
s = replace_once(s, '''def empty_override() -> dict[str, Any]:
    return {"active": False, "return_time": None, "migrated_helpers": False}''',
'''def empty_override() -> dict[str, Any]:
    from . import boost

    return {"active": False, "return_time": None, "migrated_helpers": False,
            "boost_channels": list(boost.CHANNELS)}''')
write(rel, s)
