Review of PR #3730 at bc02ae8701128c21146bee16d1260fa44e6e4bae, from a detached worktree at that SHA; live head re-read via refs/pull/3730/head before publishing.

Check: python3 tools/audit/seat/plan_phases.py --check dev/programme/round11/phases.json -> rc=0 (passes).

Dates the brief asked for:
- plan finished 2026-11-18T11:26:49Z, exit "owner confirmed plan/r11 819aa2e3": consistent with owner confirmation 11:26:49Z.
- fix-waves started 2026-11-18T12:23:00Z: consistent with first fixers fired 12:23Z.
- P3-DONE 2026-11-18T09:50Z: not recorded anywhere (plan has no started, verify-judge has no finished). Nothing contradicts it; it is an omission, not the blocking reason.

Blocking: the file contradicts itself or the record
1. round-start items set status "done" but keep details that say the opposite:
   R11-PRE-FINDER-CONTRACT, -BRIEFS-CENSUS, -BRIEFS-TEXT, -OWNER-CRITERIA "fixer running since 12:05Z";
   R11-PRE-NEW-DIMENSIONS "design first, not yet dispatched"; R11-PRE-ROUND-METRICS part 1 "fixer running since 12:43Z";
   Owner card rulings "48 cards, 2 still to rule"; Round-10 objective record "pull request #3611 open, in review";
   Outside work "#3598 in review, #3602 in repair, #3529 open"; Instrument groups "... in design ...".
   Either the status or the detail is false; the record cannot support both.
2. fix-waves item "Merged: #3714 #3717 #3720 #3721". Merge commits on main:
   #3717 bc658f9d 2026-11-18T11:32:08Z, before the phase's own start 12:23Z;
   #3714 79385228 13:09:53Z, #3720 f3c615e7 13:03:08Z, #3721 ae0ed64a 13:21:22Z.
   All four are R11-OUTSIDE / R11-PRE branches (fix/r11-outside-honest-*, fix/r11-pre-security-privacy-*), not plan/r11 fixer groups.
   A "Merged" item is also "running".

Notes (non-blocking)
- entry/exit removed from every phase but plan, and the finders forecast removed; the rendered page loses them.
- done phases round-start and verify-judge carry no finished date; finders carries no exit.
- indentation changed from 1 to 2 spaces, inflating the diff (120+/115-).
