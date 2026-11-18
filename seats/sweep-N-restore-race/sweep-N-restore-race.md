# Sweep: N-restore-race (round 11, D14 steps 3-4)

Class mechanism: a restore applies persisted state after an await during which a
writer changed the same state, so the stale snapshot overwrites the live write (or
the write lands on an object the restore then replaces). Finding: D1-s2-04
(off_restore._armed_record). Status in `dev/audit/config/bugclasses.json`: `open`,
no detector, no barrier; one earlier instance (R10 L3-restore-session-race, the
boost/away session restore, since gated by `boost.session_restored`).
Baseline: origin/handoff/audit-r11-register (28b864af6d).

## Enumerator

`python3 dev/audit/rounds/round11/D14/N-restore-race/restore_race.py [--clean] [--plant]`

AST over every module of `custom_components/heatpump_optimizer/`. A seam is an
async function that awaits a persisted-state read (`async_load`, `load_mapping`,
`async_get_last_state`, `async_get_last_extra_data`) and, after that await, writes
an attribute or subscript of `self`, a parameter, or a record fetched before the
read (or calls a mutator on one). This widens the finding's seam rule
(`grep '\.loaded = True'`, which matches only two flag-gated lazy loads) to every
restore that lands on shared state. Each seam is tagged `flag_before_await` (a
`*loaded* = True` written before the read: D1-s2-04's exact shape), `locked`
(the read is inside `async with <...lock...>`) and `lock_covered` (every call
site, transitively through module-resolved callers, is under such a lock). The
metric is `unlocked`: seams whose safety rests on something other than a lock and
so need a named guard.

| run | seams | unlocked | flag_before_await and unlocked |
|---|---|---|---|
| package (positive control) | 19 | 17 | 1 (off_restore._armed_record, the judged site) |
| `--clean` (null control: a fixture with a locked lazy load and a load into locals) | 1 | 0 | 0 |
| `--plant` (one line: `pump_arbiter.apply`'s `async with held.lock:` -> `if True:` on a copy) | 19 | 19 | 2 |

The positive control re-finds D1-s2-04 as the only unlocked flag-before-read seam,
and the finding's own harness reproduces on this box
(`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s2/off_restore_race.py`
gives consequences=2, `--serial` 0, `--fix` 0). The perturbation moves the metric
17 -> 19: pump_arbiter._load (whose flag is set before its read, safe only under the
lock) and duty_switch._load (reached only through `_arbitrate` under that lock)
both lose lock coverage. So the walk is not keyed on off_restore.

## Startup ordering the dispositions rely on

The coordinator's store loads are spawned in `HeatPumpOptimizerCoordinator.__init__`
(coordinator.py:3572-3586) and are not awaited. `async_setup_entry` then runs the first
refresh with `skip_first_solve=True` (`__init__.py:305`, 318): the light path
`_async_first_refresh_light` awaits `boost.session_restored` first (coordinator.py:6171), then
runs `_update_current_state`, the fetches and `_async_learn_price_shape`. It does not reach
`_record_accuracy`, `_accumulate_energy`, `_file_lead_predictions`, `_apply_action`,
`pump_arbiter.apply` or `boost.apply`. Services cannot reach the coordinator until
`entry.runtime_data` is set after the first refresh (`__init__.py:325`). The fence
`QuarantiningStore.async_wait_for_read` (store.py:841) awaits the in-flight read's future, which is
resolved in the read's `finally` before the loader resumes. So the loader's synchronous
assignment lands before any fenced writer resumes.

## Seams (19) and dispositions

| seam | disposition |
|---|---|
| off_restore.py:127 `_armed_record` | **instance**, the judged site (D1-s2-04): `loaded` is set before the read and there is no lock. Probe: `off_restore_race.py` gives consequences=2 |
| pump_arbiter.py:2205 `_load` | guarded: `ArbiterState.lock`. Both callers (`apply` :1859, `_lead_mode` :1917) hold `held.lock` around it. `--plant` shows the walk sees it once one lock goes |
| duty_switch.py:503 `_load` | guarded: lock-covered. Its only caller chain is `note_pass` <- `pump_arbiter._arbitrate` <- `apply` under `held.lock`, and `loaded` is set after the read |
| boost.py:579 `restore` | guarded: the session-restore gate `_RESTORES`/`session_restored` (the R10 L3 fix). `set_channel`, `set_block`, `_resolve_away` and `async_set_away` await it, and so does the light first refresh, which precedes every full cycle's `boost.apply`/`release_blocked`. `note_mode_change` comes from the `async_set_mode` service, which needs `runtime_data` (after the gate) |
| away.py:454 `restore_override` | not applicable: it writes a local `payload` from `empty_override()`, and the shared state is published through `adopt` inside the gated session task (same gate as above) |
| coordinator.py:4580 `_async_load_thermal_learning` | guarded (ordering): its writers (`_async_learn_interval` learners, `_learn_measured_cop`) fold a closed interval from a prior house sample. The light first refresh takes the first sample, and saves fence at :4776. The guard is ordering, not a lock |
| coordinator.py:8286 `_async_load_price_model` | guarded: fence `async_wait_for_read` at :8621 before `_price_learner.fold` in `_async_learn_price_shape`, the only cycle writer. `_apply_learner_payloads` is reached from services only, after publication |
| coordinator.py:8306 `_async_load_ledger` | guarded: start edges confirmed before the read are queued in the start counter and replayed by the loader after the ledger restore (`finally: self._book_starts(...)`, "part D"). The ledger writers `_accumulate_energy`/`_roll_month` run only from the second `_record_accuracy` (full cycles; `pending` is None on the first) |
| coordinator.py:8373 `_async_load_accuracy` | guarded (ordering): writers `_record_accuracy`/`_file_lead_predictions`/`_settle_defrost` run on full cycles only, after the light first refresh. `async_set_mode` fences at :6527 |
| coordinator.py:8410 `_async_load_energy_totals` | guarded: kWh keys merge as `max(live, stored)`, and the only writer `_accumulate_energy` runs from the second full cycle on |
| coordinator.py:8476 `_async_load_manual_plan` | guarded: `async_apply_manual_plan`/`async_clear_manual_plan` fence at :8580/:8606, and they are services (after publication) |
| coordinator.py:9765 `_async_load_snapshots` | guarded: the `_snapshots_loaded` gate in `_async_watch_learning_drift` (the flag is set in the same synchronous step as the ring), and `async_factory_reset` fences the snapshot store at :1508 |
| debugger.py:501 `DebugCollector.async_load` | guarded: load-then-publish. `async_setup_debugger` awaits the load before `_COLLECTORS[coordinator] = collector` and the listener (:696-698) |
| notifier.py:277 `Notifier.async_load` | guarded: load-then-publish. The update listener is added after the awaited load (notifier.py:331-339) |
| dhw_learning.py:253 `async_load_profile` | guarded (ordering): `async_learn_dynamics` takes its first sample as a baseline only (`previous_temp is None` returns) and refuses intervals under 0.02 h, so no learner write in the first ~72 s. `set_cooling_rate`'s callers fence via `async_wait_for_read` (ls-r1) |
| dhw_learning.py:376 `async_load_draws` | guarded (ordering): same first-sample baseline and 0.02 h floor before `async_fold_draw_stats` |
| legionella.py:210 `LegionellaGuard.async_load` | guarded: `async_track` fences `store.async_wait_for_read` (#2674) before crediting. `async_track_cycle` follows a plan-commanded cycle, which needs a solve (full cycles, after the light refresh) and runs after `async_track` in `async_observe` |
| frontend.py:111 `_register_lovelace_resource` | not applicable: Home Assistant's own Lovelace resource collection and its `loaded` flag, not this integration's persisted state |
| store.py:749 `QuarantiningStore.async_load` | not applicable: the store's own read bookkeeping (`_readers`, `bounded`); it provides the fence |

Instances beyond the finding: **0**. Six guards are ordering-only ("guarded (ordering)" above, plus
the ledger/energy second-cycle arms): nothing structural refuses a writer that runs before the read
lands. They hold today because the first refresh is light and the learners need a prior sample.

## Proposed barrier

A tests/ check built on this enumerator. It refuses any `*loaded* = True` written
before a store read unless the read is locked or lock-covered (D1-s2-04's shape:
today's count 1, which the fix takes to 0). It also holds the `unlocked` seams to a
reasoned list, each naming its guard (lock, `async_wait_for_read` fence,
`session_restored`, load-then-publish, `_snapshots_loaded`), so a new restore must name one.
Static and AST only, well under a gate second. Not built here. Barriered: no.
