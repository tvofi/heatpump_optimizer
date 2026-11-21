Fix review: merge e9ad13fa58e02965bb5eb772b19535c09c9523c6

bus-nonce: b737a95d8c39bd5643243911007c379d
pending-ci: gate

## Findings

- Out of scope: `parsers_fuzz.py --arm unit` reports 121 undeclared raises and 3 non-finite returns, the same at the merge base and at the head. They come from direct calls, with arbitrary types, to text-spec parsers outside `inputs.py`: `dhw_schedule._parse_time` and its siblings, `grid_fee.parse_day_range` and its siblings, `debugger._parsed`, `debugger._read_stores` and `price_model._tibber_post`. None is an input this group's class covers, and the body's `## Figures` does not claim this arm. Carry: dismissed: flat at both ends; the arm drives parsers outside inputs.py with types no caller passes, and its rows stay in the round-11 D1-s3 evidence for the judge's existing disposition

## Evidence

- Round 4 of this PR: round 2 blocked 40328a85 (`class-open: wood_fuel.lighting_window`), round 3 blocked 98cb43e7 (`mutation-vacuous: open_meteo.py _parse_block len(kept) < 2 loosened to < 1`). The body says the branch was re-cut at round four (fixer.md). Review scope: full. The packet rendered with no `--reviewed-head`.
- Head reviewed: e9ad13fa58e02965bb5eb772b19535c09c9523c6. Merge base: e893cd3d1ebd1ec3bb56756ce902144a370fe821 (`ev/HEAD.txt`). The body's `## Head` names this head.
- `git merge-tree --write-tree origin/main e9ad13fa` (origin/main a8efe1d1): rc=0, no conflict (`ev/merge_tree.txt`).
- `VERSION`, `manifest.json`, `RELEASE_NOTES.md`, `tests/golden/` and both claim files: the three-dot diff touches none of them. Golden drift was not re-run here: it was left to CI's `tests / fast (3.14)`, which is success at this head (job 136942780454).
- Round 3's block is settled. The new check "a lone sample left after the year-1 drop is no series: mean_over claims no window" fails under `len(kept) < 1` and under the guard off (`ev/mutants_om_wood.txt`).
- Mutation proof, one mutant at a time, in a separate worktree at the head, with `git status --porcelain` empty after each run (driver `ev/mutant_driver.py`). All 24 mutants were killed:
  - `open_meteo._parse_block`: `kept` keeps every index; `< 2` changed to `< 1`; guard off. Each makes `tests/open_meteo.py` rc=1 (`ev/mutants_om_wood.txt`).
  - `_lead_minutes`: the field parsed by `finite_float` again; floor made exclusive; ceiling dropped. `_attach_windows` reading the raw option with `max(0.0, finite_float(...))`. Each makes `tests/wood_advisor.py` fail 1 of 27 checks (same file).
  - `async_migrate_entry`: `if repairs:` off; `placed(effective)` without the repair. `number_repairs`: `_interval_minutes` and `_lead_minutes` dropped from `_DEFAULTED_NUMBERS`; every repair set to None; the bool clause dropped. `repaired_numbers` keeping keys mapped to None. `_interval_minutes`: floor made inclusive; ceiling dropped; the field parsed by `finite_float`. Each fails the migration checks this PR adds to `tests/entities.py`. They were run as that section alone with the file's own header, using `ev/entities_migration_block_runner.py`: 9 of 9 pass at the head (`ev/head_entities_migration_block.log`, `ev/mutants_migration_a.txt`, `ev/mutants_migration_b.txt`).
  - `parse_bool` back to `float(token) != 0.0`; `_begin`'s `isinstance(entity_id, str)` guard off; `plausible_c` one-sided. Each fails the 5 checks features.py adds. They were run alone by `tools/audit/seat/features_block.py` with three prelude lines and these markers: start `_R11IG_NONFINITE = (`, end `# -- health, and what must NOT freeze` (`ev/head_features_nonnumeric.log`, `ev/mutants_features_nonnumeric.txt`).
  - `temperature_from_c` multiplying by the factor; `/ 100.0` removed from the minor-unit price branch. Each fails features.py's P8 block, run alone through its price checks (`ev/head_features_p8_block.log`, `ev/mutants_features_p8.txt`). My end marker gives 4 checks, not the body's 5; the check each mutant fails matches the body.
