"""P5 probe: two told quantities of the sysid fit that the adoption interval
does not price -- the COP step() is told (cop=) and the outdoor reading. The
delivered heat is power x COP and the heat loss is heat / (indoor - outdoor),
so a COP or outdoor offset moves the fitted UA one-for-one. No width term in
slab_ua_adoption_halfwidth (profile, intercept prior, slab pair) carries either.

Per arm over the three shipped presets (tests/stress.py BUILDINGS), noise-free:
admitted nights, admitted with |UA bias| > 10 % (the gate's bar), and admitted
nights outside the half-width they were admitted on. Exit 1 when any arm
admits past the bar.
  --null  every arm at zero offset: expected 0 admitted past the bar, 0 misses
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep-P5/probe_told.py [--null]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import enumerate as E  # noqa: E402

ARMS = [({"cop_true": 1.10}, "true COP x1.10"), ({"cop_true": 1.15}, "true COP x1.15"),
        ({"cop_true": 0.85}, "true COP x0.85"),
        ({"outdoor_bias": 1.5}, "outdoor sensor +1.5 K"), ({"outdoor_bias": 2.5}, "outdoor sensor +2.5 K"),
        ({"outdoor_bias": -2.5}, "outdoor sensor -2.5 K")]


def main() -> int:
    null = "--null" in sys.argv
    past = 0
    for inj, label in ARMS:
        inj = {} if null else inj
        adm = bad = miss = 0
        worst = 0.0
        for name in E.M.BUILDINGS:
            b, a, hw = E.run_cell(name, inj, 0)
            adm += a
            if a and b is not None:
                bad += abs(b) > E.BAR
                miss += abs(np.log1p(b)) > hw
                worst = max(worst, abs(b))
        past += bad
        print(f"{label:24s} admitted={adm}/3 past_bar={bad} misses={miss} worst_admitted_bias={worst:.4f}")
    print(f"RESULT {'null' if null else 'tree'} admitted_past_bar={past}")
    return 1 if past else 0


if __name__ == "__main__":
    sys.exit(main())
