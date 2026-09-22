#!/usr/bin/env python3
"""D0-c mutation prover: apply ONE named mutation to a checkout's solver.

COMMAND (from the tree root; restore with the git checkout the script prints):
  python3 tools/audit/round5/D0/seat-c/mutate.py <checkout> <MUT>
  git -C <checkout> checkout -- custom_components/heatpump_optimizer/optimizer.py

MUTATIONS (each is a subset of the shipping change, applied by exact-string
substitution with a count-of-one assertion, so a mutation that no longer
matches the source refuses instead of silently doing nothing):

  M2p_cut_only       _MULTI_START_SOLVES 6 -> 4           (the cut alone)
  M2s_seeds_only     both appended seeds deleted          (the seeds alone)
  M2_seeds_and_cut   _MULTI_START_SOLVES 6 -> 4, both appended seeds deleted
  M3_warm_none       _warm_start_starts returns None      (the #1295 revert)

#1293's knob (the L-BFGS-B stop rule) is NOT in this diff: it was reverted
before this branch's handoff, and ``_LBFGSB_FTOL`` no longer exists in the
tree, so there is no M1 here.

EXPECTED reddens, from `mutation_proof.sh`:
  M2p exactly the #1294 cut check, because production and the seeds-kept/cut-4
      arm become the same configuration.
  M2s no check: the seeds are pinned structurally (the both-paths candidate
      count) and by no behavioural check, because their own cells move inside
      the noise band -- see the note under the cut check in tests/optimality.py.
  M2  the #1294 cut check and the both-paths seed-count check.
  M3  exactly the #1295 warm check.
No check outside its own finding's name moves under any of the four.
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


CUT = "_MULTI_START_SOLVES = 6"
SEED85 = """            starts.append(
                np.minimum(
                    _price_ranked_start(prices, energy * 0.85, p_max, dt),
                    headroom,
                )
            )
"""
SEED15 = """        starts.append(
            _price_ranked_start(prices, baseline_energy * 0.15, p_max, dt)
        )
"""
WARM = """        prev = getattr(self, "_prev_shipped_plan", None)
        if prev is None or len(prev) != n_steps:
            return None
        return (np.asarray(prev, dtype=float),)
"""

if name == "M2p_cut_only":
    sub(CUT, "_MULTI_START_SOLVES = 4")
elif name == "M2s_seeds_only":
    sub(SEED85, "")
    sub(SEED15, "")
elif name == "M2_seeds_and_cut":
    sub(CUT, "_MULTI_START_SOLVES = 4")
    sub(SEED85, "")
    sub(SEED15, "")
elif name == "M3_warm_none":
    sub(WARM, "        return None\n")
else:
    raise SystemExit(f"unknown mutation {name!r}")

open(P, "w").write(s)
print(f"applied {name} to {P} ({len(src) - len(s):+d} chars)")