- Finder's harnesses, from the plan export 819aa2e3. Each sha1 matches the body: m4_tariff 2798c36f, m8_agree aaef9a3b, parsers_fuzz 74da66cd, plausible_upper 9b1e8fe8, config_fuzz c0ecf63a. I re-ran every figure in the body's `## Figures` at both ends; each matches (`ev/finder_harness_base.txt`, `ev/finder_harness_head.txt`):
  - `unit_mismatches`: 0 then 0.
  - `temperature_roundtrip_disagreements`: 0 then 0, of 35 probes.
  - `pump_nonfinite_flag_true`: 10 then 0. `pump_nonfinite_freeze_fault`: 5 then 0. `pump_null_control_zero_flag_true`: 0 then 0.
  - `openmeteo_year1_solve_failures`: 3 then 0. `openmeteo_healthy_solve_failures`: 0 then 0.
  - `above_max_accepted`: 0 then 0, of 15 keys.
  - `config_fuzz.py --versions 1..6`: `build_fail` 8, 11, 10, 9, 5, 11 then all 0. `permanent_cycle_fail` 17, 14, 16, 12, 17, 12 then all 0. `migrate_fail` 0 at both ends.
- Other configurations. `parsers_fuzz.py --arm unit` reads the same at both ends: `unit_undeclared_raises=121`, `unit_nonfinite_returns=3` (`ev/parsers_fuzz_unit_both.txt`). None of those rows is in `inputs.py` (see Findings).
- The class. The round's P1 enumerator is at no fetched ref; the fixer recorded that in the body's Friction. I read every production reader of the two re-parsed keys. `optimization_interval` is read through `EntryConfig` (`coordinator.py`, `__init__.py:180`) or through `plan_stale_limit_minutes`'s `getattr` on the parsed config. `wood_lighting_lead_minutes` is read only at `wood_fuel.py:560`, through `EntryConfig.from_mapping`. Its production caller (`coordinator.py:8231`) passes `ctx._config`, an `EntryConfig`, which `from_mapping` returns as it is. No raw reader is left. I found no seam beyond the body's dispositions.
- Step 14. The one moved number is `tests/entities.py`'s N-log-flood allowance for `("__init__.py", "async_migrate_entry")`, 1 to 2. The diff adds exactly one `_LOGGER.warning` there, under `if repairs:`, so the move is earned by the change. `score.py --diff e893cd3d` prints `Architecture score: dS +0.0000 NULL`.
- Step 16. No new path skips an actuator write. `_begin` turns a non-text slot into `not_configured` on reads only.
- Behaviour change, disclosed in the body: a stored negative lighting lead now reads as the 60-minute default; it used to be clamped to 0.
- Red checks. Every red in the owed-reds set at this head or at an earlier head is named and answered in the body's `## Red checks`: `codeql / Analyze (python)`, `gate`, `arch-score / arch-score`, `tests / fast (3.14)`, `governance / env-matrix`, `pr-contract / pr-contract`, `tests / mutation`. I checked that each was answered, not the answer. The `gate` failure in the packet digest (job 136943184860) logs `FAIL run(s) [44923249295] at this head are still being judged; their gate decides`. That run's `codeql / Analyze (python)` was still in progress when I read it, so this is a wait, not a defect.
- Comms: `seat_comms.sh` init, heartbeat and checkpoints ran. No inbox command arrived.
- CI: I polled `merge_train.py classify e9ad13fa... --pr 3734` about every 95 s from 18:41 to 19:12 UTC. Every run printed `WAIT e9ad13fa58e02965bb5eb772b19535c09c9523c6 pending: gate red: none` (`ev/classify_poll.log`). The review was complete, so I am returning it with `pending-ci: gate`.
