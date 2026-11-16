Fix review: merge 83d2d614047ee669cd3b80d40fb58c511fb1112a

bus-nonce: 1ad236c585d102cf624bc70a6bd48d5c

## Summary

Round 3 of this review, a delta over the reviewed head 5c753a73c3a222053904e2a26812f7d6c24414ec. The delta is one merge of main, 83d2d61404, whose second parent is f1520e3539 (main with #3620 and #3625). The PR's own three-dot diff has not changed in content: it is the same 9 files, 254 insertions and 130 deletions, and its added and removed lines are byte-identical to the reviewed head's (ev/threedot-compare.txt). The previous verdict was `merge` with no findings, so no earlier finding is still open. The delta touches no `custom_components/` path, so the scope does not widen.

## Evidence

- review_carry: `review_carry.py 5c753a73c 83d2d614` printed `FRESH-REVIEW`, because `83d2d614... is not the automatic merge of its parents` (ev/review_carry.txt). The body says the same. I checked the resolution with a remerge-diff (ev/remerge.txt):
  - There is one conflict, in `dev/governance/config/policy_budgets.json`, in two hunks (lines and tokens).
  - The resolution keeps the PR's raised `tools/audit/briefs/COMMON.md` caps (114 lines, 1697 tokens) and main's re-recorded `D0.md` and `D1.md` caps (76/72 lines, 1112/989 tokens) from #3625.
  - Neither side's value is lost.
  - At this head, the three-dot diff of the budgets file is still only COMMON.md's two caps: 108 to 114 and 1598 to 1697.
- Merge with main: `git merge-tree --write-tree origin/main 83d2d614` exited 0. origin/main is f1520e3539, the head's second parent (ev/merge-tree.txt).
- Version files and claim files: the three-dot diff touches none of them (ev/threedot-stat.txt).
- Role contracts: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Lints at the head, run in a detached worktree (ev/lints-head.txt):
  - `check-wave-script.mjs`: `249 passed, 0 failed`, which matches the body's figure.
  - Planted harness: `driver_refuses_bare=1`, `driver_passes_full=1`, `reader_rows=2`, `reader_counted=1`, `reader_counts_bare=0`. These match the body.
  - `policy_lint.mjs`: `TOTAL: 0 error(s) across 51 policy file(s)`.
  - `--budgets`: the COMMON.md row is 114/114 lines and 1697/1697 tokens. The corpus is `~67178` against the cap `67155 +band 500 = 67655`, so it is inside its band. The body's older corpus figures were taken at earlier mains.
  - `structure.py`: `STRUCTURE RATCHET PASSED`.
  - `rules_sync --check`: ok.
  - `brief_lint.mjs`: rc 0.
- Mutation proof at this head (ev/mutants.txt). Each mutant was applied, graded with check-wave-script.mjs and restored. Every one exited 1:
  - `denominatorGaps` renamed: `FAIL ...and the driver enforces it` and `D.denominatorGaps is not a function`.
  - `denominatorGaps` returning `[]`: 11 failed, including `refuses a step with no row`.
  - `enumerator` dropped from the coverage rows' `required`: `FAIL the finder report schema's coverage rows require the denominator`.
  - No mutant survived.
- Budget raise (step 14): unchanged from rounds 1 and 2. The delta adds no COMMON.md text and the caps are the same, so the earlier judgement of the payments stands.
- Body head (step 7): the body's `## Head` names 83d2d614047ee669cd3b80d40fb58c511fb1112a.
- Carry audit: the packet's `carry_audit.py` run at the head found 6 items, all routed.
- CI: I polled `merge_train.py classify 83d2d614... --pr 3647` until it returned rc 4 (ev/classify.txt):

  `APPROVAL-OWED 83d2d614047ee669cd3b80d40fb58c511fb1112a 2 budget raise(s), first .claude/workflows/policy_budgets.json: files.tools/audit/briefs/COMMON.md: 108 -> 114 (a cap went up): a raise is the owner's (0013): tvofi's approval is on 08e362499d6b, not this head 83d2d614047e: an approval covers only the commit it was given on`

  The only red is the budget raise's approval, which follows this verdict, so I judge the head GREEN.
  - `instrument-self-tests` concluded success, which clears the packet's fail-closed `introduced-red` refusal.
  - `tests / nightly-status` is red, but it is not in the owed-reds set (ev/owed-reds.txt), so it owes no answer.
  - `gate` and `budget-raise-gate` are red only on the raise's approval.
- Head re-read before return: `fix/r11-pre-finder-contract-pr` is still at 83d2d614047ee669cd3b80d40fb58c511fb1112a (ev/head-reread.txt).
