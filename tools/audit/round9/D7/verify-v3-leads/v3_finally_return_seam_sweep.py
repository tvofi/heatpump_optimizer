"""V3 (leads) independent recheck of D7-s3-51's seam_rule enumeration: does the finder's
non-recursive `glob.glob('tests/*.py')` command cover the whole phenomenon ("no finally block in
the suite or its lanes ends in return/break/continue"), or only the demonstrated site?

Method: use CPython 3.14's own PEP 765 SyntaxWarning (compile() with warnings recorded), not a
hand-rolled AST walk -- a naive AST walk over-counts (tests/gate_lock.py:433/435 have a `break`/
`continue` scoped to their OWN nested `for` loop inside the finally, which does not escape the
finally and so does not swallow anything; CPython's compiler correctly does not warn on them,
and an AST-only check that does not track loop scope wrongly flags them: caught and discarded
below after cross-checking `python3 -W error::SyntaxWarning -c "py_compile.compile(...)"` returned
`ok` for gate_lock.py). Runs recursively over tests/, custom_components/ and tools/, not just the
top-level tests/*.py glob the finder's command names.
Command: /home/claude/venv314/bin/python \
  tools/audit/round9/D7/verify-v3-leads/v3_finally_return_seam_sweep.py
Expected: tests_recursive=1 (tests/nightly_ha.py only), custom_components=0, tools=0 -- so the
non-recursive top-level command the finder cites happens to already cover the whole tree's one
site (nightly_ha.py sits at tests/ top level), and the seam_rule enumerates the demonstrated
phenomenon fully today, despite the closure-glob trap tools/audit/README.md warns about in
general (no other file is hiding in a subdirectory this round).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine: leads box (4-core Linux container),
requires CPython 3.14 (PEP 765 warning does not exist on 3.11/3.13 -- run with venv314, not
system python3).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
import warnings

t0, th0 = time.process_time(), time.thread_time()
assert sys.version_info >= (3, 14), "PEP 765 finally-return SyntaxWarning needs CPython >=3.14"


def scan(base):
    hits = []
    for root, dirs, files in os.walk(base):
        if "__pycache__" in root:
            continue
        for fn in files:
            if not fn.endswith(".py"):
                continue
            f = os.path.join(root, fn)
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                try:
                    compile(open(f).read(), f, "exec")
                except SyntaxError:
                    continue
            for w in caught:
                if issubclass(w.category, SyntaxWarning) and "finally" in str(w.message):
                    hits.append(f"{f}: {w.message}")
    return hits


tests_hits = scan("tests")
cc_hits = scan("custom_components")
tools_hits = scan("tools")

print(f"RESULT tests_recursive={len(tests_hits)} count sites={tests_hits}")
print(f"RESULT custom_components={len(cc_hits)} count")
print(f"RESULT tools={len(tools_hits)} count")
print(f"RESULT covered_by_top_level_glob={int(all('tests/nightly_ha.py' == h.split(':')[0] for h in tests_hits) and len(tests_hits) == 1)}")
print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [ln for ln in open('/proc/vmstat') if ln.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "n/a"
print(f"RESULT swapins={sw}")
