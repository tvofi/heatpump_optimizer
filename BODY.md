R9-EG-A2 (lane EG, classes P2 and P3). Closes #1775.

This PR gives each duplicated formula and helper one copy. The work covers:
- `thermal_model`: the zone, tank and two-zone rates, one loss per step, and the seeded trajectory arrays.
- `inputs._finite` and `store.load_mapping`.
- `sysid`: the R², excursion and SNR weights.
- `dhw_planner`: the tank decay, the ceiling clip and the breach search.
- `config_flow`: the option pages.
- `optimizer._padded_nonneg`.

The score's C3 window is gap-tolerant, as tvofi ruled.

Round 4 adds four things:
- `_substeps_and_loss` is typed as `(n_sub, float, float)`, with no `Any`.
- The three windows the gapped census showed were only split are now consolidated: the sysid weights, the trajectory seeding and the DHW breach search.
- `_padded_nonneg` is rewritten with `np.pad`, so it has no comparison left to triage.
- `04zz1` is added as KNOWN-OPEN.

## Head

40ccb15307842055b1efa02fc410738a45d7237f (merge base `origin/main` 7f5727393faa13f72dd3488c28b7d6ced28a2e06, measured 2026-10-03T20:43Z)

## Mutation proof

- **Production.** Inlining `_two_zone_rates` back into `_simulate_step_two_zone` makes `python3 tests/structure.py` print `FAIL duplication_copies 39 > 38 (+1)`.
- **C3 gap-tolerant window.**
  - With `ARCHSCORE_ABLATE=C3`, 26 of 28 interleaving attempts read IMPROVES. 04b is inadmissible on coord_footprint, and the shared census already skips 04f's string junk.
  - With C3 on, all 28 read NULL.
- **Ledger.** Every site this diff adds has a `killed_by` disposition. Each was driven by hand through `tests/features.py` or `tests/config_flow_steps.py` on an export of the branch, using the table's kill rule; each entry's reason names the check that failed. No `survivor_triage` remains.
- **Eight survivors closed with checks.** Each survived until a check was added to `tests/features.py` at the boundary its guard exists for:
  - `_within_ceiling` and `_tank_decay` clamps.
  - `_r2_confidence`: the R² clip and the strict 1e-9 floor.
  - `_substeps_and_loss`: the strict 1e-6 buffer floor.
  - `_snr_weight`'s 1e-9 noise floor.
  - `_slab_confidence`'s `max(len(error), 1)`.
  - `_dhw_shortfall`'s strict 0.05 K.

## Null control

- **Physics.**
  - 0 of 2880 arrays differ bitwise between exports of `origin/main` b09e0b912 and the head 904dc8679. The merge after that brings in only main's v6.7.15 version stamp (`manifest.json` and the card).
  - A re-association in `_two_zone_rates` changes 218 arrays. Scalar against batch, the maximum difference is 0.0 at both ends.
  - Instrument: the round-1 reviewer's `mypar2.py`, with only the path changed (my scratch `h/parity2.py`, sha1 a08a07c7c55faf673ec0d762041f5f7d6e5ae218).
- **Production calls.** On the 20 scenarios of `stress.calls_population`, every one is at or under 1.0009x of `origin/main` 7f5727393, and two-zone winter is about 0.954x. `stress.calls_drift` reports 0 over. Instrument: my 3.11 emulation of stress.py's channel, `sys.setprofile` standing in for `sys.monitoring` (my scratch `h/calls311.py`, sha1 664c14a7b42901906146d78014850f8793301a3d). CI's real channel was green at 227172ac.
- **`_padded_nonneg` rewrite.** 0 of 15144 inputs differ from the old body in dtype, shape or values. A control that pads with 1.0 differs on all 13968 padded inputs.
- **Typing.** The pinned ruler's own mypy invocation, run on exports of `origin/main` and the head, gives an identical error set apart from this machine's environment errors (`import-not-found` and the like). The two `thermal_model.py` errors CI reported are gone.

## Figures

