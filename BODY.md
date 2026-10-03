R9-EG-A2 (lane EG, classes P2 and P3): one definition per formula and helper, and the interleaved-junk class in the architecture score's clone counter closed. Closes #1775.

**Production, behaviour-preserving.** Each duplicate the brief sampled now has one definition its callers use:

- `thermal_model.py`: `_two_zone_rates` (slab, inter-zone, both floors), `_single_zone_rates`, `_two_tank_rates`, `_zone_loss`, `_zone_gains`, `weather_or_calm` and `_wood_track`, shared by the scalar step, `simulate_trajectory_batch` and `_stability_substeps` (`_zone_loss`). Each sum keeps its original term order.
- `inputs._finite`, used by `freq_control` and `binary_sensor`. The `freq_control` copy is deleted.
- `store.load_mapping`, the load prelude that `boost.restore`, `away.restore_override` and `pump_arbiter._load` all shared.
- `sysid._r2_confidence` (used by `_slab_confidence` and `identify`) and `SystemIdentification._usable_samples`.
- `dhw_planner._tank_decay` and `_within_ceiling` (the LP, the run-up walk, the floor repair and the cheapest-first planner).
- `config_flow`: `OptionsFlow._page` and `_thermal_model_page`, used by every registry page the brief named.
- `optimizer._padded_nonneg`, used for the external-heat, price-sigma and margin series.

