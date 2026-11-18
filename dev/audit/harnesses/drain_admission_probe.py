#!/usr/bin/env python3
"""How much of a drain's budget admission charge reach_skip frees.

    python3 -I dev/audit/harnesses/drain_admission_probe.py TREE OUT.json \
        -- --scope full --drain DIR --max 320 --jobs 4 --seed 20261106
    python3 -I dev/audit/harnesses/drain_admission_probe.py --summary OUT.json

TREE is a checkout whose `tests/mutation_table.py` runs unmodified: the probe
replaces `drive_pool` in the imported module, never in the tree, because
tests/entities.py reads that file's text and a probe written into it turns
the entities baseline red. main() then draws, runs the traced baselines and
the null control exactly as the nightly does, and hands the pool to the
replacement, which writes one row per mutant and stops before any mutant
runs:

* need      -- what admission charges the mutant: its shared drivers at the
  schedule's own `cost`;
* need_free -- the share of it on pairs `reach_skip` frees, which no run ever
  spends.

`--summary` prints the totals. Without `--shard`, `--max N` draws the union
of the N/4-per-shard slices one run's four shards would deal under that seed
(`drain_pool` caps at max times the shard count and deals whole anchors).
The cost seconds are this machine's baselines: the share is the figure, not
the hours.
"""
from __future__ import annotations

import json
import statistics
import sys


def summary(path: str) -> int:
    with open(path, encoding="utf-8") as fh:
        rows = json.load(fh)["rows"]
    if not rows:
        print("no rows: the probe saw an empty pool")
        return 1
    pairs = sum(len(r["drivers"]) for r in rows)
    free = sum(len(r["free"]) for r in rows)
    need = sum(r["need"] for r in rows)
    need_free = sum(r["need_free"] for r in rows)
    print(f"mutants {len(rows)}; shared pairs {pairs}, reach-free {free} "
          f"({100 * free / pairs:.0f}%)")
    print(f"admission charge {need / 3600:.1f} h, reach-free "
          f"{need_free / 3600:.1f} h ({100 * need_free / need:.0f}%)")
    print("median charge per mutant: "
          f"{statistics.median(r['need'] for r in rows) / 60:.1f} min charged, "
          f"{statistics.median(r['need'] - r['need_free'] for r in rows) / 60:.1f}"
          " min without the reach-free pairs")
    return 0


def probe(tree: str, out: str, argv: list[str]) -> int:
    sys.path.insert(0, f"{tree}/tests")
    import mutation_table as mt

    def replacement(pool, workers, cost, drive, settle=None, deadline=None,
                    **_):
        cells = dict(zip(drive.__code__.co_freevars,
                         (c.cell_contents for c in drive.__closure__)))
        reaches = cells["reaches"]
        rows = []
        for m in pool:
            shared = [s for s in m["drivers"] if s not in mt.EXCLUSIVE]
            free = [s for s in shared if mt.reach_skip(reaches.get(s), m)]
            rows.append({"key": mt.triage_key(m), "anchor": m.get("anchor"),
                         "drivers": shared, "free": free,
                         "need": sum(cost.get(s, 0.0) for s in shared),
                         "need_free": sum(cost.get(s, 0.0) for s in free)})
        with open(out, "w", encoding="utf-8") as fh:
            json.dump({"cost": cost, "rows": rows}, fh, indent=1)
        print(f"ADMISSION PROBE: {len(rows)} row(s) written", flush=True)
        raise SystemExit(0)

    mt.drive_pool = replacement
    return mt.main(argv)


def main(argv: list[str]) -> int:
    if argv[:1] == ["--summary"] and len(argv) == 2:
        return summary(argv[1])
    if len(argv) < 3 or "--" not in argv or argv.index("--") != 2:
        print(__doc__, file=sys.stderr)
        return 2
    return probe(argv[0], argv[1], argv[3:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
