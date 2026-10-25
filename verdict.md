Design review: revise 04de6ae7f818646a132e5e82074b3bd6fa29bb3b product-tradeoff-regression

Reviewed: `dev/programme/designs/R10-HEAT-METER.md` at `design/R10-HEAT-METER` 04de6ae7f, round 1 of 3, from a detached worktree at that SHA. Code read at main da12aa37d and at #2753's head 8a133f390. Token count: not reported by this harness. Line numbers `note:N` are the note's; code lines are at 8a133f390.

## Revise points

1. **product-tradeoff-regression: the mode entity is a selector, not an activity signal** (note:58-70). `pump_mode.py:1-13` and `docs/configuration.md:96` describe the pump's own mode selector, and `_cop_reference_curve`'s docstring (coordinator.py:4905-4908) says `HEATDHW`/`COOLDHW` run both duties at once. Under either combination mode every read classes `blended` (both flags set, `concurrent=True`). The design then gives a worse result than #2753 on every heat-metered install in that mode:
   - the house replay gets `None` on every interval (note:64), where #2753 replays measured heat on commanded space-only intervals (coordinator.py:928-931);
   - the COP bin always returns `COP_REFUSED_BLENDED` (note:67), where #2753 bins by the commanded split (coordinator.py:4922-4935);
   - `replay_freeze` never lifts;
   - the re-anchor (note:70) voids the learned scale for a meter the replay then never uses.
   With the options-step refusal (note:69), the required mode entity is strictly worse than leaving it empty, because "not observed" keeps #2753's rule (note:65). A self-initiated hot-water charge under a combination mode leaves the selector unchanged. Note:66's claim to close #2753's carry "for every pump whose mode shows the charge" therefore closes it there only by refusing everything.
   **Fix wanted:**
   - State the selector semantics.
   - Take dwell shares only from single-duty modes and from `mode_owned` writes, which are the arbiter's step decisions (pump_signals.py:233-238).
   - Give a concurrent mode with no change inside the interval an explicit rule: either #2753's commanded rule or refusal. Routing that pick is **decision: owner**.
   - Re-derive the required-mode refusal from that pick.
   - Name an activity signal for self-initiated charges, such as a rising `CONF_DHW_TEMP_ENTITY` over the interval, or reject one with a reason.
2. **architecture-unsound: the counter rule keeps only quantum steps** (note:45-50). A zero delta while the pump draws is refused, and the baseline still advances every cycle (note:50). The rule therefore throws away the energy those cycles carried and divides the next step by a single cycle. `evidence/counter_selection_probe.py` uses an integer-kWh counter at the 30 min default (`DEFAULT_OPTIMIZATION_INTERVAL`, const.py:1423):
   - 0.6 kW reads as 2.000 kW (3.3x);
   - 1.5 kW reads as 2.000 kW;
   - null: 3.0 kW reads as 3.000 kW.
   `HEAT_ENERGY_MIN_DELTA_KWH` (note:48) does not fix this, because a quantised counter never shows a sub-quantum delta. The electric counter in the COP fold (note:54) has the same flaw.
   **Fix wanted:**
   - A refused zero or sub-quantum delta keeps the baseline, so the span grows.
   - The accepted delta is divided by its whole span.
   - State how the replay's `dt_h` match (note:52) and the COP fold's paired deltas consume a span of several cycles.
   - Add a planted integer-counter test at a sub-quantum rate to the evidence plan.
3. **class-open: `_settle_interval_diag` is missing** (note:95-102). At coordinator.py:1086-1104 it splits the measured draw "by the plan's own split — the same convention the energy settlement uses" (`draw_range.space_share` over `pending` space/dhw). The note's grep pattern cannot match it. The design changes the settlement (note:68) and leaves this site alone, so its docstring goes false and the diagnosis triple apportions differently from the ledger. **Fix wanted:** add it to the sibling list, either in scope with the ledger's rule or out of scope with a reason.
4. **architecture-unsound: attribution has three owners** (note:23-36, 63-68). The concern "what part of this interval was space and what part hot water" holds three different `blended`/`other` policies, all computed in coordinator methods:
   - the replay returns `None`;
   - the COP bin applies a threshold against `_COP_CURVE_SHARE`;
   - the ledger weights by the plan.
   The coordinator should orchestrate, not compute. **Fix wanted:** `heat_energy.py` owns the attribution as pure functions of `DwellShares`: replay space heat, COP bin and ledger `dhw_share`. The three coordinator sites call them. Also list `HeatEnergyMeter`, named at note:31 and in the diagram, in the module's contents at note:24-28.
