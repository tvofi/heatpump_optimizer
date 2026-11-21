R11-SEAM-card (round 11, size L, seam `card`): the dashboard card's hit targets, type floor, type and spacing scale, status colours, failure text and history retention. One file of production code, `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`, built to the approved design `design/R11-SEAM-card` 3913198407 (`Design review: approve`, `design-verdict/R11-SEAM-card`). Findings: D4-s1-01, D4-s1-03, D4-s3-01, D4-s3-02, D4-s3-03, D4-s3-04, D4-s3-05, D6-s4-01, D9-s2-01. No issue numbers: the findings are round-11 audit findings (`dev/audit/rounds/round11/ISSUES.json` on `plan/r11`).

What changed, by the design's sections:

- **A, targets and rows (D4-s1-01, D4-s1-03, D4-s3-02).** While the layout editor is open, `setupSvgHtml`'s `line()` draws an invisible `.layout-pipe-hit` twin on each pipe's own path, `max(3.5, _targetMinPx() * unitsPerPx)` units wide. The twin carries `data-hit-edge`, not `data-edge`, so the drawn topology and the pipe's keyboard stop stay the visible path's. It follows the pipe's ornament, which editing hides, and is drawn before the boxes and ports, so those keep their own gestures. `LayoutEditor.onClick` removes `data.edge || data.hitEdge`. `.hl-fold-head` takes `max(32, targetFloorPx)`, so it is 32 px under a mouse and 44 px under touch. `.tile` and `.hl-stat` sit on row subgrids, so the values in one row share a line however their labels wrap.
- **B, type and spacing (D4-s3-03, D4-s3-05).** Every `font-size` in `cardStyleBlock` reads a `--hpo-text-*` step, with one step added, `--hpo-text-base: 14px`, mapped per the design's table. Every padding, margin and gap reads a `--hpo-space-*` step: each length goes to the nearest step, a tie goes to the smaller one, and em is read at the rule's own new size or else the 14 px dialog base. The what-if range inputs lose the browser's default 2 px margin. The SVG drawing-unit text (`.setup-title`, `.setup-slot`, `.setup-chip-label`, `.setup-chip-page`) is left alone, per the accepted svg-11px dismissal.
- **C, one colour per status role (D4-s3-04).** The six status `*_READABLE` literals and `cardStyleBlock`'s three colour locals are gone. Error, success and warning text reads `--hpo-crit`, `--hpo-ok` and `--hpo-warn`. A filled error control under white text reads the new `--hpo-crit-fill`, whose `#b3261e` serves both themes at 6.54:1. `.setup-pipe.invalid` reads `--hpo-crit`. The wood, space-blocked and history notes and the two savings notes leave inline `style=` for classes: a warning stripe over `--hpo-warn-bg` with `--hpo-ink`, and the history note on `--hpo-surface-2`.
- **D, translated failure lines (D4-s3-01).** `serviceFailureText(hass, err)` returns `hass.localize("component.<domain>.exceptions.<key>.message", placeholders)` when the rejection carries a translation key and localize resolves it. Otherwise it returns `err.message`, and failing that `String(err)`. `HeatpumpOptimizerCard`'s `set hass` loads the backend's `exceptions` category once per language. All ten catch sites take it.
- **E, bounded history (D9-s2-01).** `HistorySource.prune(now)` runs at the top of `ensure()`. It drops the chunks, `covered` entries, rows and dedup keys older than the 12 h chunk that holds `now - HISTORY_SPAN_MS`. Each series keeps its last row before the cut, the value or mode still in force at the window's left edge, and `version` is bumped only when a row went.
- **F, D6-s4-01.** Not reproduced at main, so it is pinned and has no production edit (design-review ruling 2). The existing placeholder-parity arm in `tests/card.mjs` is the check: planting `{minuter}` reads 1 in the finder's harness and turns the arm red.

D5-s4-01's card comment units stay in `R11-SEAM-comments-production` (design-review ruling 1); every comment this diff writes or rewrites keeps to C5.

## Design deviations

