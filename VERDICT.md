Fix review: merge 45bd0ee0173837d38c12bc1fcb3578b6aa1dea99
bus-nonce: 4bbde04764ffd3b206ea1fdfe9b662af

PR #2376, review round 2. I measured head 45bd0ee0173837d38c12bc1fcb3578b6aa1dea99. Since round 1 (06f100951) it adds fbd4b2296 and 1e44fb2d1, plus a merge of origin/main 99cf51c1a. The three-dot diff touches only tools/pr/ci_predict.py, tools/pr/prepr.sh, dev/audit/rca/R10-RCA-INERT-PREDICT.md and dev/programme/delivery/2376.md. The roles contract has no difference against origin/main.

## Round-1 block, repaired

- RESULT selftest unmutated=280/0 rc=0 (230 s, ev/selftest_unmutated.txt). The new arms pass: "6d refuses an INERT READS a new top-level import adds (the import-edge arm)", "--apply-inert writes the import-edge arm's entry too, and the prediction then clears", and "6d's step line names --apply-inert ... when every red is an INERT READS".
- RESULT mutant_A (round 1's survivor: drop the import-edge `pairs.add` in under_scoped; ev/mutA.diff) = 279/1, rc=2. It fails with "--apply-inert writes the import-edge arm's entry too, and the prediction then clears (got 1, wanted 0)". **Caught**, so the block is repaired.

## Reviewer's round-2 mutant

- RESULT mutant_D (`who`: `inert == reds` changed to `inert`, so a mixed INERT READS + UNDER-SCOPED prediction would claim "`--apply-inert` repairs them"; ev/mutD.diff) = 280/0, rc=0. **It survives.** Nothing pins the mixed-case wording.
- Not blocking. It is message text only: the rc and the PREDICT lines are unchanged. After one `--apply-inert`, the re-prediction has inert=0 and prints the ci-autofix.md pointer for whatever remains, so a misled seat is corrected on its next run. Recommended for a later pass: a mixed plant (pinert plus an UNDER-SCOPED edge) asserting "the rest is ci-autofix.md's".

## Carried from round 1, unchanged by this delta

- Class search: 60 commits, 11 bot, 49 hand. Since #2129 there are 14 hand commits in 14 distinct PRs over 2.11 days.
- Demo: red on a plant, green after apply, the clean diff unchanged, and the PR's own `if added and False:` mutant caught.
- Evidence for these: refs/heads/review/2376 at 71e5eaf22, evidence/. The delta does not touch the walker's inputs or the sibling arm's code.

## Other checks

- Check-runs at 45bd0ee0173837d38c12bc1fcb3578b6aa1dea99: 28 success, 15 skipped, 1 neutral (CodeQL), and 1 in progress (CodeQL "Analyze (python)", not a gate). There are 0 failures (ev/checkruns_45bd0ee0173837d38c12bc1fcb3578b6aa1dea99.txt). The intermediate commits carry no runs. The body's "Red checks: none" holds.
- `git merge-tree --write-tree origin/main HEAD` gives rc=0.
- Closing keywords: none in the body or the branch commits.
- Policy: no policy file or CODEOWNERS path is in the diff. The ci-autofix.md sentence stays a draft in RCA section 5. **tvofi's approval is owed** before it lands, and it does not block this PR.
- VERSION, the manifest and the notes heading are untouched. The body names 45bd0ee0173837d38c12bc1fcb3578b6aa1dea99 as its head.
