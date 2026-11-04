Fix review: merge f5f56576b13dbcd8687dfabdbfbef587dcfaf3b9

bus-nonce: 8aabce21730eb49c0e7d53777007cb55

## Round

Round 1. I measured the live head f5f56576b13dbcd8687dfabdbfbef587dcfaf3b9. The merge base is b8e823699981866383f1afa54ce708ded3419316. I worked from detached worktrees at the head and at the merge base. The roles diff between the merge base and origin/main is empty, so the contract is current.

## Findings

- Residual: one mutant in the census survives the tests. In `_rule_key`, I changed `content = content or len(joint) > 2` to `content = content`. With it, `card_rule_spellings` and `card_template_spellings` stay green, the real card still reads 70, and my own harness case still reads 2. A joint's text only matters as content for a template that has no member, index, string or KEEP word of its own, such as `${a}-${a}`. The card holds no such rule today, so no figure in this PR depends on the line. Carry: dismissed: it moves no measured figure on the card, and a null-content template rule is out of #2259's scope; a later C24 change that relies on joint content owes the pin.

## Evidence

- CI: `merge_train.py classify f5f56576b13dbcd8687dfabdbfbef587dcfaf3b9 --pr 3179` printed `GREEN f5f56576b13dbcd8687dfabdbfbef587dcfaf3b9 pending: none red: none` (ev/classify.txt). I read all 55 check runs on one page of 100: every one is success or skipped, with no concluded red. The body's `## Red checks` (none) is therefore accurate, and no root-cause answer is owed.
- RESULT M1 (template arm off, `enumerate(_templates(body)[:0])`): red, `FAIL card_rule_copies: a template rule respelled inline at a second site reads both sites [0 -> 0]`. My own two-site case read 2 -> 0.
- RESULT M2 (markup criterion off, `if True:`): red, `FAIL card_rule_copies null: markup drawn again reads nothing [0 -> 2]`. The real card read 70 -> 85.
- RESULT M3, my own (`roots=True` -> `roots=False` in `rule_copies`): red, same FAIL as M1. The tree was clean after every mutant (`git status --porcelain` empty).
- Failing test first: at 9ac93f83e the test fails `[0 -> 0]`. 9ac93f83e precedes the census commit 41450b407 in the history.
- Null controls: on my own harness (ev/h.py, my instrument rather than the finder's, because no committed finder harness exists for this group), an unrelated template read 0 and markup drawn twice read 0. The PR's three nulls are green at the head.
- Generic criterion: the only exclusion in `metrics/card.py` is `_MARKUP = <[A-Za-z/!]` applied to a template's own text segments. No literal or file name is special-cased.
- Differential (ev/diff.mjs, ev/differential.txt, my own case set rather than the body's 229): base card against head card over `formatWindows`, `quietOverlapProblem` (216 spec triples, 62 clash messages), `steppedLine` and `smoothLine` at 1, 2, 3, 4, 7 and 20 points, and `Legend.storageKey`. Result: `233 cases, 0 differ`, 0 errors. The perturbed control (`pathPoint` x to 3 decimals) read `233 cases, 12 differ`.
- eslint no-undef (ev/eslint.txt): 69 messages on the base card, 69 on the head card. A planted `edgeKeyX` was reported (70), so the check can see one. This matches the body's 69.
- Archscore: `score.py --diff b8e82369 HEAD` printed `Architecture score: dS +0.0000 NULL` and `card_rule_copies 93 -> 70 (gate only)` (ev/archscore.txt).
- Census at the head: `card.measure` printed `0 103 70`, and on the base card with the head's instrument `0 103 93`. With the merge base's instrument, the base card read 72 and the head card read 70. All match the body.
- Class (ev/classes.txt): `rule_copies` on the base card returns 30 classes and 93 sites. Of these, 7 are template classes with 21 sites, sized [5, 3, 4, 3, 2, 2, 2]. At the head it returns 22 classes and 70 sites, none of them template classes. This matches the body: every seam is closed and none is open.
- Metric earned: restoring the base card under the head's instrument reads 93, above the cap of 72. The fall to 70 comes from the card dedupes, not from the instrument. The 72 -> 70 on the old instrument comes from `dropText`, a chain copy removed. The gate weights C24 at 0, so no dS credit is moved.
- Ratchet: `tests/structure.py` printed `STRUCTURE RATCHET PASSED`. `archscore.card_rule_copies` in tests/ci_budgets.json is 72, and the three-dot diff touches no `*_budgets.json`.
- Standing: the claim files, VERSION, the manifest and RELEASE_NOTES.md are byte-identical across the three-dot diff (empty `--stat`). The host-path scan of added lines is empty. `git merge-tree --write-tree origin/main f5f56576b13dbcd8687dfabdbfbef587dcfaf3b9` exits 0 against origin/main c3a279e3, which has moved past the merge base. The delivery row `dev/programme/delivery/3179.md` is in the three-dot diff. The body says `Closes #2259`, and its `## Head` names f5f56576b13dbcd8687dfabdbfbef587dcfaf3b9. The scoped gate printed `MODE: SCOPED -- 10 script(s) run, 23 scoped out.` (ev/scope.txt).
- Not re-derived: the body's rt_47 figures on the pinned tree 7952d8f9 (53 -> 53 under M1, 77 -> 78 restored) and its count of 229 differential cases. I used my own case set instead.
