Fix review: merge a30b9d94e7c9d94394b7d81b9e4a030fd95fd478

bus-nonce: 0438a8ea9fe8982aeb5513c3b2e28ffa

PR #1838, R9-F10.4. This is a delta review of a main merge, following `Fix review: merge e37cefc60a41b2cf2f134672b40dc02478dcd5a9`. The head a30b9d94 has parents e37cefc6 (the reviewed head) and 7c94526f (main, #1842). I judged only the resolution delta, from a detached worktree at a30b9d94. The briefs and rules at origin/main show no diff against this worktree's merge base, so the contract I read is current.

## The merge

- `git merge-tree --write-tree e37cefc6 7c94526f` exits 1. Its one conflict is `.claude/workflows/brief_lint.mjs`, and the auto tree is 0614d7e4.
- `git diff --stat 0614d7e4 a30b9d94` touches only `brief_lint.mjs`. Every other path equals git's automatic result. See merge_check.txt.
- The head's `brief_lint.mjs` blob is 95e02dd5. That is the blob at main 7c94526f, so the file equals main's byte for byte.

## Read back against both parents (orchestrator.md section 6)

- **#1838's side, relative to the base:** one change. It deleted the `{W1-G8, metric, coordinator_loc}` row from `REQUIRED_931DFFE` and left a comment saying the pin went with the key.
- **Main's side (#1842):** keeps that row with `whileBudgetKey: 'coordinator_loc'`. It adds `held = required.filter(r => !r.whileBudgetKey || r.whileBudgetKey in budgets())`, and it reports `held.length`.
- **What the merge keeps:** #1838's intent survives as an effect, not as text. At this head `coordinator_loc` is not a key in `tests/structure_budgets.json` (0 occurrences, 1 at main), so the pin drops out exactly as #1838's deletion made it do. The only thing lost from #1838's side is its explanatory comment. Main's comment says the same thing. No clause that matters was lost on either side.

## RESULT lines

- RESULT brief_lint head: `node .claude/workflows/brief_lint.mjs` rc=0, `FIXTURE ok: 14 error(s) pin the 931dffe acceptance (9 required)` (bl_head.txt).
- RESULT mutant M1, `held = required` (the whileBudgetKey filter dropped): rc=1, `FIXTURE VACUOUS: 931dffe acceptance pins missing: [W1-G8] metric: coordinator_loc` (bl_m1.txt). The resolution's filter is what keeps the fixture green here.
- RESULT mutant M2, #1838's own side (blob 4e2f9a0b) substituted: rc=0, 14 errors / 9 required (bl_m2.txt). The two sides agree on behaviour at this tree, so taking main's side costs #1838 nothing.
- RESULT control M3, `coordinator_loc` reinstated as a budget key: rc=0, 15 errors / 10 required, and the coordinator_loc literal error fires (bl_m3.txt). The conditioned pin still goes live when its key exists. Restored afterwards, with a clean worktree.
- RESULT structure: `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`. The merge changes no `structure_budgets.json` or `structure.py` lines relative to e37cefc6 (structure.txt).

## Body, CI and head

- The body's `## Head` section names a30b9d94, describes this merge and quotes the same fixture line. One leftover in the `briefs` red-answer bullet still says the PR "drops the pin in its own `brief_lint.mjs`". That bullet is labelled as being about a980e165, and the Head section corrects it, so I do not block on it.
- CI at a30b9d94 (check_runs.json/.txt, 35 runs): everything completed. All are success or skipped except for these:
  - `budget-raise-gate` failure. The body answers it: it stays red by design until tvofi's approving review at this head, because the PR raises `dead_methods` and `coordinator_multiassigned_attrs`.
  - One `budget-raise-gate` and one `pr-contract` cancelled. Each is superseded by a completed run on the same head (`pr-contract` success).
  - `CodeQL` neutral.
- `briefs` is now **success**. Main's conditioned linter, which CI restores from the base, settles the red the body recorded at a980e165.
- `fast (3.14)` is `MODE: SCOPED -- 24 script(s) run, 4 scoped out.` R9-F2.1 P3 and its null arm are `ok` on CI. The P3 failure on this Mac is the BLAS case and is not this PR's.
- The live head when I posted was a30b9d94e7c9d94394b7d81b9e4a030fd95fd478, the head I measured.

The owner's approving review is still required for the budget raise and the code-owned paths. This verdict does not replace it.
