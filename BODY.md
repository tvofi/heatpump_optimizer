The product page (`docs/index.html`) rebuilt to the design note design/R10-PRODUCT-PAGE-REDESIGN at 2f56c2e6a9a2d280a1ab741ad768dec2d8ced89f: one illustrative day drawn by a generator (`tools/site/day_chart.mjs`) and pinned by `tests/doc_claims.py`, a scroll story over it, a first-week timeline, and a control-path chooser in place of the table. The note's acceptance list is `dev/audit/harnesses/r10_product_page.mjs`. The first fixer stopped on four points where the tree contradicted the note (BLOCKED.md at c7b0b4611d88, build 3bfb1990c83c); this head applies the orchestrator's rulings on them, given under mandate 6715477401.

## Head

11c5dfb170be54d0bbb8166b5a961c3e80b40434, cut from origin/main cbd23f1c8bf6185c3a6c10f6e4aaf562417e75bf (origin/main's tip at 2026-11-11T10:01:20Z; no merge was needed).

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

## Null control

- At the base cbd23f1c8bf6 `python3 tools/audit/seat/selftest_wiring.py --check` reports no unwired tool, and at the first fixer's build it reports the generator unwired: the step is what wires it, not a change to the checker.
- With the row in place, `python3 -I tools/ci/selftest_scope.py select --change M:README.md` is `MODE: SCOPED` and does not list `day-chart`; `--change M:tools/site/day_chart.mjs` is `MODE: SCOPED` and lists it. The row selects the step on its own file and not on an unrelated one.
- Unmutated, `node tools/site/day_chart.mjs --self-test --check` exits 0 and the harness prints `RESULT fails=0`.

## Figures

- Harness at the head: `node dev/audit/harnesses/r10_product_page.mjs` (sha1 c4ea664dd4d7e1c1cb98f97cc3fa20cd4732b26a) prints `RESULT fails=0`, `RESULT base=cbd23f1c8bf6`. Before, at the first fixer's build 3bfb1990c83c, the same harness printed one FAIL (check 7), which the second mutation above reproduces.
- Documentation claims: `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` ends `ALL 316 checks PASSED` at the head and `ALL 315 checks PASSED` at the base; the difference is the generator's pin.
- Page size: `wc -c < docs/index.html` prints 69893 at the head against the note's 70 kB cap (70 000 bytes), and 45301 at the base.
- Self-test wiring: `python3 tools/audit/seat/selftest_wiring.py --check` ends `0 unwired` and `0 index gap(s)` at the head.
- Structure: `python3 tests/structure.py` ends `STRUCTURE RATCHET PASSED`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: FULL`, reason `tools/ci/selftest_closures.json changes the gate itself`; the full suite is CI's to run, not reproduced locally.
- CI prediction: `python3 tools/pr/ci_predict.py` predicted one red, `tests / closures INERT READS tests/harness_headers.py: dev/audit/harnesses/r10_product_page.mjs`; `--apply-inert` wrote the entry (commit 11c5dfb170be) and the predictor then reports no predicted red.

## Red checks

none

## Forward-carry

none

## Friction

none
