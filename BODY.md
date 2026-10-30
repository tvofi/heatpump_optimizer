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

- **The mutation null control, round 3 (orchestrator ruling, mandate
  6329234399).** `null_control` in `tests/mutation_table.py` now takes the
  first whole-line comment of any width and indent. It took only one whose
  full line, indentation included, was under 60 characters. That cap has no
  recorded reason (2fe38a487's message, #1521, is silent on it), and nothing
  reads a line's width: no driver, and no linter in CI (Figures). It refused
  every pool whose comments ran past it: `button.py`'s do, so `tests /
  mutation` and `--pin-killed` refused this PR whatever it pinned. The null
  arm is unchanged: a file with no whole-line comment still yields none, and
  a pool of only such files still refuses. `tests/mutation_table.py` is
  code-owned (`.github/CODEOWNERS`, the `mutation_table.py` and
  `typing_ruler.py` note: the mutation jobs install the pull request's
  requirement locks before the grader, and it runs the pull request's
  tests), so the change is kept to the predicate and its docstring: one
  condition dropped, four docstring lines.
- **The three `button.py` pins, re-recorded by the tool.** The round-2 rows
  came from an out-of-tree scratch script (`hand_pin.py`). They are
  re-pinned by `mutation_table.py --pin-killed` itself, now that the pool has
  a null control; only each row's `reason` changes.

What does not land, and why:

- **Carry 17, the P9 storage reset, is withheld.** It is measured, and the
  result needs an after-edge outside this group's seam. Routed in
  Forward-carry. Carry: R10-UX-HEALTH
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
  Routed in Forward-carry. Carry: R10-UX-HEALTH
- **#2499 stays open.** See Figures: the no-meter arm still books about 1.9x
  what it delivers. The Health line "Not observable without a power meter"
  (`health.model_unobservable`) landed in #2976. The over-booking figure is
  not met, so this body closes nothing. Routed in Forward-carry. Carry: #2499

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

525e206910e181e8839d3efb979d6f4c8d6861f9, two commits on the reviewed head
feacede17c5e1eb6b7e399bf87a2efea3ea79cc7:
baf2c4c00c3d9f0d921ccfd03179bd1ee4e0b9fc (the `null_control` predicate and
its entities.py check) and 525e206910e181e8839d3efb979d6f4c8d6861f9 (the
three `button.py` rows re-recorded by `mutation_table.py --pin-killed`).
They replace the cloud seat's 700f21c18 and 077a87b02, which were committed
under another author identity; the tree differs from 077a87b02 only in the
`null_control` docstring's wording. Merge base
d99cadb1235a5e40e250466e656c41c7ce88e641. origin/main was at
7d6a95e5edb9564f8ab632bac2a0317c820bb29e at 2026-10-30T19:07Z, and
`git merge-tree --write-tree origin/main HEAD` exits 0 (no conflict), so main
was not merged in (`fixer.md` step 6). The round-3 tests, mutants and gate
ran at this head, or at baf2c4c00 where a line says so. The card, P9 and
#2499 figures are from earlier rounds, and no card, browser-test or learner
line has moved since.

Host note: this seat ran on macOS, whose kernel refuses
`entities.py`'s heartbeat arm a task port for its own child
(`PermissionError: Cannot get task port`, in `_hb_stdlib_reads`), at this
head and at feacede17 alike. Each local `entities.py` run below therefore
hid `_remote_debugging` from `importlib.util.find_spec` through a scratch
wrapper, so that arm skips exactly as on an interpreter without the module;
no tree file changes. CI (Linux) runs the arm.

## Mutation proof

Each mutant is one line in a worktree. `node tests/card.mjs`,
`python3 tests/debug_collect.py` or `python3 tests/entities.py` was run,
then the line was restored.

- Drop `host._render();` from `openSetupSlot` → FAIL `openSetupSlot renders
  the page it opens`. The existing `Assign redraws the dialog on the Setup page`
  also goes red, so this mutant was already killed at base. The carry's
  "unpinned at base" does not hold at this base. The new case pins it at the
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
- `tests/mutation_table.py` (round 3), all in worktrees, each run
  `PYTHONPATH=tests/hastub python3 tests/entities.py`:
  - Test first: the new entities.py check at feacede17, before the
    predicate changed → `1 of 2489 ENTITY CHECKS FAILED`, the failing check
    being `a comment line past sixty characters, by indent or by its own
    text, is still the null control; a pool with no comment line still
    refuses` (`long=None none=None pool-none=None`).
  - Mutant A, restoring the old predicate (`and len(lines[ln - 1]) < 60`
    back into `null_control`'s condition) at baf2c4c00 → `1 of 2489 ENTITY
    CHECKS FAILED`, the same check, the same detail.
  - Mutant B, the over-wide predicate (`if tok.type == tokenize.COMMENT:`,
    any comment, trailing ones included) at baf2c4c00 → `3 of 2489 ENTITY
    CHECKS FAILED`: the new check's null arm (`none=` picks `Y = 1  #
    trailing`), the #1521 check `the null control edits a whole-line comment
    and nothing else`, and the shard check `a shard whose files hold no
    whole-line comment inherits the whole pool's null control`.
  - Unmutated baf2c4c00 → `ALL 2489 ENTITY CHECKS PASSED`.

## Null control

Unmodified tree: origin/main at the merge base, with this head's
`tests/card.mjs` copied in.

- `node tests/card.mjs` fails exactly `hover spec (en)` and `hover spec (sv)`,
  which is the defect. The openSetupSlot and fallback cases pass at base,
  because they pin behaviour the base already has.
- The #2809 check fails at base by construction, because the base is the
  mutant above.
- The hover case enumerates every `data-model-row` the page draws. It asserts
  the count is 6, so a seventh row without the two parts fails it, and so does
  a row dropped from the fixture.
- The null-control check has its own null arm. It asserts that a file
  holding only a string that looks like a comment, plus a trailing comment,
  yields no null control, and that `null_for` over a pool of that file
  returns None. Mutant B, a fix that took any comment at all, fails it. The
  check also asserts its preconditions: both fixture comment lines are longer
  than 60 characters in full, so the old cap admitted neither.
- The mutation run's own null control: button.py:37 plus ` (null control)`
  survived every driver that read it in both round-3 runs (Figures).

## Figures

- **Null-control census (round 3).** The rule: take every `*.py` under
  `custom_components/` (`Path("custom_components").rglob("*.py")`). Run each
  through `mutation_table.null_control` at the head, and through the old
  predicate and an indent-stripped one (the same tokenize loop with
  `len(line) < 60`, and with `len(line.strip()) < 60`). Count the files
  that get no null control. Run at baf2c4c00 (scratch one-off probe,
  `fixer.md` step 18; the standing pin is the entities.py check).
  - 84 files. The old predicate leaves 13 without a null control, the
    indent-stripped cap of 60 (the alternative the brief named) leaves 11,
    and the head leaves 3.
  - The 13: batchmath, button, currency, datetime, flow_meter, issues,
    plan_slots, plan_step, prefill_offer, repairs, silent_mode, switch and
    wood_fuel. The 11 are the same less button and plan_slots.
  - The 3 left are `flow_meter.py`, `silent_mode.py` and `wood_fuel.py`.
    `grep -cE '^\s*#'` reads 0 in each, so no whole-line comment exists in
    them: that is the null arm working.
- **Seams of the class** (a pool refused for want of a null control), by the
  census rule above:
  - The 10 files only the cap excluded, `button.py` among them: closed in
    this diff.
  - `flow_meter.py`, `silent_mode.py` and `wood_fuel.py`: still refused when
    the pool holds only these files, because no comment-only edit exists in
    them. Named under Forward-carry (the `null_for` pre-check), not closed.
  - A pool's non-Python files: outside this census. The null control is
    tokenized as Python, and this diff does not change that.
- **Why no cap remains.** The cap's only plausible purpose is the edited
  line's width: 60 plus the 15-character ` (null control)` suffix stays
  under PEP 8's 79. Nothing reads that width:
  - `grep -rlnE "ruff|flake8|pylint|pycodestyle|black " .github/` returns
    nothing, and the tree holds no `pyproject.toml`, `setup.cfg` or ruff
    config, so no linter runs in CI.
  - `grep -rnE "len\((line|l|ln|_l|row|lines\[[^]]*\])\) *(>|>=|<|<=)
    *[0-9]{2,3}" tests/*.py tools/` returns only the cap itself
    (`tests/mutation_table.py:2157` at feacede17). This search is a
    heuristic.
  - The run itself: the edited null-control line at button.py:37 is 91
    characters, and it survived every driver that read it (below).
- **Alternatives to dropping the cap:**
  - Measure the indent-stripped length under 60. It clears `button.py`, but
    by the census it still refuses 8 files that hold comments, for a cap no
    reader needs.
  - Write a short `button.py` comment to fit the tool. The orchestrator's
    ruling refuses it as shaping code to the grader.
- **`--pin-killed`:** `PYTHONPATH=tests/hastub python3
  tests/mutation_table.py --pin-killed --scope changed --base origin/main
  --jobs 3` at baf2c4c00 with the three round-2 rows deleted.
  - Printed `PIN KILLED -- 3 new unpinned site(s) against
    d99cadb1235a5e40e250466e656c41c7ce88e641 to drive` and `null control:
    custom_components/heatpump_optimizer/button.py:37 NULL_COMMENT`, which
    survived every driver.
  - 226 GUARD_OFF, 228 GUARD_OFF and 230 RETURN_DEL each read `pinned --
    killed by tests/debug_collect.py`.
  - Result: `PIN KILLED: 3 pinned, 0 left unpinned`, rc=0. A site that lived
    would print under `left unpinned`, and the run would write no row for it.
  - The rows are the tool's own (`Recorded by mutation_table.py
    --pin-killed`), byte-identical to 077a87b02's (`git diff --cached
    077a87b02 --quiet -- tests/mutation_ledger` exit 0).
- **`tests / mutation`'s own command:** `PYTHONPATH=tests/hastub python3
  tests/mutation_table.py --scope changed --base origin/main --max 10
  --jobs 3` at 525e20691.
  - Ratchet line: `3620 unpinned site(s) of 6579 candidate sites, 3620 at the
    ratchet base d99cadb1235a5e40e250466e656c41c7ce88e641`. The run drew
    `3 mutant(s) over 1 file(s)`, each `ok ... killed by
    tests/debug_collect.py`.
  - The null control button.py:37 survived every driver.
  - Result: `0 survivor(s) of 3 evaluated = 0.0%, cap 20.0%`, `MUTATION
    TABLE PASSED`, rc=0.
  - Host caveat: the drivers this tool spawns get `PYTHONPATH=tests/hastub`
    forced, so the wrapper above cannot reach them; this run used a scratch
    venv over venv-ci's packages whose `sitecustomize` hides
    `_remote_debugging`. Without it, the same command at this head read
    `MUTATION TABLE INCONCLUSIVE` on `baseline tests/entities.py: rc=1`, the
    macOS task-port crash.
  - The control: CI's run of the same command at feacede17 refused (job
    124161424410, `no full-line comment in any file in the pool`).
- **Scoped gate:** `python3 tests/closure.py select --diff $(git merge-base
  origin/main HEAD) --workdir "$D"` at 525e20691 printed `MODE: SCOPED --
  16 script(s) run, 17 scoped out.` Each of the 16 was run (see Gate).
- **#2499**, from round 2 at 7fed51072:
  `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_demand_overbook.py`.
  - Arm `nometer_half`: `scale 1.858` (true 1.0) and `plan/deliv 1.908`.
  - The null arm reads `plan/deliv 1.165`, and `meter_half_oracle` reads
    1.016. Round 1 read the same three at 855d1bbac.
  - No learner or optimizer line has changed in this PR, so the figure is the
    base's. Over-booking on a no-meter install is not met.
- **P9 grid**, from round 1 at its merge base 507a9ec26: `node
  tests/card_browser.mjs` with `P9_DEBUG=1`, run with and without the
  storage reset (`localStorage.clear(); sessionStorage.clear()` after each
  `page.goto` in `p9Grid`).
  - Without the reset, all browser checks pass, with 850 box-intersecting
    pairs inked.
  - With the reset, 1190 pairs are inked, and `P9 grid: no two text runs
    share ink` FAILs with 30 entries.
  - The 30 entries are 15 in `wood_alert` and 15 in `wood_lane`, all at 375 px.
  - The rule: `P9_DEBUG`'s `overlap` array, counted by each entry's cell
    prefix.

## Gate

At 525e206910e181e8839d3efb979d6f4c8d6861f9: one run of each script
`scope.run` names, in its order, with `PYTHONPATH=tests/hastub` and
`GOLDEN_MODE=drift` against the merge base. `card.mjs` and `card_drift.mjs`
take the plan payload `tests/plan_view.py` writes. `entities.py` ran through
the macOS wrapper named under Head.
- `tests/arch_score_head.py`: exit 0, `ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED`
- `tests/config_flow_steps.py`: exit 0, `ALL 534 checks PASSED`
- `tests/debug_collect.py`: exit 0, `ALL 159 DEBUG COLLECT CHECKS PASSED`
- `tests/deployment_shape.py`: exit 0, `ALL DEPLOYMENT SHAPE CHECKS PASSED`
- `tests/doc_claims.py`: exit 0, `ALL 203 checks PASSED`
- `tests/entities.py`: exit 0, `ALL 2489 ENTITY CHECKS PASSED`
- `tests/env_drift.py`: exit 0, `NO STALE FIXTURE: 5 committed fixture(s) still match what this tree computes`
- `tests/features.py`: exit 0, `ALL 4605 FEATURE CHECKS PASSED`
- `tests/finite_boundary.py`: exit 0, `ALL 108 FINITE BOUNDARY CHECKS PASSED`
- `tests/golden.py`: exit 0, `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`
- `tests/harness_headers.py`: exit 0, `ALL 112 HARNESS HEADER CHECKS PASSED`
- `tests/plan_view.py`: exit 0, `plan reason codes, price provenance and slot energy OK`
- `tests/card.mjs`: exit 0, `ALL CARD CHECKS PASSED`, run with
  `NODE_OPTIONS=--max-old-space-size=6144`. At node's default heap it
  aborts (exit 134, `JavaScript heap out of memory`) on this host, and so
  does the merge base d99cadb12 with the same command, so the abort is the
  host's and not this diff's; no card line moved in round 3.
- `tests/card_drift.mjs`: exit 0, `card_drift: identical in all 45 states`
- `tests/structure.py`: exit 0, `STRUCTURE RATCHET PASSED`
- `tests/typing_ruler.py`: exit 0, `ALL 12 typing-ruler source checks PASSED`
  (with `HPO_TYPING_PYTHON` set to the seat's venv-ha, as the seat shim
  sets it; without it the run reads 11 checks, the venv-ha arm skipped).

## Unpinned sites

Round 3. The three sites the #2809 rewrite adds carry `killed_by` rows that
`mutation_table.py --pin-killed` recorded (Figures). The round-2 rows from
the scratch script are replaced.

- `custom_components/heatpump_optimizer/button.py:226 GUARD_OFF` (`if collector is None:` -> `if False:`): killed by
  `tests/debug_collect.py`. Anchor `GUARD_OFF 88fa31c4`.
- `custom_components/heatpump_optimizer/button.py:228 GUARD_OFF` (`if collector.final:` -> `if False:`): killed by
  `tests/debug_collect.py`. Anchor `GUARD_OFF 7cf2cf8c`.
- `custom_components/heatpump_optimizer/button.py:230 RETURN_DEL` (`return {}` -> `pass`): killed by
  `tests/debug_collect.py`. Anchor `RETURN_DEL fc97300a`.

No site lives, so no test was added and no `-- lives` line is owed. The
`tests/mutation_table.py` change adds no site that `mutation-autofix` could
pin, because that lane mutates only `custom_components/`. The entities.py
check and mutants A and B pin the predicate (Mutation proof).

## Red checks

- `tests / mutation` at feacede17: red (job 124161424410), `MUTATION TABLE
  REFUSED -- no full-line comment in any file in the pool`.
  - Cause: the 60-character cap in `null_control`.
  - Answer: the predicate fix in baf2c4c00. The same command reads
    `MUTATION TABLE PASSED` at 525e20691 (Figures).
  - Cheaper detector: a `null_for` pre-check over the diff's pool in
    `tools/pr/ci_predict.py` (`prepr.sh` step 6d). It would have shown the
    refusal in seconds, before the handoff. Its standing cost is one
    tokenize pass per pool file on each `prepr.sh` run. Under the
    orchestrator's ruling it is carried, not built (Forward-carry).
- `tests / mutation` at 7c43d8fb1 (round 1): red, `3623 unpinned site(s)
  against 3620`. Round 2 answered it with the three rows, and this round
  re-records them with `--pin-killed`. The ratchet line now reads 3620
  against 3620.
- `tests / mutation-autofix` at 7c43d8fb1 (round 1): red,
  `skip-measure-failed`. `--pin-killed` refused the same pool for the same
  null-control reason. The predicate fix answers it. The autofix job
  measures with the base's copy of `mutation_table.py`, which keeps the cap
  until this merges; at this head the rows are recorded, so the job has
  nothing to pin. The cheaper detector is the same pre-check.
- No other check went red on this branch. The P9 reset, which would turn
  `tests / browser` red, is withheld rather than handed off red.

## Forward-carry

- **A `null_for` pre-check in `tools/pr/ci_predict.py`, the cheaper
  detector.** `prepr.sh` step 6d predicts the `mutation` ratchet but not the
  null-control refusal, so a pool with no null control first shows red in
  CI (#2997, rounds 1 and 2). The check runs `mutation_table.null_for` over
  the diff's pool of candidate sites and prints `PREDICT tests / mutation NO
  NULL CONTROL` when it returns None. `ci-autofix.md`'s table should name
  the refusal in the same change, since no autofix job repairs it. After
  this PR the refusal remains only for a pool of comment-free files, which by
  Figures' census rule are `flow_meter.py`, `silent_mode.py` and
  `wood_fuel.py`. Destination: the R10-UX-HEALTH group's `carry` list on
  `dev/programme/rosters/wave-r10-groups.json` on handoff/audit-r10-roster at 84ddbfbcfc48e248c450a1e8cf57a63bbf470038, which does not hold it yet; the orchestrator writes it (this seat's
  brief). Control for the carry: on a branch whose pool is only
  `flow_meter.py`, the pre-check prints the refusal; on this head's pool
  (`button.py`, null control at line 37) it prints nothing.
  Carry: R10-UX-HEALTH
- **P9 grid state leak (carry 17), with the collision it hides.**
  - `p9Grid` mounts every state of a cell in one browser context. The
    `hidden_series` state's chip press (`["chip", "price"]`) persists in
    localStorage into the later states, among them `wood_alert` and
    `wood_lane`.
  - With a reset after each `page.goto`, those two states read the 30
    shared-ink pairs above at 375 px, at the base.
  - Inference, not measured per element: the colliding runs are drawn once
    the price series is visible, which is the only state the leak carries.
    The likely owner is a chart axis's tick labels at narrow width.
  - Fixing it is a chart hunk in the card. This group's architect note keeps
    the group to the Health and Setup seams, so the fix needs the
    orchestrator's after-edge.
  - The reset (four lines in `p9Grid`) must land in the same PR as that fix,
    or `tests / browser` goes red.
  - Destination: carry 17 of the R10-UX-HEALTH group on `dev/programme/rosters/wave-r10-groups.json` on handoff/audit-r10-roster at 84ddbfbcfc48e248c450a1e8cf57a63bbf470038, which holds
    the leak and its reset control. Carry: R10-UX-HEALTH
- **The "driving scale" widget.** The reading and the evidence are above:
  this is the headline score's "Driving" sub-score. The backend publishes
  neither `operation_drivers` nor a heat-pump driver list. The owner's spec
  needs the owner or the orchestrator to confirm the widget. After that it
  needs a backend driver list and the card copy. Destination: carry 14 of
  the R10-UX-HEALTH group on `dev/programme/rosters/wave-r10-groups.json` on handoff/audit-r10-roster at 84ddbfbcfc48e248c450a1e8cf57a63bbf470038, which holds the owner's spec and its
  confirmation step. Carry: R10-UX-HEALTH
- **#2499, no-meter over-booking (plan/deliv 1.908 on `nometer_half`), not
  met.** No learner or optimizer line moves here; the Health copy that says
  the scale is unobservable without a power meter landed in #2976.
  Destination: carries 11 and 20 of the R10-UX-HEALTH group on `dev/programme/rosters/wave-r10-groups.json` on handoff/audit-r10-roster at 84ddbfbcfc48e248c450a1e8cf57a63bbf470038, which
  hold the residual and its harness arms (`nometer_half` against the
  `meter_half_oracle` control). Carry: #2499

## Friction

- `fixer-brief: contradiction`: residual item 1 asks for a topology whose
  place is outside `SETUP_CONFIGURE_PAGE`. The card's box list is literal and
  all eight places are in the map, so no topology reaches the fallback. The
  case withdraws a map entry instead. Carry: R10-UX-HEALTH
- `fixer-brief: stale`: carry 5 says dropping the render from
  `openSetupSlot` is unpinned at base. At 507a9ec26 `Assign redraws the
  dialog on the Setup page` kills it. Carry: R10-UX-HEALTH
