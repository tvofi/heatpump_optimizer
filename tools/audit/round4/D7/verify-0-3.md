# D7 round 4 — verifier 3 of 3 (seat re-run)

- worktree: `/Users/timmalmstrom/.zcode/workspace/default/audit-r4-verify-D7-3`
  (detached at `3e91f85`, branch head of `claude/13-dimension-audit-920935`;
  findings were measured at baseline `7dd68dd` — per-cell reasons and all
  counts reproduce identically at the head)
- interpreter: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`,
  always `PYTHONPATH=tests/hastub`, always from the worktree root
- every number below is a count or a ratio. No timing number is claimed, so
  fan-out contention does not bear. `load1` at measurement time ranged
  2.30–12.02 (other panels were running); `thread_factor=1.0` on every run.
- harnesses I ran: the finder's `sysid_plant_r4.py` and
  `learner_freeze_r4.py` (re-run, exact), and three of my own:
  `verify3_own_D7-01.py`, `verify3_own_D7-02.py`, `verify3_own_D7-03.py`
  (written blind from the finder report; plants hand-typed from
  `presets.derive` output I executed myself, drivers my own).

## Code facts established by reading (before any run)

- `_adopt_system_identification` gates on exactly
  `result.completed and result.confidence >= 0.3`
  (`coordinator.py:10151-10154`).
- `_learning_frozen` (`coordinator.py:5162-5227`) consults
  `_external_heat_active`, `_pump_signals.freeze_reason`, per-key input
  health, and `_vent_cusum.tripped`. It never reads
  `self._pump_signals.defrosting`. `defrosting` is consulted in the
  package only by the two window observers (`:5072`, `:7327`), the derate
  window close (`:8757`), and `_learn_measured_cop`'s bespoke
  `in_frost_band`/`any_defrost` block (`:3396-3399`).
- `pump_signals.read` (`pump_signals.py:290-324`) resolves `defrosting`
  from the optional defrost entity, while `freeze_reason` can only be
  `pump_offline` / `pump_fault` / `pump_cooling` (`:302-313`). A defrosting,
  online, unfaulted heating pump yields `defrosting=True,
  freeze_reason=None` — the gate passes. Reachable on any install that
  configures the v5.3.0 defrost slot.
- `sysid._sizing_model` (`sysid.py:96-113`) builds its plant without the
  slab pair, so they sit at `ThermalParameters` defaults `5.0` kWh/°C and
  `0.8` kW/°C (`const.py:905-906`). The three shipped stress presets carry
  (0.24, 0.24), (23.0, 2.0), (16.5, 1.5) — I re-derived all three through
  production `presets.derive`. `light_new` is reachable from the config
  flow's `building_preset` page (`config_flow.py:1038 _derive_preset`).

---

## D7-01 — sysid experiment adopts 0 of 18 cells — **vote: verify (medium)**

**Re-run (finder's harness, exact).** `adopted_cells=0` over `grid_cells=18`;
six `light_new` cells abort on excursion, twelve fail the fit's own guards;
`sse1_over_sse2` 40.68–154.98; null control `null_onestate_adopted=1` at
confidence 0.940, bias +5.58 %. Every stated value reproduced exactly
(tolerance ±0). load1 2.44.

**Perturbation, executed.** `HPO_D7_SLABK=100` → `adopted_cells` 0 → 9
(`adopted_cells_dt0.25=6`, `dt0.5=3`). Direction up, as stated.

**My own harness** (`verify3_own_D7-01.py`; hand-typed plants, my own
driver, same metric definition: cells where `completed and confidence>=0.3`):
`v3_adopted_cells=0` of 18. Reason split 6 aborts / 11 sign-failures /
1 gains-failure — one `heavy_old` −5 °C cell reports "fitted gains outside
plausible bounds" instead of "implausible signs" under my driver; both are
the fit's own guards, and the adopted count is identical.

**Attacks (contract order).**

- *Contention*: counts only; immune.
- *Wrong gate mode*: the predicate I scored against is the production one
  at `coordinator.py:10154`, read in the file, not re-invented.
- *Aggregate artefact*: a zero over 18 cells cannot be cell-carried; the
  per-reason taxonomy shows two independent failure classes both present.
- *Null control*: the one-state arm adopts at 0.940 — the instrument can
  adopt; a harness that could only print zero would not.
- *Reachability*: opt-in (`DEFAULT_SYSID_ENABLED=False`, `const.py:463`),
  then `_run_system_identification` → `step` → `identify` → adopt, all
  production. My/finder's settle phase holds the plant exactly at
  equilibrium — strictly more favourable than a real plan, and it still
  fails. Sensor noise (σ=0.02 °C arm) makes it no better: still 0/18.
- *Severity*: medium is earned. The feature is opt-in and adopts nothing,
  so no wrong parameter reaches a plan; what is lost is the whole feature
  on every shipped preset plus the night it spends running. Attack arms
  strengthen the structural claim rather than rescuing adoption:
  `HPO_V3_SLABK=10` (10× tighter slab coupling) still 0/18;
  `HPO_V3_BOUND=2.0` (user doubles the comfort allowance) still 0/18;
  noise 0/18.

## D7-02 — sizer's plant is not the house's plant, comfort bound breached — **vote: verify (medium)**

**Re-run (finder's harness, exact).** `comfort_breach_cells=6` (all six
`light_new` cells), `peak_ratio_min=0.486`, `peak_ratio_max=1.329`,
`honest_sizer_breach_cells=0`, `honest_sizer_peak_ratio_max=1.000`. Exact.

**My own harness** (`verify3_own_D7-02.py`; drives the production
`_size_step_power` directly rather than the full state machine, truth
simulated on a 0.05 h grid of my own): breaches 3 of 9 cells (9 = the
finder's 18 minus the cadence dimension, which the sizer does not see;
the same `light_new` cells). Ratio range 0.509–**3.037**, worst TRUE peak
**2.428 °C** against the 0.8 allowance. Honest counterfactual: 0 breaches,
ratio ≤ 0.99.

Two metric definitions now recorded for the judge: the finder's is the
peak *realized inside the protocol* (the per-cycle `_over_excursion` abort
active, capping `light_new` at ~1.06 °C); mine is the *potential of the
sized step* with the abort disabled (2.43 °C). They agree on the cause and
the direction; mine shows the production abort — not the sizer — is what
limits the realized excursion.

**Perturbation, executed.** The harness-side honest sizer (carries the
plant's own slab pair) drops breaches to 0 and ratio to ≤1.00 in both my
run and the finder's. Direction down.

**Attacks.** *Aggregate*: the breaches are all `light_new`; drop that
preset and the count is 0 — but `light_new` is a shipped, config-flow
archetype (timber crawlspace, post-2005) and the finding names it; the
other 12 cells carry the mirror-image defect (ratio ≈ 0.5, half the
permitted excitation), so the grid is not one-carried. *Null control*:
honest-sizer arm. *Reachability*: `_begin_step_phase` → `_size_step_power`
in production; the abort `_over_excursion` is also production and fires
one interval past the bound (verified: all six breach cells end in
"room temperature drifted beyond the allowed excursion"). *Severity*:
medium is earned — realized excursion 1.01–1.06 °C vs the "not negotiable"
0.8 °C bound (+33 %), on an opt-in night experiment, aborted one interval
in; the unmitigated potential is 3×. Not high: opt-in, sub-degree realized,
self-aborting.

## D7-03 — `_learning_frozen` never consults `defrosting`, 3 of 4 learners ingest — **vote: weaken (medium)**

**Re-run (finder's harness, exact).** `ingesting_cells_defrost=3` of
`live_learner_cells=20`, `positive_control_dead_learners=0`; external heat /
open window / pump fault all 0; `perturbed_ingesting_cells_defrost=0`.
Exact.

**My own harness** (`verify3_own_D7-03.py`), different observables:

- *At the gate itself*: `_learning_frozen` returns `None` for a defrosted
  interval and the correct reason string for each of the three known
  contaminants (`pump_offline` / `external_heat_source` / `ventilation`).
- *At downstream production seams*: `_apply_house_heat_loss_scale` is
  called (1) for a defrosted interval and (0) under `pump_offline` — the
  fold executes, not merely the value moving. `_learn_measured_cop`'s
  bespoke guard holds (ratio-EWMA stays 1.200) and, with the guard
  stripped by making `in_frost_band` lie False, the EWMA moves to 1.220 —
  my own execution of the finder's opposite-direction perturbation.
  Buffer and DHW learners ingest defrost, freeze on offline.
- So: house, buffer, DHW ingest; COP is held only by its own bespoke
  block. 3 of 4, exactly as claimed, and the one-line fix arm holds
  everything frozen.

**The consequence the finder flagged as unmeasured — I measured it.**
Physically defrosted intervals (8 defrost minutes per 30, zero indoor
delivery, meter still reading the draw — the exact contamination the
docstring describes), replayed by the real learner with the real replay
path (`_interval_space_power` measured-power branch), sustained for 60 h
of defrost-every-interval weather (maximal, not typical):

- `light_new` (most exposed shipped preset): `_house_heat_loss_scale`
  1.000 → **0.9775**; all 120 samples folded, none rejected, the vent
  CUSUM never trips (per-sample residual ≈ 5e-4 °C, under the 0.08
  allowance), so nothing self-corrects. Walk is monotone and
  one-directional (down — the learner books the missing heat as a lower
  house UA).
- `typical_slab`: 1.000 → 0.9978.
- One-line fix arm: scale stays 1.0000.

**Why weaken.** The mechanism verifies exactly — the gate is missing the
one condition, three learners fold the flagged interval, the fix collapses
the column, and the flag is reachable in real HA (`pump_signals.read`
yields `defrosting=True` with `freeze_reason=None`). But "high" rested on
the consequence class with the magnitude explicitly unmade. The measured
magnitude on the flagship parameter is a ≤2.3 % UA mis-scale on the most
exposed preset under maximal sustained defrost, ~0.2 % on the typical one
— the 8-minute heat deficit is ~0.4 kWh against a 21.75 kWh/°C house, so
the room-level signal is intrinsically small. A 2 % UA bias is
second-order in plan cost. Real bug, clean one-line fix, persisted but
bounded bias: **medium**. Caveat I could not close: the buffer-tank and
DHW-learner magnitudes are unmeasured by either of us — whether a defrost
draws heat from the indoor tank is a hydraulics question this repository
cannot answer; if it does, the tank learners (0.58 kWh/°C) see a larger
relative signal and the judge may want that measured before medium is
final.

## Attack summary per contract

| attack | D7-01 | D7-02 | D7-03 |
|---|---|---|---|
| contention | counts, immune | counts/ratios, immune | counts, immune |
| wrong gate mode | production predicate read at `coordinator.py:10154` | sizer is production `_size_step_power`; abort also production | gate read at `coordinator.py:5162-5227`; no other defrost consult in package (grep) |
| aggregate artefact | 0/18, two failure classes both present | breaches all `light_new` — named by the finding, config-flow reachable; other 12 cells carry the mirror defect | 3/4 with 20/20 live controls |
| null / control | one-state arm adopts 0.940 | honest sizer 0 breaches | clean interval live; offline/external/vent all freeze; fix arm |
| reachability in real HA | opt-in config, all production path | opt-in config, `_begin_step_phase` path | defrost entity slot, `pump_signals.read` |
| severity by consequence | medium (feature dead, nothing adopted) | medium (1.06 realized / 2.43 potential vs 0.8, aborting) | weakened to medium (measured drift ≤2.3 % maximal, was unmeasured) |

## Votes

- D7-01: **verify**, medium.
- D7-02: **verify**, medium.
- D7-03: **weaken** to medium — mechanism verified exactly (3/4 ingestion,
  gate returns None, fix collapses it), severity high not earned: the
  unmade drift measurement is now made and reads ≤2.3 % on the most
  exposed preset under maximal sustained defrost.
