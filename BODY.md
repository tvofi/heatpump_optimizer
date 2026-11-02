Re-centres the replay cost budgets (owner `cpu_ratio`, synthetic `cpu_ratio`, synthetic `loop_cpu_ratio`) on the readings the CI `replay` job itself takes, and pins two sites the 3078 review mutated. Closes #3129. Measures only what ran.

## Head

541033f1c60362c16eb39501f8ba5f6cdeb17fd4, on origin/main 3905069f38a60559186fef916b0241e311cc81cd (unmoved since the base; `git merge-tree --write-tree origin/main HEAD` exits 0).

## Re-cut note

Repair round 2 of #3174, after `verdict/3174` (blocked a476a578: carry-missing, and the owner `cpu_ratio` 409.7 centred on a reading the lane never takes). Ruling (mandate): no roster carry; the synthetic `loop_cpu_ratio` defect is the class this group exists for, so it is fixed here. The earlier "Carry: R10-REPLAY-COST-BUDGET" lines are removed; the 385.3 reading (a `--step-minutes 60` single-cycle run on a reviewer box) is dropped.

What changed against a476a578: `COST_BUDGETS` only, owner `cpu_ratio` 409.7 to 337.8, synthetic `cpu_ratio` 3.353 to 3.614, synthetic `loop_cpu_ratio` 0.143 to 0.1278, and the comment above it. The two pins are unchanged. No `*_budgets.json` is touched; no budget in a `*_budgets.json` is raised.

## Red checks

