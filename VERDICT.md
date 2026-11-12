Fix review: merge 04129e8498f2fb40adfb781ca11f877541823af8

bus-nonce: 37ea4e0f5147fe765ce38c5a1b5f91d7

## Evidence

- Round: first review, at the handoff, before a pull request exists. No review packet and no CI run exists to read; the red-check answer ("none") cannot be checked against live check runs until the PR opens, and the train re-proves on the current main.
- Head measured: 04129e8498f2fb40adfb781ca11f877541823af8 (ev/HEAD.txt); BODY.md on handoff-body/r10-hotfix-carry-audit-own-group (09209cb916) names the same head under its Head heading and its Code: trailer.
- Merge base 4145f2852642fd0b5ccb8b7af60d41e896a5eea3; origin/main a18e2e9d00b17a0349f29938a469d1bc3edd1ae3. git merge-tree --write-tree origin/main <head>: rc=0, no conflict (ev/merge-tree.txt).
- Scope: the diff touches exactly tools/audit/carry_audit.py (the one-line pr_group_of change plus two self-test rows) and dev/audit/harnesses/r10_carry_parser_mutants.py (the R-roundgroup mutant). tools/audit/seat/body_push.sh, VERSION, the manifest and RELEASE_NOTES.md: zero diff lines (ev/untouched.txt), so body_push.sh's default roster ref is untouched.
- RESULT carry_audit --self-test at head: 417 checks, 0 failed (ev/selftest-head.txt). On the tree merging head into origin/main: 449 checks, 0 failed (ev/selftest-merged.txt).
- RESULT the new row fails on origin/main's code: the two self-test rows grafted alone onto origin/main's carry_audit.py: 449 checks, 1 failed, "landed: an own-group status line whose group is on the round's roster branch only lands nothing"; the null-control row passes there (ev/selftest-origin-main-with-new-rows.txt).
- RESULT the mutation proof re-run two ways: the fixer's driver at the head, R-roundgroup: failed=1, verdict=killed (ev/mutant-R-roundgroup.txt); my own sed mutant restoring dests.groups.values() at the head: 417 checks, 1 failed, the same row (ev/manual-mutant-main-only.txt).
- RESULT null control: at the head, the row "a status line whose own group is on neither roster still refuses" passes. It is not vacuous: an over-permissive perturbation (pr_group_of always returns R10-NEWGRP) fails it, along with 5 other rows (ev/perturb-null-control.txt). landed() (carry_audit.py:634-651) appends an item whose own group is unresolved to the returned carries, not to the status lines. The row asserts sts == [] rather than a non-empty refusal list, and that matches the body's meaning of "refuses": the item is not treated as a status line.
- RESULT the full mutant driver: base sites=200 mutants=270 survived=8; head sites=200 mutants=271 survived=8; unmapped=6 at both ends; driver rc=1 at both ends (ev/harness-base-all.txt, ev/harness-head-all.txt). The one added mutant is killed and the surviving count is flat, so the eight survivors predate this diff. I compared counts only, not survivor names.
- Body figures re-derived: self-test 0 failed (yes); R-roundgroup survived=0 on a single-mutant run (the driver prints sites=200 unmapped=6 mutants=271 survived=0 when filtered to that mutant; yes).
- tests/entities.py with env -u BASH_ENV could not be run in this seat: venv-ci lacks homeassistant, and venv-ha (tried) lacks paho, so the import fails before any check runs (ev/entities-head.log, ev/entities-head-venvha.log). Not re-derived here; CI's run is the evidence once the PR opens. The diff adds no tracked file, so no INERT or closure classification is owed.
- merge_train.py owed-reds prints its set (ev/owed-reds.txt); no CI exists, so no red is owed an answer at this point.
- Forward-carry "none" and Friction line (dismissed): consistent with a one-seam instrument hotfix; the class is the single pr_group_of read, and the destination check already reads both sources, as the body states.
