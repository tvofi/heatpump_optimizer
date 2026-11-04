Fix review: merge da3c0168b640ab54b8039d478dd6898d010c55eb

bus-nonce: 0829d4b20e14c3ebe9deff96848a7e4a

## Summary

First-round review of #3194 (R10-HOTFIX-RECORD-ATTRIB) at head da3c0168b640ab54b8039d478dd6898d010c55eb, merge base 8e90d81443317f76f22602a89651f7ca17c633f9. The fix is correct. Replaying #3179's empty-map merge, the merge base refuses it and the head attributes it to #3179. The body's named mutant is killed. CI is GREEN. One test gap is carried below: the `enumerate_merges` wiring is unpinned.

## Findings

- Follow-up: two mutants of this PR's own lines survive `record_row.py --self-test`. One passes `""` as the subject in `enumerate_merges`. The other reverts the `git log` format to `%H%x1f%P`. Either one disconnects the fallback on the production path that went red (#3179) while the self-test stays green. Cause: the enumerate self-test's fake log still uses the old two-field format and never feeds an empty map. Fix: add a fake-log line that has a subject and an empty `/commits/<sha>/pulls` answer, and assert that its row is recovered. Carry: R10-HOTFIX-RECORD-ATTRIB
- Follow-up: the finding has no committed harness ("Finder's harness: none named" in the packet). The replay I used is my own instrument, not the finder's (ev/e2e.py). It runs the real first-parent log from fad43b04 and stubs the API with `[]` for 616868bd. Carry: R10-HOTFIX-RECORD-ATTRIB

## Evidence

- Head: da3c0168b640ab54b8039d478dd6898d010c55eb, re-read from the PR's commits before return. That head adds only `dev/programme/delivery/3194.md` on top of the authored head 1063cb1a, as the body states.
- Role contract: `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Mutation (ev/mutants-key.txt, ev/mutants.txt): M1 (subject number nulled) KILLED. M2 (confirmation dropped, the body's named mutant) KILLED. M5 (map match removed) KILLED. M3 and M4 SURVIVED (see Findings). The tree was clean after each restore.
- Self-test at head: rc=0, `record_row self-test: all checks passed` (ev/selftest-head.txt).
- RESULT e2e base: REFUSE merge commit 616868b attributes to no pull request. RESULT e2e head: [3179] (ev/e2e.txt). Harness: ev/e2e.py, my own.
- Class: `subject_number` resolves the subject of all 400 of the latest first-parent merges on origin/main (0 name no PR). The body-only deploy-key shape that `subject_number(subject, body)` accepts does not occur in that window, so passing the subject alone covers the population.
- Readers of `/commits/<sha>/pulls` re-enumerated with the body's own grep (ev/readers.txt). The result matches the body: record_row (one reader, `attribute_merge`), policy_lint.mjs (already has a subject fallback), sweep.mjs (diagnostic), and comment hits in governance.yml and entities.py.
- Merge: `git merge-tree --write-tree origin/main da3c0168` rc=0, no conflict (ev/merge-tree.txt).
- Untouched: the diff does not touch VERSION, the manifest or RELEASE_NOTES.md. No claim files or budgets are touched (diff stat: 2 files), so steps 4 and 14 have nothing to measure.
- CI: `merge_train.py classify` printed `GREEN da3c0168b640ab54b8039d478dd6898d010c55eb pending: none red: none`, rc=0 (ev/ci-classify.txt). The packet's red `tests / nightly-status` is not required and reads main's nightly state. This PR's diff does not reach it, so it is not this PR's red. The body's "Red checks: none" stands.
- Figures: the body quotes none. figure_lint resolved 7, refused 0.
- Forward-carry: none named, and none is owed beyond the follow-ups above.
- Round: first.
