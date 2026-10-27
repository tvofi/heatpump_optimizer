A 750 L buffer tank behind a manual mixing valve is a store in the two-zone
model and nothing at all in the single-zone one. The single-zone step had no
valve branch — the merge base's own docstring says the `valve_target` argument
"is accepted and ignored there" — and the terminal cost's store credit was
nested inside the two-zone branch, while `config_flow` offers
`CONF_BUFFER_TANK_VOLUME` to every install with no `when=` gate. So an install
with a valve and a tank, and zoning off (the default), planned exactly as if no
tank existed: the buffer plan was byte-identical to the no-buffer plan and the
tank never left its start temperature.

This models the tank in the single-zone step: the valve throttles the flow to
the commanded target, the tank supplies the slab within its energy bound,
charging stops at `buffer_max_temp` and books what it refuses, the COP is priced
at the tank's own temperature, the Euler stability law carries the tank's own
row, and the terminal cost credits a valved store in either zoning. The
two-zone arithmetic is unchanged (its arm reads bit-identical figures).

It also carries the group's root-cause work: process state (c), and a census
that drives the tank's three live capabilities in **every** value of the zoning
domain, registered in `tests/entities.py`'s `_P2_CENSUSES`.

The last commits are what let the above land under the ratchets. The store's
physics pushed `ThermalModel` past its class budget and left one clone over
`duplication_copies`; merging the batch's copies into module helpers paid both
but put seven calls into the sub-step loop, which the production-call channel
priced at 1.191x on an unchanged plan against a 1.05x allowance, so that attempt
is discarded. The payment instead moves the scalar two-zone valved delivery
verbatim into `_valve_two_zone_delivery` (one call per scalar step) and has the
batch's single-zone store block call `_single_valve_rates` rather than restate
it. The moved law first read fifteen scalars, which put one function over the
ten-parameter guard (`params_over_10` 7 → 8, dS -0.1699 WORSENS); it now takes
the step's own `state` and reads `p.radiator_power_fraction` and
`_buffer_capacity(p)`, so it reads ten and the score is NULL. The price is one
`_buffer_capacity` call per two-zone valved step, which moved the judged
families from 1.011x/1.012x to 1.028x/1.029x against the 1.05x allowance.

Closes #2500

Part of #2499. #2712 fixed that issue's slab/UA-estimate half and carried its
plan-versus-relaxed-DP residual here. This branch measures the residual,
confirms it survives the flat-price null, and carries it forward (below) rather
than fixed, so #2499 stays open on that residual.

## Head

`5c01e40658af339371b22b1b7c141ae3e539deb9`

A merge of the branch's `7a9c76aa6` and `origin/main`'s `524c1896b`, because
`git merge-tree --write-tree origin/main HEAD` reported a conflict and a
conflict on any path but the two claim files is the reviewer's to block on
(`fix-review.md` step 13). The one conflict was `tests/entities.py`'s py-spy
stub: both sides landed the same BSD `wc` fix — ours in `758036d`, main's from
another seat — so the resolution takes main's text and changes nothing.
`tests/structure_budgets.json` merged to `class_excess_loc` 18019 (both
deltas, under the 18031 budget) and `tests/closures.json` merged with
`inert_reads.tests/harness_headers.py` as a set, through the repository's own
drivers; both are re-measured below at this head. Every figure is re-taken at
this head and `## Unpinned sites` is re-derived against it; main touches none
of the store and valve code, and the plan sha1s read byte-identical. The
commit after the merge is the structure budget's re-record
(`functions_cc_over_15` 28 -> 27, `recorded_at` 524c1896b), a data row
`tests/structure.py` reads; that script is re-run at this head and passes.

## Mutation proof

Eleven mutants, each applied to the production tree and run against the group
probe (`tests/features.py`'s four `_grad_parity` cells plus the store section,
the new batch twin included) at this head (a `git archive` copy of the merge
head `0db6d58`; the commit since touches only the structure budget's data row,
no production file): **11 KILLED, 0 SURVIVED**, each
by the checks named here, pasted from the run.

