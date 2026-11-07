R10-WHY-NOW-WIDGET (tvofi 2026-11-01, rulings card 2 option (c) part (b)): a live "Why now" block for the current slot, built to the approved note at design/R10-WHY-NOW-WIDGET 60d61fcf (verdict 043b31ad). The solver publishes five signed drivers per step (`price_rank`, `comfort_floor`, `mold_guard`, `away`, `forecast`), each a percent of that step's push with magnitudes summing to 100; `get_current_action` carries step i's through `slot_drivers.why_now_at` at the one index it already finds; the space-plan sensor publishes it as `why_now`; the card renders it after the headline narrative, en and sv, with the metric in plain words as every hover.

**Owning seam.** New pure module `custom_components/heatpump_optimizer/slot_drivers.py` (numpy, no Home Assistant import). `_build_result` calls `slot_drivers.space_drivers` once. The away setback enters as a solver input, `SolveLimits.away_floor_drop_c`, from `away.floor_drop_c` (which shares `_setback_target` with `solve_bands`, so the setback's condition is written once).

**Coordinator growth (r3-b), the whole of it.** `_solve_record` passes one kwarg (`away_floor_drop_c=`), its two-line T5 comment folded to one; the module-level `_apply_result_payload` copies `why_now` when the action carries one (four lines with the comment). `HeatPumpOptimizerCoordinator` gains no method body and no attribute; no seam_map entry. The what-if solve (`async_simulate`) is untouched: `away_floor_drop_c` defaults to None, which is what the note says it passes, so no line is spent saying it.

**Departures from the note, each raised here.**
- `_Horizon` carries a third field, `away_floor_drops` (setback plus holiday drop, per step), beside the note's `comfort_floors` and `mold_floors`: `_build_result` sees only the horizon, so the away figure needs a per-solve carrier, and `_Horizon` is that carrier by its own docstring.
- The class growth is paid as the note says, by moving code into slot_drivers.py: `slot_drivers.step_reasons` now owns step i's `space_reason`/`dhw_reason` reads as well as `why_now`, so `get_current_action` lost two inline readers and gained one `update` call; one owner for "why this step".
- The attribute is published by a `SpaceHeatingPlanSensor.extra_state_attributes` override, not inside `_PlanSensorBase`'s 150-line method (adding it there crossed `methods_over_150`); space-only by construction rather than by a kind test.
- No `coord_*` claim (verdict r3-d): measured, the coord captures are `optimization_status: not_run` (no solve, so `_apply_result_payload` never runs) and env_drift reads all five byte-identical; a claim nothing matches is a stale claim env_drift refuses. `tests/golden/claimed_drift.txt` is byte-identical to the base.
- The card's tile and Plan-page figures under docs/img/card moved: the dialog's Plan page repeats the headline, so card_browser.mjs's P40 refused the committed `tile-*`, `plan-*` and `plan-why-*` (structure hashes; the tile 866 -> 919 px). Re-taken with `HPO_PAGES_OUT=docs/img/card`; `health-*`/`setup-*` moved in pixels only on this box and are left as committed. The note's `make_card_figures.mjs` figures are byte-identical base vs head.
- The score's unknown-code filter and the why-now one are one helper, `knownCodes`, after tools/audit/archscore read the copy as a new clone class (card_clone_copies 103 -> 105); now NULL.
- The card shows each weight as a whole signed percent (the solver's 0.1 rounding stays in the attribute).

**Brief carries.** Carry 1 (the group's spec from the owner's 2026-11-01 ruling) is implemented whole, its strings verbatim en and sv: "Why now"/"Varför nu"; "Price rank"/"Prisrang", "Comfort floor"/"Komfortgolv", "Mold guard"/"Mögelskydd", "Away"/"Bortaläge", "Forecast"/"Prognos"; the direction phrases ("pushes toward running"/"driver mot drift", "pushes toward idle"/"driver mot vila", "no effect now"/"ingen påverkan nu") as each row's visible sub-line; the metric explanation as the block's hover and appended to every row's hover; "No data"/"Ingen data" as the absent-key line, which that explanation defines. Its failing test, null control and perturbations are the ones below. Carry 2 and Carry 3 (PR 3198 item 7c609975, the same P9 defect recorded twice) are the clip-walk fix that follows.

**P9 clip check (Carry 2, Carry 3; item 7c609975).** `unreachable()` in tests/card_browser.mjs starts its walk at `run.el`, so a run clipped by its own box is reported.

**Forecast scale.** Kept at 10 °C: on the winter goldens no step of 96 saturates (rule below).

Alternatives the note weighed (second current-step search, coordinator-side derivation, re-solves, weights in reason strings, `scoreDrivers` reuse) lost for the note's reasons; nothing here revisits them.


**This pass (repair for the `tests / mutation` red).** `tests/features.py` gains seven checks in its why-now block that drive `slot_drivers.py` at its bounds and clamps: `_price_push` on zero, one and two steps; `_forecast_push` on a hand-built horizon whose 8 h window, 10 °C scale, 1 kW solar divisor and ±1 clip each change the figure; `space_drivers`' 0.5 °C half-band floor and its comfort and away clips; `away_floor_drops` on a holiday calendar with no step on a holiday; and `why_now_at` at each list's own end and on a NaN price. `tests/mutation_table.py --pin-killed` recorded the 14 sites those checks kill under `killed_by`. Two sites cannot be killed, and each has an `equivalent` verdict under `survivor_triage` that gives its reason. No production line changed in this pass.

## Head

b62b49ab9b48130bf5fa45066445bfd246c8c856, on origin/main 630bf533d838110be56ede0366756da3de0d941e (checked 2026-11-07T12:01Z). Above 8b7a1cd5d ("ci: pin killed mutants"), this pass adds two commits and two merges of main. The commits are 'tests/features.py' and the 16 new ledger rows under tests/mutation_ledger/. The merges are 136e835c3 at 58a5d8caf, and 630bf533d at b62b49ab9. Main moved after the first tools/pr/prepr.sh run, so it was merged and prepr.sh re-run at b62b49ab9. The second merge's delta is dev/, tools/, tests/entities.py and tests/closures.json: no file under custom_components/ or www/, and neither tests/features.py nor the ledger (`git diff --name-only b62b49ab9^1 b62b49ab9`). At b62b49ab9 this pass re-ran the mutation ratchet, tests/structure.py, the scope, tests/entities.py and prepr.sh. The scoped gate and the pin run were measured at 3a4dc75f1e86, whose production files, features checks and ledger are byte-identical to b62b49ab9's. The solver, card and browser figures from the previous pass were measured at d4aa09ed2ad6. Since then the production files have changed only through the merge of main: `git diff --quiet 58a5d8caf HEAD -- ':!tests/features.py' ':!tests/mutation_ledger'` exits 0, so this pass's own commits touch nothing else. That merge brought main's changes to 11 files under custom_components/ and www/ (`git diff --name-only a9a4724bf 136e835c -- custom_components/ www/`), so the figures marked d4aa09ed2ad6 describe the pre-merge tree. The checks this pass re-ran at 3a4dc75f1e86 are listed in Figures.

## Mutation proof

The 16 sites the `tests / mutation` red named are custom_components/heatpump_optimizer/slot_drivers.py lines 30, 33 and 37 (CONST); 55 (BOOLOP); 72 (CMP_BOUND, GUARD_OFF); 90, 94, 96, 118 and 120 (CLAMP_DROP); 136, 155 and 159 (CMP_BOUND); and 157 (CMP_BOUND, GUARD_OFF). `python3 tests/mutation_table.py --pin-killed --base origin/main` applied each mutant to slot_drivers.py and drove the recorded closure drivers (tests/features.py, tests/harness_headers.py, tests/stress.py). It reported `PIN KILLED: 14 pinned, 2 left unpinned (2 survived, 0 not started for the budget, 0 exclusive tails cut, 0 timed out, 0 skipped)`. Every one of the 14 reads `killed by tests/features.py`. Which check kills which mutant:
- L30 FORECAST_LOOKAHEAD_H doubled, and L33 FORECAST_OUTDOOR_SCALE_C doubled: the step reads 0.3 and 0.1 instead of 0.2. FAIL "forecast push reads 0.2 on an 8 h window at 10 C, clips at 1, divides solar by >= 1 kW".
- L94 `max(p_max_kw, 1.0)` dropped: -0.7 instead of -0.35. L96 clip dropped: 2.625 instead of 1.0. Same check.
- L37 MIN_HALF_BAND_C doubled: (75.0, -25.0) instead of (50.0, -50.0). L118 comfort clip dropped: (88.9, -11.1). L120 away clip dropped: (14.3, -85.7). FAIL "the comfort half-band floors at 0.5 C, and comfort and away clip at one half-band".
- L55 `and` -> `or`: zeros instead of None. FAIL "a holiday calendar with no step on a holiday and no setback reads None, not zeros".
- L72 `n < 2` -> `n <= 2`: two steps read [0, 0]. L72 guard off: one step reads [nan]. FAIL "the price rank is empty for no step, 0 for one, +1/-1 for two".
- L155, L157 and L159 bound `>=` -> `>`: an IndexError instead of None. L157 guard off: a NaN price returns drivers. FAIL "why_now_at is None at each list's own end and on a NaN price, never an IndexError".
- The two survivors, both `-- lives`, and both judged equivalent: L90 CLAMP_DROP (`end = (i + span)`), because a slice stop past the array's end is clamped to its length; and L136 CMP_BOUND (`weight >= 0`), because the line above has already returned `neutral` for every |weight| < 0.5, so 0.0 never reaches the comparison. Each is in tests/mutation_ledger/survivor_triage/slot_drivers.py/ with its reason.
Failing first: at 8b7a1cd5d, the head before this pass, the same 16 sites are `ADDED UNPINNED` (`python3 tests/mutation_table.py --base origin/main`, `16 of them added by this diff`).

The previous pass's solver, payload, sensor and card mutants were run at d4aa09ed2ad6. This pass changes no line they mutate. Its list is below.


Solver/payload mutants, each applied alone to the head and the why-now block of tests/features.py run (`python3 $SP/mutate.py`, a scratch driver applying the edit, running the block, restoring); 14 of 14 killed:
- M1 `_price_push` sign (`1 - 2r` -> `2r - 1`): FAIL "the cheapest step ... price_rank leads and pushes to run".
- M2 normalisation (`100.0 * push` -> `push`): FAIL "one weight per step per code, magnitudes summing to 100 or all 0".
- M3 away sign: FAIL "perturbation: away_floor_drop_c=3 reads away negative".
- M4 mold clip lower bound 0 -> -1: FAIL "control: a mold floor below the comfort floor pushes nothing" (survived before that control was added; the control is this PR's).
- M5 comfort sign: FAIL "a room below mid-band pushes comfort_floor to run".
- M6 forecast sign: FAIL "a cold spell ahead pushes the step now to run".
- M7 `why_now_at` no-drivers None branch deleted: FAIL "the plan is byte-identical with the drivers emptied; no why_now then", FAIL "why_now_at is None with no drivers, past them, or on an unknown price".
- M8 unknown-price None branch deleted: FAIL "why_now_at is None ...".
- M9 neutral threshold `<` -> `<=`: FAIL "|weight| under 0.5 is neutral".
- M10 sort ascending: FAIL "price_rank leads", FAIL "drivers are sorted by magnitude".
- M11 `_apply_result_payload` presence test -> unconditional copy: FAIL "_apply_result_payload copies why_now, and leaves the key absent without one".
- M12 `away.floor_drop_c` arithmetic reversed: FAIL "away.floor_drop_c is 3 active, None recovering or off".
- M13 holiday drop disabled: FAIL "a holiday step on the night floor reads the 0.5 C drop".
- M14 `step_reasons` drops why_now: FAIL "price_rank leads and pushes to run".
Sensor: `SpaceHeatingPlanSensor` override returning `attrs` alone -> tests/entities.py FAIL "R10-WHY-NOW-WIDGET: the space plan publishes why_now; the DHW plan does not; none without one" (1 of 2641).
Card mutants on heatpump-optimizer-card.js against tests/card.mjs (`python3 $SP/mutate_card3.py`, same scheme), 9 of 9 killed: C1 marks swapped, C2 unknown codes kept (the `knownCodes` call bypassed), C3 all-neutral line gone, C4 block hover gone, C5 sign dropped, C6 no-data line gone, C7 block not mounted, C8 `breakdownRow`'s muted class inverted (13 failing, including the score panel's "a measured part gets its bar and value": the shared row is pinned from both callers), C9 direction phrases swapped ("each row names its direction in words"). C6 survived once the brief's metric text (which itself says "No data") went into the hover; the no-data and all-neutral checks now read the rendered line, and C6 is killed.
Failing first: the why-now block of tests/features.py against the base production files fails at import (`ImportError: cannot import name 'slot_drivers'`); tests/card.mjs against the base card: every why-now check FAILs (6 at the time of that run; the direction-phrase check was added after).


## Null control

- Unmutated tree: `PYTHONPATH=tests/hastub python3 tests/features.py` at 3a4dc75f1e86 reads ALL 4924 FEATURE CHECKS PASSED, including all 22 why-now checks. The pin run's own null control (`slot_drivers.py:27 NULL_COMMENT`, a comment-only edit) survived every driver it ran.
- The previous pass's null controls were measured at d4aa09ed2ad6 and are re-read at this head by the features checks above: flat prices, mid-band room and flat weather give every weight 0.0 and every row neutral; with `space_drivers` patched to return {}, `power_schedule` is unchanged; a mold floor below the comfort floor gives `mold_guard` 0; `away_floor_drop_c` None gives `away` 0. The P9 base-walk and fixed-walk control is as recorded at d4aa09ed2ad6.

## Figures

- Ratchet: `python3 tests/mutation_table.py --base origin/main` at b62b49ab9 reads `2877 unpinned site(s) of 6886 candidate sites, 2882 at the ratchet base 630bf533d838...; the ledger agrees with the deterministic inventory`. It read the same at 3a4dc75f1e86 against 136e835c35a2. No site is ADDED UNPINNED. At 8b7a1cd5d the same command refused with 16 added. Rule: the instrument's unpinned-site count, compared with the ratchet base's.
- Pin run: `python3 tests/mutation_table.py --pin-killed --base origin/main` read `PIN KILLED: 14 pinned, 2 left unpinned (2 survived ...)`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D` printed `MODE: SCOPED -- 28 script(s) run, 5 scoped out` at 3a4dc75f1e86 (merge base 136e835c35a2) and again at b62b49ab9 (merge base 630bf533d838).
- Scoped gate: `GATE_SCOPE=auto PYTHONPATH=tests/hastub bash tests/run.sh` at 3a4dc75f1e86 printed `MODE: SCOPED -- 28 script(s) run, 5 scoped out.` and `1 TEST SCRIPT(S) FAILED`. The failure is `tests/golden.py` under `GOLDEN_MODE=strict` (55 of 56 scenarios changed, only config_flow identical). The previous pass measured the same 55-of-56 strict result against the base's committed files on this box: value-only BLAS drift, the class claimed_drift.txt's header describes. Drift mode is clean: tests/env_drift.py, both modes, read ok in the same gate run. The other 27 scripts read ok.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: ALL 2643 ENTITY CHECKS PASSED at 3a4dc75f1e86; re-run at b62b49ab9 because main's delta changes it: ALL 2644 ENTITY CHECKS PASSED.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED at 3a4dc75f1e86 and at b62b49ab9.
- `python3 -I tools/audit/carry_audit.py check --body <this body>`: `CARRY-AUDIT: 0 finding item(s)` (Forward-carry below holds two dismissals and no finding item).
- Claim files: three-dot `git diff 630bf533d838...HEAD -- tests/golden/claimed_drift.txt` is empty. `tests/golden/card_claimed_drift.txt` carries the previous pass's `score_open` claim (+5 lines, the one card state that moved), which this pass did not touch. VERSION, the manifest version and RELEASE_NOTES.md are untouched.
- From the previous pass, measured at d4aa09ed2ad6, before the merge of main: `node tests/card.mjs` all passed; `node tests/card_drift.mjs` 1 state moved and claimed, 44 identical; `python3 tools/audit/archscore/score.py --diff 80016a71f567` printed `Architecture score: dS +0.0000 NULL`; `NODE_PATH=/opt/node22/lib/node_modules PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers HPO_BROWSER_SCOPE=full node tests/card_browser.mjs` printed ALL BROWSER CHECKS PASSED; and the forecast-scale rule on the two winter goldens saturated 0 of 96 steps. Re-run at 3a4dc75f1e86 by the scoped gate: card.mjs, card_drift.mjs, optimality.py and typing_ruler.py read ok.

## Unpinned sites

none: step 6d lists no added unpinned site at b62b49ab9. Of the 16 the red named, 14 are pinned under tests/mutation_ledger/killed_by/slot_drivers.py/ by this pass's `--pin-killed` run on this head, and 2 are under tests/mutation_ledger/survivor_triage/slot_drivers.py/ (`_forecast_push.CLAMP_DROP.5b2bbfd2`, `_direction.CMP_BOUND.23463a3d`, verdict equivalent). The 33 that mutation-autofix pinned at 8b7a1cd5d keep their rows.

## Red checks

- `tests / mutation` red twice at 8b7a1cd5d (job 128340143256 in run 42350619717, and job 128356124134 in run 42350614102): `MUTATION TABLE REFUSED -- 16 unpinned site(s) added by this diff`. Class: real survivors. The bot's one pass had pinned the 33 sites a driver already killed, and mutation-autofix does not re-run on its own commit, so the other 16 had no killing check. Answer: this pass adds the checks and pins 14 (`pinned`: `--pin-killed` ran on this head), and records 2 as equivalent. Cheaper detector: prepr.sh step 6d already lists added unpinned sites locally, and the previous pass named them as predicted. What it cannot tell apart is a site some driver already kills and one that no driver kills, and only the pin drive can (minutes per mutant). So no cheaper detector exists.
- `governance / instrument-self-tests` cancelled at 8b7a1cd5d (job 128340143345, run 42350619717): superseded when run 42350614102 started on the same head; that run's job 128356124083 was still in progress at the one check-runs read. Class: cancellation, not a failure. Answer: none owed.
- `tests / mutation` red at 0260beb41 (job 128303788367): the same 49 then-unpinned sites, before mutation-autofix's pass. Class: predicted, as the previous body named it. Answer: the same as the bullet above.
- `tests / mutation-autofix` red at 0260beb41 (job 128335810798): `mutation-autofix: changed -- 16 added site(s) left alive`, which are the same 16 sites. Class: a survivor is red by design (ci-autofix.md). Answer: the same as the first bullet. Cheaper detector: none; it is the detector.
- `governance / policy-docs` red at 0260beb41 (job 128303788457): `SELF-TEST FAILED SessionStart .claude/hooks/session-start.sh 23 passed, 1 failed`. Class: inherited from main. The branch changes no file under .claude/, and the next head, 8b7a1cd5d, which carried main's session-start.sh change through the merge at a9a4724bf, read `governance / policy-docs` success (job 128356124119). Answer: none owed by this diff; main's own PR owns that hook.
- `gate` red at 8b7a1cd5d (jobs 128368038019 and 128371889117): `FAIL tests / mutation: failure (this run)` plus pr-contract. Class: downstream of the mutation red and the body's stale-tree refusal. Answer: cleared with them; no edit-run deferral is owed, because the gate's own log names no deferral.
- `pr-contract / pr-contract` red at 8b7a1cd5d (jobs 128365328341 and 128371723858): the body at that head named the earlier tree (`NOTE stale tree ... lacks origin/main 601b9695`) and carried no answer to the mutation red. Class: a stale body. Answer: this body is re-taken whole at b62b49ab9.

## Forward-carry

- The note's docs/img plan named only make_card_figures.mjs. Any headline change also moves the tile and Plan-page figures, which card_browser.mjs's P40 already refuses, so no stage owes a brief edit. Carry: dismissed: P40 already enforces it on every branch
- The verdict's r3-d expected coord_* drift, but the coord captures never solve, so a why_now key cannot reach them. Carry: dismissed: this group's own note, closed by this measurement

## Friction

- handoff-wip: stale: the step ref `refs/heads/handoff-wip/r10-why-now-widget` still held an earlier session's history (4d318d4bb), which is not an ancestor of 8b7a1cd5d. This seat's harness refused deleting it, so the step pushes could not fast-forward and none was made; the branch's only pushes are the return refs. Carry: dismissed: the brief's own end-of-run delete clears it
