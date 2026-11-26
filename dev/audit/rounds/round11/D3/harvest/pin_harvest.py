#!/usr/bin/env python3
"""Pin the kills an audit box measured, through the ledger's own drain.

A finder box that drives mutants of unpinned sites measures kills, but
nothing writes them to the ledger, so every later round re-screens them.
`tests/mutation_table.py --drain` is the tracked path that drives unpinned
stock and writes `killed_by` rows; its pool is a seeded slice of the whole
stock (`drain_pool`), so it cannot be pointed at the anchors a box named.
This driver narrows that pool and changes nothing else: the drive, the kill
rule, the baseline, the null control, `pin_results`' whole-anchor rule and
`write_drain` are mutation_table's own, and the rows land through
`apply_pins`' re-check against this tree's inventory (same anchor, same
`old` text, not already disposed).

    pin_harvest.py drive ANCHORS.json OUT_DIR [mutation_table args...]
    pin_harvest.py apply OUT_DIR
    pin_harvest.py --self-test

ANCHORS.json is a JSON list of anchor keys (`FILE:SCOPE KIND DIGEST`). An
anchor that is not unpinned at HEAD is never driven (drain_pool only sees
the unpinned stock), and is printed as `NOT UNPINNED`. Survivors are listed
in OUT_DIR/survivors.txt for a human verdict and never written.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT / "tests"))

import mutation_table as m  # noqa: E402


def narrowed(drain_pool, wanted: set[str]):
    """`drain_pool` over only the unpinned sites whose anchor is wanted."""
    def pool(unpinned, *args, **kwargs):
        return drain_pool([s for s in unpinned if s["anchor"] in wanted],
                          *args, **kwargs)
    return pool


def drive(anchors_path: str, out: str, rest: list[str]) -> int:
    wanted = set(json.loads(Path(anchors_path).read_text()))
    budgets, sites = m.load_budgets(), m.inventory()
    loose = {s["anchor"] for s in m.unpinned_sites(budgets, sites)}
    for a in sorted(wanted - loose):
        print(f"NOT UNPINNED {a}")
    n = sum(1 for s in sites if s["anchor"] in wanted & loose)
    print(f"HARVEST -- {len(wanted & loose)} of {len(wanted)} anchor(s) "
          f"unpinned at HEAD, {n} site(s)")
    m.drain_pool = narrowed(m.drain_pool, wanted)
    return m.main(["--scope", "full", "--drain", out, "--max", str(max(n, 1)),
                   *rest])


def apply(out: str) -> int:
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
                          capture_output=True, check=True).stdout.strip()
    status = m.apply_pins(out, head)
    print(f"HARVEST APPLY: {status}")
    return 0 if status in ("changed", "skip-unchanged",
                           "skip-nothing-killed") else 1


def self_test() -> int:
    seen = []
    pool = narrowed(lambda u, *a, **k: seen.append((u, a, k)) or u, {"x"})
    got = pool([{"anchor": "x"}, {"anchor": "y"}, {"anchor": "x"}], 1, k=2)
    ok = (got == [{"anchor": "x"}, {"anchor": "x"}]
          and seen[0][1:] == ((1,), {"k": 2}))
    print(f"  {'ok  ' if ok else 'FAIL'} narrowed keeps only wanted anchors "
          f"and passes the drain arguments through")
    empty = narrowed(lambda u, *a, **k: u, set())([{"anchor": "x"}])
    ok2 = empty == []
    print(f"  {'ok  ' if ok2 else 'FAIL'} an empty anchor list drives nothing")
    return 0 if ok and ok2 else 1


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return self_test()
    if len(argv) >= 3 and argv[0] == "drive":
        return drive(argv[1], argv[2], argv[3:])
    if len(argv) == 2 and argv[0] == "apply":
        return apply(argv[1])
    print(__doc__.strip().split("\n\n")[2], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
