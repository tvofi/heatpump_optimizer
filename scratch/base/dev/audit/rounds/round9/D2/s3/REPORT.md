# Round 9 — D2 seat s3 (D2.M4, tariff and prices), baseline 1936d5ca

Scope: `D2-s3` = step D2.M4 over every file. Box B7, light seat. Interpreter
`/home/claude/venv314/bin/python`, `PYTHONPATH=tests/hastub`, run from the
export root. Exposure: none (no docs/, no GitHub).

## Method

Read `tariff.py`, `grid_fee.py`, `price_model.py`, `currency.py`, `pv.py` and
the coordinator's price seams (`_price_series`, `_known_prices_for`,
`_current_spot_price`, `_fee_series`, `_pv_export_price`) and the optimizer's
`_energy_cost_fn`. Each identity was driven on the production symbol against
an independent formula, with a null arm and an in-memory perturbation.

## Findings

### D2-s3-01 — `_current_spot_price` reads a quarter up to 45 min stale under 15-minute prices (high, bug)

`coordinator.py:_current_spot_price` returns the first entry with
`ts <= now < ts + 1 h`. The default Tibber pull asks for `QUARTER_HOURLY`
prices, and with 15-minute entries the first such entry is the one that
started up to 45 min before now. The published `current_price`, the
settlement's `price`/`spot_price`, sysid's `price` and the comfort learner's
relative price all read it. The plan's step 0 (`_known_prices_for`, which
takes each entry's end from the next entry's start) disagrees with it on the
same quarters.

Harness: `tools/audit/round9/D2/s3/current_quarter_price.py`. Seven price
profiles, 96 quarters each:
- Ramp arm (prices ramp within each hour): 28..42 of 96 quarters wrong on the
  6 non-flat profiles. Mean |error| is 0.042..0.584 per kWh, with a mean of
  0.185 (0.105 after dropping the largest cell).
- Step arm (quarter entries, prices constant within each hour): 12..18 of 96
  wrong. These are the three quarters after every price change, which read
  the old price.
- Null controls: hourly entries 0, flat profile 0.
- `--perturb` (span shortened to 15 min): every quarter arm reads 0. The
  hourly-entries control then breaks (273), which shows the fixed span is the
  mechanism. An honest fix takes the span from the entries themselves.

### D2-s3-02 — the PV piecewise cost is clipped wherever import < export price (medium, bug)

`pv.import_margin` floors `import − export` at zero, so a surplus-covered kWh
is priced at the import price instead of the export compensation it forgoes.
That breaks the identity `export·min(P,s) + import·max(P−s,0)` stated in
`pv.py` and in `_energy_cost_fn`. With the shipped default export price 0.0
this happens in every negative-price hour that has surplus.

Harness: `tools/audit/round9/D2/s3/pv_piecewise.py`.
- Identity breaches:
  - `summer_negative` @0.00: 16 of 96 steps.
  - `summer_negative` @0.30: 16 of 96 steps.
  - `summer_typical` @0.30: 20 of 96 steps.
  - The other 9 cells: 0.
- Signed error at a flat 3 kW draw, export 0.30: −5.04..0 per day. The mean
  is −1.14, and −0.36 with the largest cell dropped.
- On a real solve, the published `predicted_cost` is −0.609 where the
  identity gives 0.000. The plan draws 5.07 kWh from surplus in
  negative-price steps, against 2.27 kWh unfloored.
- The DHW blended block rate (`pv.blended_block_prices`) breaches on the same
  16 steps.
- Nulls: winter and flat profiles @0.00 = 0, no surplus = 0.
- `--perturb` (floor removed): every cell reads 0.

## Non-findings (held)

From `tools/audit/round9/D2/s3/m4_probes.py`, whose `--perturb` moves probe 3
to 500/500:
- `_known_prices_for` on the 23 h and 25 h Stockholm days, with hourly and
  quarter entries: 0 of 384 steps wrong.
- `GridFeeSchedule.fee_vector` (base rule, Nov–Mar weekday 06–22, wrapping
  night rule, decimal comma) over both DST days and a January week: 0 of 900.
- `peak_cost` equals `price·Σ top-k per-day-max excess`: 0 of 500 random plans.
- `PeakTracker` billed peak equals the mean of the top 3 distinct-day hourly
  means over a month of 15-minute samples, and resets at month rollover:
  0 of 2 checks.

## Unfinished (D2.M4)

- Capacity tariff at the month boundary: plan windows past midnight on the
  1st are charged against the old month's threshold. Not measured.
- Currency: the SEK/kWh surcharge is added to entity series in another
  currency. Not measured.
- The PV export price entity against the static value under negative spot.
  Not measured.

## Harnesses

- `tools/audit/round9/D2/s3/current_quarter_price.py`
- `tools/audit/round9/D2/s3/pv_piecewise.py`
- `tools/audit/round9/D2/s3/m4_probes.py`

All three are count or currency identities. None is timing, so none is
provisional. The thread_factor was 1.000 on every run and load1 was 0.1–0.4.
