R9-EG-A2 (lane EG, classes P2 and P3): one definition per formula and helper, and the interleaved-junk class in the architecture score's clone counter closed. Closes #1775.

**Production (behaviour-preserving).** Each duplicate the brief sampled now has one definition, and its callers use it:

- `thermal_model.py`: `_two_zone_rates`, `_single_zone_rates`, `_two_tank_rates`, `_zone_loss`, `_zone_gains`, `weather_or_calm` and `_wood_track`. The scalar step, `simulate_trajectory_batch` and `_stability_substeps` share them, and each sum keeps its original term order.
- `inputs._finite` replaces the copy in `freq_control`.
- `store.load_mapping` serves `boost.restore`, `away.restore_override` and `pump_arbiter._load`.
- `sysid`: `_r2_confidence` and `SystemIdentification._usable_samples`.
- `dhw_planner`: `_tank_decay` and `_within_ceiling`.
- `config_flow`: `OptionsFlow._page` and `_thermal_model_page`.
- `optimizer._padded_nonneg`.

**Instrument (the carry from #1851).** C3 used to drop an effect-free statement only if its spelling was on a list. It now drops a statement that is dead by data flow (`counters.inert_statements`, judged per function by `_inert`). Exactly what is in the class, and what stays open, is in `tools/audit/archscore/ABOUT.md`, section "Interleaved junk".

- **Round 2** closes the three spellings the round-1 review planted: a self-assignment, an uncalled nested `def`, and a `global` nothing uses.
- Before handing off, I probed six sibling spellings: a bare annotation, a re-import, a `match` on a constant, a comprehension over an empty literal, an empty nested class, and `isinstance(<param>, int)`.
- All nine are GAMEs, `rt_04o` to `rt_04w`. Under the round-1 counters, eight of them read IMPROVES; the annotation already read NULL. With this C3 all nine read NULL.
- **Still open, by design:** a statement with an effect the grammar cannot rule out, for example a call of anything else, a write through an attribute or subscript, an `assert` that can fail, a `with`, a `yield` or an `await`. That is logic in the diff, and a reviewer reads it.

**Mutation ledger.** The consolidation moved two guard sites, which left two killed-by dispositions pointing at sites that no longer exist. Both are re-keyed to the new sites, and each kill was re-measured there.

## Head

c0f81ac988109dc9d1429b1b1fa0d03d7d26ea35 (merge base `origin/main` 0d8f2bb42fcd3ac94ca3bb36db956ac6676e1046, measured 2026-10-03T12:09Z; `origin/main` has since moved to 2622b31c8 with no change to `thermal_model.py`)

## Mutation proof

**C3 mutants.** Each was applied in place to `tools/audit/archscore/counters.py` and run with `PYTHONPATH=tests/hastub python3 tools/audit/archscore/calibrate.py --only <ids> --jobs 4`, then restored with `git checkout`. Under the full calibration, `tests/arch_score.py` fails "no red-team attempt reads IMPROVES" on each IMPROVES below. Unmutated, every listed case reads NULL.

| mutant | change | cases that read IMPROVES (all others listed read NULL) |
|---|---|---|
| M5 | Global/Nonlocal arm returns False | `rt_04q` (+25.9521) |
| M6 | self-assignment arm returns False | `rt_04o` (+14.1502) |
| M7 | nested def/class arm returns False | `rt_04p` (+25.9521) and `rt_04v` (+25.9521) |
| M8 | import arm returns False | `rt_04s` (+25.9521) |
| M9 | `isinstance` removed from PURE | `rt_04w` (+12.9226) |
| M1 (round 1) | dead-store branch off | `rt_04i` and `rt_04k` |
| M2 (round 1) | literal-method arm off | `rt_04n` |
| M3 (round 1) | assert fold off | `rt_04h` |

**Production mutant M4.** I inlined `_two_zone_rates`'s body back into `_simulate_step_two_zone`. `python3 tests/structure.py` then prints `FAIL duplication_copies 39 > 38 (+1)`.

**Re-keyed ledger kills.** Each mutant was driven through `PYTHONPATH=tests/hastub python3 tests/features.py` on a `git archive` export of the branch. The unmutated export fails only the environment check R9-F2.1 P3 (see Red checks).

- `optimizer.py:_padded_nonneg GUARD_OFF 185d0eef`, `if series.size < n_steps:` changed to `if False:`. features.py fails "a short burn forecast is padded with zeros: it plans exactly as the full-length forecast" (IndexError) and "a short margin series pads with zero rather than shortening the horizon", then crashes in `_stash_price_horizon`.
- `pump_arbiter.py:_load GUARD_OFF f7c55656`, `if raw is None:` changed to `if False:`. features.py crashes in the pump-duty arbiter section (`AttributeError: 'NoneType' object has no attribute 'get'`).

`mutation_table.py --scope changed` was not run locally. The ledger's pre-baseline checks pass (see Figures). Some sites this diff adds are unpinned at the merge base: `mutation-autofix` pins the ones a driver kills. Any that survive will be named by CI's `mutation` job.

## Null control

**Calibration.** At `origin/main`, `calibration/expected.json` records `rt_04h`, `rt_04i` and `rt_04j` as KNOWN-OPEN/IMPROVES, and `rt_04k` to `rt_04w` do not exist.
- Round 1's `--record` moved exactly seven red-team keys.
- This round's `calibrate.py --record` printed exactly nine RECORD lines, `rt_04o` to `rt_04w`, all new GAME/NULL, and no SENSITIVE line. It reports `RED TEAM 39/39 attempts read NULL or inadmissible; IMPROVES: none`, and `CALIBRATION 77/103` is unchanged.
- `calibrate.py --measure-corpus` re-derived `calibration/corpus_vectors.json` byte-identical (`git diff --quiet`). The 20 vectors printing ERRORS carry the `_family_*_error` keys that are already in the committed file.

**Physics parity.**
- Harnesses, in my scratch: `h/parity2.py` (sha1 17ffbce8974ec37dd1ddc0b690810f05db52dbc5) and `h/compare.py` (sha1 14c8a7e3fb340e624600573dfce8f8100389ebe4). `parity2.py` is the round-1 reviewer's `mypar2.py` (sha1 2e474b87) with only the hastub path changed, retyped after the scratch loss described under Friction, so it is not the fixer's own harness.
- Coverage: it sets the model flags directly. Its effective grid covers all four combinations of two_zone × wood_tank_configured, under valve `none`, `manual` and `smart_read`. That includes two_tank_modelled=True, 36 wood batch arrays, and up to 15 stability substeps.
- Base vs head: run on exports of `origin/main` 2622b31c8 and this head's `custom_components`, 0 of 2880 arrays differ bitwise.
- Control: a copy of the head with one sum in `_two_zone_rates` re-associated (`q_rad - q_loss_upper + q_inter` to `q_rad + (q_inter - q_loss_upper)`) differs in 218 of 2880 arrays, all of them two-zone keys. So the harness can see the function.
- Scalar vs batch: max |batch − scalar| over 1584 pairs is 0.0 at both ends.

**Goldens.** `env_drift.py --all 0d8f2bb42` prints `NO UNCLAIMED DRIFT: 56 scenario(s)`. Neither claim file is touched.

## Figures

- **Structure:** duplication_copies 59 -> 38, functions_cc_over_15 34 -> 33, max_cc 48 -> 45, max_method_loc 385 -> 377. These come from `python3 tests/structure.py` at the head, against `tests/structure_budgets.json` as recorded at the merge base. The per-row reasons are in commit 9b794c342.
- **Architecture score:** `PYTHONPATH=tests/hastub python3 tools/audit/archscore/score.py --diff origin/main` (at 0d8f2bb42) prints dS +5.5519 IMPROVES (duplication_copies 59 -> 38 +5.5485; coord_footprint 2514 -> 2508 +0.0034). With `ARCHSCORE_ABLATE=C1,C2,C3,C4,C5,C6,C7,C11` it prints the same +5.5519, so the gain does not depend on the counters. No score metric rises.
- **Ledger:** the mutation table's pre-baseline refusals (cap, triage, form, completeness) were run as `mutation_table.py`'s own functions, without a mutant, by a scratch harness that calls `tests/mutation_table.py`'s `cap_problems`, `triage_problems`, `ledger_form_problems` and `completeness_problems` in `main()`'s order (sha1 d3fe581361c2bc41b53a66882df201afbb446e8a, not in the tree). At 232306c9 they report 2 completeness problems, the two in CI's refusal. At this head they report 0.
- **Remaining clone classes:** the census `python3 tests/structure.py` (section "duplication: clone classes") lists 24 classes, none of them among the windows the brief named.
  - The Home Assistant entity properties (`native_value`, `available`, `extra_state_attributes`) are framework idiom and are left.
  - The rest are outside this PR's named set and are now held by the budget at 38.
- **Scoped gate:** `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=0d8f2bb42 ./tests/run.sh` reports `MODE: SCOPED -- 25 script(s) run, 5 scoped out`. 21 are green; the four red are under Red checks.

## Red checks

- **`mutation`** (check-run 111181268798 at 232306c9). It refused at "Drive the table" because the ledger named two sites the consolidation had moved. The cheaper detector is the table's own completeness check, which needs no mutant and refuses in seconds. I ran it locally (see Figures) and it now reports 0 problems. Before pushing, I had not run it; the cost of skipping it was one CI round.
- **Local only, not from this diff** (Python 3.11.5, Accelerate). CI's Linux runner is the authority for all four.
  - `features.py`: 1 failing check, R9-F2.1 P3 (shipped 110.4366 vs seeded 110.1297). Round 1 showed the same check failing with the same two values at `origin/main` on this machine.
  - `entities.py` and `harness_headers.py` (D6 `claims.py`): a Python 3.12 f-string in `tests/entities.py`, which this branch does not touch.
  - `stress.py`, 3 of 95: `sys.monitoring` exists only in 3.12, the CPU budget fails at 281x against 268x on a shared machine, and the RSS reading of one probe sits at this platform's import floor.

## Forward-carry

None. No not-started brief (R9-EG-A3, R9-EG-A4, R9-EG-B11) rests on the KNOWN-OPEN cases, on C3's coverage, or on the duplication figure; I checked with `jq` over `.claude/workflows/wave-r9-groups.json` on `handoff/audit-r9-fixplan`. The residual class is stated where the score is read, in `tools/audit/archscore/ABOUT.md`.

## Friction

- gate-scoping.md: unclear: setting `HPO_GATE_LOCK_LABEL` without first running `gate_lock.py take` makes `run.sh` refuse `stress.py`. In round 1 I stopped my own run and re-ran it without the label.
- fixer.md: cost: step 2's `mutation_table.py --scope changed` drives `features.py` once per mutant (about 450 s here), so the ledger's completeness check, which runs in seconds, is the part a seat can afford before pushing; it is not named in step 2.
- fixer.md: cost: a disk-cleanup seat deleted this seat's scratch after the round-2 commits. The commits survived in the shared object store and are pushed. The body and the parity and ledger harnesses were retyped and re-run, and the figures above come from that re-run.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
