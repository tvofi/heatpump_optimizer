# Class sweep: N-partial-window-extrapolation (round 11, PLAN phase D)

Class status: absent from `dev/audit/config/bugclasses.json` (new this round; to be added as `open`).
Mechanism: a window or period figure is projected linearly from its elapsed part with no minimum-coverage rule.

## Enumerator

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep_partial_window.py --controls --probe`

AST scan of `custom_components/heatpump_optimizer/` for functions that divide or remainder-weight a whole-period
quantity (`month_hours`, `monthrange`, `window_minutes`) by an elapsed or settled part, with no `MIN_COVERAGE`-style floor.

- Positive control: lists `ledger.coverage_factor` (D8-s1-02) and `power_guard.project_window_mean` with its caller `coordinator._on_power_event` (D17-s1-05).
- Null control: a clean fixture with a coverage floor returns `[]`.
- Perturbation: deleting the one floor line lists the fixture.

## Seams

| seam | disposition | probe / reason |
|---|---|---|
| ledger.coverage_factor | instance (D8-s1-02) | 15 min settled in Feb gives 2688.0 |
| power_guard.project_window_mean / coordinator._on_power_event | instance (D17-s1-05), one seam | 1 elapsed min gives 8.85 kW of 9.0 instantaneous; h_guard.py counts 69 |
| ledger.pro_rata_factor | instance, beyond findings | day 1 00:15 gives 28.0; coverage_factor's fallback, same missing floor |
| accuracy.pairs_interval | not applicable | an age gate, not a projection |
| optimizer/tariff projected_peak_kw | not applicable | plan simulation over the horizon, not elapsed extrapolation |
| notifier monthly receipt | not applicable | consumes closed-month savings_months rows |

Instances beyond findings: 1. Barrier: none (`barriered: false`); proposed barrier is a `tests/` minimum-coverage check over this enumerator's output.
