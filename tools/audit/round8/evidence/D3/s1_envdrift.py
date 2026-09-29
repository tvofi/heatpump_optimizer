#!/usr/bin/env python3
"""s1_envdrift.py -- run tests/env_drift.py --all <BASE> in a tree whose HEAD IS <BASE>.

Metric: env_drift's own exit status and its `N UNCLAIMED DRIFT(S)` count for the
working tree (mutated or not) against the baseline SHA, using the shared warmed
cache for the baseline side.

Why a wrapper: an audit tree is a detached worktree AT the baseline SHA with
uncommitted edits, and env_drift.main() refuses a ref that resolves to HEAD
(self-comparison guard, tests/env_drift.py:2277-2281). The seat may not commit.
The wrapper imports tests/env_drift.py unmodified and patches only
env_drift._rev(repo, "HEAD") to return a sentinel SHA, so the guard passes; every
other call (the ref, the cache key, the worktree, the capture subprocess, the
comparison) is the production instrument byte-for-byte. The branch side is the
working tree, which is what the gate compares on a PR.

Command (from the tree root; wrap in the shared flock, env_drift adds a worktree):
  flock /home/claude/audit-r8/envdrift.lock env PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
    python3 tools/audit/round8/D3/s1_envdrift.py cdf82daabcfe3777d98b31489f36df5555ec9d82
Expected on the unmodified baseline tree: rc=0, RESULT unclaimed_drift=0 (exact).
Baseline: cdf82daabcfe3777d98b31489f36df5555ec9d82; machine: 4-vCPU cloud container.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import importlib.util
import io
import re
import sys
import time
import contextlib

BASE = sys.argv[1] if len(sys.argv) > 1 else "cdf82daabcfe3777d98b31489f36df5555ec9d82"
SENTINEL = "f" * 40

spec = importlib.util.spec_from_file_location("env_drift", os.path.abspath("tests/env_drift.py"))
ed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ed)
_orig_rev = ed._rev


def _rev(repo, rev):
    if rev == "HEAD":
        return SENTINEL
    return _orig_rev(repo, rev)


ed._rev = _rev
# The cache key is NOT touched: if the shared warmed entry misses (e.g. the
# interpreter's package inventory changed after warming), the baseline is
# captured from scratch, honestly, and RESULT cache_hit=0 says so.
sys.argv = ["tests/env_drift.py", "--all", BASE]
t0 = time.monotonic()
buf = io.StringIO()


class Tee(io.TextIOBase):
    def write(self, s):
        sys.__stdout__.write(s)
        buf.write(s)
        return len(s)

    def flush(self):
        sys.__stdout__.flush()


with contextlib.redirect_stdout(Tee()):
    try:
        rc = ed.main()
    except SystemExit as e:  # pragma: no cover
        rc = e.code
    except Exception as e:  # capture crash
        print(f"CRASH {e.__class__.__name__}: {e}")
        rc = 99
out = buf.getvalue()
m = re.search(r"(\d+) UNCLAIMED DRIFT", out)
drift_names = re.findall(r"^\s+DRIFT (\S+):", out, re.M)
print(f"RESULT envdrift_rc={rc} count")
print(f"RESULT unclaimed_drift={int(m.group(1)) if m else 0} count")
print(f"RESULT drifted_scenarios={','.join(sorted(set(n.rstrip(':') for n in drift_names))) or '-'}")
print(f"RESULT cache_hit={int('reused' in out)} count")
print(f"RESULT wall_s={time.monotonic() - t0:.1f} s (provisional)")
try:
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
except OSError:
    pass
sys.exit(0 if rc == 0 else 1)
