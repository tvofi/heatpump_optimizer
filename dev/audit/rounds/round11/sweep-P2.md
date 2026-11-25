# Round 11, class P2 sweep (D14 method steps 3-4)

Seat: class-sweep P2, PLAN phase D, box SW8. Tree: `handoff/audit-r11-register` at `28b864af6d`.
Its package is the round's baseline `92d38ecb` plus 20 files (`git diff --stat 92d38ecb HEAD`).
Judge files from `5806e17d` (`dev/audit/rounds/round11/J/judge`).

Class P2 is one fact decided twice by divergent predicates: a guard at one seam, missing at its
sibling. Ledger status in `dev/audit/config/bugclasses.json` is `barriered`. The barrier is the P2
owners registry in `tests/entities.py`, which covers eight registered facts. Of the 18 facts below,
the registry covers only `two_zone_enabled`, and for that fact only the "raw proxy-key read" shape.
The other shapes and facts are outside the barrier's reach. That is why this round adds 23 judged
findings and 9 instances beyond them (see "Barrier").

Machine: Linux x86-64 cloud box, venv-ci python 3.14, `OPENBLAS_CORETYPE=Haswell`. Every enumerator
count is a static AST count. Every probe is deterministic and rests on frozen clocks. Load does not
move any number.

## Planted findings

The judge reproduced 5 of the 23 findings on a planted-defect copy (`JUDGE.md:14`, decision 0018
planted-defect recall). Their defects are **not in the register tree**: the finders audited a copy
with the defect written into it. The plant list is held out, so this seat rebuilt each plant from the
finding's own claim:

| finding | the claim's defect | at the register tree |
|---|---|---|
| D2-s1-01 | `flow_lift_factor` returns `carnot_ref / carnot_flow` | `carnot_flow / carnot_ref` (`thermal_model.py:3391`) |
| D2-s1-02 | `emitter_delivery` drops its `max(0, .)` | floored (`mixing_valve.py:138`) |
| D2-s3-06 | `_exact_topk_sum` takes `[:k]` | `[-k:]` (`tariff.py:918`) |
| D12-s2-01 | two_zone_mode `auto` forces two-zone | `auto` reaches the presence rule (`thermal_model.py:1122-1127`) |
| D12-s3-01 | `declared_modulation` maps `on_off` to modulating | `False` (`thermal_model.py:1473`) |

At the register tree, `batch_parity.py` (D2/s1) gives 0 mismatches on every arm. At these five sites
the enumerator lists `ok`. Its positive control re-plants all five on a temp copy and re-finds each
one. The other 18 findings reproduce at the register tree, each on its own harness. The table at the
end gives each command and number.

## Enumerator

`python3 dev/audit/rounds/round11/D14/sweep-P2/enumerate_p2.py` covers the whole package. Each of its
18 fact-families is one finding's `seam_rule`, widened from the files that finding named to every
module. A family lists every **site** of its fact. Sites whose shape is the finding's divergent shape
are **seams** (`SEAM`). Siblings that hold the guard are listed `ok`, with the guard the rule saw.

| family | rule (divergent shape) | findings | sites | seams |
|---|---|---|---|---|
| F01 unbounded_reap | `x.wait()` with no timeout on a non-awaited object | D1-s3-04 | 4 | 2 |
| F02 reader_settings | `InputReader(...)` without the entry's `enabled=`/`scale=` | D1-s2-52 | 4 | 1 |
| F03 data_shadow | `async_update_entry(data=...)` with no `options=` in the same write | D10-s2-01 | 3 | 2 |
| F04 zone_fact | two-zone decided outside `ThermalParameters.from_config`; a mode-dependent options row or service field with no mode gate; zone columns from trajectory presence | D12-s2-01, D12-s1-01, D17-s1-03, D17-s3-02 | 14 | 9 |
| F05 modulation | the on/off declaration read outside `declared_modulation`, or the owner mapping `on_off` to modulating | D12-s3-01 | 1 | 0 |
| F06 setpoint_range | a set-point write with no entity range in the writer, or a `quantise_setpoint_c` capped by config rather than the entity | D12-s3-02 | 5 | 5 |
| F07 domain_refuse | an `admitted()` refusal that drops a whole row/record | D15-s1-04 | 8 | 3 |
| F08 seeded_zero | `setdefault(k, [x, 0])` whose count is not `+1` in place | D15-s1-05 | 2 | 1 |
| F09 boost_branch | a return of a `boosted` target function that neither reads the boost nor follows a boost exit | D16-s1-03 | 12 | 5 |
| F10 record_trust | an arbiter comparison of its record against its own value, with no live reading among the operands | D16-s2-03 | 6 | 2 |
| F11 computed_eval | a `_Computed` default `.of()` evaluated over the pre-save mapping while judging a submit | D17-s1-02 | 1 | 1 |
| F12 wood_valve | a writer that stores `CONF_WOOD_FURNACE_ENABLED` with no throttling valve or detection | D17-s2-03 | 1 | 1 |
| F13 run_publish | `async_run_optimization()` outside the refresh cycle with no refresh after it | D17-s3-01 | 4 | 1 |
| F14 flat_windows | a function testing the clock against the flat DHW union, with no `windows_for_day` | D17-s3-51 | 5 | 5 |
| F15 twin_formula | a batch twin whose inline formula differs from its scalar owner (flow lift ratio, emitter floor, top-k slice) | D2-s1-01, D2-s1-02, D2-s3-06 | 3 | 0 |
| F16 small_rules | a water heat-capacity literal outside `const.py`; a naive instant read as host-local or HA-local; a finite-number predicate without `finite_float`'s NaN/inf/bool refusal | D7-s3-04 | 29 | 8 |
| F17 gap_feature | a `rank_sensor_gaps` row priced without its feature's gate | D8-s1-01 | 3 | 1 |
| F18 waiting_key | `_waiting_for` keyed off a value `native_value` does not read | D8-s1-03 | 4 | 2 |

