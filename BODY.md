R10-MUTATION-ANCHOR closes issue #2493. That issue is the forward-carried finding from R10-SAV-BASELINE (#2255, PR #2411): `tests/entities.py` read every mutant of a pinned line as killed. Part of #201.

The cause: a ledger row is pinned to its line's text, so a mutant of a pinned line leaves a row naming a site the mutated tree no longer generates. `tests/entities.py`'s `--anchor` self-test runs `mutation_table.main()` with the whole live ledger, and `main()` refuses a ledger that disagrees with the live inventory. So that one check went red for the row's sake, not the code's. The finder's control reproduces it at the base: the equivalent rewrite `if None is not indoor:` of the pinned `if indoor is not None:` in `HeatPumpOptimizerClimate.current_temperature` read `1 of 2425 ENTITY CHECKS FAILED`, and the one red check was `--anchor re-drives one site: ...`.

Two changes, one per seam:
- **The instrument (`tests/mutation_table.py`).** `invalidated_rows(budgets, rel, before, after)` names the ledger rows that a rewrite of `rel` makes stale by itself. Those are the site's own row when the nightly or `--anchor` re-drives it, a second operator's row on the same line under `--pin-killed`, and a row whose `#N` ordinal the rewrite shifts. `main()`'s `drive()` hides those row files from the mutant's worker tree for that run and restores them after. A kill is then a check that fails on the mutant and passes on the base, for every driver, including the `survivor_triage` staleness check that sampled mode already handles by dropping `TRIAGE_JUDGE` (R9-F10.13 arm A). `--pin-killed`, `--drain` and `--anchor` had no such guard.
- **The self-test (`tests/entities.py`, the R9-F10.13 `--anchor` block).** `_mut_anchor` now stubs the ledger with the one row it re-drives, not the live ledger. It already stubbed the clone and the driver runner. Whether the live ledger agrees with the live inventory is the mutation lane's own refusal (`completeness_problems` in `main()`), not something this behavioural test of `--anchor` should depend on.

The group's second carry is triage P-L (#2632): `pin_entry`'s `reason` no longer names the base ref, so two pins of one mutant measured on different bases are byte-identical and their add/add merges under git's default merge. No existing row is repinned.

Design choices the checks encode (`fixer.md` step 11): the hidden set is exact, not by line. Rows stale before the mutant stay visible, and rows the rewrite leaves valid stay visible.

Alternatives considered (`fixer.md` step 17):
- **Only insulate the self-test.** That closes the finder's control for `tests/entities.py`, but not a `survivor_triage` mark on a mutated line under `--pin-killed`, `--drain` or `--anchor`. The census below counts 5 second-pin lines whose other row is a triage mark.
- **Only the instrument.** Then `tests/entities.py` still goes red when someone runs it on a tree with an edited pinned line, which is the finder's literal re-measure.
- **Drive against the base's ledger.** The base ledger carries the same row with the same text, so it is stale in the mutated tree too.
- **Read the failing check names and discount ledger checks.** That is a spelling list over check names, the #1874 shape.
- **Strike the vacuous pins outright.** Each would leave its site unpinned, the unpinned count would exceed the ratchet base's, and the mutation lane refuses that. Each vacuous pin became a `survivor_triage` `gap` row instead, under the same anchor and `old` pin. That is the same shape as `sysid.py:_slab_ua_profile_halfwidth CLAMP_DROP dffcdea0`'s existing gap row, whose reason records this same mechanism.

## Head

a55a0f47ecf5e805dc86bf8b9eb157755271efa8 (code head `handoff/r10-mutation-anchor`), on origin/main `fa4dad4a75eef5d8db3d8f1c35e6ae15dd57583a`, which is also the merge base. The branch was cut at `50af6174f53c` and origin/main was merged in twice: at `3deb7cb89` (main's `e8a08cf9e`, which changed `coordinator.py`, `inputs.py`, `const.py`, `tests/entities.py` and ledger rows) and at `a55a0f47e` (main's `fa4dad4a7`, triage and delivery records only). The gate and the census were re-taken at the head (2026-10-24T12:49Z, `date -u`). The pin measurement is stamped with the SHA it ran at; after the first merge, every pin in a file that merge changed was re-driven at `3deb7cb89`.

## Mutation proof

Each mutant was applied in place and restored. The R9-F10.13 `--anchor` block and the `--pin-killed` block of `tests/entities.py` were run through a scratch driver that execs exactly those blocks against the tree's `tests/mutation_table.py`; the full `tests/entities.py` runs are under `## Figures`.
- M1, `tests/mutation_table.py` restored to the base `50af6174f`: `FAIL a re-driven pin is not reproduced by a driver that only sees the row the mutant made stale: ...` (the run read `1 reproduced`) and `FAIL invalidated_rows names exactly the rows pinned to a rewritten line, ...`.
- M2, only the two `p.unlink()` lines in `drive()` deleted (rows computed, never hidden): `FAIL a re-driven pin is not reproduced by a driver that only sees the row the mutant made stale`.
- M3, `_mut_anchor`'s one-row stub reverted to the whole live ledger, on a tree carrying the climate rewrite: `FAIL --anchor re-drives one site: the real pin is reproduced, ...` and `FAIL a re-driven pin is not reproduced ...`.
- M4, `pin_entry`'s reason re-given a ref (`against {_rev(ROOT, 'HEAD')}`): `FAIL two pins of one mutant are byte-identical whatever base measured them, and pins of different mutants differ (P-L)`.

