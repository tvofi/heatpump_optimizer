Fix review: merge afbf239f93975ae3d23f54e2b47eee3f5e7eee22
bus-nonce: 9049cdd2bf5387e8001e9f2cb2bc3e7e

Round 1, full scope: a records-only intake of four files under `dev/audit/rounds/round11/J/late-D3/top6/`, reviewed at the head.

## Evidence

- All four files are byte-identical to the finder box's output on `handoff/audit-r11-find-D3-top6` at fdd9e2d827 (blob hashes match: `evidence/blob_match.txt`).
- The new paths are classified INERT by the existing `dev/audit/` prefix in `tests/closure.py`, so `tests/entities.py` needs no new entry.
- D3-s1-02 keeps its low severity and is not routed to the judge, as the finder recorded it.
- Nothing in the diff names a home path or carries an opinion; the branch merges cleanly with main.
- Required contexts are green at the head (`evidence/checks-afbf239f.txt`); the dispatch packet is in `evidence/packet-afbf239f.md`.

## Notes

- None.
