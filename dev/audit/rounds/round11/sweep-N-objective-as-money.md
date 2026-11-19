# Class sweep: N-objective-as-money (round 11, PLAN phase D)

Class mechanism: a solve-only adjustment is carried into a figure booked or published as currency.
Status in `dev/audit/config/bugclasses.json`: **no entry** for this class (new from the round-11 judge); it needs an `open` entry.

## Source of the adjustment
`optimizer.py` `_stash_price_horizon` (L4717-4721) adds `price_risk_lambda * sigma` to unpublished
steps and returns the result as the solve's `prices`; it becomes `h.prices` and feeds
`_energy_cost_fn` (L5324). Every reader of either carries the premium.

## Enumerator (D14 step 3)
`python3 -I dev/audit/rounds/round11/D14/enum_objective_as_money.py [pkg]` lists every booking line
fed by `energy_cost_of`/`h.prices`, or by an objective-only term, gated on the adjustment existing.
- Positive control: lists `optimizer.py:5602-5603`, the D2-s3-01 site. 9 seams at the register head.
- Null control: package copy with the `+ risk` line removed -> `0 seams`.
- Perturbation: one re-introduced `predicted_cost = energy_cost_of(p)` before each `savings =` -> 11.

## Disposition (D14 step 4)
| seam | disposition |
|---|---|
| optimizer.py:5602-5603 space baseline/predicted cost | instance (judged finding D2-s3-01) |
| dhw_planner.py:519-524 `_baseline_dhw_economics` | instance beyond finding (same priced closure on the combi/DHW path) |
| optimizer.py:6318-6355 `_settle_horizon` deferred cost on `h.prices` | instance beyond finding |
| optimizer.py:3869 `result.prices` published per step (read L6581) | instance beyond finding |
| comfort penalty, terminal cost, capacity tariff, start/switch cost | guarded: separate closures summed only in `objective`; `predicted_cost` reads `energy_cost_of` alone |
| `price_tiles.monthly_held_cost_delta`, sensors `baseline_cost`/`predicted_savings` | not applicable as separate seams: downstream readers of the rows above, fixed with them |

Instances beyond the finding: 3. Proposed barrier: book with an unadjusted `energy_cost_of` built from the raw
price series; a `tests/` pin solving at lambda 0 and lambda>0 and asserting equal booked cost for equal powers.
Not barriered today.