Failing test first: commit `20106bbc4` (the two anchor checks) precedes the fix `f9878c8d9`, and `ab2d15ef2` (the P-L check) precedes `1bf9fdae4`. At each test commit the new checks read red; for P-L that is a `TypeError`, because `pin_entry` still required the ref.

## Null control

- **The finder's harness at both ends.** The climate rewrite was applied and `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` was run. At the base `50af6174f` it read `1 of 2425 ENTITY CHECKS FAILED` (the `--anchor` check). At `c1fbc5d3e`, the head carrying both changes, it read `ALL 2427 ENTITY CHECKS PASSED`.
- **The rewrite through the instrument at `c1fbc5d3e`.** `dev/audit/harnesses/r10_anchor_vacuous.py --drive --anchor '<climate anchor>' --new '            if None is not indoor:'` read `LIVES ... hidden=1`. With `--no-hide` it also read `LIVES ... hidden=0`, because the self-test change alone closes it for this driver. The instrument change alone is proven by M1 and M2 against a code-blind ledger judge.
- **Kills that should survive do.** Six `killed_by: tests/entities.py` pins with no second ledger row, chosen by sha1 order of the anchor (`nullpins`): 6 of 6 still killed with their own row hidden (`DRIVEN 6 pin(s): 6 kill(s) survive the fix, 0 vacuous`).
- **The new checks' own controls.** The ledger judge pinned to the site still lets the code-seeing stub kill it (`pinned to tests/stub_ledger_judge.py, killed by tests/stub_kills.py`). `invalidated_rows` on an unpinned line returns `[]`. Pins of two different mutants differ.

## Figures

- Census at the base `50af6174f`, rule `load_budgets()["killed_by"]` entries whose `killed_by` is `tests/entities.py`: `python3 dev/audit/harnesses/r10_anchor_vacuous.py` printed `CENSUS: 175 killed_by tests/entities.py pin(s); 52 on a line carrying a second ledger row`. The finder's `grep -rl '"killed_by": "tests/entities.py"' tests/mutation_ledger/killed_by | wc -l` printed 175 at the base, not the brief's 123, which was a snapshot at an earlier baseline.
- The second-pin set, compared as sets with the exact rule: for each of the 175 pins' sites, does `invalidated_rows` on the site's own mutant name any row besides the pin's own? 52 anchors, and `other - sec: []`, `sec - other: []`. That is set-equal to the same-line census, so the 123 others' mutants invalidate only their own row. That row was absent when `--pin-killed` recorded them (the site was unpinned), so no stale row could have voted. 5 of the 52 lines carry a `survivor_triage` row and 49 a second `killed_by` row; a line can carry both. The script is a one-off over the harness's `census()`.
- The measurement: `env -u BASH_ENV python3 dev/audit/harnesses/r10_anchor_vacuous.py --drive --jobs 3 --out m_second.json`, at `0be5e2de5`, 56 sites under the 52 anchors, three green baselines. It printed `DRIVEN 52 pin(s): 22 kill(s) survive the fix, 30 vacuous`. A pin survives only when every site under its anchor is still killed. Per pin:
  - Survive (22): `binary_sensor.py:MoldFloorBreachBinarySensor.is_on` BOOLOP and RETURN_DEL `2837b3da`; `boost.py:BoostState.active` BOOLOP and RETURN_DEL `7f4fe02b`; `boost.py:interval_boosted GUARD_OFF fb708b7a`; `config_flow.py:identity_update` BOOLOP and GUARD_OFF `58aac1a1`; `coordinator.py:HeatPumpOptimizerCoordinator._forecast_arrays` BOOLOP and GUARD_OFF `54c3c7b5`; `entry_config.py:EntryConfig.fuse_kw CMP_BOUND abdad8ea`; `replay_doc.py` `_entry_shape 82df02a9`, `_number 59b66cd2`, `_series 4f5f71fc`, `_unit 5a24a5a3`, `_walk 345dbb86`, `_walk 430524a4`, `_walk 5476d757`, `choose_price_entity 96059945` (all GUARD_OFF); `sensor.py:DHWScheduleSensor.native_value BOOLOP f17fef3f`; `sensor.py:_gap_energy_rate GUARD_OFF 6c88eaac`; `tariff.py:PeakTracker.observe` BOOLOP and GUARD_OFF `03a62eb7`.
  - Vacuous (30): `accuracy.py` `AccuracySample.from_dict.num CMP_BOUND bc6be4d0`, `plan_promise` CMP_BOUND and GUARD_OFF `f4529abb`; `boost.py` `BoostState.expire CMP_BOUND 2e90085b`, `interval_boosted CMP_BOUND fb708b7a`, `interval_boosted RETURN_DEL a7932f63`, `space_learning_frozen` CMP_BOUND and RETURN_DEL `ad026ebf`; `coordinator.py` `_dhw_plan_fields` BOOLOP and CMP_BOUND `9f6bb651`, `_fold_measured_cop GUARD_OFF a3cd4cc3`, `_solar_forecast_view CMP_BOUND 8c7cab88`, `async_set_mode BOOLOP 09b5eb9d`, `_within_window CMP_BOUND ec86de5c`; `dhw_schedule.py:_split_wrapping CMP_BOUND ba0b8fdb`; `draw_range.py` `DrawRange._metered_range CLAMP_DROP 2aa4786a`, `DrawRange.from_dict CMP_BOUND 2726f21e`, `DrawRange.from_dict CMP_BOUND ec8fe83f`, `_command_cells BOOLOP 6111075f`, `fold CMP_BOUND 8c264f30`; `inputs.py:setpoint_step CMP_BOUND 901cc8a6`; `manual_plan.py:build_override CMP_BOUND bc7e64fc`; `optimizer.py` `HeatPumpOptimizer._compute_baseline_power CMP_BOUND 64b1ab84`, `_memoized_value_and_gradient.fun CMP_BOUND 41123ecb`; `pump_arbiter.py:_share CMP_BOUND 8cc0b854`; `sensor.py` `DHWScheduleSensor.native_value GUARD_OFF f17fef3f`, `_gap_energy_rate CMP_BOUND 6c88eaac`; `sysid.py` `_one_state_ua_halfwidth CMP_BOUND a19e1b35`, `_slab_ua_profile_halfwidth CMP_BOUND 870ea3aa`; `thermal_model.py:modulation_floor_flow_c CMP_BOUND 431e5f53`.