- **The dialog scales the type and spacing steps.** The design gives every size a fixed px token on `:host`. The dialog's chrome, though, is sized from one font size that `ExpandedDialog.scaleFont` sets from the dialog's width, 14 to 18 px (R10-CARD-VOICE H1), so that it grows with its chart. Fixed tokens would have held it at 14 px at every width, removing working behaviour. Ruled by the orchestrator under mandate 6893738184: `dialog.expanded` redefines each `--hpo-text-*` and `--hpo-space-*` step as `calc(<step>px * var(--hpo-type-scale, 1))`, and `scaleFont` writes `--hpo-type-scale` = px / `DIALOG_FONT_PX_MIN`. `CARD_SCALE_TOKENS` declares `--hpo-type-scale: 1` on `:host`. Up to the scale floor (dialogs up to about 1333 px wide, every width the harnesses render) the steps are the scale's own; wider, the chrome grows as before.
- **The predicted D4-s1-01 after-read of 0 does not hold under the design's drawing order.** The design puts the twin under the ports, boxes and rows so that each keeps its gesture. Ruled by the orchestrator: keep that order. The companion harness reads each pipe at its best point along its length (the design's "check both ends"), and the pipes still cut there are reported as a residual (`## Friction`).
- The twin is emitted after the pipe's ornament rather than directly after the path. The ornament is hidden while editing, and this keeps `tests/card.mjs`'s pipe parser (path, then ornament) reading the editing drawing.
- `r2` moved above `line()`, which runs before its old declaration.
- The history note (`HistorySource.noteHtml`) also leaves inline style; the design named four sites and this is the fifth of the same family.
- **The phone tooltip at the type floor.** Not in the design, found by the P9 grid. At 12 px, the phone-width dialog's shared-step tooltip ran 43.3 px (sv) and 29.3 px (en) past its 196 px chart; base fitted with 9.75 px to spare at 10.92 px text, under the floor. The phone tooltip takes the tile's padding (`--hpo-space-1` `--hpo-space-2`) and a 1.1 line height, the shared-step sentence a 300 px bound there and 260 px elsewhere (the `tt-why` bound, was 220), and `fitWhy`, after the idle explanation, drops the step's reason line and then, last, the shared-step sentence while the box is still taller than its chart. Measured on the card itself in Chromium at 375 px, the P9 state's hover point: 176.25 px in en, sv and de, 11.4 px inside the chart, the sentence kept and the reason line dropped (base showed the reason line at 10.92 px).
- `tests/card_browser.mjs` gains three P9 states (`space_blocked`, `history_unavailable` with a `history` driver step, `savings_page_floor`), so the colour-reach check measures the three note rules this branch moved out of inline style.
- One commit for section B rather than one per rule family. The pass is one mechanical rule applied to every declaration (see the token map above), and each harness re-measures the whole stylesheet anyway.

## Head

57342c0b17a62cad8f6bf175b36c309b7645d32b, on merge base 9e7abae6bb (origin/main at the run: 9e7abae6bb, `date -u` 2026-11-21). It repairs PR head 43c37865a4 (`ci: merge main`) with one commit, touching `tests/card.mjs` and `tests/card_browser.mjs` only; no production line moves. Every figure from earlier rounds below was measured at 123db89390 or 1de96557ad, as each line names, and the card file differs between 1de96557ad and this head only by main's stamp cb8edb65a5 (`git diff 1de96557ad 57342c0b17 -- custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` prints one line, `CARD_VERSION` 10.1.0 to 10.1.1).

## Mutation proof

Each mutant is a design-named mutation target, applied to a `git archive` copy of the head. `node tests/card.mjs` was run on each group of mutants; the groups were chosen so that their mutants reach disjoint checks.

| mutant | edit | `tests/card.mjs` checks that go red |
|---|---|---|
| hitmax (group 1) | `Math.max(3.5, _targetMinPx() * unitsPerPx)` to `Math.min` | "a pipe in the layout editor takes the pointer across 24 px at 375 px (mouse)" and "... 44 px ... (touch)" |
| foldmax (group 1) | `.hl-fold-head` `min-height` to a fixed 32 px | "a fold header is 32 px tall under a mouse and takes the 44 px touch floor under touch" |
| prunecut (group 1) | `chunk < cut` to `chunk <= cut` on `covered` | "history: the bound drops nothing the window can show" |
| trkey (group 2) | `serviceFailureText` never reads the translation key | "failure text: a translated Home Assistant exception reads in the viewer's language", "failure text: a layout save failing under sv shows the sv exception and no en.json text" |
| critfill (group 2) | dark `--hpo-crit-fill` to `#f28b82` | "--hpo-crit-fill (dark) carries white text at 4.5:1" |
| keeplast (group 2) | `prune` keeps only rows at or after the cut | "history: the bound drops nothing the window can show" (the mode at the left edge) |
| emptyloc (group 3) | an empty `localize` answer is returned as the text | "failure text: a rejection with no translation key, or one localize cannot resolve, keeps its message" |
| fitold (group 4) | `fitWhy` stops after the idle explanation | "UX-1 a box too tall with no explanation drops its reason line and keeps the shared-step sentence", "UX-1 and drops the shared-step sentence only when the rows alone fit" |

