Fix review: merge dd2f26e749d54d7295dc2873a601487ce59367a4

bus-nonce: 28b90c3e2bc79cb0cee4538a26406e87
pending-ci: governance / instrument-self-tests

## Scope
Round 2 at this head, the delta 35bb34b2a3..dd2f26e749. The earlier verdict at 35bb34b2a3 does not carry: `review_carry.py` prints FRESH-REVIEW because the new commit is a `ci:` commit outside the merge-driver files. The delta changes `tools/ci/selftest_closures.json` only (+64/-0). The whole three-dot diff is data only: the table (+802/-3) and the delivery row (+1). No `custom_components/` line changes. The `dev/governance/roles/` three-dot diff against origin/main is empty, so the role contract is current.

## Evidence
- RESULT byte-identity: the head's `tools/ci/selftest_closures.json` is byte-identical (`cmp`, sha256 8db94f8a3843...) to CI's `selftest-absorbed` artifact 14730141227 of main run 44957362163 at 4ebd430fbf. Both zip digests match the API digests. ev/merge-and-artifacts.txt.
- RESULT failing and passing test, from this reviewer's own replay (ev/drift_rev.py, built by this reviewer, not the finder's). It calls `selftest_scope.drift` with that run's `selftest-closures` artifact 14729559307 as the measurement. Main's table gives 11 refusals (rc 1): the 7 the reviewed head covered, plus verdict-bus, review-packet, roster-sync-reconciler and ci-predictor, each missing `dev/programme/rosters/wave-r11-groups.json`, as the body says. The head's table gives 0 refusals (rc 0). ev/drift-replay.txt.
- RESULT mutation (data-only diff, so the mutants are table perturbations): verdict-bus without wave-r11-groups.json, ci-predictor without wave-r11-groups.json, and regret-oracle without room_record.py. Each one fails with exactly that one refusal. No survivor.
- Class: the enumeration is `drift` itself, run over all 127 gated steps of the measured run. It returns 0 at the head.
- Figures re-derived at this head (ev/figures.txt):
  - `selftest_scope.py static` prints 127 gated step(s), 0 problem(s).
  - numstat is 802/3 on the table and 64/0 on the delta.
  - Items of the 35bb34b2 table missing at the head: 0. The head table is a superset, as claimed.
  - Duplicate items: 0. No step was added or removed. run_sha changes: none.
  - The +64 falls in 7 steps: the 4 new ones (1 read each) and 60 more reads in prepr, dependency-graph-census and policy-lint-mutants. The body names only the 4 new steps; the artifact identity covers the rest.
- VERSION, manifest version, the RELEASE_NOTES heading and both claim files are untouched.
- Merge: `git merge-tree --write-tree origin/main(e4c929bd1c) <head>` exits 0 (tree 6051a60381). The main table, `selftest_scope.py` and governance.yml are unchanged between the base and origin/main.
- Head SHA in the body matches the reviewed head.
- Owed-reds and CI: ev/classify.log, with the result in the CI section below.

## CI
CI cannot be read at this head. `merge_train.py classify` exited 2 after 22 WAITs, 60 s apart: `REFUSE selftests: the head's governance / instrument-self-tests job 137029108564 concluded cancelled, which reads no step: re-run it`.
- The job ran from 23:56:57Z to 00:27:12Z and hit its 30-minute pull-request cap in step 125, the ci_predict self-test. No step before it was red. This is the same step and cap as the reviewed head's job 136929429316 (second Finding).
- The verdict is pending that context going green at this head after a re-run. The relay must not post it over a red, or while the context stays cancelled.
- At the last read, `tests / fast (3.14)` and `tests / arch-instrument` were in progress, and `tests / coverage-ratchet` and `tests / graders-head-copy` were queued. The one `gate` failure (job 137029528697, 23:57Z) is the early gate that classify reads as `gate red: none`.
- No owed red concluded failure. Evidence: ev/ci-state.txt and ev/classify.log.

## Findings
- Follow-up: the table is already stale against current main. #3814 (e4c929bd1c, merged after run 44957362163) adds 4 directories that no step's `dirs` covers: `dev/audit/rounds/round11/D3/s1/state/results/{c3c6-redrive,posctl-D3-top6,posctl-D3-top6-local}` and `.../state/superseded/gates-aborted`. The dirs-walking steps (prepr, dependency-graph-census and the policy-lint-mutants probes) will most likely refuse again on main's first push after this merge. The body's "It goes green on the first main push after merge" is therefore not expected to hold. The steps named are inferred from the 11-refusal replay, not measured: that main run (CI 44964363447) was still queued at review. This is the hotfix family's open root cause: absorb is committed by hand and lags every merge that adds a read. Carry: dismissed: the automatic absorb job that settles it is unbuilt pending the owner's D1/D2 ruling (bugclasses.json countermeasure text, body item 132fe653), so no group can take it now
- Follow-up: a pull request that changes only `tools/ci/selftest_closures.json` still forces MODE: FULL, all 127 self-test steps, under the 30-minute pull-request cap. This is the timeout margin the reviewed head hit. Carry: dismissed: already recorded in the instrument round-end triage (body item d45f668f), with no roster group to take it

## Notes
- Note: stale-body: the Red checks section says the drift step "goes green on the first main push after merge". It is expected to stay red because of #3814's 4 new directories (first Finding). The "7 steps, 738 reads" title is disclosed in the body as describing the reviewed head.
- Note: harness: the finder's harness is the committed CI drift step (`selftest_scope.drift`). The fixer's `drift_harness.py` and this reviewer's `ev/drift_rev.py` are each disclosed as their builder's.
