Fix review: merge 71b40615a67c4a54ded67a9ddd3d96ebdf9f666f

bus-nonce: 77d60b2904cc405e8f4bb361a1d27781

Round 1. Triage record only (dev/programme/triage/s6-batch117.md plus delivery row 3202.md); no production code, so no mutation proof, null control, claim-file drift, or version check applies (diff touches neither VERSION nor claim files).

## Evidence
- Head measured: 71b40615a67c4a54ded67a9ddd3d96ebdf9f666f; PR head ref still equals it at posting.
- CI: `merge_train.py classify` exit 0: GREEN 71b40615a67c4a54ded67a9ddd3d96ebdf9f666f pending: none red: none.
- Merge: `git merge-tree --write-tree origin/main HEAD` exit 0, clean, no MERGE-CLAIM lines.
- Verdict grammar vs proposal-triage.md: P379 DEFER names what would change the answer and the owning group; P380 REJECT names the binding cost; P381 ACCEPT names destination R10-TICK-LEVELS with carry text citing `triage: dev/programme/triage/s6-batch117.md#P381`. Each entry has Verdict/Source/Instances/Cost/Binding.
- Destinations: R10-TICK-LEVELS, R10-CI-PRIORITY-PAUSE, R10-TRIAGE-S6 and the four other R10-HOTFIX groups exist in the roster at handoff/audit-r10-roster (9bc39aede); R10-CI-PRIORITY-PAUSE is after R10-TICK-LEVELS as stated.
- Numbering: P372 is in s6-batch114, P373-P377 in s6-batch115 on main; P378 only in #3203's batch 116; no P379-P381 anywhere else. No collision.
- Re-derived from git: 8e90d8144 merged 12:03+01 (=11:03Z); 3583448e1 17:36+01 (=16:36Z), one first-parent commit in range; abf21ae34 at 15:51:57Z; handoff-body ad7f27a7f 12:19:15Z; 98beb50fd 11:35Z and 39e9abd50 is its ancestor. Line cites checked in the tree: prepr.sh 21/1028/1621/2860, merge_train.py 137/2889 and 7454 lines, train.sh 33/90, tests.yml 2265-2267, cloud_relay.sh 596 (48 h window). orchestrator_tick.py 903-913 is in #3200, not main, as the record says.
- carry_audit at head: 0 finding items. figure_lint (packet): 0 resolved, 1 not verified (a `git diff --stat` cite); I could not run figure_lint standalone (no such file at tools/audit/figure_lint.mjs).
- Not re-derived (session-local logs and gh/API data this seat cannot read): train.log counts (0 and 14), the filer's 13 min/4 retries/18 min x3, s9/s11 event and ci_priority logs, queue lines 53-55, #3201/#3089 timestamps, the scratch grep rule runs. The record itself labels the filer's figures as not read.

## Findings
- Residual: the record's Numbering paragraph says batch 116 "exists only on the local branch triage/s9-batch116"; it is now on origin as fix/triage-s9-batch116 (PR #3203, open). Cosmetic, true when written, affects no ruling. Carry: dismissed: stale-by-a-push narration in a triage record, no ruling depends on it
