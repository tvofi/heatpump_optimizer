The away-recovery estimate ran a model kernel on the event loop. `away.estimate_recovery_hours` steps `ThermalModel.simulate_step` up to `MAX_RECOVERY_HOURS / 0.25` times. Its route was `coordinator._resolve_away` -> `away.resolve` -> `_apply_return`, inline in `async_run_optimization`. The P10 barrier in `tests/replay.py` never reached that path, because none of its arms sets away. `_replay_interval`, the house and lower-floor loss learners' interval replay, is the sibling seam: it is on the loop and no arm drives it, because the barrier's fixture is DHW-only (D14-s1-01). Closes #2237.

**What changed.**
- `away.resolve` and `_apply_return` are awaited, and they take the recovery estimate as an awaitable, `estimate_recovery: RecoveryEstimate`. It replaces the `model`, `thermal_state` and `outdoor_temp` parameters.
  - The coordinator binds it with the new module-level `_recovery_off_loop(hass, model, live)`. That helper runs `away.estimate_recovery_hours` through `_await_off_loop` on a `replace()` snapshot of the live state, taken on the loop.
  - `away.resolve` now has 9 parameters, so its `PARAMS_OVER_10_LEFT` row in `tests/arch_score_head.py` is dropped. The check refuses a stale row.
- `_replay_interval` reads its inputs on the loop (the weather, the metered heat, the interval's hour) and hands them to `_await_off_loop` with the new pure module-level `_replay_step`. That function holds the `simulate_step` call verbatim, with its #53 comment. Its two call sites await it.
  - The job is shipped by name, as sysid's `step_detached` is. `tests/deployment_shape.py` resolves every object shipped to the worker and refused a `functools.partial` over a bound method.
  - The humidity seam rule's allow-list entry in `tests/features.py` follows the call to `("coordinator.py", "_replay_step", "simulate_step", "state")`, and so does the R9-UX-10 profile pin.
- `_resolve_away` now contains an await, so `async_set_away` (the Plan-page switch and the `datetime` entity, both `refresh=False`) can write the live away state in the middle of a resolve.
  - The resolve publishes only when the live state is unchanged across the await (`if self._away_state == written`). Otherwise it keeps the write.
  - The override expiry's two in-place writes move verbatim into a sync `_expire_away_override`, where no await splits them. They are the same statements, each joined onto one line. Its `tests/seam_map.json` entry is `core`, the seam of `_resolve_away`.
- The house-loss learner reads `ctx._thermal_params` once, before the replay's await, instead of once on each side of it.
- The barrier gains an `away` arm and a `learner` arm, each with a worker-route witness, so an arm that stops reaching its seam reads red. The witness is every package frame under a worker kernel call: the in-process worker keeps the parent's frames on the stack.
- `dev/audit/harnesses/ux10_flow_into_model.py`'s `PREDICTED_GUARD` text follows the awaited call site. That harness asserts each pattern occurs exactly once, so at this head it would otherwise refuse before running.

**A departure from the architect note, raised rather than made silently.** The note's owning seam in `coordinator.py` is "the `_replay_interval` call site". The brief's own fix, moving `estimate_recovery_hours` off the loop, cannot land there. It needs `_resolve_away`, its call site, and the new module helper. The carry says R10-LIVESTATE edits the away override path after this group and asks that it not be reshaped here.
- The override statements are unchanged, but they now sit in their own sync method.
- R10-LIVESTATE is `not-started` in the roster (`resume.stage`), and its `after` list names this group. So the hunks are no concurrent conflict surface. Its brief owes a carry, given under `## Forward-carry`.
- The orchestrator decides whether the after-edge stands as is.

## Head

`1b4fbc55bd9038385f7938595f70933b1e48e055`.

It is `add0c1023` (the fix), a merge of `origin/main` at `de69745ff` (no rebase), and three commits after it:
- `2854b1384` and `3d87e5910`: the replay's step shipped by name, after `tests/deployment_shape.py` and the typing census refused the first shape;
- `1b4fbc55b`: the structure re-record.

Every figure below was taken at this head, or at its base `de69745ff`. The base figures were taken after the merge, and the base did not move after that. Measured on 2026-10-22 22:17 UTC with `origin/main` at `de69745ffcab66b566b3e75aee0b572023f80857`. `git merge-base --is-ancestor origin/main HEAD` exits 0. Python is `/opt/hpo/venv-ci`.

## Mutation proof

Each mutant was applied alone in a detached `git worktree` at this head and then reverted. The applier is a scratch probe: one `str.replace`, asserted to match exactly once. The barrier checks are `replay.kernel_checks()`, the P10 block `tests/entities.py` runs. `features.py` was run whole with `PYTHONPATH=tests/hastub`.

| site | mutant | red | run |
|---|---|---|---|
| `_replay_interval`'s `return await _await_off_loop(coord.hass, _replay_step, ...` | the job called inline: `(lambda h, f, *a: f(*a))(coord.hass, _replay_step, ...` | `P10: the space-heating learners replay the elapsed interval in the process worker, never on the loop` (`'loop': 5`, site `coordinator.py:_replay_step`) | 1 of 5 barrier checks |
| `_recovery_off_loop`'s `return float(await _await_off_loop(` | called inline: `float((lambda h, f, *a: f(*a))(` | `P10: an away override's recovery estimate simulates the ramp in the process worker, never on the loop (D14-s1-01)` (`'loop': 183`, site `away.py:estimate_recovery_hours`) | 1 of 5 barrier checks |
| `_recovery_off_loop:return estimate` (ci_predict `RETURN_DEL`) | `pass` | the away check above | 1 of 5 barrier checks |
| `_expire_away_override:return active, ret` (ci_predict `RETURN_DEL`) | `pass` | the away check, and `P10: an armed system identification sizes, gates and fits its night in the process worker, never on the loop` | 2 of 5 barrier checks |
| `_resolve_away`'s guard `if self._away_state == written:` (ci_predict `GUARD_OFF`) | `if True:` | `D14-s1-01 the away recovery estimate is handed off the loop, and a switch written during its await is not reverted by the resolve's publish` (read back: `override_active=True`, the switch's `False` reverted) | `1 of 4307 FEATURE CHECKS FAILED`, rc=1 |

