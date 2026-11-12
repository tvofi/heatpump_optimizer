Fix review: merge 2f6188444316a9df45c714e934892140a8838855

bus-nonce: acb58ee9a5d1aac16f81776d8236ee99

## Evidence

- Round 1. This is a handoff review: no pull request exists yet, so there is no review packet and no CI run to read. Step 11 (red checks) has nothing to answer. The body's `## Red checks: none` agrees with that. `merge_train.py owed-reds` is in ev/owed-reds.txt.
- Head: I measured 2f6188444316a9df45c714e934892140a8838855. That is also the head the body's `## Head` names. The body ref handoff-body/r10-hotfix-card-health-text is recorded in ev/HEAD.txt.
- Policy currency: `git diff merge-base...origin/main -- dev/governance/roles/` touches only fixer.md. fix-review.md has not changed.
- Merge: the merge base is 61afd4f2. origin/main is now 6d16af36 (ev/main-at-review.txt). `git merge-tree --write-tree origin/main <head>` exits 0, and the LEDGER-MERGE driver resolved tests/closures.json as a set (ev/merge-tree.txt). The head is behind main but merges cleanly, so this does not block.
- VERSION, the manifest version and the RELEASE_NOTES heading are untouched (empty three-dot diff).
- Static barrier at this head: `node tests/card.mjs` prints ALL CARD CHECKS PASSED, rc 0 (ev/card-head.txt). Its new checks are ok: the pattern corpus, the extractor probe, the no-ad-list-prone-name check, and the surface+ink one-rule check.
- Mutation 1: the card file at 75839015c (`adv-*`), run with this head's tests. rc 1, and `no class or id in the card is a name generic ad-blocker hide rules target` FAILS with `1723 names read; ad-list-prone: adv-, adv-act, ... adv-value` (14 names). This matches the body (ev/card-mut-75839015c.txt).
- Mutation 2 (my own, minimal): this head's card with only `fact-text` renamed back to `adv-text`. rc 1, and the same check FAILS with `ad-list-prone: adv-text` (ev/card-mut-advtext.txt). The test fails on the old names.
- Adversarial rendered sweep, my own instrument and wider than the fixer's two rules. I ran blockerHide alone through a scratch copy of tests/card_browser.mjs on chromium. It injects every generic `##` selector that parses: 16214 unique selectors from EasyList general hide, AdGuard Base (Safari and chromium 2.5.3.83), AdGuard Annoyances 2.2.86.27 and AdGuard Social 2.1.35.10, all fetched 2026-11-12 ~00:25Z. Each selector goes in as its own `display:none!important` rule inside the shadow root. I also swept the tile outside the dialog. Counts are in ev/blocker-all-rules-count.txt.
  - At this head: 0 box-less elements on the dialog (plan=81 setup=10 savings=22 advisor=46 health=59) and 0 of 47 on the tile, in both arms (ev/blocker-all-head.txt).
  - At 61afd4f2's card: the injected arm FAILS with 49 box-less elements. Of these, 26 are `span.adv-text` and 3 are `span.adv-label`, each matched by its own rule. The other 20 are `span.adv-sub`, which lose their box through their `.adv-text` ancestor. No other selector of the 16214 matched (ev/blocker-all-base.txt).
  - The null control is ok at both ends.
  - Result: no class the card still renders matches any generic rule in these lists, by rule or by compound, as measured on the render.
- The finder's harness `r10_card_blocker_names.py` at both ends:
  - 61afd4f2: `class adv-label, class adv-text` are targeted by a rule naming each alone, in EasyList and in both AdGuard flavours.
  - HEAD: none in all four lists. The only residual hits are the compound rules `.panel.ad`, `.grid > .container > #aside-promotion` and `.contentmovie > div[class^="ad"]` on advisor-page, which the body dispositions. The rendered sweep above confirms none of them fires.
  - Output: ev/harness-base.txt, ev/harness-head.txt.
- Figures re-derived: 49 → 0 box-less, 1723 names / 14 prone, and the reach floor numbers (plan=81 ... health=59). The generic rule counts 13631 / 14005 / 14008 / 45 reproduce. The AdGuard version is now 2.5.3.83, against the body's 2.5.3.82: the list updated between the two runs, which the body anticipates. I did not re-derive the 67 runs under 4.5:1 in themeMismatch or the full P9 browser lane. I did not re-run those heavy lanes, so those figures are the fixer's.
- Claims: `node tests/card_drift.mjs 61afd4f2` prints `44 state(s) moved and claimed, 1 identical`, rc 0 (ev/card-drift-tail.txt; the full 16 MB diff log is kept out of ev). Every moved state is claimed and no claim is stale. No solver golden is touched.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED (ev/structure.txt).
- Classification: the new harness is added to tests/closures.json's inert reads, so tests/entities.py's "force FULL" refusal does not apply.
- WebKit could not be launched in this container because the Playwright webkit build is absent. The rendered sweep is chromium only.

## Findings

- Follow-up: `AD_PRONE_NAME` is a stem heuristic. It refuses `ad|ads|adv|advert|banner|sponsor|promo` bare or followed by `-`/`_`, which is narrower than the class it guards. Of 13075 single-name generic rules in EasyList general hide, 9642 name something the pattern admits. Among them are real ad names such as `.textad` and `.top-ad` (ev/deny-pattern-coverage.txt). blockerHide injects only `##.adv-text ##.adv-label`, so a future card class like `top-ad` would pass both lane barriers. Today the card matches none of 16214 live generic selectors, so this PR's fix is complete. The body names r10_card_blocker_names.py as the re-runnable live-list instrument. Carry: dismissed: the body states the barrier is a deny-stem heuristic by design and the live-list harness is the instrument for the remainder; vendoring lists is refused (licence) and a live-list gate would put the network in CI.
- Residual: the rendered proof ran in chromium only, because webkit is not installed here, and the owner's defect is in Safari. Carry: dismissed: a blocker's generic rule is plain `display:none!important` CSS whose match is engine-independent; the body's third pass reproduced the owner's state in WebKit, and whether each real Safari blocker reaches shadow roots is already with the RCA seat per the body.

## Friction

- The frugal inline-search guard refused plain `ls`/`cat`/Read of my own evidence files after five operations. Reading them took a scout dispatch. Carry: dismissed: seat tooling cost, no defect in this PR.
