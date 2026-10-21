The Advisor's three owner items (#2257 items 6, 7 and 8) and the Advisor's
share of the deep-link class (#2253). Part of #2257, part of #2253 (the
roster's `fixes` is empty for this group, so the orchestrator closes them
after verifying each).

What the owner's screenshot (2026-10-14) named, and what answers it:

- **"A degree warmer costs -266 SEK/month more" beside "a degree cooler is
  cheaper ≈ 140" (item 8).** Two defects stacked. The degree tiles moved
  `target_temp` alone, while the plan heats to the comfort schedule
  (`comfort_temp_day`/`_night`), so a tile priced what `target_temp` still
  reaches (the settlement caps, the terminal value) and not a degree of
  comfort. And the figure was the plan's single-solve spend difference from
  the house as it stands, scaled to a month: a degree cooler books a one-off
  coast and a degree warmer a one-off heat-up, each multiplied by every
  horizon in the month. A degree tile now moves every comfort level the
  schedule has set (target, day, night, and the weekend and holiday
  overrides where set), and reads the thermostat baseline's difference
  (`monthly_held_cost_delta`): a degree held from a steady start, which the
  SAV-BASELINE settlement already starts held. Then the card checks the pair
  before rendering it: a cooler degree must save, a warmer one must cost, and
  the warmer must cost at least what the cooler saves (heat loss grows with
  the indoor-outdoor gap, so comfort's cost is convex), within the one unit
  two roundings open between a linear pair. A pair that fails renders as
  "Not shown yet" with no money and no "costs … more" sentence, and a degree
  that saves nothing either way (no heating) is no row.
- **The "worth doing" figures swing day to day (item 6).** Every tile is
  published as the mean of its daily means over the last 30 local days
  (`price_tiles.HORIZON_DAYS`), with `horizon_days` beside it, and the days
  persist with the ledger, so a restart does not start the mean over. The
  degree row says it is "a 30-day average".
- **"Open settings" does not deep-link (item 7, R10-DEEPLINK's helper).**
  Home Assistant has no URL into one options-flow step (R10-DEEPLINK's
  carry), so each enable-to-see row and the feedback-sensor row now name the
  step that turns it on (for example "Configure → Savings vs comfort" for the
  price of a degree, "Configure → Advanced settings → Power and solar
  sensors" for the feedback sensor), and the button opens this entry through
  `openHaLink(host, "options")`. They dispatch a new `open_options` act; the
  Health page keeps `settings`, which R10-UX-HEALTH converts.
- **Carried from R10-SAV-REASONS:** `REASON_LABELS` and the card's
  `reasons.*` strings now name `boost`, `comfort_mode`,
  `system_identification` and `untagged`, so the Savings receipt's by-reason
  bars stop printing the raw token; a census reads `payload.py`'s `REASON_`
  constants and refuses any code without a label.

**Why the held figure, and not the alternatives.** (1) The plan's own
single-solve delta with the schedule moved overstates (the `null` arm below:
+145.6 and +85.1 per degree against a realised +59.4). (2) Settling each plan's stored heat against its own
thermostat (`predicted_cost + deferred_energy_cost`, the SAV-BASELINE
figures) is honest for one plan but not across two schedules: each side is
settled against a different thermostat, and differencing them read wrong
signs in this seat's scratch probe, so it is not used and no figure from it
is claimed. (3) Settling the two plans' end states against each other at the
refill price read wrong signs in the same scratch probe, and is not used either. The held figure is
the one estimator here that is monotone by construction, carries no solver
noise (the `days` arm's two tiles are antisymmetric within 0.9 every day), and in the null reads the plan's realised price per degree it delivers.

**Architecture.** The tiles' state, perturbation set, sampling, horizon and
persistence moved out of the coordinator class into a new pure module,
`price_tiles.py`, whose per-coordinator side table (`boost.py`'s discipline)
holds the book; the coordinator hands the functions the book, never itself.
`_price_tile_specs` and the `_price_tiles` attribute are gone (seam map entry
removed). That paid for the additions: `max_class_loc` 8541 -> 8514,
`class_excess_loc` 18299 -> 18272, `coordinator_attrs` 148 -> 147,
`seam_cut_total` 718 -> 710, re-recorded with the reason in the commit.

## Head

`cd1c837cabe9536b27a7d36d193d5f4e24d23deb` is the measured code head. Merge base
`265d3bf1acc1f52b838c52f3393db2296e59efa6`, which was origin/main's tip when
the branch merged it (`16f9c4a86`, before any figure below was taken).
origin/main's tip at the last measurement was `3688cf25977ca71b4406be942df9592577d9b42e`
(2026-10-21T12:42Z, `date -u`), whose commits past the merge base touch only
`dev/programme/delivery/` and `tools/audit/seat/cloud_dispatch.py`. At handoff
(2026-10-21T14:29Z) it is `5d433771a`, which adds orchestration tooling under
`tools/audit/seat/` and `tools/policy/`, `.github/workflows/governance.yml`,
`dev/governance/roles/orchestrator.md` and delivery rows, none of them a file
this diff touches; `git merge-tree --write-tree origin/main HEAD` merges clean
against both tips.

Where a figure was taken at an earlier commit of this branch, it names it,
and the diff from there to the head is stated:

- `f2766fd4d` -> head: no Python under `custom_components/`; the card's
  reason labels and their `tests/card.mjs` checks, the card claim, the D6
  header count and outputs, the deployment-shape docstring's file count, and
  `tests/closures.json`.
- `4eaec5793` -> head: the deployment-shape docstring, `tests/closures.json`,
  and `price_tiles.sample` renamed `monthly_figure` (its callers in
  `tests/features.py` and the harness with it).

## Mutation proof

Each mutant is one production-line replacement in a detached worktree of its
own, run through the closure named; a check named is one that went red.

| mutant | cut at | production line replaced | closure | red |
|---|---|---|---|---|
| MC1 | `187134aff` | `degreeRow`'s check `save > 0 && cost > 0 && cost >= save - 1` -> `true` | `node tests/card.mjs` | `the screenshot's pair (-140 cooler, -266 warmer) renders no money and no "more"`; `a warmer degree cheaper than the cooler one saves is not convex, so not shown`; `two units below the saving is concave, not rounding`; `a degree that saves nothing either way (no heating) is no row`; `a degree cooler that costs more is not shown as a saving` |
| MC2 | `187134aff` | the rounding allowance `cost >= save - 1` -> `cost >= save` | `node tests/card.mjs` | `a linear pair the two roundings open by one unit is still convex` |
| MC3 | `187134aff` | `open_options` -> `navigateTo(SETTINGS_PATH)` (the bare link) | `node tests/card.mjs` | `Open settings on an opt-in row links this entry's options, not the bare integration`; `every link the census records from a press is one haLink builds for this entry` |
| MC4 | `4eaec5793` | the `boost` entry deleted from `REASON_LABELS` | `node tests/card.mjs` | `UX-6: boost, comfort mode, step-response and unattributed money are named on the receipt`; `every reason code payload.py publishes has a card label (idle sub-codes aside)` |
| MB1 | `187134aff` | `specs`' degree -> `target_temp` alone (the merge base's perturbation) | `python3 tests/features.py` | `#2257: a degree tile moves every comfort level the schedule has set, and no other`; `#2257: every level a degree moves is one the what-if applies to its scratch config`; `#2257: at the real what-if seam a degree cooler saves and a degree warmer costs, convexly` (held 0.0 / 0.0; the plan's single-solve figures +2.05 / +0.92); `UX-5 the price tile and the card's what-if both price the active setback` |
| MB2 | `187134aff` | `monthly_figure` (named `sample` at that commit) reads `monthly_cost_delta` for every tile | `python3 tests/features.py` | `one solve refreshes exactly one tile, in rotation`; `#2257: a degree tile reads the held figure, the cap tile the plan's`; `#2257: at the real what-if seam …` (+41.39 / +156.04: a cooler degree that costs more); `an errored answer advances the cursor but publishes nothing; a good one publishes` |
| MB3 | `187134aff` | `published` reads the last day only (`_within(...)[-1:]`) | `python3 tests/features.py` | `#2257: a tile keeps the last 30 local days and publishes the mean of their daily means` |
| MB4 | `187134aff` | `restore` admits a tile's days all or none | `python3 tests/features.py` | `#2257: a stored tile loads day by day …` |
| MB5 | `187134aff` | `monthly_held_cost_delta` from `predicted_cost` (the plan's spend) | `python3 tests/features.py` | `#2257: at the real what-if seam …` (+25.16 / +148.33) |

Every mutated line is byte-identical at `cd1c837ca`: `git diff 187134aff
cd1c837ca -- custom_components/` is the deleted error guard in
`_maybe_refresh_price_tile`, `per_month`'s deleted clamp, the `sample` ->
`monthly_figure` rename (its `def` line and one call) and the card's reason
labels, and none of those lines is one a mutant replaced. The real-seam figures move between MB1, MB2 and MB5 because
`_solve_coord` anchors its horizon on the real clock; each run reads its own.

## Null control

- **The unmutated tree passes**: `python3 tests/features.py` ->
  `ALL 4276 FEATURE CHECKS PASSED` and `node tests/card.mjs` -> `ALL CARD
  CHECKS PASSED` (Figures).
- **The owner's null (carry 1, and SAV-BASELINE's restatement): a flat price
  and a constant outdoor temperature**, where the plan has no timing to buy.
  `r10_advisor_degree.py null` runs closed loops at the schedule moved -1, 0
  and +1 K and reads the plan's realised cost per degree it delivers:
  +59.4/month on both sides, against the held figure's +54.4 (-8.4 %, within
  the harness's 15 % bound for the loop's own stored-heat settlement). The plan's first-solve spend difference
  on the same loops reads +145.6 and +85.1 per degree: that is the transient
  the merge base published. The plan delivers only -0.514 K and +0.327 K per
  degree of setting there, which is why its realised cost per degree of
  SETTING is smaller than either.
- **The varying-outdoor arm (`timing`)** is the control that separates
  timing: with the outdoor swing the plan buys in warmer hours, and its
  realised cost per delivered degree reads +1.3 and +40.8 against the held
  +54.7. At three days the arm is too noisy to read as a term (its two sides
  disagree by 39.5); it shows the plan at or below the held figure, not a
  number for the gain.
- **The merge base's tile, on the same 40 days** (`days` arm, base column,
  `target_temp` alone and the single-solve spend): non-monotone on 5 of 40
  days and with no effect at all (0 / 0) on 3, day-to-day std 48.5 / 48.6.

## Figures

- `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_advisor_degree.py days`
  (sha1 `5d9584280158452f7527409a55131b771401534d`, at `cd1c837ca`; every RESULT line identical to the run at `464468bac`) -> `RESULT days base non_monotone 5/40
  warmer_not_costing 3/40 cooler std 48.5 range -262.8..+0.0 warmer std 48.6
  range +0.0..+217.8`; `RESULT days head non_monotone 0/40 cooler std 29.6
  range -164.5..-36.8 warmer std 29.5 range +36.8..+163.6`; `RESULT days head
  published over days 30-40 non_monotone 0/11 cooler std 1.1 range
  -75.7..-71.6 warmer std 1.1 range +71.6..+75.7`. The rule: a pair is
  non-monotone unless cooler < 0 < warmer; std is the population standard
  deviation of the 40 daily figures (11 published figures for the last row).
- **How the horizon removes the noise (carry 2), with those numbers.** The
  held figure has no solver noise left in it: each day's two tiles are
  antisymmetric within 0.9 (the per-day RESULT lines). What still moves day to day is real (that
  day's weather and prices): std 29.6. The published figure is the mean of
  30 daily means, so one day moves it by a thirtieth; over days 30-40 its std
  is 1.1. Independent days would give 29.6 / √30 ≈ 5.4; the synthetic
  sequence is periodic (7 price days, a 9-day weather swing), so its 30-day
  windows nearly coincide and the measured 1.1 is lower than real weather
  would give. The 5.4 is the rule's figure, not a measurement.
- `… r10_advisor_degree.py null` -> `RESULT null offset -1 delivered -0.514 K
  truth_per_delivered_degree +59.4 held +54.4 (-8.4 %) first_solve_plan
  +145.6`; `RESULT null offset +1 delivered +0.327 K truth_per_delivered_degree
  +59.4 held +54.4 (-8.4 %) first_solve_plan +85.1`; `VERDICT null held figure
  within 15 % …`.
- `… r10_advisor_degree.py timing` -> `RESULT timing offset -1 … +1.3 held
  +54.7`, `RESULT timing offset +1 … +40.8 held +54.7` (informational).
- The scope (fixer step 5): `python3 tests/closure.py select --diff 265d3bf1acc1f52b838c52f3393db2296e59efa6 --workdir "$D"`
  (at `cd1c837ca`, after the closure commits) -> `MODE: SCOPED -- 29 script(s)
  run, 4 scoped out.`; every script `scope.run` names was run on this branch
  and is listed in this section, `tests/stress.py` included (alone, under
  `tests/gate_lock.py take`).
- `GOLDEN_MODE=drift GOLDEN_REF=265d3bf1acc1f52b838c52f3393db2296e59efa6 PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 265d3bf1acc1f52b838c52f3393db2296e59efa6`
  (at `cd1c837ca`) -> `NO UNCLAIMED DRIFT: 56 scenario(s) checked against
  265d3bf1acc1…` and `NO STALE FIXTURE: 56 committed fixture(s) still match
  what this tree computes`: no solver fixture moves, so neither claim file
  is the solver's to touch (only the card's is).
- At `cd1c837ca`, `PYTHONPATH=tests/hastub python3 tests/<script>.py`:
  `arch_score` -> `ALL 255 ARCHITECTURE SCORE CHECKS PASSED`; `validate` ->
  `NO ISSUES`; `edge` -> `ALL EDGE CASES PASS`; `backtest` -> `ALL 25
  BACKTEST CHECKS PASSED`; `optimality` -> `ALL 84 OPTIMALITY CHECKS
  PASSED`; and `node tests/md_tables.mjs` -> `RESULT
  doc_orphaned_table_rows=0 count`, `RESULT doc_misrendered_lines=0 count`.
- `PYTHONPATH=tests/hastub python3 tests/stress.py` (at `cd1c837ca`) -> `ALL 113 STRESS CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/features.py` (at `cd1c837ca`) ->
  `ALL 4276 FEATURE CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/finite_boundary.py` (at
  `f2766fd4d`, under the closure recording) -> `ALL 106 FINITE BOUNDARY
  CHECKS PASSED`; the price tiles are in Arm 6's rich seed, so their stored
  fields are probed in and out of their declared domains.
- `node tests/card.mjs` (at `cd1c837ca`) -> `ALL CARD CHECKS PASSED`.
- `node tests/card_drift.mjs` (at `cd1c837ca`, against origin/main
  `3688cf25977c`) -> `card_drift: 1 state(s) moved and claimed, 39
  identical`: `advisor_page`, whose diff is the four enable-to-see rows alone
  (each gains its step line, and `data-act="settings"` becomes
  `"open_options"`).
- `python3 tools/audit/seat/r10_deeplink_mutants.py RV1_history_bracket_back_in_undriven_keydown RD8_insert_adjacent_html_built_href_driven_residual`
  (at `187134aff`; no census file has changed since) ->
  `RESULT mutant=RV1_history_bracket_back_in_undriven_keydown rc=1 fails=1`,
  `RESULT mutant=RD8_insert_adjacent_html_built_href_driven_residual rc=0
  fails=0`: RV1 red, RD8 green, the control R10-DEEPLINK's carry requires.
- `python3 tests/structure.py` (at `cd1c837ca`) -> `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff 265d3bf1acc1f52b838c52f3393db2296e59efa6`
  (at `cd1c837ca`) -> `Architecture score: dS +0.8296 IMPROVES`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`
  (at `cd1c837ca`) -> `CI PREDICT: no closures or fast red predicted against 265d3bf1acc1`, rc 0, and the 16 unpinned sites listed below.
- `bash tests/derive_closures.sh --single tests/entities.py` (at `c5ad992b4`;
  the head adds only that recording's `rc` field) -> `done tests/entities.py
  (exit 0)`: the suite ran clean while recording its own closure.
- `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` and
  `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/harness_headers.py`
  (at `4eaec5793`) -> `ALL 169 checks PASSED`, `ALL 109 HARNESS HEADER CHECKS
  PASSED`, and `git status --short` empty after them (the D6 outputs are the
  committed ones).
- Class seams for item 6 (step 8). Rule: every builder of a ready inbox row,
  `grep -nE 'advisorRow\(plan, "[a-z]+"|kind: "[a-z]+", status: "ready"' custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`.
  It returns six lines, five builders (`restart` twice):
  `restart` (value null: no money), `valve` (null), `degree` (closed here),
  `gap` (`sek_per_month` from `topology.rank_sensor_advisor`, today's live
  inputs) and `dhw` (`_dhw_setpoint_sweep`'s cost per day at the current
  price window's mean, times 30). The last two swing with today's prices
  and loads and are not this group's seam (the architect note confines it
  to the what-if): an open seam, see Forward-carry.
- Class seams for the monthly scaling. Rule: `grep -rnE "30\.4|DAYS_PER_MONTH|per_month\(" custom_components/heatpump_optimizer --include=*.py --include=*.js`.
  It returns `price_tiles.per_month` (the tiles, closed here),
  `async_simulate`'s `monthly_cost_delta` (the Plan page's what-if and the
  fuse advisor: the plan's single-solve spend, transient included, the
  `null` arm's `first_solve_plan` is its size: an open seam, see
  Forward-carry), and the card's `DAYS_PER_MONTH` (the DHW row above).

## Unpinned sites

`ci_predict.py` lists 16 sites the diff adds, all in `price_tiles.py`. Each is
killed by the check named, read from the line and the check (no per-site
mutant run here), so each is pinned by `mutation-autofix` when CI's
`mutation` job kills it:

- `custom_components/heatpump_optimizer/price_tiles.py:38 CONST` — `HORIZON_DAYS = 30` — killed by `#2257: a tile keeps the last 30 local days and publishes the mean of their daily means` (`len(_pt_days) == price_tiles.HORIZON_DAYS == 30`).
- `custom_components/heatpump_optimizer/price_tiles.py:63 RETURN_DEL` — `book` returns `None` — killed by every tile check (`price_tiles.book(...)` has no `.clear()` or `.get()`).
- `custom_components/heatpump_optimizer/price_tiles.py:68 RETURN_DEL` — `per_month` returns `None` — killed by `#2257: at the real what-if seam a degree cooler saves and a degree warmer costs, convexly` (`round(None)` in `async_simulate`).
- `custom_components/heatpump_optimizer/price_tiles.py:103 RETURN_DEL` — `monthly_figure` returns `None` — killed by `#2257: a degree tile reads the held figure, the cap tile the plan's`.
- `custom_components/heatpump_optimizer/price_tiles.py:109 CMP_BOUND*2` — `_within`'s two bounds — the oldest one killed by `#2257: a tile keeps the last 30 local days …` (29 days kept), today's by `#2257: a day past the horizon, or ahead of today, is not in the published mean` (today's bucket dropped).
- `custom_components/heatpump_optimizer/price_tiles.py:109 RETURN_DEL` — `_within` returns `None` — killed by `#2257: a tile keeps the last 30 local days …`.
- `custom_components/heatpump_optimizer/price_tiles.py:118 RETURN_DEL` — `fold` returns `None` — killed by `#2257: a tile keeps the last 30 local days …`.
- `custom_components/heatpump_optimizer/price_tiles.py:128 GUARD_OFF` — `record`'s `if value is None` — killed by `#1753: the tile solves through the user-limit-free path, so its turn is always spent` (its answer carries no figure, so `fold` adds `None` and raises).
- `custom_components/heatpump_optimizer/price_tiles.py:144 GUARD_OFF` — `published`'s `if not days` — killed by `#2257: a day past the horizon, or ahead of today, is not in the published mean` (an all-expired tile divides by zero).
- `custom_components/heatpump_optimizer/price_tiles.py:149 RETURN_DEL` — `published` returns `None` — killed by `#2257: a tile keeps the last 30 local days …`.
- `custom_components/heatpump_optimizer/price_tiles.py:164 GUARD_OFF` — `restore`'s Mapping guard — killed by `#2257: a store with no tiles, or tiles of the wrong shape, loads an empty book` (`None.items()`).
- `custom_components/heatpump_optimizer/price_tiles.py:167 GUARD_OFF` — `restore`'s tile-shape guard — killed by the same check (`5` and `{"days": "x"}`).
- `custom_components/heatpump_optimizer/price_tiles.py:169 BOOLOP` — `restore`'s per-day admission — killed by `#2257: a stored tile loads day by day and field by field …` (the count-0 day is kept).
- `custom_components/heatpump_optimizer/price_tiles.py:170 BOOLOP` — `restore`'s per-field admission — killed by the same check (`"min_room_temperature": "warm"` is kept).
- `custom_components/heatpump_optimizer/price_tiles.py:171 GUARD_OFF` — `restore`'s aware-stamp guard — killed by `#2257: a naive stored stamp is dropped, never published as an instant`.
- `custom_components/heatpump_optimizer/price_tiles.py:173 GUARD_OFF` — `restore`'s `if days` — killed by `#2257: a stored tile loads day by day and field by field …` (`power_cap_75`, with no admitted day, is kept).

## Architecture score

`Architecture score: dS +0.8296` — IMPROVES, admissible: `shared_inplace_writes`
19 -> 17 (the tile book is mutated in its owning module), `coord_footprint`
2494 -> 2490. No metric rises.

## Red checks

- `mutation` (predicted, step 7): the 16 sites above are ADDED UNPINNED
  until CI's `mutation` job kills and `mutation-autofix` pins them
  (`ci-autofix.md`: wait for the bot commit). The cheaper detector exists and
  ran: `ci_predict.py` (step 6d) listed every site before any push, at the
  cost of one static pass. Two sites it named earlier on this branch could
  not be killed by any input: `per_month`'s clamp (nothing sets
  `horizon_hours` below its 24.0 default) and the tile's error guard (an error
  answer carries no figure, so `record` already records nothing). Both were
  deleted rather than triaged.

No CI run has taken this head yet. Locally, before this head:
`tests/entities.py`'s classification checks and `ci_predict.py`'s
`UNDER-SCOPED` and `INERT READS` predictions were red for the new module and
harness, and are answered by the closure commits (`ci-autofix.md` names
both; the cheaper detector is `ci_predict.py`, which found them before any
push). `tests/harness_headers.py` was red on D6's module count and
`tests/card_drift.mjs` on the unclaimed `advisor_page`; both are repaired
here (the D6 header, the card claim).

## Forward-carry

- **R10-UX-HEALTH** (the next card stage that converts a `settings` link):
  the Advisor's rows moved to a NEW act, `open_options`
  (`openHaLink(host, "options", null)`); `settings` is now dispatched by the
  Health page alone, so converting `health:settings` should reuse
  `open_options` and delete the `settings` branch with its `ACTS` entry and
  PENDING row in `tests/card.mjs`. Control, re-measure at your merge base:
  `node tests/card.mjs` green with `advisor:settings` absent from PENDING.
  Carry: the `brief` of R10-UX-HEALTH in `dev/programme/rosters/wave-r10-groups.json`
  (on `handoff/audit-r10-roster`; this seat pushes only its return refs, so
  the orchestrator writes it).
- **R10-LIVESTATE** (the large coordinator move): `_price_tiles` and
  `_price_tile_specs` are no longer on the coordinator; the tile book lives in
  `price_tiles.book(coordinator)`, persisted under the ledger store's
  `price_tiles` key. A move that enumerates coordinator state should not
  expect them. Control: `grep -n "_price_tiles\b" custom_components/heatpump_optimizer/coordinator.py`
  returns nothing at this head. Carry: the `brief` of R10-LIVESTATE, as above.
- **Open seams with no live stage (orchestrator to file; this seat cannot):**
  (a) the Plan page's what-if (`async_simulate`'s `monthly_cost_delta`, also
  the fuse advisor's `cost_delta_sek_month`) scales the plan's single-solve
  spend, one-off coast or heat-up included; its size is the `null` arm's
  `first_solve_plan` against `truth_per_delivered_degree`, and the Advisor's
  "Try in what-if" lands on it (docs/dashboard-card.md now says so). (b) The
  inbox's sensor-gap and hot-water rows are today's window, scaled (the class
  seams above). Carry: a new issue each, filed by the orchestrator with this
  PR.

## Friction

- ci-autofix: unenforced: `tools/pr/ci_predict.py`'s closure arm rebinds its `scripts` parameter inside the loop (`scripts, froms = hits.setdefault(...)`), so its repair line named one script (`tests/block_duty.py`, "the 1 took 1 s") where the finding named 19 and the merge needed 21 plus `tests/entities.py`. Carry: the orchestrator's next tools/pr stage.
- gate-scoping: contradiction: the brief leaves closures to CI (`PREPR_SKIP_CLOSURES=1`), but `tools/audit/seat/body_push.sh` refuses any head `ci_predict.py` refuses, UNDER-SCOPED included, so a seat that adds a module must record its closures before it can hand off; recorded here on Linux with `strace` (`derive_closures.sh --scripts-from`, then `--single`). Carry: the dispatch template's closure line.
- gate-scoping: stale: the payload says the toolchain is on PATH, but this cloud seat's non-login shell has no numpy until `/etc/profile.d/hpo-toolchain.sh` is sourced. Carry: `tools/audit/seat/cloud-setup.sh`'s profile note.
