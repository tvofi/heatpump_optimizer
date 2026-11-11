The product page (`docs/index.html`) rebuilt to the design note design/R10-PRODUCT-PAGE-REDESIGN at 2f56c2e6a9a2d280a1ab741ad768dec2d8ced89f: one illustrative day drawn by a generator (`tools/site/day_chart.mjs`) and pinned by `tests/doc_claims.py`, a scroll story over it, a first-week timeline, and a control-path chooser in place of the table. The note's acceptance list is `dev/audit/harnesses/r10_product_page.mjs`. The first fixer stopped on four points where the tree contradicted the note (BLOCKED.md at c7b0b4611d88, build 3bfb1990c83c); this head applies the orchestrator's rulings on them, given under mandate 6715477401.

## Head

45a5053c62cd273d171d6f60be2450d81cc0a7d6: the pull request's head 33a4e689fc7f98dba7ca3af234dcd3f7187f311f plus two repair commits (dd31ed3599c8, 45a5053c62cd). Its merge base with origin/main is 6cc15e9b8f53b5393bb4ed7297bfc12747d6e2f6. origin/main's tip at 2026-11-11T22:57:56Z is 61afd4f2db10341ab9b86583944402b206eb4c78; `git merge-tree --write-tree origin/main HEAD` exits 0 against it, so no merge was made. The Rulings, and the first four mutation and three null-control entries below, were taken at 11c5dfb170be and the repair touches none of the lines they mutate; every entry under Figures is re-taken at this head unless it names another.

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

## Null control

- At the base cbd23f1c8bf6 `python3 tools/audit/seat/selftest_wiring.py --check` reports no unwired tool, and at the first fixer's build it reports the generator unwired: the step is what wires it, not a change to the checker.
- With the row in place, `python3 -I tools/ci/selftest_scope.py select --change M:README.md` is `MODE: SCOPED` and does not list `day-chart`; `--change M:tools/site/day_chart.mjs` is `MODE: SCOPED` and lists it. The row selects the step on its own file and not on an unrelated one.
- Unmutated, `node tools/site/day_chart.mjs --self-test --check` exits 0 and the harness prints `RESULT fails=0`.
- Depth root, at 45a5053c62cd with the one `const ROOT` line put back to the three-level `path.resolve` in a detached worktree (taken at dd31ed3599c8, whose `ROOT` lines are the head's): `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` exits 1, `1 of 112 HARNESS HEADER CHECKS FAILED`, with the `FAIL depth seams: dev/audit/harnesses/r10_product_page.mjs` line. The check reads the line, not the commit.

## Figures

- Harness at the head: `node dev/audit/harnesses/r10_product_page.mjs` (sha1 47d8241f76bf7df4c0434e7204994025861a66f0) prints `RESULT fails=0`, `RESULT base=6cc15e9b8f53`, its new line `ok   server: an absent path and a directory answer 404, and the page 200  [/no-such-file.html 404; /img 404; /index.html 200]` among them. Before, at the first fixer's build 3bfb1990c83c, the same harness printed one FAIL (check 7), which the second mutation above reproduces.
- Documentation claims: `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` ends `ALL 316 checks PASSED` at the head; at the first handoff's base cbd23f1c8bf6 it ended `ALL 315 checks PASSED`; the difference is the generator's pin.
- Page size: `wc -c < docs/index.html` prints 69893 at the head against the note's 70 kB cap (70 000 bytes); 45301 at cbd23f1c8bf6.
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

## Forward-carry

none

## Friction

none
