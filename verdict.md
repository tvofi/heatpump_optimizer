Fix review: merge d95a2bc761b7ce0fb14f3ff4e239a8d045567557

bus-nonce: 2ebc46f50b345d74c3c225e02dc77f41

## Scope

This round follows the reviewed head 00a470f7b7. The packet's `## Review scope` reads `full`: no verdict on verdict/3551 names 00a470f7b7. So I reviewed the PR's whole three-dot diff against merge base b3831ff64e (8 files: tools/ci/selftest_scope.py, tools/ci/selftest_scope_mutants.sh, tools/ci/selftest_closures.json, the bugclasses/schema/audit-find registration, the RCA doc and the delivery row). The diff has no `custom_components/` delta. The head's tree is byte-identical to the authored head 8ccc59556f (`git diff 8ccc59556f d95a2bc761` is empty). The prior blocking findings M1 and M3 are resolved by deletion: `shrink_gaps`, `shrink_drops` and `table_base` are absent at the head.

## Notes

Note: figure: the body's "Null control" and "Figures" sections both say `--self-test` prints `118 checks, 0 failed`. At this head and at 8ccc59556f it prints `128 checks, 0 failed`, with `GITHUB_BASE_REF` unset and also with it set to main. This is a paperwork figure and blocks nothing.

## Evidence

- RESULT self-test: `python3 -I tools/ci/selftest_scope.py --self-test` at d95a2bc761 prints `selftest_scope self-test: 128 checks, 0 failed`.
- RESULT static: `selftest_scope static: 117 gated step(s), 0 problem(s)`.
- RESULT mutation (step 1): `bash tools/ci/selftest_scope_mutants.sh` runs 27 mutants, each refused, and ends `SELFTEST-SCOPE MUTANTS: every mutant refused`. It prints no NOT REFUSED, NOT APPLIED or BASELINE RED line (ev/mutants.log). The body's count of 27 is confirmed. The failing-test-first mutant "record replaces the committed entry again" is killed.
- RESULT own mutants: I wrote six mutants of my own, outside the driver (ev/own_mutants.txt), and all six are KILLED: record starts from `{}`; `union_entry` lets the new entry override the unioned lists; the flags are dropped from the union; `union_entries` returns the bare measurement; `prune` invents a missing step; record writes only the measured steps (the merge-base semantics).
- RESULT table shrink: I compared the merge-base table with the head table for every step, kind and flag. Result: 117 vs 117 steps, `RESULT table-drops 0` (ev/table_shrink.txt). All 17 `-` lines of the diff are de-duplicated `D/**` items or grown values, which matches the body's account of them.
- RESULT merge: `git merge-tree --write-tree origin/main d95a2bc761` exits 0 against origin/main 646352ff13 (ev/merge_tree.txt).
- RESULT versions: VERSION, manifest.json, RELEASE_NOTES.md and tests/golden are untouched in the three-dot diff (ev/version.txt). No claim file is touched.
- RESULT structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- Not re-derived: the body's drift replay figures (main's table gives `4 refusal(s)`, this head's table gives `0 refusal(s)`, against artifacts from runs 43705258717 and 43716462808). These need the downloaded `selftest-closures` artifacts, which I did not fetch. The zero-drop comparison above is my own re-derivation, by my own per-item definition.
- Finder's harness: none is named. This is a process-defect barrier (R10-RCA-SELFTEST-SCOPE-DRIFT), not an audit finding, and its harness is the in-tree self-test plus mutants, run above.
- Forward-carry (step 10): the body's three `Carry:` items are routed: the packet's carry_audit reads `3 routed, 0 unrouted`. Part A of R11-PRE-SHARED-FILES already states the dependency on this union `record` in its roster brief at origin/handoff/audit-r10-roster 032023814b. The R10-NUDGE-RETIRE brief there already names `prune --step` (ev/carry_check.txt). The compact_probes-duplicate item is not yet in that roster. It is carried by the body's `Carry:`, which lands at merge.
- Red checks: the body answers the ancestry reds. Not one of them is red at this head; CI state is in ev/classify.log.
- RESULT CI: `merge_train.py classify d95a2bc761b7ce0fb14f3ff4e239a8d045567557 --pr 3551` exits 0: `GREEN d95a2bc761b7ce0fb14f3ff4e239a8d045567557 pending: none red: none` (ev/classify.log). No required check is red at this head, so no `## Red checks` answer is owed.
- RESULT head at post: the branch tip is still d95a2bc761 (ev/head_at_post.txt).