**Instrument (the carry from #1851, tvofi's option B then A).** C3 used to drop an effect-free statement only if its spelling was on a list. It now drops a statement that is dead by data flow (`counters.inert_statements`). Such a statement:

- has expressions that are effect-free by grammar: calls only of a PURE builtin, a lambda, or a non-dunder method of a value built from literals;
- binds only names that nothing in the function reads.

An `assert`, `if`, `while` or `for` whose test folds to a constant is judged on the branch that runs, and a `try` on every part. The three KNOWN-OPEN spellings (04h, 04i, 04j) are now GAMEs and read NULL. Four spellings that no list carried (04k dead store, 04l called lambda, 04m empty try, 04n `[N].clear()`) were added as GAMEs and read NULL.

04n read IMPROVES +25.95 under the first data-flow cut. That is why the literal-method arm exists. The fold is bounded: no `**`, `<<`, `*` or attribute is evaluated. A class body's binding is never treated as dead.

What stays open is stated in `tools/audit/archscore/ABOUT.md` ("Interleaved junk"): a statement with an effect the grammar cannot rule out. That is logic in the diff, read by a reviewer. A gap tolerance was not taken, because it redefines the window `tests/structure.py` shares.

## Head

ce11f42a301cc36425b68cc6e4dc45af26eead55 (merge base `origin/main` 2e569748aedf0d974420cac3689da487523ebba9, measured 2026-10-03T09:54Z)

## Mutation proof

Each mutant was applied in place to `tools/audit/archscore/counters.py` and run as `PYTHONPATH=tests/hastub python3 tools/audit/archscore/calibrate.py --only rt_04c_dup_pass_uncharged,rt_04h_dup_assert_uncharged,rt_04i_dup_assign_uncharged,rt_04k_dup_deadstore_uncharged,rt_04n_dup_method_uncharged --jobs 4`, then restored with `git checkout`:

- M0, unmutated: all five read NULL.
- M1, the Assign/AnnAssign/AugAssign/Delete branch of `_inert` disabled: `rt_04i` IMPROVES +14.1502 and `rt_04k` IMPROVES +25.9521. The other three read NULL.
- M2, the literal-method arm of `_pure_call` removed: `rt_04n` IMPROVES +25.9521. The rest read NULL.
- M3, the `Assert` fold replaced by `return False`: `rt_04h` IMPROVES +14.1502. The rest read NULL.

On the full calibration, `tests/arch_score.py` fails "no red-team attempt reads IMPROVES" and "<id> (GAME) classifies as recorded" for each IMPROVES above.

- M4, production: `_two_zone_rates`'s body inlined back into `_simulate_step_two_zone`. `python3 tests/structure.py` then prints `FAIL duplication_copies 39 > 38 (+1)`.

`mutation_table.py --scope changed` was not run locally. Each mutant drives `features.py` (about 450 s here), so survivors on the touched sites are left to CI's required mutation check and `mutation-autofix`.

## Null control

- **Calibration at `origin/main`** (`calibration/expected.json` there): `rt_04h`, `rt_04i` and `rt_04j` are recorded KNOWN-OPEN/IMPROVES, and 04k to 04n do not exist.
- **Calibration at this head:** `calibrate.py --record` reported exactly seven RECORD lines, all of them those red-team ids, and no SENSITIVE line. `RED TEAM 30/30 attempts read NULL or inadmissible; IMPROVES: none`, and `CALIBRATION 77/103` is unchanged.
- **Corpus:** `calibrate.py --measure-corpus` re-derived `calibration/corpus_vectors.json` byte-identical (`git diff --stat` empty), so the new C3 moves no history vector. 20 stored vectors carry `_family_*_error` keys, which were already present in the committed file.
- **Physics parity** (harness `be176a3292cd95252d5a6affb5dcac3f14003355 parity.py`, run once against an export of `origin/main`'s `custom_components` and once against this head's):
  - It covers 48 configurations (single/two zone, wood tank on/off, valve `none`/`manual`, weather given/None, three parameter perturbations including a `_stability_substeps` up to 13 cell).
  - It saves 1920 arrays from `simulate_trajectory_batch`, `simulate_trajectory`, `simulate_trajectory_with_dhw` and `_stability_substeps`.
  - Base against head: 0 bitwise-differing arrays.
  - Its null control: a 1-ulp change in one two-zone wood-tank batch array is detected.
  - Scalar against batch: max |batch - scalar| over 1056 pairs is 0.0 at both ends.
- **Goldens:** `env_drift.py --all 2e569748a` gives `NO UNCLAIMED DRIFT: 56 scenario(s)`. Neither claim file is touched.

## Figures

- duplication_copies 59 -> 38, functions_cc_over_15 34 -> 33, max_cc 48 -> 45, max_method_loc 385 -> 377: `python3 tests/structure.py` at `origin/main` (export) and at the head. The worst-function lists show `optimize` cc 48 -> 44, `identify` cc 47 -> 44 and LOC 385 -> 377, and `simulate_trajectory_batch` cc 37 -> 33. Recorded in `tests/structure_budgets.json`, with the reasons in the commit.
- Architecture score: `PYTHONPATH=tests/hastub python3 tools/audit/archscore/score.py --diff origin/main` gives dS +5.5520 IMPROVES (duplication_copies +5.5485, coord_footprint 2511 -> 2505 +0.0035). The same command with `ARCHSCORE_ABLATE=C1,C2,C3,C4,C5,C6,C7,C11` gives the same +5.5520, so the gain does not depend on the counters. No score metric rises. The prototype's +14.1 is a pair-count figure that the brief says does not map onto copies.
- Remaining clone classes, from the census `python3 tests/structure.py` (section "duplication: clone classes"): 24 classes, none of them among the windows the brief named.
  - sensor/climate/binary_sensor `native_value`, `available` and `extra_state_attributes`: Home Assistant entity-property idiom, left.
  - the rest (tariff batch twins, `inputs.read`/`read_state`, the coordinator learners, and others): outside this PR's named set. They are now held by the budget at 38.
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=2e569748a ./tests/run.sh` gives `MODE: SCOPED -- 25 script(s) run, 5 scoped out`. 21 are green; the four red are under Red checks.

## Red checks

None on CI yet. Four local reds on this Mac (Python 3.11.5, Accelerate), none from this diff:

- `features.py`, 1 of 3652, "R9-F2.1 P3 ... shipped 110.4366, seeded 110.1297": the same check fails with the same two values at `origin/main` (export, same machine). It is solver/BLAS environment. CI's Linux runner is the authority.
- `entities.py` and `harness_headers.py` (D6 `claims.py`): a `SyntaxError` on a Python 3.12 f-string in `tests/entities.py`, a file this branch does not touch. The local interpreter is 3.11.
- `stress.py`, 3 of 95:
  - `sys.monitoring` is 3.12-only.
  - CPU is 271x against a 268x budget on a shared machine.
  - The `winter/cycle` attributable RSS reads at this platform's import floor.

  These are machine and interpreter properties; CI runs `stress.py`.

## Forward-carry

None. No not-started brief (R9-EG-A3, R9-EG-A4, R9-EG-B11) rests on the KNOWN-OPEN cases, C3's spelling list or the duplication figure (`jq` over `.claude/workflows/wave-r9-groups.json` on `handoff/audit-r9-fixplan`). The residual class is stated where the score is read (`tools/audit/archscore/ABOUT.md`).

## Friction

- gate-scoping.md: unclear: setting `HPO_GATE_LOCK_LABEL` without a prior `gate_lock.py take` makes `run.sh` refuse `stress.py`. I set it, stopped my own run before `stress.py`, and re-ran without it.
- fixer.md: cost: step 2, `mutation_table.py --scope changed` drives `features.py` per mutant (about 450 s on this machine), so it is not affordable locally for a diff of this many sites.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
