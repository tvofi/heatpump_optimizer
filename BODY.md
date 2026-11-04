R10-GRADE-DRIVERS: the heat-pump and Driving grades publish drivers in the house grade's interface, every score hover carries its metric in plain words and its current reasons, and the P9 grid starts each state from empty storage, with the ink collision that exposed fixed.

What changed:

- **Heat-pump grade** (`coordinator.machine_score`): publishes `machine_drivers`, one driver `cop_shortfall` whose points are the grade minus 100 (the pump matching its own COP history). Ungraded, it publishes `machine_evidence` instead (`coordinator.machine_evidence`): COP samples per 3 °C outdoor band against `COP_BASELINE_MIN_SAMPLES`, fullest first, and the intervals a learner freeze refused (`MeasuredCop.frozen_refusals`, counted where `_fold_measured_cop` returns `COP_REFUSED_FROZEN`; in memory, since start, not persisted).
- **Driving grade** (new `driving_grade.py`): the day's saving against the flat replay splits exactly into `cheap_hours` (energy bought below the day's running mean, as it was bought) and `dear_hours` (the rest), each weighed against the day's own mean and scaled onto the clipped sample, so they sum to it. They fold with the grade's own EMA and persist beside it in the ledger store (`operation_drivers`, declared in `store.py`); a grade stored before they were kept reads as `earlier_days`, decaying with the EMA. The grade's own arithmetic is unchanged expression for expression.
- **One interface**: `compose_scores` publishes `envelope_drivers`, `machine_drivers` and `operation_drivers` the same way: `{code, points}`, points rounded to one decimal, summing to the grade minus that part's `SCORE_REFERENCE` (house 50, heat pump 100, Driving 0), empty with no grade; `reasons` stays the absent-grade channel.
- **Card**: `scoreDrivers` renders every part's drivers with a signed weight, and the part's own "typical" line when none moves a point; `machineEvidence` renders what an ungraded heat pump waits on; each breakdown row now has a hover (`scoreRowTitle`) carrying its grade or reason, its drivers or evidence, and its metric in plain words, the same line the headline hover gives. `score.part_machine` and `score.part_operation` now say what is measured, the unit, what high and low mean and what no grade means. Every new string has en and sv.
- **P9 grid** (`tests/card_browser.mjs`): `localStorage` and `sessionStorage` are cleared after each `page.goto`. That exposed the carried collision: `wood_lane` at 375 px stacked four value-axis labels into each other. `valueAxis` now labels a tick only a line (one font size) clear of the last label drawn, keeping every tick mark, as `timeAxis` already does for time labels.
- **Structure and architecture**: the Driving grade's booking, daily fold and drivers moved out of the coordinator class into `driving_grade.py` (a per-coordinator side table, the `price_tiles` pattern; only `held()` is handed the coordinator, and `tally` returns a new book that the coordinator rebinds). The structure budgets are re-recorded as an improvement; nothing was raised.

## Head

d113fe68fe87774daf870895b50d436cc319f9d7, a merge of origin/main 8e90d81443317f76f22602a89651f7ca17c633f9 (its tip at 2026-11-04T11:47Z) into the branch cut from c3a279e3252a8b57bb00b5a677318cd4fe20387f. Main's delta reaches this branch's files only in the card (99 lines of shared template rules) and `thermal_model.py`; the gate, the browser grid and `prepr.sh` were re-run at this head, and origin/main has not moved since.

## Mutation proof

Each mutant was applied to one production site in a copy of the tree at 7649fad's code (the Python mutants; the later side-table rename and retyped `published` move none of the three sites) or b713c02's (the card mutants), then the closure script was run. Main's merged delta touches none of the mutated lines. In each Python copy, the extra `and the path that proceeds still stamps a resolvable recorded_at (#363)` red is the copy's own artefact (fixer.md step 2), and appears in every copy.

