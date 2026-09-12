# D2 round 4 — verifier report, seat 1 of 3 (verify-0-1)

- **Worktree** `/Users/timmalmstrom/.zcode/workspace/default/audit-r4-verify-D2-1`,
  detached at `0855277` (branch head of `claude/13-dimension-audit-920935`).
- **Production code vs finder baseline**: `git diff --stat 7dd68dd..HEAD --
  custom_components/` = `manifest.json` and `www/heatpump-optimizer-card.js`
  only, both pure version bumps (6.4.2 → 6.4.3). Every Python module the
  findings touch is byte-identical to the baseline the finder measured.
- **Interpreter** `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`,
  every run from the worktree root with `PYTHONPATH=tests/hastub` and the
  five-variable BLAS pin. Harnesses copied into this tree before running
  (root rule `os.getcwd()`; nothing resolves from `__file__`) per the
  README's worktree-root warning.
- **Conditions**: `thread_factor` 0.9948–1.0056 on every run (contract
  ≤ 1.05); `load1` 2.9–10.2 quoted per harness (other panels were running;
  per the brief, load1 is quoted, not gated). **No number below is a timing
  or memory figure** — every RESULT is a count, a ratio, or a closed-form
  float identity, so none is provisional on a quiet box.

## Method

Per finding: (1) re-ran the finder's harness exactly as its header says and
diffed against the committed `.out`; (2) wrote my own harness
(`d2_own_D2-0n.py`, beside the finder's, with its own metric definition)
and measured independently; (3) attacked the method — flat-plan corner,
grid artefacts, wrong entry path, config-flow reachability, null controls.
`identities.py` was also re-run: every held identity reproduces
(`dt.worst_24h` 0.01128163367 °C, `coil` 5.55e-17 kW, `cost.no_pv_error`
0, `window.*` 0), which is what makes the finder's null-control machinery
trustworthy.

## Re-runs of the finder's harnesses (all five)

Every RESULT line matches the committed `.out` **bitwise** except the
run-condition lines (`thread_factor`, `load1`, `swapins`), as expected:

| harness | key RESULTs (mine, load1) |
|---|---|
| peak_topk_bracket.py | ratio_worst 5.083811356; break_excess_kw_1pc 5.841609022; cells_over_1pc 16/28; cell_ratio_max 13.35094575; loo_worst 2.514813011; phantom_sek_12kw 3981.716072; perturbed 1.00000032 / 0 (load1 3.12) |
| catalog_masks.py | 4 rows, 0 writing offpeak_factor; discounted_windows 0/672 ×4; declared 432/432/412/432; july nulls [0.]×3/[1.]; phantom_peak_sek 406.2499554; perturbed 432/432/412/432 & 0 (load1 3.03) |
| wood_share_jump.py | share_jump_worst 0.9985011774; wood_energy_jump_kwh −0.6416654667 (99.18 %); traj_power_gap 2.775557562e-17 kW; traj_wood_jump −1.110059838; perturbed 0.000998 / 7.33e-07 (load1 3.03) |
| cop_below_unity.py | space 51/328 below unity, min 0.7195446773 at −21/70, loo 44; dhw 23/205, min 0.84, loo 19; crossings −19.915/−18.236/−16.521/−19.395; invert drops 2.10/3.64/4.83/5.33 %; marginal 0.7384800635 / 0.84; nulls 1.05 / 1.05 / 0.0; perturbed ladder 51→28→11→2→0 (load1 2.93) |
| grid_fee_decimal_comma.py | 6/6 rejected; 6/6 dotted ok; unit 0.45; fragment 0.0; schedule 0 rules / 0.0 fee; perturbed 0 / 0.27 (load1 2.93) |

One documentation nit, not a number: `wood_share_jump.py`'s EXPECTED block
says `share_jump_worst = 0.9995` while the measured (and FINDER.md-tabled)
value is 0.9985 — the header quotes the region-3 side alone; the measured
jump subtracts the region-2 side (~0.001 at that offset). The report and
`.out` agree with each other; only the header line is off.

## D2-01 — bracket not scaled by its own logistic temperature — **verify (high)**

**Own harness** `d2_own_D2-01.py` (own metric: the multiplier
`_smooth_topk_sum(x,k,τ)/(k·peak)` driven DIRECTLY, bypassing
`peak_cost`/`metering_windows` entirely, cross-checked against the
bracket-exit closed form `n·sigmoid(−1/scale)·peak`):

- `own_multiplier_12kw = 5.083811356` — the same number the finder
  measured through the full `peak_cost` plumbing, reproduced through a
  second entry path.
- `own_closedform_maxrel_outside_cells = 3.73e-16` over all 16 cells whose
  analytic root `peak + scale·ln((n−k)/k)` lies outside `[min−1, peak+1]`:
  production's smooth sum equals the bracket-exit prediction to float
  precision. Mechanism proven, not correlated.
- The 16 root-outside cells are exactly the 16 cells with multiplier
  > 1.01 — the analytic map and the measured overstatement agree cell for
  cell.
- Null: `own_multiplier_5kw = 1.000000062` (root inside the bracket →
  exact). Perturbation (bracket widened by 40·scale):
  `own_perturbed_multiplier_12kw = 0.9999997154`.
- Money through the Ellevio row: charged 4956.716072 vs billed 975.0 →
  phantom 3981.716072 SEK at 12 kW — identical to the finder's figure.

**Attacks run**

1. *Perfectly flat plan is an unphysical corner* — defeated: a plateau with
   ±5e-4 kW jitter (inside `_PEAK_TIE_BAND`, so production still counts
   96 windows at the peak and takes the smooth branch) still overstates at
   5.0805x; a 40-of-96-window plateau over the same peak overstates at
   2.1170x. The effect needs a plateau, not exact equality.
2. *Is the term wired the way the harness drives it?* Yes:
   `optimizer.py:2109` calls `peak_cost` in the objective's `capacity`
   closure with `cfg.peak_price_per_kw`, which `coordinator.py:4411` sets
   to `tariff.marginal_price_per_kw` — exactly the price the harness
   passed, so the SEK figures are scaled as production scales them.
3. *Reachability of the worst swept cell* — **the one real weakness**:
   the 13.35x cell is 192 fifteen-minute windows = a 48-hour horizon.
   `OptimizationConfig.from_mapping` (`optimizer.py:1093–1138`) reads no
   horizon key, so `horizon_hours` stays the 24 h default and
   `n_steps = min(len(prices), len(outdoor), config.n_steps)` caps at 96.
   No write of `horizon_hours` exists anywhere in production. The finder's
   "(24, 48, 96, 192) … the horizons this optimizer actually plans" is
   wrong for the 48 h half. Production-reachable worst at the shipped
   catalog settings (15-min windows, k=3, 24 h): **5.0838x at 12 kW,
   6.6755x at 15 kW, 8.6061x at 20 kW** excess (the multiplier is
   unbounded in excess); hourly metering breaks at ~10.3 kW exactly as
   reported. The defect, break point (5.8416 kW), catalog-row numbers,
   money, nulls and perturbation are all exact, so this weakens one
   headline sweep number, not the finding or its severity.

**Vote: verify, high.** The capacity term the solver minimises is inflated
several-fold precisely on the flat plateaus a capacity tariff exists to
produce, at the shipped catalog settings, early in a month when
`PeakTracker.threshold_kw` is the lowest peak seen.

## D2-02 — hours/weekday masks inert for every catalog row — **verify (medium)**

**Own harness** `d2_own_D2-02.py` (own metric: count of 15-minute slots in
a billed week where `CapacityTariff.sample_factor` — the symbol
`PeakTracker.observe` calls per window, a different path from the finder's
`window_factors` — returns < 1.0; counted over MY OWN weeks: a November and
a March Monday-start week, both inside the Nov–Mar rows' billed months):

- `own_ellevio_discounted_nov = 0`, `own_ellevio_discounted_mar = 0` of
  672 — inert in both billed months, not just the finder's January week.
- Declared off-peak instants sample at full rate: Saturday 20:00 → 1.0,
  Wednesday 03:00 → 1.0.
- The objective's own path: `_peak_window_factors` (the builder
  `optimizer.py:2140–2147` feeds `peak_cost`) returns a real factors array
  with **0** entries below 1.0 — the mask is configured, live as an array,
  and discounts nothing.
- Null control: the month mask written by the same `apply_catalog` call is
  alive — July samples 672/672 slots at 0.0 under the Nov–Mar rows.
- Perturbation (one key, `CONF_PEAK_TARIFF_OFFPEAK_FACTOR: 0.0`):
  discounted 0 → 432, Saturday factor 1.0 → 0.0.

**Attacks run** — reachability end to end: `grid_fee.apply_catalog`
(`grid_fee.py:456–466`) writes `CONF_PEAK_TARIFF_HOURS` and
`CONF_PEAK_TARIFF_WEEKDAYS_ONLY` and not the factor;
`coordinator._capacity_tariff` (`coordinator.py:7217–7220`) defaults it to
1.0; `tariff.mask_active` (`tariff.py:404–409`) gates the hours/weekday
masks on `offpeak_factor < 1.0`; `coordinator.py:4428` propagates the same
1.0 into the optimizer config. The contradiction (a shipped config that
declares a mask the code proves cannot change any window) is measured at
every layer. The finder claims the internal contradiction, not a reading
of any DSO's published tariff — the correct claim for this evidence.

**Vote: verify, medium.**

## D2-03 — `wood_share` discontinuous where its docstring claims continuity — **verify (high)**

**Own harness** `d2_own_D2-03.py` (own metric: the share jump at a SECOND
configuration — my own outdoor temperature −15 °C giving
`flow_set = 27.8857 °C` from the production `mixing_valve.flow_setpoint`,
vs the finder's 26.6 at −5 — over a dense 400-point sweep of the band,
with the one-sided limits cross-checked analytically, and the solver's own
variable moved by `numpy.nextafter`):

- All **400 of 400** offsets in `(0, margin)` jump; `own_jump_max =
  0.99994`; the production jump equals the analytic form
  `1 − o/margin − δ/(o+δ)` to 3.5e-10 relative.
- Nulls: at the margin −3.5e-10 (probe residue), at 1.25·margin −2.5e-10,
  wood above the curve exactly 0.
- Direction is backwards against the documented wood-while-usable law:
  raising the HP tank across the curve DROPS the wood share
  (`own_direction_backward = 1`).
- The batched twin carries it (`own_jump_vec_at_0.25C = 0.875`), so the
  finite-difference gradient sees it too — the "one ulp" framing is not
  the only route.
- Solver's own decision variable: the adjacent-float power pair straddling
  the buffer crossing (gap 5.5511e-17 kW = one ulp) moves the wood tank's
  step-1 enthalpy change from −1.2353 kWh to −0.0070 kWh —
  `own_adjacent_jump_kwh = −1.2283` at my configuration (finder: −1.1101
  at his). A `nextafter` step wholly above the crossing moves nothing
  (`own_nextafter_jump_kwh = 0`), which is the correct null for the
  contrast construction.
- Perturbation (region 3 faded at the boundary): max jump falls to
  1.0e-5 — the 2e-9 probe's own residue.
- `own_optimizer_imports_wood_share = 1`: the savings baseline
  (`optimizer.py:6088`) imports the identical symbol, so the reported wood
  displacement jumps with it, as the finding claims.

**Attacks run** — the docstring itself states "Three regions, continuous
in `w * Q_draw` across every boundary" (`thermal_model.py:1132–1133`);
region 2 → 0 at the boundary while region 3 → `1 − (flow_set −
wood)/margin`, measured to match the analytic form. The topology
(`two_tank_4way`) is the configuration's own `topology_layout` for
two-zone + manual valve + wood probe; an HP tank crossing the curve is the
ordinary charging cycle.

**Vote: verify, high.** A kWh-scale discontinuity in the variable
L-BFGS-B differentiates, on a supported topology, contradicting the law's
own contract, propagating to the reported savings.

## D2-04 — COP below 1.0 and inverted in the deep cold — **verify (medium)**

**Own harness** `d2_own_D2-04.py` (own metric: production `compute_cop`
cross-checked against MY OWN closed-form reading of its source at 2000
uniform-random points, then re-gridded at 0.5 °C, the inversion counted by
derivative sign):

- `own_formula_maxrel = 0` — my independent closed form
  (nameplate·min(max(0.3, 1+0.025ΔT), 1.5) · Carnot flow ratio · final
  clamp 0.5) reproduces production exactly at 2000 random points. The
  mechanism is precisely the post-floor corrections.
- Random points: min 0.7203, **278 of 2000** below unity — the sub-unity
  region is ~14 % of the envelope, not a corner.
- My finer grid (0.5 °C): 880 of 5751 below unity, min 0.7195446773 at
  outdoor −21 / flow 70 — the same minimum cell as the finder's coarse
  grid. Robust to dropping the coldest outdoor column (817) and the
  hottest flow row (861): not a grid artefact.
- DHW: min 0.84, 214 of 1701 below unity; at the penalty's own 35 °C
  reference the min is exactly 1.05 (null).
- Inversion: 380 negative-derivative steps at 0.05 °C resolution, band
  −40…−21 °C at flow 70 (19 °C wide); COP falls 0.7600 → 0.7195 as outdoor
  rises −30 → −21.
- The money symbol: `marginal_cop(−21, "buffer", 70) = 0.7195`,
  `(−25, "buffer", 70) = 0.7385`, `(−25, "dhw", 60) = 0.84`.
- Null: valve mode "none" (no Carnot term) → min exactly 1.05, zero cells
  below unity, monotone (worst step 0.0). Perturbation (`max(cop, 0.5)` →
  `max(cop, 1.0)`): min rises to exactly 1.0, zero cells below unity.

**Attacks run** — reachability: `cop_flow_carnot` is set from
`mixing_valve.is_throttling(mode)` in `from_config`
(`thermal_model.py:916`), so every valved install has it on;
`buffer_max_temp` (70 default) and `dhw_hard_max_temp` (60) are read from
the params, not assumed; and `optimizer.py:5877`
(`_buffer_charge_ceiling`) feeds `marginal_cop(out_mean, "buffer",
store_temp=temp)` with temp bisected over [35, `buffer_max_temp`] while
`_terminal_cost` (line 1714) prices the tank at the same symbol — the
sub-unity COP reaches the objective's settlement and terminal terms, not
only the simulation. The code's own comment at `thermal_model.py:1380–83`
shows the authors already found and capped the ABOVE-reference inversion
(#776); the deep-cold band below −21 °C is the un-capped remainder.

**Vote: verify, medium.**

## D2-05 — decimal-comma rate support unreachable — **verify (low)**

**Own harness** `d2_own_D2-05.py` (own metric: my own 7-spec corpus —
different strings from the finder's, including Swedish lowercase months,
Swedish weekdays, a wrap-around night window, and mixed separators — plus
unreachability MEASURED by instrumenting `_parse_rule` to record every
rate token it is handed):

- 7 of 7 comma specs rejected; 7 of 7 dotted equivalents accepted (null).
- `own_tokens_containing_comma = 0` of 14 tokens seen: while parsing the
  whole comma corpus, `_parse_rule` never once received a token containing
  a comma. The `replace(",", ".")` at `grid_fee.py:161` is dead code,
  proven by execution, not by reading. Grep confirms `_parse_rule` has
  exactly one caller — `parse_rules` at `grid_fee.py:206`, after the
  comma split — so no other route exists.
- `_parse_rule("= 0,45")` alone → rate 0.45 (dead code proven functional
  in isolation); the first fragment of a split rate parses to a SILENT
  0.0.
- A rejected spec degrades through `GridFeeSchedule.from_config` to 0
  rules and a 0.0 SEK/kWh fee at both a January and a July timestamp,
  with only a log line.
- Perturbation (split on ";" and newline only): 0 of 7 rejected, fee
  0.40.

Two of my corpus strings initially failed for MY grammar errors
(`"lon"` for Saturday; a weekday inside a time window) and were corrected
— the module's grammar, not the comma, was at fault there, which is
itself evidence the null control discriminates.

**Vote: verify, low.**

## Votes

| id | vote | severity |
|---|---|---|
| D2-01 | verify | high |
| D2-02 | verify | medium |
| D2-03 | verify | high |
| D2-04 | verify | medium |
| D2-05 | verify | low |

The single material caveat in this round: D2-01's 13.35x headline cell
(192 windows) requires a 48 h horizon that `OptimizationConfig.from_mapping`
cannot produce — the production-reachable maximum at the shipped catalog
settings is 5.08x at 12 kW excess, unbounded in excess (8.61x at 20 kW).
Everything else in the finding, including the 5.8416 kW break point and
the 3981.72 SEK phantom at 12 kW, reproduces exactly through two
independent harnesses.
