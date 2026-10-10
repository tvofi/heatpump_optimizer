<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
R9-UX-7 (lane UX, model status and diagnostics), part of #201. Recovered onto
current `main` from the orphaned handoff `handoff/r9-ux-7` (`226e6fc24`): the
work existed and no pull request was ever opened. Issue #1795 is the lane's
feature issue and was closed by #2010 while this lane was still in flight, so
this body closes nothing; see `## Friction`.

Four changes, per `DESIGN-UX.md` section UX-7:

1. **Learning Model Status** (`sensor.py`, the model-status sensor). Reads the
   learning view the coordinator already publishes. The state is an enum:
   `learning`, `learned` (the heat-loss learner has evidence) or `attention`
   (the COP health alarm). One compact recorded row per learner; the bulky
   per-hour gains, the capacity envelope and the system identification state
   are unrecorded attributes. It adds no coordinator line.
2. **Indoor Temperature (Predicted)** (`sensor.py`). A recorded measurement of
   the plan's next-interval room prediction. A module-level
   `coordinator.predicted_next_room_temp(coord)` calls the existing
   `_predicted_next_room_temp`, so the sensor reports exactly the figure the
   accuracy tracker files. It is unavailable while no plan governs the room,
   and `waiting_for` says why: `first_plan` or `plan_not_in_control`.
3. **Diagnostics** (`diagnostics.py`). The download also carries the last
   diagnosis, the input watchdog's published keys, a plan summary (counts and
   totals, no per-step series) and the published learning view. Every
   `person.*` and `calendar.*` entity id is redacted at any depth, inside a
   message string and inside the opt-in debug bundle.
4. **Card, Health tab: "What the model has learned"**. One row per learner with
   its value, its evidence in words and an evidence bar; a COP alarm in the
   warn tone; a 24-bar internal-gains strip naming its peak hour. The Health
   page's two screenshots are regenerated from the browser test (U5) and the
   alt text names the new rows; see `## Figures` and `## Friction`.

New entities move the README count and the `tests/entities.py` rosters in the
same diff.

## Head

`4e1c290e0138b4c145b338030b557a62f58950f7` merges the authored code head `27ad9640e9232095589920aea7885a967324a4d9` into this PR's previous head, which carried its own row `dev/programme/delivery/2120.md`. The PR tree is that code head plus the row.

`27ad9640e9232095589920aea7885a967324a4d9` is the repair head: the reviewed
head `b5c9e5bbae47eb464c081be3202a09ea156ab606` (whose review verdict was
`root-cause-unanswered`), a clean merge of `origin/main` `d3dbf2c3f`, and two
commits that touch no production line — the golden-fixture and claim repair
(`64ba13e36`) and the mutation-ledger pins (`27ad9640e`). The authored code
head is still `574345d95749d35d7372fc608d843ec915e52c30`; every commit after
it touches only `tests/golden/`, `tests/mutation_ledger/` and merge metadata,
so every check that reads production code reads exactly what the review
measured.

`b5c9e5bbae47eb464c081be3202a09ea156ab606` itself adds one commit to
`574345d95749d35d7372fc608d843ec915e52c30`, containing only this PR's own row,
`dev/programme/delivery/2120.md`.

`574345d95749d35d7372fc608d843ec915e52c30`, a merge of `6c8827e54` and
`origin/main` `70b50c5730d7fa5b2e7140cb36371bc041522f73`. `6c8827e54` is in turn
the merge of the recovered handoff head `88c04a172` with the previous
`origin/main` `7cd5a588c`, plus one commit — the U5 screenshots and the alt
text — that touches no production line.

Both earlier merges were clean and neither moved a production, test or card
file on this branch's side. `git merge-base origin/main HEAD` is
`d3dbf2c3fc42b87e6aad71d3de0c0885a10c750e`; every three-dot comparison is
against that. (`origin/main`'s tip has since moved to `969c3a5c84`, whose
commits touch only `dev/programme/` and pre-study documents — nothing this
diff or any figure below measures.)

## Already on main under another shape