| mutant | checks that go red |
|---|---|
| M1 terminal credit two-zone only | `single-zone: the terminal cost credits a valved store tank`; `zoned store census: the terminal cost credits the tank in every zoning (#2500)` (single-zone 0.0000, two-zone -17.3299) |
| M2 scalar valve branch off | 9 checks: both `single-zone with valve` parity checks, `single-zone: the valved tank is charged for the cheap night` (tank peaked at 25.0 C from 25 C), `… the tank's loss is the slab's delivery plus standing loss` (0.0000 vs 0.5039 kWh), `… the slab receives exactly what the tank delivered`, `… charging stops at buffer_max_temp` (refused 0.000 kW), `… the step prices the COP at the tank's own temperature`, and both census arms on the tank move and the cap |
| M3 batch valve branch off | both `two-zone with valve` parity checks; `batch twin: charging into buffer_max_temp matches the scalar step bit-for-bit` (all six tracks diverged) |
| M4 scalar COP ignores the tank | both `single-zone with valve` parity checks; `… the step prices the COP at the tank's own temperature` (60 C tank +2.055 K against the priced 1.348 K) |
| M5 batch COP ignores the tank | both `single-zone with valve` parity checks |
| M6 energy bound dropped | `single-zone valve: a small tank coasting one step never falls below the slab` (tank ended at -55.90 C against a 22 C slab) |
| M7 stability row blind to the tank | `… the stability count subdivides for the tank's own row` (one step 26.796 C vs 400 sub-steps 27.649 C) |
| M8 no `buffer_max_temp` clamp | `… charging stops at buffer_max_temp and books the refusal` (tank 72.41 C, refused 0.000 kW); `zoned store census: the cap books what it refuses …` |
| M9 both single-zone COP rows ignore the tank | `… the step prices the COP at the tank's own temperature` — the mutant the parity pair cannot see, because both twins agree while both are wrong |
| M10 shared energy bound dropped | `… a small tank coasting one step never falls below the slab` (tank ended at -55.90 C); the bound is one expression, `_tank_bounded_draw`, and the batch's single-zone block calls it too |
| M11 batch cap not clamped | `batch twin: charging into buffer_max_temp matches the scalar step bit-for-bit` (buffer and refused tracks diverged; peak refused 12.1085 kW past a 70 C cap) |

M11 is why the new twin check exists: the four parity cells start a 750 L tank
with charge to spare, so no step refuses heat and a defect confined to the
batch's own clamp survives every one of them. The twin drives the tank into
`buffer_max_temp` and demands bit-identity on six tracks.

The census is demonstrated per arm **and per zoning** -- a census that only
echoed the single-zone arm would pass the base/hand comparison while blind to a
regression in the two-zone path. Each plant is one zoning's path broken, the
other left live; M2, M3 and M8 reproduce three of the four plants above at this
head:

| plant | valve arm | cap arm | credit arm |
|---|---|---|---|
| C1 single-zone valve branch off | FAIL (SZ +0.0000 K) | FAIL (SZ 0.0000 kW) | ok |
| C2 two-zone step blind to the valve | FAIL (TZ +0.0000 K) | FAIL (TZ 0.0000 kW) | ok |
| C3 credit gated to two-zone only | ok | ok | FAIL (SZ 0.0000) |
| C4 credit gated to single-zone only | ok | ok | FAIL (TZ 0.0000) |

## Null control

- **The unmodified tree.** At `3b4180dcc` the 750 L buffer plan on a spread
  price day is **byte-identical** to its no-buffer twin (`21d0378f2f79`, cost
  22.184 each, tank rise +0.00 K) — the tank is absent, not merely under-used.
