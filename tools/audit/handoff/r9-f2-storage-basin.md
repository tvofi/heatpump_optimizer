<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Main went red at 058e89f1, the merge of #1694 (round-9 F2.1). `tests/backtest.py` failed 1 of 25 on CI: "storage pays where the spread is wide, beyond any arm asymmetry [typical +0.79 vs flat null -0.18 SEK/day at 750 L]". This blocks the merge queue and the v6.7.3 hotfix stamp.

This PR restores the storage margin without lowering the check.

- **The cause is a lost solver basin, not a moved premise.** #1694 prices each zone of a two-zone house at the full linear floor price (D2-s2-81). On the backtest's 750 L storage house under winter_typical prices, main's own objective scores the plan the old half-price floor found at 110.437. Main ships a plan it scores 111.267 instead.
  - Seeded with the old plan, main ships the old plan.
  - The start that lost it is the smooth first guess. It scores identically on both trees, because it breaches no floor. It refines to 110.437 at 48b696c1 and to 111.880 on main: its descent crosses the floor, where the steeper price bends the path.
  - The storage premise holds under both objectives. The flat-price null arm is unchanged.
- **The fix is a continuation.** A two-zone solve now refines its first start at the half floor price, then hands that point to the true solve as the first start in place of the raw guess.
  - The objective is unchanged, so #1694's parity pins still hold.
  - What ships is still the true objective's minimum over every start.
  - The start is replaced, not added, so a two-zone solve costs one extra plain L-BFGS-B run, not another candidate and polish.
  - That run happens inside `_multi_start_minimize`, through a new `move_starts` hook (an identity by default, and for a single-zone house), and under the multi-start's own `maxiter`. A cut budget therefore starves it too, which `optimality.py`'s iteration-budget race requires: run outside the budget, the starved arm kept a full-budget first start and the race's gap fell to 4.0% against its 5%.
- **The three claims inherited from #1694 are dropped.** `env_drift.py --drop-inherited` against main. The two fixtures this change moves are claimed with direction; both ship a lower true objective.

Part of #1654 (P3). Part of #201.

## Head

Code head efb4c6c407c86d8d65395338060c124b6c4cf5cf, cut from 6ff749d6c1d61a311308c2373fb47ae1d9ff4198 (origin/main), which is also its merge base. The handoff commit stacked on it carries only this body and its evidence.

### Environment

CI's red reproduces here exactly, in the pinned lock environment: CPython 3.14.7 with `pip install --require-hashes --build-constraint tests/requirements-build.txt -r tests/requirements-ci.txt` (numpy 2.4.6, scipy 1.17.1, scipy-openblas 0.3.31, DYNAMIC_ARCH), OMP/OPENBLAS/MKL at 1 thread as the workflow sets them. What decides the result is OpenBLAS's kernel choice, which follows the runner's CPU:

