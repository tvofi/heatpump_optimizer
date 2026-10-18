Fix review: blocked 06f1009511bf2be615dbf9ec65421a5b0f3892c1 mutant-survives: deleting the import-edge arm's pairs.add in under_scoped (ci_predict.py:187-188) leaves prepr --self-test at 277 passed, 0 failed
bus-nonce: 679a999f42f648a3c158237759df55b8

PR #2376, review round 1. Measured head 06f1009511bf2be615dbf9ec65421a5b0f3892c1, which is still refs/pull/2376/head when re-read before push. Merge base 9a1ce39c3. Contract copy: dev/governance/roles/ shows no difference between the merge base and origin/main. Python: seat venv 3.14.7, from the shims.

## What blocks

The RCA (section 5.1) and the new docstring both say `--apply-inert` "collects the (script, file) pairs from both INERT READS arms, the sibling glob and the import edge". Only the sibling arm is pinned.

- Reviewer mutant A (ev/mutA.diff) removes `if pairs is not None: pairs.add((script, b))` from `under_scoped`. The full `tools/pr/prepr.sh --self-test` then ends `277 passed, 0 failed`, rc=0 (ev/selftest_mutA.txt). The mutant survives.
- It is a real behaviour, not dead code. I planted an import-edge INERT READS: `tests/wood_advisor.py` gains a top-level `import tools.audit.seat.moved_paths` (ev/demo_edge_red.txt). Unmutated, the predictor goes rc=1, then `APPLIED inert_reads tests/wood_advisor.py: tools/audit/seat/moved_paths.py`, then rc=0, and `layout_errors` returns [] (ev/demo_edge_apply.txt). Under mutant A, `--apply-inert` applies nothing and stays rc=1 (ev/mutA_edge_apply.txt).
- The failure direction is safe: the refusal stays, so nothing goes falsely green. The countermeasure's claimed behaviour is still unpinned, and `defect-root-cause.md` wants a countermeasure mutation-proven.
- **Repair:** one self-test arm, beside `pinert`, for an import-edge plant. Example: a selectable script gains a top-level import of an INERT `.py`, then `--apply-inert` must print `APPLIED` and end rc=0. Re-run mutant A against it.

## What was verified (RESULT lines)

- RESULT class_search total=60 bot=11 hand=49. I wrote my own walker, ev/class_search_review.py: non-merge commits touching tests/closures.json whose inert_reads pair set grows; "bot" means the subject is `ci: re-record closures` or the author has [bot]. It gives the same counts at 52f698905 and at origin/main (ev/class_search_52f.txt, ev/class_search_main.txt). The bot rows are all github-actions[bot]; the hand rows are tvofi 45, fixer 2, Tvofi2 2. **Confirmed**, under my own definition.
- RESULT post_2129 bot=3 hand=15 harness_headers_hand=14 distinct_prs=14. #2129 merged at 0ae0a470c, 2026-10-12T13:17:41+02:00. The 14 commits run from d7bfeb0dd (10-14 23:14) to 2f7aafdc8 (10-17 01:59), which is 2.11 days. Each maps through its first-parent merge to a distinct PR: #2212 #2281 #2282 #2284 #2285 #2294 #2293 #2305 #2301 #2329 #2320 #2340 #2339 #2342 (ev/hand_to_pr.txt). There were 17 new dev/audit/harnesses files in the window, and all 17 are listed in harness_headers' inert_reads at origin/main (ev/harness_adds.txt). None of the bot's 3 commits in the window adds a dev/audit/harnesses entry. The 15th hand commit is 0461329ce (entities.py), as the RCA says. **Confirmed.**
- RESULT demo_plant red=rc1 apply=rc0 diff=1-line layout_errors=[] idempotent=yes. The plant is `dev/audit/harnesses/review_2376_plant.py`. Before the apply, PREDICT INERT READS appears with the new route line, rc=1. After it, `APPLIED ...`, rc=0, one inserted line in sorted position. A second `--apply-inert` applies nothing (ev/demo_plant_red.txt, demo_plant_apply.txt, demo_layout.txt, demo_idempotent.txt). **Confirmed.**
- RESULT null_control clean_head rc=0 closures.json_porcelain=empty. This is `--apply-inert` on the PR head itself, with no plant (ev/demo_null_prhead.txt). **Confirmed**, and it is my own null, separate from the self-test's `pnull`.
- RESULT selftest unmutated=277/0 rc=0 (247 s) (ev/selftest_unmutated.txt).
- RESULT mutant_C (the PR's own: `if added and False:`) = 276/1, rc=2, FAIL "--apply-inert writes the predicted entry...". **Caught**, which reproduces the body's mutation proof (ev/selftest_mutC.txt).
- RESULT mutant_B (reviewer: `write_closures` replaced by `json.dumps(indent=2)`) = 276/1, rc=2, FAIL "and it writes the table in the layout closure.layout_errors accepts". **Caught** (ev/selftest_mutB.txt).
- RESULT mutant_A (reviewer: drop the import-edge `pairs.add`) = 277/0, rc=0. **Survives**: this is the block.

## Other checks

- Check-runs at the head: 45 runs, 30 success, 15 skipped, 0 failure (ev/checkruns_head.txt). On 532145c48, 5 runs were cancelled when the head was superseded, and there were no failures. "Red checks: none" holds. `mutation` is green, but this diff writes no production line that would draw a mutant.
- `git merge-tree --write-tree origin/main HEAD` gives rc=0 and no conflicts.
- Closing keywords: none in the body, none in the branch's commit messages. "Part of ... #2371" refers to a PR (R10-LEAF-IMPORTS) and closes nothing. The delivery row's "(R10-LEAF-IMPORTS)" tag matches.
- Policy: the diff touches tools/pr/ci_predict.py, tools/pr/prepr.sh, dev/audit/rca/, and dev/programme/delivery/2376.md. None is in CODEOWNERS or a policy file. The `ci-autofix.md` sentence is a draft only, in RCA section 5, and is not landed. **tvofi's approval is owed for that draft** if it is to land, and it does not block this PR.
- VERSION, the manifest and the notes heading are untouched.
- Body SHA: it names 06f1009511bf2be615dbf9ec65421a5b0f3892c1 as the head, and that is the head I measured.

## Non-blocking notes for the fixer

1. The predictor still prints its old last line, "who repairs which is ci-autofix.md's", right below the new route line. That leaves a weaker pointer beside the route. Consider dropping the pointer when an INERT READS was predicted.
2. The route line says "a Darwin --single cannot record a child's read". That is true for the sibling arm (harness_headers' child scan), but an import-edge INERT read is in-process. The repair is right either way; only the reason is wrong for that arm.
3. The class-search script is out of tree. I rebuilt my own and it agrees; it is ev/class_search_review.py.
