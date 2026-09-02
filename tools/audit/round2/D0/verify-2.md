# D0 — verifier seat 2 (consequence and reachability)

Worktree `v-D0-2` at `c398fc84eec25fc44b60d74aae05b9a2da205884`. The register's
harnesses were copied read-only into my scratch dir and reached from the repo
root through `tools/audit/round2/D0` (a symlink into scratch), so every harness
ran from the root with `PYTHONPATH=tests/hastub` and wrote only into my scratch.
No production or test file was edited, no `git` state was touched, and the only
file I created under the register is this report.

**Interpreter.** The finder's stated stack (python 3.13.1, numpy 2.5.2, scipy
1.18.1) is *not* this box's default `python3` (3.11.5 / 2.4.6 / 1.17.1). I used
the matching interpreter that exists on the box so the L-BFGS-B build is the one
the numbers were taken on. Anyone re-running with the default `python3` is on
scipy 1.17.1 and should expect different last digits; that is a reproduction
hazard the finder's header does not warn about.

**Stance.** My seat asks three things of each finding: how far the triggering
configuration sits from the shipped defaults, whether the loss survives a run of
days at production's own re-plan interval, and whether a user would see it on an
invoice. Two rules were applied without exception — a challenger that is colder
or short of hot water is not cheaper, and every claimed gain was re-run at flat
prices.

**My own harness.** `consequence.py` (my scratch dir; header carries the full
contract). One-line metric: *realised electricity cost in SEK of a closed-loop
run of N consecutive days over a Nord Pool SE3 week whose profile changes daily,
re-planned at production's own default interval (`DEFAULT_OPTIMIZATION_INTERVAL`
= 30 min, `const.py:1070`), scored by `tests/backtest.py:score` (its `cost`
field) plus the realised capacity charge from `tariff.peak_cost` — production's
solver minus the same solver with the race's cheap fixes patched in through the
`optimizer:_multi_start_minimize` seam — beside each arm's comfort violation in
degree-hours below the per-step floor and its DHW shortfall steps.*

