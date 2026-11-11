Fix review: merge 991ff6e21ab2b68fd71f5143e99319f937751ba2

bus-nonce: 27734ffb832b4478faa6beb72bec3a7f
pending-ci: gate

## Evidence

- RESULT delta c562b079..991ff6e21ab2b68fd71f5143e99319f937751ba2: of the PR's own files only tools/audit/seat/cloud_relay.sh changed (11 insertions, 8 deletions), in the arm and its self-test; the rest is a merge of the fix commits. No custom_components/ code is touched, so the review is not widened.
- RESULT mutants re-run with mutant_run.py (copy-tree, cmd `bash tools/audit/seat/cloud_relay.sh --self-test`) at the head (ev/mutants.txt, rc=0): NULL SURVIVED; 14 KILLED, 0 SURVIVED. The previous verdict's rv-privref-not-deleted is now KILLED: the new null-control check sees refs/hpo-relay/fold/cf-a standing during the push and a check that for-each-ref is empty afterwards. The other, rv-folded-memo-no-entry, has no site at this head: the redundant fold_judge memo write was deleted (cloud_relay.sh:834 is now a bare skip), so nothing remains unpinned. In its place I added rv-cloudfolded-skip-off, which replaces that skip with `:`; it is KILLED by the new check that a folded (topic, body) whose wip ref moved is not folded again.
- RESULT self-test at head: `cloud_relay self-test: 444 checks, 0 failed`, rc=0 (ev/selftest-head.txt); 441 at the previous head plus 3 new checks.
- Structure: STRUCTURE RATCHET PASSED (ev/structure.txt). git merge-tree --write-tree origin/main at the head: rc=0, clean (ev/merge-tree.txt).
- CI: classify at the head prints `WAIT 991ff6e21ab2b68fd71f5143e99319f937751ba2 pending: gate red: none` (ev/classify.txt), after about 30 minutes of polling; no red. pending-ci: gate. owed-reds listed in ev/owed-reds.txt; none is red.
- The previous verdict's stale-figure note (failing-first count) is a body figure for the re-cut; the body is not part of this delta.

## Findings

none
