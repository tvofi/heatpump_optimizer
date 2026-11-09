Fix review: merge 81fc66020512dc5bf8bcdea696b44202a45e1e44

bus-nonce: 71f00d40ecbcade3144e3233dee779f5

Round 1. Docs-only PR: two new files (triage note, delivery row); no production, VERSION, notes, budget or claim file touched.

## Evidence
- RESULT merge-tree: `git merge-tree --write-tree origin/main 81fc66020512dc5bf8bcdea696b44202a45e1e44` exit 0, no conflict.
- RESULT diff scope: 2 files added, 508 lines; VERSION and RELEASE_NOTES.md unchanged.
- RESULT checks (GitHub check-runs read through the MCP, head 81fc66020512dc5bf8bcdea696b44202a45e1e44): every run of the latest workflow runs (42643707786, 42646870017) is success or skipped; gate, pr-contract, mutation, coverage, fast, typing, closures, arch-score, budget-raise-gate green. One earlier push-time gate run (42641992250, job 129247021447) failed and was superseded by green gate runs on the same head. owed-reds lists gate-class required contexts only; the head's current runs are all green, so no red check is owed an answer.
- RESULT classify: merge_train.py classify exited 2 (could not read check runs from this cloud seat); judged from the MCP read above instead. Unreadable by the instrument, readable by the API.
- RESULT figures re-derived at roster b1de33a83a: 396 groups, 74 live; stage split 34 carries-open, 19 in-progress, 13 absorbed, 8 not-started, as the note states. At the roster branch's current tip the figures differ (399/72); the note cites its own SHA, so this is a snapshot, not an error.
- RESULT citations: all cited commits (9262e6f43d, 6188936a8b, 82a2c142fa, 72940b7954, 341da07212, fdc8d21ada, 4fe7d5934b, 87c2852ebc, 8aec354354, 0a8033305d) exist; ci_predict.py restoring_jobs is at line 582; handoff_push.sh line 212 holds the mut:push-open pattern.
- Not re-derived: figures from API reads (PR states, nightly run jobs, CI-minute denominators, 55 PRs, 170.42 h); the denominators are batch 136's and the out-of-tree s7/s12/s13 files are not in this tree.
- RESULT carry_audit (packet): 0 finding items, 0 unrouted.
- No harness, mutation, null control or forward-carry applies: the PR changes no code and states no fix.
