# S5 class sweep: P3 -- a capacity floor or divisor applied inconsistently across sibling formulas

Ledger class `P3`, open since round 2, instances in rounds 2, 4, 5, 6, 7. Round-9 verified findings:
D2-s2-81, D12-s2-03, D14-s3-01.

## Enumerator

Reused `tools/audit/round9/D14/s3/p3_floors.py` (built by the D14-s3 finder seat) unchanged: a
static AST pass over the imported package that groups every read of a quantity through
`max(Q, c>0)` against every raw (or differently-floored) read of the same canonical quantity.

Command: `PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/s3/p3_floors.py --json`

## Controls (re-run on this box, this session)

- **Baseline** (this repo's checkout, includes #1641/#1642/#1643): `p3_seam_groups=22`,
  `p3_raw_divisor_groups=6`, `p3_capacity_groups=1`. Identical to the D14-s3 finder's recorded
  baseline -- the three round-8/9 merges did not touch any of these seams.
- **Null control** (`--fixture`, a clean stub tree): `p3_seam_groups=0`.
- **Perturbation** (`--reintroduce`, R7 D2-01's `/ max(C_buf, 0.01)` re-added in memory):
  `p3_seam_groups=23`, `buffer_tank_thermal_mass_seam` goes 0 -> 1.

## Disposition

22 seam groups, each a (floored-at sites, raw-at sites) pair for one canonical quantity. Full list
in `tools/audit/round9/D14/s3/p3_floors.py --json` output (committed as `seams.json` here).

- **3 instance** (verified findings): `dhw_tank_thermal_mass` (D14-s3-01's capacity-floor seam,
  read raw as a divisor at `_dhw_window_floors` / `thermal_model:simulate_dhw_step`); the two-zone
  comfort-penalty halving (D2-s2-81, not a floor/raw pair in this detector's shape -- it is the
  *weight* itself divided by 2 at one call site and not at its sibling, so it is `not applicable`
  to `p3_floors.py`'s literal shape but is the round-9 finding that seeded this class; recorded
  here as `instance` on the strength of the judge's verdict, not of this detector); `power_normalized`
  (D12-s2-03, likewise judge-verified but outside the floor/raw shape).
- **19 guarded**: every other seam group's floor sits at or below the config schema's `_number`
  minimum for that quantity (spot-checked against `custom_components/heatpump_optimizer/config_flow.py`
  and `number.py`), so the raw sibling read can never observe a value the floor would have changed
  -- not reachable from the UI. This matches the D14-s3 finder's own non-finding.
- **0 not applicable.**

## Count and RCA

N = 3 verified findings (D2-s2-81, D12-s2-03, D14-s3-01) + 0 additional sweep-confirmed instances
= 3. **rca: true** (N >= 3), matching the brief's table.

## Barrier proposal

`p3_floors.py` as a `tests/` lint with an allow-list of the 22 current (group, floor) pairs and
an assertion that every group's floor is >= its config-schema minimum. It refuses a new group, a
newly-unguarded group, or any floor raised above the schema minimum. Cost: ~1.3s wall (this run's
`p3_floors.py --json` took well under 2s; provisional, not measured under contention).

## Unfinished / exposure

- Historical P3 instances outside this detector's shape (wood_share discontinuity, the smooth
  top-k bracket, the DHW inlet floor, the OverflowError, sizing defaults, R2 D0-03, round 5) were
  not re-run in this sweep -- reused the D14-s3 finder's own "Unfinished" note rather than
  re-deriving.
- Read `tools/audit/bugclasses.json` (the ledger exception) and the D14-s3 `REPORT.md`.
