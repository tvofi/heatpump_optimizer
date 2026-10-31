# Round 8 D2 verification (single verifier, D2-v1)

- **Baseline:** `cdf82daabcfe3777d98b31489f36df5555ec9d82`.
- **Tree:** `/home/claude/audit-r8/seats/D2-v1`, a copy tree. The finder evidence from D2-s1 and D2-s2 was copied in with `cp -rn`. No harness hard-codes a seat path, so none needed a rewrite.
- **Environment:** every run used `PYTHONPATH=tests/hastub` with the five BLAS variables set to 1, and `TMPDIR` under `/home/claude/audit-r8/tmp/D2-v1`.
- **Load:** the box was heavily contended. load1 was 23–26 and thread_factor 0.98–1.012. That does not affect any number here: every figure is a deterministic temperature, ratio, count, kWh or SEK, and none is a timing.
- **Production files:** `diff -r` against the export over `custom_components/` and `tests/` is clean.
- **Panel:** this panel has one verifier, by the owner's call. For each finding I re-ran the finder's harness, its perturbation and its null control, measured the finding with a harness of my own, and attacked the method in the order `verifier.md` gives.
- **Shared mechanisms:** none of the four findings shares a mechanism with another. D2-s1-01 and D2-s1-02 both pass through `compute_cop_dhw`, but they are independent:
  - s1-01 is the missing humidity argument.
  - s1-02 is the lift law.
  - Fixing one leaves the other's number unchanged. Under s1-02's `--perturb`, s1-01's null arms stay at 0, and s1-01's mechanism does not involve the penalty at all.

## D2-s1-01: the DHW planner prices COP at the current humidity (medium) — VERIFY

**Finder's harness, re-run.**
- Baseline: `gap_max=4.9717 K`, `gap_min_cell=3.2716`, `gap_drop_most_favourable=4.8884`. Both null controls read 0.0000 (load1 26.41, thread_factor 1.000).
- Perturbation `--ambient-matches`: 0.0000 K in all 6 cells.
- The finder's numbers reproduce exactly.

**Reading the code.**
- `extend_dhw_temps` (`thermal_model.py:1931`) calls `compute_cop_dhw(outdoor[i], temp)` with no humidity, and `simulate_dhw_only` routes through it.
- `_cop_law` then falls back to `params.ambient_humidity`, which `coordinator.py:5398` writes from `_current_humidity()`.
- The published trajectory comes from `simulate_trajectory_with_dhw`, which threads `humidity[i]` (`:3122`, `:3160`).
- The coordinator does pass a forecast humidity series (`coordinator.py:6194`), so the path is reachable in real Home Assistant. It is not an artefact of the test stub.

**My own harness:** `v1_dhw_humidity.py`.
- **Metric:** the physical consequence, measured as max over the horizon of published(ambient = forecast) − published(ambient = 55 %), in K. It compares two published trajectories, rather than the finder's planner-versus-published gap within a single run.
- **Grid:** derate {0.60, 0.85} × forecast {flat 90 %, diurnal 60–95 %} × weather {winter_mild, shoulder}.

| Measure | Result |
|---|---|
| Shortfall, max over the grid | 4.41 K |
| Shortfall, most favourable cell dropped | 3.78 K |
| Shortfall, range over the grid | 0.65–4.41 K |
| Shortfall, the more realistic 0.85 derate | up to 4.41 K |
| Shortfall, diurnal forecast | 0.65–2.85 K |
| Extra DHW electricity the correct plan buys | 0.1–0.8 kWh per cell |
| Reverse arm (current humid 90 %, forecast dry 55 %) | planner over-buys 0.79 kWh; trajectory deviates by 4.38 K |
| Null control, no derate | 0.0000 K |

- The error runs in both directions: an under-heated tank in one case, over-spend in the other.

**Attacks.**
- *Contention:* none. The metric is deterministic.
- *Gate mode:* not applicable.
- *Grid artefact:* no. Both the finder's leave-one-out and mine hold above 3.7 K.
- *Null control:* present, and it passes.
- *Reachability:* reachable in real HA, as shown above.
- *Severity:* the finder's 55 % → 85/95 % flat forecast is the extreme case. A diurnal forecast still gives up to 2.85 K. However, `dhw_min_temp` (45 °C) is crossed by both the correct and the wrong plan in every cell (published minimum 41–42.6 °C). The harm is therefore a few K of tank temperature and tenths of a kWh, not a comfort-floor breach. The plan also re-solves every cycle with fresh humidity.
- Medium ("bounded cost") is earned.

