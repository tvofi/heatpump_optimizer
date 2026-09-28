#!/usr/bin/env python3
"""R5-INST-01 — finding.schema.json admits D0-D12 but not D13, so a D13
finder report cannot validate and a D13 harness path fails harness_path.

METRIC: count of dimension ids D0..D13 (the 14 briefs tabled in CLAUDE.md and
present under tools/audit/briefs/) that BOTH regexes in
tools/audit/finding.schema.json admit — properties.dimension.pattern for the
report's `dimension` field, and definitions.finding/... the harnesses[] items'
`^tools/audit/round[0-9]+/D(1[0-2]|[0-9])/` pattern for a D<k> harness path.

COMMAND (from a checkout/export root of tvofi/heatpump_optimizer):
    python3 tools/audit/round5/round-runner/R5-INST-01/schema_d13_admission.py
EXPECTED at baseline 1cc89e020fff9040a9d0090a27bf22bc1dd497f0 (tolerance: exact):
    RESULT briefs=14
    RESULT admitted_dimensions=13
    RESULT admitted_harness_paths=13
    RESULT excluded=D13
MACHINE: round runner's box (darwin, arm64); pure regex, no timing.

PERTURBATION (run in a copy; never the tree's file): change both patterns'
`1[0-2]` to `1[0-3]` -> admitted_dimensions=14, admitted_harness_paths=14,
excluded=none. Direction: up.

NULL CONTROL: D10 and D12 (the two ids adjacent to the band edge) both admit
under the unmodified patterns — the exclusion is D13 alone, not a range shape.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

SCHEMA = Path("tools/audit/finding.schema.json")


def main() -> int:
    schema = json.loads(SCHEMA.read_text())
    dim_pat = re.compile(schema["properties"]["dimension"]["pattern"])
    # harness items pattern, same regex text also used for evidence.harness_path
    hp_pat = re.compile(
        schema["properties"]["harnesses"]["items"]["pattern"]
    )
    ids = [f"D{k}" for k in range(14)]
    briefs = sorted(p.name for p in Path("tools/audit/briefs").glob("D*.md"))
    admitted_dim = [i for i in ids if dim_pat.search(i)]
    admitted_hp = [
        i for i in ids if hp_pat.search(f"tools/audit/round5/{i}/x.py")
    ]
    excluded = [i for i in ids if i not in admitted_dim or i not in admitted_hp]
    print(f"RESULT briefs={len(briefs)}")
    print(f"RESULT admitted_dimensions={len(admitted_dim)}")
    print(f"RESULT admitted_harness_paths={len(admitted_hp)}")
    print(f"RESULT excluded={','.join(excluded) if excluded else 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
