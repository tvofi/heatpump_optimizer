# Round 9, D14 seat s3: bug classes P3, P4 and P5

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`, box B8 (4 cores, 15 GB, shared with
D14-s1 and D14-s2). The machine-readable report is `report.json` beside this file. Every
run's raw output is under `out/`.

Run every command from the export root, prefixed with
`PYTHONPATH=tests/hastub /home/claude/venv314/bin/python`.

## Method

- **M1.** I read `tools/audit/bugclasses.json`. I found the P3, P4 and P5 instance rows for
  rounds 1, 2, 4, 6 and 7 in `docs/audit-2026-09.md`, and then the pre-fix commits in the
  git history.
- **M2.** The classes are the seat's axis: P3, P4 and P5. All three are `open`, and each has
  instances in 5 to 7 rounds.
- **M3.** I wrote one detector per class:
  - **P3** (`p3_floors.py`) is a static AST pass over the imported package's source.
  - **P4** (`p4_seeds.py`) is a dynamic wrapper around `optimizer:_multi_start_minimize`.
  - **P5** (`p5_gate.py`) is a synthetic-bias sweep through the production experiment and
    `sysid:adoption_decision`. It also has a static `--seams` listing.

  For each detector I checked four things: it re-finds a listed instance at its pre-fix
  commit, it finds zero on a clean fixture or null arm, it moves under a one-line
  re-introduction, and it is keyed on a value the production seam delivers.
- **M4 and M5.** There is one finding per class, each with a proposed barrier and its cost.

## Findings

### D14-s3-01 (P3, low, hygiene): floors read inconsistently, no barrier

- **Detector:** `p3_floors.py`, with `--json` to list every seam.
- **Baseline:** 22 quantity groups are read through `max(Q, c>0)` at one site and raw (or
  through another floor) at a sibling site.
  - 6 of the groups have a raw divisor.
  - 1 group is a store capacity: `dhw_tank_thermal_mass`. It is floored at 1e-6 in
    `optimizer:_clamp_dhw_to_capacity`, and read raw as a divisor in `_dhw_window_floors` and
    in `thermal_model:simulate_dhw_step`.
- **Re-finds:**
  - `--ref ab71960d^` (before the R7 D2-01 fix): the buffer, wood and DHW capacity groups are
    present, and `buffer_tank_thermal_mass_seam=1`.
  - `--ref 7d8a0100` (carry #1487): the wood tank is floored at 0.01 and read raw as a
    divisor.
- **Controls:**
  - `--fixture`: 0 groups.
  - `--reintroduce` (R7 D2-01's `/ max(C_buf, 0.01)`, re-introduced in memory): 23 groups,
    and the buffer seam goes to 1.
- **Why it is low:** every floor I checked sits at or below the config schema's minimum for
  its quantity, so no seam is reachable from the UI.
- **Barrier:** the detector as a `tests/` lint with an allow-list of the 22 current groups.
  It would refuse any new group, and any floor raised above the quantity's schema minimum.
  Cost: 1.3 s wall (provisional).

### D14-s3-02 (P4, low, bug): multi-start stops at non-stationary points

**Grid:** 24 golden-built cells (one or two zones × DHW on or off × 6 price profiles, all
winter_cold), plus one flat-price arm per topology.

**Result:** of 30 production calls to `_multi_start_minimize`, 12 ship more than 0.1 % above
the result that same routine reaches from its own candidates at ftol 1e-12 (max 0.52 %).
Another 12 of 30 are above a dense seed ladder's result (max 0.89 %). Leave-one-out over the
24 cells:
- range −0.018 to 0.892 %;
- mean with the most favourable cell dropped: 0.094 %;
- 9 cells miss, and 8 still miss with the most favourable dropped.

**Flat null does not vanish:** 3 of 4 topologies still miss at flat prices, with a max tight
gap of 0.68 %. So this is the ftol=1e-6 stop on a rugged objective, not a price-bracketing
miss. That is why it is low, and I claim no money.

**Probe on two|nodhw|winter_typical:**
- At the shipped tolerance, the 5 candidates refine to anywhere between 77.72 and 79.16.
- At ftol 1e-12, the same 5 reach 77.43, with ABNORMAL line-search exits.

**Perturbation and re-find:**
- `--perturb no_deep` removes the round-7 0.20× seed. The gap on the R7 cell goes from
  0.389 % to 0.594 % (up), and the quick-grid miss count goes from 2 to 3.
- At `20cb1c46^` (before the R7 D0-01 fix), production scores exactly 77.884228, the round-7
  number.
- `--ref-fixture` gives 0.

**Barrier:** a nightly replay running `p4_tol_misses` as a ratchet that may only fall. The
run takes about 10 min (provisional), which is too slow for the gate. Any convergence fix
must be priced in money and in CPU first.

### D14-s3-03 (P5, medium, bug): the gate keys on the half-width, not the bias

**Sweep:** 72 cells: 3 presets × 5 bias sources × graded magnitudes. The experiment is
driven through `SystemIdentification.arm/step` on a declared plant, the plant is rolled on
the production `ThermalModel`, and `adoption_decision` rules on each fit.

**Result:** 3 fits are admitted with a true UA error beyond the gate's own ±10 % bar:
- heavy_old at +0.8 kW free heat: −12.15 %;
- typical_slab at +0.4 kW: −10.70 %;
- typical_slab at +0.8 kW: −21.43 %.

The worst blended shift in the heat-loss scale is −7.97 %.

**The gated quantity barely tracks the bias:**
- On typical_slab, as the error goes from 0 to −21 %, the half-width moves only from 0.0531
  to 0.0685.
- When the true free heat is below the declared gains (the round-7 cell), the error rises to
  +8 % while the half-width falls from 0.0531 to 0.0491.

**Controls and re-find:**
- The null arm (no injected bias) admits 0 fits over the bar.
- `--perturb prior_true`, which gives the fit the true gains prior, brings the count from 3
  to 0.
- At `b7657ea2^` (before round-7 D7-01's #1459 fix), 5 fits are admitted over the bar, at
  half-width ~1e-4, with a −20.98 % blended shift. The fix reduced the weight but kept the
  phenomenon.

**Seams:** `--seams` lists 19 sites that write a learned thermal parameter. Only the sysid
seam is swept (see Unfinished).

**Barrier:** the sweep as a `tests/` script asserting `p5_admitted_over_bar == 0`. Cost: 3 s
(provisional).

## Non-findings

- **P3 floors:** none of the 22 groups' floors is reachable from the config schema (spot
  check against the `_number` ranges).
- **Deep seed on the with-DHW seam:** adding the 0.20× seed to `_solve_space` leaves every
  with-DHW gap unmoved. Its absence there is not a live defect.
- **Winter cells at the power bound:** production is optimal in all 8 (gap 0 and tight gap
  0).
- **Sensor drift and slab-transfer mismatch:** the gate refuses both, because the interval
  goes unbounded. The drift, ks and cap series admit 0 fits over the bar.
- **Monotonicity:** gate admission is monotone in the injected magnitude on all 15 series.

## Harnesses

- `p3_floors.py`
- `p4_seeds.py`
- `p5_gate.py`

Each carries its own command, metric, count key and perturbations in its header. All three
pin threads, print `thread_factor` (1.000 on every run), `load1` and `swapins`, and keep the
production files unchanged: every perturbation is done in memory, or in a temporary git
worktree for the `--ref` re-finds.

## Unfinished

- **Ledger instances outside the detectors' shape were not re-found:**
  - P3: the wood_share discontinuity, the smooth top-k bracket, the DHW inlet floor, the
    OverflowError, the sizing defaults, R2 D0-03, and round 5 (which is not in the register
    file).
  - P4: pre-fix runs for rounds 1 to 6.
  - P5: pre-#1410 instances.
- **P5's sweep covers only the sysid seam.** `--seams` lists the passive-learner seams, but
  they are not swept.
- **P4's grid is winter_cold only.**

## Exposure

- **The ledger exception:** `bugclasses.json`, and the `docs/audit-2026-09.md` rows for the
  P3, P4 and P5 instances of rounds 1, 2, 4, 6 and 7.
- **Git diffs and messages I read:** ab71960d, 7d8a0100, b7657ea2 and its parent's
  coordinator gate, and 20cb1c46.
- **Seen but not read:** round-8 fix-branch titles (R8-P3, R8-P5) showed up in a `git log`
  listing. I did not read their contents, and I did not read the round-8 register.
- **Not read:** nothing under `tools/audit/round3..8`.
- No `gh`, and no GitHub.