Total: `RESULT sites_total=109`, `RESULT seams_total=49`.

**Controls**, all rc 0:

- **Positive** (`--control`): a temp copy takes the five rebuilt plants. Every judged site of the 23
  findings is then found again: `control_sites=29` (D7-s3-04 has five judged copies, D17-s3-02 and
  D12-s3-02 two each), `missed_sites=0`.
- **Null** (`--fixture`): a clean synthetic package, where one owner or the guard holds each of the
  18 facts. It lists 22 sites, `fixture.total=0`.
- **Perturbation** (`--perturb`): one re-introduction per family on a temp copy. Each moves its family
  by exactly +1 (`perturb_not_plus_one=0`). Families that need a whole function to match (F06, F10,
  F11, F12, F14, F16, F18) take an appended function, as round 10's F3/F5 did. Every other family
  takes a one-line edit of production text: the `_SHUTDOWN_LOCK_TIMEOUT_S` wait made bare, the
  external-heat reader losing its entry settings, the owner's two-zone and modulation mappings, a
  snapshot field refusal made a row drop, `freq_control`'s `+1` made conditional, the `_flow_target`
  boost ceiling dropped, the button's refresh deleted, the tariff top-k slice flipped, and a gap row
  re-keyed to DHW. Output: `perturb.out`, one full pass at the final rules.

**Probes for the instances beyond a finding**:
`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep-P2/probes_p2.py` -> `probes_failed=9 of 10`.
Each probe asks the seam and the fact's owner (or the sibling that holds the guard) the same question,
and fails when the answers differ. The tenth probe, `_sim_coldest`, passes, and that pass is its
disposition. Under `--perturb`, each seam gets its sibling's guard in memory, and the result is
`probes_failed=0 of 10`: the probes detect the divergence and nothing else.

## Dispositions (49 seams)

### Instances beyond a finding (9)

| seam | the fact, and the guard its sibling holds | probe |
|---|---|---|
| `config_flow.async_step_reauth_confirm:3299` (F03) | Effective Tibber token. The reauth writes `data=` only. The Entities options page stores `tibber_token` (config_flow.py:1696), and `{**data, **options}` lets that stored copy win. `_async_rewrite_entry` (coordinator.py:1498) writes both. | Entities page saved, then reauth with a new token: `reauth_successful`, effective token stays `token-old`. Perturb (write drops the data keys from options) gives `token-new`. |
| `coordinator._THERMAL_PARAM_FIELDS.upper_floor_thermal_mass:2730` (F04) | The mirror of D17-s3-02. The service accepts a two-zone-only field on a single-zone model with no mode check. Options rows have `when=_single_zone` for the house heat loss. | `two_zone_mode=off`: accepted, plan delta 0.000 kW-steps, 0.000 after restart. `house_thermal_mass` on the same install moves 45.771. |
| `..._THERMAL_PARAM_FIELDS.lower_floor_thermal_mass:2731` (F04) | Same as above. | 0.000 / 0.000 |
| `..._THERMAL_PARAM_FIELDS.inter_zone_heat_transfer:2732` (F04) | Same as above. | 0.000 / 0.000 |
| `coordinator._apply_result_payload:3107` (F04) | Zone columns. `data["schedule"]` `upper_temp`/`lower_temp` come from trajectory truthiness. The optimizer fills both lists on every model (optimizer.py:3887-3888). D12-s1-01 judged `space_plan.forecast` (`_build_plan_views`), a different payload. | `two_zone_enabled=False`: 96 of 96 schedule rows publish a zone temperature |
| `boost._window_open:738` (F14) | "Is a DHW window open now". With no plan it falls back to the flat `dhw_demand_windows`. The planner, `quiet_windows` and `silent_mode` resolve `windows_for_day`. | `weekdays 06:00-08:30, weekend 08:00-09:30`, Saturday 07:00: open=True, the weekday's window False |
| `coordinator._async_drive_pumps:4489` (F14) | Same fact. The VVC circulation pump gets `list(params.dhw_windows)` (4507-4515). | Saturday 07:00: run=True, False on the weekday's windows |
| `dhw_learning.DhwProfileLearner.async_fold_draw_stats:480` (F14) | Same fact. A draw is labelled by the flat union (`draw_window_label(..., params.dhw_demand_windows)`, 502-504). | Saturday 07:00 draw labelled `06:00-09:30`, the weekday's window `''` |
| `replay_doc._number:260` (F16) | "A finite number or nothing". It keeps NaN and ±inf as series values (replay_doc.py:300). `finite_float` refuses them. A sibling of the judged `replay_doc.numeric`. | 3 of 3 non-finite probes kept |

