# Design: R11-SEAM-money (round 11, size L)

Architect note, extended (`dev/governance/roles/designer.md`). Plan of record
`plan/r11` at 819aa2e354b4e5baaf824b8568fd72bea8168a75: `PLAN.md`, ADR-006,
ADR-001 (arms `day`, `entry`), ADR-002 part 1. Code read at `origin/main`
bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f; the group has no `after` edge, so no
predecessor head. No production code on this ref.

## 1. What each finding reads at the base (finder's harness, run here)

| finding | harness | at bc658f9ded | live |
|---|---|---|---|
| D2-s3-03 | `D2/s3/m4_tariff.py` `tibber_rows_dropped` | 0 | no |
| D2-s3-04 | same, `fee_mismatch_steps` | 0 | no |
| D2-s3-05 | same, `tracker_peak_err_max` | 0.0000 | no |
| D2-s3-06 | same, `peak_cost_err_max` | 0.0004 (tol 1e-3) | no |
| D17-s1-05 | `D17/s1/h_guard.py` `guard_wrong_minutes_total` | 0 | no |
| D2-s3-07 | `m4_tariff.py` `coverage_full_23h` | 1.001346 | yes |
| D8-s1-02 | `D8/s1/monthly.py` `first_scale` | 2688.0 | yes |
| D14-s1-03 | `D14/s1/currency_precedence.py` `money_seams` | 5 | yes |
| D5-s3-01 | `D5/s3/ha_free.py` `claimed_but_needs_ha` | 1 | yes |

(harness paths under `dev/audit/rounds/round11/`.) The first five were judged
on a "planted copy" (`JUDGE.json`); the money modules are unchanged between the
baseline 92d38ecb and the base except `ledger.py`, and the baseline already
reads both Tibber periods, `weekday()`, `kw > best`, `sort[-k:]` and the
docstring's projection. The class sweeps say the same
(`sweep-N-partial-payload-parse.md`, `sweep-N-inverted-aggregate.md`).
Their part is a **barrier, not a fix**: §3 E.

## 2. Owning seam

Money (`COMPONENTS.md`): `ledger.py` owns the open month's projection,
`price_model.py` owns which source prices the plan, `currency.py` (kernel by
the table, planned owner of D14-s1-03) owns the precedence of a money figure's
code, `tariff.py` the top-k. Callers only: `sensor.py`, `coordinator.py`,
`config_flow.py`. No concern needs two owners. `power_guard.py` and
`grid_fee.py` take no production edit (D17-s1-05 not live; D5-s3-01 is
docstring truth, made true by ADR-002 part 1).

## 3. Shape

**A. Open-month projection (D8-s1-02, D2-s3-07; sibling `pro_rata_factor`).**
- `ledger.month_hours(now)`: the month's real hours: aware first instants of
  this and the next month in `now.tzinfo`, subtracted **after** `.astimezone(UTC)`.
