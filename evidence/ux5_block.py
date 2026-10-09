"""Reviewer's probe: exec tests/features.py's UX-5 block with a stub R; print checks run/failed."""
import sys, os, re
wt = sys.argv[1]; label = sys.argv[2]
sys.path[:0] = [os.path.join(wt, 'tests/hastub'), os.path.join(wt, 'custom_components'), os.path.join(wt, 'tests')]
src = open(os.path.join(wt, 'tests/features.py')).read().splitlines()
s = next(i for i, l in enumerate(src) if l.startswith('# R9-UX-5 (#1795)'))
e = next(i for i, l in enumerate(src) if l.startswith('# -- R9-DBG-1 (#1939)'))
block = '\n'.join(src[s:e])
class R:
    run = 0; failed = []
    @classmethod
    def check(cls, name, ok, detail=''):
        cls.run += 1
        if not ok: cls.failed.append(name)
import numpy as np
g = {'R': R, 'np': np, '__name__': 'ux5probe'}
# execute statement by statement, skipping ones needing names from earlier blocks
import ast
tree = ast.parse(block)
skipped = 0
for node in tree.body:
    try:
        exec(compile(ast.Module([node], []), 'ux5', 'exec'), g)
    except NameError as ex:
        skipped += 1
    except Exception as ex:
        skipped += 1
print(f"RESULT {label} checks_run={R.run} failed={len(R.failed)} skipped={skipped}")
for f in R.failed: print("  FAILED", f)