- **Flat price** (the day's mean: nothing to store for). At this head the tank
  rises **+0.00 K** in both the 750 L and the 0 L arm, so the +40.00 K on the
  spread day is arbitrage and not an artefact of the new branch. The two flat
  arms do not price identically (38.059 vs 50.457): a valve lowers the flow
  temperature to the load, a COP effect with no storage in it.
- **Accuracy, calibrated.** `accuracy` on realised == predicted reads
  `power_ratio 1.0`, `cost_error_percent 0.0` at both ends.

## Figures

- `dev/audit/harnesses/r10_buffer_store.py plans 0` — 750 L manual valve vs no
  buffer, spread and flat, at `3b4180dcc` and at this head. Base spread 750 L
  `21d0378f2f79` / 22.63 kWh / cheap-quarter 0.965 / +0.00 K / 22.184 /
  identical **True**; base flat 0 L `1144455deb6a` / 50.457 / True. Head
  spread 750 L `6a546df76556` / 22.41 / 1.000 / +40.00 / 21.947 / False; head
  spread 0 L `21d0378f2f79` / 22.63 / 0.965 / +0.00 / 22.184; head flat 750 L
  `5d1137c8e29e` / 23.55 / 0.321 / +0.00 / 38.059; head flat 0 L
  `1144455deb6a` / 31.22 / 0.242 / +0.00 / 50.457.
- `dev/audit/rca/R10-RCA-BUFFER-STORE.md` — the group's root-cause work, with
  its disclosure that the roster's `next_step` was `rca` and the brief gave it
  to the group's own fixer, so the separate-seat independence the contract asks
  for is not obtained. Cause: one fact ("is this buffer tank a store?") decided
  by two predicates — the step had no valve branch and the credit sat inside
  `if params.two_zone_enabled:` — while `_settlement_caps` priced the buffer in
  every zoning. Process state **(c)**: followed, and did not produce the
  intended result — the parity grid built three of the four zoning x valve
  cells (33 `ThermalParameters` constructions set `mixing_valve_mode`, 32 of
  them also `two_zone_enabled=True`), and `config_flow` has offered a buffer to
  every install since the base with no `when=` gate, so nothing moved
  underneath it. Cost test: the census costs **0.001 s median / 0.031 s worst**
  marginal in `tests/features.py`, which runs once per gated pull request,
  **334 merges per release** over the seven `v6.7.12..v7.0.4` intervals =
  **0.33 s per release**; the defect costs **4.35 h = 15,660 s** per occurrence
  and the class carries **0.66 instances per release**, so **10,336 s per
  release** against 0.33 s — about **31,000x** (about 1,000x on the worst
  sample). The census's domain is the zoning flag's two values, enumerated, so
  it cannot skip a slot; its three check texts are registered in
  `_P2_CENSUSES`, which refuses a vanished text (`CENSUS-MISSING`).
- `python3 tests/features.py` (this head's test file, the store block's **18
  checks**): **9 ok, 9 FAIL** at `3b4180dcc` (the merged test file against that
  production) and **18 ok, 0 FAIL** at this head. The three census readings are
  the same lines in both: base valve `single-zone +0.0000 K, two-zone +0.1973
  K`; cap `single-zone 0.0000 kW, two-zone 1.5947 kW`; credit `single-zone
  0.0000, two-zone -17.3299`. At head: `+0.2744 / +0.1973 K`, `3.4614 / 1.5947
  kW`, `-17.3299 / -17.3299`.
- The wider probe (`mutants.py`'s probe: the same block plus the four
  `_grad_parity` cells, **34 checks**) reads **25 ok, 9 FAIL** at the base and
  **34 ok, 0 FAIL** at this head.
- `dev/audit/harnesses/r10_buffer_store.py bench 5` — `optimize` wall time and
  peak RSS over 5 solves per arm on the owner shape, base and this head **run
  concurrently** so both sides share the machine load: head 7.735 s median /
  17.314 s worst / 88.9 MB against base 5.199 / 5.821 / 79.5 MB; the flat
  no-buffer null 5.437 / 9.114 / 87.5 MB against 4.763 / 6.386 / 82.6 MB.
- The same arms in **CPU seconds**, which is the reading that does not move
  with the box's load (`benchcpu2.py`, 10 solves per arm, one process per tree,
  the same seeded price sequence at both ends). Two pairs, each end taken at
  the same moment: against the branch's own base (`3b4180dcc`) the owner arm
  **8.560 s → 22.338 s** (**×2.61**; per-solve medians 0.968 → 2.258, ×2.33),
  and against current `origin/main` (`524c1896b`) at the merged head
  **8.064 → 23.657 s** (**×2.93**; medians 0.929 → 2.513, ×2.70). The flat
  no-buffer null reads **×1.15** in both pairs (9.611 → 11.014 and
  9.164 → 10.519; medians 1.17x and 1.11x), so the ratio is the store's and
  not the instrument's dispersion. The
  wall-clock pair above is inflated on both arms by the load it was run under
  (its own null reads 1.14x) and is not the performance figure. The
  sensitivity control: doubling the batch substeps moves the owner arm
  7.492 → 84.494 s (×11.3) while it moves the no-buffer null only
  3.697 → 5.371 s (×1.45), so the benchmark responds to the buffer state
  resolution. The production-call channel (`stress.calls_population`): the
  two-zone valved families 1.028x and 1.029x (max 1.0295x where the plan is
  unchanged, against the 1.05x allowance), every other family 1.000x, and the
  single-zone valved family 3.129x raw / 1.852x vouched — it re-plans, 64
  objective evaluations against 40, and the channel exempts a re-planned family.