- M1 `driving_grade.tally`: the cheap-side `_add(book, "kwh_lo", ...)` and `_add(book, "sek_lo", ...)` replaced by `pass`. `tests/features.py` turns red on `R10-GRADE-DRIVERS: the Driving grade's drivers split it exactly -- energy bought under the day's mean pushes it up, energy bought over pulls it down -- and keep summing to it through the EMA`.
- M2 `coordinator.machine_score`: returns `[]` instead of the `cop_shortfall` driver. `tests/features.py` turns red on `R10-GRADE-DRIVERS: a graded heat pump drops its evidence and carries one driver, its distance below its own COP history: none at 100, and a Cusum a quarter of the way to its alarm takes 25 points`.
- M3 `coordinator._fold_measured_cop`: `self._measured_cop.frozen_refusals += 1` deleted. `tests/features.py` turns red on `R10-GRADE-DRIVERS: the heat pump's evidence lists each band's samples, most first, and counts only the intervals a freeze refused`.
- C1 card `scoreDrivers`: the per-part typical line replaced by the house's `score.driver_typical`. `tests/card.mjs` turns red on `R10-GRADE-DRIVERS null control: all-zero Driving drivers show the metric and no reason rows, House unchanged`.
- C2 card `machineEvidence`: returns `""`. `tests/card.mjs` turns red on `R10-GRADE-DRIVERS: an ungraded heat pump shows samples per outdoor band against the requirement, and freeze refusals`.
- A1 card `valueAxis` label thinning: the tree with the storage reset and without the thinning (71a59dc) is the mutant. `tests/card_browser.mjs` turns red on `P9 grid: no two text runs share ink`, with every pair at `wood_lane/375` (text "0" x "1", "1" x "2", "2" x "3"). With the thinning, the same grid run is green and the dumped overlap list is empty.

Failing test first: the head's `tests/card.mjs` run against the base's card turns red on all 7 new `R10-GRADE-DRIVERS` checks and on `each row carries its plain-language explanation`, which now pins the new metric wording. The new `tests/features.py` block imports `SCORE_REFERENCE` and `driving_grade`, neither of which exists at the base.

## Null control

