The product page (`docs/index.html`) rebuilt to the design note design/R10-PRODUCT-PAGE-REDESIGN at 2f56c2e6a9a2d280a1ab741ad768dec2d8ced89f: one illustrative day drawn by a generator (`tools/site/day_chart.mjs`) and pinned by `tests/doc_claims.py`, a scroll story over it, a first-week timeline, and a control-path chooser in place of the table. The note's acceptance list is `dev/audit/harnesses/r10_product_page.mjs`. The first fixer stopped on four points where the tree contradicted the note (BLOCKED.md at c7b0b4611d88, build 3bfb1990c83c); this head applies the orchestrator's rulings on them, given under mandate 6715477401. A fix review at 1a35b70dbf2c blocked on five note requirements the harness did not test; this head answers all five.

## Head

fcc7f07e673a200cfbaf89b2a00fb28c0b18b749: the blocked head 1a35b70dbf2c9225c7a2d946be27c5620e0322f1 plus three commits (d3f9e96d7, 38cb8e3fa, fcc7f07e6) that touch `docs/index.html` and `dev/audit/harnesses/r10_product_page.mjs` only. Its merge base with origin/main is 6cc15e9b8f53b5393bb4ed7297bfc12747d6e2f6. origin/main's tip at 2026-11-12T01:12:43Z is 47788534daffab7a199a132c5f2ca118951018dc; `git merge-tree --write-tree origin/main HEAD` exits 0 against it, so main was not merged in this round. Entries marked "this round" were taken at this head; the Rulings, and the entries that name 11c5dfb170be, d5afce01d6d9, dd31ed3599c8 or 45a5053c62cd, are as the reviewer re-derived them at 1a35b70dbf2c, and this round's diff touches none of the lines they mutate.

## Answer to the blocked verdict

Verdict: `verdict.md` on probe/rev-3458-4454bc77 at d5998f40efbf8c4761184db5503ccc94dc320e7d, five design-note requirements with no check. Each now has a check in `dev/audit/harnesses/r10_product_page.mjs`; none is waived. Each row's proof is the mutation named, under Mutation proof; its null control is the unmutated run, `RESULT fails=0`.

| item | check | proof (page mutation, check goes red) |
|---|---|---|
| 1 targets at least 40 px | `floor <width> <theme>: every target outside a line of text is at least 40 px in both dimensions`, four widths, two themes, and again at two widths with the page's fonts refused | M1, M1b, M1c; and the blocked head's page itself |
| 2 no scroll-driven animation | `10 no scroll-driven animation <width>`: the progress line gone, and every other element's display and box identical | M2a, M2b |
| 3 reads in order with styles off | `floor <width> styles off` | M3, M3b |
| 4 keyboard reach and ring | `floor <width> keyboard`: the Tab walk, and the operation by key | M4a, M4b |
| 5 no relational selector | `10 no relational selector <width>`, rendered; the source-text match is deleted | M5a, M5b |

Item 1, the page gives way, not the note. The harness's rule over the blocked head's page returns the story link at 26 px, the header brand at 30, the eight section links at 37, the four footer links at 23, the coffee link at 38 and the HACS link at 22: the reviewer's instance and every other member of its class. All are raised in this diff: `min-height: 40px` on `.next` and `.brand`; the section links' block padding 7 px to 9 px; a `footer a` rule with 9 px of block padding; the coffee link's block padding 8 px to 11 px; `padding-block:11px` on the HACS link. `.next` therefore departs from the note's line 508 by that one declaration. The two 11 px values are what the floor needs when the web fonts do not arrive (M1b, M1c). Lost alternatives: widening the selector to the story link only leaves the other five under the note's floor and unmeasured; an owner waiver was not sought because the payment fits under the page's size cap.

Design choices the checks encode (`fixer.md` step 11), stated in the harness header:

