# R9-P5 RCA: a sysid/adoption gate keyed on a quantity other than the bias it gates

Seat: round-9 RCA, class P5 (N=3: D2-s4-01, D2-s4-81, D14-s3-03). Starts beside F4.2 and its
barrier lands in F4.2. Baseline `1936d5ca`. Prototype: branch `handoff/r9-rca-p5` @ `d4cf63d9`,
cut from origin/main `db878b29`. `sysid.py`, `thermal_model.py`, `presets.py`, `stress.py` and
`profiles.py` are identical at baseline and main (`git diff --quiet` exits 0).
`$R` = `/mnt/project-files/audit-r9/rca/p5`; `$EV` = export of `handoff/audit-r9-evidence` @ `79aa98ec`.

## Root cause

### Cause, reproduced at 1936d5ca

`adoption_decision` bounds the fit's own **precision**: the profile-likelihood half-width, plus
since #1459 the sensitivity to one declared prior-width. Precision cannot see the bias this gate
exists to refuse. That bias comes from a plant that differs from what the experiment is **told**,
and the gate's own docstring says it bounds "the fit's self-consistency and not its accuracy".
When the unmodelled free heat moves by more than the prior's assumed 0.1 kW width, the UA error
grows faster than the interval. Reproduced with `$EV/tools/audit/round9/D14/s3/p5_gate.py`
(sha1 `4796ef7c`, `$R/p5_base.log`):

- 3 of 72 cells are admitted over the ±10 % bar: `p5_admitted_over_bar=3`,
  `p5_worst_admitted_err_pct=21.431`.
- The null arm is `p5_admitted_over_bar_null=0`.
- On typical_slab the half-width moves 0.0531 → 0.0685 while the error moves 0 → −21.43 %.