- `dev/audit/harnesses/r10_buffer_store.py accuracy` — the two fields'
  definitions read off the tree (`power_ratio` = mean(actual/predicted) over
  samples with predicted > 0.05; `cost_error_percent` = (Σpredicted −
  Σactual)/Σactual, positive when the plan over-books): calibrated `1.0 / 0.0`,
  realised 1.4× predicted `1.4 / -28.57`, plan over-books 40 % `0.714 / 40.0`.
  A mutant that flips the subtraction gives `1.4 / +28.57` and `0.714 / -40.0`
  while the calibrated null stays `0.0` — the sign convention is pinned.
- `dev/audit/harnesses/r10_demand_overbook.py --one null --dp` and
  `--one owner_i01 --dp` — the flat-price null arm and the owner-shape arm with
  the relaxed DP reference. Null (flat prices, learned scale 0.992 against a true
  1.0, 287 samples): `plan/deliv 1.205`, 12.1/10.8/11.5/14.4/15.9 kWh planned
  against 9.6/9.3/9.2/11.9/13.5 delivered, `plan_kwh 11.78` against `dp_kwh
  9.88` (**+19.2 %** learned, +20.8 % against the true-house DP), cost gap
  94.66 %/91.30 %. Owner shape (scale 0.628 against a true 0.6, 350 samples):
  `plan/deliv 1.18`, `plan_kwh 5.37` against `dp_kwh 3.88` (**+38.4 %** learned,
  +43.2 % true), cost gap 17.03 %/16.52 %. The over-booking survives the
  flat-price null, so it is demand-side, not price-chasing.

## Architecture score

Architecture score: dS +0.0000 NULL (`tools/audit/archscore/score.py --diff
524c1896b 5c01e4065`). `tests/arch_score_head.py` reads **ALL 18 CHECKS
PASSED** at this head, and `tests/structure.py` reads every metric within its
budget (`class_excess_loc` 18019, `recorded_at` 524c1896b).

## Unpinned sites