| tree | kernel | typical | flat | margin | check (needs ≥ 1.0) |
|---|---|---|---|---|---|
| 6ff749d6 (main) | Haswell (`OPENBLAS_CORETYPE=Haswell`) | +0.79 | -0.18 | 0.97 | red, CI's exact figures |
| 6ff749d6 (main) | Zen | +0.79 | -0.18 | 0.97 | red |
| 6ff749d6 (main) | SkylakeX (this box's default, AVX-512) | 1.56 | -0.41 | 1.96 | green, which is why #1694's gate and a reviewer's box read it green |
| head | Haswell | 4.09 | -0.18 | 4.27 | green |
| head | Zen | 4.09 | -0.18 | 4.27 | green |
| head | SkylakeX | 4.79 | -0.41 | 5.20 | green |

On the Haswell kernel, in that environment: the new check fails at main [shipped 111.2671, seeded with the half-price plan 110.4366] and the block passes 17 of 17 at head; `backtest.py` 25/25, `optimality.py` 84/84, `golden.py` and `env_drift.py --all 6ff749d6` with the same two CLAIMED, the one MAY-DRIFT and NO UNCLAIMED DRIFT. The pinned typing ruler (`tests/requirements-typing.txt`, `--no-deps`, as CI installs it) passes with `--mypy`.

## Mutation proof

The new check in `tests/features.py`'s `R9-F2.1` block is "the shipped storage plan is no worse on its own objective than the half-price floor's plan refined under it". Harness: the block sliced between its marker and `# -- #1524`, run by `run_block.py` (see Figures).

- At main (6ff749d6), with the check alone: FAIL `R9-F2.1 P3: the shipped storage plan is no worse on its own objective than the half-price floor's plan refined under it` [shipped 111.2672, seeded with the half-price plan 110.3808]. 15 of 16 pass.
- M1, the continuation disabled (`move_starts` returns its candidates before setting the half price): the same check fails with the same figures.
- M2, the continuation's reset removed (`finally: pass`), so the true solve runs at the half price: FAIL on the storage check [shipped 110.4367, seeded 110.1066] and FAIL `R9-F2.1 P3: the continuation leaves each zone's floor at the full linear price once the solve returns` [after a two-zone solve 3.0, a fresh optimizer 5.0]. 15 of 17 pass.
- Restored: 17 of 17 pass.
- Two more checks in the block pin the continuation's hand-off. They run #234's two-zone solve with both solvers stubbed, and they need the full `tests/features.py`, because the slice harness lacks #234's fixtures.
  - The first says "the continuation refines the first plain start, after the extra starts, within the multi-start's own iteration budget". Mutant s2 (`cands[0]` for `cands[first]`) fails it: [budgets [7]; moved [True, False, …]], so the extra start moved instead.
  - The second is "(null arm, single-zone): a single-zone solve runs no continuation". The guard's GUARD_OFF fails it: [continuation budgets on the single-zone solve: [7]].
  - The head passes 3408 of 3408.
- Mutation ledger: `mutation_table.py --pin-killed --base 6ff749d6` pinned RETURN_DEL (killed by features.py). The guard's GUARD_OFF survived every driver, so I added the null arm above, and a second `--pin-killed` run pinned it. `--scope changed` now reads 3670 unpinned, equal to the base.

## Null control

- The single-zone arm of the same check (a 750 L single-zone house, whose floor never changed) passes at main and at head.
- The flat-price storage arm, the check's own null: `_store_gain['flat']` is -0.4074 at main and at head, byte-identical.
- Goldens: every fixture but the two claimed ones and the may-drift `valve_upper_direct_slab` is byte-identical to main (`env_drift.py --all`).

## Figures

Unless the table above says otherwise: CPython 3.14.0rc2 with the same numpy/scipy pins, 4-core Intel Xeon (AVX-512, SkylakeX kernel), OMP/OpenBLAS pinned to 1 thread, PYTHONPATH=tests/hastub. Probe scripts travel on the handoff branch under `tools/audit/handoff/r9-f2-storage-basin/`, stripped before the push.

- `bt_gain.py` execs `tests/backtest.py` up to the wood-furnace section and prints `_store_gain` and the checked margin, `winter_typical - flat`:
  - 48b696c1 (main before #1694): typical 4.3707, flat 0.7628, margin 3.6079.
  - 6ff749d6 (main): typical 1.5557, flat -0.4074, margin 1.9631. CI read 0.97, so the same basin miss lands deeper there.
  - Head: typical 4.7896, flat -0.4074, margin 5.1970.
- `bt_cross.py` solves the 750 L winter_typical arm on one tree, seeded (`_prev_shipped_plan`) with either tree's plan, and prints `objective_value`:
  - Main unseeded: 111.2672. Main seeded with 48b696c1's plan: 110.4366, and it ships that plan.
  - 48b696c1 unseeded: 110.4366, and main's plan loses there too.
- `bt_seeds.py` refines each start alone and prints its result, 48b696c1 → main: start 0 110.4366 → 111.8804; start 1 111.5051 → 112.5065; start 2 111.5342 → 113.0234; start 3 110.5332 → 111.2672; start 4 111.8083 → 111.8127.
- A rejected alternative, pricing the quadratic undershoot in full as well: margin 0.7789.
- Another rejected alternative, a Huber-smoothed floor kink: margin 4.40. It breaks #1694's slope parity at zero breach, and it would have to reach single-zone homes too.
- Rejected: a `# pragma: no cover` except around the continuation. The coverage ratchet's pragma row refuses it (13 > 12, caught by `entities.py`), and a raise there is the objective's own, which fails the refine anyway. The half price is still reset in `finally`.
- Rejected: the continuation as its own one-start multi-start. It counted as an extra candidate and polish (`optimality.py`: every candidate is refined) and as the first multi-start call (`features.py`: extra starts lead).
- Rejected: the continuation as an added start rather than a replacement. Margin 5.3609, at 19–40 % more CPU per two-zone solve.
- `gcap.py` runs `golden.capture` per scenario, main → head, true `objective_value` then process CPU seconds:
  - valve_storage_flat_prices 127.2155 → 127.1950, 6.3 → 7.7 s.
  - valve_storage_small_tank 80.4944 → 79.9648, 39.7 → 43.1 s.
  - valve_upper_direct_slab 100.8374 → 100.3468, 5.2 → 6.5 s (head CPU read with other gate lanes running).
  - winter_two_zone_no_dhw 77.7898 → 77.7898, 3.1 → 3.2 s.
- Gate (`closure.py select`: SCOPED, 22 scripts), at the final code head or a semantically identical parent, all rc 0: backtest 25, card, card_drift, config_flow_steps 454, deployment_shape, doc_claims 39, edge, entities 1973, env_drift, features 3408, finite_boundary 51, golden, guard_pins 7, manual_plan 85, optimality 84, plan_view, solar_alignment, stress 87 (run alone), structure, typing_ruler 11 (and `--mypy` pinned), validate, wood_advisor 7.

## Red checks

- `backtest.py`, on the push to main at 058e89f1: "storage pays where the spread is wide, beyond any arm asymmetry".
  - Cause: #1694's full-price floor steepened the path of the first two-zone start through the floor, and the multi-start lost the 750 L storage basin. This is class P4, basin sensitivity.
  - Fix: above.
  - Cheaper detector: `tests/backtest.py` was in #1694's scope. It read 25 of 25 at #1694's head on this box, with margin 1.96 against the check's 1.0, because this box's AVX-512 kernel lands in a shallower miss; CI's Haswell-class kernel reads 0.97. #1694's PR CI did not report backtest (per the coordinator's relay), so the push to main was the first runner to measure it.
  - The margin check itself was the detector. `OPENBLAS_CORETYPE=Haswell` reproduces CI's figures on an AVX-512 box. No new check: the block's new arm now pins the basin by objective, which does not depend on the runner's margin.

## Forward-carry

none: this PR carries nothing a later stage must change. F2.4 (P4 basin sensitivity) can read the rejected-alternative figures above from this body.

## Friction

- fixer.md#5: cost: #1694's scoped gate ran backtest on a dev box whose AVX-512 BLAS kernel still cleared the check (1.96 against 1.0), while CI's Haswell-class kernel read 0.97. `OPENBLAS_CORETYPE=Haswell` puts a cloud seat on CI's side. A margin check on a basin-sensitive solve is a runner property until the basin itself is pinned, as the block's new arm now does.
