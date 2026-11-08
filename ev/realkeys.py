import sys
from pathlib import Path
sys.path.insert(0, "tools/pr")
import ci_predict as c
root = Path(".")
for k,(w,j,t) in sorted(c.restoring_jobs(root).items()):
    for p,a in c.grader_runs(t, root, j):
        key = c.run_key(j,p,a)
        part = next((why for kk, why in c.GRADER_PARTIAL.items() if key[:len(kk)] == kk), None)
        exact = key in c.GRADER_PARTIAL
        print("RUN", k, key, "| partial-prefix:", bool(part), "exact:", exact)
print("GAPS", c.grader_gaps(sorted({t for _,_,t in c.restoring_jobs(root).values()})))
