# D2 round 4 — verifier 2 of 3 (panel D2-0)

- **Worktree** `../audit-r4-verify-D2-2`, detached at `0855277` (branch head
  `claude/13-dimension-audit-920935`). The finder measured baseline
  `7dd68dd`; `git diff 7dd68dd HEAD -- <the four production files the
  findings touch>` is **empty**, so baseline and my tree carry identical
  measured code. Every finder number reproduced exactly; none is stale.
- **Stance** refute-first, per `tools/audit/briefs/verifier.md`. I read no
  other verifier's output and no register verdict column.
- **Exposure, disclosed:** one grep of mine for grid-fee doc text matched a
  line of `docs/audit-2026-09.md` (the register) — the round-4 D2-05 row,
  restating the finding text I was already given plus its reporting status.
  No verdict column, no other finding's disposition was read; I did not open
  the file again.
- **Method.** Per finding: (1) re-ran the finder's harness exactly as its
  header commands; (2) wrote my own harness —
  `tools/audit/round4/D2/verify-0-2_own.py`, same contract (thread pin
  before numpy, RESULT lines, footer, root rule `os.getcwd()`) — with my own
  metric definitions and my own robustness attacks; (3) attacked in the
  contract's order. Every number below is a count, ratio or closed-form
  float identity; **no timing or memory figure is relied on**, so box load
  (load1 4.5–10 across my runs, quoted in the `.out`s) cannot contaminate
  any of it. `thread_factor` 0.989–1.004 on every run.
- All harness reruns printed values matching the finder's committed `.out`
  files and the FINDER.md table to the last digit; I do not restate every
  one below, only where a number carries the verdict.

## D2-01 — capacity-tariff term overstates the bill (finder: high)

**Rerun.** `peak_topk_bracket.py`: `ratio_worst=5.083811356`,
`break_excess_kw_1pc=5.841609022`, `cells_over_1pc=16/28`,
`cell_ratio_max=13.35094575`, `loo_worst=2.514813011`,
`phantom_sek_12kw=3981.716072`, `perturbed_ratio_worst=1.00000032`,
nulls `1.000000062 / 0.9999997334 / 1` — all exactly as reported.
`identities.py` also rerun clean (its `window.box_average_error=0` is what
makes the 15-min-window = per-step identity the ratio rests on).

**My own numbers** (`verify-0-2_own.py` + ad-hoc):
- Unit-of-defect ratio, bypassing `peak_cost` entirely:
  `_smooth_topk_sum(flat,3,tau)/(k*peak)` = **5.0838** at 12 kW,
  **3.1287** at 9 kW, **1.1022** at 6 kW (96 windows). Same values as the
  finder's `peak_cost`-level metric, so the wrapper adds nothing.
- **Analytic break, mine:** the logistic-count root sits at
  `peak + 0.05*peak*ln((n-k)/k)`; it leaves the bracket `[min-1, peak+1]`
  when `0.05*peak*ln(31) > 1`, i.e. **peak > 5.824 kW** (n=96) and
  **10.278 kW** (n=24 hourly). The finder's measured 1 %-onset 5.8416 sits
  just above the root-exit point, as it must. The mechanism is confirmed
  by derivation, not only by sweep.
