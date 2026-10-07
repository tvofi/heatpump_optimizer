Fix review: merge 5efb428db16496dad6a81795fbe53b22415c2e20
bus-nonce: 62e4416348eca0697adbb7e593d78f9c

## Mechanical Review

### Check 1: Three-dot diff integrity

**Status: PASS**

Compared PR's three-dot diffs at both commit heads:
- Old head (bb3634f6): 1040 lines
- New head (5efb428d): 1040 lines

Apart from `tools/audit/bugclasses.json`, all files have identical added/removed lines. Only context line numbers changed due to merge resolution (expected).

File differences in hunk headers:
```
index 44f314e2..3a7992f0 100644  (old)
index 71af53a2..a013cb53 100644  (new)

@@ -3653,6 +3653,22 @@  (old)
@@ -3654,6 +3654,22 @@  (new)
```

These are harmless re-indexing and line-number shifts from the merge.

### Check 2: bugclasses.json integrity

**Status: PASS**

- JSON parsing: Valid
- Conflict markers: None
- Key preservation: All 84 existing `_rca` keys preserved
- New entries: Single addition of `R9-RCA-1990` (as required)

Main _rca entries: 84
New _rca entries: 85 (added R9-RCA-1990 only)

### Check 3: Merge tree cleanness

**Status: PASS**

```
$ git merge-tree --write-tree origin/main 5efb428d
3d2ef5b7e086fa53942846dde2b354dc077f7a46
Exit code: 0
```

No conflicts, tree merges cleanly.

### Check 4: CI check-runs at new head (5efb428d)

**Status: PASS**

Failures and cancellations:
- `delivery-status`: failure (inherited from main, does not block)
- `nightly-status`: failure (inherited from main, does not block)
- `budget-raise-gate`: cancelled (not triggered on main; cancellation is not a blocking failure)

All other checks: success, skipped, or neutral.

No non-inherited red checks that would block merge.

## Summary

All four mechanical checks pass. The PR merges cleanly from origin/main with only the expected bugclasses.json merge resolution (addition of R9-RCA-1990 to the _rca registry, matching the new RCA document). CI shows only inherited reds that do not block per the merge policy.

**Verdict: Ready to merge at commit 5efb428d.**
