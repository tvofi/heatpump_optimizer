Fix review: merge 04b2c9c76c69c7fdcdbbd600ccb4ef204fd8fdc4

bus-nonce: ddcab10b4ca891f6679c0f37631b3918

Round 2, by the same reviewer. I measured 04b2c9c76c69c7fdcdbbd600ccb4ef204fd8fdc4 from a detached worktree, which was clean after the power loss. It was still the head when this verdict was posted. The fixer's round-2 commit is 15abe48e5. The two merges after it are automatic, by the orchestrator. There are no changes to `tools/pr/app_approve.sh` since round 1: the diff 6ac0d3e6..04b2c9c7 on that file is empty.

## RESULT lines (evidence/)

- **Re-bucketing, my own harness.** `rebucket2.py` is independent of hm3 and hm4. It re-derives all 75 entries from the full list of files whose own patch differs.
  - RESULT bucket M: 29 entries, 8 after the split, 2 blocked.
  - RESULT bucket G (4): 28 entries, 7 after, 3 blocked. The lag median is 32 and the sum 1122.
  - RESULT bucket S (5): 18 entries, 6 after, 6 blocked. The lag median is 59.5 and the sum 1200.
  - RESULT mismatches against the new hm4_out.tsv: 0.
  - These match the record's table rows 4 and 5 exactly. The blocked bucket-4 entries are #2411, #2465 and #2576, as stated.
- **CM-2's population.** 23 entries hold a bot commit. 10 of them are bot-only, and 9 of those 10 carried. The other 13 also hold a code or own commit, and all 13 have `carry@t=no`. #2772 is `empty`. All of this matches hm2_out.tsv.
- **#2673's lag** is 42 min, which matches hm2_out.tsv.
- **The 8 flips are unchanged** from round 1: no yes->no, and 8 no->yes (`rerun_carry.tsv`). hm6_out.tsv's edits change only the bucket letters of the 5 re-bucketed entries.
- **Self-test at this head:** 256 checks, 0 failed. Round 1's two mutants still apply, because the file is byte-identical. The section 5 and 6 statements of the totals are now environment-dependent, and that is correct.
- **Section 8 (P242)** matches what I measured in round 1:
  - #2883, #2887 and #2894 have 0 entries.
  - Its direction agrees with CM-2's refusal.
  - The cost sits in bucket 2 and the post-split pushes.
  - #2887's stranded branch is stated as not measured, with no owner named.
- **Checks:** none red. Still in progress: codeql python, instrument-self-tests, prelude, closures, coverage (`check_runs_r2.tsv`). `## Red checks: none`, `## Head` names this head.

## Non-blocking (n2753.txt)

Section 5 says the tenth bot-only entry, #2753 at 2026-10-26T01:36, "is the bucket 2b context case". Its cause is right but its bucket is loose:

- The refusal is `coordinator.py`. That file is equal at -U0 and differs at -U3, which is the 2b shape.
- `structure_budgets.json` also differs, but it is a ledgermerge driver file, so the carry excludes it.
- The entry sits in bucket 4 of the table, because its -U0 own patch moved in `structure_budgets.json`.
- The 2b row's #2753 is the 2026-10-25T15:45 entry.

No figure changes because of this.
