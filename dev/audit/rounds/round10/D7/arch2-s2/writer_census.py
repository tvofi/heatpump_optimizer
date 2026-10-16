#!/usr/bin/env python3
"""ARCH2-s2 (round 10, D7): the coordinator writer census, attribute by attribute.

Metric: coordinator_multiassigned_attrs, tests/structure.py's own definition (coordinator_writers:
        attributes stored on the coordinator by more than one function, in or out of the class),
        on the archscore's flattened copy of ROOT (counter C4 on), printed per attribute with its
        writers so a cohesive group can be read off the census rather than asserted.
Count key: the static writer set of each attribute in the measured tree.
Instrumented symbol: tests/structure.py:coordinator_writers over coordinator:HeatPumpOptimizerCoordinator.
Command:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s2/writer_census.py [ROOT] [--only PREFIX]
Perturbation: add a second writer of any single-writer attribute; the census count rises by one.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


REPO = repo_root(__file__)
sys.path.insert(0, str(REPO / "tools" / "audit"))

from archscore import counters as K, vector  # noqa: E402


def census(root: Path) -> dict[str, set[str]]:
    with tempfile.TemporaryDirectory(prefix="arch2s2-") as tmp:
        K.flatten(root.resolve(), Path(tmp), inline=True)
        S = vector.load_structure(Path(tmp))
        S.seam_metrics = vector._stub_seams
        got: dict = {}
        orig = S.coordinator_writers

        def spy(roles):
            got.update(orig(roles))
            return got
        S.coordinator_writers = spy
        S.measure()
        return got


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    root = Path(args[0]) if args else REPO
    w = census(root)
    multi = {a: ws for a, ws in w.items() if len(ws) > 1}
    for a in sorted(multi):
        ws = sorted(x.split(".")[-1] if x.startswith("coordinator:HeatPumpOptimizerCoordinator.") else x
                    for x in multi[a])
        init_only = all(x.startswith("_init_") or x == "__init__" for x in ws)
        print(f"{a:40s} {len(ws)} {'INIT ' if init_only else ''}{', '.join(ws)}")
    n_init_plus_one = sum(
        1 for ws in multi.values()
        if len(ws) == 2 and sum(1 for x in ws if x.split('.')[-1].startswith(('_init_', '__init__'))) == 1)
    print(f"RESULT coordinator_attrs={len(w)} count")
    print(f"RESULT coordinator_multiassigned_attrs={len(multi)} count")
    print(f"RESULT init_plus_one_mutator={n_init_plus_one} count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
