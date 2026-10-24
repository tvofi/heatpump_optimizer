# R9-P3 RCA: a capacity floor or divisor applied inconsistently across sibling formulas

Seat: round-9 RCA, class P3 (N=3: D2-s2-81, D12-s2-03, D14-s3-01). It starts beside F2.1, and the
barrier lands in F1.10. Baseline `1936d5ca`. Prototype branch `handoff/r9-rca-p3` @ `2ca057ae`, cut
from origin/main `db878b29`. At main, `optimizer.py`, `thermal_model.py`, `sysid.py`, `golden.py`,
`profiles.py` and `stress.py` equal the baseline's (`git diff --quiet 1936d5ca origin/main -- …` exits 0).
`$R` = `/mnt/project-files/audit-r9/rca/p3`, and every script and log cited below is there.
`$EV` is an export of `handoff/audit-r9-evidence` @ `79aa98ec`.

## Root cause

### Cause, reproduced at 1936d5ca

Each P3 sibling writes its normalisation of a shared quantity inline, at the point of use. That
covers the floor, the clip and the per-zone scaling. So each site makes its own decision on the
degenerate edge (a zero range, a zero store, one zone of two). A fix, or a new sibling, reaches only
the copies someone found. The three instances show this:

- **D12-s2-03**: `(power − p_min) / max(p_max − p_min, 0.1)` has four inline copies in `optimizer.py`
  (`_zone_setpoints`, `_power_to_setpoints`, `_power_to_displace_schedule`, `get_current_action`).
  Three clip the result to [0, 1]. The one that publishes (`get_current_action`) does not. At the
  initial release `ec45dc4d` there were already two copies, one clipped and one not. `3e5aba6a` added
  a third copy, clipped. The disagreement was present from the first commit, and every later sibling
  was one more copy. Reproduced: `$EV/…/D12/s2/onoff_label.py` (sha1 `94575dbd`) prints
  `onoff_full_power_mislabelled=149`, `onoff_power_normalized_min=-60.0`, and on the modulating null
  arm `modulating_norm_out_of_range=585` (min −0.2) (`$R/p3_onoff_base.log`).
- **D2-s2-81**: `ed053e10` (2026-08-21) added the linear floor price `_COMFORT_FLOOR_L1` to both
  topology branches of `_comfort_terms`. In the two-zone branch it went inside the pre-existing
  `0.5 * weight * (…)` average of the quadratic terms. `_comfort_terms_batch` is a verbatim twin and
  carries the same halving. Reproduced: `$EV/…/D2/leads/l4_zone_floor.py` (sha1 `2a9ddfdc`) prints
  `two_zone_floor_deg_steps_sum=2.4672` (2 of 12 cells) against the single-zone null arm's `0.1471`
  (`$R/p3_l4_base.log`).
- **D14-s3-01**: `_clamp_dhw_to_capacity` floors `dhw_tank_thermal_mass` at 1e-6, while
  `_dhw_window_floors` and `simulate_dhw_step` divide by it raw. Reproduced:
  `$EV/…/D14/s3/p3_floors.py --json` (sha1 `8b9fd95e`) prints `p3_seam_groups=22`, and the
  `dhw_tank_thermal_mass` group has `raw_divisor=True`.

