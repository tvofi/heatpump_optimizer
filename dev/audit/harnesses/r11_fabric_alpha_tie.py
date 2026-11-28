#!/usr/bin/env python3
"""Is `fabric_learning.fold_buffer_cooling`'s CMP_BOUND survivor at the alpha choice equivalent? (R11-ARCH-fabric-learner)

Written by the R11-ARCH-fabric-learner fixer for the survivor_triage verdict on
`fold_buffer_cooling CMP_BOUND` (`if observed < rate` -> `<=`). The two arms
differ only at the tie observed == rate, where the new rate is
``(1 - alpha) * rate + alpha * rate`` for one alpha or the other: `rate` in
exact arithmetic, so the choice can move only the rounding.

Each case draws a gated interval (seed 0), reads `observed` from one head
call, then calls the head and the operator's own mutant (the function's
source with that one comparison replaced, asserted to occur once) with `rate`
set to exactly that value: the tie. The control calls both with `rate` one
ulp either side of it, where the arms agree by construction, so a mutant
that moved anything off the tie would show there. It prints:

  * ``ties`` / ``tie_differing`` -- tie cases and those whose result differs at all;
  * ``tie_max_ulps`` -- the largest difference of the two new rates, in ulps of the head's;
  * ``nonties_differing`` -- one-ulp non-tie cases whose results differ (the control).

EXPECTED RESULT nonties_differing=0
EXPECTED RESULT tie_max_ulps=1

Run: PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r11_fabric_alpha_tie.py
"""
from __future__ import annotations

import inspect
import math
import random

from heatpump_optimizer import fabric_learning as f

CASES = 20000
BOUNDS = (0.0, 1e9)

SRC = inspect.getsource(f.fold_buffer_cooling)
assert SRC.count("if observed < rate") == 1, "mutation site not found exactly once"
NS = dict(vars(f))
exec(compile(SRC.replace("if observed < rate", "if observed <= rate"), "mutant", "exec"), NS)
MUT = NS["fold_buffer_cooling"]


def main() -> None:
    rng = random.Random(0)
    ties = tie_diff = ctl = ctl_diff = 0
    max_ulps = 0
    for _ in range(CASES):
        prev = rng.uniform(f.BUFFER_AMBIENT_TEMP + f.BUFFER_COOLING_MIN_DELTA + 1.0, 90.0)
        cur = rng.uniform(f.BUFFER_AMBIENT_TEMP + f.BUFFER_COOLING_MIN_DELTA, prev)
        dt = rng.uniform(f.BUFFER_COOLING_MIN_SAMPLE_HOURS, f.BUFFER_COOLING_MAX_SAMPLE_HOURS)
        first = f.fold_buffer_cooling(1.0, prev, cur, dt, BOUNDS)
        if first is None:
            continue
        obs = first[0]
        head = f.fold_buffer_cooling(obs, prev, cur, dt, BOUNDS)
        mut = MUT(obs, prev, cur, dt, BOUNDS)
        ties += 1
        if head != mut:
            tie_diff += 1
            max_ulps = max(max_ulps, round(abs(head[1] - mut[1]) / math.ulp(head[1])))
        for rate in (math.nextafter(obs, math.inf), math.nextafter(obs, -math.inf)):
            ctl += 1
            if f.fold_buffer_cooling(rate, prev, cur, dt, BOUNDS) != MUT(rate, prev, cur, dt, BOUNDS):
                ctl_diff += 1
    print(f"ties={ties} tie_differing={tie_diff} one_ulp_nonties={ctl}")
    print(f"RESULT tie_max_ulps={max_ulps}")
    print(f"RESULT nonties_differing={ctl_diff}")


if __name__ == "__main__":
    main()
