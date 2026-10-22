Fix review: merge 9da4dcab96eca8278a81fa4589faa865a69d3803

bus-nonce: d58c3faf12c24415d9746952cc76c278

## Findings

(none this PR leaves unsettled)

## Evidence

Full review 0d29933dcd050f1977a2130e9157044fe428f637 at 6bee9961fa8bbb90d50392fee75a64ab88a3d8e2, then the delta verdict at c2c5a8969dc08c548624d5160d5e43482c0ce392. This is a delta review of c2c5a896..9da4dcab96eca8278a81fa4589faa865a69d3803 beyond main: three pure roster carry appends (R10-CI-LAYOUT-P2 and two for R10-FLOW-JIDOKA), each equal to its source file; brief_lint rc 0; merge-tree against origin/main clean; no host paths in added lines. Details: evidence/delta-checks.txt in this verdict commit.

The head also moved by merges of origin/main fef4a1351 and roster commits; the ref_privacy ci_probe.py refusal seen at the older base is resolved by the merge with origin/main (0 refused there).
