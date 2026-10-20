Fix review: merge ca8791070cd475c98e3705583d707edca39abe11

bus-nonce: 257e79cb9b79f69df87f6d675df8b91b

Round 1. Measured head ca8791070cd475c98e3705583d707edca39abe11 (still the PR head when posted); merge base = origin/main a65438c46.

- Diff scope: `origin/main...HEAD` touches only dev/programme/rosters/wave-r10-groups.json and dev/programme/delivery/2475.md (its own row). No dev/governance/roles/ change since the merge base.
- Figures recounted from the JSON (ev/origin_main.json, ev/HEAD.json): groups 90 -> 91, stage done 43 -> 43, carries 198 -> 201. R10-CI-LAYOUT 13 -> 14, R10-ROSTER-OPS 2 -> 3, R10-UPDATE-PR-SIGNALS new, wave 2, stage queued, 1 carry. All confirmed.
- R10-UPDATE-PR-SIGNALS carry: its three bullets match the three Forward-carry items in #2469's body (git show origin/handoff-body/r10-rca-worktree-vanish:BODY.md, ev/2469BODY.md), each marked Carry: R10-UPDATE-PR-SIGNALS. Same text.
- R10-CI-LAYOUT carry: matches #2464's merged body (MERGED 2026-10-20T04:44:24Z), second Forward-carry item (reused exclusion/_CIR_REUSE/budget pin, plus the harness_headers alone-phase pin). The first item (W1 composed-closure) and the R10-STAMP item were not part of this diff; the first already exists on the group, the R10-STAMP one was not asked for.
- R10-ROSTER-OPS added carry (ps dependency, "#2469 round 3 reviewer note"): I could not locate its source text in #2469's body or comments, so it is NOT verified against a source; it is additive and non-blocking.
- Mergeability: `git merge-tree --write-tree origin/main HEAD` rc=0 (tree 1ca22ab71), no conflicts.
- CI at this head via check-runs API, all 46 runs completed: success/skipped except CodeQL neutral (ev/checks.tsv). closures, fast (3.14) and the Analyze runs concluded success. No red check, so no root-cause answer owed.
- Mutation/harness/null-control steps do not apply: the diff writes no production code.
