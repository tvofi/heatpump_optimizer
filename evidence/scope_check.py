# step 14: is _is_citation_source's set EXACTLY the arm's read set?
import subprocess, re, sys
sys.path.insert(0, "tests")
import closure as C
tracked = subprocess.run(["git","ls-files"],capture_output=True,text=True).stdout.split()
pred = sorted(f for f in tracked if C._is_citation_source(f))
arm = sorted({*_SP_POLICY, *_SP_CARRIES})
print("predicate files:", len(pred))
print("arm read set   :", len(arm))
print("in predicate not arm:", sorted(set(pred)-set(arm)))
print("in arm not predicate:", sorted(set(arm)-set(pred)))
print("IDENTICAL:", set(pred)==set(arm))
# does anything else depend on these being inert? list scripts whose closure
# contains one of these files (other than tests/entities.py)
print("--- other scripts reading a citation source ---")
n=0
for s, files in C.CLOSURES.items() if hasattr(C,'CLOSURES') else []:
    pass
