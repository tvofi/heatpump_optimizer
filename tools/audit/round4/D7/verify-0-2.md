# D7 — verifier 2 of 3, panel D7-0, round 4

- worktree: `../audit-r4-verify-D7-2`, detached at branch head `0855277`
  (findings were measured at baseline `7dd68dd`; reproduction at head
  confirms nothing moved on these paths)
- interpreter: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`,
  always `PYTHONPATH=tests/hastub`, always from the worktree root
- stance: refute-first; finder's harnesses re-run, then attacked, then
  re-measured with a harness I wrote myself
  (`tools/audit/round4/D7/verify2_independent_r4.py`, in this worktree,
  uncommitted). Its root rule is `Path(".")` — it measures the working
  directory, and I ran it from this worktree.
- every number below is a count or a deterministic float. No timing is
  claimed by the finder or by me; `load1` ran 4.2–7.1 during my runs
  (quoted, not gated — the box is shared with other solve-heavy verifiers).

## Re-runs of the finder's harnesses (exact, ±0 on every line)

`PYTHONPATH=tests/hastub python3 tools/audit/round4/D7/sysid_plant_r4.py`:

| line | finder | mine |
|---|---|---|
| grid_cells | 18 | 18 |
| adopted_cells | 0 | 0 |
| comfort_breach_cells | 6 | 6 |
| peak_ratio_min / max | 0.486 / 1.329 | 0.486 / 1.329 |
| honest_sizer_breach_cells | 0 | 0 |
| honest_sizer_peak_ratio_max | 1.000 | 1.000 |
| null_onestate_adopted / bias | 1 / +5.58 % | 1 / +5.58 % |
| sse1_over_sse2_min / max | 40.68 / 154.98 | 40.68 / 154.98 |

`PYTHONPATH=tests/hastub python3 tools/audit/round4/D7/learner_freeze_r4.py`:
`live_learner_cells=20`, `positive_control_dead_learners=0`,
`ingesting_cells_external_heat=0`, `_open_window=0`, `_pump_fault=0`,
`ingesting_cells_defrost=3`, `perturbed_ingesting_cells_defrost=0` —
all exactly as filed.

## My own harness (one per finding, my metric definitions)

`PYTHONPATH=tests/hastub python3 tools/audit/round4/D7/verify2_independent_r4.py`,
header carries metric / command / expected / instrumented symbols. Key RESULTs:

```
RESULT my_relax_rise_cells=6 of 6 count        (cells that reached relax)
RESULT my_relax_rise_max_c=0.117 celsius
RESULT my_adopted_cells=0 of 9 count           (production 30-min cadence)
RESULT my_null_relax_rise_c_dt025=0.0000 celsius; my_null_adopted_dt025=1
RESULT my_null_relax_rise_c_dt05=0.0000 celsius; my_null_adopted_dt05=0
RESULT my_breach_cells=3 of 9 count            (light_new, dt=0.5, no abort)
RESULT my_peak_ratio_min=0.509 ratio; my_peak_ratio_max=3.037 ratio
RESULT my_starved_cells=3 count; my_honest_breach_cells=0 count
RESULT my_gate_passes_defrost=1 bool; my_gate_fault_control=1 bool
RESULT my_ingest_defrost_moved=1; my_ingest_clean_moved=0; coldctrl=1
RESULT my_drift_week_defrost_pct=+0.191 percent        (default house)
RESULT my_drift_week_heavy_pct=+0.509 percent
RESULT my_drift_week_lightnew_heavy_pct=+2.785 percent
RESULT my_drift_3week_lightnew_heavy_pct=+2.860 percent (saturated)
RESULT my_drift_week_fixed_pct=-0.298 percent          (fix arm)
RESULT my_vent_tripped=0 bool
```

The drift week: 336 x 30-min intervals at +2 C, plant = the coordinator's
own configured `ThermalModel` (scale frozen at truth), learner = the
production `_async_learn_house_heat_loss`, every 4th (moderate) or every
2nd (heavy) interval carrying a 10/15-min zero-delivery defrost, clean
substepped control week carrying the identical discretisation.

---

## D7-01 — sysid adopts 0 of 18 cells (medium, bug)

**Vote: verify.** Number: `adopted_cells=0/18` (finder's harness, exact)
and `my_adopted_cells=0/9` at the production 30-min cadence (my harness).

Attacks, in the contract's order:

1. *Contention* — counts only; deterministic; reproduced bit-for-bit.
2. *Wrong gate mode* — not a suite-gap claim; N/A. The adoption criterion
   in the harness mirrors production exactly: `coordinator.py:10154`
   `if not result.completed or result.confidence < 0.3: return`.
3. *Aggregate artefact* — 0 in every cell of both grids (3 presets x 3
   outdoors x 2 cadences; mine 9 cells at dt=0.5). No subset carries it;
   dropping cells cannot move a uniform zero.
4. *Null control* — present and passing: the collapsed plant (slab
   coupling x100) adopts at confidence 0.940, bias +5.58 %, reproduced
   exactly by my own drive loop (`my_null_adopted_dt025=1`), which
   validates my loop against the finder's. **Caveat I add:** the finder's
   null was taken at the 15-min cadence; at the production 30-min cadence
   my null does NOT adopt (`my_null_adopted_dt05=0`, "fitted gains outside
   plausible bounds"). This does not weaken the finding — it strengthens
   the inertness claim (the instrument is inert even on its most
   favourable plant at the default cadence) — but the null's framing as
   "the instrument can adopt" is cadence-conditional.
5. *Reachability* — the sysid path is real: `_run_system_identification`
   runs every solve (`coordinator.py:4652`) and passes exactly the
   house figures the harness passes (`:10127-10132`); arming is the
   `async_arm_system_identification` service and the feature is opt-in
   (`DEFAULT_SYSID_ENABLED = False`, const.py:463) — the finder's medium
   already prices that. The plant the harness identifies is the
   integration's own `ThermalModel` — the same model the sizer itself
   rolls out (`_predict_step_excursion_plant` simulates on it) — so this
   is a self-consistency test of the integration against its own nominal
   plant, which is the correct target.
6. *Severity earned* — medium is right: the feature fails closed (aborts
   or refuses adoption; no wrong parameter reaches a plan); what is lost
   is the feature itself plus the night it spends.

My own mechanism check (independent of the finder's two-exponential fit):
on a first-order heating plant, with Q=0 and T above its steady state the
room rate must be negative — the room cannot rise during a zero-power
relax. Measured: all 6 cells that reach relax rise (max +0.117 °C on
typical_slab; heavy_old +0.18–0.26 °C), while the collapsed null rises
0.0000 °C at both cadences. The two-state mechanism is real, and the
failure reasons split exactly as filed (6 excursion aborts = the light_new
cells = the D7-02 breach; 12 sign/guards failures on the rest). I also
note, for the judge, a production seam my loop exposed: the step→relax
transition call still returns the step power (`sysid.py:566-571`), so the
step phase actually powers 2.25–2.5 h against a 2.0 h `step_hours` —
immaterial to this finding, possibly its own small finding.

## D7-02 — `_sizing_model` uses default slab constants; comfort bound breached (medium, bug)

**Vote: verify.** Number: `comfort_breach_cells=6/18` (finder, exact);
`my_breach_cells=3/3` light_new cells at dt=0.5 with `my_honest_breach_cells=0`.

Attacks:

1. *Contention* — counts and ratios; deterministic.
2. *Wrong gate mode* — N/A.
3. *Aggregate artefact* — the 6 breaching cells are exactly the 6 light_new
   cells; drop light_new and breaches go to 0. That is not an artefact, it
   is the physics: light_new is the preset whose real slab coupling
   (0.24 kW/°C) is 3.3x weaker than the sizer's default (0.8; mass 0.24 vs
   5.0 — presets verified via `derive()`). On the other two presets the
   same wrong plant mispredicts the other way (ratio 0.51, `my_starved_cells=3`:
   roughly half the permitted excursion) — the bug is universal, the breach
   is preset-specific, and the finder reported exactly that split.
4. *Null/counterfactual* — the honest sizer arm is executed and I
   reproduced it my own way (direct `_size_step_power` + fine-grained
   rollout, no state machine): `my_honest_breach_cells=0`, honest peaks
   0.70–0.79. Direction of the perturbation as filed.
5. *Reachability* — `building_structure`/`building_era` are user config
   (`const.py:471-472`), config_flow runs `presets.derive` into the entry,
   so light_new is a real user house. The breach needs sysid enabled+armed
   (opt-in), which medium prices.
6. *Severity earned* — medium is right, and my unbounded measurement
   sharpens why: with no abort, the sized step drives light_new to
   **2.42–2.43 °C** (`my_peak_ratio_max=3.037`) — 3x the 0.8 °C allowance
   the module docstring calls "not negotiable". What bounds it in
   production is `_over_excursion`, checked once per cycle, which catches
   it at 1.01–1.06 °C (finder's trace; reproduced). So the real consequence
   is a ~0.2–0.26 °C overshoot past the allowance for one 30-min interval
   before the abort — a comfort excursion on an opt-in night experiment,
   then the experiment dies. Medium.

One attempted refute worth recording: `_sizing_model`'s docstring says the
defaults "is the two-state plant the experiment actually runs on" — a
documented choice, not an accident. But the experiment runs on the user's
configured house, whose slab pair the integration itself derives (0.24/0.24
for light_new), and the measured consequence contradicts the docstring's
own comfort constraint. A documented choice that breaches its own
non-negotiable bound is a bug by consequence; #779 moved the sizer from
one-state to two-state for exactly this reason and stopped at the wrong
constants.

## D7-03 — `_learning_frozen` never consults `defrosting`; 3 of 4 learners ingest (high, bug)

**Vote: verify.** Numbers: `ingesting_cells_defrost=3` of 20 live cells,
`perturbed_ingesting_cells_defrost=0` (finder's harness, exact);
`my_gate_passes_defrost=1` (a direct one-call read of
`_learning_frozen` with only `_pump_signals.defrosting=True` returns
`None` — the gate passes the interval; the fault control returns its
reason); `my_ingest_defrost_moved=1` with `my_ingest_clean_moved=0`.

Attacks:

1. *Contention* — exact deterministic counts.
2. *Wrong gate mode* — N/A.
3. *Aggregate* — a 4x5 matrix with a per-learner live control; the three
   other contaminants read 0 and defrost reads 3. No cell structure can
   produce that by artefact.
4. *Null/positive controls* — cleanest available: the finder's per-learner
   clean controls all move; my clean week leaves the scale at exactly
   1.000000 (336 samples, zero folds) while the defrost week moves it; the
   cold control (a legitimate −0.2 °C residual) moves it +1 % in one
   interval, proving the cell is live.
5. *Reachability in real HA* — the strongest attack available, and it
   fails to rescue the gate: `pump_signals.py` sets `freeze_reason` only
   for online=False, fault=True, or observed cooling (`:302-313`); a
   defrosting flag on an otherwise healthy heating pump leaves
   `freeze_reason=None`, so the harness's isolated contamination is
   exactly a real defrost cycle. The flag is real config
   (`heat_pump_defrost_entity`, v5.3.0, 30-min horizon), the coordinator
   reads it every cycle and folds it into `_defrost_window`
   (`coordinator.py:5071`), and the learners run every cycle from the
   update flow (`:5120`). Without the entity configured the exposure is
   worse, not better: real defrosts are then simply undetected. The
   `FakeHass` trap does not apply — no executor boundary on this path.
6. *Severity earned by consequence* — the finder set high and flagged the
   magnitude as unmeasured. I measured it (the measurement the finder
   owed): a closed defrost week through the production learner moves the
   persisted `_house_heat_loss_scale` **+0.19 %** (default house,
   10-min defrost every 2 h), **+0.51 %** (heavy: 15 min every hour), and
   **+2.79 % in week 1, +2.86 % at three weeks — saturated** on the
   light_new preset under heavy frost. Direction always up (heat loss
   overestimated), the ventilation CUSUM never trips
   (`my_vent_tripped=0`; threshold 1.2 °C vs per-interval defrost
   residuals of ~0.02–0.06 °C), the clamp is far away (0.3–3.0), and the
   value persists across restarts. The one-line fix removes the
   defrost-attributable part (the fix arm lands at my discretization
   control level, −0.30 %, which the clean-substepped control shows is an
   artifact of my plant's 1-min granularity, not a defrost effect).

   So: worst-case shipped preset, heavy-but-plausible frost regime, a
   persistent ~3 % one-directional overestimate of the heat-loss
   coefficient that prices every plan; typical install ~0.2–0.5 %. That
   is a real, measured, persisted consequence plus exactly the failure
   class the gate's own docstring exists for ("corrupts a parameter that
   is persisted to disk"). High stands on class + the light-house
   magnitude; a judge anchoring strictly on the typical-install magnitude
   could argue medium. I record both numbers and keep high.

   Caveats on my method, stated: my defrost is modeled as zero delivery
   for the defrost minutes (a reversed cycle can do worse); my drift
   covers the house-loss learner only — the finder's DHW and buffer
   ingestion cells are verified as ingestion, not as drift.

## What I could not refute, and one instrument note

- Both finder harnesses reproduce exactly; every attack I ran (aggregate,
  null, reachability, counterfactual, mechanism) confirmed the filings.
- Instrument note for the judge, not a filed finding: my first Section-A
  metric was wrong until fixed — the step→relax transition call returns
  the step power, so a naive "relax-labelled" rise measures sequencing,
  not physics. Any future harness measuring the relax window must gate on
  the applied power being zero, as mine now does.
- `learner_freeze_r4.py`'s opposite-direction perturbation (delete the
  bespoke `in_frost_band` block, 3 → 4) is asserted in the header but not
  executed by the harness; the main perturbation is executed, and my code
  read of `coordinator.py:3396-3399` confirms the block is the COP
  learner's only defrost guard.