- `custom_components/heatpump_optimizer/thermal_model.py:1677 CMP_BOUND: return 0.04 if c_buf < 1e-6 else c_buf`: `_buffer_capacity`'s 35 L fallback. Pinned by `mutation-autofix`; a survivor is equivalence unless it moves the small-tank arm, which the parity pair and M6 rest on.
- `custom_components/heatpump_optimizer/thermal_model.py:1677 RETURN_DEL: return 0.04 if c_buf < 1e-6 else c_buf`: `_buffer_capacity`'s 35 L fallback. Pinned by `mutation-autofix`; a survivor is equivalence unless it moves the small-tank arm, which the parity pair and M6 rest on.
- `custom_components/heatpump_optimizer/thermal_model.py:1719 CLAMP_DROP: * np.maximum(0.0, T_buf - floor_temp)`: `_tank_bounded_draw`, the scalar step's energy bound. Killed by M6 today and re-pinned by `mutation-autofix` on the moved line.
- `custom_components/heatpump_optimizer/thermal_model.py:1720 CLAMP_DROP: / max(dt_hours, 1e-6)`: `_tank_bounded_draw`, the scalar step's energy bound. Killed by M6 today and re-pinned by `mutation-autofix` on the moved line.
- `custom_components/heatpump_optimizer/thermal_model.py:1722 CLAMP_DROP*2: return np.minimum(drawn, np.maximum(available, 0.0))`: `_tank_bounded_draw`, the scalar step's energy bound. Killed by M6 today and re-pinned by `mutation-autofix` on the moved line.
- `custom_components/heatpump_optimizer/thermal_model.py:1722 RETURN_DEL: return np.minimum(drawn, np.maximum(available, 0.0))`: `_tank_bounded_draw`, the scalar step's energy bound. Killed by M6 today and re-pinned by `mutation-autofix` on the moved line.
- `custom_components/heatpump_optimizer/thermal_model.py:1744 CLAMP_DROP*2: drawn = np.maximum(0.0, ua * (np.minimum(T_buf, flow_set) - `: `_single_valve_rates`, the scalar valved step. Killed by M6/M8 and the small-tank check; re-pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/thermal_model.py:1749 CLAMP_DROP*2: dT_cap = np.maximum(0.0, p.buffer_max_temp - T_buf) / max(dt`: `_single_valve_rates`, the scalar valved step. Killed by M6/M8 and the small-tank check; re-pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/thermal_model.py:1750 CLAMP_DROP: refused = np.maximum(0.0, dT_buf - dT_cap) * c_buf`: `_single_valve_rates`, the scalar valved step. Killed by M6/M8 and the small-tank check; re-pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/thermal_model.py:1751 CLAMP_DROP: return q_slab, np.minimum(dT_buf, dT_cap), refused`: `_single_valve_rates`, the scalar valved step. Killed by M6/M8 and the small-tank check; re-pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/thermal_model.py:1751 RETURN_DEL: return q_slab, np.minimum(dT_buf, dT_cap), refused`: `_single_valve_rates`, the scalar valved step. Killed by M6/M8 and the small-tank check; re-pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/thermal_model.py:1788 GUARD_OFF: if valve_target is not None:`: `_valve_flow_set`'s explicit-target arm, the scalar step. The batch twin computes the same target inline and the bitwise parity pair kills a divergence; re-pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/thermal_model.py:1841 GUARD_OFF: if two_tank:`: `_valve_two_zone_delivery`'s two-tank ledger, which moved here with the law; the two-tank cell of the parity pair and the census kill it. The ledger row that pinned this guard in `_simulate_step_two_zone` is deleted in this diff because the guard moved, and the nightly drain re-pins it here.
- `custom_components/heatpump_optimizer/thermal_model.py:1885 RETURN_DEL: return q_rad_from_buf, q_floor_from_buf, wood_draw, q_wood_l`: the moved law's return, read by both parity cells for the valved families; re-pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/thermal_model.py:3007 GUARD_OFF: if throttled or cop is None:`: `_simulate_step_single`'s valved branch. Killed by M2/M4; re-pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/thermal_model.py:3049 GUARD_OFF: if throttled:`: `_simulate_step_single`'s valved branch. Killed by M2/M4; re-pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/thermal_model.py:3484 CMP_BOUND: if c_buf < 1e-6:`: the two-zone stability row's 35 L fallback. A dropped fallback is equivalent at every recorded volume; `mutation-autofix` pins the line and a survivor is triaged as equivalence.
- `custom_components/heatpump_optimizer/thermal_model.py:3484 GUARD_OFF: if c_buf < 1e-6:`: the two-zone stability row's 35 L fallback. A dropped fallback is equivalent at every recorded volume; `mutation-autofix` pins the line and a survivor is triaged as equivalence.
- `custom_components/heatpump_optimizer/thermal_model.py:3509 GUARD_OFF: if ua_valve is None:`: a direct caller's default in `_substeps_and_loss`; the batch always hands both in, so the scalar path is what exercises it. Pinned by `mutation-autofix`; a survivor is equivalence unless the scalar arm diverges.
- `custom_components/heatpump_optimizer/thermal_model.py:3514 GUARD_OFF: if c_buf is None:`: a direct caller's default in `_substeps_and_loss`; the batch always hands both in, so the scalar path is what exercises it. Pinned by `mutation-autofix`; a survivor is equivalence unless the scalar arm diverges.
- `custom_components/heatpump_optimizer/thermal_model.py:3516 CMP_BOUND: if c_buf < 1e-6:`: a direct caller's default in `_substeps_and_loss`; the batch always hands both in, so the scalar path is what exercises it. Pinned by `mutation-autofix`; a survivor is equivalence unless the scalar arm diverges.
- `custom_components/heatpump_optimizer/thermal_model.py:3516 GUARD_OFF: if c_buf < 1e-6:`: a direct caller's default in `_substeps_and_loss`; the batch always hands both in, so the scalar path is what exercises it. Pinned by `mutation-autofix`; a survivor is equivalence unless the scalar arm diverges.
- `custom_components/heatpump_optimizer/thermal_model.py:3798 BOOLOP: if throttled and not p.two_zone_enabled`: the batch's `throttled and not two_zone` hoist. The single-zone arm is pinned by the bitwise parity pair; the two-zone arm is its control. Pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/thermal_model.py:3914 CLAMP_DROP: * np.maximum(0.0, T_buf - floor_temp)`: base's own two-zone bound, re-written inline by the call-parity rework (text moved, not behaviour). The two-zone figures are bit-identical to base; pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/thermal_model.py:3991 GUARD_OFF: if throttled:`: the batch single-zone twin, now inline. Killed by the bitwise parity pair, M10/M11 and the census; pinned by `mutation-autofix`.

## Red checks

- `tests / mutation` — predicted red on the **25 sites this diff adds unpinned**
  (`tools/pr/ci_predict.py --base origin/main` lists every one). Answer: the
  cheaper detector exists and ran, at nil standing cost: the same static read
  names each site, `## Unpinned sites` above disposes of all 25, and the eleven
  mutants at this head kill every site whose text carries behaviour; the
  nightly `mutation-autofix` pins the killed sites after the push (its standing
  cost is the nightly drain, not this seat's). No added site is left an open
  seam: each is either killed by a named check above or recorded as the
  equivalent-line disposition under `## Unpinned sites`.
- `tests/optimality.py` — `one|summer_negative|shoulder: a recorded claim
  still has a gap (not stale)`: claimed but the measured gap is 0.0000 %, at or
  below the bar. Answer: **this host's platform, documented at
  `tests/optimality.py:711-717`** — "CI's linux fast lane still measures ladder
  +10.55 % (obj 0.3058), though the arm64 seat reaches the basin (obj 0.2548,
  0.0000 %); the gate's platform is the one that counts, so this claim reads
  stale on arm64 only." The cell cannot be reached by this diff either:
  `_cert_inputs` builds `profiles.house(two_zone=False)`, which sets a 200 L
  tank and no `mixing_valve_mode`, so `buffer_is_store` is false and neither the
  store's physics nor the credit is live in it.
- `node tests/card.mjs` — Node's V8 heap aborts at **2045 MB live** (165 s into
  this head's gate run; 198 s in an earlier one)
  (`FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed -
  JavaScript heap out of memory`) with **no check failing**: every card check
  printed before the abort is `ok`, and `card_drift.mjs` runs green in the same
  gate run.
  Null control: the same script at this head with
  `NODE_OPTIONS=--max-old-space-size=4096` prints `ALL CARD CHECKS PASSED`
  (1304 `ok` lines, none failed), so the red is this host's default V8 heap and
  not the diff.
- `tests/stress.py` — `no scenario exceeds its own recorded cost by the budget
  factor` reads the `summer/1z/space/valve` family near its own budget and
  straddles it by run: red at the pre-merge gate (`5.3x` its reference against
  a `4.6x` budget — `1.54x` recorded x the `3.0` factor — confirmed at median
  5.6x over 3 re-solves, min 5.5x, max 5.9x, at `173b71ba4`), green at this
  head's gate (`ok`; worst scenario `shoulder/tariff+pv+cycle` at 107.8x of
  268x). That family is the one this branch re-plans (64 objective evaluations
  against 40, above), and the solver-work channel exempts it by name; the CPU
  benchmark prices the store at 2.6–2.9x on the owner shape and the budget
  channel divides by the run's own reference solve, so the margin is a cost
  reading, not a check regression. If it recurs, the disposition is a
  `tests/stress_budgets.json` raise on that scenario's recorded ratio, which is
  the owner's under `budget-raise-gate`, not this seat's.
- `tests/stress.py` — `shoulder: cheaper than holding the setpoint`
  [4.67 vs 3.96]. Answer: **base's, not this diff's.** The case is
  `buffer 200 L, valve 'none'`, and `ThermalParameters.buffer_is_store` is
  `mixing_valve.is_throttling(...) and buffer_tank_volume >=
  BUFFER_STORE_MIN_VOLUME`, false for a `'none'` valve — so neither the store's
  physics nor the terminal credit can reach it. Measured with the same driver
  at the merge base (`3b4180dcc`), at current `origin/main` (`524c1896b`) and at
  this head: `predicted 4.6716 / thermostat 3.9585` in all three.

## Forward-carry

- **The 272 s solve outlier (D15 L4) is not reproduced.** On the owner shape the
  worst solve at this head is 17.3 s in the concurrent pair, and the
  doubled-resolution mutant reaches 143.9 s, so the instrument responds to state
  resolution; no input shape here produces 272 s.
  Carry: dismissed: measured and not reproduced on every input shape this harness drives; no bound or warm start is owed without the owner-box shape
- **The live store costs 2.6–2.9x CPU on the owner shape.** Two paired runs of
  the same seeded 10-solve sequence: 8.560 s → 22.338 s (×2.61, medians
  0.968 → 2.258) and 8.064 → 23.657 s (×2.93, medians 0.929 → 2.513). The
  flat no-buffer null reads 1.15x in both (9.611 → 11.014 and 9.164 → 10.519).
  The two-zone valved families sit at 1.028x/1.029x of the 1.05x call-channel
  allowance (max 1.0295x), and the single-zone valved family re-plans (64
  objective evaluations against 40, exempt there). A bound or a warm start on
  the planner must earn the 2.6–2.9x. Lands in
  `dev/programme/rosters/wave-r10-groups.json`.
  Carry: R10-STORE-RACES (handoff/audit-r10-roster at b5ea7fda7a9e)
- **The two accuracy biases are separate, and neither is a sign slip.** The live
  bundle reads `power_ratio ≈ 1.31`, `cost_error ≈ -29 %`: reality delivers more
  power and costs more than the plan booked. The DP arms read the plan booking
  more energy than the relaxed DP optimum (+19.2 % on the flat-price null,
  +38.4 % on the owner shape) and more than the house then receives
  (`plan/deliv` 1.205 and 1.18). So the *planner* over-books against its own
  reference, while the *realised* run over-runs the plan; the two live on
  different comparisons and neither cancels the other. The definitions are
  pinned (`accuracy`, above), and a pure power ratio of 1.31 would read a cost
  error of -23.7 %, not -29 %, so the owner's pair also carries a ~7 % cost-per-
  kWh component or two different sample windows. The same arms are #2499's
  residual: the plan books +19.2 % more kWh than the relaxed DP optimum on the
  flat-price null and +38.4 % on the owner shape, and the gap survives the null,
  so it is demand-side and #2499 stays open on it rather than closing on this
  measurement. R10-STORE-RACES inherits the residual: close it as a demand-model
  fix with the same flat-price null, or refute it and say why, either way with
  `dev/audit/harnesses/r10_demand_overbook.py`. Lands in
  `dev/programme/rosters/wave-r10-groups.json`.
  Carry: R10-STORE-RACES (handoff/audit-r10-roster at 4fa0f8418)
- **Two homes for the 35 L fallback, on purpose.** `_buffer_capacity` words it
  once, and the two-zone step and the batch step each still inline it
  (`if c_buf < 1e-6: c_buf = 0.04`). The step's copy sits two lines above the
  call that now also computes it; routing the step through the helper would
  delete those lines and drop `class_excess_loc`, at one more call per
  two-zone step — the call channel is at 1.0295x of its 1.05x allowance, so it
  is left to the group that next prices that family. Lands in
  `dev/programme/rosters/wave-r10-groups.json`.
  Carry: R10-STORE-RACES (handoff/audit-r10-roster at d6217f814a7c)

## Friction

- `gitignore-global-config: cost`: `.gitignore:28` ignores `config/` at any
  depth, so `git add dev/audit/config/bugclasses.json` (a **tracked** file)
  prints *"The following paths are ignored"* and exits 1 while still staging the
  file; `git add -A` skips new files there silently. Both nested `config/`
  directories in this tree (`dev/audit/config`, `dev/governance/config`) are
  tracked and visible to `git check-ignore`, so the rule is anchored wrong for a
  repository with policy config directories. Carry: R10-FLOW-JIDOKA (handoff/audit-r10-roster at 46df1de62)
- main-red-invisible: unenforced: `tests/stress.py`'s shoulder economics check
  is red on the merge base (`3b4180dcc`) and on current main (`524c1896b`) with
  the identical reading (`predicted 4.6716 / thermostat 3.9585`), and no
  check-run at main's head shows it: at `524c1896b` the `gate` check completed in
  21 s and `sweep` in 10 s, and of the `tests / ...` jobs only `ci-ratchet` and
  `coverage-ratchet` ran. A full-suite pass on main is therefore not visible in
  that push's checks, so a base red travels unremarked into a branch's gate. Not
  this group's to fix; the after-merge bookkeeping must read main's own suite
  state. Carry: R10-FLOW-POSTMERGE (handoff/audit-r10-roster at c0dbb4585d68)