- The floor exempts a link in a line of text: computed display `inline` with a text node beside it in its parent. Such a link takes its line's height (WCAG 2.5.8's inline exception); the note's floor is read as not reaching it, and that reading is this fixer's, not a ruling. The check prints the number exempted. A link alone in its paragraph is not exempt, which is why the HACS link is held to the floor.
- Items 2 and 5 are simulated in Chromium, not run in an engine lacking the feature: `withoutFeature` does to the parsed rules what such an engine does (drops a style rule whose selector names the feature, skips an `@supports` block that requires it, applies one that negates it). It follows whatever rules the page has; it names none of them.
- Item 4 counts a radio group as one tab stop and the gallery's tab list as one, and accepts as a stop a box that scrolls and holds no control (at 360 px the engine makes one code block focusable so it can be scrolled by key). The check requires the set of stops to equal the set of displayed controls, which is the reconciliation the reviewer's stop counts lacked.
- Item 3 leaves the script on, so the gallery panels the script hides are skipped; every other heading, paragraph and list item must have a box.

## Repair

- `dev/audit/harnesses/r10_product_page.mjs` found the repository root by a three-level `path.resolve(..., "..", "..", "..")`. It now inlines `repoRoot` from `tools/audit/repo_root.mjs` verbatim and calls it on its own directory, as `dev/audit/harnesses/r9_fr3_family_consumer.mjs` does. Importing the helper lost to inlining because `tests/harness_headers.py`'s `inline_scan` compares inlined copies and the corpus has no importer.
- The harness's loopback server tested a path with `existsSync` and `statSync` and then read it (alert 53). It now reads once and answers 404 when the read throws; the `DOCS` prefix test stays ahead of the read.
- `tools/site/day_chart.mjs` tested the page with `existsSync`, read it, and wrote it (alert 54). It now reads once; `ENOENT` is the `no such page` refusal and any other error is rethrown. Holding one descriptor across the read and the write lost: the alert's source is the check, and without it no check precedes a use.

## Rulings

1. **Self-test wiring: option (a).** `.github/workflows/governance.yml`'s instrument-self-tests job gains the step `day-chart` (`node tools/site/day_chart.mjs --self-test`), and `tools/ci/selftest_closures.json` gains the row `python3 -I tools/ci/selftest_scope.py record --step day-chart` measured for it. The pin in `tests/doc_claims.py` is unchanged; `tools/audit/seat/selftest_wiring.py` is unchanged; the invariants are not folded into check mode.
2. **"Control path" stays on the page.** The chooser's `legend` carries `<span class="eyebrow">Control path</span>` ahead of the question, under the chooser's own source mark, with one CSS rule putting it on its own line. Its computed font, letter spacing, case and colour equal a pane eyebrow's (read with Playwright at 900 px). Acceptance check 7 is not re-worded and passes: the only text under a source mark lost from the base is the removed picture's alternative text.
3. **Accepted as built.** The null control "a docs card for a built document linked to GitHub is refused" plants on the docs card's own `data-doc` attribute; the note's step-5 link stays.
4. **Accepted as built.** The control-path table's CSS, unreachable once its markup is gone, is deleted; the 70 kB cap stands and no cap is raised.

Smaller departures, accepted as built: a hidden `h3` per chooser pane (the fourth marked page copy), the print block, and the screenshot figure's default side margins.

## Mutation proof

Each run at d5afce01d6d9 (the head less the closures entry of 11c5dfb170be), each mutation restored by `git checkout`.

