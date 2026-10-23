# R10-LIVESTATE design note (designer seat, `dev/governance/roles/designer.md`)

The group's architect note, extended; lives on `design/r10-livestate` only, never merged. Size XL; issues #2232, #2248. Read at `origin/main` fd7e289d0, whose `custom_components/` is identical to 27b59c9f7 (no predecessor handoff head: R10-SCORES #2647, R10-LOOP-CPU #2632 and R10-PUMP-MODEL #2368 are merged). Revision 1 answers design review `design-verdict/r10-livestate` 5af5526b5 (revise 78228a5d0). Its measurements come from a spike: fd7e289d0 plus this shape (P1, P2, P3 from dbabc395f re-applied, then the publish method, P4, P6, the D1 guard, both restore gates and the `utc_shift` move by hand), in a standalone clone, never pushed. Prototypes: ARCH-s1 at dbabc395f (`dev/audit/rounds/round10/D7/arch-s1/ALL_P1_P2_P3.patch`), ARCH2-s2 at fabaf4664 (`dev/audit/rounds/round10/D7/arch2-s2/UNION_P1_P7.patch`).

**Correction to the roster brief.** D1-s1-02 is not "the away override read torn mid-solve": `dev/audit/rounds/round10/D1/s1/REPORT.md` and `dev/audit/rounds/round10/JUDGE.md` state it as a mode write during the solve overwritten by the in-flight AUTO plan (`async_run_optimization` re-checks only `_entry_released` after `_await_optimize`). The away-override race the brief describes is the sweep's beyond-finding instance at `apply_override_payload` (`dev/audit/rounds/round10/sweep-N-shared-config.md`) and L3. Both are designed below.

Length: designer.md's two-page cap is waived for this XL note by the orchestrator (round 2), because its length is measurement and enumeration.

## Reproduced at fd7e289d0 (seat venv, finder harnesses unmodified)

| harness | baseline | finder perturbation |
|---|---|---|
| `dev/audit/rounds/round10/D1/s1/m4_mode_midsolve.py` | torn mid-solve 1 of 2 cells (comfort), null 0 | `--perturb` 0 |
| `dev/audit/rounds/round10/catchup/leads/l3_restore_race.py` | 3 of 3 interleavings differ, null 0 of 3 | 0 of 3 |
| `dev/audit/rounds/round10/D14/sweep-N-shared-config/probe_away_restore.py` | lost mid-load 1, null 0 | `--perturb` 0 |
| `dev/audit/rounds/round10/D7/arch2-s2/event_hub_writes.py` (at fabaf4664) | 3 event in-place hub writes | P4 patch reads 0 |

## Owning seam

One concern per owner; no concern needs two. **Live-state publication** is owned by `HeatPumpOptimizerCoordinator`'s `core` seam (`tests/seam_map.json`: `_update_current_state`, `_async_handle_ecl110_state_message`, `_resolve_away`, `_expire_away_override`, `async_set_away`, `async_run_optimization`, `_async_update_data`, `_async_drive_pumps`) together with `CoordinatorContext`, the immutable carrier the coordinator rebinds to publish. `_on_power_event` (seam `grid`) and `_maybe_refresh_price_tile` (seam `fetch`) only call owners. **Tile rotation**: `custom_components/heatpump_optimizer/price_tiles.py`, which already owns the book in a per-coordinator side table. **UTC walk**: `custom_components/heatpump_optimizer/drift.py` (`utc_step_starts`). **Session restore**: `custom_components/heatpump_optimizer/boost.py`'s `restore_session`, with `custom_components/heatpump_optimizer/away.py` pure. Collaborator fields: `AccuracyTracker`, `FlowBias`.

## Shape

**Publish primitive, signature pinned.** `CoordinatorContext` gains one method that **takes the coordinator and performs the rebind itself**; every live-state write goes through it, whole local copies included:
```
def publish(self, coord: Any, state: ThermalState | None = None, /, **fields: Any) -> None:
    new = replace(self._current_state if state is None else state, **fields)
    coord._ctx = replace(self, _current_state=new)
```
A caller that publishes twice re-reads the context between the calls (`_ctx_of(self)`), never the `ctx` it published from. A copy-returning method with a coordinator-side `self._ctx =` store costs `seam_cut_total` +2 from the `grid`-seam `_on_power_event` (review evidence, 715 -> 717); this signature reads 715 there, and the whole spike reads 711. Its docstring changes from "write-once hubs" to "immutable; the coordinator publishes by rebinding". Entities S1 (`tests/entities.py`, "the four write-once hubs are not raw instance attributes") stays green: no store to the coordinator's `_current_state` property is added.