Failing test first: the head's `tests/replay.py` over the base's production code (`git checkout de69745ff -- custom_components/` in a worktree at this head). It reads both new arms red: `'loop': 183` at `away.py:estimate_recovery_hours` and `'loop': 5` at `coordinator.py:_replay_interval`. The three old arms read green.

## Null control

- **The carry's control.** With the deficit at 0, `p10_seams.py --away --deficit 0` reads `loop_kernels_away_seam=0` at both ends, so `estimate_recovery_hours` returns before simulating. At deficit 2 it reads 183 at the base and 0 at the head. That is the finding and its fix, not a scenario that stopped reaching the seam.
- **The head's 0 still reaches the seam.** The barrier's `away` arm reads `worker:simulate_step` 1911 against the `base` arm's 1728, which is +183, the base's loop count, now on the worker route. The `learner` arm reads 1733, which is +5. At the base's production code, both arms read the base arm's 1728 on the worker and carry the difference on the loop.
- **The unmutated head.** All 5 barrier checks pass, and `features.py` prints `ALL 4307 FEATURE CHECKS PASSED` (rc 0).
- **The new features check's arm.** The test's `_await_off_loop` stand-in records the job it was handed, and the check asserts that this was `estimate_recovery_hours`. So it fails if the resolve never reached the estimate, as well as if the guard reverts the write.

## Figures

**Finder's harness:** `dev/audit/rounds/round10/D14/s1/p10_seams.py`, sha1 `c8ba174c3fa7f6768a7576d31b6597835df45589`, byte-identical at base and head (`git diff --quiet de69745ff HEAD -- dev/audit/rounds/round10/D14/s1/p10_seams.py` exits 0). The base run used a full checkout of `de69745ff`. Each command is `HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/s1/p10_seams.py <args>`, over 6 cycles each.

