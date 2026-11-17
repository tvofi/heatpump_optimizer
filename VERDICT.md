Fix review: merge 49e0e0c270a9ae4d8e734df3bb338faf1e9593cf

bus-nonce: c06247e2c3e4ed48b5fe0198e1258892
pending-ci: gate

## Evidence

- Round 1, full scope (no prior reviewed head). The PR head was re-read just before this verdict: refs/pull/3707/head = 49e0e0c270a9ae4d8e734df3bb338faf1e9593cf, the head I measured. Role contracts are current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Merge: `git merge-tree --write-tree origin/main 49e0e0c2` exits 0 with no conflict (tree d6f2eca19f). The head is 0 commits behind origin/main.
- Diff (three-dot from 8f39313a44): only `tools/ci/selftest_closures.json` (+206/-15) and `dev/programme/delivery/3707.md` (+1). This matches the body's "206 lines added, 15 removed". VERSION, the manifest, RELEASE_NOTES.md and the golden claim files are untouched.
- No read dropped: every list entry of all 122 base-table steps is still present or still covered (`selftest_scope.covers`) in the head table. Scalar fields are unchanged and the step set is unchanged (122 = 122). The 15 removed lines are duplicate glob entries. 204 unique entries were added. `selftest_scope.py static`: 122 gated steps, 0 problems (ev/checks.txt).
- Independent measurement (my own, using the instrument's own recorder, not the CI artifact): `selftest_scope.py record --step field-coverage --step pr-args` under strace in a detached worktree at the head. Result: rc=0, 0 failed, 0 broken traces (ev/strace_record.txt). The traces show field-coverage reading tools/audit/seat/shell_hazard.py, and pr-args reading both shell_hazard.py and ancestry_calls.sh.
- Null control / mutation on the instrument (`selftest_scope.drift`, ev/drift_mutation.txt), counting only UNDER-SCOPED lines. The other lines are UNMEASURED for steps I did not trace.
  - Head table: 0 UNDER-SCOPED.
  - Base table: 2 UNDER-SCOPED: field-coverage misses shell_hazard.py; pr-args misses ancestry_calls.sh and shell_hazard.py.
  - Mutant head table, with shell_hazard.py removed from field-coverage and ancestry_calls.sh from pr-args: both refusals come back.
  - The table entries are therefore load-bearing and match a real measurement.
- The body's figure "20 UNDER-SCOPED refusals" was re-derived under drift's one-refusal-per-(step, kind) rule: the head adds entries to exactly 20 (step, list-kind) pairs across 15 steps. I did not fetch run 44048908427's artifact, so the 20 is not re-derived from that run's own drift output.
- Mutation proof: n/a. This is a data-only diff, so it writes no production line. The mutation lane is green.
- CI: `merge_train.py classify 49e0e0c2 --pr 3707` polled from 12:05 to about 12:37 UTC, last `WAIT 49e0e0c270a9ae4d8e734df3bb338faf1e9593cf pending: gate red: none` (rc=3). The review_packet's introduced-red refusal was an in-progress instrument-self-tests job; classify decides, and it shows no red.
- Red checks: `tests / nightly-status` read failure in the packet digest. It is not in the `owed-reds` set, so it is neither answered nor a block.
- Carry: the body routes its red-check cause to R11-RCA-SELFTEST-TABLE-DRIFT (#3684). carry_audit at the head: 0 items.