- Head a476a578 (the head reviewed): the whole check-run set, all pages, has no failure, timed_out or cancelled conclusion (`merge_train.py classify` printed GREEN, per the review). Nothing to answer.
- Inherited from #3167: replay job 125160076828 of run 41405222589, `synthetic-dhw-only.json: cycle_cost [1 offender(s): cpu_ratio 2.81 over its budget 2.173]`. Cause: a budget recorded on one runner class. Process state: recorded-on-one-class. Cheaper detector: the lane's own `record:` line, which already prints it; no new one is warranted. Countermeasure: this re-centring on both classes. The base budget 2.173 is over-run by all three CI readings (below); 3.614 passes all three.
- Synthetic `loop_cpu_ratio` was named red at base by the review. Measured: it is red only on a box outside both CI classes (this container, 4 cores, `loop_ref_ms` 87: 0.1748 against the old 0.143; the reviewer's 0.152 to 0.191). All three CI readings, at base code, read 0.0901 to 0.0907 and were green against 0.143. See Figures for what re-centring does and does not do for that box.

## Mutation proof

Per budget, a mutant that adds measurable cycle cost, read through the lane's own metric:
- synthetic `cpu_ratio`: the lane's `cpu doubled` arm (`--inject-cost cpu`) reads 5.5315, 5.701 and 4.6473 on the three CI jobs, over 3.614 (production `cost_offenders` on each logged dict: `cpu_ratio 5.532 over its budget 3.614`).
- synthetic `loop_cpu_ratio`: the `loop doubled` arm reads 0.1833, 0.186 and 0.1792, over 0.1278 (`loop_cpu_ratio 0.1833 over its budget 0.1278`).
- owner `cpu_ratio`: the lane runs no doubled arm on this fixture (`COST_ARMS_SKIPPED`), so I ran one: `PYTHONPATH=tests/hastub python3 tests/replay.py --one tests/replay/owner-2026-10-30-away.json --inject-cost cpu` at the lane's own 16 cycles reads `cpu_ratio 623.8 over its budget 337.8`.
- The two pins, run `PYTHONPATH=tests/hastub python3 tests/replay.py --fixture tests/replay/synthetic-dhw-only.json`: `AWAY_COVERED` misspelt `owner-2026-10-30-awya.json` reads `FAIL AWAY_COVERED names committed fixtures [owner-2026-10-30-awya.json: declares away coverage but is not a committed fixture]`; `tools/replay/export.py` refusal as `f"the recorder URL {url} is neither SQLite nor "` reads `FAIL recorder:unsupported_scheme_refusal_prints_none_of_the_url` with the canary credential visible. Each restored with `git checkout` of its file.

## Null control

- Budgets, base against base: the three readings are the unmodified cycle code on CI (neither #3167's nor #3078's diff touches cycle code; this PR's diff is `tests/replay.py` only): synthetic `loop_cpu_ratio` 0.0907, 0.0903, 0.0901, flat within 0.7 % across both classes, and all three within 0.1278; synthetic `cpu_ratio` 2.7543, 2.81, 2.3246 and owner 235.8, 240.7, 241.9, all within the new budgets (production `cost_offenders` on each logged dict at the head: `WITHIN`; at the base budgets the synthetic `cpu_ratio` reads all three over 2.173, the defect).
- Owner fixture null on this container, clean, lane config (16 cycles, 7 timed): `cpu_ratio 283.585`, `cycle_cost []`. Same fixture with the mutant above: 623.8, red. This container is outside the CI classes (`ref_ms` 33.8, `loop_ref_ms` 88.4), so it is a supplement, not a centre.
- Pins, clean tree: `ok control:away:covered_names_are_committed`, `ok recorder:unsupported_scheme_refusal_prints_none_of_the_url`, `ok AWAY_COVERED names committed fixtures`.

## Figures

- Readings are the `cost {...}` lines of the `tests / replay` job; rule for each budget: sqrt(2) x the geometric midpoint of the extremes of the three readings. Source jobs: 125240101580 (run 41434115932, #3174 at 5cc311bf, class A: `ref_ms` 30.7, `loop_ref_ms` 130.9), 125160076828 (run 41405222589, #3167, class A: 30.4, 128.7), 125097530406 (run 41389413359, #3078, class B: `ref_ms` 46.3, `loop_ref_ms` 155.9). Command to re-take: `gh api repos/tvofi/heatpump_optimizer/actions/jobs/<job id>/logs`, then the lines holding `cycles over` and `doubled:`.
- Owner `cpu_ratio` 235.8185, 240.6876, 241.9249: 337.8; lowest reading 70 % of it. Synthetic `cpu_ratio` 2.7543, 2.81, 2.3246: 3.614; lowest 64 %; every `cpu doubled` arm over it. Synthetic `loop_cpu_ratio` 0.0907, 0.0903, 0.0901: 0.1278.
- Only these three jobs were readable for the owner fixture and the synthetic after 2026-10-31; the earlier CI figures in the comment (249.0, and `loop_ref_ms` 79-84 at 0.1114) have no log reachable here, so the second faster-ruler CI class is not re-centred on a reading I took. They sit inside the new bands (0.1114 is between 0.0639 and 0.1278).
- A box outside both classes: this container reads synthetic `loop_cpu_ratio` 0.1748 to 0.1892 (`loop_ref_ms` 87), over both 0.143 and 0.1278. Widening to it would put the budget (about 0.19) over the CI `loop doubled` arm (0.179 to 0.186), so the lane could no longer see the regression it exists for. The lane runs on CI only, so this is recorded, not paid.
- `peak_kib` 3740 / 2686 and the owner `loop_cpu_ratio` 0.249 are unchanged: the jobs read 2649 to 2709 KiB and 0.128 to 0.142 inside both bands.
- `python3 tests/structure.py` passes at this head. Scoped gate: `MODE: SCOPED -- 3 script(s) run` (`debug_collect`, `entities`, `features`).

## Carries

- Carry 1: the owner fixture's budget entry re-recorded on the CI job's own readings: `cpu_ratio` 337.8 (readings 235.8, 240.7, 241.9 under Figures), null control the three readings within it and the clean local run 283.6 green, mutant 623.8 red.
- Carry 2: `AWAY_COVERED` names pinned against the committed fixtures, and the unsupported-scheme refusal pinned to print none of the URL; both with a null and a killed mutant under Mutation proof.
- Carry 3: the cost budget re-centred on both CI runner classes: synthetic `cpu_ratio` 3.614 and `loop_cpu_ratio` 0.1278 (`peak_kib` and the owner `loop_cpu_ratio` kept, with the reason under Figures).

## Forward-carry

none

## Unpinned sites

None added under `custom_components/`; the two checks are value checks in `tests/replay.py`, and the `tools/replay/export.py` refusal is pinned by the in-tree mutant above.

## Friction

none
