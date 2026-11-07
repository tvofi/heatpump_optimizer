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

**P9 clip check (carry 7c609975).** `unreachable()` in tests/card_browser.mjs starts its walk at `run.el`, so a run clipped by its own box is reported.

**Forecast scale.** Kept at 10 °C: on the winter goldens no step of 96 saturates (rule below).

Alternatives the note weighed (second current-step search, coordinator-side derivation, re-solves, weights in reason strings, `scoreDrivers` reuse) lost for the note's reasons; nothing here revisits them.

## Head

a9a4724bfb3ef59503d75a4cf98a0e8b3834b9ea: the merge of origin/main f2a015142714383722bf49d7ab20d8398ec9674c (taken 2026-11-07T02:02Z) into 597b79fbce97dd9af0303e437a214d50db2f3056. Every figure below was measured at 4d318d4bba14, whose tree is 597b79fbce97dd9af0303e437a214d50db2f3056's byte for byte (that commit was re-made only to carry the hpo-fixer identity on one commit that had been written as the cloud seat's default). Main's delta since the base 80016a71f567 touches .claude/hooks/session-start.sh, .github/workflows/governance.yml, dev/governance/roles/nudge.md, dev/programme/delivery/, tools/audit/seat/ and tools/policy/role_pack.py: no production, test, card, golden or closure file this diff's figures read, so they stand; tools/pr/prepr.sh was re-run at a9a4724bfb3ef59503d75a4cf98a0e8b3834b9ea.

## Mutation proof

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
Card mutants on heatpump-optimizer-card.js against tests/card.mjs, 8 of 8 killed: C1 marks swapped, C2 unknown codes kept, C3 all-neutral line gone, C4 block hover gone, C5 sign dropped, C6 no-data line gone, C7 block not mounted, C8 `breakdownRow`'s muted class inverted (13 failing, including the score panel's "a measured part gets its bar and value": the shared row is pinned from both callers).
Failing first: the why-now block of tests/features.py against the base production files fails at import (`ImportError: cannot import name 'slot_drivers'`); tests/card.mjs against the base card: 6 why-now checks FAIL.

## Null control

- Flat prices, room mid-band, flat outdoor/wind/sun over the 8 h window: every weight 0.0 and every row neutral (features check "null control"); the card renders the one all-neutral line for that shape.
- `slot_drivers.space_drivers` patched to return {}: `power_schedule` equal to the unpatched solve's (invariant 1, the drivers are never written back).
- A mold floor below the comfort floor: `mold_guard` 0 on every step; `away_floor_drop_c` None: `away` 0.
- tests/optimality.py at base and head: output identical (timing lines excluded), 84 checks passed both ends.
- tests/env_drift.py --all against the merge base: 56 scenarios, no unclaimed drift, no stale fixture.
- tests/card_drift.mjs: 44 states identical, `score_open` the one moved and claimed.
- P9 control: card_browser.mjs on the head card under the base's walk (`parentOf(run.el)`) and under the fixed walk (`run.el`): P9 passes with no clipped run under both, so the fix newly reports nothing on the real card. Perturbation: the block heading given `overflow:hidden; width:12px`: the base walk passes P9; the fixed walk FAILs naming `span.sb-name "Why now"` and `"Varför nu"` (45.5 px and 38.3 px, both themes' widths).

## Figures

