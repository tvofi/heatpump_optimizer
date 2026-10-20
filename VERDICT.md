Fix review: merge d4f8914e6772d5fd3c68eb5a002244f87ff9f8cd

bus-nonce: fa413d44d1549cd673424a53e3dbd58f
RESULT round 2; head d4f8914e unchanged and re-read before posting; origin/main still d1db05dfc
RESULT stage-counts: new body names 7 done, 6 in-progress, 1 not-started, 3 queued = 17; every name matches the roster re-derived in round 1 (done: TICK-SELFTEST-CI, SEAT-SELFTESTS-CI, RECARRY-HEAD, SETPOINT-POWER, PREPR-UNPINNED-RED, CI-RATCHET-RED, POLICY-INSTRUMENTS)
RESULT stage-moves: 8, unchanged and confirmed
RESULT carries: per-group deltas 1+5+7+1+5+1+1+10+7 = 38 match the from/to counts re-derived in round 1 (4>5, 5>10, 11>18, 0>1, 0>5, 0>1, 2>3, 3>13, 2>9); plus 2 on new groups
RESULT data-loss: round-1 field diff stands; the body change is text only and the head is the same
RESULT merge-tree origin/main d4f8914e: exit 0, clean
RESULT ci: 51 check-runs on the head, all completed; 0 failure/cancelled/timed_out; closures, fast (3.14), instrument-self-tests, env-matrix, pr-contract, arch-score, policy-docs, wave-script success; CodeQL neutral. No red, so "## Red checks: none" is correct
RESULT forward-carry: none owed; the PR is the carry landing