## D2-s1-02: two COP laws for one lift (low) — VERIFY

**Finder's harness, re-run.**
- `ratio_max=1.4548`, 102 of 105 cells above 1.01, `boost_below_ref=1.12`, 1.4286 against 1.2500, null 0.000000.
- `--perturb` gives 1.0000, 0 cells and 1.0000.
- Everything reproduces.

**My own harness:** `v1_cop_laws.py`.
- **Metric:** the DHW law's implied second-law efficiency relative to its own value at 35 °C: `eta_rel = [COP_dhw(o,T)/carnot(T,o)] / [COP_dhw(o,35)/carnot(35,o)]`.
- A physical lift law cannot improve its exergetic efficiency as the lift grows.
- This metric tests the DHW law against physics directly, not against the buffer law.

| Measure | Result |
|---|---|
| `eta_rel_dhw_max` | 1.4548 |
| `eta_rel_dhw_min` | 1.039 |
| Cells with `eta_rel_dhw` > 1.05 | 358 of 364 |
| Buffer law | 1.0000 |
| DHW/buffer ratio at the reachable 55 °C setpoint | 1.352 |
| DHW/buffer ratio at 60 °C | 1.401 |
| `--perturb` | 1.0000 everywhere |
| Null at 35 °C | 0 |

- The buffer law scores 1.0000 by construction: it is the Carnot ratio, and my reference uses the same 7 °C outdoor cap. My number confirms that the DHW law under-prices lift, but it does not independently validate the buffer law.

**Attacks.**
- *Grid artefact:* yes, in the finder's leave-one-out. The ratio does not depend on `cop_nominal`, so the 105 cells are only 39 distinct values: `finder_grid_distinct_cells=39 of 105`. That is why `drop_most_favourable` equals the maximum (1.4548). The leave-one-out is uninformative, but my finer 364-cell grid holds the result.
- *Reachability:* only with `cop_flow_carnot` on (a throttling mixing valve, `thermal_model.py:959`) together with DHW. On other installs the DHW law is the only lift law, and the claim reduces to "the DHW penalty is too shallow at high tank temperatures".
- *Consistency:* plan and physics use the same `compute_cop_dhw`, so this is a model-accuracy question, not a plan-versus-physics split.
- *Severity:* low stands.

## D2-s2-01: capacity peaks tracked per window, not per day (high) — VERIFY

**Finder's harness, re-run.**
- Baseline: `headline_overbill_sek=96.3667`, threshold 9.60 against 6.50, `free_hour` 0 against 40.83 SEK, grid 1.421–34.401 SEK/month (mean 19.114, leave-one-out 16.930, 8 of 8 cells non-zero), plan ratio 3.0.
- `--k1`: every figure goes to 0, and the plan ratio to 1.0.
- Everything reproduces exactly.

**Reading the code.**
- `PeakTracker._close_window` (`tariff.py:285`) appends every closed window to one sorted list, with no key by day.
- `billed_peak_kw` and `threshold_kw` read that list.
- The catalog row's own source comment quotes the rule "medelvärdet av de tre högsta topparna fördelat på tre olika dygn" (`grid_fee.py:420-421`, and `:405` for Ellevio). The code contradicts the rule it cites.

**My own harness:** `v1_peak_days.py`.
- **Metric:** a solver-facing measure, hour by hour through the month. For each hour, the SEK by which the distinct-day bill rises across hours where `PeakTracker.threshold_kw`, read before the hour, says "free" while the same threshold rule applied to per-day maxima does not.
- **Grid:** 20 seeded 31-day months.

| Arm | Hidden SEK/month (median) | Range | Leave-one-out mean | Other |
|---|---|---|---|---|
| Baseline | 76.66 | 40.35–146.74 | 77.98 | 20 of 20 months non-zero; median 9.5 hidden hours |
| Null, no cold snaps (one peak per day, morning and evening bumps only) | 21.37 | 10.8–56.2 | — | billed error at end of month is only 0.08 SEK median |
| Perturbation `--k1` | 0.52 | max 14.5 | — | — |

