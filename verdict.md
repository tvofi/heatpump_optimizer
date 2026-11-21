Fix review: merge 35bb34b2a3790539cd5555606a6c935d9abe4c17

bus-nonce: 53e5d81b105582c3f32e0a41fd58b483
pending-ci: governance / instrument-self-tests

## CI
CI is unreadable at this head: `merge_train.py classify` exited 2. The head's `governance / instrument-self-tests` job 136929429316 was cancelled by its 30-minute pull-request timeout. It was in step 125 of 139 (the ci_predict self-test), and steps 1-124 had passed. The diff changes `tools/ci/selftest_closures.json`, a gate file, so `selftest_scope select` puts the PR in MODE: FULL with all 127 gated steps, which governance.yml's own comment puts at the margin of 30 minutes. The job needs a re-run. This verdict is pending that context going green at this head: the relay must not post it over a red, or while the context stays cancelled. No owed red concluded failure. ev/ci-state.txt.
## Scope
Round 1, full review (first round, no prior reviewed head). Head 35bb34b2a3790539cd5555606a6c935d9abe4c17, merge base a8efe1d1c2a8f1e0b44cdf1046a0ea4ca2155a3b, which is origin/main at review time. Role contract current: base equals origin/main, so the `dev/governance/roles/` three-dot diff is empty. The diff is data only: `tools/ci/selftest_closures.json` (+738/-3) and the delivery row `dev/programme/delivery/3832.md` (+1). No `custom_components/` line changes.

## Evidence
- RESULT byte-identity: the head's `tools/ci/selftest_closures.json` is byte-identical (`cmp`, sha256 0974553324366f6d...) to CI's `selftest-absorbed` artifact 14716467433 of main run 44922703115 at a8efe1d1c2. The zip digest matches the API's recorded digest. ev/merge-and-artifacts.txt.
- RESULT failing and passing test, reviewer's own replay (ev/drift_rev.py, built by this reviewer, not the finder's): it calls `selftest_scope.drift` with the run's `selftest-closures` artifact 14715768946 as the measurement. Main's table gives 7 refusals (rc 1), the seven steps the body names (policy-lint-mutants, dependency-graph-census, prepr, roster-library, regret-oracle, self-tests-outside-seat, temp-or-machine-path). The head's table gives 0 (rc 0). ev/drift-replay.txt.
- RESULT mutation (data-only diff, so mutants are planted on the table): three perturbations differ from the fixer's own and each fails with exactly one refusal. They are regret-oracle without `room_record.py`, prepr without `dev/audit/rounds/round11/D0/s3/race_out`, and temp-or-machine-path without the `killed_by/room_record.py/.gitattributes` probe. No survivor.
- Class: the enumeration is `drift` itself over the whole measured run, across all 127 gated steps. It returns 0 at the head, so no gated step this run measured is left uncovered.
- Figures re-derived at the head (ev/figures.txt):
  - `selftest_scope.py static` prints 127 gated step(s), 0 problem(s).
  - numstat is 738/3 on the table. The 3 deleted lines are roster-library probes `dev/governance/dimensions/{D12,D3,D99}.md`, now covered by its new dirs entry; the replay confirms no refusal.
  - Duplicate list items: 0. run_sha changed: none. No step added or removed. No other top-level key changed.
  - "738 reads" equals the CI log's own `selftest_scope absorb: 738 read(s) added to 7 step(s)` for job 136902224642.
  - Not re-run: the body's local absorb on python 3.14.7. Byte identity with CI's artifact makes it moot.
- VERSION, manifest version, RELEASE_NOTES heading and both claim files are untouched by the three-dot diff.
- Merge: `git merge-tree --write-tree origin/main <head>` exits 0 (tree 8f503338f9).
- Head SHA in the body matches the reviewed head. Forward-carry: none named. The drift step is a committed CI check (`tools/ci/selftest_scope.py drift`). The fixer's `drift_harness.py` is seat scratch, disclosed as the builder's, and so is this reviewer's ev/drift_rev.py.
- Not provable on the PR: the drift step is push-only, so this PR's own CI cannot show it green. The replay above is the evidence that the first main push after merge clears all 7 refusals.

## Findings
- Follow-up: a pull request that changes only `tools/ci/selftest_closures.json` forces MODE: FULL, all 127 self-test steps, under `instrument-self-tests`' 30-minute pull-request timeout (governance.yml:310). This head's run was cancelled at 30m16s in step 125. Every absorb hotfix, and the automatic absorb job still to be built, lands on the same margin, so a timeout cancellation can hold a main-red repair indefinitely. Possible remedies: a longer pull-request timeout for a table-only diff, or a narrower selection for that diff. Carry: R11-PRE-SHARED-FILES
- Follow-up: the root cause of this hotfix family is not settled here. The body counts this as at least the fourth instance (#3487, #3718, 912b87c035, this PR). The job that runs `absorb` on a red drift step and opens the PR is unbuilt, pending the owner's ruling on design decisions D1/D2, as bugclasses.json's countermeasure text records. Main reddens again on the next merge that adds a read. Carry: R11-PRE-SHARED-FILES

## Notes
- Note: harness: the finder's harness is the committed CI drift step (`selftest_scope.drift`). The fixer's `drift_harness.py` and this reviewer's `ev/drift_rev.py` are each disclosed as their builder's. The reviewer's replay reproduces main's 7 refusals and the head's 0.
