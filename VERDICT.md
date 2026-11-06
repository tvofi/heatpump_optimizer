Fix review: merge 195ef4432452bd359922578e910b1bde4e3deb24

bus-nonce: ec2078fcbf2b8020a4901870141d76e3

CI-only re-check, round 2 (round 1 blocked 9e2f045e6c6d8de6c76c403d25f5555fea8c1e4d on cancelled runs only). Content not re-reviewed.

## Evidence
- review_carry 9e2f045e6 -> 195ef4432452bd359922578e910b1bde4e3deb24: CARRY (one branch-only commit, a main merge, no resolution).
- classify 195ef4432452bd359922578e910b1bde4e3deb24 --pr 3209: GREEN, pending none, red none (rc 0).
- All check-run pages listed (ev/check-runs.tsv): the fresh gate run (2026-11-06T00:33Z) has gate, arch-score, budget-raise-gate, pr-contract success. The 2026-11-04T22:5x cancellations belong to the old head and are superseded; no cancelled or pending run remains on this head.
- Two failures remain, both grading main and not this diff: tests / nightly-status (exit 1, run 23:57Z) and governance / delivery-status (DELIVERY STATUS OVERDUE on other rows #3205/#3206; log says not a required context). The diff only adds a triage file and a delivery row, touching nothing they read, so no answer is owed.
- PR body ## Head names 195ef4432452bd359922578e910b1bde4e3deb24. merge-tree with origin/main: ev/merge-tree.txt.

## Findings
- Follow-up: P383 may need renumbering if #3204 (P382, s6-batch118) lands first. Carry: dismissed: record-only; orchestrator renumbers at merge
- Follow-up: the held-worktree reproduction in the P383 entry should be re-run at its own base by the fixer. Carry: R10-CLOSEOUT-CLEANUP
