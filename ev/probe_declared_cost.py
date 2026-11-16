"""Reviewer probe: run tests/features.py's metered-floor block up to and
including the 'declared cost' check, in the tree given as argv[1]."""
import os, sys
tree = sys.argv[1]
os.chdir(tree)
sys.path[:0] = [os.path.join(tree, "tests/hastub"), os.path.join(tree, "tests"), os.path.join(tree, "custom_components")]
src = open("tests/features.py").read().splitlines()
head = "\n".join(src[11:20])  # __future__ .. numpy imports
s = next(i for i, l in enumerate(src) if l.startswith("# -- R11-OUTSIDE-HONEST-METERED-FLOOR: the learned floor moves"))
e = next(i for i, l in enumerate(src) if 'f"declared {_mf_declared} measured {_mf_measured}",' in l) + 1
code = head + "\nR = Results('probe')\n" + "\n".join(src[s:e + 1]) + "\n"
g = {"__name__": "probe"}
exec(compile(code, "features_slice", "exec"), g)
R = g["R"]
for attr in ("failed", "failures", "n_failed"):
    if hasattr(R, attr):
        print("FAILED-ATTR", attr, getattr(R, attr))
