#!/usr/bin/env python3
"""Merge the pre-screen's passes into one record per mutant.

The pre-screen ran in two passes: the assertion scripts for all 34 mutants,
then the differential gate (`env_drift.py --all`) for every mutant no
assertion script actually failed on.  This folds the second pass's
`tests/env_drift.py --all` row into the first pass's record.

Run (from the repository root):

    python3 tools/audit/round3/D3/merge_runs.py \
        tools/audit/round3/D3/prescreened.json \
        tools/audit/round3/D3/prescreened_capture.json \
        tools/audit/round3/D3/prescreened_capture_b.json

Writes tools/audit/round3/D3/prescreened_merged.json.
Baseline SHA: ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

def main() -> int:
    base = json.loads(Path(sys.argv[1]).read_text())
    rows = {r["id"]: r for r in base["prescreened"]}
    for extra in sys.argv[2:]:
        p = Path(extra)
        if not p.exists():
            continue
        for r in json.loads(p.read_text())["prescreened"]:
            tgt = rows.get(r["id"])
            if tgt is None:
                rows[r["id"]] = r
                continue
            # Merge by script name; a later pass's row wins.
            by = {x["script"]: x for x in tgt.get("ran", [])}
            for x in r.get("ran", []):
                by[x["script"]] = x
            tgt["ran"] = [by[k] for k in sorted(by)]
            if r.get("drift") and r["drift"].get("killed") is not None:
                tgt["drift"] = r["drift"]
    out = {"baseline_sha": base["baseline_sha"], "tier": base["tier"],
           "prescreened": [rows[k] for k in sorted(rows)]}
    Path("tools/audit/round3/D3/prescreened_merged.json").write_text(
        json.dumps(out, indent=1))
    n_drift = sum(1 for r in out["prescreened"]
                  if any(x["script"] == "tests/env_drift.py --all"
                         for x in r.get("ran", [])))
    print(f"RESULT merged_mutants={len(out['prescreened'])} mutants")
    print(f"RESULT with_differential_gate={n_drift} mutants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
