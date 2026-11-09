Fix review: merge 0a02619939e72e83cd52702aaf319e98049c4ba9

bus-nonce: e1dcaf4828faf4bc9a850d545c5062bb

## Evidence
- Re-check only. Head 0a02619939e72e83cd52702aaf319e98049c4ba9 is the same SHA as the earlier review that found no defect, so its diff is unchanged by construction (15 files, +469/-7 against the merge-base at this head).
- The earlier block was "codeql / Analyze (python) cancelled". At this head merge_train.py classify prints: GREEN 0a02619939e72e83cd52702aaf319e98049c4ba9 pending: none red: none (exit 0). See ev/classify.txt.
- merge-tree against origin/main reports no conflict (only the LEDGER-MERGE auto-resolution of tests/closures.json). See ev/merge-tree.txt.
- owed-reds output is in ev/owed-reds.txt (a list of required contexts); the classify result is GREEN, so none is red at this head.
- No fresh code review was run, as the brief directs.
