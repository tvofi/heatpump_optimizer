R10-GRADE-DRIVERS: the heat-pump and Driving grades publish drivers in the house grade's interface, every score hover carries its metric in plain words and its current reasons, and the P9 grid starts each state from empty storage, with the ink collision that exposed fixed.

What changed:

- **Heat-pump grade** (`coordinator.machine_score`): publishes `machine_drivers`, one driver `cop_shortfall` whose points are the grade minus 100 (the pump matching its own COP history). Ungraded, it publishes `machine_evidence` instead (`coordinator.machine_evidence`): COP samples per 3 °C outdoor band against `COP_BASELINE_MIN_SAMPLES`, fullest first, and the intervals a learner freeze refused (`MeasuredCop.frozen_refusals`, counted where `_fold_measured_cop` returns `COP_REFUSED_FROZEN`; in memory, since start, not persisted).
- **Driving grade** (new `driving_grade.py`): the day's saving against the flat replay splits exactly into `cheap_hours` (energy bought below the day's running mean, as it was bought) and `dear_hours` (the rest), each weighed against the day's own mean and scaled onto the clipped sample, so they sum to it. They fold with the grade's own EMA and persist beside it in the ledger store (`operation_drivers`, declared in `store.py`); a grade stored before they were kept reads as `earlier_days`, decaying with the EMA. The grade's own arithmetic is unchanged expression for expression.
- **One interface**: `compose_scores` publishes `envelope_drivers`, `machine_drivers` and `operation_drivers` the same way: `{code, points}`, points rounded to one decimal, summing to the grade minus that part's `SCORE_REFERENCE` (house 50, heat pump 100, Driving 0), empty with no grade; `reasons` stays the absent-grade channel.
- **Card**: `scoreDrivers` renders every part's drivers with a signed weight, and the part's own "typical" line when none moves a point; `machineEvidence` renders what an ungraded heat pump waits on; each breakdown row now has a hover (`scoreRowTitle`) carrying its grade or reason, its drivers or evidence, and its metric in plain words, the same line the headline hover gives. `score.part_machine` and `score.part_operation` now say what is measured, the unit, what high and low mean and what no grade means. Every new string has en and sv.
- **P9 grid** (`tests/card_browser.mjs`): `localStorage` and `sessionStorage` are cleared after each `page.goto`. That exposed the carried collision: `wood_lane` at 375 px stacked four value-axis labels into each other. `valueAxis` now labels a tick only a line (one font size) clear of the last label drawn, keeping every tick mark, as `timeAxis` already does for time labels.
- **Structure and architecture**: the Driving grade's booking, daily fold and drivers moved out of the coordinator class into `driving_grade.py` (a per-coordinator side table, the `price_tiles` pattern; only `held()` is handed the coordinator, and `tally` returns a new book that the coordinator rebinds). The structure budgets are re-recorded as an improvement; nothing was raised.

## Head

Dismissed review finding (not a forward-carry: it has no destination file): the fix review observed that rounded drivers do not always sum to the rounded grade (up to 0.1). Carry: dismissed: per-item rounding of an exact sum is the house grade's existing convention (`envelope_drivers` since #2816), invisible at the card's whole-point display.

