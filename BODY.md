R10-UX-HEALTH part 2: the residual after #2976. Part of #2809, Part of #2499.

What lands:

- **Hover spec (carry 14), the Health model rows.** Each model row's hover
  (`healthModelTitle` in the card) is now the metric in plain words, then the
  row's current reason: its learner phase, its evidence, or its COP reason.
  The rows were the metric title alone. `health.metric_lower`, `_tank` and
  `_gains` (en, sv) now also say what no data means. The other three already
  did.
- **#2809.** `DebugFinalizeButton.extra_state_attributes` names
  `debug_collect_start` for a finished collection. That is the action's
  `start`, the way out. The option-off case keeps `debug_collect`. Home
  Assistant drops attributes while the button is unavailable, so the card's
  Health debug row (`health.debug_final`, from #2976) stays the visible
  surface.
- **Card test gaps (carry 5).** `tests/card.mjs` pins the render that
  `openSetupSlot` must follow its state change with. It also drives the Configure
  chip's place-name fallback through a real Setup render.

What does not land, and why:

- **Carry 17, the P9 storage reset, is withheld.** It is measured, and the
  result needs an after-edge outside this group's seam. See Forward-carry.
- **The "driving scale" (carry 14), not built.** My reading is the headline
  score's third sub-score, `score.label_operation` = "Driving" (en) /
  "Körningen" (sv). It sits in the same hover as the House and Heat pump grades
  the owner names (`scoreParts`, `scoreDrivers` in the card). The card's own
  comment on `score.part_operation` reads "Driving: whether the plan buys at
  the cheap hours". Evidence that it lacks the owner's factor list: `scoreDrivers` reads
  `attrs["<key>_drivers"]`, and the backend publishes only `envelope_drivers`
  (`coordinator.py`, the `envelope_drivers` payload key, #2816).
  `grep -n operation_drivers custom_components/heatpump_optimizer/*.py`
  returns nothing. So the Driving part never shows "each factor pushing it,
  its direction and rough weight", and neither does Heat pump. Building that is a
  backend driver list plus card copy, outside this seam. The carry requires
  the orchestrator to confirm the widget first, so it is not built here.
- **#2499 stays open.** See Figures: the no-meter arm still books about 1.9x
  what it delivers. The Health line "Not observable without a power meter"
  (`health.model_unobservable`) landed in #2976. The over-booking figure is
  not met, so this body closes nothing.

Design choices:

- **The fallback case withdraws a map entry.** The Setup boxes are a literal
  list in `setupSvgHtml`: outdoor, heat_pump, wood_tank, mixing_valve,
  buffer_tank, dhw_tank, upper_zone, lower_zone. All eight are keys of
  `SETUP_CONFIGURE_PAGE`. A slot whose place is not in that list is dropped
  by `slotsAt`, so no topology reaches the fallback; the brief's "topology
  whose place is outside" cannot be built. The case instead deletes
  `wood_tank` from the live map for one render and restores it. That is the
  case the fallback guards: a box added without its page.
- **One owner for the hover.** `healthModelTitle` is used by both
  `healthModelRow` and `healthGainsRow`, so the gains row cannot drift from
  the others. Alternative considered: append the reason at each of the six
  call sites. It lost because it spells the rule six times.

## Head

31da5f026563cbf2091b2e5e87005607b9d4cbfb, cut from origin/main
507a9ec264eb373b132248d752259254d8a9fa4d (merge base; main's tip at
2026-10-30T13:33Z).
The tests and mutants ran at 855d1bbac6b04e4675fc93c4db4dabbb68dedca7. The
head commit after it only deletes the three stale ledger pins under
`tests/mutation_ledger/killed_by/button.py/`, as `body_push.sh`'s predictor
required.

## Mutation proof

Each mutant is one line in a worktree at the head. `node tests/card.mjs` or
`python3 tests/debug_collect.py` was run, then the line was restored.

- Drop `host._render();` from `openSetupSlot` → FAIL `openSetupSlot renders
  the page it opens`. The existing `Assign redraws the dialog on the Setup page`
  also goes red, so this mutant was already killed at base. The carry's
  "unpinned at base" does not hold at this base; the new case pins it at the
  function rather than through the Advisor press.
- `b.cfgPage = page ? L(page) : placeLabel(b.place);` → `b.cfgPage =
  L(page);` → FAIL `P08/P41: the Configure chip of a place with no options
  page names the place, never undefined`.
- `healthModelTitle` returns `L(\`health.metric_${id}\`)` alone → FAIL
  `hover spec (en)…` and `hover spec (sv)…`.
- `button.py`: the final branch returns `{"waiting_for": "debug_collect"}` →
  FAIL `the finalize button on a finished collection names the action's
  start, not the option that is already on`. Output: `1 of 159 DEBUG COLLECT
  CHECKS FAILED`.

## Null control

Unmodified tree: origin/main at the merge base, with this head's
`tests/card.mjs` copied in.

- `node tests/card.mjs` fails exactly `hover spec (en)` and `hover spec (sv)`:
  the defect. The openSetupSlot and fallback cases pass at base, because they
  pin behaviour the base already has.
- The #2809 check fails at base by construction, because the base is the
  mutant above.
- The hover case enumerates every `data-model-row` the page draws. It asserts
  the count is 6, so a seventh row without the two parts fails it, and so does
  a row dropped from the fixture.

## Figures

- Scoped gate, `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`:
  `MODE: SCOPED -- 16 script(s) run, 17 scoped out.` Each of the 16 was run
  at the head with `PYTHONPATH=tests/hastub` and passed. Their summary lines
  are in Gate.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- #2499, `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_demand_overbook.py`
  at the head, arm `nometer_half`: `scale 1.858` (true 1.0) and `plan/deliv
  1.908`. The null arm reads `plan/deliv 1.165`; `meter_half_oracle` reads
  1.016. This head changes no learner or optimizer line, so the figure is the
  base's. The carry recorded 1.828 / 1.936 at d6ab12b4; the drift is the
  solver's environment, not a change. Over-booking on a no-meter install is
  not met.
- P9 grid, `node tests/card_browser.mjs` with `P9_DEBUG=1`, at the merge base
  with and without the storage reset (`localStorage.clear(); sessionStorage.clear()`
  after each `page.goto` in `p9Grid`):
  - Without the reset, all browser checks pass: 850 box-intersecting pairs
    inked.
  - With the reset, 1190 pairs are inked, and `P9 grid: no two text runs
    share ink` FAILs with 30 entries.
  - The 30 entries are 15 in `wood_alert` and 15 in `wood_lane`, all at 375
    px. That is 3 pairs in each of the five 375-px cells: light/en,
    light/sv-SE, dark/en, dark-on-light, light-on-dark. Each cell has text
    "0" x "1" (4 px), "1" x "2" (2 px) and "2" x "3" (4 px).
  - The rule: `P9_DEBUG`'s `overlap` array, counted by the cell prefix of
    each entry.

## Gate

At the head, one run per script that `scope.run` names. `card.mjs` and
`card_drift.mjs` take the plan payload `tests/plan_view.py` writes.
- `tests/arch_score_head.py`: exit 0, `ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED`
- `tests/config_flow_steps.py`: exit 0, `ALL 534 checks PASSED`
- `tests/debug_collect.py`: exit 0, `ALL 159 DEBUG COLLECT CHECKS PASSED`
- `tests/deployment_shape.py`: exit 0, `ALL DEPLOYMENT SHAPE CHECKS PASSED`
- `tests/doc_claims.py`: exit 0, `ALL 203 checks PASSED`
- `tests/entities.py`: exit 0, `ALL 2484 ENTITY CHECKS PASSED`
- `tests/env_drift.py`: exit 0, `NO STALE FIXTURE: 5 committed fixture(s) still match what this tree computes`
- `tests/features.py`: exit 0, `ALL 4605 FEATURE CHECKS PASSED`
- `tests/finite_boundary.py`: exit 0, `ALL 108 FINITE BOUNDARY CHECKS PASSED`
- `tests/golden.py`: exit 0, `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`
- `tests/harness_headers.py`: exit 0, `ALL 112 HARNESS HEADER CHECKS PASSED`
- `tests/plan_view.py`: exit 0, `plan reason codes, price provenance and slot energy OK`
- `tests/card.mjs`: exit 0, `ALL CARD CHECKS PASSED`
- `tests/card_drift.mjs`: exit 0, `card_drift: identical in all 45 states`
- `tests/structure.py`: exit 0, `STRUCTURE RATCHET PASSED`
- `tests/typing_ruler.py`: exit 0, `ALL 12 typing-ruler source checks PASSED`

## Unpinned sites

The #2809 rewrite deletes three ledger pins: `RETURN_DEL.3dca65c8`,
`GUARD_OFF.85c924c9` and `BOOLOP.85c924c9` on the old guarded line. The
predictor named them as stale, so they are removed by hand.

`mutation_table.py --pin-killed` and `--anchor` both refuse on this diff
(`no full-line comment in any file in the pool`: `button.py` has no short
whole-line comment to carry the null control), so the three mutants were
driven by hand against `tests/debug_collect.py`: baseline `ALL 159 DEBUG
COLLECT CHECKS PASSED`; each mutant applied to `button.py`, the script run
with `PYTHONPATH=tests/hastub`, the file restored. All three are killed;
`mutation-autofix` records the ledger pin after the push.

- `custom_components/heatpump_optimizer/button.py:226 GUARD_OFF` (`if collector is None:` -> `if False:`): killed by
  `tests/debug_collect.py` (the next line raises `AttributeError` on `None`).
- `custom_components/heatpump_optimizer/button.py:228 GUARD_OFF` (`if collector.final:` -> `if False:`): killed by
  `tests/debug_collect.py` (1 of 159 checks failed, the finalize button on a
  finished collection).
- `custom_components/heatpump_optimizer/button.py:230 RETURN_DEL` (`return {}` -> `pass`): killed by
  `tests/debug_collect.py` (2 of 159 checks failed).

## Red checks

No check went red on this branch except as below. The P9 reset, which would turn
`tests / browser` red, is withheld rather than handed off red.
- `mutation` at 31da5f026563: red by construction on the 3 site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push.

## Forward-carry

- **P9 grid state leak (carry 17), with the collision it hides.**
  - `p9Grid` mounts every state of a cell in one browser context. The
    `hidden_series` state's chip press (`["chip", "price"]`) persists in
    localStorage into the later states, `wood_alert` and `wood_lane`
    among them.
  - With a reset after each `page.goto`, those two states at 375 px read the
    30 shared-ink pairs above, at the base.
  - Inference, not measured per element: the colliding runs are drawn once
    the price series is visible, the only state the leak carries. The likely
    owner is a chart axis's tick labels at narrow width.
  - Fixing that is a chart hunk in the card, which this group's architect note
    keeps to the Health and Setup seams. It needs the orchestrator's
    after-edge.
  - The reset (four lines in `p9Grid`) must land in the same PR as that
    fix, or `tests / browser` goes red. Carry: R10-UX-HEALTH
    (dev/programme/rosters/wave-r10-groups.json on handoff/audit-r10-roster)
    (R10-UX-HEALTH; orchestrator assigns the chart seam).
- **The "driving scale" widget.** The reading and evidence are above: the
  headline score's "Driving" sub-score. Neither `operation_drivers` nor a
  heat-pump driver list is published. The owner's spec needs the owner or
  orchestrator to confirm the widget, then a backend driver list and the
  card copy. Carry: R10-UX-HEALTH
    (dev/programme/rosters/wave-r10-groups.json on handoff/audit-r10-roster)
  (R10-UX-HEALTH; orchestrator confirmation).

## Friction

- `fixer-brief: contradiction`: residual item 1 asks for a topology whose
  place is outside `SETUP_CONFIGURE_PAGE`. The card's box list is literal and
  all eight places are in the map, so no topology reaches the fallback. The
  case withdraws a map entry instead. Carry: R10-UX-HEALTH
    (dev/programme/rosters/wave-r10-groups.json on handoff/audit-r10-roster)
  (R10-UX-HEALTH).
- `fixer-brief: stale`: carry 5 says dropping the render from
  `openSetupSlot` is unpinned at base. At 507a9ec26 it is killed by `Assign
  redraws the dialog on the Setup page`. Carry: R10-UX-HEALTH
    (dev/programme/rosters/wave-r10-groups.json on handoff/audit-r10-roster)
  (R10-UX-HEALTH).
