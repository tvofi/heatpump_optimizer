# Round 10 class sweep: N-shared-config

This is D14 method steps 3 and 4 for the class, run after the judge. The tree is
`handoff/audit-r10-register` at `9355f107d`. Its `custom_components` is the
v7.0.0 stamp, `9cb735dfc`. The machine was macOS arm64, using the seat venv's
python 3.14. Every count below is a static count or an exact probe count.

The ledger (`dev/audit/config/bugclasses.json`) gives this class status
`barriered`. The barrier is R9-EG-B1 (#1736). It has three checks:

- `tests/arch_score_head.py` refuses any hub write that is outside
  `CYCLE_HUB_WRITERS`.
- The identity walk in `tests/features.py` refuses a solve record that shares
  any mutable object with the hubs.
- The `tests/entities.py` hand-off check.

All five judged findings sit outside what that barrier sees, or inside its
allow-table.

## Enumerator

```
PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-N-shared-config/shared_config_seams.py
```

The enumerator has four families, one for each finding's `seam_rule`, and it
scans the whole package:

| family | seam | source |
|---|---|---|
| A | an off-loop await (`_await_optimize`, `_await_off_loop`, `_await_process`, `async_add_executor_job`) in an async function that later writes `self.*` or adopts or publishes | D1-s1-02 |
| B | an in-place hub write reachable from a solve root (`archscore.metrics.hub_solve_writes`) | D7-s1-51 |
| C | an in-place write to a coordinator-held object, made in a coordinator async method or a collaborator (`archscore.metrics.shared_inplace_writes`) | D7-s1-52, D7-s1-53 |
| D | a module-level runtime channel: a `global` rebinding, `setattr` on a module-level or imported object, or a store or mutator call on a module-level name inside a function | D7-s3-54 |

Baseline output is in `D14/sweep-N-shared-config/baseline.out`. It finds
**81 seams**: A 3, B 38, C 22, D 18.

### Controls

- **Positive.** Every finding is re-found, 5 of 5 `POSITIVE ... found=1`:
  - D1-s1-02 at `coordinator.py:5720`, in `async_run_optimization`.
  - D7-s1-51 at the 22 `_current_state` sites.
  - D7-s1-52 at the 6 `_away_state` sites in `async_set_away`.
  - D7-s1-53 at `lead_pending.clear` ×2, `_solar_radiation_forecast.append`
    and `flow_meter._flow_bias.heat_output_kw`.
  - D7-s3-54 at the `setattr(planned_draw_runs, ...)` sites in `pump_arbiter`.
- **Null.** `--null` writes a clean fixture package: a coordinator that
  rebinds whole states and adopts nothing after its executor await. The result
  is `seams_total=0`.
- **Perturbation.** `--perturb A|B|C|D` adds one line of that family to the
  clean fixture. Each run gives `family_X=1` and `seams_total=1`.
- **Finding attribution.** I applied the judged prototype patches to a scratch
  tree: D7 `ALL_P1_P2_P3.patch` plus `D7-arch3-04`. The count drops from 81 to
  47 (output in `prototype_patched.out`). The 34 removed seams, plus
  `coordinator.py:5720`, are the **35 judged sites**. `5720` stays because
  D1-s1-02 has no patch. The other **46 seams** are dispositioned below.

## Disposition of the 46 non-judged seams

### Instance: 5, each with a failing probe

| seam | why | probe |
|---|---|---|
| `away.py:349`, `:351`, `:352` `apply_override_payload` | `boost.restore_session` spawns `restore_override` from the coordinator's construction, and setup never awaits it. The restore awaits `load_mapping` and then writes the stored payload into the live `AwayState` unconditionally. If the user calls `async_set_away` inside that await, the call is reverted, and its own persist saves the old value. This is the #1517 unconditional-restore shape, again in the away envelope. | `probe_away_restore.py`: `lost_midload=1`, `lost_null=0`. `--perturb` (skip the restore when the state was written since the restore began) gives `0`. |
| `coordinator.py:6053` `_thermal_params.mixing_valve_target`, `:6178` `_thermal_params.ambient_humidity`, in `_update_current_state` | The mechanism is the same as D7-s1-51: a per-cycle sensor value is written field by field into a live hub, inside an async function that has 7 awaits. P1 publishes `ThermalState` whole and leaves both sites. `CYCLE_HUB_WRITERS` allow-lists them, so the barrier passes them. | `shared_config_seams.py --root <tree with ALL_P1_P2_P3 applied>` still lists 2 such sites. The property needs 0. |

The away restore window opens only at startup, between setup and the spawned
store load finishing. The probe drives the two real functions,
`away.restore_override` and `HeatPumpOptimizerCoordinator.async_set_away`, with
the store faked. It does not show that a user can reach that window in
Home Assistant.

### Guarded: 38

- **A `coordinator.py:1483` `_sysid_step_off_loop`.** After the await,
  `vars(experiment).update(state)` writes back the worker's copy. The only
  loop-side writer of the experiment is `async_arm_system_identification`. It
  sets `config.enabled` from config, which is idempotent, and `arm()` refuses
  while the experiment is active. The step runs only while it is active.
- **A `coordinator.py:11148` `async_simulate`.** The what-if is computed from
  `replace(state)` and a base record taken before the await. It is rebound
  whole into `_simulation_cache`, and nothing actuates it.
- **B, 14 `_thermal_params` and `_opt_config` writes:**
  - `_apply_cop_scale`, `_apply_buffer_cooling_rate`,
    `_apply_house_heat_loss_scale`, `_apply_lower_floor_loss_ratio`
  - `_refresh_model_corrections` ×5
  - `_apply_learner_payloads`
  - `_apply_comfort_weight`
  - `dhw_learning` `apply_cooling_rate`, `apply_payload`, `async_learn_usage`

  Each is one synchronous field write with no await between it and its
  reader, and each is declared in `CYCLE_HUB_WRITERS`. The solve reads deep
  copies through `_solve_hubs` (#240, #1736).
- **C `_async_set_pump` `_pump_commanded`.** The cycle's pump step is the
  only writer. The write is recorded after the service call on purpose, so a
  failed command is retried.
- **C `_async_update_data:5372` `_current_action["price"]`.** It is written
  synchronously, right after `adopt_plan`, in the same step.
- **C `_async_save_if_changed` `_store_digests`.** The digest is written after
  the save. A race costs at most one redundant write.
- **C `_async_learn_price_shape` `_price_days_seen` and `_price_qdays_seen`.**
  The check and the add are synchronous. The only await is the final save.
- **C `_maybe_refresh_price_tile` `_price_tiles` ×2.** The tile is rebound per
  name. The gate can flip only through an options change, which reloads the
  entry.
- **C `async_arm_system_identification` `_sysid.config.enabled`.** This is
  idempotent; see A:1483.
- **D, 14 module-level writes:**
  - `boost._PLAN_BASES`, `boost._STATES`, `pump_arbiter._STATES`,
    `early_cutoff._STATES` and `debugger._COLLECTORS` ×2 are
    `WeakKeyDictionary`s keyed by coordinator and written only on the loop.
  - `_PROCESS_WORKER` ×3 is guarded by `_PROCESS_LOCK`, and the shutdown kills
    first.
  - `_WORKER_FALLBACK_CAUSES` ×2 is keyed by entry (#1755).
  - `store._NEWER_ON_DISK` ×3 is keyed by store key (#1869).

### Not applicable: 3

- **C `async_shutdown` `_background_tasks.clear`.** This is owner teardown,
  after the tasks have been awaited.
- **D `boost.bind_cold_lease` `global _cold_lease`.** It is bound once, at
  import of `pump_arbiter`.
- **D `_best_effort_cycle_step` `_FENCED_CAUSES`.** The fence is process-wide
  by design (D1-s2-04).

## Totals

The 81 seams split as:

- 35 judged sites: D1-s1-02 1, D7-s1-51 22, D7-s1-52 6, D7-s1-53 4, D7-s3-54 2.
- 5 instances beyond the findings.
- 38 guarded.
- 3 not applicable.

`instances` = 5.

## Barrier implication

The existing barrier has two gaps:

1. It prices **solve-path hub writes only**. It does not see the following
   three shapes:
   - a result adopted after an off-loop await without a re-check of loop-side
     writers (D1-s1-02)
   - an unconditional restore over a live object (`away.py`)
   - a module-global channel read by the thread fallback (D7-s3-54)
2. Its allow-table admits the field-by-field `_update_current_state` writes
   (D7-s1-51 and the two `_thermal_params` instances).

I propose a barrier that fails on families A, C and D the way
`arch_score_head.py` fails on B. It would be an allow-table of
`(file, symbol)` seams, using this enumerator's output as the census, in
`tests/`. Family A would also need a declared re-check per await. The cost is
one AST pass plus two archscore metrics, about 2 s of gate time measured
locally. This is a proposal, not a measured CI figure.
