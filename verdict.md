Fix review: merge 97ecbaea1db8614d224feae9e79611b504d5e2b5

bus-nonce: dedf1f21e8bd8466dab626db1eafe2fd
pending-ci: gate, governance / instrument-self-tests, tests / fast (3.14), tests / typing, tests / coverage, tests / closures, tests / arch-instrument, tests / browser

Scoped resume from refs/heads/verdict/3465 (blocked 332f882cf carry-missing). Reviewed the delta 332f882cf..97ecbaea1db8614d224feae9e79611b504d5e2b5: the code delta is cloud_relay.sh (+13, self-test arms), the rest is main merges and the delivery row.

## Evidence
- RESULT carry-missing block closed: the roster (origin/handoff/audit-r10-roster e7f6a56c1) now holds P603 OPENER-LIVE-TIP in R10-SEAT-IDENTITY-P5 (not-started; files list tools/audit/seat/open_driver.py), moved by the orchestrator's ruling on verdict/3465 at d1ce0cc571, with the card verbatim: self-test (board line A, live clean tip B opens at B), mutation proof (restoring the skip fails), null control (handoff ref gone still prints SKIP moved) and the 18 SKIP moved figure marked to be re-measured. The old R10-REVIEW-DISPATCH-RESIDUE carry 27 is marked [moved: R10-SEAT-IDENTITY-P5]. The PR body's Forward-carry names the same destination and control; carry_audit: 2 routed, 0 unrouted, 0 bad.
- RESULT surviving mutants m2/m3 from the last round: killed by the new lister-count arms (one lister call per pass under --confirm; lone handoff_arm lists once). Arm order is now pinned itself.
- RESULT head self-test: cloud_relay.sh --self-test rc 0, 424 checks, 0 failed, matching the body (ev/selftest-head.log).
- RESULT mutants of the pass() order line, re-run here: m7 (carry_fold before probe): 2 failed; m8 (confirm after handoff): 1 failed. Both match the body (ev/m7.diff, m8.diff, mut7.log, mut8.log). Both were survivors last round.
- PR body no longer stale: head line names 97ecbaea1db8614d224feae9e79611b504d5e2b5 merging code head 9647bc111; figures (424 checks) re-derived.
- Merge with main: git merge-tree --write-tree origin/main 97ecbaea1db8614d224feae9e79611b504d5e2b5 rc 0.
- CI: merge_train classify prints WAIT (pending: gate red: none) after about 7 min of polling; tests jobs still queued, instrument-self-tests in_progress. The combi census and instrument-self-tests reds are main's, cured by the remerge of main 6cc15e9b. owed-reds set in ev/owed-reds.txt.
- VERSION, manifest, RELEASE_NOTES and claim files untouched.

## Findings
- Follow-up: P603 OPENER-LIVE-TIP is built by R10-SEAT-IDENTITY-P5, not here. Carry: R10-SEAT-IDENTITY-P5