- One preset price changed in `tools/site/day_chart.mjs` (`peaks: [3.0,` to `[3.4,`): `node tools/site/day_chart.mjs --self-test --check` exits 1 with `FAIL price: the page's markup is not the generator's`, and `tests/doc_claims.py` goes red on `the page's illustrative chart is its generator's output, and the generator's self-test holds`.
- The legend's `Control path` span deleted from `docs/index.html`: the harness prints `FAIL 7 sentences: every text node under a source mark at the base is on the page at the head  [124 marked nodes at the base; missing ["Control path"]]` and `RESULT fails=1`. This is the state the first fixer blocked on.
- The new step's `run:` replaced by `true`: `python3 tools/audit/seat/selftest_wiring.py --check` prints `UNWIRED tools/site/day_chart.mjs: no workflow run line names its self-test`.
- The `day-chart` row deleted from `tools/ci/selftest_closures.json`: `python3 -I tools/ci/selftest_scope.py select --change M:README.md` prints `MODE: FULL -- every step runs (the table is stale: its steps differ from the workflow's: missing ['day-chart'], extra [])`.
- Repair, depth root: `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` at 33a4e689fc7f prints `FAIL every inlined walk matches the canonical helper and no depth root remains  [FAIL depth seams: dev/audit/harnesses/r10_product_page.mjs:31: ...` and `1 of 112 HARNESS HEADER CHECKS FAILED`; at dd31ed3599c8 it exits 0 with `ALL 112 HARNESS HEADER CHECKS PASSED`.
- Repair, server read, at 45a5053c62cd: the catch's `body = null` changed to `body = Buffer.alloc(0)`: the harness prints `FAIL server: an absent path and a directory answer 404, and the page 200  [/no-such-file.html 200; /img 200; /index.html 200]` and `RESULT fails=1`; restored by `sed`, `git diff` empty.
- Repair, generator read: no mutation kills it, because with the `try` removed `node tools/site/day_chart.mjs --check --page /nonexistent/x.html` still exits 1, on an uncaught `ENOENT` instead of the refusal line. What is shown instead is the same output at both ends: `FAIL /nonexistent/x.html: no such page`, exit 1, at 33a4e689fc7f and at the head.

This round, each a mutation of `docs/index.html` at this head with the harness at sha1 a750358a4047fa476401634860a904dc79ecadb3, the page restored from a copy afterwards. Mutants that add bytes also turn `6 size` red; that line is omitted below.

