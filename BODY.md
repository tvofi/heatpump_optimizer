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

7fed51072fac2bef5068d53e618ba4ba308eda46, a fast-forward of the reviewed
head 7c43d8fb1505320e2b10d7c122dab3215ebd085c by one commit that adds the
three `killed_by` rows under `tests/mutation_ledger/killed_by/button.py/` and
nothing else. Merge base e77418f9b48f89421bd72b0ab511c057341c7fa4. origin/main
was at 3fc19b0f6e375793fcbc71d7f88232b173b0604f at 2026-10-30T14:55Z;
`git merge-tree --write-tree origin/main HEAD` exits 0 (no conflict), so main
was not merged in (`fixer.md` step 6). The tests, mutants and gate in this
body ran at 7fed51072.

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

- Mutation rows, `python3 hand_pin.py` (scratch; drives the three sites
  with `mutation_table.inventory`, `anchor_sites`, `killed`, `pin_entry`):
  baseline `tests/debug_collect.py` rc=0 failed=0 (`ALL 159 DEBUG COLLECT
  CHECKS PASSED`); null control button.py:43 rc=0 failed=0, `killed=False`;
  226 GUARD_OFF rc=1 failed=1, 228 GUARD_OFF rc=1 failed=1, 230 RETURN_DEL
  rc=1 failed=2, each `killed=True`. Had a site lived, `killed` would read
  False and no row would be written (the script writes only on True).
- Sites in scope, rule: `inventory([button.py])` filtered to lines 225-230
  of `DebugFinalizeButton.extra_state_attributes`: 3 sites, the 3 above. The
  CI lane's own enumeration agrees: `3 mutant(s) over 1 file(s)` in the
  local `--scope changed` run.
- Unpinned count, `python3 tests/mutation_table.py --scope changed --base
  origin/main --max 10 --jobs 3` at 7fed51072: `3620 unpinned site(s) ...
  3620 at the ratchet base`; at 7c43d8fb1 the reviewer's run read 3623, so
  the ratchet arm separates the two heads. rc=1 on the null-control refusal.
- Scoped gate, `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`:
  `MODE: SCOPED -- 16 script(s) run, 17 scoped out.` Each of the 16 was run
  at 7fed51072 with `PYTHONPATH=tests/hastub` and passed. Their summary lines
  are in Gate.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- #2499, `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_demand_overbook.py`
  re-run at 7fed51072, arm `nometer_half`: `scale 1.858` (true 1.0) and
  `plan/deliv 1.908`. The null arm reads `plan/deliv 1.165`;
  `meter_half_oracle` reads 1.016. Round 1 read the same three at 855d1bbac.
  This head changes no learner or optimizer line, so the figure is the
  base's. The carry recorded 1.828 / 1.936 at d6ab12b4; the drift is the
  solver's environment, not a change. Over-booking on a no-meter install is
  not met.
- P9 grid, not re-taken in round 2 (this round adds only ledger rows; no card or browser-test line moved since round 1, which measured it at its merge base 507a9ec26), `node tests/card_browser.mjs` with `P9_DEBUG=1`, at that merge base
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

At 7fed51072, one run per script that `scope.run` names, with `PYTHONPATH=tests/hastub` and `GOLDEN_MODE=drift`. `card.mjs` and `card_drift.mjs` take the plan payload `tests/plan_view.py` writes.
- `tests/arch_score_head.py`: exit 0, `ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED`
- `tests/config_flow_steps.py`: exit 0, `ALL 534 checks PASSED`
- `tests/debug_collect.py`: exit 0, `ALL 159 DEBUG COLLECT CHECKS PASSED`
- `tests/deployment_shape.py`: exit 0, `ALL DEPLOYMENT SHAPE CHECKS PASSED`
- `tests/doc_claims.py`: exit 0, `ALL 203 checks PASSED`
- `tests/entities.py`: exit 0, `ALL 2488 ENTITY CHECKS PASSED`
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

Round 2. The three sites the #2809 rewrite adds now carry `killed_by` rows.