### Judged sites at the register tree (24 seams, `beyond_finding: false`)

| family | seam | finding |
|---|---|---|
| F01 | `coordinator._run_in_process:2107` | D1-s3-04 |
| F02 | `coordinator._indoor_humidity_value:9178` | D1-s2-52 |
| F03 | `config_flow._async_save_reconfigure:2875` | D10-s2-01 |
| F04 | `config_flow._OPTION_FIELDS.CONF_HOUSE_THERMAL_MASS:1865` | D17-s1-03 |
| F04 | `coordinator._THERMAL_PARAM_FIELDS.house_heat_loss_coefficient:2725`, `.house_thermal_mass:2726` | D17-s3-02 (two-zone arms: `on` at this tree; `auto` resolves single-zone here, see the plants) |
| F04 | `coordinator._build_plan_views:4821` | D12-s1-01 |
| F06 | `setpoint_check._dhw:169`, `repairs.DhwSetpointRepairFlow.async_step_confirm:51` | D12-s3-02 |
| F07 | `debugger._repair:166` | D15-s1-04 |
| F08 | `coordinator._fold_capacity_envelope:9335` | D15-s1-05 |
| F09 | `pump_arbiter._space_target:649` | D16-s1-03 |
| F10 | `pump_arbiter._write:1599` | D16-s2-03 |
| F11 | `config_flow._omit_unstored_computed:2448` | D17-s1-02 |
| F12 | `quick_setup.derive:202` | D17-s2-03 |
| F13 | `services.handle_run_optimization:604` | D17-s3-01 |
| F14 | `coordinator._dhw_in_demand_window:6040` (`_dhw_effective_windows`, which also feeds `_dhw_next_window_in_hours`) | D17-s3-51 |
| F16 | `sensor._gap_probe_terms:3000` (4.187), `open_meteo._ensure_utc:77`, `entity.payload_number:125`, `sensor._as_float:84`, `replay_doc.numeric:180` | D7-s3-04 |
| F17 | `topology.rank_sensor_gaps.CONF_DHW_TEMP_ENTITY:943` | D8-s1-01 |
| F18 | `sensor.MonthlySavingsSensor._waiting_for:532` | D8-s1-03 |

### Guarded (6)

| seam | guard |
|---|---|
| `heat_curve._send:397` (F06) | The value is clamped to the entity's declared min/max before `_send`: `offset_target` (heat_curve.py:308-329) and `persistent_target`'s `_within_range` (463-469). |
| `pump_arbiter._write:1608` (F06) | Every value it writes comes from `_bounded(...)` (`SetpointGrid.bounded`, inputs.py:658-684) in `_space_target`/`_flow_target`/`desired`. |
| `coordinator._valve_write_problem:744` (F06) | The written target is the entity's own configured valve target, not a computed floor. A write the entity refuses raises, is caught into the reason (746-747), and is latched by `log_held` at 7764-7766 with no record of a command. Residual for the barrier: no range is read before the write. |
| `coordinator._stored_fuse_advisor:3049` (F07) | A whole-record refusal. On the owner's download the ledger store is inside its domain: D15-s1-04's real-bundle replay found off-domain fields only in `off_restore` (1) and `snapshots` (101) (D15/s1/REPORT.json:205, :335). Not re-run here, because the bundle is private. The synthetic bundle (`tools/replay/dbg_bundle_gen.py`) writes no ledger. |
| `coordinator._async_load_ledger:8316` (`month_reports`, F07) | Same measurement. |
| `freq_control.FrequencyMap.observe:162` | Listed `ok` by the rule (count `+1` before any save; loader accepts `>= 0`). Named here because D15-s1-05's seam_rule names it. |

