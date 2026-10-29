R10-COP-PARTLOAD: price the compressor's power in COP, off by default

`ThermalModel.compute_cop` priced a heat pump's efficiency from outdoor
temperature, humidity and flow or tank temperature only. Electrical power entered
every heat conversion as a plain multiplier, `heat = cop * power`, so the model
called a compressor equally efficient at its modulation floor and at its maximum,
where the heat-exchanger approach the power sets has grown.

`ThermalParameters.cop_partload_derate` (options flow
`heat_pump_cop_partload_derate`, default 0) is the share of COP lost at maximum
power against the floor, linear across the band, refused to 0 at or past the
band's `partload_derate_limit` (band / (band + p_max)), where delivered heat
would fall with power. `thermal_model.delivered_heat_kw` and `heat_per_cop_kw`
apply it at the priced forward conversions (scalar and batch space-heat steps,
the hot-water trajectory, `extend_dhw_temps`, the optimizer's buffer charge
ceiling). At the default 0 they return `cop * power` unchanged, so no existing
install's plan moves. The options page refuses an over-limit derate on its field
(`config_flow._partload_errors`), and the pre-fill save on `base`.

The root-cause analysis is `dev/audit/rca/R10-RCA-COP-PARTLOAD.md`.

## Re-cut

This body replaces the round history. It describes one tree, the head below, and
carries only figures re-taken at that head in this pass, on an x86_64 host with
Python 3.13 and the hashed `tests/requirements-ci.txt` set. Earlier rounds'
readings (the arm64 host's) are deleted, not restated.

## Head

`3dbefe25f95cfb70b03e6455cfc0aa320537e173` merges origin/main `3042dcd4f`
(which carries #2949, the `ref_privacy` fix the previous seat stalled on) into
the PR head `8ecde5f26`. origin/main's tip was `3042dcd4f` at
2026-10-29T15:01:19Z, the time the figures below were stamped.

The merge resolved three conflicts by hand. Each resolution is in the merge
commit's message.

- `config_flow.py`, a semantic conflict. Main folded `_options_suggested_numeric`
  and `_suggested_entity` into one `_suggested_optional`. This branch had only
  added `_partload_errors` directly above the old helper. The resolution keeps
  `_partload_errors` and takes main's `_suggested_optional`. No caller of the
  deleted helper remains:
  `grep -rn _options_suggested_numeric custom_components` returns nothing.
  `_prefill_errors` and `_try_thermal_model_save` both still call
  `_partload_errors`, as at `8ecde5f26`.
- `thermal_model.py`, a semantic conflict. Main's single-zone batch step now
  runs a throttled single-valve law (`_single_valve_rates`) after
  `thermal_power = cop * power_i + ext`. This branch had renamed `power_i` to
  `heat_per_cop_i`, the draw's heat per unit of COP taken once per schedule. The
  resolution is main's block, with its COP call passing `throttled`, and the
  branch's product: `thermal_power = cop * heat_per_cop_i + ext`. `power_i` no
  longer exists, so main's block would have raised `NameError` unmodified.
  `## Mutation proof` M2 shows this line is pinned. Main added no other
  `cop * power` site to `thermal_model.py`, `optimizer.py` or `coordinator.py`.
  The command was a grep of main's added lines (three-dot from the merge base)
  for a product of a COP with a power. Its one hit was
  `wood_draw = min(w * drawn, ...)`, which is not a heat-pump conversion.
- `tests/golden/claimed_drift.txt`. The `claimnotes` driver refused it as a
  claim list both sides rewrote. The resolution is main's list (its
  R10-BUFFER-STORE claims and suspended may-drift notes, untouched), plus this
  branch's one `config_flow` claim. `env_drift.py --all` reads it as below.

The ledger driver merged `tests/structure_budgets.json` (`class_excess_loc`
17762) and `tests/closures.json` (`inert_reads` as a set) without a conflict.

## Mutation proof

Run by `$SCRATCH/mutants.py` (sha1 `8baf968f7aad`). It applies one mutant to
`thermal_model.py` in a throwaway worktree at `3dbefe25f`, runs
`tests/features.py` there, prints the failing check names, then restores the
file with `git checkout --`. Both runs end with `git status --short` empty.

- M1: `partload_factor` returns `1.0`, so the derate's law is removed. Result:
  `7 of 4593 FEATURE CHECKS FAILED`. The failing checks are:
  - the factor's linear law
  - the pump's max-power heat
  - the scalar step's slab warm
  - the buffer's charge ceiling
  - the flat-price plan's max-power share
  - the hot-water schedule
  - the full trajectory's hot-water track
- M2, the merge's resolved line: `cop * heat_per_cop_i` is written
  `cop * np.asarray(power_matrix, dtype=float)[:, i]`, the raw draw. Result:
  `2 of 4593 FEATURE CHECKS FAILED`. The failing checks are
  `batched simulation is bitwise-identical: single-zone part-load derate` and
  `batched jac == scipy 2-point FD bit-for-bit on free variables: single-zone
  part-load derate`.

`PYTHONPATH=tests/hastub python3 $SCRATCH/mutants.py <worktree at the head> M1`,
then `M2`.

## Null control

- The unmutated tree: `ALL 4593 FEATURE CHECKS PASSED`, from the scoped gate
  run below.
- The derate at its default moves no plan. `r10_cop_partload.py` was run at
  `3dbefe25f` and at origin/main `3042dcd4f`. At main a copy of the harness ran
  (sha1 `0b2f5ce911c0`, the tree's file), and it prints `term in tree False`.
  The 32 `d=0.0` plan hashes are identical between the two trees. The check is
  `diff` of the extracted hash lines, which printed
  `d=0 hashes IDENTICAL 32 of 32`. Its own null: at `3dbefe25f` the
  `d=0.112` hashes differ from the `d=0.0` ones, so the comparison can see a
  moved plan.

## Unpinned sites

none: `ci_predict --base origin/main` predicts no red, and this pass adds no
production site. The seven round-2 sites are pinned in
`tests/mutation_ledger/killed_by/` by the bot's `ci: pin killed mutants`
(`2b215e01e`), and CI's `tests / mutation` reads green at `8ecde5f26`.

## Figures

- The scoped gate at `3dbefe25f`:
  `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh`
  - Mode line: `MODE: SCOPED -- 30 script(s) run, 3 scoped out`.
  - Result: `1 TEST SCRIPT(S) FAILED`, which is `tests/harness_headers.py`
    (answered under `## Red checks`). Every other script is `ok`. That includes
    `ALL 4593 FEATURE CHECKS PASSED`, `ALL 113 STRESS CHECKS PASSED`,
    `ALL 84 OPTIMALITY CHECKS PASSED`, `ALL 2470 ENTITY CHECKS PASSED` and
    `ALL 108 FINITE BOUNDARY CHECKS PASSED`.
- `env_drift.py --all origin/main`, run inside that gate:
  - `CLAIMED config_flow: 2 leaves moved`
  - `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main`
  - `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`

  The one claim this branch adds excuses exactly its own diff.
  `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all origin/main`
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, with
  `class_excess_loc 17762 <= 17762`. Against origin/main the budget file moves
  only `class_excess_loc`, from 17814 to 17762, which is down.
  `git diff origin/main HEAD -- tests/structure_budgets.json`
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`:
  `CI PREDICT: no closures, fast, wave-script or instrument red predicted
  against 3042dcd4f6fc`
- The finding's harness, `r10_cop_partload.py`, at `3dbefe25f`. It reads
  `failures 0`. Its lines:
  - `partload: grid 27 plants; ratio at p_max >= 0.808, at p_min >= 0.985`
  - `solves: central plant derate 0.112 term in tree True`
  - `spread term vs none: cost per plant kWh change min -0.0598 max +0.0293
    cells cheaper 13 dearer 3`
  - `flat term vs none: cost per plant kWh change min -0.0810 max +0.1066
    cells cheaper 11 dearer 1`
  - `spread d=0.0: cells 16 heat short max 0.1093` and
    `spread d=0.112: cells 16 heat short max 0.0822`

  On this host, pricing the fall is therefore not a one-way gain even on
  price-spread days: 3 of 16 cells get dearer per delivered kWh. That is why
  the term ships off by default. The arm64 host's earlier reading (16 cheaper,
  0 dearer) is not re-taken here and is not claimed.
  `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_cop_partload.py`
- `tests/harness_headers.py`'s one red, measured standalone by
  `$SCRATCH/cpu.py` (sha1 `c42cc4a915ef`). It runs the harness as
  `run_harness` does: BLAS pinned to one thread, the same `PYTHONPATH`, and the
  reaped child's CPU. Both trees were run side by side.
  - At `3dbefe25f`: `sysid_estimator_frontier.py cpu=289.7s rc=0`
  - At origin/main `3042dcd4f`: `cpu=287.7s rc=0`
  - Both trees are over the 240 s headroom by the same amount (+0.7%).
  `python3 $SCRATCH/cpu.py <tree>`
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture
  score: dS +0.0000 NULL`

## Red checks

- `governance / delivery-status`, red at `8ecde5f26`: it grades main's delivery
  record, and this diff touches none of what it reads. The only delivery file
  this diff touches is its own `dev/programme/delivery/2872.md`, unchanged by
  the merge.
- `budget-raise-gate / budget-raise-gate`, red in this branch's ancestry at
  `fe964895e` (`class_excess_loc` rose) and green at `8ecde5f26`. That raise
  was paid in code by `2f082ee3b`. At `3dbefe25f` the budget file moves only
  `class_excess_loc`, 17814 to 17762, which is down, and the gate prints
  `the diff raises no cap, and the body has no raise section to judge`.
  `python3 -I tools/policy/budget_raise_gate.py --check-body BODY.md --base origin/main --head HEAD`
  Answer: `python3 tests/structure.py` names a growing row locally before the
  push, and costs about 30 s; no cheaper detector exists.
- `tests / fast (3.14)` was red in the ancestry at `fe964895e`, `bf1983846`,
  `d2e128d49` and `a7411d7ad`, and is green at `8ecde5f26`. At `fe964895e` the
  red was `tests/finite_boundary.py` (`_partload_derate` read its option
  through a bare `float()`), repaired by `54437ac84`. At `a7411d7ad`,
  run 40743208879 reads `1 TEST SCRIPT(S) FAILED`; this pass did not identify
  which script. Answer: the cheaper detector is the scoped gate run locally.
  This pass ran it at `3dbefe25f`, and its one red is the CPU-headroom line
  below.
- `tests / typing` was red in the ancestry at `fe964895e`, `bf1983846` and
  `d2e128d49` (`no-any-return` +1). It was repaired by `eeb7430a6` and is green
  at `8ecde5f26`. Answer: `tests/typing_ruler.py` is the cheaper detector, and
  costs about 1 s locally.
- `tests / mutation` was red in the ancestry at `fe964895e`, `bf1983846`,
  `d2e128d49`, `05316a9b1` and `a7411d7ad`, and is green at `8ecde5f26`.
  `tests / mutation-autofix` was red at `fe964895e` and `a7411d7ad`, and
  skipped at `8ecde5f26`. Both are red by construction while a push adds
  unpinned killed sites, and the bot's `ci: pin killed mutants` commits
  (`d2e128d49`, `ea4630ace`, `2b215e01e`) pinned them. Answer:
  `prepr.sh` step 6d is the cheaper detector, and this head adds no unpinned
  site (`## Unpinned sites`).
- `tests / nightly-status`, green at `8ecde5f26`: it grades main's nightly
  record, and this diff touches none of what it reads.
- `tests/harness_headers.py`, local only:
  `dev/audit/rounds/round4/D7/sysid_estimator_frontier.py costs at most 50% of
  its CPU bound [cpu=287.6s against 240s]`. It is not this branch's: origin/main
  reads the same, 287.7 s against 289.7 s at the head (`## Figures`), on this
  x86_64 host. CI's `tests / fast (3.14)` read the gate green at `8ecde5f26`.
  Answer: the detector is that script itself, and none is cheaper; the host's
  speed sets the reading.

## Forward-carry

- The inverse conversions still close the loop with `heat / cop`:
  `dhw_planner._plan_dhw_min_cost`, `_clamp_dhw_to_capacity`,
  `optimizer._compute_baseline_power` and `coordinator._dhw_setpoint_sweep`.
  With a derate the forward relation is quadratic in power, so the closed form
  understates the electrical power needed for a given heat, by up to the
  derate. At the default 0 the current forms are exact.

  Carry: R10-COP-PARTLOAD
- D2's item 2 lists the inputs its COP step sweeps, and power is not among
  them. The countermeasure is one sentence in `dev/governance/dimensions/D2.md`:
  derive the priced formula's inputs from the device's own control surface.
  That is policy, which the owner approves; this seat did not edit it.

  Carry: R10-COP-PARTLOAD

## Friction

none

## Architecture score

Architecture score: dS +0.0000 NULL (`python3 tools/audit/archscore/score.py
--diff origin/main`, origin/main `3042dcd4f`, at `3dbefe25f`).