5. **harness: the goldens are misnamed** (note:118, 79-82).
   - "Expected moving goldens: none" is wrong: the new key's `_F` row moves `tests/golden/config_flow.json`, as #2753 moved it (+17 lines, claimed as `config_flow` in `tests/golden/claimed_drift.txt`).
   - The ledger change (note:68) applies with a mode entity and no heat key, which the invariants do not cover.
   **Fix wanted:** name `config_flow` and its claim. Then state which `coord_*` fixtures configure a mode entity and whether they move.

## Checked and holding

- **#2753 dependency** (decision: orchestrator). The PR is OPEN, MERGEABLE, REVIEW_REQUIRED, with head 8a133f390 unchanged. Every "(#2753)" symbol was checked by `git grep`:
  - present at 8a133f390 and absent at da12aa37d: `cop_evidence`, `space_reference_cop`, `replay_freeze`, `CONF_THERMAL_POWER_ENTITY` and `InstallCapability.measured_heat`;
  - present at both: `_interval_measured_heat_kw` and `_fold_capacity_envelope`.
  **Recommendation:** dispatch the fixer only after #2753 merges, and re-check these names at its merge SHA, which is the note's step 9.
- **Size.** `git diff --numstat da12aa37d...8a133f390 -- custom_components` gives 173 added and 84 deleted lines over 8 files, matching the note. Against #2753's head, L holds even with points 1-4 added: those land in files the note already lists or in coordinator.py. Against main alone, XL stands, as the note says.
- **Seam of `heat_energy.py`.** A pure module for `CounterDelta` and `ModeDwell` is sound. The rejected alternative of putting it in `flow_meter.py` is rightly rejected, because that module is stateless today. `read_heat_output_kw` stays the single heat answer. Point 4 is the only seam defect.
- **Re-anchor.** `heat_loss_basis_voids` orders the three bases, and `heat_loss_anchor_pair` returns a pair when `void` is set (thermal_model.py:2010-2040, `reanchor_heat_loss` at :2043). The coordinator zeroes both sample counts on void (coordinator.py:5199), so `reanchor_heat_loss` runs at confidence 0 and both of its clamp branches (`if a and not`, `if b and not`) are skipped. Removing a meter keeps evidence, which is consistent with "a later one is kept". Two fixer notes follow below.
- **Sibling sites.** The note's grep returns 8 sites. I confirmed them as `_fold_flow_lift` :879, `_interval_measured_heat_kw` :929, `_propagated_slab` :1011, `_commanded_power` :4620, `_interval_space_power` :4641, `_cop_reference_curve` :4925, `_record_accuracy`/`draw_range.fold` :9798 and `_accumulate_energy` :10152. The out-of-scope reasons hold. The only site missed is the one in point 3.
- **Files growth.** Of the other groups listing the five added files, all are `done` except R10-ARCH-SHAPES (`thermal_model.py`, not started, already in `after`) and R10-UX-HEALTH (after this group). This matches the note.
- **#2698 carry, "clamp means reset"** (decision: owner, or the orchestrator under mandate 6329234399). The carry calls this "a design call for the owner of the #86 decisions" and asks for a re-measurement at this group's merge base. A design note cannot close it as "dismissed: decided by this design".
  - The orthogonality argument is verified: the void path cannot trip either clamp.
  - Recommendation: keep "clamp means reset", the recorded decision.
  - Route the carry to the decider with that recommendation instead of dismissing it, and keep the re-measurement as the fixer's.

## Notes for the fixer (carries, not revise points)

- `_interval_measured_heat_kw` returning `None` leaves the replay inferring heat from the draw (coordinator.py:901-910). Evidence under the `measured_heat` basis therefore includes draw-inferred intervals, and a power meter added later will not void them. State this in `HEAT_LOSS_BASES`'s comment, or freeze those intervals on a heat-metered install. Carry: R10-HEAT-METER (item dr1-basis-mix)
- `house_heat_loss_basis` is a store `Domain("choice", choices=HEAT_LOSS_BASES)` (store.py:326). Check what a downgrade does with a stored `measured_heat` value, and check that the store schema check accepts the third choice. Carry: R10-HEAT-METER (item dr1-store-choice)
- The lag rule ("either counter older than `HEAT_COUNTER_MAX_LAG_MINUTES`", note:56) meets `INPUT_ON_CHANGE_MAX_AGE_MINUTES = inf` (note:40). An idle counter has an old `last_updated` and is still correct. Use the read instant, not `last_updated`, for alignment. Carry: R10-HEAT-METER (item dr1-lag-idle)
- `last_changed` on a `MODE_SOURCE_LAST_GOOD` reading is the stale state's own timestamp. Treat that as unobserved for the dwell. Carry: R10-HEAT-METER (item dr1-last-good)
