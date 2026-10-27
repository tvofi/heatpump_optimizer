Part of #2499.

On an install with a power entity and no floor-return sensor, the slab estimate advances through the house learner's own `_replay_interval` at the metered space draw (`coordinator._propagated_slab`), instead of along the previous plan's commanded `slab_temp_trajectory`. With no reading, no previous sample or a gap outside `(0, HOUSE_LOSS_MAX_SAMPLE_HOURS]` it falls back to the plan's trajectory, as before; a resistive element sharing the meter keeps the plan's trajectory; a reading at or below `draw_range.running_kw`'s floor is standby. An install with no power entity is unchanged.

This round merges `origin/main` into the round-5 code and pins the seven mutation sites the diff adds. It changes no production line.

## Head

f7ee98672ef780aea83807147d7a18709e4d5612: fe96b2289e66d9dfe188caa507f3c9dc02ea762a merged with `origin/main` f40142d66c9cc8e2f144a815990fc1fe1d99d9a8 (fetched 2026-10-25), plus the ledger pins. Merge base f40142d66c9cc8e2f144a815990fc1fe1d99d9a8. Every figure below was taken at this head unless it names another tree.

## Mutation proof

Each site the predictor lists, driven by `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --jobs 4`, with `--scripts` set to every driver in play except `tests/entities.py` (see `## Null control`). The killing run of each is recorded in its `tests/mutation_ledger/killed_by/` entry:

| site | mutant | killed by | run |
|---|---|---|---|
| `coordinator.py:5443 BOOLOP` | `and` -> `or` | `tests/features.py` | rc=0 failed=0 -> rc=1 failed=4 |
| `coordinator.py:5445 RETURN_DEL` | `pass` | `tests/features.py` | rc=0 failed=0 -> rc=1 failed=8 |
| `coordinator.py:6487 BOOLOP` | `and` -> `or` | `tests/harness_headers.py` | rc=0 failed=0 -> rc=1 failed=15 |
| `coordinator.py:6487 GUARD_OFF` | `if False:` | `tests/features.py` | rc=0 failed=0 -> rc=1 failed=2 |
| `coordinator.py:6512 GUARD_OFF` | `if False:` | `tests/features.py` | rc=0 failed=0 -> rc=1 failed=8 |
| `legionella.py:482 GUARD_OFF` | `if False:` | `tests/features.py` | rc=0 failed=0 -> rc=1 failed=2 |
| `legionella.py:487 RETURN_DEL` | `pass` | `tests/typing_ruler.py` | rc=0 failed=0 -> rc=1 failed=1 |

The same four `features.py` mutants applied by hand, each in its own detached worktree at a22eece4ef3d03b5404025cd15d9587ee7663d46 (the merge, before the pins), `PYTHONPATH=tests/hastub python3 tests/features.py`:

- `legionella.py:482` -> `if False:`: `1 of 4385 FEATURE CHECKS FAILED`, `#2499: a tank at the disinfection temperature resets the legionella timer through the coordinator's cycle; a cooler reading or none leaves it unset [hot=None cool=None none=None]`.
- `coordinator.py:6487` -> `if False:`: `1 of 4385 FEATURE CHECKS FAILED`, `#2499: a tank reading reaches the DHW learner, and its freeze reason the coordinator; no reading reaches neither`.
- `coordinator.py:6512` -> `if False:`: `7 of 4385 FEATURE CHECKS FAILED`, among them `D12-s1-01: and the slab seed follows the previous plan, not the one-time room+1 K seed` and `#2499: the slab rises with the metered draw, below the commanded trajectory while the pump draws less than 4 kW`.
- `legionella.py:487` -> `pass`: `ALL 4385 FEATURE CHECKS PASSED`; its kill is `tests/typing_ruler.py`'s, above.

## Null control

- The pin drive's own null control, a comment-only edit (`coordinator.py:514 NULL_COMMENT`), `survived every driver`; each killing driver's baseline was `rc=0 failed=0`.
- The unmutated head: `ALL 4385 FEATURE CHECKS PASSED` (scoped gate run below).
- Why `tests/entities.py` is out of `--scripts`: the first drive with every driver printed `MUTATION TABLE INCONCLUSIVE` on `the baseline is already red in tests/entities.py`, after which it reported every remaining site `lives`. `PYTHONPATH=tests/hastub python3 tests/entities.py` at `origin/main` f40142d66 prints the same `2 of 2440 ENTITY CHECKS FAILED` (`gate-sweep.yml: on CI's completion ...`, `graders-head-copy's delivery_status step ...`), so that red is this container's, not this diff's. The single-site drive `--anchor "custom_components/heatpump_optimizer/legionella.py:LegionellaGuard.async_observe GUARD_OFF c97515c6" --scripts tests/features.py` printed `killed by tests/features.py` for a site the first drive had called `lives`.

## Figures

