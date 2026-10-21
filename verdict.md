Fix review: merge 1beed40bfefac3265b2c2dd8551a0b51d47f9ade

Round 1. Group none: no entry in wave-r10-groups.json for topic r10-cloud-rev-head-ev; reviewed against the PR body. Contract current (roles/ diff merge-base...origin/main empty). Measured at 1beed40bfefac3265b2c2dd8551a0b51d47f9ade from a detached worktree; head re-read before return, unchanged.

- RESULT mutation-1: removing the new prompt clause -> self-test 30 checks, 1 failed ("the reviewer is told a file under ev/ must contain the full head"), matches body. ev/selftest-mutant1.txt
- RESULT mutation-2 (own): keeping the words but dropping the `{head}` interpolation -> same check fails. ev/selftest-mutant2.txt
- RESULT null: head self-test 30 checks, 0 failed; origin/main 03b49e152 29 checks, 0 failed, clause absent. ev/selftest-head.txt, ev/null-main.txt
- RESULT defect: probe/rev-2544-131f9c75 and probe/rev-2513-e19a37e0 each have 0 ev/ files naming their verdict head; bus.sh push-verdict (line 210, grep -rqF) refuses that. ev/probe-refs.txt
- Harness: the finding has no committed finder harness; the instrument is the fixer's --self-test plus bus.sh's own gate. I re-ran both ends myself and added mutation-2.
- Class: one seam (the reviewer prompt string); fixer/probe prompts return no verdict to bus.sh. No rule named; the issue states one seam.
- Claims/VERSION/manifest/notes/golden: untouched (diff is cloud_dispatch.py + delivery/2556.md). No figures, no forward-carry.
- Merge: `git merge-tree --write-tree origin/main 1beed40bfefac3265b2c2dd8551a0b51d47f9ade` exit 0. 59df92b8c's merge resolution delta vs main is only the fix diff. ev/merge-tree.txt
- CI on head (49 check runs, all concluded): all success/skipped except nightly-status, which grades main's nightly run 39563978649 (mutation-nightly, slow); this diff doesn't reach those lanes, so it isn't this PR's red. ev/checkruns.tsv, ev/nightly-status.txt

bus-nonce: 8050f8455f4c5acf6630039ed48b434c
