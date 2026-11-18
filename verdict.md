Fix review: merge cc10065b3727a9d707d8752444ea03fe56c1e8d9

bus-nonce: 7fa9a496692775b3021c7ff51df43cf2

## Findings

- Note: body-stale: `## Red checks` carries a pasted fragment after the `pr-contract` bullet ("## Approval`. No cheaper detector exists ... - `gate`: follows the one above"), a leftover of an earlier body; the real `## Approval` section follows it and pr-contract passes. Carry: dismissed: paperwork on a body that merges as is, no later stage acts on it

## Evidence

- Round 2, scope `delta` over the reviewed head f7ef7c069865bdf254044c6c334b9b5e1b22c30e (previous verdict: merge). Policy pull request; no `custom_components/` line moves in the PR's own diff or in its delta, so nothing widens the review.
- RESULT delta: `review_carry.py f7ef7c06 cc10065b` prints `FRESH-REVIEW` (8081be96 is a hand-resolved main merge, not the automatic one). The branch-only commits are d82c5b2fd2 (drops the `nudge.md` and `harnesses/README.md` token caps, the same two rows main deleted in #3668) and three merges of main. Comparing the +/- lines of the PR's own three-dot diff at f7ef7c06 and at cc10065b gives an empty diff: the authored change is byte-identical; only context lines (main's `architect-planner.md` 85->89 lines, 1261->1325 tokens; `plan-review.md` 24->27, 304->360) moved. `git diff origin/main cc10065b -- dev/governance/config/policy_budgets.json | grep -cE 'nudge|harnesses/README'` prints 0, as the body states. `ev/delta.txt`.
- RESULT previous finding: the `**You never**` reflow note was paperwork, dismissed then; the delta does not touch `proposal-triage.md`, so it stands unchanged and owes nothing.
- RESULT head (step 7, 12): the PR's head and the body's `## Head` both name cc10065b3727a9d707d8752444ea03fe56c1e8d9; base 99a4010e47. `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty: `fix-review.md` is current. `ev/HEAD.txt`.
- RESULT merge (step 13): `git merge-tree --write-tree origin/main cc10065b` (origin/main 7c2f4c30ca) exits 0, tree 7a4ef62b8f: no conflict. `ev/merge-tree.txt`.
- RESULT mutation (step 1), carry 5's entities predicate copied into `ev/check5.py` against the real `policy_lint.mjs --budgets` at the head: head PASS; M1 `const live = r.file` FAIL; M2 key on every row FAIL (the unmoved `tests/README.md` null control); M3 key dropped from the printed row FAIL. 3 of 3 killed, tree restored (`git status` clean). `ev/mutation-carry5.txt`.
- RESULT figures (step 8, 14) re-derived at the head: `policy_lint.mjs` `TOTAL: 0 error(s) across 57 policy file(s)`; `--budgets` rows `proposal-triage.md 42/42 594/594`, `root-cause.md 81/81 990/990`, `defect-root-cause.md 151/151 1885/1885`, `dev/audit/README.md ... key tools/audit/README.md`, `tests/README.md` with no key; `grep -c " key "` prints 23; no `nudge.md`/`harnesses/README.md` key left in `files_tokens`; `rules_sync.mjs --check` ok; `tests/structure.py` STRUCTURE RATCHET PASSED. The raise (40->42 lines, 563->594 tokens) is unchanged from the reviewed head, where step 14 was judged; the merge adds no raise. `ev/figures.txt`.
- RESULT entities: `PYTHONPATH=tests/hastub python3 tests/entities.py` at the head: `ALL 2732 ENTITY CHECKS PASSED`, rc 0, carry 5's check `ok`. The indented `FAIL` lines in the log body (a3:/a4: fixtures such as `sensor.x`, `button.b`) are self-test negative controls; the closing line and exit code decide. `ev/entities-tail.txt`.
- RESULT steps 4-5: the diff touches no golden fixture, claim file, `VERSION`, manifest or `RELEASE_NOTES.md` (11 files, as at f7ef7c06).
- RESULT CI (step 11): `merge_train.py classify cc10065b --pr 3688` exits 0: `GREEN cc10065b3727a9d707d8752444ea03fe56c1e8d9 pending: none red: none`. `tests / nightly-status` (red in the packet digest) is outside the owed set and owes nothing. The body's `## Red checks` answers the branch's owed reds (`gate`, `governance / env-matrix`, `tests / briefs`, `pr-contract / pr-contract`), each with cause, process state and cheaper detector or none. `ev/classify-1.txt`, `ev/owed-reds.txt`.
- RESULT step 10: `## Forward-carry` is `none`; nothing in the delta needs one.
- RESULT step 16: no actuator path touched.
