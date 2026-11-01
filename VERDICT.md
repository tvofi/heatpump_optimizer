Fix review: merge 9ef51b8215dd7216950f177386fb2f5a8f010a47

bus-nonce: de774e283b26fc790fb40c74a9cd6ac6

## Scope

Round 4 of PR #3045 (R10-HOTFIX-CI-CRITPATH-2). The head is unmoved, and only the rewritten body changed. The brief limited this review to the rewritten `## Raise justification`, held to fix-review.md step 14 and CLAUDE.md rule 2. I judged it from a detached worktree at 9ef51b8215dd7216950f177386fb2f5a8f010a47. `git diff a7dd7f50d...origin/main -- dev/governance/roles/` is empty, so the contract is current.

## Findings

- The live-window cut "33.867 + 0.951 - 34.267 = 0.551 min" applies the window's largest downward 8-run deviation (center 33.867 minus the low median 32.916 = 0.951). GREW reads only the upper side. The cut the live window actually needed at zero band is 34.575 - 34.267 = 0.308 min. That is why the body's own simulation can say that a 0.45 to 0.53 min cut "would have kept the live window green", which is less than the 0.551 it states as needed. The decisive figure, 0.800, is right on the upper side: the recording window's 1.300 is 33.850 - 32.55, its upward deviation. So the conclusion that no payment clears the recording window's spread at zero band stands. Carry: dismissed: the overstatement is internal to the body's arithmetic, does not change which payment clears and which does not, and moves no number in the tree

## Evidence

- RESULT archscore: `python3 tools/audit/archscore/score.py --diff a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0 9ef51b8215dd7216950f177386fb2f5a8f010a47` at this head printed `Architecture score: dS +0.0000 NULL`. It matches the body's `Architecture score: dS +0.0000 NULL` line. a7dd7f50d is `git merge-base origin/main 9ef51b82`, so this is the three-dot diff (ev/archscore.txt).
- RESULT merge: `git merge-tree --write-tree origin/main 9ef51b82` exits 0, a clean merge (ev/merge_tree.txt; origin/main in ev/main.txt).
- RESULT CI: `merge_train.py classify` printed `RED 9ef51b82... pending: none red: gate` (ev/classify1.txt). From the commit's check-runs, every completed check is success or skipped except `budget-raise-gate / budget-raise-gate` and `gate`. That red is the expected state the brief names, held until the owner's approving review at this head. `pr-contract` is green on its latest run (2026-11-01T06:58:17Z).
- RESULT window: I re-gathered with `GITHUB_REPOSITORY=tvofi/heatpump_optimizer python3 tests/ci_ratchet.py --gather-runs runs60.json --window 60`, which printed `push runs: 60 (60 CI)`. I analysed the runs with my own script, ev/win.py, which calls the production `ci_ratchet.run_minutes` and is disclosed as mine, not the finder's (ev/window_now.txt):
  - The 8-run medians span 32.916..34.575, which reproduces the body exactly.
  - In the ci-ratchet cut simulation, cut 28 s gives 32.683..34.108 and cut 36 s gives median 33.341. Both reproduce the body exactly.
  - The window median reads 33.925 against the body's 33.867. My window holds runs created after the body's 2026-11-01 gather (newest at 06:24:34Z), so the median is not exactly re-derivable.
- Figure not re-derived: the 40-run p90 "34.267 -> 35.317" (payment 1). On today's moved window it reads 35.067 to 35.15 (ev/p90_40.txt). The band is still the looser bound, 35.567 against at most 35.317, so the comparison's direction holds. The recording window (86 runs of 2026-10-25, p90 34.267, 8-run medians 31.709..33.850) is older than the newest 60 and was not re-gathered.
- Payments: the body lists all three: re-record, critical-path pay-down and wider window. Each is judged with its reason. The round-3 reason for rejecting the re-record is withdrawn and the comparison is corrected. I found no unlisted payment that improves the code. The `prelude` `fetch-depth: 0` checkout (18.5 s) is named in the body with the reason the merge-base derivation needs it. I did not measure any cut to it, so it is not a finding. Adding it to the ci-ratchet cut would still be a workflow change that archscore does not read, and it routes the same way as payment (2). The NULL is stated as NULL and is not presented as an improvement. Nothing is gamed: the band row is the measured upward maximum, 1.300, unpadded.
- Head: the PR head re-read at posting is 9ef51b8215dd7216950f177386fb2f5a8f010a47 (ev/head_at_post.txt, ev/HEAD.txt).
