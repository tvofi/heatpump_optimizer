"""G4a (GOOD): replace pump_arbiter.py's private reach-through with the PUBLIC
accessors the coordinator already has: coord._config -> coord.effective_config
(13 sites), coord._mode -> coord.mode (7), coord._current_action ->
coord.current_action (1). 21 private reaches become public; the coordinator
class is untouched.
"""
import re, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import PKG, read, write

rel = f"{PKG}/pump_arbiter.py"
src = read(rel)
counts = {}
for old, new in (("coord._config", "coord.effective_config"), ("coord._mode", "coord.mode"),
                 ("coord._current_action", "coord.current_action")):
    counts[old] = len(re.findall(re.escape(old) + r"\b", src))
    src = re.sub(re.escape(old) + r"\b", new, src)
assert counts == {"coord._config": 13, "coord._mode": 7, "coord._current_action": 1}, counts
write(rel, src)
