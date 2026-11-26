Fix review: blocked dbaca057a07250e002538b3176477c5046732746 mutation-vacuous: ledger_unread window upper bound survives (check_scopes.py:1432 `< b` dropped)

bus-nonce: 06f2f8ee05132b207d5925e6fd979e94

Round: 3. This is a delta review over the last verdict's head e60d25b9bdf1533647cace5cb190901109d8829c (review/3898 round 2, `blocked ... mutation-vacuous: ledger_unread window filter survives`). The packet reads `full` only because verdict/3898 names e60d25b9 and not this head. `review_carry.py e60d25b9 dbaca057` prints FRESH-REVIEW. Comparing the PR's own three-dot diff at the two heads, it moved only by the 5-line self-test arm ab3ac69097 and a `tests/closures.json` hunk offset (`ev/own_diff_delta.txt`). The two merges, c892a81941 (origin/main d9100de7) and dbaca057a0, have empty combined diffs, so there is no hand resolution. The delta writes no `custom_components/` line, so nothing widens the scope.

## Block

- mutation-vacuous: the round-2 survivor is only half killed.
  - The new arm "a seat class whose only row predates the window prints unread" turns False under the round-2 mutant, the whole filter dropped (`win = [r for r in rows if r.get("t")]`). It also turns False under the lower bound alone dropped (`... and at(r["t"]) < b`). The self-test fails both times (`ev/mutants.txt`).
  - The upper bound still survives. With `tools/audit/check_scopes.py:1432` changed to `win = [r for r in rows if r.get("t") and a <= at(r["t"])]`, `check_scopes.py --repo . --self-test` prints `SELF-TEST passed` and exits 0 (`ev/mutants.txt`, last block).
  - Why it matters: grading reads round N-1's window after that window has closed. The ledger is cumulative and `collect` runs daily, so it always holds rows from after the window, such as round N's own cloud seats. That makes this the more likely silent pass of the two.
  - With the upper bound gone, a graded window with no cloud row reads no `LEDGER unread` as soon as any later cloud row exists. The same change makes later unkeyed rows count toward the window's unkeyed total.
  - Owed: an arm where a seat class's only row falls at or after the window's end (b), for example a cloud row dated after the next tag. It must print `seat classes with no row in the window: cloud`.
  - Round 2 asked for the pre-window example. The bound it pinned is the one that example reaches. The predicate has two bounds, and each needs its own arm.

## Findings

none

## Evidence

- RESULT: head reviewed dbaca057a07250e002538b3176477c5046732746 (`ev/HEAD.txt`), in a detached worktree at that SHA. The worktree was restored after each mutant and `git status` is clean.
- RESULT: `git diff <mb>...origin/main -- dev/governance/roles/` is empty (mb d9100de781), so the contract is current.
- RESULT: `git merge-tree --write-tree origin/main dbaca057...` exits 0 with tree 8a6121f57e (`ev/merge_tree.txt`). The head is 0 commits behind origin/main d9100de781.
- RESULT: VERSION, the manifest, RELEASE_NOTES.md and tests/golden are untouched (empty diff stat over those paths).
- RESULT: mutants at the head (`ev/mutants.txt`):
  - Unmutated: `SELF-TEST passed`.
  - D5, the whole filter dropped: killed, rc=1 (the new arm turns False).
  - D5a, the lower bound dropped: killed, rc=1 (the new arm turns False).
  - D5b, the upper bound dropped: survives, rc=0.
- RESULT: self-tests at the head (`ev/selftests.txt`): token_ledger 18 passed, 0 failed; cloud_dispatch 188 checks, 0 failed. They are unchanged from round 2, since the delta does not touch either file.
- RESULT: round-1 and round-2 resolutions are unaffected. The delta adds one test arm to check_scopes.py and no production or instrument logic.
- CI: `merge_train.py classify dbaca057... --pr 3898` read WAIT, `pending: gate red: none` (`ev/classify.txt`).
  - The digest's `gate` failure is the provisional gate. `gate` is in the owed-reds set (`ev/owed_reds.txt`), but classify reads no gate red, so no `## Red checks` answer is owed at this head.
  - `tests / nightly-status` is red and is not in the owed-reds set.
  - I did not wait for GREEN, because the verdict blocks on tests.
- No finder's harness is named: this is instrument-building, not an audit finding (unchanged from rounds 1 and 2).
