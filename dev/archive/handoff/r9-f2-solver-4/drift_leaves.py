"""R9-F2.4 companion: the complete leaf census of the golden drift this PR claims.

`tests/env_drift.py --all` prints at most five leaves per scenario
(`for line in diffs[:5]`), so its log cannot answer "is every moved leaf the on
schedule, and does every one move the same way" -- the question a claim has to
answer before it asks a reviewer to accept 46 moved leaves on one reason. This
captures the named scenarios from the tree it is run in and writes them as JSON,
so the census is a diff of two dumps and not a reading of a truncated log:

    # in each tree, from its repository root
    PYTHONPATH=tests/hastub python3 \
        tools/audit/handoff/r9-f2-solver-4/drift_leaves.py --out base.json
    python3 tools/audit/handoff/r9-f2-solver-4/drift_leaves.py --diff base.json head.json

The diff arm is pure JSON and needs no solver. A leaf is reported as its dotted
path and its two values, so the direction is in the output rather than in an
adjective.
"""
from __future__ import annotations

import argparse
import json
import sys

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

#: The nine scenarios `env_drift.py --all` reported as unclaimed drift at this
#: PR's merge base, plus the five coordinator captures as a control: the D8 arm
#: of this fix gates a published value, so a coordinator fixture that stays
#: byte-identical is the measurement that the gate moves no published number in
#: the fixtures that carry one.
SCENARIOS = (
    "away_setback",
    "capacity_tariff",
    "dhw_cold_tank",
    "horizon_48h",
    "mild_windy_rain",
    "start_below_band",
    "valve_storage_flat_prices",
    "valve_storage_low_target",
    "valve_storage_small_tank",
    "coord_minimal",
    "coord_dhw",
    "coord_two_zone",
    "coord_grid_fee",
    "coord_all_features",
)


def flatten(value, path=""):
    """Every leaf of a capture, as (dotted path, value)."""
    if isinstance(value, dict):
        for k, v in value.items():
            yield from flatten(v, f"{path}.{k}" if path else str(k))
    elif isinstance(value, (list, tuple)):
        for i, v in enumerate(value):
            yield from flatten(v, f"{path}[{i}]")
    else:
        yield path, value


def capture(names):
    import golden

    out = {}
    for name in names:
        if name.startswith("coord_"):
            out[name] = golden.capture_coordinator(
                golden.coordinator_scenarios()[name]
            )
        else:
            out[name] = golden.capture(name, dict(golden.SCENARIOS[name]))
        print(f"captured {name}", file=sys.stderr, flush=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="write this tree's captures")
    ap.add_argument("--diff", nargs=2, metavar=("BASE", "HEAD"),
                    help="diff two dumps written by --out")
    ap.add_argument("--scenarios", default=",".join(SCENARIOS))
    a = ap.parse_args()

    if a.diff:
        with open(a.diff[0], encoding="utf-8") as fh:
            base = json.load(fh)
        with open(a.diff[1], encoding="utf-8") as fh:
            head = json.load(fh)
        moved = {}
        for name in sorted(set(base) | set(head)):
            b = dict(flatten(base.get(name, {})))
            h = dict(flatten(head.get(name, {})))
            rows = [(k, b.get(k, "<absent>"), h.get(k, "<absent>"))
                    for k in sorted(set(b) | set(h)) if b.get(k) != h.get(k)]
            if rows:
                moved[name] = rows
            print(f"{name:28s} leaves_moved={len(rows)}")
        fields = {}
        directions = {}
        for rows in moved.values():
            for key, was, now in rows:
                field = key.split("[")[0].split(".")[-1]
                fields[field] = fields.get(field, 0) + 1
                directions[f"{was} -> {now}"] = directions.get(
                    f"{was} -> {now}", 0) + 1
        print(f"RESULT scenarios_moved={len(moved)} count")
        print(f"RESULT leaves_moved={sum(len(r) for r in moved.values())} count")
        for field, n in sorted(fields.items()):
            print(f"RESULT leaves_by_field[{field}]={n} count")
        for d, n in sorted(directions.items()):
            print(f"RESULT leaves_by_direction[{d}]={n} count")
        for name, rows in moved.items():
            for key, was, now in rows:
                print(f"LEAF {name}.{key}: {was!r} -> {now!r}")
        return 0

    names = a.scenarios.split(",")
    dump = capture(names)
    text = json.dumps(dump, default=str, sort_keys=True)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"wrote {a.out} ({len(text)} bytes, {len(dump)} scenarios)")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
