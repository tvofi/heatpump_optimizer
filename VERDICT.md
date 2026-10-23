Fix review: merge ea1cde9fd3f95ab13d6d2c2e834a672af44850b5

bus-nonce: 487840aa9516e44bda1807e7548b2d63

Round 1. Head measured and still current: ea1cde9fd3f95ab13d6d2c2e834a672af44850b5 (PR read at review time).

RESULT roster groups=167/167 new=0 removed=0 changed=2 (R10-CI-LAYOUT-P2, R10-FLY-GH-READ-RETRY)
RESULT stages main==head done=88 in-progress=12 not-started=60 queued=6 absorbed=1
RESULT diff three-dot vs base: only resume.pr 2638 and 2639 added; no other field or group moves
RESULT null-control main roster == 3e7aaed31 (empty diff): nothing main wrote is overwritten
RESULT brief_lint 0 errors; ref_privacy --check 0 refused
RESULT merge-tree origin/main(5056615) vs head: exit 0, no conflict
RESULT versions VERSION/manifest/RELEASE_NOTES untouched (diff is the roster and delivery/2641.md only)
RESULT ci no failed check at head; closures, fast, instrument-self-tests, env-matrix, Analyze(js-ts) were still in progress at the last read, so this verdict rests on no red so far

Notes:
- Mutation proof: n/a, roster-only diff, no production code (step 1). Steps 4, 6, 14, 15 have nothing to measure: no fixture, claim, budget or code moved.
- Brief item 1 is stale on one point: #2638 was open when the sync ran but merged at 02:26:44Z, after the PR was created. #2639 is open, draft. Head branches fix/r10-ci-layout-p2-policylint and fix/r10-fly-gh-read-retry-2 match topics r10-ci-layout-p2 and r10-fly-gh-read-retry under roster_sync's B13 rule. The stage stays in-progress for R10-CI-LAYOUT-P2 (P2b owed); the next roster_sync pass will read #2638 as merged and may derive done for that group. #2638's own body carries the forward-carry to R10-CI-LAYOUT-P2. For the orchestrator.
- ref_privacy count differs from the body (4 lines since 4e38e7d vs 3 since 3e7aaed31); only the reference commit differs, 0 refused either way.
- Forward-carry none; no red check owed an answer.