None of it was. Measured with
`git grep -l <symbol> origin/main -- custom_components tests docs README.md`
against `origin/main` `d3dbf2c3fc42` (re-taken 2026-10-10T18:19Z):
the model-status sensor, the predicted-temperature sensor, `_without_private_ids`, `_published_sections`,
`PRIVATE_ENTITY_ID`, and the entity keys `learning_model_status` and
`indoor_temperature_predicted` each answer **0 files**, bare or word-bounded.
The module-level `predicted_next_room_temp` answers **0 files word-bounded**
(`git grep -lE '(^|[^_[:alnum:]])predicted_next_room_temp' origin/main --
custom_components tests docs README.md`) and **5 files bare** — every one of
the five is the private method `_predicted_next_room_temp` (`coordinator.py`,
`tests/boost_drift_replay.py`, `tests/features.py`, a `killed_by` ledger
entry, `tests/seam_map.json`), whose name the bare substring also matches;
the module-level function exists nowhere on `main`. The earlier body's "0
files" for the bare grep was wrong; the rule is now stated with the figure.
`last_diagnosis` is
absent from main's `diagnostics.py` (it is a payload key the coordinator
publishes; this diff reads it into the download), and the card's
"What the model has learned" block is absent. `dev/programme/delivery/` carries
no row claiming #1795 as delivered.

## The diagnostics collisions, read against mine

`diagnostics.py` is the one file where main moved into this diff's lines twice.
Both were read hunk-against-hunk, not merged blind:

- **#2065** added `_VIEWS` and `_never_breaks` and the `draw_range` and
  `probe_install` imports. Untouched by this diff; both sides kept.
- **#2071** replaced `"config": dict(entry.data)` with
  `**config_view(entry.data, entry.options)`, adding `config_view()` and the
  `config_setup` / `config_overridden_by_options` keys.
- **#1940** wrapped the debug bundle in
  `debugger.capped(..., f"{DOMAIN}_{entry.entry_id}_debug")`.

This diff re-indents that same dict literal (to wrap it in
`_without_private_ids`) and adds `**_published_sections(coord)`. Both merges
therefore conflicted in exactly two regions: the module docstring, and the
return statement. A side-pick either way would have been silent: taking this
branch's side would have **reverted #1940's 8 MiB inline cap** and #2071's live
config; taking main's would have dropped the redaction wrapper. The resolution
keeps both, and `git merge-tree` being clean is why this section exists.

**The interaction is load-bearing.** #2071 made the export carry
`entry.options` *values* (it previously emitted only `options_keys`), and the
away and holiday options hold the `person.*` and `calendar.*` ids this diff
redacts. So the wrapper now covers a surface that did not exist when it was
written: `_without_private_ids(_coarsen({... **config_view(...) ...}))`, the
wrapper outermost.

## Mutation proof

Three production lines were deleted at `e12202d9b`, in a detached worktree at
that head, and `PYTHONPATH=tests/hastub python3 tests/entities.py` was run
against each; each mutant is a predicate, not a tail.

The baseline, unmutated at `e12202d9b`, printed `ALL 2267 ENTITY CHECKS PASSED`.

- `diagnostics.py` `_without_private_ids`'s `str` arm turned off
  (`if isinstance(value, str):` becomes `if False:`): `2 of 2267 ENTITY CHECKS
  FAILED`, naming `UX-7: no person or calendar id leaves the instance, from the
  entry or an input problem` and `UX-7: the over-redaction control -- an
  ordinary sensor id survives beside them`.
- `sensor.py` `ModelStatusSensor`'s COP-alarm guard removed
  (`if _mapping(data.get("cop_health")).get("alarm"):` becomes `if False:`):
  `1 of 2267 ENTITY CHECKS FAILED`, naming `UX-7: the status is learned, still
  learning, or needs attention on a COP alarm`.
- `coordinator.py` `predicted_next_room_temp`'s
  `return predict() if callable(predict) else None` replaced with `return None`:
  `3 of 2267 ENTITY CHECKS FAILED`, naming `UX-7: the predicted indoor
  temperature is the plan's next-interval prediction, recorded`, `UX-7:
  waiting_for names why: no plan yet, or a plan that does not run the room` and
  `every entity is available against a payload that satisfies every gate`.