- `tests/features.py`: buying flat all day scores 0, and no Driving driver moves the grade a point (`R10-GRADE-DRIVERS null control`).
- `tests/card.mjs`: a payload whose Driving drivers are all zero renders the metric and the "bought at the day's flat mean price" line, with no reason row, and the House row's hover is byte-equal to the same payload without `operation_drivers`. Perturbation: flipping the sign of `dear_hours` flips its mark from − to + (`R10-GRADE-DRIVERS perturbation`).
- House grade unchanged (Carry 3's precondition, re-measured at the merge base and at the head): `dev/audit/harnesses/r10_scores_envelope.py` prints 40 `tree_grade=` rows and none off 50.0 at both ends; `dev/audit/harnesses/r10_house_grade.py` prints `owner_min=35.2`, `monotone=True` and `drivers_max_gap=0.0` at the head.
- Driving grade: `driving_grade.fold` computes the sample with the base's expressions in the same order. The pre-existing #908 checks in `tests/features.py`, which compare two fold sequences for exact equality and pin the seed to 100, pass unchanged.

## Figures

- `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` at d113fe6: `MODE: SCOPED -- 28 script(s) run, 5 scoped out.`, rc=0, with `tests/features.py` and `tests/card.mjs` among them; `env_drift.py --all origin/main` reads no unclaimed drift, and `card_drift.mjs origin/main` one moved state, claimed.
- `NODE_PATH=/opt/node22/lib/node_modules PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node tests/card_browser.mjs` at d113fe6: ALL BROWSER CHECKS PASSED. Indicative only: CI's browser job decides. At 71a59dc (reset, no thinning) the same run failed `P9 grid: no two text runs share ink`, every pair at `wood_lane/375`.
- `bash tools/pr/prepr.sh` at d113fe6: rc=0.
- `python3 tests/structure.py`: rc=0, after `--record` lowered `max_class_loc` 7975 -> 7971 and `class_excess_loc` 17640 -> 17636 (commit 467ee2d's message carries the reason).
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py`: `claims_true=123`, `claims_false=0`, `arch_map_missing=0`.
- `python3 tools/pr/ci_predict.py --only under-scoped`: no closures, fast, governance or instrument red predicted.
- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_scores_envelope.py`: 40 `tree_grade=` rows, 0 off 50.0, at the base and at the head.
- Goldens: the five coordinator fixtures (`coord_all_features`, `coord_dhw`, `coord_grid_fee`, `coord_minimal`, `coord_two_zone`) gain the new score keys, inserted by path into the committed files (70 lines added, 0 removed). A `golden.py --record --only` here also rewrote float values this box computes differently, so it was discarded: no value is re-recorded on this box. Each fixture, and the card's `score_open`, is claimed.

## Architecture score

`python3 tools/audit/archscore/score.py --diff c3a279e3252a8b57bb00b5a677318cd4fe20387f`: `dS +0.0036 IMPROVES`, `coord_footprint 2381 -> 2375`; no other metric moves. An earlier cut of this branch read `shared_inplace_writes 3 -> 4` (a collaborator writing into the coordinator's day book) and `coord_footprint 2381 -> 2390` (every `driving_grade` function was handed the coordinator); `tally` now returns a new book and only `held()` sees the coordinator.

## Red checks

- `mutation` at d113fe68fe87: red by construction on the 32 site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push.

## Unpinned sites

- custom_components/heatpump_optimizer/coordinator.py:3106 CLAMP_DROP: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/coordinator.py:3107 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/coordinator.py:3167 BOOLOP: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/coordinator.py:3167 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/coordinator.py:3169 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/coordinator.py:5099 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/coordinator.py:10398 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:29 CONST: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:31 CONST: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:42 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:54 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:55 CLAMP_DROP: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:57 BOOLOP: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:57 CMP_BOUND: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:57 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:60 BOOLOP: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:60 CMP_BOUND: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:60 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:61 CLAMP_DROP: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:63 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:68 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:84 BOOLOP: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:84 CMP_BOUND*2: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:85 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:92 CLAMP_DROP: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:94 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:102 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:111 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:115 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:120 BOOLOP: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:120 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)
- custom_components/heatpump_optimizer/driving_grade.py:127 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/; not run locally, so a survivor it reports is owed a triage)

The five stale pins this branch deleted name sites it moved or rewrote: `_fold_score_sample`'s BOOLOP (a survivor triaged equivalent), CLAMP_DROP and GUARD_OFF, whose booking is now `driving_grade.tally`'s, and `machine_score`'s CLAMP_DROP and RETURN_DEL.

## Carries

Numbered from 1 as the review packet counts them; the brief numbered the same six from 0 (the roster's index), so the brief's Carry N is Carry N+1 here.

- Carry 1 (roster index 0, P9 grid storage leak, #2841): done. `p9Grid` clears both storages after each `page.goto`, and the collision it exposed is fixed in `valueAxis` rather than allow-listed.
- Carry 2 (roster index 1, owner's spec, heat-pump hover reason codes): done. A graded heat pump shows its COP shortfall; an ungraded one shows samples per outdoor band against the requirement and the samples a freeze refused.
- Carry 3 (roster index 2, plain-words metric): done in `score.part_machine` (COP by 3 °C outdoor band against its own history, the 20 samples a band needs, what no grade yet means), en and sv.
- Carry 4 (roster index 3, mirror the driver interface): done. The same `{code, points}` lists, rounded to one decimal, summing to the grade minus its reference, zero drivers dropped by the renderer with a "typical" fallback per part. The precondition was re-measured at this merge base (Null control).
- Carry 5 (roster index 4, the same interface requirement as routed to R10-COP-GATE): answered by Carry 4 here, which builds that interface for the heat-pump grade; its control (a typical state reads no driver, one perturbed input moves the figure) is the Driving null control and the sign-flip perturbation above. The brief marks this index done or moved; nothing further is built for it.
- Carry 6 (roster index 5, Driving score-row hover, ruled 2026-11-01): done. `operation_drivers` are signed and weighted; the Driving row and the headline hover list them; every score row's hover carries its metric and its current reasons. The brief's examples of a price spread and comfort-forced runs are not drivers here: the day book holds neither, and the cheap/dear split is the exact decomposition the book supports. Nothing of R10-WHY-NOW-WIDGET is built here.

## Forward-carry

none

## Friction

none