- **Structure.** duplication_copies 59 -> 38, functions_cc_over_15 34 -> 32, max_cc 48 -> 45, max_method_loc 385 -> 374, methods_over_150 18 -> 17, all from `python3 tests/structure.py`. The reasons are in the commit messages 9b794c342 and a648731f5; 9e3bcffe1 corrects the latter's attribution to `sysid.identify`.
- **Score.** `PYTHONPATH=tests/hastub python3 tools/audit/archscore/score.py --diff origin/main` gives dS +3.3243. The gapped duplication_copies goes 87 -> 67 and coord_footprint 2517 -> 2511. No score metric rises.
- **Calibration.**
  - `calibrate.py --record` reports RED TEAM 44/44 and KNOWN-OPEN `rt_04zz1` IMPROVES (+12.63), with no SENSITIVE line.
  - `a1_G2_dedupe` reads NULL under the gap census. The reason is in ABOUT.md "Interleaved junk".
  - No corpus verdict moved.
- **Ledger.** 0 completeness problems and 0 added unpinned sites, with 4790 unpinned against 4852 at the merge base. These come from `tests/mutation_table.py`'s own pre-baseline functions, run by a scratch harness of mine that is not in the tree (sha1 d3fe581361c2bc41b53a66882df201afbb446e8a).
- **Residual duplicates the gapped census still finds.** Each was left after measuring the cost:
  - **Scalar and batch physics** (`_simulate_step_single`, `_simulate_step_two_zone`, `simulate_trajectory_batch`). They share one-line statements: `q_buf_loss`, `thermal_power`, `flow_set`, `drawn`, `avg_room` and `q_internal`, plus the call lines of the shared rates helpers. One copy would need a helper per step in the scalar loop, and one per-step helper call is the size of what this round removed: about 4.6% of a two-zone scenario's production calls. The single-zone scenarios are at 1.0009x against a 1.05x allowance, so they cannot carry one. The batch forms are vectorised, `np.maximum` where the scalar uses `max`.
  - **Trajectory step recording** (`simulate_trajectory` and `simulate_trajectory_with_dhw`). The per-step `room_temps[i + 1] = ...` lines are in the same per-step loop, so the same price applies.

## Red checks

- **`typing`** (at 227172ac): +2 mypy errors, because `_substeps_and_loss` returned a tuple-or-float behind `Any`. Answered by the typed return above.
  - Cheaper detector: the ruler's pinned mypy invocation, which runs locally in about 7 s. I did not run it before the push.
  - Two separate helpers would also have typed it honestly. Each caller already branches on the zone model, but both helpers would end with the same `n_sub` expression, a new duplicate. A named tuple would add a constructor call per step.
- **`fast (3.14)` `stress.py` production calls** (at c0f81ac9): every scenario was over 1.05x. Answered in round 3 and green on CI at 227172ac.
  - Cheaper detector: the call emulation above, about 3 minutes.
- **`mutation`**: refused at earlier heads on stale and unpinned sites. Answered by the ledger above; green on CI at 227172ac.
  - Cheaper detector for the stale sites: the table's completeness check, which runs in seconds.
- **Local only, not from this diff** (Python 3.11.5, Accelerate). CI is the authority:
  - `features.py` R9-F2.1 P3.
  - `entities.py` and `harness_headers.py`, which use a 3.12 f-string.
  - `stress.py`'s `sys.monitoring` check and its CPU factor.

  The scoped gate for this head was stopped before it finished, so these are carried from the round-3 gate at 227172ac.

## Forward-carry

R9-EG-A4's roster brief (#1774, the score becomes a required check). The roster lives on the orchestrator's fix-plan ref rather than in this tree, so the carry text goes to the orchestrator with this hand-off.

The finding: `tests/structure.py`'s adjacent census credits a split window as a removed copy. At `origin/main` it reads 59 copies where the gapped census reads 87, and this branch's first cut gained 3 of its 21 copies that way. Which census the ratchet gates on is A4's to settle.

## Friction

- fixer.md: cost: `mutation_table.py --pin-killed` refuses wherever `features.py`'s baseline is red for the environment, so every disposition here was driven by hand.
- gate-scoping.md: unclear: `stress.py`'s production-call channel needs Python 3.12+ (`sys.monitoring`), so a 3.11 seat cannot run the check that turned this PR red.
- fixer.md: cost: a cleanup seat deleted this seat's scratch mid-round 2; the harnesses were retyped and re-run.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