It differs from the finder's `rolling_gap.py` in three ways that turned out to
matter: it re-plans every **30 minutes** (production's default) rather than every
2 h; it **advances the buffer-tank temperature** from the plant's own
`last_buffer_trajectory` instead of freezing it at 40 °C, which is the state
variable D0-03 turns on; and the price profile **changes day by day**. `score` is
lifted verbatim from `tests/backtest.py` via `ast` (that module runs its whole
suite and `sys.exit`s at import, so it cannot be imported).

*Harness perturbation, run:* `--improved-off` makes both arms production.
`RESULT realised_gap_sek_week=0.0000`, and the two arms reproduce
`bt_cost 190.1774 / peak_charge 60.0000 / violation 0.00000` bit-for-bit. The
harness is deterministic and is not measuring a constant.

*Two caveats on my own numbers.* The improved arm is `d0lib.ImprovedSolver`, a
slightly stronger search than either proposed fix, so my gaps are an upper bound
on what the fixes recover. And the plant is the optimizer's own model
(`--plant-error 1.0` equivalent), so these are solver gaps with no forecast or
model error; a real installation recovers less.

*Label bug in my harness, for the judge:* the `RESULT week=` line prints `flat`
whenever `--week` is passed, so the `--week winter_typical` run below is
mislabelled `week=flat` in its own output. The run is identified by its `--tag`
and by its distinct costs; the true flat run is the one with
`prod_cost_sek_week=229.9130`.

**Contention.** `load1` ran 3–70 across the day. Every number below is a count, a
SEK figure on the production objective, or a realised SEK cost — all
contention-immune. `thread_factor` was 1.000 on every run. No wall or CPU figure
carries weight in this report.

---

## D0-01 — capacity tariff, single-zone stall (finder: medium, bug)

### Re-run — exact

```
PYTHONPATH=tests/hastub python tools/audit/round2/D0/race_grid.py --tz 0 \
  --weather winter_cold --quiet --random 3 --tag tariff15_baseline \
  --opt '{"peak_price_per_kw":20.0,"peak_threshold_kw":6.0,"peak_window_minutes":15,"baseline_load_kw":1.0}'
RESULT cells_with_gap_sz=15 count            (finder 15)
RESULT restart_improves_sz=7 count           (finder 7)
RESULT pg_above_pgtol_sz=16 count            (finder 16)
RESULT mean_gap_sek_sz=4.8198 SEK            (finder 4.8198)
RESULT max_gap_sek_sz=58.2850 SEK            (finder 58.2850)
RESULT mean_energy_gap_pct_bill_sz=2.517     (finder 2.517)
RESULT mean_restart_gap_sek_sz=0.1661 SEK    (finder 0.1661)
RESULT loo_mean_gap_pct_sz=2.192             (finder 2.192)
RESULT thread_factor=1.000  load1=12.83
```

Every aggregate *and* every one of the 16 per-cell lines reproduces to the last
printed digit.

### Perturbation — moves, but not where the title points

`D0_PERTURB=ftol9`, same command:

```
RESULT restart_improves_sz=0 count           (7 -> 0,        finder 0)
RESULT mean_restart_gap_sek_sz=0.0000 SEK    (0.1661 -> 0,   finder 0.0000)
RESULT cells_with_gap_sz=10 count            (15 -> 10,      finder 10)
RESULT mean_energy_gap_pct_bill_sz=1.385     (2.517 -> 1.385, finder 1.385)
RESULT mean_gap_sek_sz=4.2303 SEK            (4.8198 -> 4.2303)
RESULT max_gap_sek_sz=58.1688 SEK            (58.2850 -> 58.1688)
RESULT thread_factor=1.000  load1=41.54
```

Confirmed in the stated direction. Note what it does *not* move: the headline
58 SEK cell survives at 58.1688 and the mean gap falls only 12 %. **The stall the
title names is 0.166 of the 4.820 SEK mean — 3.4 %.** The remaining 96.6 % is
basin/seed (`restart_same` = 0.0000 in 8 of the 15 gap cells in the finder's own
per-cell table). The mechanism that costs the money is the top-k plateau, not
the FACTR stop.

### My own number — consequence over a run of days

```
PYTHONPATH=tests/hastub python tools/audit/round2/D0/consequence.py --tz 0 --dhw 1 --days 3 \
  --opt '{"peak_price_per_kw":20.0,"peak_threshold_kw":6.0,"peak_window_minutes":15,"baseline_load_kw":1.0}'
  [production] bt_cost 190.1774  peak_charge 60.0000  violation 0.00000 Kh  min_room 18.627  energy 176.56 kWh  peak 6.00 kW  dhw_short 0
  [improved]   bt_cost 188.7865  peak_charge  0.0000  violation 0.00000 Kh  min_room 18.463  energy 177.92 kWh  peak 5.00 kW  dhw_short 0
RESULT realised_energy_gap_sek_week=1.3909 SEK   -> 0.4636 SEK/day, 0.73 % of the energy bill
RESULT peak_charge_prod=60.0000  peak_charge_improved=0.0000
RESULT violation_delta_kh=0.00000  parity_ok=1  dhw_short 0/0
RESULT solves_per_arm=144  improved_calls=109   thread_factor=1.000  load1=40.38
```

**Feasibility parity is exact** — 0.00000 comfort degree-hours and 0 DHW-short
steps in both arms — and the improved arm buys *more* energy (177.92 vs 176.56
kWh), so nothing here is bought with cold.

The consequence is two different currencies and the finding conflates them:

* **Energy: 0.46 SEK/day**, 0.73 % of the bill, ~170 SEK/year.
* **Capacity charge: 60.00 SEK vs 0.00 SEK.** Production runs the compressor
  flat out (6.00 kW; 7.00 kW at the meter against a 6.00 kW threshold) in at
  least three metering windows; the improved solver never exceeds 5.00 kW.
  `tariff.peak_cost` is by its own docstring *"what this plan would add to the
  **monthly** capacity charge"* = `full_price × mean(top-k monthly peaks)`. So
  60.00 SEK is **60 SEK per month** — up to ~720 SEK/year while the tariff bills
  — not 60 SEK per day. The finder's "1–4 SEK/day" headline is a per-solve
  objective difference in which the peak term is a monthly charge; amortised
  honestly the two components come to about 2.4 SEK/day, which lands inside the
  stated band for reasons the report never established.

**This is larger than the finder's own closed loop found.** `rolling_gap.py`
reports "realised peak charge 0.000–0.014 SEK in both arms". Its 2-hour re-plan
and single tiled profile were hiding the only consequence that matters.

### Attacks

**Grid artefact.** The 58.285 SEK cell is `summer_negative` prices ×
`winter_cold` weather — `tests/profiles.py` documents these as a "windy/sunny
summer day … negative midday prices" and a "Stockholm mid-Jan cold spell"
(−12 °C, 45 W/m² peak solar). The pairing is physically impossible. It carries
58.285 of the 77.117 SEK summed objective gap over the 16 cells — **76 %**. The
finder's leave-one-out does drop it and mostly quotes the dropped figure, which
is correct; any aggregate that keeps it is meaningless.

**Objective gain is not bill money.** Summing my re-run's per-cell records: the
16 cells' objective gap totals 77.117 SEK but the *energy* gap totals 26.736 SEK
on a 699.55 SEK summed bill (3.82 %), and in **4 of 16 cells the winning
challenger spends more on energy than production** — worst
`winter_typical/sz/nodhw` at −11.09 SEK, −44 % of that cell's bill. On the 58 SEK
cell the challenger's energy bill is **1.02 SEK higher** and 59.30 SEK of the
gap is non-energy. Single-solve objective gaps are not money; the closed loop is.

**Null control (mandatory), run.** Same command with `--week flat`:

```
RESULT peak_charge_prod=0.0000   peak_charge_improved=0.0000   (both arms peak 5.00 kW)
RESULT realised_energy_gap_sek_week=2.8649 -> 0.9550 SEK/day, 1.25 % of bill
RESULT violation_delta_kh=0.00000  parity_ok=1
```

The **capacity over-run does not survive flat prices** — the money is genuinely
price-driven and belongs on this panel. The **energy component fails the null
control**: it is *larger* at flat prices (0.955 vs 0.464 SEK/day), so that half
is non-convexity, exactly as the finder concluded for D0-02 and did not for this
one. Single-solve cells agree: flat mean gap 0.594 SEK with restart 0.0000,
non-flat mean 1.357 SEK (58 SEK cell dropped) — 2.3×.

**Robustness of the decisive number.** Re-run with an ordinary week
(`--week winter_typical`, 3 days): `peak_charge` 0.0000 in **both** arms, both
peaking at 5.00 kW, energy gap 0.476 SEK/day. So the 60 SEK over-run comes from
the `winter_extreme` day — the −12 °C cold snap with a 7.40 SEK/kWh evening.
That is not a weakness of the finding: it is precisely the day a Swedish
`effektavgift` sets the month's peak on, and a winter month contains several.

**Reachability.** `DEFAULT_PEAK_TARIFF_ENABLED = False` (`const.py:311`), so this
is opt-in. Once on: `peak_tariff_window_minutes` is a two-option select
`["15","60"]` (`config_flow.py:2535`), so 15 min is one click from the default
60; `peak_tariff_price_per_kw` is `_number(0, 500, 1)` with default 45 — the
finding's 20 SEK/kW *marginal* is 60 SEK/kW full price
(`marginal = price / peaks_averaged`), 33 % above default, so a default-priced
tariff sees roughly 75 % of the effect; `peak_tariff_peaks_averaged` is a slider
`_number(1, 10, 1)`, default 3. The 6.0 kW threshold is not configured at all —
it is `_peak_tracker.threshold_kw(tariff)`, the month's own recorded peaks. An
opt-in corner, but a shallow one, and both golden fixtures (`capacity_tariff`,
`capacity_tariff_15min`) already ship it. **The finder's `peak_count=16`
demonstration is not a user workaround** — the selector's maximum is 10. It
stands only as a mechanism probe, and the report should not read as if a user
could configure their way out.

**Proposed fix against the repo's own gate.** `ftol=1e-9` removes the restart
component but leaves 96.6 % of the mean gap and the whole 58 SEK cell, and it
roughly doubled production CPU on the same 16 solves (32.7 → 65.3 s,
provisional). The smooth-top-k half of the proposal is the half that carries the
consequence; a fix that ships only the `ftol` change would move the goldens for
almost no money.

### Vote — `verify` (medium)

**Decisive number: realised capacity charge 60.00 SEK (production) vs 0.00 SEK
(improved) over three closed-loop days at production's own 30-minute re-plan, at
exact comfort parity (0.00000 Kh and 0 DHW-short steps in both arms), falling to
0.00 vs 0.00 at flat prices.** That is one month of `effektavgift` on a
60 SEK/kW tariff — a visible invoice line, avoidable, and price-driven.

Medium is earned by consequence; high is not, because it needs an opt-in tariff
and costs 60 SEK a month rather than a month's heating.

Two corrections for the register: the title's "1–4 SEK/day" mixes a daily energy
cost with a monthly capacity charge, and the title's "stalled iteration" names
the mechanism behind 3.4 % of the measured gap.

---

## D0-02 — two-zone FACTR stops (finder: low, bug)

### Re-run — exact

The full 80-cell grid is a ~13-minute run at rest and the box was at `load1`
20–70; I re-ran the 16-cell subset the finding also cites, which carries its
largest cells.

```
PYTHONPATH=tests/hastub python tools/audit/round2/D0/race_grid.py --tz 1 \
  --weather winter_cold --quiet --random 2
RESULT cells_tz=16   cells_with_gap_tz=13         (finder 13)
RESULT restart_improves_tz=7 count                (finder 7)
RESULT mean_restart_gap_sek_tz=0.2183 SEK         (finder 0.2183)
RESULT mean_gap_sek_tz=0.4494 SEK                 (finder 0.449)
RESULT pg_above_pgtol_tz=16 count                 (finder 16)
RESULT null_flat_mean_gap_sek_tz=0.7319           (finder 0.732)
RESULT nonflat_mean_gap_sek_tz=0.4091             (finder 0.409)
RESULT thread_factor=1.000  load1=58.48
```

Per cell too: `winter_narrow/winter_cold/tz/dhw` gap 2.5099, restart 2.1631 —
the finder's headline 2.163 SEK cell to four digits.

### Perturbation

`D0_PERTURB=restart`, same subset:

```
RESULT mean_restart_gap_sek_tz=0.0030 SEK   (0.2183 -> 0.0030,  finder 0.003)
RESULT mean_gap_sek_tz=0.2494 SEK           (0.4494 -> 0.2494,  finder 0.249)
RESULT restart_improves_tz=3 count          (7 -> 3)
RESULT null_flat_mean_gap_sek_tz=0.6471     nonflat 0.1926
```

Moves as stated, and it exposes the shape of the residue: **after the fix the
flat cells carry 3.4× the gap of the priced ones** (0.647 vs 0.193 SEK). What
survives the proposed fix is not price optimality at all.

### Null control

The finding is scoped to the restart component and that component passes: it
vanishes at flat prices in the finder's data and in mine. The whole-race gap
fails outright — 0.7319 SEK flat vs 0.4091 SEK non-flat, i.e. *larger* without a
price signal — and the finder says so and excludes it from the claim. That is the
right call and I could not break it.

### My own number — consequence

The arithmetic settles this one from executed numbers; a closed-loop run was not
worth the box time. Summing my re-run's per-cell records over the 16 subset
cells: objective gap 7.191 SEK, but **energy gap 4.825 SEK on a 1102.99 SEK
summed bill — 0.44 % — and in 8 of 16 cells the winner spends more energy than
production.** The finder's own closed loop realises +0.100 to +0.220 SEK per two
days: 0.05–0.11 SEK/day on a ~69 SEK/day bill, i.e. 0.07–0.16 %, or 18–40 SEK a
year against a ~25 000 SEK/year bill. A Swedish electricity invoice is rounded to
the krona; this sits under the rounding.

### Vote — `verify` (low)

**Decisive number: energy gap 4.825 SEK across the 16 subset cells against a
1102.99 SEK summed bill = 0.44 %, with the winner spending *more* energy than
production in 8 of those 16 cells**, becoming 0.05–0.11 SEK/day realised.

The mechanism is real, the claim is scoped honestly, the perturbation moves and
the scoped null control passes — but the consequence is below what any user can
see. `low` is right and there is nothing lower; if the register carried a
`hygiene` class for a true-but-invisible defect this would belong in it. The one
thing the judge should not allow is the 2.163 SEK single-cell figure travelling
without the 0.05 SEK/day it becomes.

---

## D0-03 — small buffer tank with a mixing valve (finder: medium, bug)

### Re-run — exact

```
PYTHONPATH=tests/hastub python tools/audit/round2/D0/race_grid.py --tz 1 --dhw 0 \
  --weather winter_cold --quiet --random 3 --tag smalltank \
  --cfg '{"mixing_valve_mode":"manual","buffer_tank_volume":35.0,"buffer_max_temperature":70.0}' \
  --state '{"buffer_tank_temperature":32.0}'
RESULT cells_with_gap_tz=5 count             (finder 5 of 8)
RESULT pg_above_pgtol_tz=8 count             (finder 8)
RESULT mean_gap_sek_tz=1.1333 SEK            (finder 1.1333)
RESULT max_gap_sek_tz=4.1884 SEK             (finder 4.1884)
RESULT mean_energy_gap_pct_bill_tz=4.396     (finder 4.396)
RESULT loo_mean_gap_pct_tz=0.804             (finder 0.804)
RESULT null_flat_mean_gap_sek_tz=0.1411      (finder 0.1411)
RESULT thread_factor=1.000  load1=14.32
```

Exact per cell as well: `winter_typical` gap 3.4708 with production `under`
0.1119 K-steps and pg 131; `winter_moderate` 4.1884.

### Perturbation

Config, `buffer_tank_volume` 35 → 750 L:

```
RESULT mean_gap_sek_tz=0.2047 SEK       (1.1333 -> 0.2047,  finder 0.205)
  winter_typical   3.4708 -> 0.0000     (finder 0.0000)
  winter_moderate  4.1884 -> 0.1984     (finder 0.1984)
  max |proj. grad| 1.05e4 -> 0.18
```

Moves decisively. One caveat for the judge: the supporting statistic
`pg_above_pgtol_tz` is **8/8 in the perturbed run too** — PGTOL is 1e-5 and the
perturbed gradients are 0.003–0.18, still far above it. That *count* is saturated
and discriminates nothing in either direction; only the magnitude moves. The
finding does not rest on the count, but the count should not be quoted as if it
did.

### Reachability — the finding's strongest fact, and the report undersells it

"A small buffer tank with a mixing valve" reads like a corner. It is not:

| field | finding's value | shipped default | selector |
|---|---|---|---|
| `buffer_tank_volume` | 35.0 L | **`DEFAULT_BUFFER_TANK_VOLUME = 35.0`** (`const.py:851`) | `_number(10, 1500, 5, "L")` on the thermal-model page (`config_flow.py:1248`) **and** the mixing-valve page (`config_flow.py:2056`) |
| `buffer_max_temperature` | 70.0 °C | **`DEFAULT_BUFFER_MAX_TEMP = 70.0`** (`const.py:580`) | `_number(40, 90, 1, "°C")` |
| `mixing_valve_mode` | `manual` | `none` | `_select(SELECTABLE_MODES)` — 4 options, of which **3** (`manual`, `smart_read`, `smart_write`) are in `THROTTLING_MODES` |

So 35 L is not merely inside the selector's range: it is the value the form
arrives **pre-filled** with, on both pages carrying the field, and the valve page
writes it on any save. The only field a user must move off its default to reach
this finding is turning the mixing valve on, and three of the four valve modes
get there. Further, `BUFFER_STORE_MIN_VOLUME = 100.0` (`const.py:863`) and
`ThermalParameters.buffer_is_store` requires
`buffer_tank_volume >= BUFFER_STORE_MIN_VOLUME`, so **the shipped default tank is
never a store** and every default installation with a valve lands in exactly the
`_tighten_buffer_caps` branch. Meanwhile the suite's own house
(`tests/profiles.py:house`) uses `buffer_tank_volume: 200.0` — the fixture most of
the suite runs on does not exercise the shipped default. This is a default, not
a corner, and the severity should be read with that in mind.

### Feasibility parity at the single solve — the challenger dominates

On `winter_typical`: production objective 88.9746, comfort `under` 0.1119
K-steps, 71.843 kWh; `seed_bang1.0` objective 85.5038, `under` 0.0000, 61.954
kWh. Cheaper on the objective, cheaper on the bill and warmer at once — no
cost-for-comfort trade. Summed over the 8 cells the *energy* gap is 30.171 SEK on
a 544.90 SEK bill — **5.54 %** — which exceeds the 9.066 SEK objective gap,
because some of the energy the challenger saves is stored heat the terminal
credit pays production back for. That is exactly why this finding needed a closed
loop, and why the finder's "MPC masking: not run (budget)" is the gap I filled.

### My own number — the closed loop the finding did not run

```
PYTHONPATH=tests/hastub python tools/audit/round2/D0/consequence.py --tz 1 --dhw 0 --days 3 \
  --cfg '{"mixing_valve_mode":"manual","buffer_tank_volume":35.0,"buffer_max_temperature":70.0}' \
  --state '{"buffer_tank_temperature":32.0}'
  [production] bt_cost 285.6421  violation 0.00605 Kh  min_room 16.976  energy 241.48 kWh  buffer 17.0-70.0 C
  [improved]   bt_cost 278.7991  violation 0.01142 Kh  min_room 16.954  energy 237.84 kWh  buffer 17.0-70.0 C
RESULT realised_gap_sek_week=6.8430 -> 2.2810 SEK/day, 2.40 % of the bill (~830 SEK/year)
RESULT violation_delta_kh=0.00537  parity_ok=0   dhw_short 0/0
RESULT solves_per_arm=144  improved_calls=218    thread_factor=1.000  load1=5.20
```

The loss **persists**: 2.28 SEK/day realised over three closed-loop days at
production's own 30-minute re-plan, with the buffer tank swinging its real
17–70 °C rather than frozen at 40 °C. A user would see roughly 830 SEK a year,
which is well above the rounding on their bill.

**Parity, honestly.** `parity_ok=0`: the improved arm's realised violation is
0.01142 Kh against production's 0.00605 Kh — it is *colder*, so by my seat's rule
the gain is not clean. But the size is 0.0054 degree-hours across 72 hours and
0.02 K at the coldest quarter-hour (16.954 vs 16.976 against a 17.0 floor). It is
a nominal parity failure, not a comfort trade — and the flat run below has exact
parity (0.00000 both) with a *larger* gain, which settles it.

### Null control — **failed**, and this is the finding's real problem

```
... consequence.py (same, plus --week flat)
  [production] bt_cost 294.8374  violation 0.00000 Kh  energy 245.70 kWh
  [improved]   bt_cost 286.3004  violation 0.00000 Kh  energy 238.58 kWh
RESULT realised_gap_sek_week=8.5370 -> 2.8457 SEK/day, 2.90 % of the bill
RESULT violation_delta_kh=0.00000  parity_ok=1
```

**At flat prices the realised gain is larger, in absolute SEK (8.54 vs 6.84 per
three days) and as a share of the bill (2.90 % vs 2.40 %)** — and this despite
`flat` having the *lower* mean price (1.20 SEK/kWh against ~1.93 for my SE3
week). The gain does not merely survive the null control; it grows.

The single-solve null control (flat 0.1411 vs non-flat 1.2750 SEK) passes only
because it starts the tank at 32 °C once and solves once. Let the tank state
evolve and re-plan 144 times and the kink recurs at every solve regardless of
prices. So the finding's `null_control` claim — *"the kink gaps (3.5–4.2 SEK)
appear with a price spread and with a tank too small to absorb the cheap-hour
charge"* — is **false in the closed loop**: only the second half holds.

By the panel's own rule, that means this is not price optimality. It is a
seeding/kink defect in the cap-tightened re-solve that costs the same money with
no price signal at all, and the title and the panel placement are wrong. The
comfort-breach half of the title does not survive either: production's realised
breach is 0.006 Kh over three days, and the cheaper alternative breaches *more*.

### Vote — `verify` (medium)

**Decisive number: realised closed-loop gap 6.8430 SEK over 3 days = 2.2810
SEK/day (2.40 % of the bill, ~830 SEK/year) at production's own 30-minute
re-plan, with the buffer tank advancing 17–70 °C; and 8.5370 SEK = 2.8457 SEK/day
(2.90 %) at flat prices with exact comfort parity.**

The defect is real, it is reachable at the **shipped default** tank size and
ceiling (only the valve mode differs from default, and 3 of 4 valve modes
qualify), it persists across a run of days rather than being one solve on one
grid cell, and it costs money a user can see. Medium is earned — if anything
conservative, given the reachability and that the finder's own single-solve
figure (3.5–4.2 SEK/day) is the *smaller* of the two ways to count it once the
loop runs.

But the register must carry the correction: **this finding fails the flat-price
null control in the closed loop and is therefore not about price optimality.**
Its `null_control` field and its D0 placement are wrong; the fix scope
(`optimizer.py:_tighten_buffer_caps` and the re-solve seeding) is right.

---

## Votes

| id | vote | decisive number |
|---|---|---|
| D0-01 | `verify` (medium) | realised capacity charge 60.00 SEK vs 0.00 SEK over 3 closed-loop days at the 30-min re-plan, exact comfort parity, 0.00 vs 0.00 at flat prices |
| D0-02 | `verify` (low) | energy gap 4.825 SEK on a 1102.99 SEK summed bill = 0.44 %, winner spends more energy in 8/16 cells; 0.05–0.11 SEK/day realised |
| D0-03 | `verify` (medium) | realised 6.8430 SEK / 3 days = 2.2810 SEK/day (2.40 %) priced, **8.5370 SEK = 2.8457 SEK/day (2.90 %) at flat** — real money, failed null control |

Nothing voided. No refutation here rests on a timing number.
