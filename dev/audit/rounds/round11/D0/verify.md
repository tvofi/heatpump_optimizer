# D0 verifier, audit round 11

One verifier, three lenses (V1 reproduce, V2 independent, V3 reach and class), per `verifier.md`.
None of the four findings is in a planted-tree scope (all are D0-s*), so every number below was taken
in the **git worktree** `audit-r11-verify-D0`, detached at `handoff/audit-r11-register` (28b864af6d).
`custom_components/heatpump_optimizer/optimizer.py` is byte-identical to baseline 92d38ecb there
(`git diff --stat 92d38ecb HEAD -- optimizer.py` is empty); `tests/` and other files moved.
Interpreter: `hpo-orch/r10s6/venv-ci` (numpy 2.5.4, scipy 1.18.1), macOS, 8 cores.
**Contention:** load1 was 30-210 throughout (other seats). Every number here is a count or an
objective value (contention-immune); every run printed `thread_factor=1.000`. No timing is used.
The finder harnesses end in `open("/proc/vmstat")`, which does not exist on macOS (`wall_d15.py`
crashes after its RESULT lines; the others print `swapins=-1`); the RESULT lines are complete.
Logs: `dev/audit/rounds/round11/D0/verify/logs/`; my harnesses: `verify/v2_*.py`.

## D0-s2-01 -- wood tank zeroes space-only seeds; mild two-zone days ship all-off -- **weaken**

**V1** (worktree, load1 157-176, tf 1.000).
- `--census`: `census_cells_all_but_one_start_zero[prod]=32`, `zero_starts_total=128`; identical
  per cell to the finder's `results/wood_seeds_census_prod.txt`. Perturbation `WOOD_SHARE_OFF=1`:
  32 -> 4 cells, 128 -> 16 starts, down as stated.
- `--race` (7 cells): gap_abs 2.0292 / 1.9945 (winter_typical/shoulder) / 1.6782 / 1.6310 / 1.3572
  (winter_moderate/summer_cool), prod_kWh 0.000-0.002. Two values are outside the stated +-0.01:
  shoulder 1.9945 against the finder's 1.725, moderate 1.3572 against 1.468. The range is
  **1.36-2.03**, not 1.47-2.03. Perturbed: 0.000 / 0.577 / 0.000 / 0.009 / 0.000, down.
- Null control `flat/*`: summer_cool 1.6782 (survives flat, as declared). flat/shoulder gives
  **1.3426, not 0.0001**, with prod_kWh 5.33, so that gap is a different phenomenon (not a zero plan).

