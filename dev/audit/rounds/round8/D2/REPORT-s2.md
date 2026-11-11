# Round 8 D2, seat s2: objective, tariff and price folding, estimators

Baseline `cdf82daabcfe3777d98b31489f36df5555ec9d82`. Tree `/home/claude/audit-r8/seats/D2-s2` (a copy). Machine: 4-vCPU shared cloud container. Every number below is a deterministic count or ratio; none is a timing.
Run all harnesses from the tree root with `PYTHONPATH=tests/hastub` and the five BLAS variables set to 1.

## Method
- Step 3 (objective): checked the cost and savings identities on every golden plan fixture. The terminal credit, `price_weight` scaling and the gradient-versus-FD check were not executed (see "Not finished").
- Step 4 (tariff and prices): drove `PeakTracker` with the catalog rows; drove the coordinator's `_price_series` and `_pv_export_price` from a Nord-Pool-style entity; ran grid-fee folding across both 2026 DST days.
- Step 5 (estimators): not reached.

## Findings

### D2-s2-01 (high, bug): capacity peaks are counted per metering window, not per day
- **Where:** `tariff.PeakTracker` keeps the k highest closed windows in one list, with nothing grouping them by day.
- **What the tariff says:** both catalog rows (Ellevio and Göteborg Energi) bill the mean of the three highest hourly peaks *on three different days*.
- **Consequences:**
  - `billed_peak_kw` is published as a sensor value and is too high.
  - `threshold_kw` is too high. The solver and the live peak guard both price against it, so they treat a costly hour on another day as free.
  - `peak_cost` charges k same-morning windows k times.
- **Harness:** `s2_distinct_day_peaks.py`
  - Headline: tracker 9.80 kW against a true 7.83 kW, so +96.37 SEK/month at 49 SEK/kW. Threshold 9.60 kW against a true 6.50 kW. A 9.0 kW hour on a new day is priced 0 SEK; the bill charges 40.83 SEK.
  - Grid of 8 random months: overbill 1.42 to 34.40 SEK/month, mean 19.11. Leave-one-out (largest cell dropped): 16.93.
  - Plan side: 3.0x overcharge ratio.
- **Perturbation and null control (`--k1`, `peaks_averaged=1`):** every error goes to 0 and the plan ratio to 1.0.

### D2-s2-02 (high, bug): entity prices are read without their unit
- **Where:** `price_model.prices_from_entity_state` and `Coordinator._pv_export_price` both ignore `unit_of_measurement` and `price_in_cents`.
- **Result:** a sensor publishing öre/kWh or SEK/MWh gets into the plan at the wrong scale. The grid fee, capacity tariff and cycling cost stay in SEK/kWh, SEK/kW and SEK.
- **Harness:** `s2_price_unit.py`

| Sensor unit | Planning price vs true SEK/kWh | Export price vs true | Fee share of the price spread |
|---|---|---|---|
| SEK/kWh (null control) | 1.0 | 1.0 | 0.132 (matches the true share) |
| öre/kWh | 83.0x | 100x | 0.0015 |
| SEK/MWh | 828.6x | 1000x | 0.00015 |

- **Perturbation:** change the sensor's unit attribute while keeping the same true price.

## Non-findings
- **Cost and savings identities** (`s2_cost_identity.py`): `predicted_cost == dt·Σ price·(P_space+P_dhw)` (piecewise in PV surplus) and `savings == baseline − predicted − deferred` hold on all 50 golden fixtures. Worst residuals: 1.3e-4 SEK on cost (power is recorded to 1e-3 kW) and 1e-6 SEK on savings. The PV fixtures use export price 0.0.
- **Grid-fee windows across DST** (`s2_fee_dst.py`):
  - A 06:00–22:00 rule charges 64 steps on the 23 h, 25 h and normal days, which is 16 local hours each time.
  - A wrapping 22:00–06:00 rule charges 28, 36 and 32 steps, which are the real 7, 9 and 8 night hours.

## Not finished
- Terminal credit compared with a re-simulated continuation.
- `price_weight` scaling (confirmed by reading the code only, not executed).
- Forward-FD gradient compared with a central FD.
- Estimator bias for `sysid.identify`, and the clamps on the COP and heat-loss learners.
- Horizons that cross a month boundary for the capacity term.

## Schema note
The finding ids follow the task's `D2-s2-NN` form. `finding.schema.json` only accepts ids of the form `D2-NN`, so these two ids fail that one check. Everything else in `report-s2.json` validates.

## Exposure
None. I read only the tree. `README.md` was used once, to confirm that Nord Pool is a supported price source.
