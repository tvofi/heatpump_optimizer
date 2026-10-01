<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi** · [project thread](https://claude.ai/code/project/chan_01EL5jLi4rokGBbkaevYXSJV?thread=cmsg_01EL5jLi4rokGBbkaevYXSJV5v29UEnNacN91FYh9YD8FQ)_

R9-F1.11 (plan `handoff/round9/fix/F1.md` section F1.11). Fixes #1651 (P6); Fixes #1644 (P2). Part of #201.

Before: two round-9 bug classes had no barrier, so each instance was found by an audit seat after it shipped. The plan sensors read `horizon_hours` from `coordinator.data`, which nothing wrote, so every plan claimed 24 h whatever horizon it was solved over (D14-s1-02). `boost.set_channel` probed `boost_calls`, an attribute only a test double defines, and skipped the real persist when the double had it.

After: the gate refuses both classes. `tests/entities.py` gains two class-named blocks in sorted position:

- **P2: one fact, one owner.** A registry of eight facts (`two_zone_enabled`, `wood_furnace_on`, `dhw_enabled`, `state_age`, `on_threshold_kw`, `entity_write_domain`, `fenced_cycle_step`, `plan_running_rule`). Each entry names an AST shape, the owner function(s) and reasoned dispositions; any other site that decides the fact fails as a SEAM, and OWNER-MISSING, DEAD-RULE and STALE-DISPOSITION refuse a green reached by skipping. The two facts with no syntactic shape rest on censuses in `tests/features.py`, and a CENSUS-MISSING check refuses their removal. This is the RCA prototype's owners lint (`handoff/r9-rca-p2@3938c8ea`) converted into the block; the prototype file stays out of the tree.
- **P6: every read has a producer.** The RCA prototype's seven arms (payload keys K, built entity ids B, getattr probes G, flow error codes E, offered modes P, pre-fill preview fields F, solve seeds S), cherry-picked from 95535695 and aa2026b7. Each arm takes its universe from production, asserts it is non-empty, and has a planted-defect null control. Arm S cites tvofi's A3(e) ruling beside the room, upper and lower declarations.

Production changes, all the D14-s1-02 finding and the running-rule route:

- `coordinator.py`: the payload publishes the optimizer's own `horizon_hours`, through a new module-level `_plan_settings_view(opt)` that also carries the comfort schedule `_thermal_view` already published. Moving it out of the class pays for the key (the structure ratchet improves; see Figures).
- `boost.py`: `set_channel` always persists; the `boost_calls` probe is gone. The three boost-switch checks patch `boost.persist` with a recorder inside `tests/entities.py`, so `tests/harness.py` is untouched and `FakeCoordinator.boost_calls` stays for `async_set_boost`.
- `coordinator.py`: the schedule's `heat_pump_on` fallback was the last copy of the plan's running rule (`p > 0.1`, space only). It now calls `thermal_model.planned_draw_runs(space, dhw)`, the owner. The fallback applies only when a result carries no `heat_pump_on_schedule`. `_observe_compressor_start`'s docstring now says its threshold is `on_threshold_kw`, a different fact on purpose.

Census changes in `tests/features.py`:

- #1526 (P2 RCA state d, the D12-s2-02 escape): the census no longer skips a slot because it accepts `sensor`. Every sensor-accepting slot is a driven writer or a reasoned read-only entry (15 measurement slots and 7 flag slots, each with a reason). The heat-pump mode slot gets a driver through `pump_arbiter.apply`, a command routed to a read domain fails, and the service table gains `select` and `input_select` (the domains the mode slot accepts). The null control adds a sensor-accepting slot and asserts it is reported unclassified.
- #1747: the census now requires the co-optimisation replan's DHW build among the blocked builds (`>= 2`). The RCA's reach script shows the old check passing with the replan's build removed.

Golden captures: the five `coord_*` fixtures gain `data.horizon_hours` (24.0) and nothing else. `golden.py --record --only coord_` was cut back to that one line per file, because the recorder's other churn on this box (the battery view and its floats) belongs to the environment, not the branch. All five are claimed in `tests/golden/claimed_drift.txt`.

`tools/audit/bugclasses.json`: P2 and P6 carry detector and barrier text and `status: "barriered"`; #1747 is added as a P2 non-round instance.

The six-code flow-error check that arm E subsumes is kept: deleting it was optional, and it names the codes a reader looks for.

## Head

dfab4c6e (the merge of main d536fb4d, v6.7.13, into code head 965860aa; `claims-for` re-keyed to 6.7.13 by the claimnotes driver, the five claim lines kept)

## Mutation proof

Each mutant is one replace in a detached worktree, followed by `PYTHONPATH=tests/hastub python3 tests/entities.py`. The failing check names below are copied from the output.

- M1 `set_channel` probes `boost_calls` again (at 548b7b48): rc 1, 4 failing
  - `every getattr/hasattr probe names what production or upstream defines (P6 G)` [test-double-only: boost.py:244 boost_calls]
  - `turning DHW boost on holds and persists the DHW channel`
  - `turning space boost on holds and persists the space channel`
  - `turning DHW boost off releases and persists the DHW channel`
- M2b `horizon_hours` dropped from `_plan_settings_view` (at 8bae4c4b): rc 1, 2 failing
  - `the payload carries the optimizer's own horizon, so the plan sensors publish 12 h for a 12 h plan rather than a constant 24 (D14-s1-02)`
  - `every coordinator.data key a platform reads is one production writes (P6 K)` [sensor.py:1531 and 1564 horizon_hours]
- M3 the open-loop DHW seed dropped (at 548b7b48): rc 1, 1 failing
  - `no solve seed stays at its constructor default unless declared, and no declaration is stale (P6 S)` [undeclared dhw_temperature]
- M4 the `heat_pump_on` fallback back to `p > 0.1` (at 8bae4c4b): rc 1, 2 failing
  - `P2 owners: plan_running_rule is decided only by its owner or a dispositioned site, its owner exists, no disposition is stale, the rule is live` [SEAM coordinator.py in _apply_result_payload]
  - `and each P2 fact fails on a new sibling outside its owner, and each refusal fires on its planted skip (null controls)`
- M5 the round-9 E, P and F catalogue instances re-introduced by removing three `strings.json` entries (at 8bae4c4b): rc 1, 5 failing
  - `every error code a flow can return is in that flow's error table, in every catalogue (P6 E)` [config.error.prefill_device_unreadable]
  - `every non-standard mode an entity offers is translated and iconed (P6 P)` [the climate preset_mode state auto]
  - `every field the pre-fill preview can render has a label and a description, in both flows and every catalogue (P6 F)` [config.step.device_prefill.data.dhw_legionella_temperature]
  - `en.json matches strings.json exactly` and `sv.json matches strings.json exactly` (the existing catalogue checks)

New mutation sites in `coordinator.py` and `boost.py` are left to `mutation-autofix`, which pins killed unpinned mutants on CI. No local `--pin-killed` was run.

## Null control

- **Unmodified tree (merge-base e1ded322) plus the P6 block alone**: 3 of 2037 checks fail, all real instances. K fails on `sensor.py:1531` and `1564` `horizon_hours`, G on `boost.py:244 boost_calls`, and S on `dhw_temperature`.
- **Failing-first commit 2b2fe58c (tests, no fix)**: 7 of 2038 checks fail: the horizon check, K, G, S and the three boost checks.
- **Fix commit**: all 2038 pass.
- **P2 block against the round-9 baseline 1936d5ca** (the tree before any P2 instance PR; only the census file taken from the head): every fact fails on its round-9 instances:
  - `two_zone_enabled`: config_flow `_derive_preset`, modbus_prefill `_plant`
  - `wood_furnace_on`: topology `_wood_tank_shown`
  - `state_age`: inputs `age_of`, `_age_minutes` and `_age_gate`; OWNER-MISSING `inputs.py::state_stamp`
  - `on_threshold_kw`: the coordinator, optimizer and pump_arbiter copies; OWNER-MISSING `thermal_model.py::on_threshold_kw`
  - `entity_write_domain`: `pump_arbiter.py:457 _write`
  - `fenced_cycle_step`: the unfenced cycle steps; OWNER-MISSING `_best_effort_cycle_step`
  - `plan_running_rule`: coordinator `_apply_result_payload`, pump_arbiter `step_duty` and sensor `DHWScheduleSensor`; OWNER-MISSING for both thermal_model owners
  - `dhw_enabled`: STALE-DISPOSITION only, because F1.2's two dispositioned sites did not exist yet
  - the null-control check: red because its owners are missing
- **P2 block at the head**: 0 failing, 3.87 s standalone.
- **#1747 census reach**, using the RCA's `rca_census_reach.py` from `handoff/rca-1747@43ac2705` at the head:
  - as-is: the blocked builds are [True, True] and the census passes
  - the replan removed: [True], and the census fails
  - the off-spy variant: [True], 9.22 kWh shipped, breach 0.629, and the census fails
- **D14-s1-02 seam rule** (`tools/audit/round9/D14/s1/p6_keys.py`):
  - merge-base: `p6_unproduced_reads=2`, `p6_undefined_getattr=1`; SEAM C `boost.py:244 boost_calls`
  - head: both 0; no SEAM A-unproduced, B or C line
  - `distinct_reads=419` and `entity_ids_built=75` are unchanged. The nine A-conditional seams are unchanged; they are conditional producers, not this finding.

## Figures

- `ALL 2038 ENTITY CHECKS PASSED` at the fix commit, and `2048` checks at the head: `PYTHONPATH=tests/hastub python3 tests/entities.py`
- coordinator_loc 9014 to 9006, cut_views 109 to 104, max_class_loc 9014 to 9006, recorded in 8bae4c4b with the reason in its message: `python3 tests/structure.py`
- `p6_unproduced_reads` 2 to 0, `p6_undefined_getattr` 1 to 0: `PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/s1/p6_keys.py`
- Scoped gate at dfab4c6e `MODE: SCOPED -- 17 script(s) run, 11 scoped out`, `19 TEST SCRIPT(S) PASSED; 10 SCOPED OUT AND NOT RUN`, env_drift claiming the five coord captures: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh`
- typing ruler `ALL 9 typing-ruler checks PASSED`, errors and type_ignores did not grow: `$HPO_TYPING_PYTHON tests/typing_ruler.py --mypy`
- `mypy --strict` clean on `coordinator.py` and `boost.py`, at the head and at the merge-base: `$HPO_TYPING_PYTHON -m mypy --strict --follow-imports=silent custom_components/heatpump_optimizer/coordinator.py`
- real Home Assistant 2026.9.3 `ALL 61 contracts PASSED`: `/opt/hpo/venv-ha/bin/python tests/ha_contract.py --contracts-only`

## Red checks

none

## Forward-carry

The P2 RCA asked whether stored-string `fromisoformat` parses need a P2 entry owned by F3.1's stored-instant rule. Measured at the head: about 16 parse sites sit outside `drift.stored_instant`, under at least three different rules for a naive string:

- UTC: coordinator 629
- the current zone: coordinator 812 and 8821
- left naive: coordinator 3395 and 3404, accuracy 429, manual_plan 250 and 260

No registry entry is added here. Routing those sites means editing other lanes' files, and an entry without the routing would only fail the gate. This changes how whichever stage owns the stored-instant rule must work, so it goes to the orchestrator to place in that stage's brief, per `finding-propagation.md`. This seat cannot write the roster.

## Friction

none
