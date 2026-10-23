Fix review: merge 42cb7d1692680f3ebb41477d86be68bcc0a36321

Delta re-check of 42cb7d16 (conflict-resolution merge 6d3770f39 into 05b9c1d5); the 05b9c1d5 verdict is not carried. Delta only; no mutation or harness re-run (delta touches only tools/audit/seat/INSTRUMENTS.md prose).

RESULT tree-vs-merge-tree: git merge-tree 05b9c1d5 57b7b4994 conflicts only in INSTRUMENTS.md; diff of its tree against 42cb7d16 is exactly the 3 conflict-marker lines removed (ev/tree-delta.diff). PASS.
RESULT rows: flow_metrics.py (#2645) and gh_read.py (#2639) rows both kept; 2 matches, 0 duplicate rows (also 0 on 05b9c1d5 and main); no marker lines at head; all listed files exist at the head (some under tools/pr or tools/audit, ev/missing.txt then resolved by basename). PASS.
RESULT ci: one bulk check-runs read at the head: 42 runs, 33 success, 9 skipped, 0 red/pending (ev/checks.tsv). "entities" is a script inside the scoped gate, not its own check; it could not run locally (no homeassistant), so I cite CI's fast/scope/closures/policy-docs greens. nightly-status is green. PASS.
RESULT carry_audit: "CARRY-AUDIT #2645: 21 finding item(s): 21 routed, 0 unrouted, 0 bad destination(s)". PASS.
RESULT merge-with-main: git merge-tree origin/main head, see ev/mt-main.txt. VERSION/RELEASE_NOTES untouched in range.
Round: delta re-check, not a new fix round.

bus-nonce: 09bb1e7be482a702394c58c21efbf7b5
