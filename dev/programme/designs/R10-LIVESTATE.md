# R10-LIVESTATE design note (designer seat, `dev/governance/roles/designer.md`)

The group's architect note, extended; lives on `design/r10-livestate` only, never merged. Size XL; issues #2232, #2248. Read at `origin/main` fd7e289d0, whose `custom_components/` is identical to 27b59c9f7 (no predecessor handoff head: R10-SCORES #2647, R10-LOOP-CPU #2632 and R10-PUMP-MODEL #2368 are merged). Prototypes: ARCH-s1 at dbabc395f (`dev/audit/rounds/round10/D7/arch-s1/ALL_P1_P2_P3.patch`), ARCH2-s2 at fabaf4664 (`dev/audit/rounds/round10/D7/arch2-s2/UNION_P1_P7.patch`).

**Correction to the roster brief.** D1-s1-02 is not "the away override read torn mid-solve": `dev/audit/rounds/round10/D1/s1/REPORT.md` and `dev/audit/rounds/round10/JUDGE.md` state it as a mode write during the solve overwritten by the in-flight AUTO plan (`async_run_optimization` re-checks only `_entry_released` after `_await_optimize`). The away-override race the brief describes is the sweep's beyond-finding instance at `apply_override_payload` (`dev/audit/rounds/round10/sweep-N-shared-config.md`) and L3. Both are designed below.

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

**Publish primitive.** `CoordinatorContext` gains one method returning a copy of itself whose live state is a copy carrying the given fields. Every live-state write becomes a rebind of `_ctx` through it (or `replace(ctx, _current_state=state)` for a whole local copy). Its docstring changes from "write-once hubs" to "immutable; the coordinator publishes by rebinding". Entities S1 (`tests/entities.py`, "the four write-once hubs are not raw instance attributes") stays green: no store to the coordinator's `_current_state` property is added.

```
before: _update_current_state --field writes, 7 awaits--> ctx._current_state <--field writes-- ECL110 msg, _on_power_event
after:  _update_current_state: copy -> sensor fields on copy -> publish | await learners | copy(published) -> field -> publish (x3)
        ECL110 msg / _on_power_event: publish(published + reading)      readers holding a ctx or state keep their snapshot
```