| reEscape (repair, 57342c0b) | `reEscape` back to the dot-only `s.replace(/\./g, "\\.")` the CodeQL alert named | "a selector spliced into a RegExp matches only itself, backslash included" (`node tests/card.mjs`: 1 FAIL, rc 1; unmutated: 0 FAIL, rc 0) |

Group 1 failed 4 checks, group 2 4, group 3 1, group 4 2, each exactly the rows above; the unmutated head passed all.

## Null control

- CodeQL repair: the new check's input `a\\.b c` holds a backslash, and its negative arm `a\\xb c` is what a dot-only escape lets through. Under the dot-only mutant (the `reEscape` row above) the check reads FAIL with detail `a\\.b c`, and it reads ok at 57342c0b.
- Comment ratchet repair: `python3 tests/comment_ratchet.py --base origin/main` at 43c37865 (the null control) reads `long_units_head=1625` against base 1622 and `comment_ratchet: FAIL`. At 57342c0b it reads `long_units_head=1622` and `comment_ratchet: OK`.
- D4-s3-01: `m3_look.mjs --err=plain` (a rejection with no translation key) reads `english_error_lines` 0 at base and at head.
- D4-s1-01: the port centre band (`port_hit_median_px`), the finder's control, reads 31.25 px at base and 30.75 px at head under the companion (on this machine it reads 30.75 to 31.25 px run to run; the finder's Linux reading is 30.5 px). The companion's perturbation `PERTURB=1` (`Math.max` to `Math.min` in the twin's width) reads 576 of 576 at head.
- D9-s2-01: `card_history_retained.mjs --arm nopan` reads 0 rows/day and 0 chunks at base and at head.
- D6-s4-01: `card_placeholders.mjs` reads `unresolved_en=0` and `unresolved_de=0` at both ends. The `{minuter}` plant reads `unresolved_sv=1` and `stale_title_literal_tokens=1`.
- D4-s1-03: the fine-pointer arm of `m1_browser.mjs STATES=score_open` reads 0 at both ends; the count is the coarse arm's alone.
- D4-s3-04: dark `ok` was one colour at base, because `SUCCESS_READABLE_DARK` equals `--hpo-ok`'s dark literal; it stays one colour at head.
- `tests/card.mjs`'s new checks run against the base card go red. The output names: the fold floor; both pipe-twin floors; the twin's unlaid width; the twin click; `--hpo-crit-fill` in both themes; and status tokens alone in both themes. It then stops with `ReferenceError: serviceFailureText is not defined`, the symbol section D adds. The history checks after it are shown red at base by the D9 harness (1448.0 rows/day) and by the `prunecut` and `keeplast` mutants above.

## Figures

The finders' harnesses are from `plan/r11` 819aa2e354, `dev/audit/rounds/round11/` exported beside each tree, sha1 m1_pipes f0f66a6e84d6, m1_browser 3326714a0c1e, m3_look 2fe434efc2cc, card_history_retained 59cfb61babfc, card_placeholders 330e7302a8a1. Base is 1723f9fdc9. The machine is macOS (Darwin), Chromium 1254 (158.0.8127.18), Node 20.10.0; `tests/card.mjs` ran on Node 24.22.1 with `--max-old-space-size=6144`.

