Fix review: merge 82f2641aa964dfcc4f9a16ac4c242a70ec6d7577

bus-nonce: 5fd2146a5987aa3f5fe4163bf5f47386

Round 5. This round changes the body only. The head is unchanged at 82f2641aa964dfcc4f9a16ac4c242a70ec6d7577, and when I re-read it just before posting it was still that commit and MERGEABLE. Round 4 found the code delta (baadb840..82f2641a) correct and blocked only on body line 37. This round judges only the body change and the CI runs that have finished since.

## The round-4 finding is cleared

- Body line 39, previously line 37, now says: "One `tests/closures.json` entry names it: `inert_reads["tests/harness_headers.py"]`, re-pointed to the new path ... No harness README row names it." (`body_r4_r5.diff`)
- RESULT `git grep -n eg_b7_seam_hubs 82f2641a` returns exactly 2 hits: the file's own usage line and `tests/closures.json:3578`. The line-3578 entry sits in `inert_reads["tests/harness_headers.py"]`, as round 4 found. RESULT README hits: 0. The body matches the tree (`grep_eg_b7_at_head.txt`).
- The round-4 code evidence carries forward, since the head did not move. Stand-in arms at the head: rc=0. The perturbed old-path arm: rc=1. The control arm: rc=0. Missing-path entries: 0 in `closures` and 0 in `inert_reads`; the planted control counts 1.

## CI at 82f2641a (check-runs API)

- RESULT `closures` success (job 112885974811): it re-recorded `tests/harness_headers.py` on Linux with strace and printed "committed closures cover every file this run touched".
- RESULT these finished since round 4, all success: `fast (3.14)` (112885821688), `coverage` (112885821881), `coverage-ratchet`, `browser` (112885821732), CodeQL `Analyze (python)`. `pr-contract` also succeeded on the body edit (112910302796, 17:02:55Z).
- Totals: 24 success, 12 skipped, 2 failure, 1 cancelled, 0 in progress. The two failures are `delivery-status` and `nightly-status`, which are main's per the dispatch. The cancelled run is the `budget-raise-gate` twin, check-run 112885821312 in run 37648625290; its sibling run 37648625777 succeeded. The orchestrator reruns the cancelled one. No new reds.

## Non-blocking body notes (not this round's finding)

- The `## Head` section now opens with two sentences about 82f2641a, lines 30 and 32. The first, which the script prepended, says it "merges origin/main `e0f0b6fb` ... into this PR's previous head". The actual parents are baadb840 and 60c00052, and 60c00052 contains e0f0b6fb. That is accurate as to content but redundant with line 32.
- Line 39's "as the next bullet records" points one bullet too early: the closures bullet is the second bullet after it, at line 41.
- Line 71 still quotes `ALL 2191 ENTITY CHECKS PASSED` "at the head above". At this head the count is 2198 (round 4's run, and body line 38).