**Which side moved.** The round-7 fix `b7657ea2` (#1459) added the prior term and verified it with
the gate's own weight: "weight 0.9988 … → 0.5199", with "the bias … +7.438 % at both refs". It
measured that the gate discounted the fit. It did not measure that the gate refused a biased fit.
The phenomenon was kept (`D14-s3 REPORT.md`: at `b7657ea2^`, 5 cells over the bar; now 3).

### Class search: beyond the sweep

The R8-P5b barrier is `tests/features.py` `_z1524_run`, the "#1524" block. It already asserts the
class property ("adopts within the bar … or is refused") on a mismatched plant. Its only mismatch
axes are `true_ua` and `true_mass`, which are quantities the fit **estimates**. I gave it an axis
for every quantity the experiment is **handed**: the `house_*` keywords of
`SystemIdentification.step`, plus a drifting reading. Then I ran 54 nights
(`$R/p5_axes_all.py`):

| axis | over the bar | disposition |
|---|---|---|
| free heat +0.4, +0.8 kW (plant > declaration) | 3: heavy_old +0.8 (scale 0.8799), typical_slab +0.4 (0.8967) and +0.8 (0.7916), all single-zone | the three instances, re-found by the R8 runner itself |
| **plant slab mass 0.5× declared** | **1: heavy_old single-zone, scale 0.8827** (graded: 0.9 → 0.9912 … 0.6 → 0.9269, 0.5 → 0.8827, 0.4 refused) | **open seam, not in the sweep.** p5_gate perturbs the declared room mass and slab transfer but not slab mass. The orchestrator should decide whether it is a fourth instance for F4.2 |
| free heat −0.2, slab transfer 0.5×/2×, slab mass 2×, drift 0.05–0.1 K/h | 0 | guarded (refused, or admitted within the bar) |

Other seams checked:
- **The passive learners' residual gate** (`coordinator.py` `HOUSE_LOSS_MAX_RESIDUAL`) rejects
  outliers per sample. It is not a precision-keyed admission of a fit, so it is not this cause. I
  reached that by reading the code, not by measuring it.
- **`gains_prior_kw`.** Production sets it to the static configured `internal_gains`
  (`coordinator.py`, the `SysIdConfig(...)` construction). It does not use the internal-gains
  profile the coordinator learns (`_internal_gains_profile`). The fixer may use that, but it needs
  `coordinator.py`, which F4.2's brief says to hand back to F1.
- **`async_update_thermal_params` (the S5 lead, carried to F1.4):**
  - It is **not** caught by this barrier. It does not reach `SystemIdentification.step` or
    `adoption_decision`, so no sysid sweep can see it.
  - It is also not this class, because it writes no estimate. Reading `coordinator.py`
    (`async_update_thermal_params` and `_apply_*`): a new heat-loss coefficient resets
    `house_heat_loss_scale` to `DEFAULT_HOUSE_HEAT_LOSS_SCALE` through the clamp in
    `_apply_house_heat_loss_scale`, and an explicit `buffer_cooling_rate` is clipped to
    `_buffer_cooling_bounds()`. These are user-asserted values with bounds, and there is no bias to
    gate.
  - Whether they need more than that bound is D1-s2-53's fixer's call in F1.4, as the plan says.

### Process state: (c), followed and did not produce the intended result

The process was a per-group BARRIER in round 8, and the fix-review contract in round 7. Both were
followed:

- **R8-P5b's brief:** "BARRIER: a parametrised test … that runs one production experiment on every
  stress preset … and asserts adoption within the existing UA error bound". It was built, with a
  mismatch arm (`true_ua=1.15, true_mass=1.5`), and merged as #1610.
- **Round 7's #1459:** failing test first, and measured at both refs.

They did not produce the intended result. Both chose perturbations along the axes the fit
estimates, and measured the gate's own output (weight, admission on a correct declaration). The
axis the class lives on is the one the fit is told and cannot estimate, and neither process had a
rule that made anyone enumerate it. The ledger's own detector idea, "gate decision … monotone in
the true injected bias", has been in `bugclasses.json` since 2026-09-24. It was never a check: the
ledger still has `"detector": null, "barrier": null`.

This is not (b), because the instruction was obeyed. The countermeasure is not "sweep harder". It is
an enumerator that derives the axis set from the experiment's own signature, so a told quantity with
no axis is refused.

### Cost test

    cost(countermeasure, recurring) < cost(defect) × P(recurrence)

- **Standing cost:** 3.9 CPU-s per `tests/features.py` run for 60 nights (`cpu_s=3.89`, 10.6 s wall
  at load1 about 18 on 4 vCPU, measured after the imports `features.py` already pays). For scale,
  the whole `tests/features.py` at origin/main took 335 CPU-s. The barrier adds about 1.2 %.
- **Defect cost:** measured on the three round-8 P5 fix PRs, first commit to merge on main. #1581
  took 12.8 h, #1610 7.9 h and #1613 13.3 h. I use the minimum, 7.9 h. This is fix-only; find,
  verify and judge are excluded.
- **P(recurrence):** P5 had instances in 9 of 9 rounds. That combines ledger rounds 1–7, round 8
  (#1523/#1524/#1525) and round 9, which gives 1.0 per round.
- **Break-even:** 7.9 h × 3600 × 1.0 / 3.9 s ≈ 7,300 runs per round. Main merged 69 PRs over
  2026-09-24/25.

**Verdict:** build it. If the budget matters, the 12 `true_ua`/`true_mass` nights overlap the
#1524 mismatch arm's joint cell, and dropping them saves about a fifth of the cost.

### The class-eliminating barrier

The barrier extends the existing R8-P5b check. It adds no new file, needs no closure or budget
change, and prints `STRUCTURE RATCHET PASSED` at the head. It has four parts:

1. `_z1524_run` gains `true_gains`, `true_slab_mass`, `true_slab_transfer` and `drift`.
2. **Enumerator arm:** the set of `house_*` keywords of `SystemIdentification.step` must equal the
   axis table. Every axis must be a runner keyword with at least one magnitude.
3. **Sweep arm:** every perturbed night, single- and two-zone, on all three presets, either adopts
   within the bar of the plant's own heat loss or is refused. The night count must match the table.
4. **Liveness** stays with the existing #1524 null-control checks, which require the unperturbed
   nights to adopt.

Demonstrations (`$R/run_p5_block.py`, `$R/p5_modes.log`). They were run in the block harness, not
through the full `tests/features.py`, because a full run takes 14 minutes on this box:

| mode | result |
|---|---|
| defect (main = baseline sysid) | **FAIL**: 60 nights. Names heavy_old gains 0.8, heavy_old slab mass 0.5, typical_slab gains 0.4 and 0.8 |
| null (every magnitude at identity, the healthy plant) | PASS, 0 fails |
| oracle (stand-in for a fixed gate, below) | PASS, including the #1524 liveness checks |
| bar ÷ 10 (a gate that refuses almost everything) | R9-P5 PASS, but **4 #1524/R8-P5c liveness checks FAIL** (0 of 3 adopt), so it cannot go green by refusing |
| axis tables emptied | **FAIL** (the enumerator arm), so it cannot go green by skipping |
| a new `house_*` keyword on `step` | **FAIL** (the enumerator arm names it) |

The oracle stand-in turns any admission that is more than the bar off the plant into a refusal. No
production fix exists yet, so "passing once fixed" is shown only with this stand-in. The F4.2 fixer
owes the real run on their fixed gate.

## Plan fold

- **Landing PR:** F4.2, as planned. The barrier lands with the instance fixes in one PR.
- **Files:** `tests/features.py` only, which is not code-owned and not policy. Test lines: +79/−4
  (prototype). Production lines: 0. The fix is F4.2's.
- **New open seam (orchestrator's call):** heavy_old slab mass 0.5×. If it is counted, P5 goes
  N 3 → 4, still inside F4.2. Either way the barrier as written is red until F4.2's gate refuses it
  too. The alternative is to carry it by name to a later PR, which fixer.md step 14 would make an
  allow-list keyed to be blind. I recommend F4.2 fixes it.
- **Constraint on F4.2 (a carry into F4.2's brief before this lands):**
  - A fix that feeds the learned free-heat profile into the prior needs `coordinator.py` (the
    `gains_prior_kw` construction). Per F4.2's brief, that part goes back to F1.
  - The R9-P5 check deliberately leaves out the #1524 check's `peak <= 0.8` clause. Aborted
    free-heat nights peak at 0.846 and 0.880 K (light_new and heavy_old two-zone). That is
    D2-s4-02's abort-at-sample seam, F4.2's own P2 finding, and it should not be judged by this
    class's check.
- **F1.4 lead (async_update_thermal_params):** this barrier does not cover it, and does not need
  to. It stays D1-s2-53's decision.
- **Needs tvofi:** nothing for the barrier. There is no budget raise, no policy change and no
  code-owned file.
- **PR set and `after` edges:** unchanged.