- After the merge of `e8a08cf9e`, the 9 of those pins in `coordinator.py` or `inputs.py` were re-driven at `3deb7cb89` (`--anchor` x9). The run printed `DRIVEN 9 pin(s): 2 kill(s) survive the fix, 7 vacuous`, the same partition.
- The ledger, measurement change (the ledger is data, not a ratchet). `python3 dev/audit/harnesses/r10_anchor_vacuous.py --strike m_second.json --at 0be5e2de5` printed `STRUCK 30 vacuous pin(s) into survivor_triage gap rows` (commit `382ddf506`). The `killed_by: tests/entities.py` pins, by the finder's grep: 175 before, 145 after. The census at the head prints `CENSUS: 145 ... ; 22 on a line carrying a second ledger row`, and those 22 are the surviving set. Unpinned sites (`unpinned_sites(load_budgets(), inventory())`) are 3999 at the head and 3999 at `base_unpinned("origin/main")`. `ledger_form_problems`, `layout_problems`, `completeness_problems` and `triage_problems` are all `[]`.
- Unpinned sites (`fixer.md` step 2): none. The diff adds no production line.
- Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out`. With `PYTHONPATH=tests/hastub` at the head:
  - `tests/entities.py` under `env -u BASH_ENV`: `ALL 2428 ENTITY CHECKS PASSED` at `1bf9fdae4` and at `3deb7cb89`; and `ALL 2428 ENTITY CHECKS PASSED` at `a55a0f47e`.
  - `tests/harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`.
  - The `run_always` set: `tests/layout.py` `layout self-test: ok`; `tests/closure.py selftest` `ALL 117 closure shrink pins PASSED`; `tests/env_drift.py --claims-only origin/main` `claims hygiene: origin/main ok`.
  - `tests/stress.py` is left to CI's required mutation check (`fixer.md` step 5).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL`.
- `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --selftest-pin-drive`: `PIN EQUALITY: identical -- 7 pin(s) of 8 site(s)`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `no closures or fast red predicted`. It had predicted an INERT READS entry for the new harness, repaired before the handoff with `--apply-inert` (commit `926e0a8c3`). `tests/harness_headers.py` had refused the harness's fixed-depth root; it now uses the canonical `repo_root` walk (commit `1398ee7bc`).
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused`.

## Red checks

none: no CI has run on this ref. The one predicted red, INERT READS for the new harness, was repaired before the handoff. The harness's first `--drive` runs came back with red baselines, both for this seat's environment and not the branch: an inherited `BASH_ENV` reddened two workflow-step checks in the worktree (the finder's recipe unsets it, and the harness docstring now says so), and one of four parallel baselines failed a timing check under load (re-run at `--jobs 3`). The harness refuses to read a verdict over a red baseline, so neither produced a figure above.

## Forward-carry

none. Every later stage now gets the fixed instrument at its merge base. The 30 struck sites are `gap` rows whose reason says that only `tests/entities.py` re-drove them; a later drain or fixer may re-pin one when another driver kills it. That is the ledger's normal route, not a change in how a stage works.

## Friction

none
