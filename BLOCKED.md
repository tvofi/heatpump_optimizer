# BLOCKED: r10-sav-valuation-residue-p3 (Carry 10)

Question: Carry 10's fix has no sound surface inside this part's edit set. Which route does the orchestrator rule: (a) name the split by relabelling the three DHW entities as pump-mode figures, which needs README.md (sensor table) and tests/entities.py (entity-name list) added to the edit set; (b) recount the settled split as one store channel on combi in coordinator.py's `_planned_split` / heat_energy.py attribution, added to the edit set; or (c) close the part as a disposition, carrying the reader census below to R11-INTAKE-R10-RESIDUE?

Measured at merge base a77d71fb75 (origin/main), head 6ce29b69ab (adds only the harness row).

## Reader census (FIRST STEP)

Command: `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_combi_tank.py exchange`

| row | dhw_kwh (plan, kWh_el) | published dhw_heating_cost | tap_draw_kwh_th | worst_shortfall_c | rounds |
|---|---|---|---|---|---|
| exchange | 22.135 | 46.357 | 7.830 | -1.455 | 3 |
| null | 5.327 | 7.304 | 7.830 | 28.767 | 0 |

Null control (separate tank, same day, same probe with `combi=False`): exchange and null rows identical, dhw_kwh 4.216, dhw_heating_cost 6.215, so the move is the combi exchange's alone.

User-visible readers of the plan's hot-water split, each by code read:

1. **Card DHW kWh tile: does not exist.** The card's tiles are `tiles.price_now`, `tiles.planned` (total electricity), `tiles.cost`, `tiles.indoor` (custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js); the only DHW series is the `dhw_slots` power bars (`dhw_power`), and the receipt shows billed lines only (`BILLED_LINES`), not the `dhw`/`space` lines.
2. **DHW Heating Cost (next 24 h)** (`dhw_heating_cost`, sensor and climate attribute): shows the exchanged heat as hot water, 46.357 against 7.304. Computed in dhw_planner.py `_baseline_dhw_economics` as DHW-mode marginal cost (`predicted_cost - energy_cost_of(optimal_space)`); dhw_planner.py is not in the edit set.
3. **DHW Energy (lifetime) / DHW Cost (lifetime)** and the ledger's monthly `dhw`/`space` lines and reason partition (`explain_metered`): booked from coordinator.py `_planned_split(pending)` through heat_energy's attribution, i.e. the actuated slot's `dhw_power` (22.135 kWh on this day where the meter follows the plan and no mode dwell is observed). Neither file is in the edit set.
4. **Savings figure: does not read the split.** `Ledger.observe_spot_and_settle_savings` books from total `actual_kwh`, `pending["power"]` and `SETTLEMENT_KEYS` (custom_components/heatpump_optimizer/ledger.py); the plan's `baseline_cost - predicted_cost` sums both channels. (Its value does move with the exchange, -3.165 against 35.888 on this day, because the exchange buys the extra charge on a fixed space plan; that is the exchange's feasibility mechanism, not this part's.)

## Why no route fits the edit set

- Label ("say which split it shows"): no card tile exists; the published keys' labels are the entity names in strings.json / translations, and renaming them breaks README.md's sensor table and tests/entities.py's name list, neither editable here.
- One channel at the optimizer publication site: the pre-exchange DHW plan is not a clean counterfactual (the published plan passes `_avoid_priced_switches` and `_realize_joint` after the exchange), and an outflow-based apportion moves the combi `null` row, which the brief's null control requires bitwise.
- The settled split (reader 3) lives in coordinator.py / heat_energy.py.

My recommendation: (a), as pump-mode labels are true on every install (a separate tank's DHW mode is its hot water), keep every figure bitwise, and leave actuation untouched. Carry: R10-SAV-VALUATION-RESIDUE (pending orchestrator ruling)