| finding | command | base | head |
|---|---|---|---|
| D4-s1-01 | `node $EXPORT/D4/s1/m1_pipes.mjs` `pipe_hit_under_floor` | 576 of 576 (max 5.75 px) | 576 (max 0 px): flat, see below |
| D4-s1-01 | `node dev/audit/harnesses/r11_card_pipe_hit.mjs` `pipe_hit_under_floor` | 576 of 576 (max 6 px; port null 31.25 px) | 132 of 576, all cut by targets (`## Friction`) |
| D4-s1-03 | `STATES=score_open node $EXPORT/D4/s1/m1_browser.mjs` `strict_small` | 72 | 0 |
| D4-s3-01 | `node $EXPORT/D4/s3/m3_look.mjs --vp=375,768,1280 --err=ha --states=pin_fail,save_fail` `english_error_lines` | 24 | 0 |
| D4-s3-02 | `m3_look.mjs --vp=375,768,1280 --states=score_open,score_open_typical,score_open_no_evidence,score_open_graded_pump,savings_open,folds_open` `tile_row_misaligned` | 12 (max 14 px) | 0 |
| D4-s3-03 | `m3_look.mjs --vp=375,768,1280 --states=tooltip_hover,shared_steps_hover,estimated_price_hover,layout_editing,picker_twins,setup_clear_armed` `below_floor_cells` | 78 (9 elements) | 0 |
| D4-s3-04 | `m3_look.mjs --vp=375,768,1280 --states=status_stale,status_fallback,live_default,draft_menu_open,pin_ok,pin_fail,save_ok,save_fail,wood_alert,health_page` `role_colour_split` | 5 | 0 |
| D4-s3-05 | `m3_look.mjs --vp=375,768,1280 --states=live_default_expanded,score_open,tooltip_hover,shared_steps_hover,savings_page,health_page,setup_two_tank,advisor_page,draft_menu_open,save_confirm` `offscale_font_sizes` / `offscale_spacing` | 14 / 41 | 1 / 0 |
| D9-s2-01 | `node --expose-gc $EXPORT/D9/s2/card_history_retained.mjs --days 30` `retained_rows_slope`, `covered_chunks` | 1448.0 rows/day, 60 | 0.0 rows/day, 5 |
| D6-s4-01 | `node $EXPORT/D6/s4/card_placeholders.mjs` `unresolved_sv` | 0 | 0 (pinned; the plant reads 1) |