- The no-snaps arm shows that ordinary same-day morning and evening double peaks already mislead the solver, even though the end-of-month billed error almost disappears.
- The `--k1` residual is my harness's own one-hour window-close lag: the tracker closes an hour's window only on the next hour's first sample. It is not the finding.
- The end-of-month billed error reproduces the finder's picture: median 14.6 SEK and max 53.2 SEK.
- The hidden-SEK figure is an upper bound on the planner's exposure. It counts whole-house load, and the pump is only part of that.

**Attacks.**
- *Contention:* none. The metric is deterministic.
- *Grid artefact:* no. The leave-one-out holds.
- *Null control:* present, and it moves as expected.
- *Reachability:* the tracker is fed by the coordinator in real HA. Only the Göteborg Energi row is in force; the Ellevio row is historical. A user-entered k>1 tariff for a DSO that bills top hours regardless of day would be correct as coded.
- *Severity:* high. `billed_peak_kw` is a wrong published value, and the threshold under-prices hours the bill charges.
- One further point: `peak_cost`'s 3× same-day over-charge sits on the conservative side, and its docstring (`tariff.py:729-734`) already concedes it is an upper bound. That sub-claim alone would be low.

## D2-s2-02: entity prices read unit-blind (high) — VERIFY

**Finder's harness, re-run.**
- Import ratios 1.0000, 83.0147 and 828.6029. Export ratios 1, 100 and 1000. Fee share 0.13228, 0.00152 and 0.00015.
- The perturbation is the unit arm itself, and the SEK/kWh null reads exactly 1.
- Everything reproduces.

**Reading the code.**
- `prices_from_entity_attributes` and `prices_from_entity_state` (`price_model.py:686-730`) never read `unit_of_measurement` or `price_in_cents`.
- The configured `surcharge` (SEK) is added to the raw value unscaled.

**My own harness:** `v1_price_unit.py`.

*(a) The lower parse seam, measured directly.* Ratio of the row `total` to the true SEK/kWh with a 0.10 SEK surcharge:

| Unit | Ratio |
|---|---|
| SEK/kWh | 1.0000 |
| öre/kWh | 92.08 |
| SEK/MWh | 920.12 |

The figures differ from the finder's 83.0 and 828.6 only because the SEK additive terms (my surcharge; their grid fee) enter at different magnitudes. The mechanism is the same.

*(b) Plan consequence.* I ran `optimize` on `golden.make` with prices ×100 against ×1:

| Weather | Arm | Effect of ×100 |
|---|---|---|
| winter_cold | with or without a fee step | plan identical; capacity-bound, 41.167 kWh in both |
| winter_mild | with fee | plan buys +5.43 kWh (+17 %) |
| winter_mild | pure ×100, no SEK term at all | +5.72 kWh |
| shoulder | with fee | +2.03 kWh; compressor starts 8 → 7 |

- The published `predicted_cost` is 100.000× in every arm.

**Attacks.**
- *Mechanism:* the plan damage does not rest mainly on the finder's stated mechanism, the fee losing weight. A pure ×100 scale with no additive SEK term moves the plan by the same +5.7 kWh. So the objective is not scale-invariant in price: comfort and other non-currency terms are re-weighted. The finder's fee-share numbers are correct as ratios, but the larger plan consequence runs through the price-versus-comfort balance. This strengthens the finding.
- *Reachability:* real. The HACS Nord Pool integration offers `price_in_cents` and a MWh price type, and the README and config text invite "Nord Pool or similar" sensors with no unit guidance.
- *Workaround:* the VAT multiplier (`config_flow.py:1509`, range 0–2, step 0.01) could scale an öre sensor by 0.01. That does not cover 25 % VAT exactly (0.0125 is off the step), it cannot express 1/1000, and it does not touch the export seam or the surcharge.
- *Severity:* high (a wrong published value, plus silently changed plans) stands.

## Harnesses (mine)

All four are under `tools/audit/round8/D2/`:
- `v1_dhw_humidity.py`
- `v1_cop_laws.py` (supports `--perturb`)
- `v1_peak_days.py` (supports `--k1` and `--no-snaps`)
- `v1_price_unit.py`
