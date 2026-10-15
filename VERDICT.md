Fix review: merge 84c24884c64af7c427164721bfb9aadc4f1c1f8c
bus-nonce: a8a980316cd8d5984bc1d7b45c249fbe
reviewer: r10-rca-reviewer
evidence: /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/r2215-r2/evidence

Round 2. Delta review of 84c24884c against round 1's 990743c07 (blocked figure-unverified).

RESULT delta: one commit, direct child of 990743c07; only dev/audit/rca/R10-RCA-2205.md moved (+8/-8, section 3 and section 4); bugclasses.json and 2215.md byte-identical to round 1
RESULT runner-class split REPRODUCED from round-1 logs: 17 slow (ref_ms 52.3-53.9, loop 0.2441-0.2783, 1.14x), 13 fast (ref_ms 22.2-43.1, loop 0.2957-0.405); block cleared
RESULT "the channel dates from 2026-10-01" REPRODUCED: first slow-job log printing loop_cpu_ratio is the 2026-10-01T09:00:52Z nightly
RESULT window 2026-09-25T07:00Z..2026-10-14T07:41:52Z by committer date on main: 19 stamps, 335 first-parent PR merges, 60 touching the five COST_FILES, optimizer.py or tests/replay.py -- all three REPRODUCED; 60/19=3.16 -> 3.2/cycle and 1/19=0.053 -> 0.05 hold
RESULT round 1's 64 was my wider calendar window (first-parent merges 09-25T00:00..10-15T00:00); under the stated window it is 60, so the seat's correction is right and round 1's "64 REPRODUCED" was a window coincidence
RESULT everything else carried from round 1 unchanged: 37-run figures, arithmetic, fold_ledger 0 violations with DANGLING control, state (c) and recorded refusal, delivery row correct
RESULT check-runs at 84c24884c: every gate check concluded success/skipped/neutral, closures and coverage included; nightly-status failure is main's, the diff touches nothing it reads, and the body answers it; CodeQL Analyze (python) still in_progress, not a gate; merge-tree vs origin/main clean; body ## Head names 84c24884c
RESULT residual, not blocking: #2205's Root cause comment 6180550675 still says "1 triggering speed-up in 20 release cycles"; the in-tree record is now the authority