### Not applicable (16)

| seam | reason |
|---|---|
| `coordinator._shutdown_process_pool:1919` (F01) | A recorded design choice (docstring 1884-1898, #533). At exit, `wait(timeout=)` polls with `time.sleep` on the loop thread, and Home Assistant reports that as a blocking call. A SIGKILL'd child reaped by `os.waitpid` does not hit that report, and nothing is served at that point. The lock is not held (it is taken at 1932, after the reap). D1-s3-04's `proposed_fix_scope` names this arm too: the fixer must weigh #533 before bounding it. |
| `coordinator._sim_coldest:2616` (F04) | The fact is the same, but no input separates the values. On a single-zone plan the zone tracks never fall below the room track: `min_room_temperature` 19.51 = the room trajectory's 19.51 (probe passes). |
| `pump_arbiter._space_target:648` (F09) | The misdeclared-indoor refusal writes nothing at all, so there is no level for a boost to raise. |
| `pump_arbiter._level_kw:670` (F09) | The experiment's commanded power ranks above the boost by the documented order (docstring 660-667). An experiment step is its own action. |
| `pump_arbiter._flow_target:963` (F09) | A non-space duty (`_gate_c`, the DHW gate set-point), which has no space boost level. |
| `pump_arbiter._flow_target:974` (F09) | Duty `None`: the hold path, with no space duty to boost. |
| `pump_arbiter._note_sent:1120` (F10) | Compares the arbiter's own record with its own new output for feedback bookkeeping. By design it reads no entity. The write gate it feeds is `_write:1599` (judged D16-s2-03). |
| `coordinator._dhw_plan_fields:4309` (F14) | Rule over-match. The clock picks the weekday pattern and the immersion cutoff. The windows only key the stats table, and no instant is tested against them. |
| `coordinator._refuses_non_finite:496` (F16) | It refuses NaN and ±inf as `finite_float` does. A bool or a numeric string cannot reach it: it wraps learned scalars parsed from the store as floats (uses 5087, 5475, 5482, 5488). |
| `entity._finite:147` (F16) | A publication scrub, not a predicate. Non-finite floats become `None`, as `finite_float` says. Bools and strings are published values. |
| `sensor.WoodBurnAdvisorSensor._waiting_for:3085` (F18) | `native_value` returns a string whenever available (`... or "none"`), so "available but unknown" cannot occur. |
| `quick_setup.stored_answers:137`, `:138`, `config_flow.async_step_zones:3130` (F04, listed `ok`) | Form answers prefilled from the stored override, not topology verdicts. |

Counts: 9 beyond-finding instances, 24 judged sites, 5 guarded among the seams (the 6th, freq_control,
is an `ok` site), 11 not applicable among the seams (the table's last row holds `ok` sites,
named for the reader). 9 + 24 + 5 + 11 = 49.

## Barrier

The registry in `tests/entities.py` ('P2: one fact, one owner') holds eight facts. This round's
escapes fall into two groups:

- **Facts outside the registry**: the effective entry setting (F03), the reader's settings (F02),
  the DHW window at an instant (F14), the record against the live state (F10), boost precedence
  (F09), the entity's range (F06), and finite numbers (F16).
- **A registered fact in a new shape**: `two_zone_enabled` read as trajectory presence, or ignored by
  a service field or options row (F04).

Proposed barrier: register the families above whose rule held its controls here. Each would join the
registry as a new fact with its owner, `{F03, F04(c,d,e), F14, F10, F02}`. A registry entry's planted
sibling is this enumerator's perturbation. Measured cost: the full enumerator takes 23.9 s on this box
(all 18 families, AST only, every family re-walking every module). A registry entry that shares one
parse per module, as `tests/entities.py` does, costs a fraction of that; the gate seconds are owed by
the fixer that builds it, measured there.
The F14 entry, "no time test against `dhw_windows`/`dhw_demand_windows` outside `windows_for_day`",
would have caught D17-s3-51 and three of this round's escapes. The F03 entry, "an entry write of
`data=` drops those keys from options", would have caught D10-s2-01 and the reauth escape.

## Files

- `dev/audit/rounds/round11/D14/sweep-P2/enumerate_p2.py`: the enumerator, with `--control`,
  `--fixture`, `--perturb [--only]` and `--json`.
- `dev/audit/rounds/round11/D14/sweep-P2/probes_p2.py`: the 10 probes, with `--perturb`.
- `dev/audit/rounds/round11/sweep-P2.json`: the return.