- **D4-s1-01, the finder's harness, reads flat by its rule (fixer.md step 3).** `m1_pipes.mjs` counts a point only where `elementFromPoint` returns the visible `.setup-pipe`, and only across the midpoint. The twin is drawn over the stroke, so the stroke is never on top. The sha1-cited companion `dev/audit/harnesses/r11_card_pipe_hit.mjs`, landed here, makes two changes. It counts a point when the element there is the pipe or its twin naming the same edge, which is the rule `LayoutEditor.onClick` applies. It also reads the band at 19 points along the pipe, each scrolled into view, and keeps the pipe's best point. Its `PERTURB=1` reads 576 of 576.
- D4-s1-01 residual: 132 of 576 pipe renders read under the floor at their best point under the companion harness. Each is cut by a target the design draws above the twin: `.layout-port-hit` (starts a connection), `.setup-box` (moves a box), `.setup-chip-hit` (opens the options page), or `.setup-hit` (opens a slot). They are the short pipes `buffer_tank>mixing_valve`, `buffer_tank>lower_zone` and `mixing_valve>upper_zone`, mostly in the dragged state. Each such pipe stays removable from the keyboard (D4-s1-04's Enter or Delete on the focused pipe) and at its best point, 10.25 to 43 px. Carry: dismissed: no remaining round-11 group owns the layout editor's target geometry (`R11-SEAM-config`, `R11-SEAM-product-text` and `R11-SEAM-comments-production` are text, config and comment seams), and the residual is the approved drawing order, which keeps every other editor gesture reachable; a later D4 round re-measures it with the in-tree companion.
- **D4-s3-05.** The one off-scale size left is 14 px, the design's added step: the harness's scale set is fixed at {12, 13, 15, 18} (design-review ruling 3). No padding, margin or gap reads off the scale (the what-if range inputs’ browser-default 2 px margin was the last one).
- **D9-s2-01.** Retained rows hold flat from day 3 to day 30 (3454 rows at day 30 against 43400 at base).
- **Class enumeration (fixer.md step 8).** The design's sibling-site commands (section 5) were re-run on the head, with these dispositions:
  - `grep -nE 'err(\.message| && err\.message)' $F`: 1 hit, `serviceFailureText`'s own fallback; the ten former sites call it.
  - `grep -nE 'READABLE|var\(--(warning|error|success)-color' $F`: `ACCENT_READABLE` alone, the accent role, kept by the design.
  - `grep -nE 'style="[^"]*(font-size|color|padding|margin)' $F`: 0.
  - Font-size declarations in `cardStyleBlock` not reading a `--hpo-text-*` token (`inv.py` rule: every `font-size` in the function): the 5 SVG drawing-unit rules, dismissed (svg-11px).
  - Padding, margin and gap declarations not on a `--hpo-space-*` token: 1, `.expand, .close { margin: calc(-1 * var(--hpo-space-1, 4px)) }`, a negative step.
  - `grep -n 'this\.\(log\|actionLog\|seen\|covered\|memo\|chunks\)\b' $F`: all `HistorySource`, all now bounded by `prune`.
- `node tests/card.mjs`: ALL CARD CHECKS PASSED at 1de96557ad, in the scoped gate below.
- Repair at 57342c0b17. The delta's own scope, `python3 tests/closure.py select --diff 43c37865a4`, reads `MODE: SCOPED -- 4 script(s) run, 29 scoped out` and names `doc_claims.py`, `plan_view.py`, `card.mjs` and `card_drift.mjs`, and each was run at 57342c0b17. Results: `tests/plan_view.py` rc 0; `node tests/card.mjs` rc 0 with 1466 `ok` and 0 `FAIL` lines, one of the `ok` lines the new backslash check; `tests/doc_claims.py` ALL 441 checks PASSED; `node tests/card_drift.mjs <merge-base>` 44 states moved and claimed, 1 identical. Also at 57342c0b17, `tests/entities.py` reads ALL 2736 ENTITY CHECKS PASSED, `tests/structure.py` STRUCTURE RATCHET PASSED and `tests/env_drift.py` rc 0. The `tests/card_browser.mjs` change is a comment, so the browser job was not re-run here.
- `node tests/card_browser.mjs` (CI’s never-scoped `browser` job; run here at 123db89390 with `HPO_PAGES_OUT=docs/img/card`, which wrote the figures 1de96557ad commits): ALL BROWSER CHECKS PASSED, `P9 grid: 396 cells, 23876 text runs, 889 box-intersecting pairs inked, 112 colour rules`. At the pre-fix head it read three reds: three colour rules unreached, the phone tooltip 29.3 / 43.3 px outside its chart, and P40 figures stale in ten pictures. 1de96557ad only re-lays the phone tooltip rule’s text, which the P9 grid does not read.
- `node tests/card_drift.mjs <merge-base>`: 44 of 45 states move and are claimed in `tests/golden/card_claimed_drift.txt` (`claims-for: 10.1.0`). `editor_schema` is identical and unclaimed. `tests/golden/claimed_drift.txt` is byte-identical.
- Scoped gate, `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub ./tests/run.sh` at 1de96557ad, machine load 200 to 380: `MODE: SCOPED -- 11 script(s) run, 22 scoped out`. ok: env_drift (`--claims-only`, `--all`), plan_view, closure selftest, arch_score_head, card.mjs, card_drift.mjs, features, layout, deployment_shape. Red, each disposed under `## Red checks`: doc_claims (1 of 439), entities (1 of 2731), harness_headers (12 of 115).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- prepr: passed rc=0 at 57342c0b17a62cad8f6bf175b36c309b7645d32b (`PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>`, scoped; the delta reaches no closure). The run before it refused on two counts. One was the body (`tests / browser` unanswered), answered under `## Red checks`. The other was a `ci_predict` step replay of `bash tools/audit/seat/bus.sh --self-test`: rc 1 at the head, 0 at the base. That replay does not reproduce at 57342c0b17. Run alone, the self-test reads `bus self-test: 240 checks, 0 failed`, rc 0. `python3 tools/pr/ci_predict.py --base 9e7abae6bb --only step-replay` reads `no closures, fast, governance or instrument red predicted`. The repair touches no file the bus self-test reads.
- `python3 tools/pr/ci_predict.py --apply-inert`: applied `inert_reads tests/harness_headers.py: dev/audit/harnesses/r11_card_pipe_hit.mjs`, then no closures, fast, governance or instrument red predicted.

<!-- figure-block: scope-line mb=9e7abae6bbce9bc971393a5010ae099dfd9e6a90 head=57342c0b17a62cad8f6bf175b36c309b7645d32b -->
~~~text
MODE: SCOPED -- 11 script(s) run, 22 scoped out.
~~~
<!-- /figure-block -->

## Architecture score

`python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0280 IMPROVES` (`card_clone_copies` 103 to 101, +0.0280; `card_rule_copies` 70 to 67, gate only). `card_clone_copies` falls because ten respellings of the error rule became one function, `serviceFailureText`, and the three per-role colour locals became the role tokens: a real move, banked for the reviewer's diff (design-review note rule-copies-bank). `card_rule_copies` is gate-only.

## Red checks

Owed reds at 43c37865a4, from `python3 tools/audit/seat/merge_train.py owed-reds` and the job logs the dispatch names:

- `tests / fast (3.14)` (job 136625614390): `tests/doc_claims.py`'s comment ratchet refused five test-comment sentences over 40 words, four in `tests/card.mjs` (97 to 99 long units) and one in `tests/card_browser.mjs` (21 to 22). Fixed in 57342c0b17: each sentence is split with its meaning kept, and `python3 tests/comment_ratchet.py --base origin/main` reads `long_units_head=1622` against base 1622, `comment_ratchet: OK` (`tests/doc_claims.py`: ALL 441 checks PASSED). Root-cause trigger: the ratchet (`tests/comment_ratchet.py`, added to main at 3702981d47 on 2026-11-19T01:00Z) reached this branch by the merges of main after ba991fac8a, so the sentences predate the check. The cheaper detector exists and costs nothing new: the scoped `doc_claims.py` re-run after a main merge, which the recovery brief now requires. State (d), preconditions changed under the branch; no further countermeasure.
- `CodeQL` (check run 136577575390), `js/incomplete-sanitization` high at `tests/card.mjs:1660`: the phone-rule probe spliced a selector into a RegExp escaping dots only. Fixed in 57342c0b17 with `reEscape`, which escapes every regex metacharacter, the backslash included, through one character class and `$&`. It is pinned by "a selector spliced into a RegExp matches only itself, backslash included", and the dot-only form fails that check (`## Mutation proof`). The alert is fixed, not dismissed. Root-cause trigger: no cheaper detector runs here. The environment has no `codeql` binary, and `eslint`'s stock rules carry no equivalent of this query, so the CodeQL job is the cheapest detector that finds it. Recorded: no countermeasure.
- `pr-contract / pr-contract` (job 136620208870): the body did not answer `tests / fast (3.14)`, and its figure-block scope line named 1e0e175cbe. This body answers it, and the figure block is refreshed at 57342c0b17.
- `gate`: `merge_train.py classify 43c37865a4 --pr 3821` prints `red: gate`. `gate` is `ci.yml`'s one required check, and `tools/ci/gate.py` judges it from the units above. Its log was not read here; once those units are green at this head, CI is the authority on it.

Earlier rounds' reds, at 1de96557ad and ba991fac8a:

- `tests/doc_claims.py` "every declared width and height equals the PNG header": `docs/index.html` declared `advisor-light.png` at 1056x708, the regenerated file is 1056x716. Fixed in ba991fac8a by setting the declared size from the PNG header; the other declared card figure sizes already matched. Re-run: ALL 439 checks PASSED.
- `tests/entities.py` "a measured script's late-writing descendant is waited for, not recorded as nodata" (1 of 2731): a wall-clock wait bound in the coverage stage's self-test, read under a load average of 200 to 380; no file this branch touches is in its path (closure stage, `tests/closure.py`). CI is the authority.
- `tests/harness_headers.py` (12 of 115): every failure is `dev/audit/rounds/round4/D7/sysid_estimator_frontier.py`, `rc=124 ... wall limit 900s exceeded` (154 s of CPU in 900 s of wall at that load), and its 11 RESULT lines then print nothing. The new `dev/audit/harnesses/r11_card_pipe_hit.mjs` passes its header checks. CI is the authority.
- `tests / browser` (`tests/card_browser.mjs`, Linux): red on an earlier commit of this branch. P40 read the committed setup figures at a height drawn off Linux (706 px against the Linux render's 698), because the figures were written on macOS, whose fonts lay the card out differently. Fixed by 30e547d7f7, which regenerates the figures on Linux. The job reads success at 43c37865a4 (job 136625614782), and this repair touches only a comment in that file. Root-cause trigger: the cheaper detector is the same script run on Linux before the push (`HPO_PAGES_OUT=docs/img/card node tests/card_browser.mjs`, about 5 minutes, the job's own wall time). It exists, and `fixer.md` step 5 already names it for a `GRID_SURFACE` diff; it was run, but off Linux. State (b): run, but not on the platform the check measures. No new countermeasure: the cloud seats run on Linux.
- `tools/audit/machinery_ratchet.py --check --base origin/main --head HEAD` (prepr): `FAIL churn_per_kilo_product_lines 33762 <= 14797 + band 3636` over a window of 580 merges (23860 product lines, 805571 nonproduct). Inherited from the window, not from this branch: the candidate is a production merge whose own diff is 570 product lines against about 505 nonproduct, under 1000 per kilo, so it lowers the metric. Not a fix this group can make (`ratchet-budgets.md`: paid by production merges).

## Forward-carry

none

## Friction

none
