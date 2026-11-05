Fix review: merge ece7cbabb8bd012617692eaeb8ef585f13ee1f4e

bus-nonce: e13af1b0c50e8472de6afcb8390324ba

## Summary

Round 3 of the fix review of #3227 (R10-BODY-CONTRACT). There were two blocking reviews before this one; this is the repair round 2 head. I measured head `ece7cbabb8bd012617692eaeb8ef585f13ee1f4e` from a detached worktree. The merge base is `b707d89329c746c870d07e0b1725e644874078dc`. The role files have not changed on main since the merge base (`git diff <mb>...origin/main -- dev/governance/roles/` is empty). Every arm the body names has a mutant that I re-derived and that turns its self-test red, and every null control holds. Running the live bodies of #3170, #3198, #3218, #3220 and #3222 through the new checks refuses none of them. The head merges cleanly with current origin/main and with #3221's head. The verdict is merge. The policy text below needs the owner's approving review at merge.

## Policy text changed (for the owner)

Three-dot diff, `ev/policy-diff.txt`. The diff edits more than "one sentence each". It makes four edits in `dev/governance/roles/fix-review.md` and five in `dev/governance/roles/judge.md`. Only one sentence in each file is a new rule: the rest are trims made to stay under the token caps. The body's `## Approval` section lists every change correctly:
- fix-review.md step 2: removed "A fixer who measures with a harness they wrote is measuring themselves."
- fix-review.md step 14: "judge each payment the body lists" became "judge each listed payment".
- fix-review.md closing: "owes a re-cut, not a repair." became "owes a re-cut."
- fix-review.md, ADDED: "A ruling naming a destination stage states it as a `Carry:` marker."
- judge.md opening: "You do not trust the finders or the verifiers;" became "You trust neither finders nor verifiers;"
- judge.md step 3: "Compare the metric definitions the finder and the verifiers wrote. Where they measured different things, mark the votes `not comparable` ..." became "Compare the metric definitions; where they differ, mark the votes `not comparable` ..."
- judge.md step 7: "`unreproduced` is no kill and no pass: the round is not dry until it is re-measured or refuted." became "`unreproduced` is no kill, no pass: re-measure or refute it before the round is dry."
- judge.md closing, ADDED: "A ruling naming a destination stage states it as a `Carry:` marker."

The step 2 removal drops the stated reason, not the rule ("Measure with the finder's harness" stays). The other trims keep their meaning.

## Findings

- A body that closes two issues can answer both with one `Fold (x):` line. `fold_problems` keys answers by letter only. `Closes #7` plus `Closes #8`, each issue with a `Fold (a):` ask, and one `Fold (a): built` line returns no problems (probe in `ev/probes.txt`). Answers should be keyed per issue, for example `Fold (#8 a):`, or a fold letter shared across closed issues should be refused. The body does not disposition this. Carry: R10-BODY-CONTRACT
- The issue-side `FOLD_LINE` also misses `Fold(a):` with no space before the parenthesis. This is in addition to `Fold (A):` and `**Fold (a)**:`, which the body already carries. All three return no fold, so the close passes unchecked (probe in `ev/probes.txt`). None of the five live bodies closes an issue, so no live body exercises the fold check. Carry: R10-BODY-CONTRACT
- The body's Figures line for `node tools/policy/brief_lint.mjs | tail -3` says it shows `TOTAL: 0 error(s)`. At this head the last three lines are the `CONTROL ok` and `TREEREV ok` lines, and no `TOTAL:` line is printed anywhere in the output. The command exits 0, so the lint passes, but the quoted output does not match. Correct the figure's description in the next body. Carry: R10-BODY-CONTRACT
- No finder's harness is named (packet: "Finder's harness: none named"). For this tooling group the arms' own self-tests are the only instrument, and the mutants below were run against them. This verdict adds no harness of its own beyond the throwaway probes in `ev/probes.txt`. Carry: dismissed: tooling group whose self-tests are the committed harness, recorded here per fix-review step 9

## Evidence

- Figures re-run at the head (`ev/figures.txt`): carry_audit self-test 364 checks, 0 failed; carry_fold 6, 0 failed; body_patch 98, 0 failed; body_push 32, 0 failed; brief_lint rc 0 (`CONTROL ok`, `TREEREV ok`); `STRUCTURE RATCHET PASSED`; `bare_array.py --check` rc 0; policy budgets fix-review.md 137/140 lines and 2440/2451 tokens, judge.md 29/30 lines and 467/469 tokens, matching the body's figures.
- No `*budget*` file is in the diff. VERSION, the manifest and RELEASE_NOTES.md are untouched against the merge base. Both claim files are byte-identical to origin/main.
- Mutants, each run and restored (`ev/mutants.txt`): postfold `[]` (1 failed), `if bad:` changed to `if False:` (1), `# mut:branch` changed to `pass` (1), `fold_rc = 0` (2), live() `CARRY_CLOSED` changed to `DONE_STAGES` (1, the absorbed arm), `pr_group_of` returning None (3), trailer alternation dropped (2), HTML-comment strip dropped (1), dismissal pointer branch off (1), brief_lint `if (!names)` changed to `if (false)` (`CONTROL VACUOUS`), `treeListing(undefined, cwd)` (`TREEREV VACUOUS`), body_push `# mut:keep` emptied (18 failed), body_patch treerev (self-test's own mutant row fails). All killed.
- LEGACY_CONTROL_FILES narrowing: with the exemption removed, every one of the 15 listed files fires the control lint and no file outside the list fires an error, so the set is exactly the failing files and hides no passing control. Two non-legacy files (carry-1922.json, carry-2075.json) print only WARNINGs, both at the head and without the narrowing.
- Over-firing: the live bodies of #3170, #3198, #3218, #3220 and #3222 were run through `carry_audit.py check --body ... --branch <head ref>` at the head and through main's checker. Results are identical, all rc 0, and `policy_lint.mjs --pr-body` reports 0 errors for each (`ev/live-bodies.txt`). #3227's own body: 11 routed, 0 unrouted, 0 bad.
- carry_fold writes only through `apply` (the `append-carry --push` op the fold returns), refuses before any write on a bad destination, and fails after the fold when `landed()` still reports an item missing. All three behaviours are pinned and mutation-tested above.
- Merge simulation: `git merge-tree --write-tree origin/main <head>` exits rc 0 against origin/main `8bf45e5dcedd3fbeb6842c5bfc7545ba5c8176fc`, with `LEDGER-MERGE: resolved tests/closures.json` (`ev/merge-tree-main.txt`). Against #3221's head `0f6771a7a4b8ca1146d74b81e66bc5b357e45f9b` it also exits rc 0 (`ev/merge-tree-3221.txt`), so the edits to the shared file `body_push.sh` do not conflict.
- `## Head` names ece7cbab, the head I measured.
- Red checks at this head: `governance / delivery-status` (job 127294466018) lists OVERDUE rows of other merged PRs (#3201, #3206, #3189, #3174, #3091, ...). `tests / nightly-status` (job 127294466316) reports `NIGHTLY FAILED: slow failed last night.` Both are inherited, the diff does not reach what they read, and the body answers both against base b707d893 (`ev/job-*.tail.log`).
- CI: `merge_train.py classify ece7cbab... --pr 3227` exited rc 0 at 14:57:24 UTC: `GREEN ece7cbabb8bd012617692eaeb8ef585f13ee1f4e pending: none red: none` (`ev/classify.txt`). Head re-read before publishing: still ece7cbab.
