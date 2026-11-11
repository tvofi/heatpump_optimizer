Fix review: merge 11c5dfb170be54d0bbb8166b5a961c3e80b40434

bus-nonce: dde2c50168b040472abe8cfb02bce29b

## Scope

Review round 1 of the continuation handoff `handoff/r10-product-page-redesign` at 11c5dfb170be54d0bbb8166b5a961c3e80b40434, cut from cbd23f1c8bf6185c3a6c10f6e4aaf562417e75bf, against design note design.md at 2f56c2e6a9a2d280a1ab741ad768dec2d8ced89f. Body: BODY.md at handoff-body/r10-product-page-redesign 6d1d06560ce336b5e62df6903aefff988a7eb011. Run from detached worktrees at the head and at the base.

## Rulings

- Ruling 1 (self-test wired in governance.yml with its selftest_closures.json row): accepted. The step is in the workflow at governance.yml:492-498. The row re-derives byte for byte (`selftest_scope.py record --step day-chart` leaves no diff). `selftest_wiring.py --check` gives 130/130 wired at the base and 131/131 at the head. The step runs `--self-test` only, and the page comparison (`--check`) is pinned in tests/doc_claims.py, as the ruling states.
- Ruling 2 ("Control path" kept as the chooser's visible label): accepted. At 900 px the legend eyebrow's computed font family, weight, size, letter spacing, case and colour equal a pane eyebrow's (ev/chooser-eyebrow.txt).
- Ruling 3 (the docs-card null control keyed on `data-doc`): accepted. The replacement is guarded by `card != page`, so a planting that matches nothing is red, not vacuous. All 316 checks pass.
- Ruling 4 (the dead table CSS deleted, no cap raised): accepted. The page is 69893 bytes against the 70000-byte cap, `tests/structure.py` prints STRUCTURE RATCHET PASSED, and the diff touches no `*_budgets.json`.
- Smaller departures (a hidden h3 per chooser pane, the print block, the screenshot figure's side margins): accepted. None of them changes a link, an anchor or a marked sentence (checks 4, 5 and 7 below).

## Evidence

- RESULT head: the fetched head equals the body's head and the remote ref at the time of verdict (ev/HEAD.txt, ev/head-recheck.txt). The worktree was clean after every mutation was restored.
- RESULT merge: `git merge-tree --write-tree origin/main 11c5dfb1` exits 0 with tree 058fb4b990bb (ev/merge-tree.txt). origin/main is the cut base cbd23f1c8bf6.
- RESULT version: VERSION, the manifest, RELEASE_NOTES.md and tests/golden are untouched three-dot (ev/version-untouched.txt). No claim file moved, so the env_drift step has nothing to compare.
- RESULT CI: no pull request exists yet, so there is no review packet, no CI run and no check to read. `merge_train.py owed-reds` was printed (ev/owed-reds.txt), and no red exists to answer. The body's `## Red checks: none` cannot yet be verified against live checks. The train re-proves this on the PR.
- RESULT harness: the harness under dev/audit/harnesses/r10_product_page.mjs (sha1 c4ea664dd4d7e1c1cb98f97cc3fa20cd4732b26a) was built by the fixer to the note's section 10 list, so it is the builder's instrument, not the finder's. Re-run at the head it prints `RESULT fails=0` and `RESULT base=cbd23f1c8bf6` (ev/harness-head.txt). Independent reviewer instruments for checks 4-9 and 11 are listed below and agree with it.
- RESULT 1: doc_claims prints ALL 315 checks PASSED at the base and ALL 316 at the head. The added check is the generator pin.
- RESULT 2/3: generator `--self-test --check` exits 0 at the head (ev/gen-head.txt).
- RESULT 4: the href set is identical at the base and the head, 13 lines (ev/acceptance-4-5-6.txt).
- RESULT 5: each of the ten anchors appears exactly once.
- RESULT 6: no `data:` in the page; 69893 bytes against the 45301-byte base. That leaves 107 bytes under the cap, a constraint on the next edit to this page rather than a defect.
- RESULT 7 (reviewer's own instrument, ev/sentences2.py): this rule takes each text node whose nearest mark is `data-src`, and checks it against the head's whitespace-normalised text. Nothing marked at the base is missing at the head except the old inline script body, which the parser reads under a mark and which states no sentence. The only marked alt text not on the head is the removed how-it-works picture's ("One optimization interval: ..."). That matches check 7 and the harness's single exempted line. A stricter per-node rule (ev/sentences.py) also reports two headings, "Act, then learn" and "Immediately". Both carry `data-copy` inside a source-marked div, so they are page copy, not claims. It also reports two `<br>`-split fragments, which are on the head joined as one sentence. The harness's "124 marked nodes" was not re-derived: my rule counts 148, under a definition I built myself.
- RESULT 8 (reviewer's own Playwright, ev/browser-own.txt): at 360, 390, 768 and 1440 px, light and dark, scrollWidth equals innerWidth, there are 0 console messages, and every request goes to the serving host only (page, fonts, images). Screenshots of desktop and narrow, light and dark, are in ev/shots/: hero, story and chooser render without overlap or clipping.
- RESULT 9 (reviewer's own, ev/story-own.txt): at 1440 px, scrolling step n to mid-viewport gives `.viz` the classes s1..sn for n = 1..5 and back down to 1.
- RESULT 10/11: covered by the builder's harness only (no-script, reduced motion, no IntersectionObserver, chooser panes all `ok`). These were not rebuilt independently.
- RESULT mutation proof (ev/mutations.txt), all four body mutants re-run at the head:
  - Price 3.0 to 3.4: check mode exit 1 with `FAIL price: the page's markup is not the generator's`; doc_claims `1 of 316 checks FAILED`, on the chart pin.
  - Legend span deleted: harness `FAIL 7 sentences ... missing ["Control path"]` and `RESULT fails=1`.
  - Step `run:` replaced by `true`: `UNWIRED tools/site/day_chart.mjs`.
  - Row deleted: `MODE: FULL -- ... missing ['day-chart']`.
  - Each was restored to exit 0.
  - The first M4 header in that file records an unmutated run left by a failed planting script; the retry below it is the mutation.
- RESULT null controls: with the row in place, `select --change M:README.md` is SCOPED and does not list day-chart, and `--change M:tools/site/day_chart.mjs` is SCOPED and lists it (ev/selftest-scope.txt). The unmutated generator and harness are green.
- RESULT reviewer mutants on the toy planner, `--self-test` only (the CI step):
  - L86 with one hot-water run: 4 FAIL.
  - L84 picking the dearer span pair: 3 FAIL.
  - L61 with `continue` removed: survives; see Findings.
- RESULT class: the note's enumeration rule (§12, `git grep -n 'index.html' -- tools/site tests .github`) returns pages.yml, tests/closure.py, tests/closures.json, tests/doc_claims.py and tests/entities.py (ev/sibling-sites.txt). The note dispositions all of these as needing no change. doc_claims, structure and the harness are green with tests/closure.py unchanged.
- RESULT figures: these body figures were re-derived equal: 316/315, 69893/45301, 0 unwired / 0 index gaps, STRUCTURE RATCHET PASSED, harness fails=0, and every mutation message. Not re-derived: the `closure.py select` MODE: FULL line and the `ci_predict.py` prediction. The full suite is CI's to run.
- RESULT forward-carry: the body states none, and no finding of this review changes a later stage.

## Findings

- Residual: a reviewer mutant at tools/site/day_chart.mjs:61 survives both `--self-test` and `--check`. It removes the `continue` that stops a hot-water hour from also taking the idle or space-heating branch. The mutation changes the DP's internal costs but not the plan on the drawn day or under the flat-price control. Everything the page shows is pinned byte for byte (L197-199 and check mode), so any effect that reached the page would fail. Carry: dismissed: equivalent on every output the page carries; the generator is illustrative and its drawn hours are pinned exactly.
