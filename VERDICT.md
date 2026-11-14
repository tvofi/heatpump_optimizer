Fix review: merge c6becb3175c5979f1c117755161b1950aee2d821

bus-nonce: 5c9958bab47ef55c15a04971e28a69bc
pending-ci: gate

## Evidence

- CI: `merge_train.py classify c6becb31 --pr 3425` printed `WAIT c6becb31... pending: gate red: none` on every poll from 03:58Z to 04:29Z (ev/classify.log). Because it still read WAIT after about 30 minutes, this verdict is returned with `pending-ci: gate`. There is no concluded red at this head, so the body's `## Red checks: none` has nothing yet to answer.
- Round 2: a delta re-review of the repair since the blocked head 779c94324f7f15a17938526cc6e2c875170fabc0. `review_carry.py 779c9432 c6becb31` prints FRESH-REVIEW. The delta (ev/delta.diff) is one file: 18 added self-test lines in tools/audit/seat/orchestrator_tick.py, from 0613c67b62 merged as c6becb3175. It changes no production lines.
- Head reviewed: c6becb3175c5979f1c117755161b1950aee2d821 (ev/HEAD.txt). The PR body's `## Head` names it and the authored head 0613c67b62 that it merges.
- Roles: this checkout is origin/main (dbd1ab5b07), so the role pack I followed is main's fix-review.md. Since the branch's merge base, main changed roles/fix-review.md (4 lines) and roles/fixer.md (10 lines).
- Merges with main: `git merge-tree --write-tree origin/main c6becb31` exits 0 with tree 50c8fb41e61329d40b0a287e53094abb8e5b2f8d, and `LEDGER-MERGE: resolved tests/closures.json` (ev/merge-tree.txt).
- Self-test at head: `python3 tools/audit/seat/orchestrator_tick.py --self-test` gives `308 checks, 0 failed`. That matches the body's figure.
- The previous block's survivors are now killed (ev/mutants-head.txt, ev/st-*.log). The figures match the body:
  - M3 (delete the two one_pr lines that clear `_red[n]`): `308 checks, 1 failed`, `FAIL carry 9 one_pr: WAIT clears the red`.
  - M4 (the `_classify_red` except-branch returns False): `308 checks, 1 failed`, `FAIL carry 9 one_pr: an unread classify keeps it`.
- Additional mutants of my own, all killed:
  - M5 (`_classify_red` returns True always): 2 failed.
  - M8 (`not` dropped from the one_pr condition): 3 failed.
  - M9 (the clear made unconditional on classify): 2 failed, `RED keeps it (null control)` and `an unread classify keeps it`.
- The new pin is not vacuous:
  - Its three arms want different `_red[77]` values: [] for WAIT, and ['gate'] for both RED and mt.Stop.
  - The RED null control fails under M8 and M9, so it discriminates.
  - The stub is restored in `finally`.
- The body says "no RED-UNOWNED" for the WAIT arm, but the arm asserts `_red[77] == []`, not the absence of the printed line. This is equivalent: the red-unowned bucket is built from `self._red[n]`, at orchestrator_tick.py `"red {','.join(self._red[n])}, ... red-unowned"`.
- The other three self-tests (beat_jobs, owed_unactioned, remerge_main_selftest) and their carries (13, 10, 15) are outside the delta. They carry from round 1, where they were killed and re-derived at 0 failed.
- VERSION, the manifest and the release-notes heading are untouched; the delta touches one tool file. No golden fixture or claim file moved.
- Finder's harness: none. This is a roster-carry group, and every instrument is the fixer's own self-test (as in round 1).
- review_packet: no refusals; carry_audit: 1 routed, 0 unrouted; figure_lint: 4 resolved, 0 refused.

## Findings

none