`mutation_table.py --pin-killed` still refuses this pool (`no full-line
comment in any file in the pool`): `null_control` takes only a whole-line
comment shorter than 60 characters, and every whole-line comment in
`button.py` is longer. So the three mutants were driven with the tool's own
functions instead, not with a copy of its rules: `inventory([button.py])`
for the sites and their `new` text, `anchor_sites` for the anchors,
`killed` (a red run naming more failing checks than the baseline, a
traceback counting one) for the verdict, and `pin_entry`/`ledger_relpath`/
`row_text` for the rows. Each row's `reason` says it was driven by hand and
why. The run carries the null control the tool could not find: button.py:43
(`# (parallel-updates, Silver): ...`) plus ` (null control)`, driven through
`tests/debug_collect.py`, lived (rc=0, failed=0). `--normalize` leaves the
rows unchanged.

- `custom_components/heatpump_optimizer/button.py:226 GUARD_OFF` (`if collector is None:` -> `if False:`): killed by
  `tests/debug_collect.py`, rc=0 failed=0 -> rc=1 failed=1 (the next line
  raises `AttributeError` on `None`, which `failing_count` counts as one).
  Anchor `GUARD_OFF 88fa31c4`.
- `custom_components/heatpump_optimizer/button.py:228 GUARD_OFF` (`if collector.final:` -> `if False:`): killed by
  `tests/debug_collect.py`, rc=1 failed=1 (the finalize button on a
  finished collection). Anchor `GUARD_OFF 7cf2cf8c`.
- `custom_components/heatpump_optimizer/button.py:230 RETURN_DEL` (`return {}` -> `pass`): killed by
  `tests/debug_collect.py`, rc=1 failed=2. Anchor `RETURN_DEL fc97300a`.

No site lives, so no test was added and no `-- lives` line is owed.

## Red checks

- `tests / mutation` at 7c43d8fb1: red, `MUTATION TABLE REFUSED -- 3623
  unpinned site(s) against 3620`. Cause: the round-1 handoff deleted the three
  stale pins and relied on `mutation-autofix` to record the new ones, which
  could not happen (below). Answer: the three rows in this head. Run locally
  at 7fed51072 with CI's command (`python3 tests/mutation_table.py --scope
  changed --base origin/main --max 10 --jobs 3`), the ratchet line now reads
  `3620 unpinned site(s) of 6579 candidate sites, 3620 at the ratchet base
  e77418f9b`. **It is still red**: the same run then stops at `MUTATION TABLE
  REFUSED -- no full-line comment in any file in the pool`, because its
  sampled lane draws only `button.py` sites and `null_control` finds no
  comment under 60 characters there. Pins cannot clear that arm; only an
  instrument change can (`tests/mutation_table.py`, code-owned by the owner),
  or a `button.py` comment written to fit the tool, which I did not add
  because it would shape the code to the grader. Not repaired in this head;
  see Forward-carry. The cheaper detector: `null_for` over the pool, which
  `prepr.sh` step 6d / `ci_predict.py` could run in seconds before the
  handoff; it does not today, so this refusal first shows in CI.
- `tests / mutation-autofix` at 7c43d8fb1: red, `AUTOFIX:
  skip-measure-failed -- THE REPAIR DID NOT HAPPEN`. Cause: it drives
  `--pin-killed`, which refuses the same pool for the same null-control
  reason, so no bot commit came. Answer: the rows were recorded here
  (`ci-autofix.md`: when mutation-autofix goes red, the repair is the
  seat's). The cheaper detector is the same `null_for` pre-check; round 1
  had already seen `--pin-killed` refuse locally and should have named this
  red instead of predicting the bot's commit.
- No other check went red on this branch. The P9 reset, which would turn
  `tests / browser` red, is withheld rather than handed off red.

## Forward-carry

- **The mutation null-control gap.** `null_control` in
  `tests/mutation_table.py` takes only a whole-line comment under 60
  characters, a cap with no recorded reason (2fe38a487). A pool whose files
  hold none -- `button.py` at this head -- refuses both `--pin-killed` (so
  `mutation-autofix` goes `skip-measure-failed`) and the sampled lane of
  `tests / mutation`, so a pull request touching only such a file cannot go
  green whatever it pins. A fallback to any whole-line comment is safe: the
  null control fails closed if a driver notices it. The file is code-owned,
  outside this group's seam, so it is not changed here; this PR needs that fix
  merged first, or the orchestrator's call. `ci-autofix.md`'s table also omits
  this case. Carry: R10-UX-HEALTH
    (dev/programme/rosters/wave-r10-groups.json on handoff/audit-r10-roster)
  (R10-UX-HEALTH; orchestrator assigns the instrument fix).

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