**Which side moved** (`git log -S`): in D12 and D2 the inconsistent sibling is either original or
was added later beside a correct one. Neither is a regression of a fix. In D14-s3-01, #1556 removed
seven capacity floors and three coefficient floors from the DHW seams. It kept this one and
dispositioned it "already guarded … a 1e-6 floor cannot bind" (the #1556 PR body, `## Figures`). That
disposition is correct on reachability. The inconsistency it left is the hygiene finding.

### Class search: what else the same cause reaches

The instrument is a rule, not a list: arm (a) of the prototype (`$R/p3_divisors.py` is its
standalone form). It groups every `max(E, c>0)` on a `ThermalParameters` quantity, keyed on E after
resolving locals, and flags a key that is floored in more than one function, floored with two
constants, or divided raw beside its floor. At origin/main it returns **9 groups**:

| key | shape | disposition |
|---|---|---|
| `max_electrical_power - min_electrical_power` | floored in 4 functions, one unclipped | instance D12-s2-03 |
| `dhw_tank_thermal_mass` | floored in `_clamp_dhw_to_capacity`, divided raw in 2 | instance D14-s3-01 |
| `slab_heat_transfer` | **two constants** (1e-6 in optimizer.py, 1e-9 in sysid.py) across 4 functions | open seam, not in the sweep: report, no probe of consequence run |
| `min_electrical_power * 0.5` (the on threshold) | floored in 3 functions across `optimizer.py` and `pump_arbiter.py` | latent: same shape as D12 (consistent today) |
| `cop_nominal`, `emitter_design_delta_t` | each floored at 1.0 in 6 functions across 3 modules | latent |
| `ecl110_pid_time_constant_hours`, `DHW_MIXED_USE_TEMP - dhw_inlet_reference`, `0.3 * max_electrical_power` | each floored in 2 functions | latent |

At the historical pre-fix refs, the same rule re-finds the ledger's capacity instances:
- `ab71960d^`: R7 D2-01, buffer `divided raw beside its floor`.
- `7d8a0100` and `266d795b^1`: R7 D2-03 / #1487, wood `divided raw beside its floor`, and DHW with
  two constants.
- `266d795b` (#1556's merge): only the DHW residual is left, which is D14-s3-01.

The rule does **not** reach D2-s2-81, which is a weight and not a floor. It also does not reach the
ledger's non-floor instances: R2 D2-05 (the wood_share discontinuity), R4 D2-01 (the top-k bracket)
and R6 D7-03 (the OverflowError). I did not run those at their pre-fix refs, so their coverage is
unmeasured, not zero.

**The sweep's proposal, examined.** The sweep proposed `p3_floors.py` as a lint with an allow-list of
the 22 (group, floor) pairs, plus "floor ≤ schema minimum". I refuse it on three measured grounds:
1. It covers 1 of the 3 round-9 instances. Neither the `p_range` range nor the two-zone weight is
   among its 22 groups.
2. Its key blinds it (fixer.md step 14). I added one new raw divisor of `dhw_tank_thermal_mass`
   beside the floor, in memory. `p3_floors` then read 22 → 22 groups with the same (group, floor)
   key set, while that group's raw sites went 10 → 11. This is R7 D2-01's shape, passed silently.
3. 12 of its 22 keys are function-local names with no schema key at all. By the rule
   `grep '"<leaf>"\|CONF_<LEAF>'` over `config_flow.py` and `const.py`, 2 of 22 name one.

### Process state: (c), followed and did not produce the intended result

The process: fixer.md step 8 (since `6bc932db`, 2026-09-22) says *"name a rule that enumerates the
class's seams (a command, not a description), run it, and put every seam it returns in
`## Figures`"*. Round 8 added a `BARRIER:` per group.

It was followed. #1556 ran two class rules:
- `grep -rnE 'max\([^)]*(thermal_mass|c_dhw|C_dhw|C_buf|C_w|c_w)\b'`
- `grep -rnE 'max\([^)]*heat_loss_coefficient'`

It dispositioned every returned seam in its body. R8-P3 (`wave-r8-groups.json`) built the
barrier its brief named: *"a static check that the seam rule returns no call without per-step
humidity … and a property test … marginal_cop for dhw and for buffer agree"*.

It did not produce the intended result, for two reasons:
- Each rule was keyed on its own instance's spelling (`thermal_mass`, a `humidity` keyword). A
  sibling spelt `p_range` or `0.5 * weight` is in no rule.
- Each enumeration lived in a pull-request body and ran once. None became a standing check, and the
  ledger still reads `"detector": null, "barrier": null` for P3 after 13 instances.

This is not (b): the instruction was obeyed. The countermeasure for (c) is a rule keyed on the
class's shape, not the instance's spelling, run on every gate. The owner's class-elimination rule
(`1d38497a`, 2026-09-25) already requires that. This seat supplies the form.

### Cost test

    cost(countermeasure, recurring) < cost(defect) × P(recurrence)

- **Standing cost:** 1.0 CPU-s per `tests/features.py` run for both arms (`cpu_s=0.94–1.02` over 6
  runs). Wall time was 2.6–3.5 s at load1 17–21 on 4 vCPU, on a shared box. `run_p3_block.py`
  measures from after the imports `features.py` already pays. For scale, the whole
  `tests/features.py` at origin/main took 335 CPU-s (user) and 14 m 24 s wall on the same box, with
  `ALL 3374 FEATURE CHECKS PASSED`. The barrier adds about 0.3 %.
- **Defect cost, measured:** P3 fix pull requests took 10.0 h (#1556, opened 04:06Z to merged
  14:07Z) and 22.0 h (R8-P3, first commit 2026-09-24T23:19 to the #1605 merge 2026-09-25T21:17).
  Both are fix-only lower bounds: they exclude find, verify, judge and sweep.
- **P(recurrence), measured class frequency:** P3 had instances in 7 of 9 audit rounds, taken from
  three sources: ledger rounds 2, 4, 5, 6 and 7 (`tools/audit/bugclasses.json`), round 8's R8-P3
  group, and round 9. That gives 0.78 per round.
- **Break-even:** 10.0 h × 3600 × 0.78 / 1.0 s ≈ 28,000 `features.py` runs per round. For scale,
  main merged 69 pull requests over 2026-09-24/25
  (`git log --first-parent --merges --since=2026-09-24 --until=2026-09-26`).

**Verdict:** build it. It passes unless a round runs `features.py` more than about 28,000 times.

### The class-eliminating barrier

It is two arms in the existing selectable `tests/features.py`, in a block placed after the R8-P3
block. It adds no new tracked file, no closure change and no budget change. At the prototype's head
`python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

- **(a) One floor per thermal parameter.** Every positive floor on a `ThermalParameters` quantity
  lives in one function with one constant, and nothing divides by it raw.
  - It must reach zero groups, not an allow-list. That makes a second, diverging copy of a floor
    impossible to express, which is the ledger's mechanism.
  - Design choice, stated (fixer.md step 11): a floor that two sites need becomes a helper.
  - A fixture probe pins the rule's own keying: two spellings of a range, a floor through a local,
    a second constant, a raw divisor, and a parameter floor left out of class.
  - A module-count guard stops it going green on an empty read.
- **(b) One floor price per zone.** The marginal price of one zone-kelvin under `min_temp` equals the
  single-zone room's, in `_comfort_terms` and `_comfort_terms_batch`.
  - Only the linear floor term is pinned. How the quadratics combine the zones is left to the fixer.
  - A `ref > 0` guard stops it passing vacuously.

Demonstrations (`$R/run_p3_block.py`, `$R/p3_mutants.sh`, `$R/p3_mutants.log`):

| tree | arm (a) | arm (b) |
|---|---|---|
| origin/main (= baseline for these files) | **FAIL**, 9 groups incl. D12-s2-03 and D14-s3-01 | **FAIL** 4/4, ratio 0.5000 |
| scratch fixed tree (`$R/fixed-tree.diff`: three instance fixes, then the other seven groups moved into `ThermalParameters` properties) | PASS, 0 groups | PASS 4/4 |
| fixed tree + D14-s3-01 re-introduced | FAIL, `dhw_tank_thermal_mass: divided raw beside its floor` | PASS |
| fixed tree + D12-s2-03's inline floor re-introduced | FAIL, `max_electrical_power - min_electrical_power: floored in two functions` | PASS |
| fixed tree + D2-s2-81 re-introduced (scalar twin) | PASS | FAIL 2/4 (the scalar pair only) |
| fixed tree + R7 D2-01 (`/ max(C_buf, 0.01)`) | FAIL, `buffer_tank_thermal_mass` | PASS |
| fixture probe (null and positive control) | PASS, exactly the two expected groups | n/a |

`$R/fixed-tree.diff` is 5 files, +63/−36 production lines. `STRUCTURE RATCHET PASSED` on it once its
one local import was dropped.

**What it does not do:** arm (a) sees an inline copy of a floor, not a missing clip behind a shared
helper. The published fraction staying in [0, 1] on an on/off pump is D12-s2-03's own pin in F2.1,
and this barrier does not replace it. The class's wider reading, "sibling formulas that should agree
do not", has no mechanical barrier within the bound. See the tvofi item below.

## Plan fold

- **Landing PR:** F1.10, as planned. It must wait on F2.1, because arm (a) reads zero only after the
  D12 copies are one, and arm (b) only after D2-s2-81 is fixed.
  - Nothing in the barrier needs tvofi. F1.10 is gated only by `tests/harness.py`.
  - Option: if F1.10 stalls on that gate, D14-s3-01 and this barrier could move into their own
    ungated PR after F2.1, with the same borrows.
- **Files:**
  - `tests/features.py`: not code-owned, not policy. Prototype +212 lines.
  - Consolidation in `thermal_model.py` (the new properties), `optimizer.py`, `sysid.py` and
    `coordinator.py`: all already in F1.10's edits or borrows.
  - **`pump_arbiter.py`**: not in F1.10's borrows. Add a borrow from F3, after F3.2, which edits
    `pump_arbiter.py`'s `hold()`.
- **Estimated lines:** production about +60/−35, measured on the scratch fixed tree: +63/−36
  including the F2.1 instance fixes. Test about +210.
- **Constraint on F2.1 (carry before F2.1 merges, `finding-propagation.md`):**
  - D12-s2-03's fix should send all four `p_norm` sites through one helper that owns the floor
    (better, the clipped fraction). Otherwise F1.10 re-opens them.
  - D2-s2-81's fix must give each zone the full linear floor price. Arm (b) leaves the quadratics
    free.
  - Neither of these is in F2.1's brief today.
- **New open seam** for the orchestrator: `slab_heat_transfer` is floored at 1e-6 in `optimizer.py`
  and 1e-9 in `sysid.py`. It is not in the sweep's lists and has no probe of consequence. F1.10
  consolidates it under arm (a) either way.
- **Budget:** no raise is needed on the measured scratch tree.
- **Needs tvofi:** the class boundary. D2-s2-81 (a halved weight) and the ledger's non-floor
  instances fall outside the mechanism "a capacity floor or divisor", which is the only thing arm (a)
  eliminates. Either P3's mechanism text narrows to floors and divisors, and D2-s2-81-shaped
  instances get another class, or the wider "siblings disagree" reading is accepted as barriered
  only per sibling pair (arm (b) is one such pin). No mechanical class-wide barrier for the wider
  reading fits the bound.
- **PR set and `after` edges:** unchanged, except F1.10's added borrow of `pump_arbiter.py`, which
  puts F1.10 after F3.2.