- Gate scope: `python3 tests/closure.py select --diff 80016a71f567 --workdir $D` printed `MODE: SCOPED -- 28 script(s) run, 5 scoped out`.
- Scoped gate: `GATE_SCOPE=auto PYTHONPATH=tests/hastub bash tests/run.sh`: red on tests/golden.py and tests/entities.py at 1b0f46a86; entities.py's one failure (deployment_shape.py's note citing 103 files and 144 pairs) is fixed in this branch and `python3 tests/entities.py` now passes 2641 of 2641; golden.py's strict mode reads 55 of 56 scenarios changed against the committed files at the base too (`GOLDEN_MODE=strict python3 tests/golden.py` at 80016a71f: exit 1, same count), value-only BLAS drift on this box, the class claimed_drift.txt's header describes; drift mode is clean (env_drift line above).
- `python3 tests/features.py`: all 4891 checks passed; the why-now block is 15 of them.
- `node tests/card.mjs`: all card checks passed.
- `node tests/card_drift.mjs`: 1 state moved and claimed, 44 identical.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, no budget touched.
- `python3 tools/audit/archscore/score.py --diff 80016a71f567`: `Architecture score: dS +0.0000 NULL`.
- `python3 tests/typing_ruler.py`: no growth (slot_drivers.py typed: the census read 3, then 1, then 0).
- `python3 tests/harness_headers.py`: 112 of 112 (dev/audit/rounds/round4/D6/claims.py's header follows the module count, 85 -> 86 on disk and listed).
- `python3 tests/doc_claims.py`: 296 of 296 (docs/architecture.md: 86 modules, 57 HA-free, slot_drivers.py in the map).
- Closures: `tests/derive_closures.sh --scripts-from <the 27 scripts whose closure holds optimizer.py> --record-only`: 26 exit 0, entities.py exit 1 on the classification this branch supplies; every recording added slot_drivers.py and no other tracked file, so only that line is merged, 27 closures. `python3 tools/pr/ci_predict.py` then: no closures, fast, governance or instrument red predicted.
- Forecast scale: on tests/golden/winter_single_no_dhw.json and winter_two_zone_dhw.json, the outdoor and solar arms of the forecast push at /10 °C saturate on 0 of 96 steps (median |push| 0.17; /5 °C reads 0.34, still 0 saturated); rule: `clip((out_i - mean out[i:i+32])/scale - (mean sun - sun_i)/9)` over the fixture's own outdoor_temps and solar_gain_trajectory, the hlf arm omitted (fixtures carry no loss factors).
- Card figures: `node docs/img/card/make_card_figures.mjs` with the base card and with the head card: chart-anatomy.svg and chart-dashed-lines.svg byte-identical between the two.
- Browser: `NODE_PATH=/opt/node22/lib/node_modules PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers HPO_BROWSER_SCOPE=full node tests/card_browser.mjs` at 4d318d4bba14: ALL BROWSER CHECKS PASSED (P9 grid MODE: FULL, 360 cells, 'no text is clipped where its ancestor cannot scroll to it' ok; P40 ok). The light and dark themes and the phone and desktop widths are the grid's own cells.

## Unpinned sites

- custom_components/heatpump_optimizer/away.py:365 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/away.py:367 RETURN_DEL: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/away.py:374 CLAMP_DROP: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/away.py:374 RETURN_DEL: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/away.py:396 BOOLOP: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/away.py:396 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/coordinator.py:2942 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/optimizer.py:4029 CLAMP_DROP: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/optimizer.py:4036 RETURN_DEL: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/sensor.py:1611 RETURN_DEL: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:110 CLAMP_DROP: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:118 CLAMP_DROP: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:119 CLAMP_DROP: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:120 CLAMP_DROP: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:125 CMP_BOUND: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:134 CMP_BOUND: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:134 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:136 CMP_BOUND: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:136 RETURN_DEL: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:143 CMP_BOUND: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:144 CMP_BOUND: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:146 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:148 RETURN_DEL: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:155 CMP_BOUND: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:155 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:157 CMP_BOUND: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:157 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:159 BOOLOP: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:159 CMP_BOUND: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:159 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:168 RETURN_DEL: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:23 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:30 CONST: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:33 CONST: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:37 CONST: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:39 CONST: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:55 BOOLOP: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:56 BOOLOP: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:56 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:60 CLAMP_DROP: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:72 CMP_BOUND: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:72 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:74 CMP_BOUND: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:77 RETURN_DEL: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:84 CLAMP_DROP: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:90 CLAMP_DROP: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:94 CLAMP_DROP: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:96 CLAMP_DROP: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)
- custom_components/heatpump_optimizer/slot_drivers.py:96 RETURN_DEL: pinned by mutation-autofix (a custom_components/ site; the lane pins it once a killing check exists, and the mutants above kill this family)

## Red checks

- `mutation`: predicted red, not yet run (no pull request exists): the 49 sites under `## Unpinned sites` have no ledger pin until `mutation-autofix` records them after the PR opens (ci-autofix.md); the two ledger pins this diff staled (`solve_bands` GUARD_OFF ffad43d2, `_build_comfort_bounds` CLAMP_DROP 525de22f) are deleted here so that lane re-pins the rewritten lines. Cheaper detector: prepr.sh step 6d already predicts it locally in seconds, which is how it is named here; none cheaper exists.
- Locally, tests/golden.py's strict comparison is red at the base and the head alike on this box (value-only BLAS drift, Figures); this branch did not turn it red.

## Forward-carry

- The note's docs/img plan named only make_card_figures.mjs; any headline change also moves the tile and Plan-page figures, which card_browser.mjs's P40 already refuses, so no stage owes a brief edit. Carry: dismissed: P40 already enforces it on every branch
- The verdict's r3-d expected coord_* drift; the coord captures never solve, so a why_now key cannot reach them. Carry: dismissed: this group's own note, closed by this measurement

## Friction

none
