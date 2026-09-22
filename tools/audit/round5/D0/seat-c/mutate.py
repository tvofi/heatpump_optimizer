#!/usr/bin/env python3
"""D0-c mutation prover: apply ONE named mutation to a checkout's solver.

COMMAND (from the tree root; restore with the git checkout the script prints):
  python3 tools/audit/round5/D0/seat-c/mutate.py <checkout> <MUT>
  git -C <checkout> checkout -- custom_components/heatpump_optimizer/optimizer.py

MUTATIONS (each is a subset of the shipping change, applied by exact-string
substitution with a count-of-one assertion, so a mutation that no longer
matches the source refuses instead of silently doing nothing):

  M3_warm_none       _warm_start_starts returns None      (the #1295 revert)

WHY THERE IS ONE. This branch shipped three D0 knobs and now ships one. The
raised refinement cut and its two appended seeds (#1294) were dropped on cost
and on non-reproducibility, so their source literals -- ``_MULTI_START_SOLVES =
6``, the 0.85-energy seed and the 0.15-energy seed -- are not in the tree and
the M2p/M2s/M2 mutations that reverted them can no longer match; they were
removed with the finding rather than left to refuse on a vanished literal. That
finding is deferred, and its instruments travel with it: the finder's
``../seat-a/race.py`` and ``../seat-a/perturb_prev.py``, and this seat's
``arms.py`` (which still arms the cut at run time) and ``regression.py``.

#1293's knob (the L-BFGS-B stop rule) is NOT in this diff: it was refuted on
money before this branch's handoff, and ``_LBFGSB_FTOL`` no longer exists in
the tree, so there is no M1 here. Its re-application instrument is
``refute_1293.py`` beside this file.

EXPECTED redden, from `mutation_proof.sh`:
  M3  exactly the #1295 checks -- the extra-candidate check (the seam's first
      call carries one candidate fewer) and, where the handed-in plan is beaten
      by the solve's own refinement set, the no-worse check.
No check outside the #1295 finding's name moves.
"""
import os
import sys

ROOT, name = sys.argv[1], sys.argv[2]
_P = os.path.join("custom_components", "heatpump_optimizer", "optimizer.py")
P = os.path.join(ROOT, _P)
src = open(P).read()
s = src


def sub(old, new):
    global s
    n = s.count(old)
    assert n == 1, f"{name}: {n} matches for {old[:70]!r}"
    s = s.replace(old, new)


WARM = """        prev = getattr(self, "_prev_shipped_plan", None)
        if prev is None or len(prev) != n_steps:
            return None
        return (np.asarray(prev, dtype=float),)
"""

if name == "M3_warm_none":
    sub(WARM, "        return None\n")
else:
    raise SystemExit(f"unknown mutation {name!r}")

open(P, "w").write(s)
print(f"applied {name} to {P} ({len(src) - len(s):+d} chars)")
