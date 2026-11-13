# Dimension coverage audit, round 10 (read-only)

Baseline: `origin/main` at `90c6bc3b07` (detached worktree, fetched 2026-11-13).
Part B's roster is `origin/handoff/audit-r10-roster`, and its RCA is
`origin/handoff-wip/r10-rca-setpoint-latch-deadlock`.
Marks: **[M]** measured by a command run here; **[R]** read, quoted with its line; **[J]** my judgement.
D5 and D6 are out of Part A's subject because a separate seat is rewriting them (R10-D5-D6-FULL-SCOPE). Part B treats them as existing dimensions.

Commands whose output is cited: `python3 tools/audit/check_scopes.py --repo . --ref HEAD`, which printed rc=0 and is
quoted in section A.0. Also `../natural.py`, which reuses `check_scopes.py`'s own `match()` to diff each dimension's natural file
universe against its declared one, plus greps and counts given inline.

---

# Part A — does each dimension cover its whole universe?

## A.0 What the shared machinery proves

**What `check_scopes.py` proves:**

- **[R]** `tools/audit/check_scopes.py:2` says *"Prove the finder scopes are disjoint and complete within each dimension, and cover the tree."*
- **[R]** Completeness is computed over `uni = match(tree, d["universe"])` (`:47`). In `cells` mode the wanted set is `itertools.product(uni, d["steps"], axis_vals)` (`:84`).
- **[R]** Tree coverage (`:103-128`) holds when every tracked path is in **some** dimension's universe or in `_coverage_excluded`.
- **[M]** The run printed: `ok coverage tracked=10924 in_universe=1570 excluded=9354 unclassified=0`, and `ok` for all 16 dimensions with 48 seats.
- **[M]** Per-dimension universe sizes: D0 3, D1 91, D2 91, D3 162, D4 15, D5 100, D6 86, D7 91, D8 6, D9 92, D10 110, D11 1325, D12 91. D13, D14 and D15 have 1 each (`<none>`, no file axis).

**What it cannot prove [J]:**

1. **No per-dimension check that a dimension's own territory is in its own universe.** A file that is in D11's universe and missing from D3's still passes. Examples measured below: `tests/hastub/**` and `tests/closures.json`, both of which D3 needs.
2. **Nothing below file granularity.** In every dimension except D3, D5 and D6, every seat's block is `"files": ["**"]` [M, scopes dump]. So the "cells" are really *steps* × axis. Whether a step visited every store, entity, rule, `except`, guard or price cell in those files is not represented anywhere.
3. **Nothing about the method.** A step whose text says "sample 30–40" is "complete" to the checker once one seat owns it.

**`rotation.json` [R]:**

- `_rule` says: *"rounds[<round>] holds seats …, coverage (step -> deep|spot|none), unfinished ([{step, what}]) … and yield."*
- `finding.schema.json:12-16` defines `coverage.depth ∈ {deep, spot, none}` per **step**, self-reported, with free-text evidence. It has no item count and no denominator.
- The `unfinished` description says *"the next round's dispatch raises them"* (`finding.schema.json`).
- **[M]** `audit-find.js` reads `rotation` only to check that it equals the committed file (`:213`, `:221`) and to write the new round (`:363-370`, `:403`). The finder prompt (`:231-235`) passes no prior `unfinished` or `spot` step to any seat, and `grep -n '\.rounds' audit-find.js` finds nothing else.
- So rotation records partial coverage and does **not** rotate it. Nothing re-dispatches an unreached item.

**[M] Round-10 self-reported step depth from `rotation.json`** (unfinished entries in brackets):

| | steps reported spot / none | unfinished |
|---|---|---|
| D0 | M3, M6 spot | 6 |
| D1 | M4, M5 spot | 6 |
| D2 | M3, M4, M5 spot | 5 |
| D3 | M5 spot | 8 |
| D4 | **all 3 spot** | 3 |
| D7 | M5 spot | 2 |
| D8 | none | 1 |
| D9 | none | 5 |
| D10 | none | 2 |
| D11 | **all 4 reported steps spot** (M5 absent) | 4 |
| D12 | M3 spot | 3 |
| D13 | none | 1 |
| D14 | none | 6 |
| D15 | M7 spot, M5 and M8 none | 5 |

**Cadence [R]:**

- `audit-find.js:90`: `CADENCE = { …, D5: 2, D6: 2, D11: 3, D13: 3 }`.
- `EVERY_DIM_ROUNDS = new Set([9, 10])`.
- From round 11, D11 and D13 run only on rounds divisible by 3, and D5 and D6 only on even rounds. That is a per-round coverage gap of 100 % in the off rounds [J].

**The finder contract, COMMON.md [R]:**

- `:31` *"Measure only the cells your task names."*
- `:86` *"Everything you checked that held, each with the command and the number"*. This lists what was checked, never what exists.
- `:93-94` the report has *"what you could not finish"*.
- `:104` *"Aim to return within about two hours of wall clock. Prefer three findings … over ten"*. This is a time cap with a stated preference for depth over breadth.
- No line asks for the size of the universe the step ranges over, or for the items not reached. The `coverage` object's evidence is free text. So **coverage is not visible as a denominator in any dimension** [J], unless a brief adds one (D10's tier table; D13's populations).

## A.1 Per dimension

### D0 — price optimality

