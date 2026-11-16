Fix review: merge 9e535642649c96ade5a1ad960b37851130319378

bus-nonce: 3e08ab86a08a97fb0422e7df6ef4db07

Round 2 of this pull request (delta review over e078a0bb2e3b4663cc505282d70aaad8053a566b, the packet's `## Review scope: delta`). Reviewed from a detached worktree at 9e535642649c96ade5a1ad960b37851130319378.

## Findings

- Note: paperwork: the body's `## Head` section has two lines saying a merge commit "merges the authored code head 94503ed95b": one names this head, and the other names `e8f23fea178bf755a4b007fda4b26480adaa342e`, which origin does not serve (`not our ref`, ev/delta.txt). It looks like a leftover from an earlier push. The head the body measures is the one reviewed here. Carry: dismissed: body paperwork only; the line names no code, and the next push of the body drops it

## Evidence

- RESULT: delta scope. The PR's own delta since e078a0bb2e is one commit, 94503ed95b (19 added lines of self-test in `tools/audit/enumerate.py` and `tools/audit/seat/finder_overlap.py`), plus the merge of origin/main 92d38ecb64 at 387b83ea0e. That merge's tree equals the automatic `git merge-tree` of 92d38ecb64 and e078a0bb2e except for `dev/programme/delivery/3672.md`, a one-line delivery row (ev/delta.txt). No file under `custom_components/` or `tests/golden/` changes, and neither do `VERSION` or `RELEASE_NOTES.md`, so nothing widens the scope (fix-review.md step 12).
- RESULT: previous block item 1 is resolved. `finder_overlap.py:50`'s seat bound is now pinned. In my mutants at the head, `1[0-5]`, `1[0-6]`, `1[0-8]`, `1[0-9]` and `[0-9]+` are all KILLED by the new case `seat: a D16 and a D17 seat are seated, a D18 one refused`. The unmutated null is `finder_overlap self-test: ok (with mutants)`, rc 0, and the three new `MUTANTS` entries are each killed by the self-test's own mutant pass (ev/mutants.txt). The case seats a synthetic scopes dict rather than the live `scopes.json` the earlier block asked for. It pins the bound either way, and on the live `scopes.json` at the head `seat_pair` still seats `D16-s1` and `D17-s3`.
- RESULT: previous block item 2 is resolved. `kind=a.kind` dropped from `main()`'s call of `run` (`enumerate.py:1020`), and the same kwarg forced to `None`, are both KILLED by `d17 the command line's --kind reaches the filter`. The unmutated null is `SELF-TEST passed (161 arms)`, rc 0 (ev/mutants.txt).
- RESULT: previous items 3 and 4 still survive at the head, as the body says: `enumerate.py:1005` with `choices=KINDS` dropped, and `enumerate.py:130` with `and isinstance(arg.value, str)` dropped, each rc 0 (ev/mutants.txt). Both are now listed under the body's `## Unpinned sites` at the line numbers they have at this head, with the equivalence reasoning the earlier verdict gave. That settles them.
- RESULT: the body's figures for this delta match what I measured at the head: 161 arms; `finder_overlap self-test: ok (with mutants)`; `KILLED F1`, `F2` and `E14` correspond to my F1, F2 and E14. Figures that the delta does not move were verified in the round-1 verdict and were not re-taken.
- RESULT: `git merge-tree --write-tree origin/main 9e535642649c96ade5a1ad960b37851130319378` exits 0 against origin/main 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, which is the PR's base (ev/merge_tree.txt). There is no conflict.
- RESULT: CI at this head: `merge_train.py classify 9e535642649c96ade5a1ad960b37851130319378 --pr 3672` was polled from 20:29 UTC and exited 4 at 20:57 UTC: `APPROVAL-OWED 9e535642649c96ade5a1ad960b37851130319378 1 budget raise(s), first .claude/workflows/policy_budgets.json: corpus_tokens: 69244 -> 71212 (a cap went up): a raise is the owner's (0013): no decisive review by tvofi (id 70032254) on this pull request`. That is APPROVAL-OWED, so the head is judged GREEN; the raise's approval follows this verdict (ev/classify.log).
- Red checks: the body answers `budget-raise-gate / budget-raise-gate`, which is in `merge_train.py owed-reds`, as red by design until an approving review. The packet digest's `tests / nightly-status` failure is not in the owed-reds set, so it is not answered here.
- seat_comms: initialised (`resumed 812c89488216`) and beating; no command arrived.
- Step 12: the PR branch still reads 9e535642649c96ade5a1ad960b37851130319378 when the verdict is returned.
