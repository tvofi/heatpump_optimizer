#!/usr/bin/env python3
"""D13-s3 enumerator for D13.M4 and D13.M5: the window's merges, one per line.

METRIC: none -- prints the universe both steps range over: every first-parent
merge commit of the baseline whose committer date is in [W0, W1]
(d13s3lib.W0/W1), as `<merge sha> #<pr number>` from `/commits/<sha>/pulls`.
A merge whose pull request the API does not name prints `#?` and is counted
under `api_failures` (stderr), never dropped.

COMMAND (from the export root):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D13/s3/enum_merges.py
EXPECTED at baseline 92d38ecb: 271 lines, exact (a closed window of history).
MACHINE: any; network-bound.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d13s3lib as L  # noqa: E402

if __name__ == "__main__":
    ms = L.window_merges()
    prs = L.pmap(L.pr_of, [s for s, _ in ms])
    miss = 0
    for (s, _), p in zip(ms, prs):
        n = (p or {}).get("number")
        miss += n is None
        print(f"{s} #{n if n is not None else '?'}")
    print(f"api_failures={len(L.FAILURES)} unnamed={miss}", file=sys.stderr)
