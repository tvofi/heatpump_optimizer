# Monthly savings history (card page)

Approved design, 2026-09-05. Realised thermostat-baseline savings, calendar
pro-rata for the open month, third expanded-dialog tab.

Part of #201. Programme seat: **3L-G7** (see Seat).

## Goal

A Savings page on the expanded card: one row per calendar month that has
booked savings, showing baseline SEK, actual SEK, savings SEK, and savings %.
Closed months are booked totals. The current month is the same four numbers
scaled to a full month and labelled estimated.

## Non-goals

- Capacity tariff, grid fee, wear, or `deferred_energy_cost` in this table.
- Reconstructing history from HA Recorder or from `predicted_savings`.
- A new Store. The existing `MonthlyLedger` (24 months) is the store.
- Changing Plan or Setup, or making `ContractComparisonSensor` required.
- Publishing the baseline power series on the plan sensor (goldens must not
  move for this feature).
- Re-recording value-bearing goldens. `claims-for:` stays `6.3.14`.

## Settlement

Two new ledger lines, booked in `_accumulate_energy` next to `spot`:

| line | kWh | SEK |
|---|---|---|
| `savings_baseline` | `baseline_kw × dt` | that × spot |
| `savings_actual` | metered kWh (spot + immersion, same as contract comparison) | that × spot |

Savings is **derived**, never booked: `savings_sek = baseline.sek − actual.sek`.

On interval **start**, `_pending_prediction` stores `baseline_kw`: the then-current
step of the last solve’s thermostat baseline (space + DHW, the same arrays
`_compute_baseline_power` already builds). Keep that series on the coordinator
only.

On interval **end**, if `baseline_kw` is missing (no plan for that interval),
**skip** both lines. Do not write zeros.

Spot is `_current_spot_price` already on the pending dict. `dt` is the settled
elapsed hours. Do not use the grid-fee-inclusive price.

`%` uses the existing clip in `_savings_percentage`: `savings / baseline` when
`baseline_sek > 0.01`, else omit `savings_pct` (`null`).

## Rows

A month is included only if it has any `savings_baseline` booking.

Each published row:

```
month: "YYYY-MM"
baseline_sek: float
actual_sek: float
savings_sek: float
savings_pct: float | null
estimated: bool
```

Closed months: `estimated: false`, SEK from ledger lines, `%` from those.

Open month (`month_key(dt_util.now())`): take live MTD of the two lines, then
multiply `baseline_sek`, `actual_sek`, and `savings_sek` by

```
days_in_month / max(1, now.day)
```

`now` is `dt_util.now()` (HA local). `days_in_month` is that calendar month’s
length, not 30. `%` is not rescaled (all three SEK columns share the factor).
`estimated: true`.

Row order: oldest first, newest last (current month at the bottom).

## Publish

Coordinator helper builds the list into `data["savings_months"]`.

New always-on sensor `MonthlySavingsSensor`:

- object id / discovery suffix: `_monthly_savings` (same suffix contract as
  `_predicted_savings`)
- state: open-month **estimated** `savings_sek`, or `None` if the open month
  has no row
- attributes: `{ "savings_months": <list> }` and, when the list is empty,
  `waiting_for: "settled_savings_month"`. Omit `waiting_for` once any row
  exists.

Do not put the list on `ContractComparisonSensor` (disabled by default).

Pin the new attribute names in the entities holes list (the #405 rule).

`_freeze_month_report` already copies non-`reason:` lines; the two new lines
ride along. The card does not read the receipt for this table.

## Card

Third expanded-dialog tab: Plan / Setup / Savings. `activePage` is
`plan | setup | savings`. Default tab unchanged (plan if a plan exists, else
setup). Legend remains plan-only.

Savings body: a table with columns month, baseline, actual, savings, %.
Keys (en + sv): `header.tab_savings`, `savings.col_month`,
`savings.col_baseline`, `savings.col_actual`, `savings.col_savings`,
`savings.col_pct`, `savings.estimated`, `savings.empty`. Empty state when
the attribute is missing or the list is empty — no invented zeros.

Find the sensor by suffix `_monthly_savings`. Currency from the existing card
currency rule (plan / HA / SEK). Do not convert.

## Tests

- Settlement: with a pending baseline, both lines move; without, neither
  moves. Mutation: delete the book, the “lines move” check fails.
- Pro-rata helper: known MTD + known day-of-month → scaled triple; `%`
  unchanged; day 1 uses divisor 1.
- Sensor: empty → state `None`; one open month → state equals that row’s
  estimated `savings_sek`; attributes list matches.
- Holes-list pin covers the new attribute names.
- `card.mjs`: third tab; empty copy; one estimated current-month row.

`cp` backups for mutation, restore md5. Gate lock if select is `MODE: FULL`
or names `tests/stress.py`. No `SOLVE_BUDGET_RATIO` raise. `coordinator_loc`
after W3-G3 is at ceiling: pay for new helper lines or stop and ask; do not
raise without the owner.

## Seat

**3L-G7**, one PR, after **3L-G6 (#457)**, before Wave 4. Coordinator
behaviour must land before the #193 moves (principle 3).

Do not start while W3-G3 holds `coordinator.py`. Do not start while 3L-G5
(#408) holds coordinator/config if that group is still open.

If #457 is still blocked on the conflict-flow spec, sit **after 3L-G5 (#408)**
instead so Wave 4 does not wait on the setup button.

Model: Grok 4.6 extra high (touches coordinator settlement). Card half may
be the same PR.

Issue **#460** is filed. `Closes #460` on its own line. Do not reuse #457.
