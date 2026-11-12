Fix review: merge 438d15f1926d713925c2b00f2fcbd0dcf20b5a72

bus-nonce: 5ea8e7e43563c45bd34007ba1302a299
pending-ci: gate

Round: third review of this PR, a delta review over the reviewed head 1a35b70dbf2c9225c7a2d946be27c5620e0322f1 (verdict on probe/rev-3458-4454bc77 at d5998f40efbf8c4761184db5503ccc94dc320e7d). Measured in a detached worktree at 438d15f1926d713925c2b00f2fcbd0dcf20b5a72, base 6cc15e9b8f53b5393bb4ed7297bfc12747d6e2f6; `git ls-remote` gave that SHA for the branch and for refs/pull/3458/head when this was written. Scope: `git diff 1a35b70dbf2c 438d15f1926d` is `docs/index.html` (11 lines) and `dev/audit/harnesses/r10_product_page.mjs`; no `custom_components/` line, so the scope is not widened.

## Previous findings

All five of the blocked verdict's items are answered by a check in the harness, and each check goes red under a page mutation I ran myself. None is open.

1. Targets at least 40 px: closed. The page gave way: `.next` and `.brand` take `min-height: 40px`, the section links, the footer links, the coffee link and the HACS link take block padding. The floor check now reads every displayed link, button, summary, radio pill and tab stop in both dimensions at four widths, two themes, and at two widths with the fonts refused. Proof: M1, M1b, M1c, and my R1, R2, R3 below.
2. No scroll-driven animation: closed. The row is run by simulation on the parsed rules. Proof: M2a, M2b, and my R4.
3. Reads in order with styles off: closed. Proof: M3, M3b.
4. Keyboard reach, operation and ring: closed. The Tab walk's stop set must equal the displayed-control set, which reconciles the stop counts my last verdict left underived. Proof: M4a, M4b, and my R5, R6.
5. No relational selector: closed. Rendered, and the source-text match is deleted. Proof: M5a, M5b, and my R7.

## Evidence

- Harness at the head: `node dev/audit/harnesses/r10_product_page.mjs` (sha1 a750358a4047fa476401634860a904dc79ecadb3) prints 95 `ok`, `RESULT fails=0`, `RESULT base=6cc15e9b8f53` (ev/harness_head.txt). The harness is the builder's, written to the judge's note; no finder's harness exists for this feature.
- The same harness over the reviewed head's page (`git show 1a35b70dbf2c:docs/index.html`): `RESULT fails=10`, the eight `floor <width> <theme>` checks and the two without fonts, nothing else red (ev/harness_new_on_reviewed_page.txt). The body's figure holds.
- Null control: my driver with no mutation prints `RESULT fails=0` (ev/mut_NULL.txt).
- The body's eleven mutants, re-run by me at the head, one worktree each (ev/reviewer_mutants.py, ev/reviewer_mutant_driver.sh, ev/mut_<name>.txt). All killed, with the check and detail the body quotes:
  - M1 `fails=10`, every floor check lists `["Scroll through one day",193,26]`.
  - M1b `fails=2`, the two fonts-refused checks, `["Buy me a coffee",172,37]`.
  - M1c `fails=1`, `floor 1440px without the page's fonts`, `["Open this repository in ",354,37]`.
  - M2a `fails=4`, both `no scroll-driven animation` first arms `display block -> block`, and both reduced-motion checks.
  - M2b both `nothing else changes` arms, `display and layout box DIFFER`.
  - M3 `fails=2`, both `styles off`, anchor tops `...,29217,38623,37995,38806`.
  - M3b both `styles off`, `15 without a box, 15 out of order`; it also turns the two `no script ... every section is visible` checks red, which the body does not mention.
  - M4a both keyboard walks, `36 controls ... 35 stops ... missed 1` and `28 controls ... 28 stops, 1 of them a scrolling box; missed 1`.
  - M4b `fails=2`, both walks, the ringless list opening `"Skip to content","Heat Pump Cost Optimizer"`.
  - M5a `fails=2`, `4,4,4,4 panes shown`, names `["","","",""]`.
  - M5b `fails=2`, `0,0,0,0 panes shown`.
