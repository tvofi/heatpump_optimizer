# R10-COMBI-TANK-PR-B: design note 1

Group R10-COMBI-TANK-PR-B (roster L, outside tier, #3225), after R10-COMBI-TANK.
**Base** `01782a1e3c327cbfb69784b8e676359e5bcfa079`. **Predecessor head read**:
PR A #3358 at `handoff/r10-combi-tank-pr` = `577c6974205926e7dbaa178b91af96a229ea02f3`
(open, not in the base; its model commit is `1743a1392`). Line numbers below are at
`577c6974` unless marked *base*. Parent design: `design/r10-combi-tank` `a605014b`
(approved at `design-verdict/r10-combi-tank` `56810263`); this note extends it and
re-states only what PR B changes or decides anew.

**Prior spike.** `handoff-wip/r10-combi-tank-b` `8a8ad71f2` (hpo-fixer, commit
`c2cb6262d` plus ledger commits, on `577c6974`) already implements parent items
§option/loader/seed/learners/topology/advisor/§T.4/§L and carries the trailer. It was
written with no PR B design. It is a spike under this note (designer.md step 8), not a
head: the fixer may rebase it onto PR A's merge and keep what this note confirms, and
re-runs fixer.md steps 2-8 at the new base. It **does not** implement carry 6
(accounting, §X below): none of `heat_energy.py`, `dhw_planner.py`'s economics or
`_accumulate_energy` is touched there.

## 1. Owning seams (one owner per concern)

| concern | owner | callers only |
|---|---|---|
| option keys, presets, limit | `const.py` (`COMBI_TANK_PRESETS`, `COMBI_LEGIONELLA_POTABLE_LIMIT_L`) | config_flow.py |
| option rows, pre-fill, `combi_needs_store` refusal | `config_flow.py` (`_F` rows on `building`, group `combi`) + `entry_config.py` `_WIRING` | strings.json, translations/{en,de,sv}.json |
| loading the four fields; the gate predicate | `thermal_model.py` `ThermalParameters._tabled_values` / `from_config`; `legionella_cycle_active` property beside `combi_tank_active` (thermal_model.py:319) | legionella.py, setpoint_check.py, dhw_planner.py, coordinator.py |
| the combi seed | module functions beside `_seed_store` (coordinator.py, base :2548) | `_update_current_state` (seam `core`) |
| learner skips | coordinator.py `_async_learn_buffer_cooling` (seam `learning`) and the `async_learn_dynamics` call | — |
| DHW edge, `dhw_source` | `topology.py` `layout_edges` / `describe_setup` | — |
| **booked hot-water share** (new) | `heat_energy.py`, beside `dhw_share` (base :266) | coordinator.py `_accumulate_energy` (base :10392) |
| **predicted DHW cost and baseline standby** (new) | `dhw_planner.py` `DhwPlanner._baseline_dhw_economics` (:362-408) | optimizer.py:5263 |

No concern has two owners. The type slug is read only by const.py/config_flow.py
(census `combi_type_branch`); the model reads two numbers.

## 2. Shape: items confirmed from the parent, with the carried corrections

- **Option**: `CONF_DHW_COMBI_TANK_ENABLED`, a type select pre-filling
  `CONF_COMBI_DHW_EFFECTIVENESS` and `CONF_COMBI_POTABLE_VOLUME_L`, and
  `CONF_DHW_COMBI_LEGIONELLA_FORCE`; refused with `combi_needs_store` by the model's
  own `combi_tank_active` on a `from_config` of the submitted page (one predicate,
  not a re-implementation in the flow).
- **Loader**: the two numbers in `_tabled_values`' table, the two booleans in its
  coerced-bool loop. `dhw_combi_tank_enabled` is loaded **raw**, not gated on
  another key, so the single-key probe in tests/features.py reaches it (unlike
  `toggle_gated`'s `wood_tank_volume`): `combi_tank_active` does the gating.
- **Presets (carry 3 figures)**: `internal_coil` 0.85 / 30 l
  [assumed; one measured 1.8 kW/K corrugated coil gives 0.89 at 12 l/min];
  `tank_in_tank` 0.95 [assumed] / 150 l, volume text "~100-250 l (IEA SHC Task 26
  store C: 228 l)"; `external_station` 0.75 / 0 l, help: eps 0.88 at 16 l/min to
  0.58 at 38 l/min (Remko RK WP table), read it at the typical draw flow, primary at
  or below 60 C; no "70 C cap". Worked example in help text: MFS 600 S, 504 l
  heating volume, coil 40 l / 7.5 m2, standing loss 111 W at 65 C ErP (2.66
  kWh/24h), UA = 111/45 = 2.47 W/K, 0.106 K/h over 504 l, 0.098 K/h over 544 l; the
  user enters **40 l**. Standing-loss help: prefer ErP S at 65 C, UA = S / 45 K,
  20 C ambient labelled [assumed]. T.1's EN 12977-4 sentence reads "multi-node
  model with fitted parameters". No preset or key names a product.
- **§L (carry 3 item 6 supersedes the parent's citation)**:
  `legionella_cycle_active = dhw_legionella_enabled and (not combi_tank_active or
  combi_potable_volume_l > COMBI_LEGIONELLA_POTABLE_LIMIT_L or
  dhw_combi_legionella_force)`. The default-off at <= 3 l rests on **physics** (no
  stored potable water to disinfect), not on a W 551 exemption: the help text
  removes the exemption citation, says W 551's 3 l is per pipe run downstream of
  the heater and a one/two-family house is a Kleinanlage whatever the volume, and
  that W 551 still expects >= 60 C (Grossanlage) or >= 50 C (Kleinanlage) delivery.
  Force toggle kept. `decision: owner` may re-rule the default (carry 3).
  Behaviour readers move to the property; census `combi_legionella_gate` = 0.
- **Seed**: `combi_tank_seed` = buffer reading if ok, else `_seed_store(dhw,
  result, "buffer_temp_trajectory", now)`, written to both fields; non-combi keeps
  the two independent `_seed_store` calls. Module-level, not coordinator methods
  (`max_class_loc` and `class_excess_loc` sit at zero headroom).
- **Learners, topology, advisor**: as parent (`async_learn_dynamics` skipped in
  combi; buffer-cooling samples with a planned draw skipped; edge
  `("buffer_tank","dhw_tank")`, `"dhw_source": "combi"`; DHW-probe miss price 0
  over a probed combi store).

## X. Display and accounting of the exchange (carry 6) — new in this note

**Finding.** `_combi_flux_exchange` (optimizer.py:1415) re-plans DHW against the
fixed space plan's net draw on the store, so `dhw_power_schedule` buys heat the
space side consumes (`exchange` arm: `exchange_dhw_kwh` vs `null_dhw_kwh`; the
carry's 22.135 vs 5.327 is a snapshot, re-measured at PR B's merge base). Two
money sites read that schedule as hot-water use:
1. **Realised**: `_accumulate_energy` books `energy * dhw_share(attribution(...))`
   into `dhw_energy_kwh` / `dhw_cost` / ledger line `"dhw"` (base :10392-10403),
   with the plan's `(space_power, dhw_power)` as the split whenever no mode dwell
   is observed. Where a dwell **is** observed, a combi pump's DHW-mode dwell (type-4
   ports) or its absence (no DHW valve) gives a third, unrelated split: the tile
   would change meaning with the observability of each interval.
2. **Predicted**: `_baseline_dhw_economics` sets `dhw_cost = predicted -
   cost(optimal_space)` (:407), which charges the exchanged space heat to hot water,
   and its baseline adds `p.dhw_store.ua_kw_per_c * (setpoint - 20)` as standby
   (:390). In combi `dhw_store` is the whole store (PR A `dhw_store_of`,
   thermal_model.py:1932). Combi needs a throttling valve, so the baseline space
   run (`_compute_baseline_power`, optimizer.py:5576) charges the store through
   `valve_charge_demand` (optimizer.py:764), the tank law the step inverts, which
   carries the store's own loss: **the store's loss is counted twice in
   `baseline_cost`, so predicted savings are inflated** — the "fictitious savings" the docstring's PV paragraph
   forbids.

**Decision: in combi the store's charge is one channel, booked as space heating,
and the hot-water figures say so.**
- `heat_energy.py` gains one pure function beside `dhw_share`: the booked
  hot-water share of a metered sum, `0.0` when the store is one channel, else
  `dhw_share(a)`. `_accumulate_energy` calls it with
  `params.combi_tank_active`. Learner readers of `Attribution` (`cop_duty`,
  `space_heat_kw`, `ran_hot_water`, coordinator.py:958) are **not** changed: they
  judge physics by duty, not money.
- `_baseline_dhw_economics`, when `p.combi_tank_active`: `dhw_cost = 0.0` and the
  baseline standby term is `0.0` (the space baseline run carries the store's loss
  once); `p.dhw_draw_power` stays in the baseline. Off combi, bit-identical.
- The DHW energy/cost sensors (sensor.py `DHWEnergySensor`, `DHWCostSensor`,
  `DHWHeatingCostSensor`) and climate.py:274 then read 0 in combi; the attribution
  statement the `_accumulate_energy` docstring promises in the sensor attributes
  gains the combi case ("one store: hot water is booked under space heating").
  No new entity, no payload key removed.

**Conservation invariant**: booked space + booked DHW = metered energy, and
predicted space cost + DHW cost = predicted cost, in both modes.

**Alternatives that lost.**
- *Consumer split* (DHW = tap draw heat + potable share of loss): a new
  estimator over a draw volume combi cannot measure (the parent skips
  `async_learn_dynamics` in combi), so a profile figure would be published as
  metered; and it needs a second COP conversion owned by neither seam.
- *Net the exchange out of the plan split* (space + exchanged, DHW - exchanged):
  needs the exchange series carried from the optimizer through the result and
  the pending interval into the coordinator (three modules, one new payload
  field), and still fails on observed intervals, where the dwell wins.
- *Baseline standby at UA x (setpoint - mean baseline store temp)*: exact, but
  `_compute_baseline_power` would have to return its store trajectory (a new
  output on a core-seam method); the chosen rule under-states the baseline by
  at most that term (measured below), never over-states it.

## 3. Sibling sites (enumerated by command)

- Money readers of the split: `git grep -nE 'dhw_share\(|\bdhw_cost\b|"dhw_energy_kwh"|dhw_heating_cost' -- 'custom_components/heatpump_optimizer/*.py'`
  at `577c6974`: writers coordinator.py:10392-10403 and dhw_planner.py:407 (both
  fixed); pass-through readers coordinator.py:2411/2414/3104/3183/4052/4055,
  payload.py:978/992, sensor.py:1262/1838/1883, climate.py:274, optimizer.py
  (result plumbing) need no change; coordinator.py:958 is the COP learner, out of
  scope (physics by duty). `_settle_interval_diag` apportions the meter for the
  model's space channel, a diagnosis comparator, not money: out of scope.
- Legionella behaviour readers: `git grep -n "dhw_legionella_enabled"
  custom_components/heatpump_optimizer/*.py`, re-measured at the merge base; the
  parent's reader/display partition stands.
- Preset slugs and product names: census `combi_type_branch`'s grep, base count
  recorded, must not grow.

## 4. Evidence plan

- **Failing tests first** (tests/features.py): (a) a combi stub interval with
  planned `(1.0, 3.0)` kW books `dhw_energy_kwh` +0 and space = metered (today:
  75 % to DHW); null control combi off: 75 % unchanged. (b)
  first the premise's control: the combi baseline space run's energy moves when
  the store's UA is zeroed (it books the loss); if it does not move, §X's standby
  rule is wrong and the fixer stops and reports to the designer. Then
  `_baseline_dhw_economics` combi: `dhw_cost == 0`, `baseline_cost` drops by
  exactly the store's `ua_kw_per_c*(setpoint-20)` over the horizon, priced; null:
  off combi bit-identical. (c) `unwired_combi` emptied (carry 5) and the 9720 check
  sees all four fields reachable; control: the check's own red at 577c6974
  (`probe` None for all three). (d) parent arms `legionella_potable`, seed and
  learner mutation, `presets` with source labels.
- **Finder's harness**: `dev/audit/harnesses/r10_combi_tank.py` (PR A's arms)
  gains arm `accounting` on the `exchange` day: prints `exchange_dhw_kwh`,
  `null_dhw_kwh` (carry 6 re-measure at merge base), the booked DHW and space
  kWh over the plan, their sum against Σ(space+dhw)·dt (conservation), the
  removed baseline double count, and the under-statement bound UA x (setpoint -
  mean baseline store temp) x 24 h. Run at both ends: `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_combi_tank.py exchange accounting`.