- **P1 + P4 (`_current_state`).** The sensor block (every read before the first learner await, `_dhw_learner.async_learn_dynamics`) writes a private copy and publishes once before that await. The legionella hours, the ECL110 lag (`update_ecl110_displace_state`) and the slab seeds each copy the *currently published* state after the awaits. ThermalModel's `update_slab_from_return_temp` and `update_ecl110_displace_state` keep mutating, but only the caller's private copy. `_async_drive_pumps` reads the state after its own await. `_recovery_off_loop`'s captured state becomes a stable snapshot.
- **P2 (away state).** `async_set_away` computes the override on locals and publishes one `replace` of `_away_state`, persisting the published object. `_expire_away_override` publishes the lapsed override the same way and still ends `return active, ret`. `_resolve_away`'s guard becomes identity: publish only if `_away_state` is still the object read before the await. `apply_override_payload` returns a new `AwayState` instead of writing one.
- **L3 (restore race).** `restore_session` stops taking the spawn-time `AwayState`. The coordinator passes a bound adopt method (the way `_entity_state` is passed now); it publishes the restored override onto whatever `_away_state` is live at apply time, which closes interleaving C by construction. `restore_session` turns into a plain function: it registers a per-coordinator restore gate in boost's side table **synchronously at the spawn line**, then returns the coroutine that settles the gate in `finally`. `async_set_away`, `boost.set_channel` and `boost.set_block` await the gate (shielded) before their first write, which closes A and B. A cycle does not wait: if a restore lands inside `_resolve_away`'s await, the identity guard drops that cycle's resolve.
- **D1-s1-02 + ARCH2 P2 (running action).** A coordinator method builds the fixed-mode action whole, including `price` (ARCH2-s2 P2 at fabaf4664, keeping main's `space_reason`/`dhw_reason` per mode). `_async_update_data`'s three branches and the trailing write to `_current_action["price"]` collapse to one `boost.adopt_plan` of it, which ends the alias into `boost`'s plan base. `async_run_optimization` records the mode at entry. After `_await_optimize`, if the entry mode was AUTO or ECONOMY and the mode is now COMFORT, BOOST or OFF, it adopts the fixed-mode action and returns `None`, skipping the result's adoption and tail. That means no `_optimization_result`, no lead predictions filed after `async_set_mode` voided them, and no manual release. The `finally` re-run runs only while AUTO or ECONOMY holds. A run started in a fixed mode, and an AUTO-to-ECONOMY switch mid-solve, keep today's behaviour: no finding names them.
- **P6.** `price_tiles.py` holds the per-coordinator cursor beside the book and hands out the next spec, advancing *before* the await. `_price_tile_cursor` leaves the coordinator. **Behaviour change (carry 2):** a cancelled tile solve now skips its spec on that pass. The pull request states this and tests it.
- **P3.** `AccuracyTracker` gains a void method replacing the four `lead_pending.clear()` pairs in `async_set_mode` and `_file_lead_predictions`. `FlowBias.observe_temps` takes the heat output as a keyword, so `observe_water` writes no field. The solar forecast in `_fetch_weather_forecast` is one comprehension.
- **utc_shift.** It moves to `drift.py` beside `utc_step_starts`. Importers (`boost.py`, `manual_plan.py`, `pump_arbiter.py`, `services.py`, `coordinator.py`) import it from `.drift` with no re-export (decision 1).

**Invariants.** (I1) No await between reading the published state for a copy and publishing that copy. (I2) No in-place write to an object reachable as the published `_current_state` or `_away_state`. (I3) A write landing inside an await is never reverted by the awaiting publisher (`_resolve_away`, the restore, the post-await `_update_current_state` publishes). (I4) The adopted action's mode is the mode at adoption, unless the run began in a fixed mode. (I5) Every user writer of away or boost state runs after the session restore.

## Alternatives rejected

- **Live state as its own coordinator attribute.** Every `_current_state` read in `coordinator.py` moves, `_solve_hubs`' single-read consistent hub set splits, and entities S1 refuses a raw attribute.
- **Frozen `ThermalState`.** Every ThermalModel `update_*` mutator and every optimizer-side constructor changes, outside the owning seam.
- **ARCH2-s2 P4's coordinator helper.** `_on_power_event` is `grid` and the helper `core`, so a new cut against `seam_cut_total` at zero headroom, plus coordinator-class lines against `max_class_loc` at zero headroom. A `CoordinatorContext` method moves neither (`fixer.md`: class, not file).
- **Restore skips when the state was written since it began** (the probe's perturbation). The writer's whole-payload persist then drops stored fields it did not touch, `migrated_helpers` among them, so the helper migration re-runs.
- **Hold the away and boost stores and use `async_wait_for_read`.** Its future exists only once `async_load` starts, leaving a pre-start window. The finder's L3 harness also replaces `load_mapping` and both store constructors, so it could not confirm the fix.
- **D1-s1-02 by re-check plus a fresh refresh** (m4's perturbation). The AUTO action stays live until a refresh that upstream HA may drop under the debouncer lock (D1 REPORT). Adopting the fixed action closes it in the same cycle.
- **Cursor stays on the coordinator.** The class holds state it never computes with, and the book's owner is already `price_tiles.py`.
- **`utc_shift` stays in `accuracy.py`.** That leaves two UTC-walk owners of one rule; `accuracy.py` already re-exports drift's `utc_elapsed_seconds` for the same move.

## Sibling sites

1. `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-N-shared-config/shared_config_seams.py` reads seams_total 80 (A 3, B 41, C 17, D 19) at fd7e289d0. **In scope, 40:** A `async_run_optimization`; B the 25 `_current_state` rows (21 coordinator, 4 `thermal_model.py`); C 14 (`away.py` 3, `async_set_away` 6, `lead_pending` 2, solar append 1, `flow_meter.py` 1, `_current_action` price 1). The census misses `_expire_away_override` 2 and `lead_pending` 2 more, both in scope. **Out, 40:** B 16 `_thermal_params`/`_opt_config` writes (decision 3); A 2 and C 3 guarded or not applicable per the sweep's dispositions; D 19 (D7-s3-54 is R10-PUMP-MODEL's, done; the rest guarded). Expected at head: A 2, B 16, C 3.
2. Held context read after an await (I1's reader side), an AST pass over the package. It reads 9 at fd7e289d0: `_async_drive_pumps` 1 and `_update_current_state` 8, all in scope. Expected 0. The fixer commits it as a harness (`fixer.md` step 18):
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
3. N-restore-race: `git grep -nE "await (load_mapping\(|[a-z_.]*store[a-z_.]*\.async_load\()" -- custom_components` prints 17 lines. In scope: `away.py` and `boost.py`, through `restore_session`. Out: 15, held stores with D1-s2-52's save gate (no finding names an in-memory writer race there) and `store.py`'s own `load_mapping`. Carry: dismissed: class not swept, no finding names them (item ls-r1)

## Evidence plan (`fixer.md` steps 2-4)

- **Failing first, `tests/features.py`:**
  - a COMFORT, BOOST or OFF write inside the solve await gives a published mode equal to the action's mode and files no lead prediction;
  - an ECL110 message and a peak-guard flip landing during `_update_current_state`'s learner awaits survive its post-await publishes (red if a publish reuses the pre-await copy);
  - an object held before an event keeps its values;
  - the dict `boost.adopt_plan` receives in a fixed mode already carries `price`;
  - an away-off and a boost cancel during the restore load, and a `_resolve_away` replacement during it, each end as the serial order does;
  - a `CancelledError` from the tile solve advances the cursor.
- **Finder harnesses at both ends.** m4 reads 0 with its null 0. l3 reads 0 of 3; it drives `restore_session`'s signature, so its port keeps the gate on `load_mapping` and the serial null. The probe reads 0. `event_hub_writes.py` reads 0 at head (precondition from #2311's review), and its planted write reads 1. `tools/audit/archscore/score.py --diff` before and after.
- **Controls that must stay green:**
  - the carried `features.py` D14-s1-01 check (red with the guard as `if True:`);
  - the `_expire_away_override` keystone on `return active, ret`;
  - "an unexpired away override is not re-persisted each cycle";
  - entities S1;
  - `_ACTION_PRODUCERS` in `tests/entities.py` gains the fixed-mode builder.
- **Goldens.** `tests/golden.py` at the merge base. The prototype union read no unclaimed drift; touch no claim file unless drift appears (`claim-files.md`).
- **Mutation targets:**
  - the post-await mode guard and the re-run guard in `async_run_optimization`;
  - the identity guard in `_resolve_away`;
  - the gate awaits in `async_set_away`, `set_channel` and `set_block`;
  - the gate's `finally`;
  - the cursor advance;
  - the context publish method.
  The ledger re-keys `_resolve_away.GUARD_OFF`, both `_expire_away_override` entries and `_recovery_off_loop` (carry 5).
- **Budgets.**
  - `tests/ci_budgets.json` `archscore.hub_solve_writes` is re-recorded to the head measure (P4 share 3, P1 share 22: expect 16, re-measure). `shared_inplace_writes` likewise, with the reason in the commit.
  - Drop from `tests/arch_score_head.py`'s `CYCLE_HUB_WRITERS`: the three event rows, the `_current_state` set of `_update_current_state`, and both ThermalModel rows.
  - `max_class_loc`, `seam_cut_total` and `max_cc` sit at zero headroom (`python3 tests/structure.py`). The prototypes paid −24 class lines; the adopt method and the mode guard are paid from that.
- **Owed.** The quiet-window stress re-take (`tests/stress.py`, carry 5).

## Hot files, serial position, carries

`coordinator.py` is the hot file. Before: R10-SCORES, R10-LOOP-CPU, R10-PUMP-MODEL, all merged (re-read #2632's `_resolve_away` before dispatch). After: R10-PARAMS-OWNER, R10-ARCH-SHAPES, R10-ARCH-DOCS. Beyond roster `files`: `price_tiles.py`, `drift.py`, `manual_plan.py`, `pump_arbiter.py` (R10-ARCH-SHAPES, after us), `services.py` (R10-PARAMS-OWNER, after us), and import lines only (decision 1). Received carries 1-12 are honoured above: P1 with P2; P6 skip; P3 here; goldens; ledger and stress; hub_solve_writes; harness precondition; utc_shift; no `_price_tiles` on the coordinator; design gate; `_resolve_away` guard; the expiry controls.

### Notes for the fixer

- I1 is the trap: the post-await publishes must copy the published state, not the pre-await local, or an ECL110 message landing in a learner await is reverted. Carry: R10-LIVESTATE (item ls-01)
- Context holders now see snapshots; the ARCH-s1 replay harness held one at set-up (`tests/boost_drift_replay.py` re-reads it). Carry: R10-LIVESTATE (item ls-02)
- After this group `FlowBias` sets its heat output through `observe_temps`' keyword; `read_heat_output_kw`'s caller changes. Carry: R10-HEAT-METER (item ls-03)
- Rebinding `_ctx` is the live-state publish; L4's "make the context write-once" must mean the instance, not the binding. `_update_current_state`'s `mixing_valve_target` and `ambient_humidity` writes stay for the parameter owner. Carry: R10-PARAMS-OWNER (item ls-04)

**Decisions.** (1) orchestrator: widen `files` with `price_tiles.py` and the `utc_shift` import lines, or rule that `utc_shift` stays and why. (2) orchestrator: correct the brief's D1-s1-02 sentence (above). (3) orchestrator: write ls-03 and ls-04 into those groups' roster briefs; a designer edits no roster.
