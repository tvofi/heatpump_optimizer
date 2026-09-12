# D7 round 4 — verifier 0-1 report (re-run seat)

- verifier seat: D7-0-1 (re-run of a seat that died mid-work; the stale
  worktree was removed and re-created from `claude/13-dimension-audit-920935`)
- tree: worktree `../audit-r4-verify-D7-1` at `0855277` (branch head)
- production code vs baseline:
  `git diff --stat 7dd68dd..HEAD -- custom_components/` touches only
  `manifest.json` and `www/heatpump-optimizer-card.js` (version stamps).
  **No `.py` under `custom_components/` differs from the baseline**, so the
  baseline numbers apply to this tree. Cited by both harnesses' root rule
  (`Path(".")`), run from this worktree's root throughout.
- interpreter: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`,
  always `PYTHONPATH=tests/hastub`, from the worktree root.
- box: load1 3.99–5.37 across all runs (quoted per harness), 2–6 concurrent
  audit processes observed and quoted per harness. **Every number below is a
  count, a sign, or a ratio** — no timing number is claimed by the finder or
  by me, so contention does not bear on any figure.

## What I ran

| run | command | result |
|---|---|---|
| finder D7-01/02 harness | `PYTHONPATH=tests/hastub python3 tools/audit/round4/D7/sysid_plant_r4.py` | every EXPECTED value reproduced exactly (below) |
| finder D7-01 perturbation | `HPO_D7_SLABK=100 … sysid_plant_r4.py` | `adopted_cells` 0 → 9, direction up, as stated |
| finder D7-03 harness | `PYTHONPATH=tests/hastub python3 tools/audit/round4/D7/learner_freeze_r4.py` | every EXPECTED value reproduced exactly (below) |
| own harnesses | `d7_own_D7-01.py`, `d7_own_D7-02.py`, `d7_own_D7-03.py` (beside the finder's, this directory) | RESULT lines below |

Note on the D7-03 harness list: the finding cites `learner_freeze_r4.py` and
`_sentinel_run.py`. `_sentinel_run.py` is written and executed by
`dead_methods_r4.py` and supports the dead-methods **non-finding**; it carries
no D7-03 evidence. I re-ran `learner_freeze_r4.py` and reviewed
`_sentinel_run.py`; I did not re-run the dead-methods screen (no finding rests
on it).

## D7-01 — sysid adopts 0 of 18 cells — VOTE: verify (medium)

**Finder harness re-run (exact reproduction, load1 5.26, thread_factor 1.0):**
`grid_cells=18`, `adopted_cells=0`, `comfort_breach_cells=6`,
`peak_ratio_min=0.486`, `peak_ratio_max=1.329`, `peak_ratio_mean=0.760`,
`peak_ratio_loo_mean=0.735`, `sse1_over_sse2_min=40.68`,
`sse1_over_sse2_max=154.98`, `honest_sizer_breach_cells=0`,
`honest_sizer_peak_ratio_max=1.000`, `null_onestate_adopted=1`,
`null_onestate_bias_pct=5.58`. Every figure inside the stated tolerance ±0.
Perturbation `HPO_D7_SLABK=100`: `adopted_cells` 0 → 9 (finder said 0 → 9;
direction up confirmed).

**My own harness (`d7_own_D7-01.py`, load1 4.98, 6 concurrent procs):**
independent drive loop — 400 h dynamic pre-roll to the hold equilibrium (not
the finder's analytic steady state), own closed loop, own adoption predicate.
- `own_grid_cells=18`, `own_adopted_cells=0` — same count from a different
  construction.
- Failure census (mine, matching the finder's): 6 × "room temperature drifted
  beyond the allowed excursion" (all `light_new`), 11 × "fit gave implausible
  signs", 1 × "fitted gains outside plausible bounds".
- `own_null_slabk100_adopted=9` — the collapse perturbation executed
  in-process; adoption returns. The instrument can adopt.
- Attack arm, cadence outside the finder's grid: `own_adopted_cells_dt1h=0`
  of 9 at a 1 h cadence — the 0-adoption result extends beyond the claimed
  grid, it is not a cadence artefact of the 15/30-min pair.
- Exploratory second null: `own_null_smallmass_adopted=0` — collapsing the
  plant from the mass side (slab mass ×0.01) does **not** rescue adoption.
  The rescue is specific to the coupling-side collapse; worth knowing, but the
  primary null stands and the failure census shows two distinct guard
  failures, not a knife-edge.

**Metric definitions.** Finder: count of (preset × outdoor × cadence) cells
with `SysIdResult.completed and confidence >= 0.3` — the exact gate at
`coordinator.py:_adopt_system_identification` (verified in source:
`if not result.completed or result.confidence < 0.3: return`). Mine: same
gate, different drive (pre-rolled equilibrium, own loop), same 3×3×2 grid.
The counts are directly comparable.

**Attacks run.**
1. *Contention* — all figures are counts; load1 quoted; nothing rests on
   timing.
2. *Grid artefact* — 0 in every cell; nothing can carry it; the dt=1 h arm
   extends the result to a fourth cadence.
3. *Null control* — executed twice over (finder env-var arm, my in-process
   arm): 9 of 18 adopt on the collapsed plant at confidence up to 0.94. A
   harness that can only print zero is ruled out.
4. *Causal story* — the "wrong-sign slope" prose refers to the four-column
   fit's `ua_over_c ≤ 0` (the 11 "implausible signs" cells are that claim,
   executed). I attacked it with my own probe: a relax-window-only OLS of rate
   on ΔT comes out **negative** (physically signed) in every finite cell
   (`own_wrongsign_relax_cells=0`) — the sign flip lives in the combined
   settle+step+relax regression (step-phase rows: room rising at high ΔT), not
   in the relax window alone. The finder's prose compresses this; the executed
   evidence (guard reasons, sse ratio 41–155×) is unaffected.
5. *Reachability* — the coordinator path is real (`_run_system_identification`
   passes `house_ua/house_capacity/house_gains` from `_thermal_params`; the
   harness passes the same). Opt-in confirmed: `DEFAULT_SYSID_ENABLED = False`
   (const.py:463), armed only via `async_arm_system_identification`.
6. *Severity* — medium is right: the feature fails safe (adopts nothing
   rather than wrong values); what is lost is the entire opt-in feature plus
   the experiment night.

**Vote: verify, medium.** Executed value: `own_adopted_cells=0` of 18 (finder
harness re-run: 0 of 18; perturbation 0 → 9).

## D7-02 — the sizer's plant is not the house's plant — VOTE: verify (medium)

**Finder harness re-run:** exact reproduction (same run as D7-01):
`comfort_breach_cells=6`, `peak_ratio_min=0.486`, `peak_ratio_max=1.329`,
`honest_sizer_breach_cells=0`, `honest_sizer_peak_ratio_max=1.000`.

**My own harness (`d7_own_D7-02.py`, load1 4.14, 6 concurrent procs):**
- Static: `own_sizer_default_slab_cells=18`, `own_sizer_plant_mismatch_cells=18`.
  Production `_sizing_model(ua, capacity, gains)` returns slab
  `(5.0, 0.8)` — the `ThermalParameters` defaults (const.py:905-906) — in
  every cell, while the presets' plants carry `(0.24, 0.24)` (`light_new`),
  `(23.0, 2.0)` (`heavy_old`), `(16.5, 1.5)` (`typical_slab`). The finder's
  quoted tuples are exactly right. The coordinator passes the house's real
  UA/mass/gains one frame up (`coordinator.py:_run_system_identification`)
  and drops the slab pair; the fix is a parameter pass.
- Dynamic: `own_comfort_abort_cells=6` — counted by the module's **own**
  abort ("room temperature drifted beyond the allowed excursion"), not by my
  threshold; all six are `light_new`. `own_max_excursion_over_bound=1.328`
  (≈1.06 °C against the 0.8 °C bound the module docstring calls
  "not negotiable"). The finder's 1.01–1.06 °C is the same physics measured
  at the abort sample; my loop takes one extra plant step past detection, so
  my ceiling is higher — both constructions breach.
- Counterfactual, executed in-process: honest sizer (harness-side swap
  carrying the plant's own slab pair) → `own_honest_comfort_abort_cells` = 0
  on the finder's arm (3 presets, dt 0.25; `light_new` 0.998 of bound) and
  **1 on my wider arm** (dt 0.5: `light_new` at 1.018 of bound — a 1.8 %
  margin, versus 33 % over for the production sizer at the same cell).
  `own_honest_max_excursion_over_bound=1.018`.

**Two nuances the finder's report overstates; neither touches the core.**
1. `honest_sizer_breach_cells=0` was measured on a 3-cell arm (dt 0.25). At
   dt 0.5 the honest sizer still breaches by 1.8 % on `light_new` (sizer
   predicts with a 0.25 h rollout; coarser plant steps overshoot it). The fix
   collapses the breach 33 % → 1.8 %; it does not perfectly eliminate it
   across all cadences.
2. The secondary claim "heavy_old and typical_slab gather about half the
   excitation permitted" holds for `typical_slab` only (production achieved
   0.52 of bound vs 0.95 available under the honest sizer). For `heavy_old`
   the honest step is **power-capped** at max electrical power
   (`own_honest_power_capped_presets=2` = heavy_old, typical_slab): both
   sizers already command the 6 kW maximum there and the achieved excursions
   are the same (0.36 vs 0.36 of bound). The sizer bug has no dynamic effect
   on `heavy_old`; the excitation-halving argument does not apply to it.

**Attacks run.** Grid artefact: the breach is the whole `light_new` column
(6/6 of its cells, both cadences, all three outdoors) — a preset property,
not an outlier cell; drop-any-one leaves ≥5. Null control: executed (honest
sizer, both by the finder and by me). Reachability: preset-derived slab pairs
land in the real config entry (config_flow.py:1058 `presets.derive(preset)`
merged into the entry), so real installs carry non-default slab values; the
feature is opt-in, and the severity (medium, comfort excursion caught one
interval late on an opt-in night experiment) accounts for both.

**Vote: verify, medium.** Executed value: `own_sizer_default_slab_cells=18`
of 18 with the wrong slab pair; `own_comfort_abort_cells=6` of 18
(production's own comfort abort); counterfactual 6 → 0 on the finder's arm,
6 → 1 (1.8 % margin) on my two-cadence arm.

## D7-03 — the learner freeze never consults `defrosting` — VOTE: verify (high)

**Finder harness re-run (exact reproduction, load1 5.37):**
`live_learner_cells=20`, `positive_control_dead_learners=0`,
`ingesting_cells_defrost=3`, `ingesting_cells_external_heat=0`,
`ingesting_cells_open_window=0`, `ingesting_cells_pump_fault=0`,
`ingesting_cells_away=4`, `perturbed_ingesting_cells_defrost=0`. Table
identical: house/buffer/DHW ingest the defrost interval; measured_cop refuses
via its own `in_frost_band`/`any_defrost` block (coordinator.py:~3397).

**My own harness (`d7_own_D7-03.py`, load1 4.43, 2 concurrent procs):**
independent interval shapes (deeper fall: residual ≈ −0.5 °C), own probes.
- Static: `own_gate_open_defrost_only=1` — production `_learning_frozen`
  returns `None` with only `_pump_signals.defrosting=True` set, while fault
  returns `pump_fault` and a tripped vent CUSUM returns `ventilation`.
  Source-verified: `_learning_frozen` (coordinator.py:5162) consults external
  heat, `freeze_reason` (offline/fault/cooling only — pump_signals.py:302-313
  never sets it for defrost), input health, and the vent CUSUM; `defrosting`
  is read every cycle at coordinator.py:5071-5072 and nowhere near the gate.
- Ingestion: `own_ingest_defrost=3` of 4 live learners (house heat loss,
  buffer cooling, DHW dynamics); `own_ingest_fault=0`; all four clean
  positive controls live.
- Direction (the one-directional-bias claim, executed): 20 consecutive
  defrost-shaped folds of the house learner — every fold that moves the
  persisted `_house_heat_loss_scale` moves it **up**.
- Perturbation A (the one-line fix, executed): patched gate returns
  "defrosting" → `own_perturbed_ingest_defrost=0`, walk up-steps 0.
- Perturbation B (the finder's described opposite direction, executed):
  `in_frost_band` forced False in the coordinator namespace (removing
  `_learn_measured_cop`'s bespoke guard) → the COP learner ingests the
  defrost interval: `own_reverse_perturb_cop=1` (3 → 4).

**The drift magnitude the finder left unmeasured — measured here.**
- Contiguous contamination (defrost every interval): the open-window CUSUM
  (`side=-1` — it watches negative residuals, which is the defrost
  signature) latches at fold 4: `own_walk_ups=4`, `own_walk_drift_pct=4.00`,
  `own_walk_vent_trip_fold=4`. A coincidental, mislabelled partial
  mitigation: it freezes every learner as "ventilation" and the corrupted
  scale is what gets persisted on the trip path.
- Defrost every 3rd interval, whole-interval deficit: latch at fold 18,
  6 ingested folds, `own_walk_intermittent_drift_pct=6.00`.
- **Realistic small deficits (0.15 °C per defrost, every 3rd interval): the
  CUSUM never latches** (`own_walk_small_vent_trip_fold=0` — the 0.08 °C/h
  drift allowance absorbs 0.15 °C every third hour), all 20 defrost folds
  ingest upward (`own_walk_small_ups=20`), and the scale walks
  `own_walk_small_drift_pct=20.00` and is still climbing at the end of the
  run. Construction caveat, stated honestly: my clean folds are
  model-consistent by construction, so they exert no downward pull; the +20 %
  endpoint is an upper envelope. The construction-independent results are
  (a) the latch does not fire at realistic per-interval deficits and (b)
  every contaminated fold moves the persisted scale in one direction.

**Attacks run.** Positive control live on every cell; negative control
(fault) freezes all; reachability — the flag arrives from
`pump_signals.read()` in a real cycle when the user configures the optional
defrost entity, and the learners run from the real update cycle; no FakeHass
executor/coroutine seam is involved in the gate logic. The DHW column of the
3-of-4 is mechanically open but physically the weakest contamination (a
defrost pulls heat from the space circuit, not the DHW tank) — a nuance, not
a refutation; the house heat-loss column alone carries the severity.

**Severity.** The finder rated high while flagging the magnitude as owed. My
anchors: default-on learners (only the defrost **entity** is optional); a
persisted parameter that prices every plan; ingestion ungated and
one-directional; at realistic deficits no latch fires and the walk is
unbounded within an episode; recurring every frost episode (0–5 °C band =
common heating weather); the failure class is the one
`_learning_frozen`'s own docstring names; the fix is one line of the same
shape as the three pump-signal conditions already there. High stands.

**Vote: verify, high.** Executed value: `own_ingest_defrost=3` of 4 live
learners ingest a defrost-flagged interval; `own_gate_open_defrost_only=1`;
`own_walk_small_ups=20` of 20 defrost folds move the persisted scale up with
no latch at realistic deficits.

## Summary of votes

| id | vote | severity | my executed number |
|---|---|---|---|
| D7-01 | verify | medium | `own_adopted_cells=0` of 18 (null arm 9 of 18; dt=1 h arm 0 of 9) |
| D7-02 | verify | medium | `own_sizer_default_slab_cells=18` of 18 wrong slab pair; `own_comfort_abort_cells=6` of 18 (counterfactual: 0 on the finder's arm, 1 at 1.8 % on my wider arm) |
| D7-03 | verify | high | `own_ingest_defrost=3` of 4 learners; `own_walk_small_ups=20` of 20 defrost folds up, vent latch never fires at 0.15 °C deficits |

All harnesses (finder's and mine) live in `tools/audit/round4/D7/` in this
worktree, uncommitted. Every number is a count or ratio; `load1` and the
concurrent-process count are quoted per run; no timing-based refutations are
claimed or needed.
