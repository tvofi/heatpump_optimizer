#!/usr/bin/env python3
"""R5-INST-01 fix-seat property probe — the finder's harness reads two of the
schema's dimension-band patterns; this reads all of them, at both ends of the
range the fix widens (D12 null control, D13 the fix, D14 the clamp that must
stay refused). It walks the schema generically, so a fifth band pattern added
anywhere is counted rather than assumed absent.

COMMAND (from a checkout root): python3 tools/audit/round5-fix/R5-INST-01/probe_band_edges.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

SCHEMA = Path("tools/audit/finding.schema.json")
SITES = {
    "properties.dimension": ("properties", "dimension"),
    "properties.harnesses.items": ("properties", "harnesses", "items"),
    "definitions.evidence.harness_path": ("definitions", "evidence", "properties", "harness_path"),
    "definitions.finding.id": ("definitions", "finding", "properties", "id"),
}
SAMPLES = {
    "properties.dimension": "D{k}",
    "properties.harnesses.items": "tools/audit/round5/D{k}/x.py",
    "definitions.evidence.harness_path": "tools/audit/round5/D{k}/x.py",
    "definitions.finding.id": "D{k}-01",
}
IDS = (12, 13, 14)


def band_patterns(node, path):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "pattern" and isinstance(v, str) and "1[0-" in v:
                yield path, v
            else:
                yield from band_patterns(v, path + [k])
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from band_patterns(v, path + [i])


def main() -> int:
    schema = json.loads(SCHEMA.read_text())
    found = list(band_patterns(schema, []))
    print(f"RESULT band_patterns_in_schema={len(found)}")
    for name, key in SITES.items():
        node = schema
        for k in key:
            node = node[k]
        pat = re.compile(node["pattern"])
        cells = ",".join(
            f"D{k}={'yes' if pat.search(SAMPLES[name].format(k=k)) else 'no'}"
            for k in IDS
        )
        print(f"RESULT {name}: {cells}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