```
before: _update_current_state --field writes, 7 awaits--> ctx._current_state <--field writes-- ECL110 msg, _on_power_event
after:  _update_current_state: copy -> sensor fields on copy -> publish | await learners | copy(published) -> field -> publish (x3)
        ECL110 msg / _on_power_event: publish(published + reading)      readers holding a ctx or state keep their snapshot
```

- **P1 + P4 (`_current_state`).** The sensor block (every read before the first learner await, `_dhw_learner.async_learn_dynamics`) writes a private copy and publishes once before that await. The legionella hours, the ECL110 lag (`update_ecl110_displace_state`) and the slab seeds each copy the *currently published* state after the awaits. ThermalModel's `update_slab_from_return_temp` and `update_ecl110_displace_state` keep mutating, but only the caller's private copy. `_async_drive_pumps` reads the state after its own await. `_recovery_off_loop`'s captured state becomes a stable snapshot.
- **P2 (away state).** `async_set_away` computes the override on locals and publishes one `replace` of `_away_state`, persisting the published object. `_expire_away_override` publishes the lapsed override the same way and still ends `return active, ret`. `_resolve_away`'s guard becomes identity: publish only if `_away_state` is still the object read before the await. `apply_override_payload` returns a new `AwayState` instead of writing one.
- **L3 and the manual plan (restore race).** `restore_session` stops taking the spawn-time `AwayState`. The coordinator passes a bound adopt method (the way `_entity_state` is passed now); it publishes the restored override onto whatever `_away_state` is live at apply time, which closes interleaving C by construction. `restore_session` turns into a plain function: it registers a per-coordinator restore gate in boost's side table **synchronously at the spawn line**, then returns the coroutine that settles the gate in `finally`. `async_set_away`, `boost.set_channel` and `boost.set_block` await the gate (shielded) before their first write, which closes A and B. A cycle does not wait: if a restore lands inside `_resolve_away`'s await, the identity guard drops that cycle's resolve. **`_async_load_manual_plan`** (review point 1): its store is held, so `async_apply_manual_plan` and `async_clear_manual_plan` await `_manual_plan_store.async_wait_for_read()` before writing `_manual_override`, the R6 shape `async_set_mode` already uses. The review's probe, ported (stub load registers its read; clear runs as a task), reads lost mid-load 1 (null 0) at fd7e289d0 and 0 (null 0) on the spike. Its residual, a write before the load task's first step, is unreachable: `__init__.py` spawns the loaders in the constructor, and services, entities and actions reach the coordinator only through `entry.runtime_data`, assigned after `async_config_entry_first_refresh` (`__init__.py:318`, `:325`). By then each loader has taken its first step, which sets the store's read future synchronously (`store.py:686` "create_future").
- **D1-s1-02 + ARCH2 P2 (running action).** A coordinator method builds the fixed-mode action whole, including `price` (ARCH2-s2 P2 at fabaf4664, keeping main's `space_reason`/`dhw_reason` per mode). `_async_update_data`'s three branches and the trailing write to `_current_action["price"]` collapse to one `boost.adopt_plan` of it, which ends the alias into `boost`'s plan base. `async_run_optimization` records the mode at entry. After `_await_optimize`, one call to a module-level predicate (entry mode an optimizer mode and current mode not) decides it: if true, it adopts the fixed-mode action and returns `None`, skipping the result's adoption and tail. That means no `_optimization_result`, no lead predictions filed after `async_set_mode` voided them, and no manual release. The `finally` re-run is **not** guarded there: `async_set_mode` clears `_optimization_rerun_requested` inside its existing leaving-the-optimizer branch, so the re-run guard gains no decision point. A run started in a fixed mode, and an AUTO-to-ECONOMY switch mid-solve, keep today's behaviour: no finding names them.
- **P6.** `price_tiles.py` holds the per-coordinator cursor beside the book and hands out the next spec, advancing *before* the await. `_price_tile_cursor` leaves the coordinator. **Behaviour change (carry 2):** a cancelled tile solve now skips its spec on that pass. The pull request states this and tests it.
- **P3.** `AccuracyTracker` gains a void method replacing the four `lead_pending.clear()` pairs in `async_set_mode` and `_file_lead_predictions`. `FlowBias.observe_temps` takes the heat output as a keyword, so `observe_water` writes no field. The solar forecast in `_fetch_weather_forecast` is one comprehension.
- **utc_shift.** It moves to `drift.py` beside `utc_step_starts`. Importers (`boost.py`, `manual_plan.py`, `pump_arbiter.py`, `services.py`, `coordinator.py`, and `tests/dst_checks.py`) import it from `.drift` with no re-export.

**Invariants.** (I1) No await between reading the published state for a copy and publishing that copy. (I2) No in-place write to an object reachable as the published `_current_state` or `_away_state`. (I3) A write landing inside an await is never reverted by the awaiting publisher (`_resolve_away`, the restore, the post-await `_update_current_state` publishes). (I4) The adopted action's mode is the mode at adoption, unless the run began in a fixed mode. (I5) Every user writer of away, boost or manual-plan state runs after its restore.

## Alternatives rejected

- **Live state as its own coordinator attribute.** Every `_current_state` read in `coordinator.py` moves, `_solve_hubs`' single-read consistent hub set splits, and entities S1 refuses a raw attribute.
- **Frozen `ThermalState`.** Every ThermalModel `update_*` mutator and every optimizer-side constructor changes, outside the owning seam.
- **ARCH2-s2 P4's coordinator helper.** `_on_power_event` is `grid` and the helper `core`, so a new cut against `seam_cut_total` at zero headroom, plus coordinator-class lines against `max_class_loc` at zero headroom. A `CoordinatorContext` method moves neither (`fixer.md`: class, not file).
- **Restore skips when the state was written since it began** (the probe's perturbation). The writer's whole-payload persist then drops stored fields it did not touch, `migrated_helpers` among them, so the helper migration re-runs.
- **Hold the away and boost stores and use `async_wait_for_read`** (taken for the manual plan, whose store is already held). For away and boost it needs two new held stores, and their future exists only once `async_load` starts, leaving a pre-start window that the spawn-line gate does not have.
- **Both mode guards inline as worded in revision 0.** `async_run_optimization` cc 13 -> 16, so `functions_cc_over_15` 30 -> 31 over its cap (review measurement); the predicate plus the `async_set_mode` clear gives 14.
- **D1-s1-02 by re-check plus a fresh refresh** (m4's perturbation). The AUTO action stays live until a refresh that upstream HA may drop under the debouncer lock (D1 REPORT). Adopting the fixed action closes it in the same cycle.
- **Cursor stays on the coordinator.** The class holds state it never computes with, and the book's owner is already `price_tiles.py`.
- **`utc_shift` stays in `accuracy.py`.** That leaves two UTC-walk owners of one rule; `accuracy.py` already re-exports drift's `utc_elapsed_seconds` for the same move.

## Sibling sites

1. `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-N-shared-config/shared_config_seams.py` reads seams_total 80 (A 3, B 41, C 17, D 19) at fd7e289d0. **In scope, 40:** A `async_run_optimization`; B the 25 `_current_state` rows (21 coordinator, 4 `thermal_model.py`); C 14 (`away.py` 3, `async_set_away` 6, `lead_pending` 2, solar append 1, `flow_meter.py` 1, `_current_action` price 1). The census misses `_expire_away_override` 2 and `lead_pending` 2 more, both in scope. **Out, 40:** B 16 `_thermal_params`/`_opt_config` writes (R10-PARAMS-OWNER, ls-04); A 2 and C 3 guarded or not applicable per the sweep's dispositions; D 19 (D7-s3-54 is R10-PUMP-MODEL's, done; the rest guarded). On the spike: A 3, B 16, C 3, D 21. A keeps `async_run_optimization` (the census is syntactic and does not see the re-check); D gains the two side tables (the restore gate in `boost.py`, the cursor in `price_tiles.py`).
2. Held context read after an await (I1's reader side), an AST pass over the package. It reads 9 at fd7e289d0: `_async_drive_pumps` 1 and `_update_current_state` 8, all in scope. The spike reads 0. The fixer commits it as a harness (`fixer.md` step 18):
```
python3 - <<'E'
import ast, pathlib
n = 0
for f in sorted(pathlib.Path("custom_components/heatpump_optimizer").glob("*.py")):
    for fn in ast.walk(ast.parse(f.read_text())):
        if not isinstance(fn, ast.AsyncFunctionDef): continue
        b = {a.targets[0].id: a.lineno for a in ast.walk(fn) if isinstance(a, ast.Assign)
             and isinstance(a.targets[0], ast.Name) and "_ctx" in ast.unparse(a.value)}
        w = [a.end_lineno for a in ast.walk(fn) if isinstance(a, ast.Await)]
        for r in ast.walk(fn):
            if (isinstance(r, ast.Attribute) and r.attr == "_current_state" and isinstance(r.value, ast.Name)
                    and r.value.id in b and any(b[r.value.id] < x < r.lineno for x in w)):
                n += 1; print(f"{f.name}:{r.lineno} {fn.name}")
print(f"RESULT held-ctx-reads-after-await={n}")
E
```
3. N-restore-race: `git grep -nE "await (load_mapping\(|[a-z_.]*store[a-z_.]*\.async_load\()" -- custom_components` prints 17 lines. The criterion: can a writer of the attribute the load assigns run inside the load's await without waiting for it?
   - **In scope, 3:** `away.py` and `boost.py` through `restore_session` (user writers `async_set_away`, `set_channel`, `set_block`), and `_async_load_manual_plan` (user writers `async_apply_manual_plan`, `async_clear_manual_plan`).
   - **No, 4:** `store.py`'s own `load_mapping`; `_stored_fuse_advisor` assigns nothing; `_async_load_snapshots` (its writer checks `_snapshots_loaded`); `_async_load_accuracy`'s `_mode` (`async_set_mode` awaits the read, R6).
   - **No, 3 more (writer registered after the load, or under its lock):** `notifier.py` `async_setup_notifier` awaits the load (`notifier.py:322`) before it registers `handle` as a listener; `debugger.py` `async_setup_debugger` awaits it (`debugger.py:662`) before the collector and its listener exist; `pump_arbiter.py` `_load` runs under `held.lock` inside `apply`, and every writer of `held.written` (`hold`, `_write`, `_write_night_schedule`, `_forget`) is reached only from `_arbitrate` under that lock. The one path outside it, `release` at unload, writes only when `held.written` is non-empty, which nothing makes it before the load lands. Established by reading.
   - **User-command writers, 4 loads, routed to R10-PARAMS-OWNER** (the learned-parameter owner; its D7-s1-82 is the `set_thermal_parameters` service). Established by reading, not by a probe:
     - `async_update_thermal_params` resets the house-heat-loss scale and samples and the buffer cooling rate and samples (`coordinator.py:6138-6143`) before any await, against `_async_load_thermal_learning`; only its save waits for the read (`coordinator.py:4178` "async_wait_for_read").
     - `dhw_learning.py` `async_set_cooling_rate` writes the cooling rate and `cooling_samples` (`dhw_learning.py:230-231`) before its save, against `async_load_profile`.
     - `async_restore_learned_snapshot`, the `restore_snapshot` service, runs `_apply_learner_payloads` with no await, writing thermal learning, the DHW profile, the DHW draws (`apply_draws`) and the price model (`adopt_model`), against those four loads.
     Carry: R10-PARAMS-OWNER (item ls-r1)
   - **Per-cycle writers in the first refresh, unprobed leads, 7 loads:** `_async_load_thermal_learning` (`_async_learn_buffer_cooling`, `coordinator.py:6481`), `async_load_profile` (`async_learn_dynamics`, `coordinator.py:6459`), `legionella.py` `async_load` (`async_track_cycle`, `coordinator.py:6471`), `_async_load_price_model` (`_async_learn_price_shape`), `_async_load_energy_totals` (`coordinator.py:10216` "space_energy_kwh"), `_async_load_ledger` (`coordinator.py:10227` "self._ledger.add"), `_async_load_accuracy`'s trackers (`coordinator.py:9952` "self._accuracy.record"). The loads are spawned in the constructor and the first refresh runs while they are in flight (`__init__.py:302` "HeatPumpOptimizerCoordinator", `:318`); whether each writer runs in that refresh is not established. The loss would be one cycle's increments. The fixer's pull request files one issue naming these as unprobed leads, not findings, with the probe recipe of item ls-r1, and leaves #2248 open (`Part of`). Carry: #2248 (item ls-r2)

## Evidence plan (`fixer.md` steps 2-4)

- **Failing first, `tests/features.py`:**
  - a COMFORT, BOOST or OFF write inside the solve await gives a published mode equal to the action's mode and files no lead prediction;
  - an ECL110 message and a peak-guard flip landing during `_update_current_state`'s learner awaits survive its post-await publishes (red if a publish reuses the pre-await copy);
  - an object held before an event keeps its values;
  - the dict `boost.adopt_plan` receives in a fixed mode already carries `price`;
  - an away-off and a boost cancel during the restore load, and a `_resolve_away` replacement during it, each end as the serial order does;
  - a manual-plan clear and an apply during the manual-plan load each survive it;
  - a `CancelledError` from the tile solve advances the cursor.
- **Finder harnesses at both ends.** m4 reads 0 with its null 0. l3 reads 0 of 3; it drives `restore_session`'s signature, so its port keeps the gate on `load_mapping` and the serial null. The probe reads 0. The review's manual-plan probe (`design-verdict/r10-livestate` 5af5526b5, evidence directory) is committed as a harness: 1 at the merge base, 0 at head. `event_hub_writes.py` reads 0 at head (precondition from #2311's review), and its planted write reads 1. `tools/audit/archscore/score.py --diff` before and after.
- **Controls that must stay green:**
  - the carried `features.py` D14-s1-01 check (red with the guard as `if True:`);
  - the `_expire_away_override` keystone on `return active, ret`;
  - "an unexpired away override is not re-persisted each cycle";
  - entities S1;
  - `_ACTION_PRODUCERS` in `tests/entities.py` gains the fixed-mode builder.
- **Goldens.** `tests/golden.py` at the merge base. The prototype union read no unclaimed drift; touch no claim file unless drift appears (`claim-files.md`).
- **Mutation targets:**
  - the post-await predicate call in `async_run_optimization`, the predicate itself, and the `_optimization_rerun_requested` clear in `async_set_mode`;
  - the identity guard in `_resolve_away`;
  - the gate awaits in `async_set_away`, `set_channel` and `set_block`, and the two `async_wait_for_read` awaits in the manual-plan writers;
  - the gate's `finally`;
  - the cursor advance;
  - the context publish method.
  The ledger re-keys `_resolve_away.GUARD_OFF`, both `_expire_away_override` entries, `_recovery_off_loop`, and `tests/mutation_ledger/killed_by/accuracy.py/utc_shift.GUARD_OFF.69015aa6.json` and `tests/mutation_ledger/killed_by/accuracy.py/utc_shift.RETURN_DEL.ca5ce0e9.json`, which anchor on `accuracy.py:utc_shift` (carry 5).
- **Budgets.**
  - `tests/ci_budgets.json` `archscore.hub_solve_writes` is re-recorded to the head measure (P4 share 3, P1 share 22: expect 16, re-measure). `shared_inplace_writes` likewise, with the reason in the commit.
  - Drop from `tests/arch_score_head.py`'s `CYCLE_HUB_WRITERS`: the three event rows, the `_current_state` set of `_update_current_state`, and both ThermalModel rows.
  - Structure (review point 3). Every row of `python3 tests/structure.py` sits at its cap at fd7e289d0. On the spike the run exits 2 ("improved and not yet recorded"), with no row over its cap:
    - better: `max_class_loc` -26, `class_excess_loc` -20, `seam_cut_total` -4, `max_cc` -1 (`_update_current_state` cc 45 -> 44, 290 -> 279 lines: the `floor_temp` walrus guard goes and no decision point is added), `coordinator_attrs` -1 and `coordinator_multiassigned_attrs` -1 (`_price_tile_cursor` leaves);
    - flat: `functions_cc_over_15`, `functions_cc_over_25`, `methods_over_150`, `methods_over_200`, `max_method_loc`, `duplication_copies`, `dead_methods`, `dead_top_level_symbols`, `coordinator_private_reach`, `import_cycle_modules`, `const_modules_over_50`, `name_kept_members`;
    - the touched functions: `async_run_optimization` cc 13 -> 14 (the predicate is the payment against the review's 16); `_async_drive_pumps` 15 -> 15 (a fresh read, no branch); `_async_update_data` 10 -> 7; `async_set_away` 7 -> 8; `_async_handle_ecl110_state_message` 4 -> 5 (the comprehension filter); the new builder, adopt method and predicate each 2 or less.
    No raise is needed. Record the improved rows with the reason in the commit.
- **Owed.** The quiet-window stress re-take (`tests/stress.py`, carry 5).

## Hot files, serial position, carries

`coordinator.py` is the hot file. Before: R10-SCORES, R10-LOOP-CPU, R10-PUMP-MODEL, all merged (re-read #2632's `_resolve_away` before dispatch). After: R10-PARAMS-OWNER, R10-ARCH-SHAPES, R10-ARCH-DOCS. Roster `files` gains `price_tiles.py`, `drift.py`, `manual_plan.py`, `pump_arbiter.py` (R10-ARCH-SHAPES, after us), `services.py` (R10-PARAMS-OWNER, after us), `tests/dst_checks.py` (its `utc_shift` import from `accuracy`) and the two `utc_shift` ledger entries. The orchestrator accepted the widening; the roster seat writes it. Received carries 1-12 are honoured above: P1 with P2; P6 skip; P3 here; goldens; ledger and stress; hub_solve_writes; harness precondition; utc_shift; no `_price_tiles` on the coordinator; design gate; `_resolve_away` guard; the expiry controls.

### Notes for the fixer

- I1 is the trap: the post-await publishes must copy the published state, not the pre-await local, or an ECL110 message landing in a learner await is reverted. Carry: R10-LIVESTATE (item ls-01)
- Context holders now see snapshots; the ARCH-s1 replay harness held one at set-up (`tests/boost_drift_replay.py` re-reads it). Carry: R10-LIVESTATE (item ls-02)
- After this group `FlowBias` sets its heat output through `observe_temps`' keyword; `read_heat_output_kw`'s caller changes. Carry: R10-HEAT-METER (item ls-03)
- Rebinding `_ctx` is the live-state publish; L4's "make the context write-once" must mean the instance, not the binding. `_update_current_state`'s `mixing_valve_target` and `ambient_humidity` writes stay for the parameter owner. Carry: R10-PARAMS-OWNER (item ls-04)

- l3_restore_race.py and probe_away_restore.py drive `restore_session`'s and `restore_override`'s current signatures, and l3's C perturbation patches `apply_override_payload`'s in-place write; both need a port. Run each port at the merge base first: it must read l3 3 of 3 (null 0) and the probe 1 (null 0) there before its head reading counts. Carry: R10-LIVESTATE (item drev-01)
- The restore gate settles on every path, including a coroutine closed or cancelled before its first step (a `finally` in an unstarted coroutine never runs). Test: spawn after `_entry_released`; `async_set_away` then returns rather than waiting forever. Carry: R10-LIVESTATE (item drev-02)
- `update_ecl110_displace_state` recomputes `ecl110_effective_displace` as a lag from its current value every cycle with a `displace_value`. Word the ECL110 test as "the lag starts from the message's value", not "the field equals the message", or it is red at head too. Carry: R10-LIVESTATE (item drev-03)
- The restore gate and the cursor each add a census D row: expected at head is D 21 (spike reading), not unstated. Carry: R10-LIVESTATE (item drev-04)
- Identity replaces equality in `_resolve_away`'s guard: re-run the carried D14-s1-01 control and its `if True:` null against the identity form, not only its green arm. Carry: R10-LIVESTATE (item drev-05)

- `async_set_mode` clearing `_optimization_rerun_requested` also drops a re-run requested before an AUTO -> COMFORT -> AUTO round trip within one solve. Test that a mid-solve input change followed by such a round trip still re-runs, or state the loss in the PR. Carry: R10-LIVESTATE (item drev-06)
- `restore_session` now calls `asyncio.get_running_loop()` from the constructor's spawn line; a test or harness constructing the coordinator outside a running loop raises there. Keep construction inside the loop in the ported harnesses (drev-01). Carry: R10-LIVESTATE (item drev-07)
- Item ls-r1's probe, for R10-PARAMS-OWNER or this fixer: a stub store whose `async_load` waits on an `asyncio.Event` replaces the loader's store; spawn the load, yield once, run the user command as a task, set the event, await both. Metric: the commanded value (house-heat-loss samples 0; DHW `cooling_samples` 0; the snapshot's model) is lost after the load, 1 or 0. Null: the command after the load, 0. Fix shape: the writer awaits the store's `async_wait_for_read`, as the manual plan does here. Carry: R10-PARAMS-OWNER (item ls-r1-probe)

The decisions routed in revision 0 (the `files` widening, the D1-s1-02 brief correction, carries ls-03 and ls-04) are accepted by the orchestrator and are being written by the roster seat.