**V2** (`verify/v2_wood.py`). Metric: J_prod minus J with one extra candidate (the best
single contiguous block, P in {1,1.5,2} kW, 1-8 h, ranked by the space call's own objective).
- 5 gap cells: gap 1.766 / 0.732 / 1.678 / 1.456 / 1.468, 5 of 5 > 0.01. The all-off plan is beaten
  by 0.7-1.8 units.
- **Attack on the mechanism:** with the tank at 45 C (`WOOD_TANK_C=45`) the census shows
  **zero_starts=0 of 5** on all five cells. Even so, the 0 kWh plan still ships on 3 of 5, with gaps
  1.768 / 1.379 / 1.278. Seed *collapse* is sufficient but not necessary. The defect is that no
  start brackets a floor-level one-run plan when the seed energy is small.
- Single-zone twins (65 C): zero_starts 0 of 4, gap 0.000-0.001 on 5 of 5.

**V3.**
- Reachable in real HA: the solver path is pure numpy/scipy. Building the record goes through
  FakeHass, but the optimizer itself is not stubbed. It needs a configured two-tank wood plant with
  a top-probe reading that covers the reference.
- Severity low (as stated): an objective-unit comfort-pull gap with about 0 SEK of energy.
- seam_rule (`--census`) enumerates only two-zone/no-dhw/wood cells at one tank temperature, so it
  covers only the demonstrated seam. The 45 C seam (non-zero but small seeds) is outside it.
- Class: **P4** (the seed set does not bracket the optimum), not `new`.

## D0-s3-01 -- the finder export's strip deletes bundles.json's evidence; d15-installs refuses -- **verify**

**V1** (worktree, load1 30, tf 1.000).
- `wall_d15.py`: `before_strip_lines=1 rc=0; after_strip_lines=0 rc=2` (REFUSE: evidence
  dev/audit/rounds/round10/D15/s1/intake.py ... is not in the tree), exact.
- `--perturb keep_bundles`: `after_strip_lines=1 rc=0`, up as stated.
- Null control (the before-strip count) = 1.

**V2** (own method, full `git archive HEAD` tree in scratch rather than the harness's 3-dir copy).
- `enumerate.py d15-installs`: 1 line rc 0 before. After `prepare_baseline.sh --strip . 11`
  (12 rounds stripped, 1832 files removed): 0 lines, rc 2.
- The real planted finder export `plant-export/audit-r11-baseline` also refuses (rc 2). That was a
  direct run of the enumerator, with no diff against git.
- Seam sweep: all 19 `enumerate.py` universes run unstripped against stripped. **Only d15-installs
  changes**; the other 18 print identical counts.

**V3.**
- Instrument finding; reached in every finder export the round's wave scripts build.
- Consumers: D0.M8, D15's universe, and `regret_oracle.py installs`.
- Severity medium is earned: a whole step's universe cannot be printed in the tree a finder works in.
- seam_rule (`grep 'is not in the tree\|exists()' enumerate.py`) enumerates enumerate.py's refusals
  (L573, plus L399's `.git`). My 19-universe sweep confirms there is no other enumerator seam. It
  does not reach readers outside enumerate.py (regret_oracle consumes the same universe).
- Class I2 accepted: the strip's keep set is derived from closures and does not follow the real
  dependency set.

## D0-s3-02 -- no all-off start; negative-price storage plants ship plans worse than off -- **verify**

**V1** (worktree, `offstart.py`, fresh output, load1 158-210, tf 1.000).
- `summer_negative_gap_cells=14/60` (finder 16): max gap 2676.85, rel max 0.0838, mean rel 0.0395.
- By plant: flow-setpoint 6, valve-storage 4, manual-valve-buffer 2, wood 2. There are 0 plain cells.
- Flat twins: 0/60 (null control holds).
- `--perturb off_in_prod`: 14 -> 2 (both flow-setpoint, as stated), down.
- The count differs from the finder's 16. The finder's own off-arm descends from the lower bound,
  and on some cells (min gap_off -1217) that descent leaves the off basin.

**V2** (`verify/v2_offscore.py`). Metric: J(shipped) - J(lower-bound vector itself, no descent),
both scored by the scope `_commit_runs` returned for the shipped plan.
- **16/60** summer_negative cells where doing nothing scores better than the shipped plan: gap
  168-2677, rel max 0.0838. By plant: flow-setpoint 8, valve-storage 4, manual 2, wood 2. 0 plain.
- Flat twins: 0/60. 0 unmatched.
- Leave-one-out (drop the 2677 cell): 15/59, rel max 0.0838. Not a grid artefact of one cell.

**V3.**
- Reachable in real HA: negative spot prices are real, and storage plants are configured. Pure solver.
- MPC masking (the finder's own loop numbers) keeps severity at **low**. The published plan and its
  forecast overheat are wrong.
- The relative range in the title (to 8.6 %) matches my 8.38 %. The claim text's "7.4 %" is below
  my max.
- seam_rule (offstart over summer_negative/summer_warm) covers only the demonstrated price×weather.
  Other negative-price weathers are not enumerated.
- Class P4 confirmed.

## D0-s3-03 -- _terminal_cost docstring's floor-breach half never holds at learnable weights -- **refute**

**V1** (worktree, `terminal_claim.py`, load1 132-138, tf 1.000), on the finder's 40 committed cells.
- Unperturbed: `tail_breach_worse_cells=0/40`, tail_dump 39/40 (finder 40/40).
- `--perturb learned_min`: 0/40, dump 39/40.
- `--perturb weak_floor`: 13/40, max 6.12 K-steps (finder 6.08). Reproduced, and the perturbation
  moves up.

**V2** (`verify/v2_terminal.py`). Metric: the min over the last 8 steps and over **every zone
trajectory** (room, upper, lower) of temperature minus the per-step floor. Breach < -1e-3 K.
Cells are my own: all 40 d0-grid winter_typical/{winter_cold,shoulder}/*/24h lines plus
winter_typical/winter_cold/*/plain/48h (44).
- comfort_weight **1.0 (COMFORT_WEIGHT_MIN, learnable)**: **24/44** cells where the no-credit plan
  breaches the tail floor and the credit plan does not. The worst margin is -0.147 K, and every
  winter_cold cell breaches.
- Default 5.0: 0/44 (worst -0.0001 K).
- Control 0.05: 24/44 (worst -1.14 K).
- **Cross-check with the finder's own harness** on 3 of my cells at `--perturb learned_min`:
  `tail_breach_worse_cells=2/3`, max 0.0328 K-steps. The third, a two-zone cell, breaches only in
  the upper/lower zone trajectories, which `terminal_claim.py` does not read, because it reads
  `room_temp_trajectory` alone.

Attacks:
- Grid artefact: the finder's 40 cells contain no winter_typical/winter_cold/24h line, the cold
  coast-down day where the claim lives.
- Metric blind spot: two-zone breaches go unread.

The docstring's floor-breach consequence holds at the learner's minimum weight, which is inside the
range comfort_learning can reach. The "never at any learnable weight" claim is refuted with an
executed number. What survives: at the default weight 5.0 the breach is 0/44, and the size is small
(0.01-0.15 K).

**V3.**
- Reachable: a learned weight at 1.0 is reachable in real HA via comfort_learning.
- Severity: if anything survives, it is a docs nuance (the breach is weight-dependent), so low at most.
- seam_rule greps optimizer.py only. The same claim is in `docs/how-it-works.md:191`, which it
  misses.
- Class I5 would fit only if the drift were real. It is not, at w=1.0.