- **Null controls hold**: below the break the identity is exact (finder's
  two flat nulls; my 6 kW point = 1.1022 is above the 5.84 break, and my
  5 kW rerun of the finder's null = 1.000000062).
- **Perturbation holds**: bracket widened by `40*scale` → every ratio
  1.0000003, 0 cells over 1 % (finder executed it; I confirmed the
  re-implementation differs from production only in the bracket line).

**Attacks run, and outcomes.**
- *Tie-condition fragility (my main attack — does the blowup need
  bit-exact solver ties?):* no. Plateau jittered uniformly ±5e-4 kW
  (inside the 1e-3 `_PEAK_TIE_BAND`): ratio **5.0805**. Jitter ±2e-3 —
  four times the tie band, so the max's neighbourhood is decided by
  chance, not by solver repetition: ratio **5.0693**. A saturated or
  near-flat plan overstates regardless of exact float ties.
- *Realistic threshold:* the finder used `threshold_kw=0`. Production's
  threshold (`PeakTracker.threshold_kw`) is the lowest peak seen, not 0.
  With an ordinary early-month threshold of 3 kW and a 12 kW flat house
  (9 kW excess): ratio **3.1287** — the effect survives realistic
  thresholds; it is not an artefact of threshold 0.
- *Wrong gate mode:* N/A (bug finding, not a test-gap claim).
- *Aggregate artefact:* the 28-cell grid's worst cell (192 windows, 15 kW)
  is **not reachable today**: `OptimizationConfig.horizon_hours` defaults
  to 24.0 and nothing in the coordinator or config flow overrides it (no
  CONF key exists), so the plan is always 96 steps = 96 15-min windows.
  Within the reachable 96-window column the ratios are 1.10 / 3.13 / 5.08 /
  **6.68** / 8.61 at 6 / 9 / 12 / 15 / 20 kW excess. So the headline
  "13.35x" is a grid corner needing a 48 h horizon production does not
  offer; the reachable worst is ~6.7x. This trims the headline, not the
  finding: 3–5x at 9–12 kW excess is inside a 3x16-20 A install's ordinary
  cold-snap range, and the finder's own leave-one-out (2.515) already
  conceded the grid corner.
- *Reachability of the branch:* `peak_cost` is the optimizer's live
  capacity term (`optimizer.py:_grid_terms`, used at `:2109` and in the
  grid report at `:3637`), fed `marginal_price_per_kw` by the coordinator
  (`coordinator.py:4411`) exactly as the harness assumes; all four catalog
  rows set `peak_tariff_window_minutes = 15`; `threshold_kw` is lowest
  early in a month, when a cold snap makes excess largest. Reachable.
- *Consequence direction:* measured, not asserted — flat 12 kW excess vs a
  spiky plan with the **identical** billed top-k (3 × 12 kW): objective
  charges **4956.72 vs 975.00 SEK**. The term prefers the spiky profile by
  3981.72 SEK — the exact inversion of what a capacity tariff is for.

**Vote: verify, high.** One headline caveat recorded for the judge: the
13.35x figure needs a 48 h horizon; at the shipped 24 h horizon the ceiling
is 6.68x (15 kW excess), 5.08x at 12 kW. High survives: the term is wrong
by 3–6x in the reachable band, its error grows with the very excess it
punishes, and it rewards spiky over flat plans at equal billed cost.

## D2-02 — catalog masks inert (finder: medium)

**Rerun.** `catalog_masks.py`: all four rows `discounted_windows=0` of 672,
declared 432/432/412/432, `rows_writing_offpeak_factor=0`,
`ellevio.phantom_peak_sek=406.2499554`, July nulls `[0.]`/`[1.]`,
perturbation 0→432/432/412/432 and 406.25→0.00. Exact.

**My own numbers:** I walked `CapacityTariff.sample_factor` by hand over a
tariff month week (672 quarter-hours), **not** through `window_factors` —
so my count cannot inherit a bug in the walk the finder's metric uses:
`sample_factor < 1.0` for **0 of 672** instants; Saturday 00:00 and
Wednesday 12:00 both factor **1.0**; July unique factors `[0.0]` (the
month mask bites — null control, independently); with `offpeak_factor=0.0`
(the finder's one-line perturbation) the same walk gives **432** of 672.
Built through the real coordinator builder
(`HeatPumpOptimizerCoordinator._capacity_tariff` on `apply_catalog`'s
config), not a hand-made `CapacityTariff`.

**Attacks.**
- *Aggregate artefact:* "0 of 672" is total, not a grid corner; dropping
  windows cannot change it. The declared counts (432 = 2 weekend days +
  5 × 12 h weekday nights at 96 windows/day; 412 for E.ON's 07–20 peak)
  re-derive by hand.
- *Is the gate real?* `tariff.mask_active` (tariff.py:404-409) requires
  `offpeak_factor < 1.0` for an hours/weekday mask to count; the code
  itself says the masks are inert at 1.0. `apply_catalog`
  (grid_fee.py:456-466) writes hours/weekdays/months/window/price/count
  and no offpeak factor; `DEFAULT_PEAK_TARIFF_OFFPEAK_FACTOR = 1.0`
  (const.py:372).
- *Reachability / user visibility:* the options schema exposes the fields
  the catalog writes (`config_flow.py:1512-1518`), so the user sees
  "07:00-19:00" and weekdays-only set after picking their DSO, with the
  offpeak slider still at 1.0. A user could set the slider by hand — the
  finding does not claim otherwise; it claims the catalog's own declared
  mask changes nothing, which is exactly what executes.
- *Severity:* two of three mask fields provably inert for every catalog
  user, one demonstrable 406.25 SEK weekend-night charge at full rate
  against the row's own declared mask. Medium is earned; not high because
  the month mask (the 0.0 factor) does work and the energy-fee half of the
  catalog is unaffected.

**Vote: verify, medium.**

## D2-03 — `wood_share` discontinuous at `hp_temp == flow_set` (finder: high)

**Rerun.** `wood_share_jump.py`: `share_jump_worst=0.9985011774` (wood
0.001 °C below curve), `share_jump_at_0.25C=0.8749961786`, both nulls
(≈0 at the full 2.0 °C margin; exactly 0 above the curve),
`wood_energy_jump_kwh=-0.6416654667` (99.18 % of the one-step discharge),
`traj_power_gap_kw=2.78e-17`, `traj_wood_jump_kwh=-1.110059838`,
`perturbed_share_jump_worst=0.000998`. Exact.

**My own numbers.**
- Sup-jump over a dense 4001-point wood-temp grid, my own metric
  (`|share(flow⁻)−share(flow⁺)|` supremum, 1e-9 °C probe): **0.9997** at
  flow_set 26.6, **0.9997** at 40, **0.9997** at 55 — the jump is ~1.0 of
  the share at every curve temperature, not just the finder's 26.6 °C.
- Band fraction (my aggregate attack on "is the jumping set measure
  zero?"): over the 2 °C band below the curve, **49.9 %** of wood
  temperatures jump by > 0.5 and **89.9 %** by > 0.1. Any wood tank within
  ~1.8 °C below the curve jumps materially; that is hours of ordinary
  depletion, not a knife edge.
- Docstring contract: `thermal_model.py:1132-1133` — "Three regions,
  continuous in ``w * Q_draw`` across every boundary". Region 2's limit at
  the boundary is 0 (`f_w→0`); region 3's is
  `1 − (flow_set − wood)/margin` = 0.875 at 0.25 °C. Discontinuous unless
  the wood tank sits a full `WOOD_TANK_MIN_MARGIN` (2.0 °C) below. The
  batched twin `_wood_share_vec` computes the identical region-3 formula
  (verified bitwise by the finder's `share_jump_vec` and my trajectory
  runs), so the solver's batched path carries it.
- **Trajectory, at five outdoor temperatures** (my cherry-pick attack on
  the finder's single −5 °C point; 1.1e-15 kW power gap ≈ 4 ulp):
  wood-tank step-1 enthalpy jump **−1.110 kWh at −5 °C** (finder's exact
  number), **−1.272 at −10 °C**, **−1.433 at −15 °C** — the ulp-jump
  reproduces and *grows* across the ordinary winter band. At **−20 and
  −25 °C it vanishes** (both arms drain equally; the deep-cold coupling
  masks the law's jump in energy). The finder's point was representative,
  not lucky; the effect covers −5…−15 °C, the band a Swedish winter
  actually lives in.

**Attacks.**
- *Reachability:* the topology is `two_tank_4way`, reached from
  `two_zone_enabled` + a throttling valve mode + a configured wood probe
  (`ThermalParameters` lines 267-271, 923-925; `topology_layout` at 305).
  All three are ordinary config-flow options; `topology.py` ships and
  validates the layout. Not a stub-only path.
- *Null controls:* hold exactly (0 at the margin, 0 above the curve).
- *Perturbation:* fading region 3 out over the margin drops the worst jump
  to 9.98e-4 (the probe's own residue) and the energy jump to 7.3e-7 kWh.
- *Wrong gate mode:* N/A.
- *Severity:* the objective is discontinuous in the decision variable
  L-BFGS-B differentiates — one ulp of step-0 power moves the wood tank's
  next-step enthalpy by ~1.1–1.4 kWh through the production batched
  trajectory, and `wood_share` is shared verbatim with the savings
  baseline (docstring, lines 1153-1154). High stands.

**Vote: verify, high.** (Noted for the judge: the energy consequence
vanishes at −20/−25 °C; the law-level discontinuity does not, anywhere.)

## D2-04 — modelled COP below 1.0 and inverted (finder: medium)

**Rerun.** `cop_below_unity.py`: `space.min_cop=0.7195446773` at
(−21 °C, 70 °C), `cells_below_unity=51/328`, loo 44; `dhw.min_cop=0.84`,
23/205, loo 19; crossings −19.91/−18.24/−16.52 (flow 45/55/65), DHW
−19.40 at the 55 °C default setpoint; `marginal_cop(−25,"buffer",70)=
0.7384800635`, `marginal_cop(−25,"dhw",60)=0.84`; inversion drops
2.10/3.64/4.83/5.33 % over −30→−21 °C at flow 45/55/65/70; nulls 1.05 /
1.05 / monotone; perturbation 51→28→11→2→0 at cop_nominal
3.5/4.0/4.5/4.8/5.0. Exact.

**My own numbers.**
- Closed form: `3.5 × 0.3 × max(0.25, carnot(70)/carnot(35))` at −21 °C
  computes to **0.7195446773** — bit-identical to `compute_cop(-21,
  flow_temp=70)`. The whole defect is the product of the curve's own 0.3
  floor (which alone pins COP at 1.05) with the post-floor Carnot ratio
  and the DHW penalty; the final `max(cop, 0.5)` clamp cannot restore
  unity. Mechanism confirmed by reconstruction.
- My own grid, 0.5 °C spacing (5751 cells vs the finder's 328): min
  **0.7195446773**, **880 cells (15.3 %)** below unity.
- **Re-aggregation:** drop the flow-70 row → 861; drop the −25 column →
  817; drop both → **799**. The aggregate is not a corner artefact; 14 %
  of the dense envelope stays sub-unity after removing both extreme axes.
- Inversion: `cop(-30,70)=0.7600 > cop(-21,70)=0.7195` — COP *falls* as
  the weather warms, confirmed on my own calls. Production's own comment
  (thermal_model.py:1380-1384) shows the authors capped the *warm*-side
  inversion (#776) and left the cold-side one open — the mechanism is of
  a class they have already accepted as real elsewhere.
- DHW at the **shipped default** setpoint 55 °C (not the 60 °C hard max):
  min **0.882**, 12 of 81 outdoor cells below unity, crossing −19.4 °C —
  mandatory hot-water load priced below a resistive element in a cold
  snap.
- Null: valve off (`mixing_valve_mode: none` → `cop_flow_carnot` 0) →
  grid min **1.05**, as claimed.

**Attacks.**
- *Reachability of the extreme cells:* `cop_flow_carnot` is on for every
  throttling valve mode — `{manual, smart_read, smart_write}`
  (mixing_valve.py:57-59, wired at thermal_model.py:916) — i.e. the
  mainstream valved install, not an exotic flag. `buffer_max_temp`
  defaults to 70 °C (`DEFAULT_BUFFER_MAX_TEMP`, const.py:648) and the
  optimizer itself charges buffers toward it; DHW setpoint 55 is the
  default. Outdoor −20 °C is weather, not config. The DHW sub-unity cells
  sit on mandatory load at the default setpoint. Reachable.
- *Does it reach money?* `marginal_cop` is called by the terminal credit
  and settlement terms (optimizer.py:1714, 3156, 4945, 5877, 5966, 5980)
  and inside the batched step itself (thermal_model.py:2546-2558). Yes.
- *Severity:* a pricing distortion bounded by ~28 % under-valuation of
  heat at the envelope corner (0.72 vs the 1.05 floor), plus a sign error
  in d(COP)/d(T_out) over a 19-degree band. It biases plans in deep cold;
  it does not corrupt every plan. Medium is right; I would not raise it.

**Vote: verify, medium.**

## D2-05 — decimal-comma grid fees unreachable (finder: low)

**Rerun.** `grid_fee_decimal_comma.py`: `specs_rejected=6/6`,
`dotted_equivalents_ok=6`, `unit_accepts_comma=1` (rate 0.45),
`first_fragment_rate=0`, `schedule_rules_after_reject=0`,
`schedule_fee_after_reject=0` (with the log line),
`perturbed.specs_rejected=0`, `perturbed.schedule_fee_after_reject=0.27`.
Exact.

**My own numbers:** six comma specs through `parse_rules` directly
(including a Swedish-month form and a semicolon-separated pair): **0 of 6**
parse; the same six, comma→dot: **6 of 6** parse; `_parse_rule("lor
00:00-24:00 = 0,09")` alone returns rate **0.09** — the
`.replace(",", ".")` at grid_fee.py:161 is dead from its only caller,
which has already split on that comma at line 201-203.

**Attacks.**
- *Other callers:* grep for `_parse_rule` outside `grid_fee.py` finds none
  in production; the comma path is unreachable, full stop.
- *Severity:* the UI documents the dotted form only
  (translations/en.json:981, 1074 — "… = 0.25" in both the help text and
  the error message), and the config flow validates with
  `spec_problem`, so a comma typed in the UI is refused with an error,
  not silently stored. The silent-zero path needs a hand-edited or
  migrated store. Low is exactly right.
- The first-fragment-rates-0.0 detail (a comma spec whose second fragment
  *had* parsed would have become a silent zero fee) is real but
  counterfactual — the second fragment always raises. It supports low,
  not more.

**Vote: verify, low.**

## Panel-level checks

- **At least one own-harness number per finding:** all five, in
  `tools/audit/round4/D2/verify-0-2_own.py` (in this worktree,
  uncommitted), header states its command; final full run clean
  (`rc=0`, `thread_factor=0.998`, `load1=9.97` — all results are
  counts/ratios/identities, load-independent).
- **Contention:** every number is contention-immune by class (count,
  ratio, closed-form identity); no timing- or memory-based refutations
  were made, so nothing here is provisional on the quiet box.
- **Baseline drift:** none — production diff between `7dd68dd` and `0855277`
  empty for tariff.py, thermal_model.py, grid_fee.py, optimizer.py.
- **Harness root rule:** all five finder harnesses and mine use
  `os.getcwd()`; I ran them from this worktree's root only.
