Fix review: blocked 1a35b70dbf2c9225c7a2d946be27c5620e0322f1 harness: design-trace-missing targets-40px (a.next is 26 px), no-scroll-driven-animation row, styles-off reading order, keyboard reach and ring beyond chooser and gallery, no-relational-selector row read as text only

bus-nonce: 4454bc77d121225a9c08700d922d54aa

Round: first fresh review at this head (review_carry answered FRESH-REVIEW; the verdict at 11c5dfb1 is not carried). Measured in a detached worktree at 1a35b70dbf2c9225c7a2d946be27c5620e0322f1, base 6cc15e9b8f53b5393bb4ed7297bfc12747d6e2f6; the head on origin was still that SHA when this was written.

## Block

fix-review.md step 9: design note design/R10-PRODUCT-PAGE-REDESIGN at 2f56c2e6a9a2, section 10, names requirements that `dev/audit/harnesses/r10_product_page.mjs` and `tests/doc_claims.py` do not test, and the body records no waiver by tvofi for any of them (the Rulings cover four other points). All five, not one per round:

1. "targets are at least 40 px". The harness's floor check measures `a.btn, button, .cp .opts label, a.iconbtn` only, and is named for that subset. Measured by me at the head (ev/reviewer_targets_both_ends.txt): the link this redesign adds, `a.next` "Scroll through one day", is 26 px tall at 360, 390, 768 and 1440 px, and it is absent at the base. Its CSS is the note's own text (note line 508), so the note's rule and the note's floor disagree: this needs either a `min-height` on `.next` (the page has 107 bytes left under the 70 000 cap) and the selector widened, or tvofi's waiver in the body. Same measure, unchanged from the base and also outside the selector: header section links 37 px at 1440 px, `a.brand` 30 px, `a.bmc` 38 px.
2. Fallback row "no scroll-driven animation: no progress line; nothing else changes". No check runs it; the no-script check excludes scroll timelines by construction (`a.timeline instanceof DocumentTimeline`). My probe, with the page's one `@supports (animation-timeline: scroll())` condition made false: `.progress` display none, 0 console messages (ev/reviewer_probe.txt). The page holds the row; the harness does not test it.
3. "the page reads in order with styles off". No check. My probe with every style element and style attribute removed: the 40 headings lie top to bottom in document order and the ten anchors in page order. Holds by my instrument; untested by the harness.
4. "every control is reachable and operable by keyboard with a visible ring". The harness presses ArrowRight in the chooser and the gallery keys; no Tab traversal, the theme button is only clicked, and the ring is read on the chooser pill alone. My probe: Tab reaches 34 stops at 1440 px and 27 at 360 px, each with an outline or shadow drawn. I did not reconcile those counts with the 42 focusable elements in the DOM (radio group, roving tabs and width-hidden links would account for it; not derived).
5. Fallback row "no relational selector: all four control-path answers shown, named". The harness matches the two `@supports not selector(:has(*))` rules as source text and says so in its header; nothing renders the state. Not waived.

Items 2 to 5 are closed by a check each (or a waiver); item 1 also needs the page or the note to give way.

## Evidence

- Harness at the head: `node dev/audit/harnesses/r10_product_page.mjs` (sha1 47d8241f76bf7df4c0434e7204994025861a66f0): 82 `ok`, `RESULT fails=0`, `RESULT base=6cc15e9b8f53` (ev/harness_head.txt). The harness is the builder's, written to the judge's note; no finder's harness exists for this feature.
- Mutation, preset price `[3.0,` to `[3.4,`: `node tools/site/day_chart.mjs --self-test --check` rc 1 `FAIL price: the page's markup is not the generator's`; `tests/doc_claims.py` `1 of 316 checks FAILED` on the generator pin; restored, `ALL 316 checks PASSED` (ev/mutations_1_3_4.txt).
- Mutation, legend's `Control path` span deleted: `FAIL 7 sentences ... missing ["Control path"]`, `RESULT fails=1` (ev/mutations_2_server.txt).
- Mutation, the step's run line to `true`: `UNWIRED tools/site/day_chart.mjs`, `130 wired, 1 unwired`; restored `131 wired, 0 unwired`.
- Mutation, `day-chart` row deleted: `MODE: FULL -- every step runs (the table is stale ... missing ['day-chart'] ...)`; restored: `M:README.md` SCOPED 18 steps without `day-chart`, `M:tools/site/day_chart.mjs` SCOPED 20 steps with it.
- Mutation, server catch `body = null` to `Buffer.alloc(0)`: `FAIL server: ... [/no-such-file.html 200; /img 200; /index.html 200]`, `RESULT fails=1`.
- Acceptance 1: product-page claims 49 at the base, 53 at the head; `ALL 315 checks PASSED` at 6cc15e9b8f53, `ALL 316` at the head (ev/base_claims.txt, ev/figures.txt). The body quotes 315 at cbd23f1c8bf6; I took it at the merge base.
- Design text: 329 of the note's 343 code-block lines are in the page or the generator verbatim after whitespace normalisation; the 14 others are the nine marker lines (filled by the generator), the legend (Ruling 2) and four pane lines (the hidden per-pane heading the body discloses) (ev/design_trace.txt).
- Figures re-derived at the head: page 69893 bytes; `0 1219` depth seams; `STRUCTURE RATCHET PASSED`; `tmp_paths: 0 refused`; generator `self-test OK`, `--check --page /nonexistent/x.html` rc 1 `no such page`, `--write --page` on a copy `unchanged`; `closure.py select` `MODE: FULL`, reason as the body gives.
- Not re-derived: the mutation and null-control entries the body took at 33a4e689fc7f and dd31ed3599c8 for the depth root; `ci_predict.py`; the two `tests/closures.json` entries (CI's `tests / closures`, pending).
- Step 4: `tests/env_drift.py` did not run in this container (its baseline `git worktree add` exits 129). `git diff 6cc15e9b8f53 HEAD -- tests/golden custom_components VERSION RELEASE_NOTES.md` is empty, so no fixture, claim file, production line or version is touched.
- Merge: `git merge-tree --write-tree origin/main 1a35b70dbf2c9225c7a2d946be27c5620e0322f1` exits 0 against main at 6d16af36c26a (`LEDGER-MERGE: resolved tests/closures.json`). The head is a merge of 33a4e689fc7f and 45a5053c62cd; the body's "no merge was made" refers to main.
- CI at the head when written: `merge_train.py classify` printed `WAIT 1a35b70dbf2c9225c7a2d946be27c5620e0322f1 pending: gate red: none` on each of 7 polls to 00:24 UTC. This block does not turn on CI. Step 11 (the body's Red checks answers for `tests / fast (3.14)` and CodeQL) is unverdicted: the head's workflows had not concluded.
- Reviewer's instruments, out of tree and mine, not the finder's: ev/reviewer_probe.cjs, ev/reviewer_targets_both_ends.cjs (Chromium only).

## Findings

none
