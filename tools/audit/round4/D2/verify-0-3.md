# Verifier 3 report — panel D2-0, audit round 4

- **Tree** worktree `../audit-r4-verify-D2-3` at `0855277` (branch head;
  findings measured at baseline `7dd68dd`). My five own harnesses are
  `verify03_d2_0{1..5}.py` next to the finder's, same run rule
  (`PYTHONPATH=tests/hastub`, five-variable thread pin, from the tree root).
- **Nature of the numbers.** Every metric in this panel is a count, a ratio,
  or a closed-form float identity. No timing or memory figure is load-bearing
  anywhere below, so the fan-out load does not touch any verdict. `load1`
  4.4–11.6 across my runs (quoted, ungated by rule); `thread_factor`
  0.979–1.021 on every run (gate 1.05).
- **Exposure** none: I read `briefs/verifier.md`, `README.md`, the D2 finder
  report and harnesses only. No register, no other verifier's output.

Re-run table (finder's harnesses, exact header commands, my box, `concurrent_processes = 2` on every run):

| harness | outcome |
|---|---|
| `peak_topk_bracket.py` | every RESULT matches the finder bit-for-bit: `ratio_catalog_6kw=1.102246261`, `ratio_catalog_9kw=3.128723195`, `ratio_worst=5.083811356`, `ratio_null_flat_5kw=1.000000062`, `ratio_null_hourly_8kw=0.9999997334`, `ratio_null_spiky_12kw=1`, `break_excess_kw_1pc=5.841609022`, `cells_over_1pc=16` of 28, `cell_ratio_max=13.35094575`, `loo_worst=2.514813011`, `phantom_sek_12kw=3981.716072`, `perturbed_ratio_worst=1.00000032`, `perturbed_cells_over_1pc=0` |
| `catalog_masks.py` | matches: 4 rows, `rows_writing_offpeak_factor=0`, `discounted_windows=0` of 672 ×4, declared 432/432/412/432, `july_factor_unique=[0.]/[0.]/[0.]/[1.]`, `phantom_peak_sek=406.2499554`, perturbed 432/432/412/432 and 0 SEK |
| `wood_share_jump.py` | matches: jumps 0.9985011774 → … → 0.0004996783, null at 2.0 °C `−3.21428411e-07`, null above 0, `wood_energy_jump_kwh=−0.6416654667` (99.18 % of the discharge), `traj_power_gap_kw=2.775557562e-17`, `traj_wood_jump_kwh=−1.110059838`, `perturbed_share_jump_worst=0.000998322857`, `perturbed_wood_energy_jump_kwh=7.33e-07` |
| `cop_below_unity.py` | matches: `space.cells_below_unity=51` of 328 (loo 44), `min_cop=0.7195446773` at −21/70, crossings −19.91/−18.24/−16.52, DHW 23 of 205 (loo 19), `dhw.min_cop=0.84`, crossing −19.39 at setpoint 55, inversion drops 2.10/3.64/4.83/5.33 %, nulls 1.05/0 cells, perturbation ladder 51→28→11→2→0 |
| `grid_fee_decimal_comma.py` | matches: 6 of 6 rejected, 6 of 6 dotted OK, `unit_accepts_comma=1` (`rate=0.45`), `first_fragment_rate=0`, `schedule_rules_after_reject=0`, `schedule_fee_after_reject=0.0`, perturbed 0 rejected / 0.27 |
| `identities.py` (cited under D2-01) | reproduces the committed `identities.out` (conservation −1.30e-13 kWh, COP monotone 0.0, Euler 0.0113 °C, PV-piecewise 2.13e-14 SEK, etc.) — the non-findings table holds on this tree |

## D2-01 — capacity-tariff penalty overstates the bill (high) — **verify**

**My own number** (`verify03_d2_01.py`; metric: `peak_cost(production-shaped
plan) / (marginal_price × exact top-k)` where the plan is driven the way
production drives it — constant per-step baseline, since
`coordinator._baseline_house_load` returns `np.full(n_steps, baseline)` —
window length from the shipped catalog rows):

- `v3_analytic_break_kw_n96 = 5.824133524` kW — my closed form
  `1/(tau·ln((n−k)/k))` for the excess where the logistic root
  `peak + scale·ln((n−k)/k)` leaves the fixed ±1.0 bracket. The finder's
  measured `5.8416` (1 % gate) sits just above the analytic onset, as it
  must. n=24 gives 10.278 kW — the finder's "~10.3 kW at hourly metering".
- Production-shaped saturated plan at the default 24 h horizon
  (n=96, 15-min windows): ratios 1.0000003 / 1.102246261 / 3.128723195 /
  5.083811356 at 4/6/9/12 kW flat excess — identical to the finder's
  `np.full` drive, which is the point of the next attack.
- Flat-vs-spiky at the **same billed top-k** (3 windows at 12 kW + 93 at
  11 kW): charged 2745.258 vs 540.000 SEK — `v3_flat_over_spiky = 5.0838`.
  The reward-inversion consequence is a measured number, not prose.
- Wide-bracket perturbation applied to the live module:
  `v3_ratio_saturated_12kw_widebracket = 0.9999997154`.
- Reachable-horizon aggregate (my one-liner): at n=96 over excess
  2–15 kW, 6 of 9 cells over 1 %, max 6.675 at 15 kW.

**Attacks and outcomes.**

1. *Is the flat plateau an `np.full` artefact?* No. Production's baseline is
   itself `np.full` (coordinator.py:8507), so a plan pinned at `p_max`
   produces exactly tied windows. With uniform jitter inside the tie band
   (`±5e-4`, `±9e-4` kW) the ratio stays 5.08 with 96 and 52 windows
   counted at peak — the smooth branch fires on any ≥4-window tie within
   `_PEAK_TIE_BAND` (1e-3 kW), not on exact equality.
2. *Does a bumpy house load dodge it?* Yes — a per-step baseline varying
   ±0.2 kW leaves only 2 windows within the band and the exact branch runs
   (ratio 1.0). The defect needs the plateau, which the saturated-cold-snap
   plan produces. This bounds reachability, it does not refute: the branch
   is the plan shape a capacity tariff is supposed to create.
3. *Aggregate artefact.* The 13.35x headline cell (192 windows, 15 kW)
   needs a 48 h horizon; `OptConfig.horizon_hours` defaults to 24.0 and
   nothing in options changes it, so the production ceiling is n=96: 5.08x
   at 12 kW, 6.68x at 15 kW, break 5.84 kW (all four catalog rows write
   15-minute windows — `v3_catalog_all_15min=1`). The finder's own quoted
   `ratio_worst` (5.08) and every money figure already use n=96, so the
   finding's substance is the reachable number; only the grid-sweep max is
   not. LOO (2.515) already shows the aggregate is not one-cell.
4. *Null controls.* Reproduced: exact below the break (1.000000062 at 5 kW,
   0.99999973 hourly at 8 kW) and exactly 1.0 for a spiky plan at 12 kW —
   the effect is the bracket, not the top-k sum. The existing suite's only
   tie test (`tests/features.py:1277`, n=5, tie at 20, k=3) sits below the
   break point, which is why the gate never caught it.
5. *Severity.* The objective's capacity term is overstated up to ~5–6.7x at
   the reachable horizon, 3981.72 SEK phantom against a 975 SEK bill at
   12 kW, and the term measurably prefers a spiky profile over the flat one
   at identical bill. High stands.

**Vote: verify, high.** One noted weakness: the headline "13.35x" is a
sweep cell the 24 h horizon cannot reach; the reachable max is 6.68x. The
finding's own quoted numbers are the reachable ones.

## D2-02 — every DSO catalog row writes two provably inert masks (medium) — **verify**

**My own number** (`verify03_d2_02.py`; metric: over a full 365-day year at
15-minute resolution, count windows whose `CapacityTariff.sample_factor` is
below 1.0 under the exact config the options flow stores after a catalog
selection — `config_flow.py:2917`'s `cleaned.update(apply_catalog(...))`
path — vs the count the row's own hours/weekday mask declares off-peak):

- Three Nov–Mar rows: `v3_discounted_year = 5136`, all of them
  `zeroed_by_monthmask_year = 5136` — every discount in the whole year
  comes from the month mask; the hours/weekday mask discounts nothing
  against `declared_masked_year = 5628`.
- Göteborg Energi (Jan–Dec): **0 discounted windows year-round** despite
  5628 declared off-peak — on this row all three masks are inert.
- A 5 kW excess living entirely inside the declared off-peak
  (Sat 22:00–Sun 06:00, Nov): charged `v3_ellevio_night_excess_charged_sek
  = 406.2500397` at `night_factor_unique = [1.]`.

**Attacks and outcomes.**

1. *Aggregate artefact (0 of 672).* Not an artefact: with
   `offpeak_factor = 1.0`, `sample_factor` returns exactly 1.0 for an
   off-peak window (`min(1.0, max(0.0, 1.0))`) — no week, month, or year
   choice can produce a discount. My year-long re-aggregation says the same
   thing at 35040 windows.
2. *Null control.* Reproduced: the month mask, written by the same
   `apply_catalog` call, moves the factor (July `[0.]` for Nov–Mar rows).
   The metric can tell an inert mask from a live one.
3. *Reachability in real HA.* Confirmed end to end: the options `grid_fees`
   step applies `apply_catalog`'s dict into the stored config; the "grid"
   page shows the hours/weekdays fields; `CONF_PEAK_TARIFF_OFFPEAK_FACTOR`
   is a slider there too — but it defaults to 1.0 and the catalog never
   writes it, so the shipped path is silently inert. (A user who knows the
   slider matters can repair it; that bounds severity, it does not erase
   the internal contradiction.)
4. *Perturbation.* Reproduced through the real builder: adding the factor
   (0.0) lifts discounted windows to 432/432/412/432 and drops the
   Saturday-night charge to 0.00.
5. *Header discrepancy, noted.* The harness header says E.ON declares 408
   off-peak windows; the run (and `FINDER.md`, and 103 h × 4 arithmetic)
   say 412. Stale header value only; measured, report, and code agree.

**Vote: verify, medium.** The plan defends night and weekend peaks at the
full rate on every catalog install, silently; medium is earned and not more.

## D2-03 — `wood_share` discontinuous where its docstring claims continuity (high) — **verify**

**My own number** (`verify03_d2_03.py`; metric: my own probe at
eps = 1e-9 °C across the curve, compared with the closed form
`1 − d/margin` — region 3's limit minus region 2's limit 0 — plus the
production finite-difference slope of the wood tank's enthalpy at the
crossing):

- Jumps 0.995 / 0.95 / 0.75 / 0.5 / 0.25 / 0.05 at wood-tank offsets
  0.01 / 0.1 / 0.5 / 1.0 / 1.5 / 1.9 °C below the curve; worst deviation
  from the closed form 9.98e-08. Nulls: at the full margin −3.2e-10, above
  the curve 0 exactly.
- **The objective's own gradient**: with the production FD step
  (1e-4 kW, the L-BFGS-B 2-point abs step `tariff.py:489` documents), the
  wood-enthalpy slope at the crossing power is 3162.67 kWh/kWh against
  −2.49 kWh/kWh 0.1 kW above and 0 below — a 1269x spurious spike, and the
  FD jump across the two probe points is 0.633 kWh. This is the solver's
  own finite difference, not a diagnostic.

**Attacks and outcomes.**

1. *Header expectation off by its own tolerance.* The header promises
   `share_jump_worst = 0.9995 ± 1e-9`; the run (and the finder's report)
   say 0.9985. I re-derived it: region 2 just above the boundary is
   `f_w·useful/span ≈ 1e-3` at the finder's 1e-6 probe distance with wood
   only 0.001 below the curve, so the probe measures 0.9995 − 0.001 =
   0.99850 exactly. The header's expectation neglected the probe's own
   residue; the reported number is right and my probe (1e-9, residue 1e-7)
   converges to the closed form. Evidence, not a verdict.
2. *Aggregate artefact.* 13 of 13 sweep cells nonzero, LOO mean 0.452; my
   own 6-cell sweep matches the closed form everywhere. The jump exists
   across the whole (0, margin) band, not at one point.
3. *Reachability in real HA.* The topology is options-derived, not
   fabricated: `two_zone` via the zones selector, `mixing_valve_mode`
   "manual" via the valve selector, the wood tank via the wood-probe
   entity fields (gated on wood fuel on); `topology_layout` then derives
   `two_tank_4way`. The law is live at three production sites
   (`optimizer.py:6088` savings baseline, `thermal_model.py:2043` scalar
   step, `:2608` the batched twin the solver differentiates), and the HP
   tank crossing the curve temperature is the ordinary charge cycle. The
   one-ulp demonstration is a limiting case, but the 1e-4 kW FD spike
   shows the cliff at production step size.
4. *Direction.* Confirmed backwards against the docstring's priority law:
   the wood share falls (to 0) because the HP tank got hotter across the
   curve.
5. *Nulls and perturbation.* Reproduced exactly (above), including the
   fade-out perturbation landing at 0.000998 / 7.3e-07 kWh.

**Vote: verify, high.** A documented-continuous law that jumps by up to the
full emitter draw, shared verbatim with the savings baseline, with a
measured 1269x gradient spike in the solver's own finite difference on an
options-reachable topology.

## D2-04 — modelled COP below 1.0 and inverting (medium) — **verify**

**My own number** (`verify03_d2_04.py`; metric: cells below unity on my own
grid — outdoor −30…−10 °C at 1 °C × tank 40…70 °C at 5 °C, the charging
envelope a valved install actually sweeps — through `marginal_cop`, the
settlement symbol, with `ThermalParameters.from_config` so `cop_flow_carnot`
is derived the way every real install gets it):

- 71 of 126 cells below unity; warmest outdoor cell −17 °C; coolest tank
  40 °C; min 0.7503. Dropping the 70 °C column changes nothing (my grid
  tops at 65); restricted to outdoor ≥ −25 (a real Swedish cold snap):
  41 cells.
- DHW at the factory setpoint 55: 11 of 21 outdoor cells below unity, min
  0.882, warmest −20 °C; at 60: 12 cells, min 0.84, warmest −19 °C.
- Inversion slice at tank 55: COP 0.8551 at −30, 0.8386 at −25, 0.8883 at
  −20 — falls as weather warms within the floored band (outdoor ≤ −21),
  rises again above it, exactly the finder's band claim.
- Null: unvalved install min 1.05 over the whole grid.

**Attacks and outcomes.**

1. *Construction trap I hit myself.* My first run used the bare
   `ThermalParameters(mixing_valve_mode="manual")` and got
   `cop_flow_carnot = 0` — the bare constructor's default is False;
   `from_config` derives it from `is_throttling(mode)`
   (thermal_model.py:916). Through `from_config` (the only way a real
   install reaches the code) the finding's premise holds: every throttling
   valve mode turns the Carnot factor on.
2. *Aggregate artefact.* 51-of-328 LOO is 44; my concentrated grid says 71
   of 126 and my no-70 °C-column re-aggregate is unchanged. The unity
   crossings at flow 45/55 (−19.9/−18.2 °C) are inside the ordinary
   radiator envelope, so no re-aggregation removes the effect.
3. *Reachability.* `simulate_step` charges the tank at
   `compute_cop(outdoor, flow_temp=tank_temp if throttled)`
   (thermal_model.py:1904) with the tank sweeping toward
   `DEFAULT_BUFFER_MAX_TEMP = 70`; `compute_cop_dhw` has no gate at all and
   `DEFAULT_DHW_SETPOINT = 55`. Outdoor −17…−21 °C is deep but real in
   Sweden; the DHW half needs no valve.
4. *Money path.* Confirmed: `_terminal_cost` prices stored buffer heat at
   `marginal_cop(out_mean, "buffer", store_temp=caps["buffer"])`
   (optimizer.py:1714) — the finder's instrumented symbols are the
   settlement calls.
5. *Severity.* Below-unity COP prices stored heat under a resistive
   element exactly in the coldest hours — real consequence, but confined
   to deep cold on the space half. Medium stands.

**Vote: verify, medium.**

## D2-05 — decimal-comma grid fees unreachable (low) — **verify**

**My own number** (`verify03_d2_05.py`; metric: count of comma-rate specs
that `is_valid_spec` accepts, vs their dot twins; plus the SEK/kWh a
`GridFeeSchedule.from_config` store carrying a comma spec prices at Monday
noon, before and under my own one-line perturbation of `parse_rules` —
split on ";" and newlines only):

- 5 of 5 decimal-comma specs rejected; 5 of 5 dot twins accepted. (My sixth
  spec was a month-list comma — `maj, jun` — invalid in both regimes and
  unrelated to decimal commas; a separate grammar limitation, not evidence
  against this finding.)
- `_parse_rule("= 0,45")` alone returns rate 0.45 — the dead conversion is
  live in isolation, dead through its only caller, exactly as claimed.
- Hand-edited store with `"...= 0,27"`: 0 rules, fee 0.0 SEK/kWh. Under my
  perturbation: 1 rule, fee 0.27.

**Attacks and outcomes.**

1. *Code reading confirms the mechanism*: `parse_rules`
   (grid_fee.py:201-203) rewrites ";" and newlines to "," and splits on
   ",", so `_parse_rule`'s `.replace(",", ".")` (line 161) can never see a
   comma. The config flow validates on the way in
   (`spec_problem` → `invalid_grid_fee_rules`), so the UI path rejects with
   feedback; the silent zero-fee pricing needs a hand-edited or migrated
   store, which `from_config` deliberately degrades with a log line.
2. *Severity.* Intended support (Swedish locale, the conversion itself)
   unreachable, a confusing validation error, and a silent zero on
   hand-edited stores. Low is right: the user-visible path fails loudly.

**Vote: verify, low.**

## Summary

| id | vote | severity | one-line basis |
|---|---|---|---|
| D2-01 | verify | high | reproduced exactly; my closed form 5.824 kW break, my saturated-plan drive 5.08x at 12 kW / 6.68x at 15 kW at the reachable 24 h horizon, flat-vs-spiky 2745 vs 540 SEK; headline 13.35x cell needs a 48 h horizon the options cannot set |
| D2-02 | verify | medium | reproduced; my year-long re-aggregation 5136/yr all from the month mask, Göteborg 0/yr, night excess 406.25 SEK at factor [1.]; not an aggregate artefact; options path confirmed |
| D2-03 | verify | high | reproduced; my 1e-9 probe matches the closed form 1−d/margin to 1e-7; my FD attack: production 1e-4 kW step sees a 1269x gradient spike at the cliff; topology options-reachable |
| D2-04 | verify | medium | reproduced; my own grid 71/126 below unity (41 at outdoor ≥ −25), DHW at default setpoint 11/21, min 0.882; from_config derivation confirmed; inversion confined to the floored band as stated |
| D2-05 | verify | low | reproduced; my 5/5 comma rejections vs 5/5 dot twins, hand-edited store 0.0 SEK/kWh, my own perturbation 0.27; UI path fails loudly, silent zero needs a hand-edited store |

No timing-based refutations; nothing here is provisional on the quiet
window. All five findings survived a refute-first pass with executed
numbers on both sides.
