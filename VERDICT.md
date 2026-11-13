Fix review: blocked f11bdd4d483c0509ad108b0e00112aaae8f1368d comment-evidence: advisor.refit_detail is verdicted true on a code comment; the ±7-10 % lower bound exists only in accuracy.py:646-650's comment

bus-nonce: c1e04704ece088aa66287f43b445823c

## Block

- Reviewer addition (1) of this group's brief: "a row whose evidence is a comment is a block". `dev/audit/rounds/round10/user-text-card.md:176` verdicts `advisor.refit_detail` true. The text says, in en, sv and de, "about ±7-10 % uncertain". The row's evidence for that clause is "accuracy.py:651 REFIT_BAND_PERCENT=10 (comment states 7-10 %)". In code, at base 90c6bc3b0, `REFIT_BAND_PERCENT = 10` (accuracy.py:651) is published as `"band_percent": REFIT_BAND_PERCENT` (accuracy.py:776). The 7 appears only in the `#:` comment at accuracy.py:646-650, a pre-study figure. The card renders this key at card.js:10097 with `{days}` and `{pairs}` only, so it never reads `attrs.refit.band_percent`. The row's other quoted evidence, `_refit_start` "after the last boost-tagged pair plus settle, and after the last restore", is the docstring at accuracy.py:657-658. The code body at :659-663 does implement that behaviour, but the row quotes the docstring, not the code. The coordinator.py:1363 "Recommend-only" citation is also a docstring (restart_advice, :1358-1365). The row must be re-judged against code. Either the band clause is verdicted unverifiable or corrected to the published `band_percent`, or the card renders `band_percent` and a test pins it (brief addition 3). The other docstring-citing rows I sampled also cite a deciding code line: `score.part_overall` (:50, coordinator.py:3381/3392) and `health.cop_reason_unaligned_meters` (:140, heat_energy.py:567, the `unaligned if got.elec_kw is None` expression in close_span). This is the only row I found whose claim rests on a comment alone. The sample covered every row that names a comment or docstring (`grep -niE 'docstring|comment'`, 6 hits, 3 of them rows). Rows that quote a docstring without saying so were not swept.
- Surviving mutant on a pinned claim (brief addition 3). The body says the invalid-window pin checks that "the card's check reads `quietWindows`". The body's own corrected-list item says "the save and simulate checks also read `quietWindows`". The check is `/quietWindows \|\| \[\]\)\.find\(/.test(cardSrc)` (tests/card.mjs, last block), which one match satisfies. Mutant `drop-quiet-find-first` swaps `(draft.quietWindows || []).find(` for `(draft.dhwWindows || []).find(` at card.js:13217 (the first of two sites, :13217 and :13336). The suite stays at rc 0, `ALL CARD CHECKS PASSED`. With that mutant, the channel-neutral error text is false for one of the two handlers, and nothing fails. The fix is to require both sites, or to pin the behaviour by driving each handler with an invalid quiet window.

## Findings

- `tests/card.mjs`: the `check("user text: the invalid-window error ...` call in the new block is indented four spaces where its siblings use two. This is cosmetic only. Carry: dismissed: whitespace, no behaviour; the re-cut touches this block anyway

## Evidence

- Round 1 of review, a handoff review: no pull request exists yet, so there is no review packet and no CI to read. This verdict reads no check runs and answers no red. `merge_train.py owed-reds` prints the required set, but no run exists at this head.
- Head measured: f11bdd4d483c0509ad108b0e00112aaae8f1368d, which is the tip of handoff/r10-user-text-verify-card and the head the body's `## Head` names. Merge base: 90c6bc3b0756475e28d4ace8d8e31c4788474933. origin/main is e23124ff6e45bac1d48b4a775dad555a37965355.
- `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- `git merge-tree --write-tree origin/main f11bdd4d4` gives rc 0 and tree cda4d02d02dc4a8257fb41b6913ec3c431f2b13b, so there is no conflict (ev/merge-tree.txt).
- RESULT card.mjs at head: rc 0, `ALL CARD CHECKS PASSED`, after `tests/plan_view.py` wrote its payload (ev/card-head.txt).
- RESULT mutation proof, re-run: the base card with the head's tests gives rc 1, with exactly the 7 FAILs the body lists (ev/mut-basecard.txt). This reproduces the body.
- RESULT targeted mutants, 9 run and 8 killed (ev/targeted-mutants.txt):
  - Killed: `COP_TRACKING_ERROR_GATE` 0.3→0.25, sv gate 30 %→40 %, the modelled floor `<= 0.1`→`<= 0.2`, "Varmvatten" re-added to the sv window error, both `quietWindows` finds removed, the old de "Wärmespeicherung", a truncated sv grid page, and a de.json grid menu label.
  - Survived: `drop-quiet-find-first` (see Block).
- RESULT enumerator, own run: the head prints `table 644 (unreached 0)`, `literal 4`; the base prints `table 648 (unreached 3)`, `literal 4`. These match the body's Figures (ev/enum-head.txt, ev/enum-base.txt). The planted null control was not re-run.
- Not re-derived: the verdict counts true 331 / false 22 / stale 1 / unverifiable 6 / n/a 292. They come from the fixer's nine reader tables, which are not in the tree. Only the summary table and the per-row record are, so I could not re-derive the `cut -f4` count.
- Not re-derived: the browser PNG cmp results and the 11-script gate table. This is a cheap-checks-only review, and card.mjs plus card_drift were the closures I re-ran.
- RESULT VERSION, manifest and RELEASE_NOTES.md: absent from the three-dot diff. `tests/golden/claimed_drift.txt` is untouched.
- Forward-carry destination `R11-INTAKE-R10-RESIDUE` exists in `dev/programme/rosters/wave-r10-groups.json` on origin/main. I did not check whether its brief already holds the five carries. The body states no roster SHA for them, and this block returns the branch anyway.
- RESULT `GOLDEN_MODE=drift node tests/card_drift.mjs` at the head: rc 0, `card_drift: 21 state(s) moved and claimed, 24 identical` (ev/card_drift-head.txt). Every moved state is claimed, which matches the body's 21.
