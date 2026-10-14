Fix review: blocked 990743c078a3c85b87dfaf09ab3a25fb679c8dcd figure-unverified: R10-RCA-2205.md section 4 runner-class split (19 slow at 0.2441-0.2742, 11 fast) re-derives as 17 slow at 0.2441-0.2783 (1.14x), 13 fast
bus-nonce: b95a6835d0b61f48d1eb17e1f05f52ca
reviewer: r10-rca-reviewer
evidence: /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/r2215/evidence

Round 1. Detached worktree at 990743c07; roles/ current against origin/main.

RESULT runs-enumerated 125 tests.yml runs (schedule+workflow_dispatch, 2026-09-25..10-14), 0 API failures; slow job completed in 37 (20 schedule, 17 dispatch), skipped 86, cancelled 2
RESULT 37-run figure REPRODUCED from the 37 slow-job logs, 0 log-fetch failures: hot/clean 1.8947-2.0874; lowest pre-window clean 1.9147 (2026-09-27); memory arm 1.9945-2.0061; exactly 1 arm under 3.576 (38530020347, 3.5628/1.8804)
RESULT arithmetic REPRODUCED: 1.9147x1.895=3.628; 1.8804x[1.87,1.97]=3.52-3.70; 2x1.8804=3.761; 4.550/(3.576/sqrt2)=1.80; 0.763 and 0.656 from the quoted medians; 2.173 centring; 7.7%/24% and 15.6% headroom; loop centre 0.445, 5.2%/14.6%
RESULT replay step 38-128 s over the 20 nightlies REPRODUCED (jobs API, 0 errors); 20 stamps in window REPRODUCED; 64 merges touching COST_FILES/optimizer.py/tests/replay.py REPRODUCED (first-parent merges, calendar window)
RESULT denominator 335 merged PRs NOT reproduced: 338 (nightly-to-nightly window), 367 (calendar first-parent), 387 (search merged:) -- not load-bearing, 3.2/cycle uses only 64/20
RESULT loop runner-class split NOT reproduced: 30 runs, corr(loop_cpu_ratio, ref_ms) -0.939 (claim -0.94, OK); ref_ms 52-54 holds 17 runs at 0.2441-0.2783 (1.14x), not 19 at 0.2441-0.2742 (1.12x); ref_ms 22-43 holds 13, not 11. The conclusion (spread is runner class) survives; the figures do not
RESULT local seat-box medians (2.983/2.931/2.237/1.958) not re-run -- arithmetic only; agrees with the fixer's independent 0.671x
RESULT fold_ledger.py check: 0 violations, 106 rca entries; control: in_tree_home pointed at a missing file -> DANGLING _rca[R10-RCA-2205], 1 violation; entry key set equals the 105-entry majority shape
RESULT process state (c) and refusal: legitimate. Class null, no audit-class barrier owed; cost test stated with numbers; refusal rests on #2212's exact arm + short_doubling (present at handoff/r10-2205 d7bfeb0dd tests/replay.py:389, controls pair at :469-470, run per PR via tests/entities.py:34236-34239). Note for the record, not blocking: before the fix the same numbers favour the lane (0.05 x >=19.9 h ~ 60 min/cycle vs ~10 runner-min), so the refusal is valid only once #2212 lands; entry status "done" with landed null presumes it
RESULT delivery row 2215.md: CORRECT as written. OPEN_ROW_TITLE is record_row.py's self_row for a record pull request's own row; handoff_push.sh:109 and open_pr.sh:47 write a non-record PR's row with its real $TITLE. The #2214 row (a fix PR carrying OPEN_ROW_TITLE) is the deviation, not this one
RESULT check-runs at head: all concluded success/skipped/neutral except nightly-status failure (main's; diff touches nothing it reads; body answers it) and Analyze (python) still in_progress at review time; closures success; merge-tree vs origin/main clean (rc 0); body non-empty (1973 chars), ## Head names 990743c07
RESULT forward-carry: body routes the two budget findings to the live fixer via the orchestrator; finding-propagation.md binds stages not yet started, and #2212 has started -- not blocking, but #2212's body still carries 2.332 with no reply to the off-centre finding

To clear: correct section 4's slow/fast split to the measured 17/13, 0.2441-0.2783, 1.14x (or name the ref_ms boundary that yields 19/11 and its source), and the same figures nowhere else; nothing else is owed.
