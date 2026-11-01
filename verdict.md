Fix review: merge afe70dea605d513f01c241d17444735d63c17cb2

bus-nonce: 8e761269756c98ee0ae14eeb02d81ac0

## Findings

- Roster row R10-HOTFIX-AWAY-PRESENCE (PR 3052) reads stage `in-progress`, `commit` null at this head; the handoff/audit-r10-roster file has `done` at 1d28de9936efb7d784224f274232a50722952c02, and PR 3052 is merged (merged_at 2026-11-01T15:36:06Z). This is the only row that differs in resume from the handoff, and it is a stage regression for a merged PR. Not blocking a record PR (origin/main has no such row; roster_sync derives `done` from a merged PR on its next pass), but the orchestrator should set it done at the next beat. Carry: R10-ROSTER-OPS
- Six carry strings differ from the handoff copy (groups 146, 220, 259 ordering, 273, 274, 286, 290), consistent with the host-path scrub; the groups[259] carry list is reordered. No group dropped or added (302 vs 302). Not re-derived character by character. Carry: dismissed: scrub differences only, no rows lost.

## Evidence

- Diff three-dot against merge-base d052f80f: exactly dev/programme/delivery/3118.md (+1, row present) and dev/programme/rosters/wave-r10-groups.json. 
- claimed_drift.txt, card_claimed_drift.txt, VERSION byte-identical to base; no VERSION/manifest/RELEASE_NOTES change.
- Roster parses; 302 groups, same set as handoff; main had 236, all retained.
- Versus origin/main file: five stage moves look backward (R10-UX-HEALTH in-progress to carries-open, R10-PREPR-CAP carries-open to in-progress, R10-SAV-COMFORT done to carries-open, R10-TRAIN-OVERLAP-GRADE in-review to carries-open, R10-ADVISOR-WHATIF done to carries-open). All five are identical in the handoff file, so they are the handoff's content, not this PR's edit; main's file dates from 2026-10-30.
- policy_lint rc=0 (0 errors), brief_lint rc=0, carry_audit sweep 0 findings; no /Users/ or /home/ in added lines or in the roster file.
- git merge-tree --write-tree origin/main head: clean (tree f89cfe61).
- Head unmoved: refs/pull/3118/head = afe70dea605d513f01c241d17444735d63c17cb2.
- CI: all 46 check-runs read, none red; merge_train classify exit 0 GREEN with pending none, red none. No Red checks to answer.