| args | base `de69745ff` | head |
|---|---|---|
| `--away` | `loop_kernels_away_seam=183`, `loop_kernels_all=183` | `loop_kernels_away_seam=0`, `loop_kernels_all=0` |
| `--away --deficit 0` | 0, 0 | 0, 0 |
| `--arm base` / `fallback` / `sysid` | -- | `loop_kernels_all=0` each; fallback `barrier_set_executor=3881` (the #511 trade) |

**The class census (fixer.md step 8).** The rule is the finder's static seam list, `p10_seams.py`'s `static_seams()`: every call of a `simulate_*`, `numpy.linalg` or `scipy.optimize` name in the package. It reads 36 sites at both ends. One site moved: `coordinator.py:_replay_interval:simulate_step` at the base is `coordinator.py:_replay_step:simulate_step` at the head (`diff` of the two `--away` runs' `seam` lines prints that one pair). Each returned site and its disposition:
- **Closed in this diff:** `away.py:estimate_recovery_hours:simulate_step`, read on the worker by the `away` arm; `coordinator.py:_replay_step:simulate_step`, read on the worker by the `learner` arm.
- **Guarded, worker-run, and reached by the base, sysid, away and learner arms** (worker witness from `python3 tests/replay.py --kernels <arm>`; on the executor under `fallback`): `dhw_planner.py` `_apply_dhw_min_run`, `_build_dhw_requirements`, `_clamp_dhw_to_capacity`, `_dhw_plan_temps`, `_plan_dhw_min_cost` (both its `simulate_dhw_only` and `linprog`) and `trajectory`; `optimizer.py` `_compute_baseline_power`, `_optimize_with_dhw`, `_scoped_minimize`, `_space_traj` and `objective_batch`; `topology.py:_advisor_replay`; `thermal_model.py:extend_dhw_temps`.
- **Guarded by construction, and not driven by any arm.** Each is called only from inside the optimizer's or DHW planner's solve, which `_await_optimize` sends to the worker: `dhw_planner.py` `_dhw_coil_wood_forecast` (called from `optimizer.py`) and `_dhw_legionella_due`; `optimizer.py` `_repair_throttled_buffer_caps:solve`, `_replay_end_state`, `_solve_objectives` (both) and `_tighten_buffer_caps`.
- **Inside a counted kernel**, where the barrier counts at the outermost call: `sysid.py` `_held_state`, `_lm_solve`, `_one_state_ua_halfwidth`, `_slab_ua_profile_halfwidth`, `_valve_drive` and `identify` (both); the four sysid entries sit under `SYSID_KERNELS`, and the sysid arm reads them on the worker. Also `thermal_model.py` `simulate_trajectory:simulate_step` and `simulate_trajectory_with_dhw` (both).
- **Off the loop by its call site:** `diagnosis.py:_room_after`, reached only through `diagnose_record`, which `async_diagnose_interval` hands to `_await_process`.
- **Not a model kernel:** `coordinator.py:async_simulate:simulate_wood_slots`, which parses slots (the finder's own disposition). `drift.py:_positive_definite:cholesky` validates a stored k x k reference covariance at store load, once per load and not per cycle, where k is the stored reference's length. No arm drives it.

**The barrier:** `replay.kernel_checks()` (scratch driver: `for name, ok, detail in replay.kernel_checks(): print(...)`). It reads 5 of 5 pass at this head. With the base's production code, it reads 3 of 5 (`## Mutation proof`).

**The scoped gate:** `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 23 script(s) run, 10 scoped out.` The gate ran as `PYTHONPATH=tests/hastub GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=de69745ffcab66b566b3e75aee0b572023f80857 bash tests/run.sh`: `25 TEST SCRIPT(S) PASSED; 9 SCOPED OUT AND NOT RUN`, rc 0 (scoped mode, not a full gate; CI's push to main runs it unscoped).

**Structure:** `python3 tests/structure.py` exits 0 at this head. Its one moved row is re-recorded in `1b4fbc55b`, with the reason in the commit message: `class_excess_loc` 18268 -> 18258, by `--record` on a clean tree. The model step left `_replay_interval`, a helper handed the coordinator, for the pure `_replay_step`, which takes none. Within the class itself, the guard's single `replace(resolved, ...)` publish and the joined expiry lines leave the line count flat. `seam_cut_total` would have read +1 from `coord.hass` in the learning seam. That is paid by the single `ctx._thermal_params` read in the house-loss learner, and the row reads 708 against 708.

**Architecture score:** `python3 tools/audit/archscore/score.py --diff origin/main` prints `dS +0.1687 WORSENS (inadmissible: coord_footprint 2489->2491)`, with `params_over_10 8 -> 7`. `python3 tests/arch_score_head.py` prints `ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED`.

**The agreement lane** (the brief's instruction), run on both grader copies:
- `python3 -I tools/policy/agreement_py.py --out J && node tools/policy/agreement.mjs --py-json J` prints `AGREEMENT ok` (rc 0) on the branch copy.
- It prints the same on a worktree at this head with every path the `wave-script` job restores taken from the base (`git checkout de69745ff --` over that job's pathspec list). This diff touches one pinned path, `tests/replay.py`.

**The R9-UX-10 harness**, `dev/audit/harnesses/ux10_flow_into_model.py` (sha1 `5e92ff7d4e06e9ab897e4dd133abd7c5c34aab0a` at this head, with one line changed: `PREDICTED_GUARD`), run as `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/ux10_flow_into_model.py OUT`.
- At the base (a full checkout of `de69745ff`, which carries the base's copy of the harness) and at this head, its `BLOCK` lines are identical: `diff` of the two prints nothing, and both include `m_guard_off_house` and `m_guard_off_lower` at `failing_checks=1`.
- Both runs then end in the same `KeyError: 'UPPER_PLANTED'` in the harness's own summary step, rc 1. That failure predates this branch and is outside this group.

**Cost.** No timing figure is taken. The finding is a count, which contention cannot move. Each offload costs a worker round trip, a pickled `ThermalModel` (2508 bytes at defaults, from `pickle.dumps(ThermalModel(ThermalParameters()))`), and an away resolve only when a return time is set.

## Architecture score

- `coord_footprint` 2489 -> 2491: the net of the logic statements this diff adds to the coordinator's charged span against those it moves out. It adds the publish guard and the expiry split, whose call returns the override; it moves the replay's model step out to `_replay_step`. The await that the P10 fix puts in `_resolve_away` requires the guard and the split: without them the switch's override write is reverted, or the expiry's in-place writes sit in an async method (`shared_inplace_writes 17 -> 19`, measured before the split).

## Alternatives

- **Estimate on the loop but cache it per solve.** This leaves the kernel on the loop on every cycle where the cache is cold, so P10 stays open.
- **Precompute the estimate before `away.resolve`, always.** This spends up to 96 worker steps per cycle on a house that is simply below comfort while nobody is away. It would also put the comfort target outside the resolve, where the finder's harness no longer reaches it (the harness raises the target through `resolve`'s `comfort_temp`), so the head's 0 would be vacuous.
- **Run all of `away.resolve` in the worker.** `_parse_return_time` loads a typed wall time in `dt_util.DEFAULT_TIME_ZONE`, which the worker interpreter does not share. A calendar end time would then shift by the zone offset.
- **Publish first and fold the estimate in afterwards.** This writes the published state in place after the publish, which is the shape R10-LIVESTATE exists to retire.
- **Ship the replay step as a `functools.partial` over the model's bound method.** This was the first shape. `tests/deployment_shape.py` refused it because the worker-bound object does not resolve to an importable name, and the humidity seam rule stopped seeing the call.
- **Keep `_resolve_away` whole and async.** This reads `shared_inplace_writes 17 -> 19` (`score.py --diff`, measured before the split), for the two expiry writes.

## Red checks

This head has not run in CI. One red is predicted:
- **`mutation`**, predicted by `prepr.sh` step 6d: the diff adds the three unpinned sites under `## Unpinned sites`. Each is killed by a value check in the scoped closure (`## Mutation proof`), and `mutation-autofix` pins killed unpinned mutants with a bot commit (`ci-autofix.md`); that commit is awaited, not duplicated. The cheaper detector is step 6d itself, which caught this before the push and has no standing cost beyond its own run.

## Unpinned sites

`PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` lists three:
- `custom_components/heatpump_optimizer/coordinator.py:1629 RETURN_DEL`: killed by the value check `P10: an away override's recovery estimate simulates the ramp in the process worker, never on the loop (D14-s1-01)` in `tests/replay.py`, which `tests/entities.py` runs (`## Mutation proof`).
- `custom_components/heatpump_optimizer/coordinator.py:9553 RETURN_DEL`: killed by the value checks `P10: an away override's recovery estimate simulates the ramp in the process worker, never on the loop (D14-s1-01)` and `P10: an armed system identification sizes, gates and fits its night in the process worker, never on the loop`.
- `custom_components/heatpump_optimizer/coordinator.py:9577 GUARD_OFF`: killed by the value check `D14-s1-01 the away recovery estimate is handed off the loop, and a switch written during its await is not reverted by the resolve's publish` in `tests/features.py`.

`mutation-autofix` pins what CI's mutation run kills (`ci-autofix.md`).

## Forward-carry

- **R10-LIVESTATE inherits an awaiting `_resolve_away`.**
  - `away.resolve` takes `estimate_recovery`, run in the process worker by `_recovery_off_loop`.
  - `async_set_away` can therefore write the live away state inside the resolve.
  - The resolve publishes only when the live state is unchanged across the await. The override expiry's in-place writes sit in the sync `_expire_away_override`.
  - A copy-then-publish-whole of the away state keeps that guard or an equivalent.
  - Its control is the `features.py` check `D14-s1-01 the away recovery estimate is handed off the loop, and a switch written during its await is not reverted by the resolve's publish`, which reads red with the guard as `if True:`.
  - Re-measure at your merge base.
  - **Not yet in the roster:** this seat writes only its return refs, and the roster's writer, `roster_edit.py`, pushes to `handoff/audit-r10-roster`. It is owed before this merges: `python3 tools/audit/seat/roster_edit.py append-carry R10-LIVESTATE "<the text above>" --push`.

  Carry: R10-LIVESTATE

- **`ux10_flow_into_model.py`'s summary step raises `KeyError: 'UPPER_PLANTED'` at the base as at this head** (`## Figures`). It is a harness defect outside this group's seam, so it is left for the orchestrator to route. No issue was filed.

  Carry: dismissed: pre-existing at base de69745ff, routed to the orchestrator in this body

## Friction

- orchestrator.md#5: contradiction: R10-LOOP-CPU's architect note names one owning seam, the `_replay_interval` call site. The group's brief moves `estimate_recovery_hours`, whose only route runs through `_resolve_away` and its call site, so the brief cannot land within the note. Carry: dismissed: raised in this body for the orchestrator's after-edge call