- New `ledger.MIN_COVERAGE_HOURS` (finder's perturbation: 24).
- `coverage_factor(meta, now) -> float | None`: `None` when settled hours (or,
  on the pro-rata fallback, real hours elapsed since the month's start) are
  below the floor; else as today, on real hours. `pro_rata_factor` keeps its
  name and the floor is read inside `coverage_factor`, its one caller.
- `MonthlyLedger.savings_months`: a `None` factor omits the open month's row.
  No payload key is added (`payload.SavingsMonth` untouched).
- `MonthlySavingsSensor._waiting_for`: `"open_month_coverage"` when rows exist
  and none is `estimated`; the existing `"settled_savings_month"` otherwise.

```
before: cycle -> ledger.savings_months -> coverage_factor (x2688) -> row -> sensor/card
after:  cycle -> ledger.savings_months -> coverage_factor None (< floor) -> no open row
                                                    -> sensor waiting_for open_month_coverage
```

**B. One currency for every money figure (D14-s1-03).**
- `price_model.price_feed(config) -> str | None`: the entity that prices the
  plan, read through `EntryConfig`; replaces `coordinator._price_feed` and
  `_entity_price_source`, and `pull_prices` reads its source through it (a
  third copy of the test, raw `config.get`).
- `currency.figure_currency(hass, feed, adopted=None) -> str`: the feed's
  `declared_currency`, else `adopted`, else `resolve_currency`. Duck-typed
  `hass` (`states.get`, `config.currency`); no new import.
- Coordinator `__init__` and the cycle's adoption call it (adopted =
  `self.currency`); `coordinator._feed_currency` goes.
- `config_flow`: `_ByHass.of` takes `(hass, current)`; `_money`,
  `_fee_placeholders`, `_grid_fee_errors` call `figure_currency(hass,
  price_feed(current))`, so labels, the fee bound and validation follow the feed.
- Kept: the coordinator's currency-mismatch notice compares feed with
  `resolve_currency` on purpose.

```
config_flow._money --\                          /-- declared_currency(feed attrs)
coordinator.__init__ --> currency.figure_currency --- adopted
coordinator cycle  --/   feed = price_model.price_feed(cfg) \-- resolve_currency(hass)
```

**C. ADR-001 arms.** `price_model._usable_day(prices, steps)` shared by
`observe_day`/`observe_day_quarters`; `MonthlyLedger._entry(when, section,
name, zero)` shared by `add`/`observe_meta_mean`, as
`D7/s1/m7_prototypes.py` arms `day`, `entry`.

**D. ADR-006.** Part 1 already holds (both take `[-k:]`). Part 2
(`_smooth_topk_sum` as one row of `_smooth_topk_sum_batch`) is tried under its
condition; `_plateau_aware_topk_sum`'s docstring records the one-row overhead,
so the expected outcome is "dropped and recorded" (`prototypes.py --only topk`).

**E. Barriers for the five not-live findings.** For each, a check in
`tests/features.py` that fails on the harness's planted inverse; where an
existing check already kills it, the fixer records that check, adds none.

**Invariants kept:** a closed month's figures are unchanged; a month at or
above the floor scales by `month_hours/settled` exactly as today except DST
months; every money unit the coordinator publishes keeps its code (golden
`currency` keys byte-identical, no claim).

## 4. Alternatives (lost on the code)

- Floor in `sensor.py` only (the finder's perturbation): the card, notifier and
  diagnostics read `savings_months` from the payload and keep the x2688 row;
  two owners of one projection.
- Open row kept with `None` figures and a `below_coverage_floor` flag: adds a
  `payload.SavingsMonth` key (input-boundary file), a card branch and a string.
- `price_feed` in `currency.py`: the kernel module would import `entry_config`
  (input boundary), an upward edge `layer_violations` counts.
- Options flow reading `coordinator.currency` from `runtime_data`: no value
  before first setup; a second path.

## 5. Sibling sites (commands)

- `grep -rn 'resolve_currency(' custom_components/heatpump_optimizer/`: six;
  `config_flow` three and `coordinator` `__init__` covered, the two notice
  reads kept (§3 B).
- `grep -rn 'monthrange\|month_hours(\|pro_rata_factor(\|coverage_factor(' custom_components/heatpump_optimizer/`:
  all in `ledger.py`, covered.
- `grep -rn 'PRICE_SOURCE_ENTITY\|price_source' custom_components/heatpump_optimizer/`:
  `coordinator`, `price_model` covered; `config_flow` steps choose the source
  (not a read of it); `debugger`/`replay_doc` read a stored replay document,
  out of scope (not the entry).
- `grep -rln 'savings_months' custom_components/heatpump_optimizer/`: card,
  notifier (closed months), optimizer, payload already handle an absent open month.
- Class sweeps' enumerators (`D14/sweep_partial_window.py` and siblings) are
  cited by the sweep notes but not in the tree; the greps above stand in.

## 6. Evidence plan

- Failing tests first, `tests/features.py`: March 2026 settled every hour reads
  `coverage_factor` 1.0 (fails today 1.001346); one settled quarter in February
  gives no open row and sensor `waiting_for == "open_month_coverage"` (fails
  today: row x2688); SEK instance + EUR feed: the four `_money` fields, the
  placeholder and `spec_problem` bound in EUR (fails today: SEK). Existing
  `month_hours == 672.0` (Feb) and the `pro_rata` upgrade row checks keep.
- Finder's harnesses at both ends: `m4_tariff.py` `coverage_full_23h` 1.0;
  `monthly.py` swing to the perturbation's value; `currency_precedence.py`
  `money_seams` 0; `ha_free.py` 0 (§7). Null controls: `monthly.py` on a
  closed month, `currency_precedence.py` SEK feed (reads 0 before and after).
- Goldens: none move (no tariff, solver or currency change on the goldens'
  paths); `claimed_drift.txt` byte-identical.
- Mutation targets: `ledger.month_hours`, `coverage_factor`'s floor compare,
  `figure_currency`'s precedence order, `price_feed`'s source test, and each
  planted inverse of §3 E.
- Fitness: `prototypes.py --only owners` two copies; `tests/structure.py`
  `duplication_copies`, `layer_violations` not up; `tests/stress.py` for
  part 2.

## 7. Hot files, serial position, carries

Hot-file order (`PLAN.md`): after `kernel-layering` on `currency.py`,
`tariff.py`, `power_guard.py`; after `kernel-step` on `power_guard.py`,
`sensor.py`; seventh on `coordinator.py`; fourth on `config_flow.py`. D5-s3-01
closes only after `kernel-layering`'s ADR-002 part 1 (`currency.py`'s import
annotation-only); this group does not make that edit. Release notes owe the
open-month change (unknown for the first 24 h) first (T7). No p1/p2 split.

### Notes for the fixer

- Subtracting two datetimes that share one `tzinfo` is wall-clock in Python:
  convert to UTC first or March still reads 744. Carry: R11-SEAM-money (item month-hours-utc)
- `waiting_for` codes are untranslated attribute values (`settled_savings_month`
  has no `strings.json` entry), so the new code adds no string. Carry: dismissed: no string owed (item waiting-code-string)
- `replay_doc.py` comments name `coordinator._entity_price_source`; repoint at
  `price_model.price_feed`. Carry: R11-SEAM-money (item replay-doc-pointer)
