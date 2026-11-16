Fix review: merge 5c753a73c3a222053904e2a26812f7d6c24414ec

bus-nonce: 20788bb07615bfd7226ad61afab23f2d

## Summary

Round 2 of this review. It is a delta over the reviewed head e1a6bedad8dfa5a2b29c51c40022456ca241da81. The delta is two merges of main: 08e362499d ("ci: merge main") and 5c753a73c3. The PR's own three-dot diff is unchanged in content: the same 9 files, 254 insertions and 130 deletions. The previous verdict was `merge` with no findings, so no prior finding is open. The delta touches no `custom_components/` path, so the scope does not widen.

## Evidence

- review_carry: `review_carry.py e1a6bedad 5c753a73c` printed `FRESH-REVIEW`. The reason was `5c753a73c is not the automatic merge of its parents`. The body says the same. I checked the resolution by remerge-diff (ev/merge.txt).
  - 08e362499d: the only driver line is `LEDGER-MERGE: resolved tests/closures.json`. There is no textual resolution.
  - 5c753a73c3: one hand resolution, in `dev/audit/README.md` Round start. It keeps the PR's step 3 (`COMMON.md`, `finding.schema.json`'s `coverage`, `audit-find.js`'s `denominatorGaps`). It keeps main's new step 4 (Proposals). It renumbers Scope to step 5. Neither side's text is lost, and the PR's removal of the carry-31 paragraph is kept.
  - `tests/closures.json` was resolved by the ledger driver, set-merged.
- Merge with main: `git merge-tree --write-tree origin/main 5c753a73c3` exited 0. origin/main is 4ce615b5e6, the head's second parent (ev/merge.txt).
- Version files: the three-dot diff touches none of `VERSION`, the manifest or `RELEASE_NOTES.md`.
- Claim files: the diff touches no golden or claim file.
- Role contracts: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract read is current.
- Lints at the head, in a detached worktree (ev/lints-head.txt):
  - `check-wave-script.mjs`: `249 passed, 0 failed`, the body's figure.
  - Planted harness: `driver_refuses_bare=1`, `driver_passes_full=1`, `reader_rows=2`, `reader_counted=1`, `reader_counts_bare=0`, the body's figures. The harness is the fixer's, as round 1 noted. The finding is a contract change with no separate finder's harness.
  - `policy_lint.mjs`: `TOTAL: 0 error(s) across 51 policy file(s)`.
  - `--budgets`: the COMMON.md row is 114/114 lines and 1697/1697 tokens. The corpus is `~66241` against `66226 +band 500 = 66726`. The body's merged-tree corpus figure (`~66010` against 66426) was taken at an older main. At this head the corpus is still inside its band.
  - `structure.py`: `STRUCTURE RATCHET PASSED`.
  - `rules_sync --check`: ok.
  - `brief_lint.mjs`: rc 0.
- Mutation proof at this head (ev/mutants.txt). Each mutant was applied, graded with check-wave-script.mjs, then restored. Every one exited 1:
  - `denominatorGaps` renamed: 25 failed, including `...and the driver enforces it` and `round 9 dispatches exactly the scopes.json seats`.
  - `denominatorGaps` returning no gaps: 11 failed, including `refuses a step with no row`.
  - `enumerator` dropped from the coverage rows' `required`: 2 failed, including `the finder report schema's coverage rows require the denominator`.
  - No survivor.
- Budget raise (step 14): unchanged from round 1. The delta adds no text to COMMON.md, and its caps are still 114/1697. Round 1's judgement of the payments stands.
- Body head (step 7): the body's `## Head` names 5c753a73c3a222053904e2a26812f7d6c24414ec, the head reviewed here.
- Carry audit: the packet's run of `carry_audit.py` at the head found 6 items, all routed.
- Red checks: `merge_train.py owed-reds` was read (ev/owed-reds.txt). The body answers the earlier heads' reds.
- CI: I polled `merge_train.py classify 5c753a73c3a222053904e2a26812f7d6c24414ec --pr 3647` until it returned rc 4: `APPROVAL-OWED 5c753a73c3a222053904e2a26812f7d6c24414ec 2 budget raise(s), first .claude/workflows/policy_budgets.json: files.tools/audit/briefs/COMMON.md: 108 -> 114 (a cap went up): a raise is the owner's (0013): tvofi's approval is on 08e362499d6b, not this head 5c753a73c3a2: an approval covers only the commit it was given on`. The only red is the budget raise's approval, which follows this verdict, so I judge the head GREEN (ev/classify.txt).
  - `tests / nightly-status` is red at the head, but it is not in the owed-reds set, so it owes no answer.
  - `instrument-self-tests` concluded success, which clears the packet's fail-closed `introduced-red` refusal.
- Head re-read before return: `fix/r11-pre-finder-contract-pr` is still at 5c753a73c3a222053904e2a26812f7d6c24414ec (ev/head-reread.txt).
