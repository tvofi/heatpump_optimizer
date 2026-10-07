Fix review: merge 189b57b614807bd9900bc2af02f7a033e0c3d90e

bus-nonce: 524f41df97c6d3f88ce3352bdb4c3e08

## Delta Review

The head moved from b956925c to 189b57b6 due to an automatic merge of main after PR #2015 (R9-RO-8) moved `tools/audit/bugclasses.json` to `dev/audit/config/bugclasses.json`.

### Mechanical Check 1: Three-dot diffs (old vs new heads)

All files except `bugclasses.json` have identical added and removed lines (301 additions/removals each):
- closure.py: code changes preserved despite line number shifts due to file structure changes in the merge
- stress.py: code changes preserved

For bugclasses.json, the same content appears at different paths:
- Old head (b956925c): at `tools/audit/bugclasses.json`
- New head (189b57b6): at `dev/audit/config/bugclasses.json`

The R9-RCA-stress-recording citation was added identically in both versions:
- BULK-2-I2 entry now includes "R9-RCA-stress-recording" in the rca array
- New R9-RCA-stress-recording entry with full I2 definition present in both

### Mechanical Check 2: New head state at 189b57b6

✓ `dev/audit/config/bugclasses.json` parses and has no conflict markers
✓ `tools/audit/bugclasses.json` does not exist
✓ `python3 tools/audit/fold_ledger.py check` reports 0 violations

### Mechanical Check 3: Merge tree

✓ `git merge-tree --write-tree origin/main 189b57b6` exits 0 (no conflicts)

### Mechanical Check 4: CI check-runs at 189b57b6

In progress (non-blocking):
- pr-contract, closures, Analyze (python), browser, instrument-self-tests, env-matrix, Analyze (javascript-typescript), typing, coverage, fast (3.14)

Failures (non-blocking per task):
- delivery-status: main's status, not this PR's responsibility
- nightly-status: main's status, not this PR's responsibility
- budget-raise-gate: cancelled (expected after merge of #2015)

## Conclusion

All mechanical gates pass. The delta is purely the file path move of bugclasses.json from tools/audit to dev/audit/config, with identical content and code changes preserved.