All three ran to completion at `e12202d9b`, the baseline included, and each
mutant was checked with `ast.parse` before its run — so a refusal is a check
failing and not a file that stopped importing.

The recovered handoff's own proof, at the pre-merge head `6931952`, deleted the
same three lines and printed `6 of 2227 ENTITY CHECKS FAILED` — the same six
checks this head names, at a tree that predates `#2025`, `#2065` and `#2071`.
This run supersedes it.

## Null control

`main`'s `custom_components/` with this head's `tests/`, in a detached worktree
at `origin/main` — the shape that shows which checks the implementation, and not
another change, satisfies.

That run printed `21 of 2267 ENTITY CHECKS FAILED` (re-taken at `d3dbf2c3fc42`
with this head's `tests/`; the same shape at the previous base `70b50c5730d7`
with the pre-repair tests printed 26 — the difference is the baseline's own
movement plus the fixture repair, not this diff's code, which both runs hold
at `main`'s). Every one of the fifteen
UX-7 checks is in that set, together with the checks the two new entities
move: `a3:roster`, `ModelStatusSensor publishes exactly
its pinned attribute keys (#373)` and the same for `PredictedIndoorTempSensor`,
`every class that publishes attributes is in the pinned roster (#373)`, the
62-entity build-count check, and the diagnostic-category check that names both
new keys. Each is therefore satisfied by this implementation and by
nothing on `main`.

Absence assertions that pass at the base by construction are the controls for
the presence ones: with no model-status sensor there is nothing to be
unavailable, and with no tank or profile there is no tank-cooling row.

## Figures

Each line is the command that printed it, run at `27ad9640e9` against
`origin/main` `d3dbf2c3fc42` (re-taken 2026-10-10T18:19Z; main's newer tip
`969c3a5c84` moves only `dev/programme/` documents) unless the line names
another tree. CI's check-runs at the pushed head are the authority for
anything this host cannot produce.

- `python3 tests/structure.py` -- `STRUCTURE RATCHET PASSED`. `max_class_loc`
  measured 8814 against a budget of 8814, and `origin/main`'s budget is 8818,
  so this diff is a payment of 4, not a raise. **The payment is the deletion,
  in `coordinator.py`'s learning-payload block, of a four-line comment** whose
  warning ("the defect noted at `_thermal_learning_payload`") describes the
  options-edit re-anchor that backlog item #110 closed with `cca2b115` — spent
  prose, not a code change; restoring the comment reads 8818 > 8814 and fails.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`
  -- `MODE: SCOPED -- 22 script(s) run, 11 scoped out`, over 28 changed files:
  the code, tests, docs and screenshots this diff touches, the two Health
  screenshots included, plus the five coord fixtures, the claim file and the
  eleven ledger entries the repair adds.
- `node tests/card_drift.mjs origin/main` -- `origin/main = d3dbf2c3fc42,
  tree = 27ad9640e92, 40 states`; `39 state(s) moved and claimed, 1 identical`.
  The identical one is `editor_schema`, which renders no stylesheet.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` --
  `claims_extracted=125 claims_true=123 claims_false=0 claims_stale=0
  claims_unverifiable=2`; `arch_modules_on_disk=75 arch_map_listed=75
  arch_map_missing=0`. Re-running it rewrote `claims.json` and `claims.md` and
  left the tree clean, so the committed 81 entities / 62 sensors are this
  tree's own answer rather than a carried figure.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` -- `ALL 2267 ENTITY CHECKS PASSED`
  at this head. The same
  command in a worktree holding `origin/main`'s `custom_components/` with this
  head's `tests/` printed `21 of 2267 ENTITY CHECKS FAILED`; see `## Null control`.
- `PYTHONPATH=tests/hastub python3 tests/deployment_shape.py` -- `ALL DEPLOYMENT SHAPE CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all $(git merge-base origin/main HEAD)`
  -- `NO UNCLAIMED DRIFT: 56 scenario(s) checked against
  d3dbf2c3fc42b87e6aad71d3de0c0885a10c750e`; `NO STALE FIXTURE: 56 committed
  fixture(s) still match what this tree computes`. The earlier body's
  `env_drift.py` line (5 scenarios, `NO UNCLAIMED DRIFT` against
  `70b50c5730d7`) answered the claims-only comparison against the older base
  and hid what CI measured; this is the same shape the `fast (3.14)` job runs.
- `PYTHONPATH=tests/hastub python3 tests/arch_score.py --smoke` -- `ALL 257 ARCHITECTURE SCORE CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/arch_score_head.py` -- `ALL 15 ARCHITECTURE SCORE HEAD CHECKS PASSED`.
- `python3 tools/audit/archscore/score.py --diff origin/main` -- `dS -0.0017
  WORSENS (inadmissible: coord_footprint 2586->2589)`; see `## Architecture score`.
- `python3 tools/pr/ci_predict.py --base origin/main` -- prints no
  `ADDED UNPINNED` line at this head (11 before the pins; see
  `## Unpinned sites`); `no closures or fast red predicted against d3dbf2c3f`.
- `python3 tests/mutation_table.py --base origin/main` -- the table no longer
  refuses: `PIN KILLED: 11 pinned, 0 left unpinned` is the pin drive's own
  closing line at this head, and the committed `killed_by` entries carry it.
- `PYTHONPATH=tests/hastub python3 tests/typing_ruler.py` -- `ALL 11
  typing-ruler source checks PASSED`. The mypy census itself is CI's `typing`
  job; `HPO_TYPING_PYTHON` is unset here and both the ruler and this line say
  so rather than claiming it was checked.
- `HPO_PAGES_OUT=docs/img/card HPO_BROWSER_SCOPE=auto node tests/card_browser.mjs`
  (U5, after `python3 tests/plan_view.py`) -- measured at `e12202d9b`, the
  tree the screenshots were regenerated in: `health-light.png`
  (80360 -> 113974 bytes) and `health-dark.png` (80375 -> 113574), the two
  pages this diff changes, the other pages byte-identical. The card JS, the
  card claims and the two screenshots are byte-identical between the reviewed
  head `b5c9e5bbae` and this head
  (`git diff --stat b5c9e5bbae 27ad9640e9 -- custom_components/heatpump_optimizer/www docs/img/card`
  is empty), so the figure still describes this tree. The same
  command at a clean `origin/main` worktree moves only `advisor-*.png` and
  `plan-why-*.png`, which are stale on `main` already and are not this PR's.
  Its own run reports `1 BROWSER CHECK(S) FAILED`; see `## Red checks`.
- Green locally at this head, each on its own run: `tests/block_duty.py`,
  `tests/config_flow_steps.py`, `tests/debug_collect.py`, `tests/doc_claims.py`,
  `tests/finite_boundary.py`, `tests/harness_headers.py` (green now; the
  earlier body named it unrun -- see `## Friction`), `tests/manual_plan.py`,
  `tests/plan_view.py`,
  `tests/solar_alignment.py`, `tests/wood_advisor.py`, `tests/md_tables.mjs`,
  `tests/card.mjs`.
- Left to CI (heavy, per tvofi's 2026-10-07 rule): `tests/golden.py`,
  `tests/boost_drift_replay.py` and the required mutation drive. `tests/features.py` is
  the known macOS BLAS defect; its line is under `## Red checks`.

## Unpinned sites

The 11 sites `python3 tools/pr/ci_predict.py --base origin/main` printed as
`ADDED UNPINNED` at the reviewed head. `mutation-autofix` could not pin them:
it went red `skip-measure-failed` because its pin drive's baseline
`tests/env_drift.py` was itself red on the unclaimed coord drift (see
`## Red checks`) — a driver red at baseline gives no mutant a verdict, and a
red autofix means no bot commit (`ci-autofix.md`). With the fixtures claimed
and recorded in `64ba13e36`, `python3 tests/mutation_table.py --pin-killed
--base origin/main` was run at this head — `tests/features.py` excluded from
the driver net, because its baseline is the known macOS BLAS red
(`R9-RC-BLAS-KERNEL-RED`) on this host and a red-at-baseline driver cannot
testify. `PIN KILLED: 11 pinned, 0 left unpinned`, no survivor, and the
eleven `killed_by` entries are committed in `27ad9640e`: ten killed by
`tests/entities.py` and the `_without_private_ids` fall-through return by
`tests/debug_collect.py`. Each entry names its anchor, the driver and the
before/after. The three the old mutation proof drove (M1-M3) are among them,
re-driven at this head.

- `custom_components/heatpump_optimizer/coordinator.py:931 RETURN_DEL` --
  `predicted_next_room_temp`'s `return predict() if callable(predict) else
  None`. Pinned: `tests/entities.py`, rc=0 failed=0 -> rc=1 failed=3.
- `custom_components/heatpump_optimizer/diagnostics.py:99 GUARD_OFF` -- the
  `str` arm of `_without_private_ids`. Pinned: `tests/entities.py`.
- `custom_components/heatpump_optimizer/diagnostics.py:101 GUARD_OFF` -- the
  `Mapping` arm. Pinned: `tests/entities.py`.
- `custom_components/heatpump_optimizer/diagnostics.py:103 GUARD_OFF` -- the
  `list` arm. Pinned: `tests/entities.py`.
- `custom_components/heatpump_optimizer/diagnostics.py:105 RETURN_DEL` -- the
  fall-through return. Pinned: `tests/debug_collect.py`.
- `custom_components/heatpump_optimizer/sensor.py:2028 GUARD_OFF` -- the
  predicted sensor's `_waiting_for` guard. Pinned: `tests/entities.py`
  ("UX-7: waiting_for names why", all three states as one set).
- `custom_components/heatpump_optimizer/sensor.py:2032 RETURN_DEL` -- the same
  property's return. Pinned: `tests/entities.py`.
- `custom_components/heatpump_optimizer/sensor.py:2037 RETURN_DEL` -- the
  predicted sensor's `native_value`. Pinned: `tests/entities.py`.
- `custom_components/heatpump_optimizer/sensor.py:2081 GUARD_OFF` -- the
  model-status sensor's no-data guard. Pinned: `tests/entities.py`
  ("UX-7: before the first update the model status is unknown and does not
  raise").
- `custom_components/heatpump_optimizer/sensor.py:2084 GUARD_OFF` -- the
  COP-alarm guard. Pinned: `tests/entities.py`.
- `custom_components/heatpump_optimizer/sensor.py:2086 RETURN_DEL` -- the
  learned/learning return. Pinned: `tests/entities.py`.

## Architecture score

`python3 tools/audit/archscore/score.py --diff origin/main` reads
`dS -0.0017 WORSENS (inadmissible: coord_footprint 2586->2589)`.

- coord_footprint 2586 -> 2589: the metric charges every function handed the
  coordinator, one per non-plumbing statement, and this diff adds two such
  functions: `coordinator.predicted_next_room_temp` costs 1 statement and
  `diagnostics._published_sections` costs 2. Each exists so a rule has one
  owner rather than a second copy — the module function is what keeps
  `sensor.py` from re-deriving the prediction the accuracy tracker scores, and
  `_published_sections` is what keeps the diagnostics payload section out of
  the export function. Both read the coordinator through `getattr(coord, ...)`,
  the idiom `coordinator.py` already uses 19 times for its module-level helpers
  (`getattr(coord, "_ctx", coord)`, `getattr(coord, "_snapshot_ring", None)`).
  The alternative considered and rejected is a bare
  `return coord._predicted_next_room_temp()`, which the metric excludes as
  plumbing but which drops the tolerance for a coordinator-like object without
  the private method that the rest of that helper set keeps. No payment removes
  the statements without duplicating the prediction rule in `sensor.py`, which
  the design rejects.

## Red checks

Three checks are red at the reviewed head `b5c9e5bbae47eb464c081be3202a09ea156ab606`
(check-runs at that SHA: `fast (3.14)`, `mutation`, `pr-contract` — and
`mutation-autofix`, so no bot commit was coming), and two checks are red
locally; all five are answered here. The body at that head opened this
section with "Nothing has been pushed to CI yet, so there is no pushed-head
red" — that was false, and this section replaces it.

- `fast (3.14)` (`tests/env_drift.py --all` against `d3dbf2c3f`): `5 UNCLAIMED
  DRIFT(S)` and `5 COMMITTED FIXTURE(S) ARE STALE` — the same five
  `coord_*` fixtures both ways: the two new sensors appear in the coordinator
  capture, and neither the fixtures nor `tests/golden/claimed_drift.txt` were
  touched. Answered in `64ba13e36`: the five scenarios are claimed in
  `tests/golden/claimed_drift.txt` ("keys added, no value moved", the
  `63414e06a` precedent) and the two sensors' subtrees are added to the five
  committed `coord_*.json` fixtures add-only, by hand from a fresh capture —
  the `875ed11c` method; the fixtures are float-bearing, so no solver float
  was re-recorded on this dev box, and the structural comparison the check
  runs is satisfied while the value drift it never fails on is untouched.
  `tests/env_drift.py --all $(git merge-base origin/main HEAD)` now prints
  `NO UNCLAIMED DRIFT: 56 scenario(s)` / `NO STALE FIXTURE: 56`. Cheaper
  detector: `env_drift --all` is the check.
- `mutation`: `MUTATION TABLE REFUSED -- 4619 unpinned site(s) ... 11 of them
  added by this diff`. `mutation-autofix` reddened `skip-measure-failed` for
  the reason above — its baseline `env_drift` was red — so per `ci-autofix.md`
  the pin drive was run in the branch: `PIN KILLED: 11 pinned, 0 left
  unpinned`, committed in `27ad9640e`; see `## Unpinned sites`. Cheaper
  detector: the mutation table itself, which is the check.
- `pr-contract`: `check 'mutation' is red and '## Red checks' does not name
  it` — the false sentence quoted above. Answered by this section, which
  names all three. Its `preflight.sh` also REFUSE'd the earlier `## Friction`
  bullet's backticked quote of the closing keyword for #1795 ("not in the
  intended list"): the friction bullet now describes it without the literal
  keyword.

Two checks are red locally, both answered here.

- `tests/card_browser.mjs`: `P9 grid: no two text runs share ink` -- `20: text
  "2" x text "3" 2 px of shared ink`. **Pre-existing at `main`, not this diff.**
  The same command under `HPO_BROWSER_SCOPE=full` at a clean `origin/main`
  worktree reports the identical failure, and this diff adds no chart, axis or
  tick rule. It went unseen because the grid is scoped: with no card file in a
  diff `card_browser` prints `P9 GRID SKIPPED -- the class barrier did not run
  on this diff`, so `main` has not paid this check since the rule landed.
  Cheaper detector: the same scoped grid, which is the check.

- `tests/features.py` (`closures`' recording arm, and `prepr` step 6): `1 of
  3930 FEATURE CHECKS FAILED`, and the failing check is `R9-F2.1 P3: the
  shipped storage plan is no worse on its own objective than the half-price
  floor's plan refined under it [shipped 110.4366, seeded with the half-price
  plan 110.1297]`. This is the known macOS BLAS defect (group
  `R9-RC-BLAS-KERNEL-RED`), not this diff: the check compares solver floats and
  this diff touches no optimizer module. No check was weakened and no flag was
  added. The clean-`origin/main` reproduction was started twice at this head and
  did not finish on this host (see `## Friction`), so the identical single
  failure is cited from the completed run at the intermediate head `88c04a172`
  rather than claimed for the base. Cheaper detector: none on this host; the
  defect is a BLAS-kernel property, so the recording arm and CI's Linux runner
  are where it is settled.

## Forward-carry

none: no finding here changes how a later stage must work. The carry in
`dev/programme/carries/carry-1795.json` (third entry, from R9-UX-3) is honoured:
the new Health block reads only an always-available, enabled-by-default sensor,
and nothing is added to `HEALTH_WAITING`.

## Friction

- `fixer.md`: cost: this lane's mutation loop was killed mid-run three times —
  once by an unrelated seat's process-group cleanup, and twice more when a
  session boundary ended under it. A killed loop leaves a log that reads like a
  result, so nothing was carried from a killed run and the loop was re-run from
  a clean worktree; the section above is that run, and `mut3.log` — a fragment
  from the first — was discarded rather than read.
- `gate-scoping.md`: cost: `tests/entities.py` takes the gate lease for its own
  lock self-tests, so it queues behind whichever seat holds it, and under this
  host's load it was the slowest step by far: one mutant's run sat at 0.0% CPU
  for half an hour. `tests/features.py` at a clean `origin/main` worktree was
  started twice and never reached its summary (see `## Red checks`).
- `claim-files.md`: cost: the recovered handoff's
  `tests/golden/card_claimed_drift.txt` claimed 39 cards with reasons written
  at its 2026-10-07 base. Between then and this merge `main` was stamped
  (6.7.16 -> 6.7.17), which empties the list, and #2010 then re-added two
  claims for its own tooltip change. Both are the baseline now, so the file was
  re-measured rather than textually merged; the `claimnotes` driver refused the
  merge, which is its documented behaviour.
- `delivery-status-tracking.md`: stale: `dev/programme/delivery/2010.md` reads
  `**open**` for #2010, which merged at 2026-10-10T06:37:58Z. It is this lane's
  own row; reported, not fixed, since the delivery row is the orchestrator's to
  write.
- `delivery-status-tracking.md`: contradiction: the roster's R9-UX-7 brief says
  the lane's feature issue #1795 "stays open for its other groups", but #2010
  carried the closing keyword for #1795 and closed it at 2026-10-10T06:37:59Z.
  This body therefore closes nothing, and the lane's remaining groups (R9-UX-6,
  R9-UX-8..10) now have no open lane issue.
- `gate-scoping.md`: cost: `tests/harness_headers.py` did not finish on this
  host at the reviewed head while unrelated seats held the machine; it
  completed green at the repair head (`ALL 109 HARNESS HEADER CHECKS PASSED`).
- `gate-scoping.md`: cost: an untracked seat-claim file in the worktree made the
  closed-over gate report the whole suite rather than the scoped set, until it
  was removed; this run's logs were kept outside the tree for that reason.
- `ci-autofix.md`: cost: one defect chained three checks red. The unclaimed
  coord drift made `fast (3.14)` red, the same red made the pin drive's
  baseline `env_drift` red so `mutation-autofix` could not measure
  (`skip-measure-failed`, no bot commit), and the body's denial of pushed-head
  red made `pr-contract` red. Fixing the first and pinning in-branch answers
  all three; the bot's measure step has no way to say "a sibling check's red
  is my blocker" beyond the status word.
- `gate-scoping.md`: cost: `tools/pr/prepr.sh` step 6b refuses on this host —
  `REFUSE closures -- failed while being recorded: tests/features.py (exit 1)`
  — the R9-RC-BLAS-KERNEL-RED platform defect again; no interpreter on this
  M1 runs features green, and the fix is PR #2114, open and unmerged at this
  head. The push therefore carries the closures step delegated to CI
  (`PREPR_SKIP_CLOSURES=1`, the mode `tools/audit/seat/handoff_push.sh`
  parameterizes and `open_pr.sh` sets), disclosed here rather than silent;
  CI's own `closures` job was green at the reviewed head `b5c9e5bbae`, and
  this diff adds no file any closure reads (`ci_predict`: a data-file read is
  not seen).
- `gate-scoping.md`: cost: this host's default `python3` is 3.11 and
  `tests/entities.py` has needed 3.12+ f-string syntax since `a5fda1741`
  (R9-F1.11), so every python figure in this body was re-taken under a 3.13
  venv; the first pin drive attempt also died on that SyntaxError inside the
  tool's own driver-parse.

_Requested by **tvofi**_

🤖 Generated with [Claude Code](https://claude.com/claude-code)