- M1, `min-height: 40px` deleted from `.next`: ten `FAIL floor ...: every target outside a line of text is at least 40 px in both dimensions`, each listing `["Scroll through one day",193,26]` (213 wide with the fonts refused); `RESULT fails=10`.
- M1b, the coffee link's padding 11 px to 9 px: `FAIL floor 360px without the page's fonts` and `FAIL floor 1440px without the page's fonts`, `["Buy me a coffee",172,37]`; the eight checks with the fonts loaded stay `ok`. `RESULT fails=2`.
- M1c, the HACS link's `padding-block` 11 px to 9 px: `FAIL floor 1440px without the page's fonts`, `["Open this repository in ",354,37]`; `RESULT fails=1`.
- M2a, the base rule `.progress { display: none }` changed to `display: block`: `FAIL 10 no scroll-driven animation 1440px: the progress line is drawn with the feature and gone without it  [display block -> block; ...]`, the same at 390 px, and the two reduced-motion progress checks.
- M2b, `body{margin:9px!important}` added inside the `@supports (animation-timeline: scroll())` block: `FAIL 10 no scroll-driven animation 1440px: nothing else changes, and no console message  [424 elements, display and layout box DIFFER; 0 console]`, the same at 390 px.
- M3, the `limits` and `ai` ids exchanged: `FAIL floor 1440px styles off` and `FAIL floor 390px styles off`, anchor tops `...,29217,38623,37995,38806`. Check 5 (each id once) stays `ok`.
- M3b, `hidden` added to the limits section: both `styles off` checks, `15 without a box, 15 out of order`.
- M4a, `tabindex="-1"` on the theme button: `FAIL floor 1440px keyboard: Tab stops at every displayed control ...  [36 controls ..., 35 stops ...; missed 1, ...]`, and at 360 px `28 controls ..., 28 stops, 1 of them a scrolling box; missed 1`.
- M4b, `:focus-visible { outline: 3px solid` changed to `0 solid`: both `keyboard` walks red, the stops listed `without a ring` starting `"Skip to content","Heat Pump Cost Optimizer"`.
- M5a, the `@supports not selector(:has(*)) { .cp .pph { display: block } }` rule deleted: `FAIL 10 no relational selector 1440px ...  [... without it 4,4,4,4 panes shown over the four radios, names ["","","",""]; ...]`, the same at 390 px.
- M5b, the `.cp .pp` rule under the same condition deleted: the same two checks, `without it 0,0,0,0 panes shown`.

Disclosed self-correction: the first cut of three of these checks let a mutant live, found by running the mutants before the handoff. M2b lived while the comparison read parent-relative offsets, M4a while the expected set was derived from `tabindex`, M3b while every `hidden` subtree was skipped; 38cb8e3fa changes each check and the lines above are from the changed checks. Two earlier spellings of M2b (`h2 { margin-top: 9px }`, `body{margin:9px}`) were vacuous because later rules of the page override them; `!important` is what makes the mutant reach the page. A footer-link padding of 11 px lived as a mutant (9 px reads 41 px with and without the fonts), so fcc7f07e6 takes it back to 9 px.

## Null control

- At the base cbd23f1c8bf6 `python3 tools/audit/seat/selftest_wiring.py --check` reports no unwired tool, and at the first fixer's build it reports the generator unwired: the step is what wires it, not a change to the checker.
- With the row in place, `python3 -I tools/ci/selftest_scope.py select --change M:README.md` is `MODE: SCOPED` and does not list `day-chart`; `--change M:tools/site/day_chart.mjs` is `MODE: SCOPED` and lists it. The row selects the step on its own file and not on an unrelated one.
- Unmutated, `node tools/site/day_chart.mjs --self-test --check` exits 0 and the harness prints `RESULT fails=0`.
- Depth root, at 45a5053c62cd with the one `const ROOT` line put back to the three-level `path.resolve` in a detached worktree (taken at dd31ed3599c8, whose `ROOT` lines are the head's): `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` exits 1, `1 of 112 HARNESS HEADER CHECKS FAILED`, with the `FAIL depth seams: dev/audit/harnesses/r10_product_page.mjs` line. The check reads the line, not the commit.
- This round: unmutated at this head the harness prints `RESULT fails=0`, run immediately before M1b, M1c and M2b. The layout comparison waits for running clock-driven animations to finish; without that wait two walks of the unchanged page differed in 36 boxes (scratch probe), which would have read as a page defect.
- With `:has()` working, the relational check's own first arm reads `1 pane, 0 names`, so the four named panes are the simulated engine's and not the page's default.
- With scroll-driven animation, the same check's first arm reads `display block`, so the missing line is the simulated engine's.

## Figures

- Harness, this round: `node dev/audit/harnesses/r10_product_page.mjs` (sha1 a750358a4047fa476401634860a904dc79ecadb3) at fcc7f07e673a prints `RESULT fails=0`, `RESULT base=6cc15e9b8f53`; `grep -c '^ok'` over its output prints 95. Before: the same harness with `git show 1a35b70dbf2c:docs/index.html` in place of the page prints `RESULT fails=10`, the eight `floor <width> <theme>` checks and the two without fonts, and nothing else red: the blocked head's page meets the four other new checks, as the reviewer's probes found.
- Target class, this round (`fixer.md` step 8): the enumerating rule is the harness's `targetFloor` (every displayed `a[href]`, `button`, `summary`, `select`, `textarea`, radio pill, bare `input` and `[tabindex]`, less links in a line of text). The check prints, at 1440 px, 38 targets held and 4 exempt; at 360, 390 and 768 px, 30 and 4. Seams it returns at the blocked head: `.next`, `.brand`, `nav.links a`, the footer's four links, `.bmc`, the HACS link; each closed in this diff. At the base 6cc15e9b8f53 the same rule, run from a scratch copy of the page without its fonts, returns the same seams less `.next`, which the redesign added.
- Documentation claims: `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` ends `ALL 316 checks PASSED` at the head (this round); at the first handoff's base cbd23f1c8bf6 it ended `ALL 315 checks PASSED`; the difference is the generator's pin.
- Page size: `wc -c < docs/index.html` prints 69989 at this head (69893 at 1a35b70dbf2c) against the note's 70 kB cap (70 000 bytes); 45301 at cbd23f1c8bf6.
- Self-test wiring: `python3 tools/audit/seat/selftest_wiring.py --check` ends `0 unwired` and `0 index gap(s)` at the head.
- Structure: `python3 tests/structure.py` ends `STRUCTURE RATCHET PASSED`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: FULL`, reason `tools/ci/selftest_closures.json changes the gate itself`; the full suite is CI's to run, not reproduced locally.
- Depth seams, the class and not the instance: `PYTHONPATH=tests/hastub:tests python3 -c "import harness_headers as h; print(len(h.depth_root_seams()), len(h._scope_paths()))"` prints `0 1219` at the head: the scan's own rule over every file of its corpus returns no seam. The null control above is the result it gives when one exists. `tools/site/day_chart.mjs` also resolves its root by depth; `_scope_paths` does not list `tools/site/`, so the check does not bind it and it is left as built.
- Generator at the head: `node tools/site/day_chart.mjs --check --self-test` prints `day_chart: self-test OK` and `day_chart: docs/index.html carries the generator's chart`, exit 0; `--write --page` on a copy of the page prints `unchanged`, exit 0.
- Temp paths: `python3 tools/audit/seat/tmp_paths.py --check` prints `0 refused`.
- CI prediction at the head: `python3 tools/pr/ci_predict.py` prints `no closures, fast, governance or instrument red predicted against 6cc15e9b8f53`. At the first handoff it predicted one red, `tests / closures INERT READS tests/harness_headers.py: dev/audit/harnesses/r10_product_page.mjs`; `--apply-inert` wrote the entry (commit 11c5dfb170be) and the predictor then reported no predicted red, with the depth root already in the harness (3bfb1990c83c).

## Red checks

- **tests / fast (3.14)**: `python3 tests/harness_headers.py` failed on this branch's own harness, the depth root above; repaired in dd31ed3599c8. A cheaper detector exists and was not on the handoff path: the scan alone (`depth_root_seams`, the command under Figures) runs in 0.4 s wall (`time`, this container) against the whole script, which outran a 120 s foreground bound here on each of its three runs, and `tools/pr/ci_predict.py`, which `fixer.md` step 18 names for a new harness, reported no predicted red at the first handoff while the seam was in the tree. Standing cost of putting the scan in the predictor: that 0.4 s per `prepr.sh` run. Whether to build it is `root-cause.md`'s seat, not this fix's.
- **CodeQL**, **code-scanning alert 53 (js/file-system-race)** and **code-scanning alert 54 (js/file-system-race)**: both in this branch's code, `dev/audit/harnesses/r10_product_page.mjs` (the server's read) and `tools/site/day_chart.mjs` (the page's write); both check-then-use pairs are removed in dd31ed3599c8. No cheaper detector exists: the query runs only in CodeQL's analysis, which no local path or predictor carries, so the gate that caught it is the cheapest one. Whether the alerts close is CodeQL's to say on this head; it was not run locally.
- **tests / nightly-status**: not this branch's. It grades `main`, and its red is nightly run 42934263129, which lost its runner. Owner: the orchestrator (`defect-root-cause.md`, Enforcement).
- **gate**, at 1a35b70dbf2c, run 43124554958: `FAIL run(s) [43124733968] at this head are still being judged; their gate decides`. It is the body-edit run deferring to the push run, not a defect of the branch; no cheaper detector exists because nothing in the tree is wrong for one to find.

## Forward-carry

none

## Friction

none