- Seven mutants of my own, each a member of the class the body's mutants do not plant. All killed:
  - R1, section links' padding back to 7 px: the three 1440 px floor checks, eight links at 37 px.
  - R2, `min-height` off `.brand`: `fails=10`, `["Heat Pump Cost Optimizer",245,30]`.
  - R3, the `footer a` rule deleted: `fails=10`, four footer links at 23 px.
  - R4, a scroll timeline declared on `.hero-art` outside the `@supports` block: both `nothing else changes` arms red.
  - R5, `.bmc:focus-visible { outline: none }`: both walks, `without a ring ["Buy me a coffee"]`, so one ringless control among 36 is seen.
  - R6, `tabindex="-1"` on the story link: both walks `missed 1`.
  - R7, pane 3 forced hidden: both `no relational selector` checks, `3,3,3,3 panes shown`, the third name empty.
- Step 6, the floor at configurations the harness does not walk. My own probe (ev/reviewer_targets_delta.cjs, mine and out of tree, Chromium only) at 320, 360, 390, 480, 600, 768, 900, 939, 940, 1024 and 1440 px, in the default state, each of the four chooser states and each gallery tab: 99 states, and no interactive element outside a line of text is under 40 px in either dimension at the head (ev/reviewer_targets_delta_head.txt). At the reviewed head the same probe returns one or more in all 99 (ev/reviewer_targets_delta_reviewed.txt): the story link 193x26, four footer links at 23, the coffee link at 38, the brand at 30, the HACS link at 22, eight section links at 37. The enumeration matches the body's list of seams; each is in the diff.
- Overlap, the risk the added padding carries: the probe's overlapping-pair list is the same at both heads (the sticky header over a scrolled link, and a section link clipped by its scrolling list). The padding adds no overlapping pair.
- The four links the floor exempts are named by my probe: `how it works`, `the dashboard card documentation` link, `setting up the integration`, `README`, each computed `inline` with sentence text beside it, 24 or 25 px tall.
- Figures re-derived at the head: page 69989 bytes (11 under the cap); `ALL 316 checks PASSED` from `tests/doc_claims.py`; floor counts 38 held and 4 exempt at 1440 px, 30 and 4 at the other three widths; keyboard 36 controls and 36 stops at 1440 px, 28 controls and 29 stops with one scrolling box at 360 px.
- Not re-derived: the body's base-page target enumeration with fonts refused; `ci_predict.py`; the figures for `structure.py`, `selftest_wiring.py`, `tmp_paths.py`, the depth-seam scan and the generator, which this round's two-file delta does not reach and which I took at 1a35b70dbf2c.
- Step 4 and 5: `git diff 1a35b70dbf2c 438d15f1926d -- VERSION RELEASE_NOTES.md custom_components tests/golden` is empty.
- Step 7: the body's `## Head` names 438d15f1926d713925c2b00f2fcbd0dcf20b5a72.
- Step 13: `git merge-tree --write-tree origin/main 438d15f1926d713925c2b00f2fcbd0dcf20b5a72` exits 0 against main at 2cfa3d7d6906 (`LEDGER-MERGE: resolved tests/closures.json`).
- Step 14: the one number the delta moves is the page size, 69893 to 69989 bytes, which is the added declarations. The cap is not raised.
- Step 15: `.next` departs from the note's line 508 by `min-height: 40px`, disclosed in the body, and made so the note's own floor holds. No other departure in the added lines.
- CI: `merge_train.py classify 438d15f1926d713925c2b00f2fcbd0dcf20b5a72 --pr 3458` printed `WAIT 438d15f1926d713925c2b00f2fcbd0dcf20b5a72 pending: gate red: none`, rc 3, on each of 28 polls from 01:47:33 to 02:17:45 UTC (ev/classify_polls.txt). The review was complete, so I stopped waiting and return this with its `pending-ci:` line. The check digest at render showed `gate` concluded failure and `tests / nightly-status` failure while classify read WAIT; classify decides.
- Step 11: the body answers `tests / fast (3.14)`, CodeQL with alerts 53 and 54, `tests / nightly-status` and `gate`. I did not verdict those answers: the head's workflows had not concluded. `tests / nightly-status` is outside `merge_train.py owed-reds`' set.
- carry_audit: `carry_audit.py check` over this verdict, rc 0. I gave it a body holding only the PR's `## Forward-carry` and `## Friction` sections (both `none`), not the full body; the packet's own run over the full body reads `0 finding item(s)`.

## Findings

- The floor check exempts a link in a line of text, and that reading of the note's "targets are at least 40 px" is the fixer's, not tvofi's ruling; the body says so. Four links are exempt and measure 24 or 25 px tall. I did not block on it: the note states the floor among its accessibility floors, the exemption is WCAG 2.5.8's own, and my last verdict's item 1 named standalone targets only. tvofi may read the note more strictly. Carry: dismissed: inline prose links take their line height under the WCAG 2.5.8 inline exception, disclosed in the body, owner may overrule
