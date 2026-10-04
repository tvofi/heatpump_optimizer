#!/usr/bin/env python3
"""The architecture score still measures today's tree (R9-EG-A1).

tests/arch_score.py measures a pinned tree and stored history, so it cannot notice the instrument
going blind on the tree it is run against: a coordinator renamed, a role the engine no longer finds, a
module the metrics cannot parse. This is that check, and it is the only part that reads the working tree
-- so it is its own script, and a change to the integration selects it and not the calibration.

  * every score metric and every tripwire is a number on this tree;
  * a tree compared with itself reads NULL, and the report names no metric;
  * the coordinator class the metrics key on is the one ``tests/structure.py`` keys on.

    PYTHONPATH=tests/hastub python3 tests/arch_score_head.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tools" / "audit"))

from harness import Results  # noqa: E402

from archscore import counters, score, vector  # noqa: E402
from archscore.metrics import common  # noqa: E402

R = Results("architecture score on today's tree (R9-EG-A1)")


def main() -> int:
    here = vector.measure(ROOT)
    missing = [m for m in (*vector.SCORE_METRICS, *vector.GATE_ONLY) if not isinstance(here.get(m), int)]
    R.check("every score metric and tripwire measures on today's tree", not missing,
            f"no value for {missing}; errors {[v for k, v in here.items() if k.endswith('_error')]}")
    R.check("a tree against itself reads NULL", score.delta(here, here)["verdict"] == "NULL")
    R.check("a tree against itself reports no metric moved",
            score.report(here, here).count("\n") == 0, score.report(here, here))
    structure = vector.load_structure(ROOT)
    R.check("the metrics and tests/structure.py key on the same coordinator class",
            common.COORD_CLASS == structure.COORDINATOR_CLASS_NAME,
            f"{common.COORD_CLASS} vs {structure.COORDINATOR_CLASS_NAME}")
    trees = structure.module_trees()
    shared, adjacent = structure.duplicate_clones(trees), counters.gapped_clones(structure, trees, gap=0)
    R.check("the score's clone census with no gap is the ratchet's census (C3 only widens it)",
            adjacent == shared, f"{len(adjacent)} classes vs {len(shared)}")
    wide = counters.gapped_clones(structure, trees)
    R.check("...and with any gap it keeps every class the ratchet finds",
            all(any(set(g) <= set(w) for w in wide) for g in shared))
    return R.close("ARCHITECTURE SCORE HEAD CHECKS")


if __name__ == "__main__":
    raise SystemExit(main())