- **Mutation targets**: the one-channel term in the new heat_energy function;
  the combi branches of `dhw_cost` and standby; `>` -> `>=` and the force term in
  `legionella_cycle_active`; the seed's buffer-first order; the learner skip.
- **Goldens**: no golden config enables combi, so savings goldens do not move;
  the option-flow fingerprint golden gains additive keys (the spike claims them,
  `82d5ba034`): claim in `tests/golden/claimed_drift.txt` with `claims-for:` =
  `VERSION`; otherwise both claim files byte-identical.
- **Censuses kept** (carry 7): `combi_flux_live` (tests/entities.py
  `_P2_CENSUSES`) stays; `lp_flux` is not read as covering the LP-free recursion
  or the legionella run-up exo sites.
- **Ratchet**: `class_excess_loc` and `max_class_loc` have zero headroom at base;
  new code goes to module functions; pay by improving code; any raise is the
  owner's, asked before the push.

## 5. Hot files, order, carries

Hot: config_flow.py, entry_config.py, const.py, thermal_model.py, coordinator.py,
topology.py, sensor.py, legionella.py, setpoint_check.py, dhw_planner.py,
heat_energy.py, strings.json + translations, docs/configuration.md,
tests/features.py, tests/entities.py, tests/config_flow_steps.py, the harness.
Order: after R10-COMBI-TANK; **its merge base must contain PR A** (`1743a1392`), and
PR A is open and `blocked ci-red` at this note. The designer revalidates against
PR A's merged diff before the fixer dispatches (designer.md step 9). Overlaps
admitted by the roster note are ordered by after-edges.

Carries received (roster carries 0-7): 0 survey/generality — met by the parent's
§T, unchanged; 1 ten-round waiver and the four review lenses; 2 and 3 web
figures — §2; 4 trailer `Co-authored-by: Bankaifan <476059+Bankaifan@users.noreply.github.com>`
in one of PR B's own commits, named under `## Forward-carry`, no README change;
5 `unwired_combi` — §4(c); 6 accounting — §X; 7 census — §4.

## Notes for the fixer

- Carry: R10-COMBI-TANK-PR-B (item spike-rebase). The spike's commits carry
  `Co-authored-by` already; after a rebase confirm with `git log --format=%B`
  that exactly one PR B commit carries it and no tool trailer exists.
- Carry: R10-COMBI-TANK-PR-B (item exchange-remeasure). Record the `exchange` and
  `accounting` arms' lines at the merge base in `## Figures`, not the carry's
  snapshot.
- Carry: R10-COMBI-TANK-PR-B (item probe-height). Help text: one probe is read as
  the store mean; the middle well (MFS: 1 250 mm), not the top well.
- Carry: R10-COMBI-TANK-PR-B (item w551-proxy). The option help says the 3 l
  limit is a physical proxy (no stored potable water), not a W 551 exemption.