- Structure: `PYTHONPATH=tests/hastub python3 tests/structure.py` exits 0, `STRUCTURE RATCHET PASSED`. Every row equals its budget; against `origin/main` the budget file moves `seam_cut_total` 420 -> 419, `max_class_loc` 8442 -> 8410, `class_excess_loc` 18202 -> 18201, `duplication_copies` 17 -> 16 (`git diff origin/main HEAD -- tests/structure_budgets.json`), nothing raised.
- Predictor: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` prints `CI PREDICT: no closures, fast, wave-script or instrument red predicted against f40142d66c9c` and no `ADDED UNPINNED` line. Control: the same command at a22eece4e, before the pins, printed `7 unpinned site(s) the diff adds`.
- Scoped gate: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 28 script(s) run, 5 scoped out.` `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub ./tests/run.sh` prints that mode line and `1 TEST SCRIPT(S) FAILED`: `tests/entities.py`, `2 of 2440 ENTITY CHECKS FAILED`, the two names `origin/main` also fails (`## Null control`). It printed `ALL 4385 FEATURE CHECKS PASSED`, `ALL 113 STRESS CHECKS PASSED`, `STRUCTURE RATCHET PASSED`, `NO UNCLAIMED DRIFT: 56 scenario(s) checked against f40142d66c9cc8e2f144a815990fc1fe1d99d9a8` and `no committed fixture is stale`. `git diff --quiet origin/main HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt` exits 0.
- Architecture: `PYTHONPATH=tests/hastub python3 tools/audit/archscore/score.py --diff f40142d66c9cc8e2f144a815990fc1fe1d99d9a8 HEAD` prints `Architecture score: dS +0.3255 WORSENS (inadmissible: coord_footprint 2463->2464)`, with `duplication_copies 39 -> 38` and `coord_footprint 2463 -> 2464`.

## Architecture score

- `coord_footprint` 2463 -> 2464: `_async_learn_interval` reads the house learner's baseline time (`prior_at = self._last_house_sample_time`) before `_async_learn_house_heat_loss` overwrites it. Passing it in from `_update_current_state` re-adds a seam crossing; propagating the slab on every cycle costs an off-loop replay where the slab is sensed.

## Unpinned sites

`tools/pr/ci_predict.py --base origin/main` at a22eece4e listed seven `ADDED UNPINNED` sites; each is pinned in this diff by a measured kill (`## Mutation proof`):

- `custom_components/heatpump_optimizer/coordinator.py:5443 BOOLOP`: pinned, killed by `tests/features.py`.
- `custom_components/heatpump_optimizer/coordinator.py:5445 RETURN_DEL`: pinned, killed by `tests/features.py`.
- `custom_components/heatpump_optimizer/coordinator.py:6487 BOOLOP`: pinned, killed by `tests/harness_headers.py`.
- `custom_components/heatpump_optimizer/coordinator.py:6487 GUARD_OFF`: pinned, killed by `tests/features.py`.
- `custom_components/heatpump_optimizer/coordinator.py:6512 GUARD_OFF`: pinned, killed by `tests/features.py`.
- `custom_components/heatpump_optimizer/legionella.py:482 GUARD_OFF`: pinned, killed by `tests/features.py`.
- `custom_components/heatpump_optimizer/legionella.py:487 RETURN_DEL`: pinned, killed by `tests/typing_ruler.py`.

`coordinator.py:5443 GUARD_OFF` (the COP save cadence) survived the drive; the predictor does not list it as added, because it moved unchanged from `_update_current_state`, where it was already unpinned on `origin/main`.

## Red checks

- `tests / fast (3.14)`, red at the PR head 0b03e095f: cause, that head is the round-4 head 7afd9452b merged with `origin/main` ab00437c9, and does not contain the round-5 code fe96b2289; `PYTHONPATH=tests/hastub python3 tests/structure.py` there exits 1 with `FAIL seam_cut_total 424 > 418 (+6)`. At this head it exits 0. The cheaper detector exists: `tests/structure.py` after the merge (`fixer.md` step 5, "runs before every push"), its standing cost the `17s  python3 tests/structure.py` line of the `tests / fast (3.14)` wall-clock table at 0b03e095f, per push; this round ran it.
- `tests / mutation`: predicted red at fe96b2289 on its seven unpinned sites. This head pins all seven, and the predictor lists none. The cheaper detector exists and ran: `tools/pr/ci_predict.py`, a static read at nil standing cost.

## Forward-carry

- No power entity, so a draw shortfall cannot be told from UA; the health surface must say the learned scale is unobservable there. Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-UX-HEALTH
- A standby-drawing, under-delivering pump gives the house learner no samples, because `COP_TRACKING_ERROR_GATE` in `_interval_space_power` refuses every interval. Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-LEARNER-DEFAULT
- The plan books more than the relaxed DP optimum on its own learned model, a lead and not a proof. Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-BUFFER-STORE
- The `dhw_temp_trajectory` tank seed is still open-loop. Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-BUFFER-STORE

## Friction

- R10-PIN-DRIVE-INCONCLUSIVE: cost: `tests/mutation_table.py --pin-killed` with a red `tests/entities.py` baseline prints `MUTATION TABLE INCONCLUSIVE` and then reports every remaining site `lives` with `5 survived`, the wording of a real survivor; four of those five were killed once `entities.py` was left out (three by `tests/features.py`, one by `tests/typing_ruler.py`). Carry: R10-FLOW-JIDOKA
