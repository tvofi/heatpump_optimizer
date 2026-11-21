Fix review: blocked b1ee994a6ea56e3fbd5eec91b2adae6e071005e9 mutation-vacuous: custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:7344 custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:11424 custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:5257

bus-nonce: 81fb1f195c740fb6278d0c70b3552291

Round 1 (first review of #3821). Cloud reviewer seat, Linux, Chromium 1243 at /opt/pw-browsers, Node with `--max-old-space-size=6144`.

## Block

Three production lines the body names survive deletion. Nothing in the closure fails for any of them: not `node tests/card.mjs` and not `node tests/card_browser.mjs` (CI's browser job), each run on a mutated copy of the head. Every survivor this review found is listed (survivor_list.py rule):

- `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:7344` (section E, D9-s2-01: "drops the chunks ... older than the 12 h chunk"). Deleting `if (chunk < cut) this.chunks.delete(chunk);` leaves `card.mjs` at 0 FAIL and `card_browser.mjs` at ALL BROWSER CHECKS PASSED. The check named "history: a card panned daily for 30 days holds no more than the 48 h span's chunks, and its rows plateau" (`tests/card.mjs:14274`) reads `hs.covered.size` and the row counts, never `hs.chunks`. The finder's `card_history_retained.mjs` does not count `chunks` either. So the bound on the `chunks` Map is unpinned: under the mutant it grows by one entry per 12 h chunk panned into, without limit.
- `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:11424` (`## Design deviations`, first bullet: `scaleFont` writes `--hpo-type-scale`). Deleting the `setProperty("--hpo-type-scale", ...)` write leaves `card.mjs` at 0 FAIL and `card_browser.mjs` at ALL BROWSER CHECKS PASSED. The body says this deviation preserves working behaviour: without it the dialog chrome is "held at 14 px at every width". No check pins that behaviour. The `dlgOf` checks read `fontPx`, and the test DOM's `style` stub has no `setProperty`, so the write never executes under test.
- `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:5257` (section A, D4-s3-02: `.tile` and `.hl-stat` on row subgrids). Replacing `display: grid; grid-template-rows: subgrid;` with `display: block;` leaves `card.mjs` at 0 FAIL and `card_browser.mjs` at ALL BROWSER CHECKS PASSED. The finder's `m3_look.mjs` does see it: `tile_row_misaligned` goes back to 12 (max 14 px), which is the base figure exactly. So D4-s3-02's fix has no in-tree pin, and a regression would reach main green.

Each needs an in-tree check that goes red on its mutant, with that red shown in the body. The rest of the fix held under review (see `## Evidence`).

## Findings

none

## Evidence

- Head: `b1ee994a6ea56e3fbd5eec91b2adae6e071005e9`, merge base 9e7abae6bb. At the final re-read the branch tip had moved to `1bd0f355b941d0dd432e3b3db6e4741d452d1af6`, `ci: merge main` alone. `review_carry.py` reads 0 of 1 branch-only commits non-merge. The three-dot diff against the new merge base 86859b9594 is the same 23 files, 808+/275-, differing only in `tests/closures.json` context lines. `git diff --stat b1ee994a6e 1bd0f355b9 -- tests/card.mjs tests/card_browser.mjs tests/card_rig.mjs custom_components/heatpump_optimizer/www/` prints nothing, and the three survivor lines sit at the same line numbers at 1bd0f355b9. Every figure here therefore holds at both SHAs.
- `git merge-tree --write-tree origin/main b1ee994a6e` rc 0 (`LEDGER-MERGE: resolved tests/closures.json`); no conflict.
- CI: `merge_train.py classify b1ee994a6e --pr 3821` went from WAIT to `GREEN b1ee994a6ea56e3fbd5eec91b2adae6e071005e9 pending: none red: none` (ev/classify_poll.log). The range's reds in the owed set (`tests / fast (3.14)`, `pr-contract / pr-contract`, `tests / browser`, `gate`) are each answered under the body's `## Red checks`. `CodeQL` is outside the owed set and is answered there too.
- Mutation proof, the body's eight targets re-applied by my own driver (ev/mutant_driver.py, ev/mutants_card_mjs.txt; each one a single-site replace on a copy of the head, then `node tests/card.mjs`). hitmax: 2 FAIL (the 24 px mouse and 44 px touch pipe checks). foldmax: 1 FAIL. prunecut: 1 FAIL. trkey: 2 FAIL. critfill: 1 FAIL. keeplast: 1 FAIL. emptyloc: 1 FAIL. fitold: 2 FAIL. Each matches the body's table. Extra targets: hitedge (`data.edge || data.hitEdge` to `data.edge`) 1 FAIL; noprune (the `this.prune(liveEdge)` call removed) 1 FAIL; noph (placeholders dropped) 2 FAIL. Unmutated head: `ALL CARD CHECKS PASSED`, 1466 ok lines. Survivors: the three under `## Block`.
- Finder harnesses from plan/r11 819aa2e354, sha1 prefixes re-derived equal to the body's (m1_pipes f0f66a6e84d6, m1_browser 3326714a0c1e, m3_look 2fe434efc2cc, card_history_retained 59cfb61babfc, card_placeholders 330e7302a8a1). My base is the merge base 9e7abae6bb; the body's is 1723f9fdc9.
  - D4-s1-01, `m1_pipes.mjs`: 576 of 576 (max 5.75 px) at base and 576 (max 0 px) at head, flat by its rule as the body states. Companion `r11_card_pipe_hit.mjs`: 576 of 576 at base, 132 of 576 at head (min 10.25 px, max 56.25 px), `PERTURB=1` 576. Port null control 30.25 px at both ends (body: 31.25/30.75; finder: 30.5).
  - D4-s1-03, `STATES=score_open m1_browser.mjs` `strict_small` at head: 0. Base not re-run.
  - D4-s3-01, `m3_look.mjs --err=ha --states=pin_fail,save_fail` `english_error_lines`: 24 at base, 0 at head.
  - D4-s3-02, `tile_row_misaligned` over the body's six states: 12 (max 14 px) at base, 0 at head, 12 under the nosubgrid mutant.
  - D4-s3-03, `below_floor_cells` over the body's six states at head: 0. Base not re-run.
  - D4-s3-04, `role_colour_split` over the body's ten states: 5 at base, 0 at head.
  - D4-s3-05, `offscale_font_sizes` / `offscale_spacing` at head over the body's ten states: 1 / 0. Base not re-run over that set; over the ten role states it reads 9 / 34 at base.
  - D9-s2-01, `card_history_retained.mjs --days 30`: 1448.0 rows/day, covered 60, total 43400 at base; 0.0 rows/day, covered 5, total 3454 at head. `--arm nopan` reads 0.0 at head.
  - D6-s4-01, `card_placeholders.mjs`: 0/0/0 at both ends. Planting `{minuter}` in sv `status.stale_title` reads `unresolved_sv=1` and `stale_title_literal_tokens=1`, and `card.mjs` goes red on two checks (ev/d6_plant_minuter.txt).
- Claims: `node tests/card_drift.mjs 9e7abae6bb` reads `card_drift: 44 state(s) moved and claimed, 1 identical`. `tests/golden/card_claimed_drift.txt` reads `claims-for: 10.1.1`, equal to `VERSION` 10.1.1; the body's `claims-for: 10.1.0` predates main's stamp. `tests/golden/claimed_drift.txt` is untouched. `python3 tests/env_drift.py --claims-only` rc 0.
- `VERSION`, the manifest version and `RELEASE_NOTES.md` are untouched by the three-dot diff.
- Class enumeration, re-run on the head: `grep -nE 'err(\.message| && err\.message)'` prints 1, `serviceFailureText`'s own fallback. The other 15 `catch` sites show no message to the user (each returns, ignores storage or clears history state). The 10 `serviceFailureText(` call sites match the body's ten.
- Architecture score: CI `arch-score / arch-score` success, cited not re-run. `tests/closures.json` adds only `dev/audit/harnesses/r11_card_pipe_hit.mjs` to `inert_reads`.
- Forward-carry: the body has `none`. Its one residual (132 pipes cut by targets drawn above the twin) carries a valid `dismissed:` (carry_audit at head: 1 routed, 0 unrouted).
- Body figures not re-derived here: D4-s3-03's base 78, D4-s3-05's base 14 / 41, D4-s1-03's base 72, the comment-ratchet figures and the prepr run.