1. **Brief [R]** `D0.md:3` *"Price optimality. Specifically hunt for sub-optimal planning."*
   - Natural universe: every solver path and plan cell.
   - [M] The import closure of `optimizer.py` and `dhw_planner.py` is 22 modules, plus `coordinator.py`, which gives 23.
   - [M] Two `_multi_start_minimize(` call sites (`optimizer.py:4691`, `:5285`).
   - The grid of step 4 (`D0.md:34-36`): 8 price × 5 weather × 2 topologies × DHW on/off × valve × wood × 3 horizons, which is ≥ 480 cells [J, arithmetic on the brief's own axes].
2. **Declared universe [M]:**
   - 3 files: `optimizer.py`, `thermal_model.py`, `coordinator.py`, crossed with 7 steps and 8 price profiles.
   - **20 of the 23 solver-closure modules match no D0 cell.** Among them are `dhw_planner.py`, `batchmath.py`, `tariff.py`, `plan_step.py`, `manual_plan.py`, `slot_drivers.py`, `wood_fuel.py`, `pv.py` and `flow_lift.py`.
   - The axis holds price profiles only. Weather, topology, DHW, horizon and wood are not axes, so check_scopes cannot see them.
3. **Sampling and early stops:**
   - **[R]** `:24` *"Challengers, cheapest first"* is ordered, with no stated stop. Round 10's unfinished entry reads *"No global outer bound … not raced"* [R rotation].
   - **[R]** `:36` *"Report per cell"* is exhaustive in wording.
   - **[M]** Round 10's unfinished list contains *"valve storage, wood, horizon 6/48 h and coordinator captures not run"* twice and *"closed loop cut after 2 of 7 cells"*.
   - **[J]** Of the step-4 grid, round 10 ran roughly the price × weather plane at one topology and horizon. That is well under 20 % of the ≥ 480 cells.
   - Already exhaustive: step 4's wording and step 6's "every cell with a gap".
4. **Coverage visible:** no. The report has no cell count. Leave-one-out (COMMON.md :65-68) asks for "at least five cells", which is a floor, not a denominator [R].
5. **Full form:**
   - Feasible as a mechanical grid [J]: an enumerator emits the cell list, and the ledger marks each cell raced, feasible-parity checked, or not reached.
   - About 480 cells × about 10 s per race is about 1.3 h CPU per round. That is 1 seat plus 1 compute-heavy seat for the challengers [J].

### D1 — robustness and stability

1. **Brief [R]** `D1.md:3` *"Robustness and stability — lifecycle, staleness, executor boundaries, store corruption, guards."*
   - **[M] Natural universe:**
     - 17 `store.DOMAINS` keys, and 14 `*_STORE_VERSION` constants.
     - 254 `except` clauses in 55 files, of which 98 are broad (`except Exception`) in 29 files.
     - 18 `async_track_*`/`call_later` timers in 6 files; 9 listener registrations; 11 task creations; 8 executor jobs.
     - 8 `services.async_call(` actuator writes in 4 files.
     - 295 staleness references in 34 files.
2. **Declared universe [M]:** `custom_components/heatpump_optimizer/*.py`, 91 files, crossed with 6 steps. Missing: the card JS, 1 file of 16,407 lines (a client-side staleness surface) [J, minor].
3. **Sampling and early stops:**
   - **[R]** `:19` *"setup → first refresh → reload mid-solve → unload mid-solve → setup again"*. This is **one scripted lifecycle path**. Options-update reload, `async_migrate_entry`, restart with persisted state, and service calls during unload are not enumerated [J].
   - **[R]** `:25` *"Per store, at least 200 seeded mutants"* is exhaustive over stores (17) and a random sample of each store's mutation space. Valid **old-version** payloads are not a mutant class. The setpoint-latch RCA quotes this gap (Part B).
   - **[R]** `:41` *"Each swallowing try/except"* and `:45` *"Each parse"* are exhaustive in wording.
   - [M] Round 10 marked M4 (executor boundary) and M5 (guards) `spot`. The share of the 98 broad excepts examined is not recorded anywhere.
4. **Coverage visible:** no.
5. **Full form:**
   - A mechanical enumerator for M2, M5 and M6: grep `except`, `Store(`/DOMAINS, and parse sites into a ledger, one row each.
   - About 98 + 17 + about 20 parsers is about 135 rows. At 2 rows per seat-minute that is about 1 extra seat [J].

### D2 — mathematical and physical sanity

1. **Brief [R]** `D2.md:3` *"… the optimizer's objective, the thermal model, COP and derates, tariff and price arithmetic."*
   - Natural universe [M]: the import closure of the solver, tariff, grid_fee, price_model and sysid, which is 32 modules, plus 190 numeric constants in `const.py`.
2. **Declared universe [M]:** 91 files, a superset. 0 natural files are missing.
3. **Sampling and early stops:**
   - **[R]** `:32` *"gradient versus a central finite difference at random points"* samples, with no count.
   - **[R]** `:52` *"sweep"* gives no grid and no count.
   - **[R]** `:38-39` step 5 lists noise models *"white, quantised (0.1 °C) and drifting noise"*. R10-N-confounded-learner [R :80] says *"Every perturbation in it is measurement noise"*, so model-error covariates were never in the list. This is a method that cannot see a class, not a sample.
   - **[R]** R10-RCA-COP-PARTLOAD: D2 step 2 ran every round from 3 to 10, and the six-release COP defect was found by D0. That is process state (c).
   - [M] Round 10 marked M3, M4 and M5 `spot`.
   - Exhaustive steps: `:29` *"on every golden fixture"*, `:24` *"every derate"*, `:31` *"every penalty term"*.
4. **Coverage visible:** no.
5. **Full form:** an identity × operating-point ledger [J]. Each identity gets a stated grid instead of "random points" or "sweep", and each constant in `const.py` (190) gets an owner identity or "out of scope". About 1–2 seats [J].

### D3 — test-suite gaps

1. **Brief [R]** `D3.md:3` *"Test-suite gaps — what the suite cannot fail on. Unnecessary test suite resource use."*
   - Natural universe [M]: 91 production modules and the card, 60 top-level test scripts, `tests/hastub` (35 files), and the budget and closure JSONs.
   - Guard candidates [M]: 3,511 `if`/`elif`, 676 `min`/`max`/`clip` and 254 `except`, about 4,441 sites.
2. **Declared universe [M]:**
   - 162 files. Natural is 212, so **50 are missing**: 35 under `tests/hastub/**` and 15 `tests/*.json|txt`, including `closures.json`, `ci_budgets.json` and `stress_budgets.json`.
   - Step 5 reads `closures.json`'s *"recorded seconds"* (`D3.md:33`), but that file is outside D3's cells (it is in D11's universe).
   - The stub, which `fixer.md:171` warns *"a green test may pin the stub"*, is not D3 territory either.
3. **Sampling and early stops:**
   - **[R]** `:15-17` *"Weight by consequence. Sample 30–40 mutants with a recorded seed, no module more than four"*.
   - **[R]** `:27-28` *"the top six survivors; only those become findings"*.
   - [M] Round-10 D3-s2 reported *"seed 10, 36 mutants, <=4 per module … RESULT sampled=36"*.
   - Share: about 36 / 4,441 ≈ 0.8 % of guard sites per seat, at most 40 of 91 modules per seat. Over 3 seats, ≤ about 2.5 % [J, arithmetic].
   - Findings are capped at 6 per round, whatever survives.
   - **[J]** By construction, a kill-based method cannot see a test that **asserts the defect as intended** (`_pa_upgraded`, Part B).
   - Exhaustive steps: step 5 (per-script resource), and step 1's *"any `tests/` check that cannot fail"*.
4. **Coverage visible:** partly. The sample size is recorded (`sampled=36`). The candidate count is not required.
5. **Full form:**
   - The nightly `mutation-autofix` and `tests/mutation_ledger/` already mutate `custom_components/` [R fixer.md:32]. The honest form is to make D3's denominator *that ledger*: every site pinned / survived / not run, with D3 auditing the unpinned remainder each round instead of re-sampling 36.
   - Cost is about the same 3 seats, but over the ledger's remainder [J].

### D4 — UI/UX

1. **Brief [R]** `D4.md:3` *"UI/UX — the card and the config flow, including grouping and setup ergonomics."*
   - **[M] Natural universe:**
     - 5 card pages (`tab("plan"|"savings"|"health"|"advisor"|"setup")`, card `:11160ff`).
     - 45 `card_drift.mjs --list` states.
     - 15 config and 26 options steps in `strings.json`.
     - 3 repair-flow `async_step_` in `repairs.py`.
     - 5 blueprints.
     - 3 translation files: **de, en, sv**.
2. **Declared universe [M]:** 15 files. Natural is 20, so 5 are missing: `repairs.py` (user-facing repair flows), `notifier.py`, `narrative.py` (the plan told in sentences), `frontend.py` and `issues.py`.
3. **Sampling and early stops:**
   - **[R]** `:15` *"`sv` and `en`"* covers 2 of 3 shipped languages. The German catalogue is never rendered. [M] Main went red on missing `de` keys (R10-HOTFIX-MAIN-FAST-1109).
   - **[R]** `:13-14` *"drive every state"* is exhaustive. The state space is 45 × 3 viewports × 2 themes × 2 languages × reduced-motion × coarse pointer = 1,080+ renders.
   - **[M]** Round 10 reported **all three steps `spot`**.
   - **[J]** No step varies the environment (content blockers, themes other than the defaults). R10-HOTFIX-CARD-HEALTH-TEXT was class names hidden by a content blocker plus dark-theme ink/surface pairs.
4. **Coverage visible:** no.
5. **Full form:**
   - A mechanical render matrix with a ledger row per (state, viewport, theme, language, a11y mode), and a rubric row per flow step (41 + 3 repairs + 5 blueprints).
   - About 1,080 renders at about 2 s each is about 40 min in one Chromium seat. The rubric needs about 1 more seat [J].

### D7 — architecture and maintainability

1. **Brief [R]** `D7.md:3` *"… coordinator.py's size, … and everything this year's train introduced."*
   - Natural universe [M]: 91 Python modules plus the card JS (16,407 lines, the second-largest module).
2. **Declared universe [M]:** 91. **The card JS is missing**, so a 16k-line module sits outside the architecture dimension. It is in D3, D4, D5 and D9 only.
3. **Sampling and early stops:**
   - **[R]** `:24-27` *"Each addition since v4 (…11 named…): a spot mutation a test fails on"*. That is one mutation per feature, for a fixed list of 11 rather than "everything this year's train introduced". Round 10 marked M5 `spot` [M].
   - **[R]** `:32-33` *"Guideline bar: 150 % of the cells' 30 % share. A review trigger, never a target"*.
   - Exhaustive steps: step 1 (every ratchet metric), step 6 (AST reachability over the package), and step 8 (*"Per rule written twice, enumerate implementations by a seam rule"*).
4. **Coverage visible:** partly. The structure metrics have a fixed denominator.
5. **Full form:** add the card to the universe. Replace the step-5 list with the enumerated set of feature groups merged since the last round, from the roster's `done` groups [J]. Cost is unchanged in seats, plus about 0.5 seat for the card.

### D8 — sensor verification and ordering

1. **Brief [R]** `D8.md:3` *"… every entity, constructed against realistic coordinator payloads in each topology/feature combination …"*
   - **[M] Natural universe:**
     - 6 platforms (`__init__.py:132-137`: SENSOR, BINARY_SENSOR, BUTTON, CLIMATE, SWITCH, **DATETIME**).
     - 82 `strings.json` entity translation keys (sensor 62, binary_sensor 6, button 6, switch 6, climate 1, datetime 1).
     - 3 translation files.
2. **Declared universe [M]:** 6 files. Natural is 12, so 6 are missing: **`datetime.py`** (a registered platform), `strings.json`, `icons.json` and `translations/{de,en,sv}.json`.
3. **Sampling and early stops:**
   - **[R]** `:18-19` *"construct every entity of every platform"* is exhaustive.
   - **[R]** `:35-36` *"compare `strings.json` with both languages"*. There are three.
   - **[R]** `:30-31` operating-state checks are done *"in a DHW-only cell … and at minimum modulation"*: two named cells.
   - [M] Round 10: all steps deep.
4. **Coverage visible:** no denominator is required. The matrix "graduates" with *"one `RESULT` line per violation class"* (`:41-42`), which reports violations, not entities checked.
5. **Full form:** already mechanical [J]. Add `datetime.py` and the string files to the universe, change "both" to "every shipped language", and print `entities=N cells=M checked=N×M` in the RESULT header. That costs 0 extra seats.

### D9 — CPU and memory (Pi-class)

1. **Brief [R]** `D9.md:3-15` lists priorities, among them *"renders per gesture"* and *"per-cycle loop work outside the executor"*.
   - Natural universe [M]: hot paths are the 2 solver call sites and the DHW loops. Scheduled jobs are 18 timers in 6 files. The card has 16,407 lines.
2. **Declared universe [M]:** 92, equal to natural by file.
3. **Sampling and early stops:**
   - **[R]** `:24-26` fixes 4 solve configurations for SSE per gradient.
   - **[R]** `:27-29`: full solves per cycle are counted over *"one coordinator cycle"*.
   - **[R]** `:34`: loop-thread work is one aggregate number per cycle. No timer or job is enumerated.
   - **[J]** *"renders per gesture"* is a stated priority (`:7`) with **no metric definition** under `## Metric definitions` (`:19-41`). So the card's runtime cost is a priority with no method.
   - [M] Round 10: 5 unfinished entries.
4. **Coverage visible:** no.
5. **Full form:**
   - A measurement dimension cannot be exhaustive over workloads [J].
   - The honest form is a ledger of **cost centres**: every scheduled job (18), every executor job (8), every listener (9), each solve path, and each card gesture. Each gets measured, carried from a previous round with its SHA, or not reached. Rotate the "not reached" rows.
   - About 40 rows; 2 seats [J].

### D10 — HA quality scale

1. **Brief [R]** `D10.md:3` *"Adherence to home assistant integration platinum quality requirements."*
   - Natural universe: the rules. **[M]** The brief lists 54 rules. The upstream `rules/` directory, fetched today via the GitHub contents API, lists 54, and `comm -3` printed nothing: the sets are identical.
2. **Declared universe [M]:** `custom_components/heatpump_optimizer/**`, 110 files. 69 files that rules read are missing: `README.md` and the 7 `docs/*.md` (docs-* rules), the 60 `tests/*` scripts (config-flow-test-coverage, test-coverage), and `hacs.json`.
3. **Sampling and early stops:**
   - **[R]** `:12` *"execute one check per rule"*. That is exhaustive and mechanical, the model case.
   - **[J]** "One check per rule" can grade `done` on one site of a rule that has many: R10-N-log-flood [R :65-66] says *"the round-10 D10 seat graded it `done`"*, while 77 unlatched warnings existed.
4. **Coverage visible:** yes, the tier table (`:34-35`).
5. **Full form:** widen the universe by 69 files. For per-site rules (log-when-unavailable, entity-*, action-exceptions), require the check to enumerate sites and report `sites=N violations=k`. That costs 0 extra seats [J].

### D11 — governance mechanisms

1. **Brief [R]** `D11.md:3` *"Governance mechanisms and policy — audited against public golden standards …"*
   - **[M] Natural universe:**
     - 18 workflow files with 64 jobs.
     - 65 `dev/governance` files (16 decisions, 16 dimensions, 18 roles, 10 rules, 5 config).
     - 576 `tools/` files.
     - 1,086 first-parent merges on main since v7.0.0.
2. **Declared universe [M]:** 1,325 files. Against my natural set the only real misses are `hacs.json` (release metadata, which is in D6) and nothing else material. My first natural set wrongly included behaviour tests, which belong to D3.
3. **Sampling and early stops:**
   - **[R]** `:59` *"Conformance, sampled, with the sample and how it was drawn stated"*. The population is 1,086 merges since v7.0.0 [M].
   - [M] Round 10 D11-s2: *"M3 conformance sample and staleness not executed"*. All 4 reported steps were `spot`.
   - **[R]** `:16-17` *"One row per refusal a seat can meet"* is an exhaustive inventory.
   - **[R]** Cadence 3 (A.0).
4. **Coverage visible:** partly. "One fraction per obligation" (`:64`) is a denominator, over a sample.
5. **Full form:** conformance is computable over the whole merge population by API, as D13 already does for yield. Replace "sampled" with "every merge in the window". The inventory gets a ledger. About 1 seat [J]. Cadence 1.

### D12 — generalization

1. **Brief [R]** `D12.md:3` *"the integration should be possible to use with a wide range of setups and heat pumps."*
   - Natural universe [M]: 48 `CONF_*ENTITY*` optional slots, plus topologies, control surfaces, the card, blueprints and translations.
2. **Declared universe [M]:** 91. 9 missing: 5 blueprints, 3 translations and the card. The card renders per topology, so a card that breaks on a two-zone plant is in no D12 cell [J].
3. **Sampling and early stops:**
   - **[R]** `:31` *"Derive the cell count; do not carry one"* and `:35` *"every optional entity both mapped and omitted"* are both exhaustive.
   - **[R]** `:39-41` *"A surface the tree does not implement is not a cell"* is a bounded universe.
   - [M] Round 10: M3 (heat-pump axes) `spot`.
4. **Coverage visible:** yes, since it counts failing cells (`:45-46`), but no total-cells line is required.
5. **Full form:** already an enumerator [J]. Require `cells=N failed=k not_run=r` in the report and add the card. 0 extra seats.

### D13 — process yield and cost

1. **Brief [R]** `D13.md:3` *"a governance structure that enforces this and has good first pass yield."* Natural universe: every merge in the window [M: 1,086 since v7.0.0].
2. **Declared universe:** `<none>`, with steps only. That is correct for an API dimension.
3. **Sampling:** none. **[R]** `:16-17` *"every count derived at your own window"*, and *"Population: merged pull requests"* (`:19`) is exhaustive. **[R]** Cadence 3.
4. **Coverage visible:** yes. `api_failures printed beside the count` (`:22`) is a denominator.
5. **Full form:** already exhaustive. Cadence 1 is the only change [J].

### D14 — recurring bug classes

1. **Brief [R]** `D14.md:6` *"build the detector that enumerates every seam of each"*.
   - **[M] Natural universe:** 55 classes in `bugclasses.json`: 30 barriered, 19 open (12 production, 7 instrument), 5 detector, 1 prototype-only.
2. **Declared universe [M]:** `<none>` with a `class_status` axis (open, prototype-only, detector, barriered, nightly-replay). That is complete over statuses.
3. **Sampling and early stops:**
   - **[R]** `:16` *"Pick two or three `open` production classes: most rounds, then severity."*
   - Share: 2–3 / 12 open production classes = 17–25 % a round. 0 % of the 7 open instrument classes.
   - Barriered classes are re-checked only at step 1 and 5 level by s2.
   - **[R]** `:30-32` the stop rule is per round, not per class.
4. **Coverage visible:** no. Which classes were not picked is not required.
5. **Full form:**
   - Every open class gets a detector, rotating the remainder with the rotation recorded per class.
   - Every barriered class gets its barrier re-run as a recurrence check, which is mechanical (12 of 18 round-9 barriered classes have round-10 instances, Part B.4c).
   - Mechanically, 19 detectors at about 1 seat per 3 classes is about 6 seats for one pass, or 3 seats over 2 rounds with rotation [J].

### D15 — debugging from a live bundle

1. **Brief [R]** `D15.md:3` *"a debugging run from a diagnostics data export"*.
   - Natural universe: every section of the bundle given (stores = 17 domains, `cycle_rows`, `payload_snapshots`). Across rounds, the universe of installs is unbounded.
2. **Declared universe:** `<none>`, with steps only.
3. **Sampling:**
   - **[R]** `:15` *"No real bundle: every step `unfinished`"*.
   - **[R]** `:26` step 7's row scan is exhaustive over rows.
   - **[R]** `:27` *"Each step-7 anomaly"* is exhaustive.
   - [M] Round 10: M5 and M8 `none`, M7 `spot`.
   - The share of installs is one bundle (the owner's) [J].
4. **Coverage visible:** no.
5. **Full form:** exhaustive within a bundle is feasible. Report `rows=N scanned=N anomalies=k` per section. Across installs it is a sample by nature, so state it as such. About 1 seat [J].

## A.2 Summary table

Share examined per round by the sampling steps is [J] from [M] counts.

| Dim | Natural universe | Declared | Share examined per round by sampling steps | Coverage visible | Verdict | Smallest change to "always check everything" |
|---|---|---|---|---|---|---|
| D0 | 23 solver modules; ≥ 480 grid cells | 3 files × 8 price | about < 20 % of grid (valve, wood, horizons unrun) | no | both | universe = solver import closure; axes for weather, topology, DHW and horizon; cell ledger with raced / not-reached |
| D1 | 17 stores, 98 broad excepts, 18 timers, 8 writes | 91 | one lifecycle path; M4 and M5 spot | no | samples in method | enumerate lifecycle paths (incl. migrate, upgrade); old-version payloads in store fuzz; site ledger |
| D2 | 32 modules, 190 constants | 91 | "random points", "sweep"; M3–M5 spot | no | samples in method | stated operating-point grid per identity; model-error covariates in step 5; constant ledger |
| D3 | 4,441 guard sites, 60 scripts, 35 stub files | 162 (−50) | about 0.8 % per seat, top 6 to findings | sample size only | both | universe + `tests/hastub/**` + budget JSONs; denominator = mutation ledger's unpinned remainder |
| D4 | 5 pages, 45 states, 44 flow steps, 3 languages | 15 (−5) | 2 of 3 languages; all steps spot | no | both | add repairs, notifier, narrative, frontend; every shipped language; render-matrix ledger |
| D7 | 91 modules + 16k-line card | 91 (−card) | 11-feature spot list | partly | gaps in scope | add card; step 5 over the round's done groups |
| D8 | 6 platforms, 82 entity keys | 6 (−datetime, strings) | exhaustive (2 of 3 languages) | no | gaps in scope | add `datetime.py` and strings; "every language"; `entities=N` line |
| D9 | about 40 cost centres | 92 | 4 fixed solves, 1 cycle; card has no metric | no | samples in method | cost-centre ledger with rotation; define renders-per-gesture |
| D10 | 54 rules | 110 (−69 docs/tests) | 100 % of rules, 1 site per rule | yes | gaps in scope | add docs, tests, hacs.json; per-site rules report sites=N |
| D11 | 64 jobs, 65 policy files, 1,086 merges | 1,325 | conformance sampled (not run R10); cadence 3 | partly | samples in method | every merge in window; cadence 1 |
| D12 | 48 optional slots × topologies | 91 (−card, blueprints) | exhaustive; M3 spot | partly | gaps in scope | add card, blueprints; `cells=N not_run=r` |
| D13 | 1,086 merges | none | 100 %; cadence 3 | yes | covers everything (when it runs) | cadence 1 |
| D14 | 55 classes (19 open) | status axis | 2–3 of 12 open production (17–25 %); 0 of 7 instrument | no | samples in method | every open class each round or recorded rotation; barrier re-run for every barriered class |
| D15 | bundle sections; installs unbounded | none | per bundle exhaustive in wording; M5, M8 none | no | samples in method (by nature) | per-section rows=N scanned=N; state the install sample |

## A.3 One rule or per-dimension changes?

**[J]** A single COMMON.md rule would close most of the gap: every finder names the enumerator of each step's universe, reports `universe=N examined=n not_reached=[…]`, and lists the remainder; the schema requires it; rotation dispatches the remainder next round. It would make every row's coverage visible and turn D1, D8, D10, D12, D13 and D15 into honest full-coverage dimensions with no new seats.

It cannot by itself fix method text that **instructs** sampling or a fixed short list. Those need their own brief change:

- D3 ("Sample 30–40", "top six")
- D14 ("Pick two or three")
- D11 ("Conformance, sampled")
- D2 ("random points", noise-only perturbations)
- D0 (axes not in scopes)
- D9 (no card metric; cost centres not enumerated)
- D7 (a fixed 11-feature spot list)
- D4 (2 of 3 languages)

Universe edits for D0, D3, D4, D7, D8, D10 and D12 are scopes.json changes. They also need a per-dimension "natural universe ⊆ declared" check in `check_scopes.py`, because today's check is global only.

The cadence (D11, D13 every third round) and the fact that `audit-find.js` never re-dispatches `unfinished` are machinery changes, not brief changes.

---

# Part B — is any dimension missing?

## B.1 Reference attributes against the sixteen briefs

Rows are ISO/IEC 25010 (2023) characteristics plus product-specific rows. "Full" means a brief line names it; "partial" means a step touches part of it; "none" means no brief names it. All quotes are [R].

| Attribute | Covered by | Quote / note |
|---|---|---|
| Functional suitability: completeness | D6 partial | D6 `:3` *"every claim against actual code and data"*. It checks claims, not features. |
| Functional correctness (a feature does what it is for, e.g. away mode, boost) | **partial/none** | D0 checks optimality, D2 equations, D8 entity values. No brief says "each user-visible feature behaves as specified". |
| Functional appropriateness | D4 partial | D4 `:4` *"intuitive, user friendly"* |
| Performance: time, resources, capacity | D9 full (backend); card none | D9 `:3`; *"renders per gesture"* has no metric |
| Compatibility: co-existence, interoperability | D12 partial, D10 partial | D12 `:12-15` *"a different control surface"*; HA versions only via D10's `hacs.json` floor (`D10.md:36-37`) |
| Usability: learnability, operability, error protection | D4 full | D4 `:22-29` |
| Accessibility | D4 partial | D4 `:18-19` *"WCAG AA contrast … hit targets … keyboard tab order"*. No screen reader or ARIA audit. |
| Internationalisation | D4, D8 partial | `D4.md:15` *"`sv` and `en`"*, `D8.md:35-36` *"both languages"*. 3 languages ship. |
| Reliability: faults, recoverability | D1 full | D1 `:3` |
| Reliability: availability over upgrade | **none** | D1 `:23-29` fuzzes *corrupt* payloads. The RCA quote: *"Its store fuzz (step 2) mutates corrupt payloads, not a valid payload from a previous version."* |
| Security: confidentiality, integrity, authenticity | **partial** | D11 `:29-34` (OpenSSF Scorecard of the *repository*); D1 `:45-48` *"hostile payloads"*; D15 `:21` privacy gate on a bundle. Nothing audits the integration's own attack surface (services, frontend static path, MQTT input). |
| Maintainability | D7, D3 full | D7 `:3`, D3 `:3` |
| Flexibility / portability, installability | D12, D10 partial | D10 rules docs-installation-*, D5 `:13` *"installing via HACS"* |
| Safety (ISO 25010:2023 new): operational constraint, fail-safe, hazard warning | **none** | No brief names actuator writes, set-point bounds, or fail-safe state on stop/upgrade. `fixer.md:231` is a layering rule only (RCA §2.6). |
| Product: actuator-write liveness and safety | **none** | as above |
| Product: upgrade and migration of persisted state | **none** | 17 store domains, 14 store versions, config entry v7 [M]; 169 v* tags [M] |
| Product: release notes and user-facing text truth | D6 partial (no release notes) | `RELEASE_NOTES.md` is in D11's universe only [M], and D11 audits mechanism. D6 covers `strings.json` (D6 universe [M]). |
| Product: privacy of diagnostics and logs | D15 partial | D15 `:21` checks a bundle it was given. `diagnostics.py` redaction is not enumerated by any brief. 245 log calls [M] are unaudited for PII. |
| Product: supply chain, dependency pins | D11 partial (repository), D10 dependency-transparency | manifest `requirements` `numpy>=1.24.0, scipy>=1.10.0, threadpoolctl>=3.5.0` [M], unpinned upper bounds; nothing audits them |
| Product: licence and third-party notices | **none, by exclusion** | scopes `_coverage_excluded`: *"{LICENSE,NOTICE}": "… no claim a dimension can test"* [R]. vendored fonts are excluded too. |
| Product: HACS and hassfest conformance | D10 partial; CI | `hassfest.yml`, `validate.yml` exist [M]; D10 rule `brands` |
| Product: observability / explainability ("why did it do that") | **partial** | D8 checks entity values; D15 replays. No brief audits whether reason codes and `narrative.py` explain each action correctly. `narrative.py` is in no D4/D8 universe [M]. |
| Test-vs-intent (a test pinning a defect as correct) | **none** | D3's kill method cannot see it [J]; D6 checks docs vs code, not tests vs intent |

## B.2 Escapes: defects not found by the round's finders

The table covers defects that reached a release or were found by owner, outside or RCA rather than by a finder seat. Sources: roster `origin/handoff/audit-r10-roster` (513 R10 groups [M], 26 `source: outside`, 15 HOTFIX/bug groups touching `custom_components/` [M]), RCAs on main and on the latch branch, and the owner's three of today. Product defects only. Instrument hotfixes (about 45) are excluded as D11/D13 territory.

| # | Escape | Found by | Owning dimension (territory) | Why missed [R/J] |
|---|---|---|---|---|
| 1 | Set-point write held with no release after upgrade (PR 3404, v7.1.12 to 7.1.15; R10-HOTFIX-FLOW-SETPOINT-STUCK) | owner | **no dimension** (actuator liveness, upgrade path) | RCA state (a): *"No contract asks … a refusal on an actuator write path must have a release that needs no person"*; `_pa_upgraded` pins it |
| 2 | Space boost writes a partial flow set-point (since v6.7.17; R10-HOTFIX-BOOST-FLOW-CEILING) | owner | **no dimension** (functional correctness of an actuator write); D3 nearest | the test covers an idle plan only (owner); one state sampled |
| 3a | Config-flow help "the optimizer never writes a recommended space set-point" false since September (`strings.json:595`) | owner | D6 | D6's universe holds `strings.json` [M]; claim-sentence extraction missed it [J] |
| 3b | v7.1.12 release note omits the required user action | owner / RCA | **no dimension** (`RELEASE_NOTES.md` only in D11's universe) | RCA §2.5 |
| 4 | Health tab text missing (v7.1.11; content blocker hides `adv-*` classes; ink/surface pairs) | owner | D4 | all D4 steps `spot` in R10 [M]; no environment axis |
| 5 | Away override persisted but live away off, so the plan heated (R10-HOTFIX-AWAY-LIVE) | owner | D1 (store vs live state) / functional | one lifecycle path in D1 |
| 6 | Away weekend/holiday comfort fields not set back (AWAY-SETBACK) | owner | **functional correctness: none**; D12 nearest | no feature-behaviour dimension |
| 7 | Away presence entity not subscribed, so a 30 min lag (AWAY-PRESENCE) | owner | D1 (staleness) partial | listeners not enumerated |
| 8 | Preheat-for-weather label when the learned scale exceeds 1.1 (PREHEAT-LABEL) | owner | **observability: none**; D8 nearest | reason codes unaudited |
| 9 | Heat-loss learner input defects, 67 kWh/day (LEARNER-INPUTS) | owner | D2 step 5 | noise-only perturbations (RCA confounded-learner) |
| 10 | Savings estimate books a tank-decided first step (SAV-ESTIMATE, v7.0.4/v7.1.1) | owner | D2 (savings identity) | RCA state (c) |
| 11 | COP health watch graded the model against itself (COP-UNMEASURED, v4.0.0 to v7.1.5) | owner | D2/D8 | RCA state (c) |
| 12 | COP law priced no compressor power (v1.0.0 to v7.0.4) | D0 finder (out of dimension) | D2 | RCA state (c): D2 step 2 ran rounds 3–10 |
| 13 | Buffer store absent from single-zone step | RCA | D2/D12 | RCA state (c) |
| 14 | Process-worker reply wait had no deadline (v7.1.2 to v7.1.4) | outside PR 3226 | D1 step 5 | RCA (c): *"never put a live, silent peer"* |
| 15 | Learned-store lifecycle defects (R10-LEARNED-STORE-LOAD) | a fixer | D1 | lifecycle not enumerated |
| 16 | Price fetch failure made every entity unavailable (outside 3437) | outside | D1 | M5/M6 coverage spot |
| 17 | Diagnostics leaked home location, solar option unredacted (outside 3436) | outside | **privacy: none** (D15 checks a bundle, not the redactor) | — |
| 18 | Configured input re-read only after a full interval (outside 3292) | outside | D1 staleness | — |
| 19 | Action cut before await, then stale step (outside 3457) | outside | D1 executor boundary (M4 spot) | — |
| 20 | Valve target accepts a flow temperature, silently drives plan (outside VALVE-TARGET-LABEL) | outside | D4 (validation) / D12 | — |
| 21 | DHW charge settle confounds two learners (outside 3434) | outside | D2 step 5 | noise-only |
| 22 | Learner robustness, 1 of 50 samples for days (outside 3435) | outside | D2 step 5 | noise-only |
| 23 | Water set-point feedback writes the modulation floor (outside 3380) | outside | **actuator: none** | — |
| 24 | Climate native temperature members (outside 3443) | outside | D10/D12 | — |
| 25 | `de` catalogue missing keys on main (MAIN-FAST-1109) | CI | D4/D8 (i18n) | `sv`/`en` only |

Tally [M over this table]: 25 product escapes.

| Owning dimension | Rows | Count |
|---|---|---|
| D1 | 5, 7, 14, 15, 16, 18, 19 | 7 |
| D2 | 9, 10, 11, 12, 13, 21, 22 | 7 |
| D4 | 4, 20, 25 | 3 |
| D6 | 3a | 1 |
| D10/D12 | 24 | 1 |
| no dimension | 1, 2, 3b, 6, 8, 17, 23 | 7 |

Of the 7 with no dimension:

- actuator write (rows 1, 2, 23): 3
- release notes (3b): 1
- functional feature behaviour (6): 1
- observability (8): 1
- privacy (17): 1

**[M] bugclasses beyond the finders:**

- No class carries a `beyond_finding` field at main (`grep -c` = 0).
- 16 classes carry `non_round_instances` (incidents and screens), and 10 of them are instrument classes.
- Production ones: P2 1, P10 2, P11 12, N-restart 1, N-shared-config 7.

## B.3 Candidate missing dimensions

Each candidate below has a one-line owner-style brief, its universe, its method, the rows it would have caught, its overlap, a cut verdict and a cost.

1. **Actuator-write safety and liveness**
   - Brief: *"Every write the integration makes to a real heat pump is bounded, intended, and never held without an automatic release."*
   - Universe [M]: 8 `services.async_call(` sites in 4 files, 32 `log_held(` sites, and write-owning modules `pump_arbiter.py`, `heat_curve.py`, `off_restore.py`, `inputs.py` and `coordinator.py`.
   - Method: an enumerator of write and hold sites. Per site, drive the plan states (idle, partial, boost, DHW-only, upgrade-from-previous-record) and assert the value written equals the documented target. Per refusal, assert a release that needs no person.
   - Would have caught: rows 1, 2 and 23, and plausibly 20.
   - Overlap: D1 (guards), D12 (surfaces).
   - Cut: **new dimension** [J]. Neither D1 ("wedges, leaks, races") nor D12 owns *the written value* or its liveness, and the RCA records state (a).
   - Cost: about 40 sites × 5 states. 1–2 seats.
   - **Supported by the evidence.**
2. **Upgrade and persisted-state compatibility**
   - Brief: *"Every release upgrades from every supported previous release with its persisted state, and behaves as a fresh install would."*
   - Universe [M]: 17 store domains, 14 store versions, config entry v7 migrations, and the 22 v7.* tags.
   - Method: for each domain, produce a valid payload at each of the last N tags (by running that tag's writer), load at HEAD, run one cycle, and compare with the fresh install. Same for `async_migrate_entry`.
   - Would have caught: row 1, plus R9 bug-5 reboot persistence (RC2) and row 5 partly.
   - Overlap: D1 step 2 (corrupt fuzz).
   - Cut: **widen D1 with a step** [J]. Same harness, same seat skills. The universe is bounded and mechanical.
   - Cost: 17 domains × about 5 tags. +1 seat in D1.
   - **Supported.**
3. **Functional (feature) correctness against the documented behaviour**
   - Brief: *"Each user-visible feature does what its documentation and option say, in every state that reaches it."*
   - Universe [J]: features = options pages (26 options steps [M]) plus services (15 [M]) plus switches and buttons (12 [M]).
   - Method: per feature, its documented effect as an executable oracle, driven across plan states.
   - Would have caught: rows 2, 6, 5 and 3a (via behaviour, not text).
   - Overlap: D6 checks text against code, which is a different oracle.
   - Cut: **new dimension** [J]. No current brief has "feature spec as oracle".
   - Cost: about 55 features, 2–3 seats.
   - **Supported** (3 or more rows).
4. **Release engineering and user-facing change truth**
   - Brief: *"Every release's notes name every user-visible change and every action a user must take; version, tag and manifest agree."*
   - Universe [M]: `RELEASE_NOTES.md` (16 headings), 169 tags, manifest and `hacs.json`.
   - Would have caught: rows 3b and R10-HOTFIX-RELEASE-TAG (v7.1.2 showed 7.1.1).
   - Overlap: D6 (truth), D11 (stamp mechanism).
   - Cut: **widen D6** by adding `RELEASE_NOTES.md` to its universe, plus one step "each merged user-visible PR in the window has its note and any required action" [J].
   - Cost: +0.5 seat.
   - **Supported** (2 rows).
5. **Security and privacy of the integration**
   - Brief: *"No input the integration did not produce can make it write, leak or execute, and nothing it exports or logs carries personal data."*
   - Universe [M]: 15 services, the frontend static path, MQTT and external parsers, `diagnostics.py`, and 245 log calls.
   - Would have caught: row 17.
   - Overlap: D1 step 6 (hostile payloads), D15 privacy gate, D11 Scorecard (repository).
   - Cut [J]: **widen** rather than add. D1 step 6 enumerates parsers already, and a "privacy" step (every redaction key, every log argument against a PII list) can go to D15 or D1.
   - A new dimension is not supported by count: 1 row.
   - Cost: +0.5 seat.
6. **Observability and explainability**
   - Brief: *"For every action, the published reason is the true reason."*
   - Universe [M]: `narrative.py`, reason codes, and the advisor and health pages.
   - Would have caught: row 8, and arguably 11 (the health watch graded itself).
   - Overlap: D8 (entity values), D4 (presentation).
   - Cut: **widen D8** with a step "reason-code oracle: each code fires exactly when its condition holds" [J].
   - Cost: +0.5 seat.
   - **Weakly supported** (1–2 rows).
7. **Accessibility and internationalisation**
   - Would have caught: rows 25 and part of 4.
   - Cut: **widen D4** (every shipped language, environment axis, ARIA). Not a new dimension [J].
8. **Test-vs-intent**
   - Brief: *"No test asserts as intended a behaviour the brief, docs or owner rule call wrong."*
   - Would have caught: rows 1 (`_pa_upgraded`) and 2 (an idle-only test).
   - Cut: a **D3 step** [J]: for every test touching an actuator or user-visible value, name the oracle it asserts and its source; flag any test whose oracle is the code itself. A new dimension is not supported separately, since its rows are already counted under candidates 1 and 3.
9. **Supply chain and licence** — **not supported by the evidence**: 0 escape rows [M over B.2].
   - Still, licence is *excluded by fiat* from every universe (scopes `_coverage_excluded`) [R], and manifest requirements have no upper pins [M].
   - Cut [J]: widen D11 (it already runs Scorecard `Pinned-Dependencies`) to the product manifest and `NOTICE`. +0 seats.

**Not supported [J]:** a separate security dimension (1 row), a separate supply-chain/licence dimension (0 rows), a separate i18n dimension (1 row, absorbed by D4). **Supported as new:** actuator-write safety and liveness (3–4 rows) and functional-feature correctness (3–4 rows). **Supported as widenings:** D1 (+upgrade), D6 (+release notes), D8 (+reason-code oracle), D3 (+test oracle audit), D4 (+languages, environments).

## B.4 Convergence towards zero objective bugs

**Operational definition [J, from COMMON.md :38-82 and the schema]:** an *objective bug* is a falsifiable claim about the code at a baseline, with an executed number from a committed harness that hooks a production symbol and moves in the stated direction under a one-line perturbation. Its stop-rule class is `bug`, its severity is set by consequence, and a judge has verified it, not refuted it. Owner and outside escapes count when a hotfix's failing-test-first proof meets the same bar.

**The expected count falls toward zero over rounds iff all of the following hold [J]:**

**(a) No blind spot.** Every objective bug has non-zero detection probability each round.

- Not met. Part A shows sampled methods (D3 about 0.8 % of guard sites per seat; D14 17–25 % of open production classes) and coverage nobody measures.
- Part B shows kinds **no current method can see at all**:
  - an actuator write's held state or wrong value (rows 1, 2, 23)
  - a valid old-version store across an upgrade (row 1)
  - feature behaviour against its documented effect (rows 2, 6)
  - a test that pins the defect as intended (`_pa_upgraded`, row 2's idle-only test)
  - release-note completeness (3b)
  - environment variance in the card (row 4)
  - model-error covariates in learners (rows 9, 21, 22; D2 step 5 lists noise only)
  - diagnostics redaction (17)
- For these the probability is zero by construction, not small.

**(b) Removal beats injection.**

- **[M]** In R10 the record shows 138 finding ids across 75 groups with findings, and all 75 are `done`. Round-10 JUDGE.json holds 96 verdicts (72 verified, 10 weakened) and CATCHUP holds 50 (39 verified).
- **Injection, measured where the record names a fix as cause:**
  - Row 1: PR 3404, an R10 fix.
  - R10-HOTFIX-COMBI-CENSUS-MAIN-RED: PR 3398, R10, main-red only.
  - MAIN-FAST-1109: merge skew of #3372/#3360, R10.
  - Row 2 dates from v6.7.17, which falls in the round-9 window (v6.0.0 2026-08-31 to v7.0.0 2026-10-14 [M]), and the brief names *"the commit that introduced flow_setpoint_for_level"*.
  - Row 4 is a candidate among v7.1.10..v7.1.11 product merges (#3398, #3405, #3433, #3447), which the brief marks *"leads only, not a cause"*.
  - So at least 3 product injections are attributable to R9/R10 fixes, against about 111 verified findings fixed (72 + 39). The removal/injection ratio is ≥ about 30:1 by count [J; the injection count is a floor because no record attributes causes systematically].
- **What bounds injection [R]:**
  - `fixer.md:15` failing test first
  - `:17` mutation proof
  - `:54` *"measured at both ends of its input range"*
  - `fix-review.md:10` re-runs the mutation proof
  - the gate
- **Where it does not:**
  - Row 1 obeyed every one of these, and the RCA quote is *"`fixer.md:54-56` … was obeyed: `_pa_upgraded` is the upgraded end"*. A test can pin the defect as the intended behaviour.
  - No contract asks for an upgrade-path drive or an actuator-liveness criterion.
  - Row 2's test sampled one plan state (idle).
  - Mutation proof shows a test *detects* the change. It cannot show the change is *right*.

**(c) No recurrence.**

- **[M]** `bugclasses.json`: 55 classes, 30 barriered and 5 detector.
- Of 18 classes whose barrier cites a round-9 fix wave, **12 have round-10 instances**: P1 4, P2 34, P3 5, P5 1, P6 4, I1 15, I3 2, I4 2, I5 8, N-structure-blind 6, N-shared-config 14, N-silent-zero 2. The other 6 (P7, P9, I2, N-future-instant, P11, N-restart) had none.
- **[J] Caveat:** an R10 instance may sit in a seam the barrier's rule does not enumerate, or predate the barrier's merge. The ledger records rounds per class, not instance dates against barrier dates. So "recurred after barrier" cannot be told apart from "pre-existing, newly enumerated".
- `defect-root-cause.md:91-93` requires a barrier for *"any instance of a `barriered` class"* [R], so the rule exists. Its effectiveness is unmeasured.

**(d) Production growth.**

- **[M]** 1,086 first-parent merges on main since v7.0.0 (one round), against 665 in the prior round's window.
- R10 admitted 26 outside groups and new features (combi tank, generic heat curve, duty-switch learning) mid-round.
- **[R]** `orchestrator.md:133` *"A round's scope freezes at its register"* freezes *findings*, not features. Owner rulings put outside work at top tier with *"no deferral out of the round"* (roster briefs).
- Nothing bounds new surface per round, so the universe each next round must cover grows [J].

**(e) The measurement.**

- **[R]** `scorecard.py` prints ten report-only lines, among them `E` (escapes: outside groups plus product hotfix groups), `Y_rev` and `H`. *"no line sets an exit code."*
- Per-round judged counts by dimension are derivable only for R8 and R10 [M]:
  - R8: 43 verdicts (29 verified). D7 6, D11 6, D1 4, D2 4, D3 4, others ≤ 3.
  - R10: 96 verdicts plus 50 catch-up. D7 31 + 24, D1 7, D2 6, D13 5, D15 5, D5 4, others ≤ 3, and 18 + 23 non-dimension ids (ARCH, L*).
- No other round has a `JUDGE.json` [M: only round8 and round10].
- **Missing, and needed to tell convergence from a finder that stopped looking:**
  - per dimension per round: `universe=N`, `examined=n` (Part A), `found`, `fixed`, `injected` (with the fixing PR named as cause), and `escaped` (found outside finders, attributed to the owning dimension as in B.2)
  - per class, instance dates against barrier merge dates
- With those, a falling `found` is convergence only if `examined/N` is flat or rising and `escaped` is falling. Today a falling `found` is indistinguishable from a shrinking `examined`.

**Necessary changes, ordered by how many B.2 rows each would have caught [J].** Rows can count under more than one change.

1. **Widen D1 and D2 methods:** lifecycle paths and listeners enumerated, valid old-version store payloads in the fuzz (the upgrade step), and model-error covariates in D2 step 5. Rows 1, 5, 7, 9, 14, 15, 16, 18, 19, 21, 22 = **11**.
2. **Widen D4 and the D2 identity grids:** D4 to every shipped language and an environment axis (content blocker, theme), and D2's savings and COP identities to a stated operating grid instead of "random points" or "sweep". Rows 4, 25, 10, 11, 12, 13 = **6**.
3. **New functional-feature correctness dimension** (the feature spec as oracle), plus a D3 step auditing each test's oracle (test-vs-intent). Rows 2, 5, 6, 3a = **4**.
4. **New actuator-write safety and liveness dimension:** every write and hold site, the written value against the documented target per plan state, and a release that needs no person for every refusal. Rows 1, 2, 23 (and 20) = **3–4**.
5. **Widen D6, D8 and D1/D15:** D6 to `RELEASE_NOTES.md` with a "required user action" step; a reason-code oracle step in D8; a redaction enumerator in D1 or D15. Rows 3b, 8, 17 = **3**.
6. **A denominator rule** in COMMON.md and `finding.schema.json` (`universe`, `examined`, `not_reached` per step), with `audit-find.js` dispatching the unreached remainder next round. It catches 0 rows directly. It is still necessary, because without it condition (a) cannot be shown and no convergence claim can be checked.
7. **Record injection and escape per dimension per round:** a `caused_by` PR field on fixes and hotfixes, scorecard `E` split by owning dimension, and instance dates against barrier merge dates in `bugclasses.json`. It catches 0 rows. It is necessary for (b), (c) and (e) to be measurable at all.

Not on this list, because they are helpful but not necessary for the objective-bug criterion: cadence 1 for D11/D13 (process dimensions), and supply chain and licence (0 rows).
