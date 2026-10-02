"""Run only the R9-P3 block of tests/features.py against the package on sys.path."""
import sys, time
sys.path.insert(0, "tests")
tree = sys.argv[1] if len(sys.argv) > 1 else "custom_components"
sys.path.insert(0, tree)
src = open("tests/features.py").read()
a = src.index("# -- R9-P3: one floor per quantity")
b = src.index("# -- #1524: the experiment identifies a TWO-ZONE house")
head = '''
import numpy as np
class _R:
    fails = 0
    def check(self, name, ok, detail=""):
        print(("PASS " if ok else "FAIL ") + name[:100] + ("" if ok else f"  [{str(detail)[:1500]}]"))
        self.fails += not ok
R = _R()
'''
import heatpump_optimizer.optimizer, golden, numpy  # already imported by features.py
t = time.time(); c0 = time.process_time()
exec(compile(head + src[a:b], "features.py[R9-P3]", "exec"))
import heatpump_optimizer
print(f"RESULT package={heatpump_optimizer.__file__} fails={R.fails} groups={len(_r9p3_open)} wall_s={time.time()-t:.2f} cpu_s={time.process_time()-c0:.2f}")
