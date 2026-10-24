Fix reviewer, PR #2637 (tvofi/heatpump_optimizer), roster batch 18 (roster ops, sonnet). Head 0662d20c57d24742da549682641da687477557ab. Follow dev/governance/roles/fix-review.md from a detached worktree at that head. Re-read the head first; if it moved, the verdict is blocked.

Check:
1. Each of the 8 ops in the body lands as stated (git show each sha, or diff dev/programme/rosters/wave-r10-groups.json three-dot against origin/main):
   - R10-SCORES routings to R10-UX-HEALTH (9a4953627) and R10-PARAMS-OWNER (c3711a1f0, 75c891e28);
   - the P-C carry on R10-FLY-RELAY-REVIEW-FF (600635c16);
   - new groups R10-FLY-SUITE-ENV-FLAKES (d37aa1b1f) and R10-FLY-NO-FOOTERS (4d79efd87);
   - set-stage done for R10-BRIEFS-FOLD (62be37fe3, merged as #2631 b24cfe51) and R10-NIGHTLY-ABSENT-NEW (3e7aaed31, merged as #2627 e364a0d7).
2. Counts: groups 165 to 167, 2 new, 5 changed, 0 removed; stages done 86 to 88, in-progress 13 to 12, not-started 59 to 60.
3. Each carry's text equals its source verbatim (the R10-SCORES PR body at origin/handoff-body/r10-scores; the triage Batch 4 text is quoted in the body). No host paths and no Claude text.
4. Each done stage matches a merged PR whose merge commit is an ancestor of origin/main.
5. brief_lint reports 0 errors, ref_privacy --check reports 0 refused, and the null control is real. Read CI at the head from check-runs.

ev/HEAD.txt must hold the full 40-hex head sha, or the relay refuses the verdict.
Do not add Claude Code footers, Co-Authored-By/Claude-Session trailers or any claude.ai session link to commits, verdicts or comments.