e9742808d0f8ea882063b62d2a6ac17c1d41eb28. Repair round 4 over the reviewed head 25e478a7fe7315710064e953bea1f0de3ace607e: merges origin/main at dad3178d6c81cfe2bb410e7045de28f686a6f845, then three commits, then a merge of origin/fix/r10-grade-drivers at 49608a692 (the bot's main merges and #3185): the evidence-band wording fix (card and `tests/card.mjs`), the P9 grid's score fixture, and a no-tree-change merge of the stale `handoff-wip` history. the last merge is of origin/main at e57dfbbe05caf1b4716bc1a8089d8335653080cd (fetched 2026-11-05T09:10Z), and `origin/main` had not moved when `prepr.sh` ran, so the `prepr.sh` run below describes this tree. Claim files are byte-identical to the reviewed head (`git diff 25e478a7 HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt` is empty apart from main's own newer lines merged in); `score_open` was already claimed, and the added state `score_open_graded_pump` exists only in `card_browser.mjs`, which `card_drift.mjs` does not read, so no second fixture moves.

## Mutation proof

Each mutant was applied to one production site in a copy of the tree at 7649fad's code (the Python mutants; the later side-table rename and retyped `published` move none of the three sites) or b713c02's (the card mutants), then the closure script was run. Main's merged delta touches none of the mutated lines. In each Python copy, the extra `and the path that proceeds still stamps a resolvable recorded_at (#363)` red is the copy's own artefact (fixer.md step 2), and appears in every copy.

- M1 `driving_grade.tally`: the cheap-side `_add(book, "kwh_lo", ...)` and `_add(book, "sek_lo", ...)` replaced by `pass`. `tests/features.py` turns red on `R10-GRADE-DRIVERS: the Driving grade's drivers split it exactly -- energy bought under the day's mean pushes it up, energy bought over pulls it down -- and keep summing to it through the EMA`.
- M2 `coordinator.machine_score`: returns `[]` instead of the `cop_shortfall` driver. `tests/features.py` turns red on `R10-GRADE-DRIVERS: a graded heat pump drops its evidence and carries one driver, its distance below its own COP history: none at 100, and a Cusum a quarter of the way to its alarm takes 25 points`.
- M3 `coordinator._fold_measured_cop`: `self._measured_cop.frozen_refusals += 1` deleted. `tests/features.py` turns red on `R10-GRADE-DRIVERS: the heat pump's evidence lists each band's samples, most first, and counts only the intervals a freeze refused`.
- C1 card `scoreDrivers`: the per-part typical line replaced by the house's `score.driver_typical`. `tests/card.mjs` turns red on `R10-GRADE-DRIVERS null control: all-zero Driving drivers show the metric and no reason rows, House unchanged`.
- C2 card `machineEvidence`: returns `""`. `tests/card.mjs` turns red on `R10-GRADE-DRIVERS: an ungraded heat pump shows samples per outdoor band against the requirement, and freeze refusals`.
- A1 card `valueAxis` label thinning: the tree with the storage reset and without the thinning (71a59dc) is the mutant. `tests/card_browser.mjs` turns red on `P9 grid: no two text runs share ink`, with every pair at `wood_lane/375` (text "0" x "1", "1" x "2", "2" x "3"). With the thinning, the same grid run is green and the dumped overlap list is empty.

Failing test first: the head's `tests/card.mjs` run against the base's card turns red on all 7 new `R10-GRADE-DRIVERS` checks and on `each row carries its plain-language explanation`, which now pins the new metric wording. The new `tests/features.py` block imports `SCORE_REFERENCE` and `driving_grade`, neither of which exists at the base.

Repair round 4 mutants:

- E1 card `machineEvidence`: the unrepaired text (ASCII hyphen, bare count) is the mutant: with the card at the previous head and the new `tests/card.mjs`, `2 CARD CHECK(S) FAILED`, on `an ungraded heat pump shows samples per outdoor band against the requirement, and freeze refusals` and `a negative evidence band uses the card's minus sign and its count carries a unit, in sv as well`. With the repair: `ALL CARD CHECKS PASSED`.
- B1 `tests/card_browser.mjs`: the mutant `.sb-row { overflow: hidden; max-height: 2.2em; }` added to the card's CSS turns `P9 grid: no text is clipped where its ancestor cannot scroll to it` red, naming the three `sb-drivers` lines (the House, Heat pump and Driving drivers) with 8.8, 51.8 and 8.8 px clipped. Null control: the unmutated head reads `ALL BROWSER CHECKS PASSED`. Two weaker mutants stayed green and are recorded as non-findings: a 263-character unbroken driver label (the card wraps it) and `.sb-drivers { overflow:hidden; white-space:nowrap; width:6em }` (the grid's clip check starts at the run element's parent, so a clip on the text's own element is outside its reach).

## Null control

- `tests/features.py`: buying flat all day scores 0, and no Driving driver moves the grade a point (`R10-GRADE-DRIVERS null control`).
- `tests/card.mjs`: a payload whose Driving drivers are all zero renders the metric and the "bought at the day's flat mean price" line, with no reason row, and the House row's hover is byte-equal to the same payload without `operation_drivers`. Perturbation: flipping the sign of `dear_hours` flips its mark from − to + (`R10-GRADE-DRIVERS perturbation`).
- House grade unchanged (Carry 3's precondition, re-measured at the merge base and at the head): `dev/audit/harnesses/r10_scores_envelope.py` prints 40 `tree_grade=` rows and none off 50.0 at both ends; `dev/audit/harnesses/r10_house_grade.py` prints `owner_min=35.2`, `monotone=True` and `drivers_max_gap=0.0` at the head.
- Driving grade: `driving_grade.fold` computes the sample with the base's expressions in the same order. The pre-existing #908 checks in `tests/features.py`, which compare two fold sequences for exact equality and pin the seed to 100, pass unchanged.

## Figures

- `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` at d113fe6 (the earlier head; the delta since is the merge of main, the bot's re-record, the pins and one check in `tests/features.py`, re-run directly below): `MODE: SCOPED -- 28 script(s) run, 5 scoped out.`, rc=0, with `tests/features.py` and `tests/card.mjs` among them; `env_drift.py --all origin/main` reads no unclaimed drift, and `card_drift.mjs origin/main` one moved state, claimed.
- `NODE_PATH=/opt/node22/lib/node_modules PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node tests/card_browser.mjs` at d113fe6: ALL BROWSER CHECKS PASSED. Indicative only: CI's browser job decides. At 71a59dc (reset, no thinning) the same run failed `P9 grid: no two text runs share ink`, every pair at `wood_lane/375`.
- `bash tools/pr/prepr.sh` at b256f36d285247b1cf22fd60d039c70fc01f165c: rc=0.
- `python3 tests/structure.py`: rc=0, after `--record` lowered `max_class_loc` 7975 -> 7971 and `class_excess_loc` 17640 -> 17636 (commit 467ee2d's message carries the reason).
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py`: `claims_true=123`, `claims_false=0`, `arch_map_missing=0`.
- `python3 tools/pr/ci_predict.py --only under-scoped`: no closures, fast, governance or instrument red predicted.
- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_scores_envelope.py`: 40 `tree_grade=` rows, 0 off 50.0, at the base and at the head.
- Goldens: the five coordinator fixtures (`coord_all_features`, `coord_dhw`, `coord_grid_fee`, `coord_minimal`, `coord_two_zone`) gain the new score keys, inserted by path into the committed files (70 lines added, 0 removed). A `golden.py --record --only` here also rewrote float values this box computes differently, so it was discarded: no value is re-recorded on this box. Each fixture, and the card's `score_open`, is claimed.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` at 1017865aefe429ec5399dd9d4a86ac88178f09f5: `ALL 2616 ENTITY CHECKS PASSED`; `PYTHONPATH=tests/hastub python3 tests/features.py`: `ALL 4807 FEATURE CHECKS PASSED`.
- Toolchain: `python3 -c 'import numpy,scipy;print(numpy.__version__,scipy.__version__)'` prints `2.5.4 1.18.1`, equal to `tests/requirements-ci.txt` (`numpy==2.5.4`, `scipy==1.18.1`) after `bash tools/audit/seat/cloud-setup.sh`; `--check` reads OK. CI stays the authority for goldens, and none was re-recorded here.

- Repair round 4, at the head above: `node tests/card_browser.mjs` reads `P9 grid: 333 cells, 21308 text runs, 1040 box-intersecting pairs inked` (324 + 9 cells for the added `score_open_graded_pump` state across 3 viewports, 2 languages, light and dark -- rule: the grid's own cell count) and `ALL BROWSER CHECKS PASSED`, with no shared ink, AA contrast and no clipping. `score_open` now renders the reviewer's fixture (a graded house with two drivers, an ungraded pump with four bands and 7 freeze refusals, a Driving row with `cheap_hours`, `dear_hours`, `earlier_days`), and `score_open_graded_pump` a graded pump with `cop_shortfall`, so every new label string is rendered and measured, en and sv, light and dark, phone, tablet and desktop. Indicative only: CI's browser job decides.
- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) bash tests/run.sh`: `MODE: SCOPED -- 28 script(s) run, 5 scoped out.`, then `30 TEST SCRIPT(S) PASSED; 4 SCOPED OUT AND NOT RUN`, rc=0. `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`; no budget raised.

## Architecture score

`python3 tools/audit/archscore/score.py --diff c3a279e3252a8b57bb00b5a677318cd4fe20387f`: `dS +0.0036 IMPROVES`, `coord_footprint 2381 -> 2375`; no other metric moves. An earlier cut of this branch read `shared_inplace_writes 3 -> 4` (a collaborator writing into the coordinator's day book) and `coord_footprint 2381 -> 2390` (every `driving_grade` function was handed the coordinator); `tally` now returns a new book and only `held()` sees the coordinator.

## Red checks

This head has no check run yet (a new commit, no PR run has reached it). The concluded reds the PR's current head 49608a692 (a `ci: merge main` bot commit over 25e478a7), over all 70 check runs of both pages, and what each means here:

- `tests / closures`: `prepr.sh` step 7 reads it as red at the PR head, and the run list I read afterwards shows it `success` in run 41991584454 and `in_progress` in 41991540101 (the bot's re-attempt after its closure re-record). I could not read a concluded log of the red attempt, so I do not state its cause; the diff carries no closure-affecting file beyond `tests/card.mjs` and `tests/card_browser.mjs`, and `tests/closures.json` was merged by the ledger driver from the PR head. Cheaper detector: `python3 tests/closure.py select` (the scoped gate) ran green here at this head; the standing cost is the CI re-derivation `closures-autofix` repairs on Linux, which a seat may not run off Linux (`gate-scoping.md`).
- `governance / delivery-status`: `DELIVERY STATUS OVERDUE`, all rows of other merged PRs (#3174, #3091, #3089, #3192, ...). Inherited: red on the base's ancestry (main e57dfbbe0 (79f765e6b at the PR head's merge)), a job that states it is not a required context. This diff writes no delivery row.
- `tests / nightly-status`: grades `main`, not this diff (`defect-root-cause.md`). Inherited: red on the base's ancestry, main 79f765e6b, check `tests / nightly-status`; the log says it is not a required context. This diff touches none of `ci.yml`, `tests.yml`, `nightly.yml`, `governance.yml`, the plan or `HANDOVER.md`.
- `gate` (06:18Z and 06:19Z at the earlier head 25e478a7): cancelled when a PR-edit run cancelled the code run; the re-attempt concluded green. Not a defect.

Every earlier red of the earlier heads (`tests / fast (3.14)`, `tests / mutation`, `pr-contract`, `tests / replay`, `tests / mutation-autofix`) concluded green at 25e478a7; none is open on this page. The finding of the fix review (the section's spliced fragment) is repaired by this retake.

## Unpinned sites

The ledger rows (`tests/mutation_ledger/killed_by/`) are in this diff. `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main` at this head's parent: 8 new sites driven, 6 pinned killed by `tests/features.py`, 2 survived (both `driving_grade.py:84` CMP_BOUND). The first run read one of them killed by `tests/features.py` and one alive; the alive one, `sample > 0.0` -> `sample >= 0.0`, differs from the original only for a sample of negative zero (the scale becomes -0.0, so every driver prints `-0.0`). That is a value, not an equivalent mutant, so it got a killing check, not a triage: `R10-GRADE-DRIVERS day_drivers: a negative-zero sample books the same zeros as a zero one, sign included` (`tests/features.py`). Re-run after the check: `PIN KILLED: 2 pinned, 0 left unpinned`. The 32 sites the earlier body listed (coordinator.py and driving_grade.py) are covered by the killed_by rows in this diff; no `survivor_triage` was written.

Mutation proof of the new check: with line 84 of `driving_grade.py` mutated to `sample >= 0.0 and total > 0.0`, `day_drivers(book, 2.0, -0.0)` returns `{'cheap_hours': -0.0, 'dear_hours': -0.0}` against `{'cheap_hours': 0.0, 'dear_hours': 0.0}` unmutated, and the mutation table reports the site killed by `tests/features.py`. Null control: the unmutated tree passes `tests/features.py` (`ALL 4807 FEATURE CHECKS PASSED`).

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
