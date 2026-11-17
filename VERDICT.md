Fix review: merge f31110589dc2fe910249a76ac0048d4da1b3a80b

bus-nonce: 5b77d4b4d7d49f36f19c44a149f0c982
pending-ci: gate

## Scope

Round 3. The scope is `delta` over the reviewed head e0238c1fe8. Head reviewed: `f31110589dc2fe910249a76ac0048d4da1b3a80b`. The PR body names this head, and it is the live branch tip (`ev/head_check.txt`). The head is a merge of 3d12f40a50 onto e0238c1fe8, and its tree equals 3d12f40a50's tree. `git diff e0238c1fe8 f31110589d` adds 2 lines to `self_test()` in `tools/audit/seat/shell_hazard.py`. That is an instrument test row, so nothing widens the scope.

## Findings

- Follow-up (unchanged from round 2, outside the delta): the `break` after `out.append((n, "wc-compare", ...))` in `hazards()` still survives `--self-test` (`ev/mutants.txt`, mutant B, rc 0). Without it, a line with two raw wc compares gets a duplicate report line, but its verdict does not change. The body dispositions it under Unpinned sites. Carry: dismissed: duplicate report lines on one already-refused line change no refusal

## Evidence

- Round 2's block is resolved. The new row is `[ "$a" = b ] && [ "$(wc -l <f)" = 3 ]`, which must be refused. With the first-opener mutant applied at the head (`opener = TEST_OPEN.search(pre)` in place of the last-opener loop), `--self-test` prints `FAILED`, rc 1, with exactly that one FAIL row: `got [], want ['wc-compare']`. Null control: the same mutant on e0238c1fe8's file (no row), run in place, prints `ok` rc 0. The unmutated head prints `ok` rc 0. So the row is what kills the mutant, which re-derives the body's round-3 figures (`ev/mutants.txt`). The worktree was confirmed clean with `git status` after each restore.
- Merge with main: `git merge-tree --write-tree origin/main f31110589d` rc 0, no conflict (`ev/merge_tree.txt`).
- Role contract: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` touches only `COMMON.md` (the finder's contract), not `fix-review.md` (`ev/roles_diff.txt`).
- Not re-taken this round: the body's round-2 mutant counts, the 288-line corpus figure (already re-derived in round 2), and the step-6d' survivor list. The delta leaves the code they measure unchanged. Per step 11, I cite CI for the gate and the mutation table.
- Finder's harness: none named (the packet). This is an instrument lane, and round 1 reproduced the instance commits.
- CI at this head: `merge_train.py classify f31110589d --pr 3639` printed `WAIT f31110589dc2fe910249a76ac0048d4da1b3a80b pending: gate red: none` on every run from 23:57 to 00:26 UTC (`ev/classify.log`). No owed red is reported. I stopped waiting after about 30 minutes, as the brief says, so this verdict carries `pending-ci: gate`.
