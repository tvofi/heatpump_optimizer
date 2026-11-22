Design review: revise 6deece87f2c53f27bb3dd60938e7adc705ad8f94 harness

Review of design/R11-OWNER-STEP-KICK at 6deece87f2 (rev 1). Code was read at origin/main 3a98735a7e, from a detached worktree. Sibling designs were read at design/R11-OWNER-FLOWCAP fa8cd13408, design/R11-OWNER-FROST-HOLD e91a4e30d7 and design/R11-OWNER-MODE-LEGS 79719c386a (pending review). The owner's bundle was read locally and only for this review. No value from it appears here.

## What holds
- The root cause is confirmed in code. `_map_inputs` (pump_arbiter.py:988-997) takes `_flow_inlet_c`, whose first rung is the pump-loop return (pump_arbiter.py:741-746). It adds `start_flow_min_lift_k` (thermal_model.py:1894) through `modulation_floor_flow_c` (thermal_model.py:1776). In `flow_setpoint_for_level` (thermal_model.py:1802), `low = floor if floor < heat else heat`, so a floor at or above the ceiling writes `heat_c` at every level. `_bounded`'s `lo=min(floor, heat)` (pump_arbiter.py:954-961) pins it there as well.
- The bundle agrees qualitatively. The hot-inlet starts show the return at tank temperature on the swap pass. It falls to space-loop water within about a minute or two, and the write follows return plus lift down.
- Option D's shape (a `min()` anchor, the sibling-site list for `_flow_inlet_c`, and the I1-I5 invariants) is sound. T1 fails on today's code. The return-target exclusion matches the duty-switch design's finding (docs/design/2026-11-10-duty-switch-restart-learning/design.md).
- FLOWCAP composes cleanly. FLOWCAP lowers `heat_c` and this group lowers `floor_c`. The two new modules hold different concepts (the limit and the floor anchor), and FLOWCAP's fallback payment does not touch `FLOW_INLET_KEYS`.

## Revise points
- R1 harness (design.md §4 "Perturbation"). The perturbation injects ceiling writes at windows shifted by +7.5 min. The classifier only reads "a mode write to Heating, or a space write rising off the gate, within 90 s of a plan step boundary". A write at mid-step is neither, so the injected writes are never classified and the `hot-inlet`/`other` counts cannot move. Fix: inject where the classifier reads. For example, raise the first write of N `none` step starts to the ceiling with the return set within the lift: `hot-inlet` must rise by N. Or lower the first write of N `hot-inlet` starts: it must fall by N.
- R2 harness (§4 H2 and its pass criteria). H2 has no perturbation that shows it can detect a start regression. Its null (space→space starts) has no swap, so it cannot give the spread of a stop-at-swap rate.
  - Fix: add a perturbation that moves each H2 measure. For example, delay the first meter reading at or above `_ran_kw` after N swaps by a fixed time: the median latency must move. Remove the restart on N swaps: missed starts must rise.
  - State the minimum number of running-at-swap events the soak needs before its comparison means anything.
  - Replace the space→space "spread" with a variance of the before measure itself, for example day-by-day.
- R3 harness (§4 "Pass", "synthetic replay"). "The synthetic replay shows zero hot-inlet kicks" names no replay. The bundle records today's writes, so the after leg exists only after the change is deployed. The design therefore has no pre-merge leg beyond T1-T8.
  - Fix: define the replay as the harness recomputing the would-be write of each swap pass from the bundle's own sensor series. It runs `settled_inlet_c` → `modulation_floor_flow_c` → `flow_setpoint_for_level` with the pass's level and band, before and after.
  - Then mark the H2 legs explicitly as post-merge soak evidence.
- R4 harness (§1 last paragraph, and §2 row A "No new start risk"). The note's start-risk premise is that on a supply-target controller "a target above the hot water keeps the heating request on across the swap". The reporting install's own bundle does not bear this out. Under today's ceiling write, most swaps that run at the swap still stop the compressor within `duty_switch.STOP_WINDOW_S` and restart about a minute later. So the stop-at-swap measure is near-saturated before the change, and as a pass criterion it can hardly fail. The risk D adds on this install is restart latency after that stop, plus a possible extra missed start.
  - Fix: restate the risk analysis and option A's row on that basis.
  - Make restart latency after the swap stop the primary H2 measure, with the +60 s tolerance justified against the before median, not as an absolute.
- R5 class-open (§3 shape, `swap_at` trigger). The trigger keys on a change of served duty from `dhw` to `space`/`both`. A pass served `both` throughout leaves the swap to the pump's own two thermostats, with no served change. That covers Heating + DHW from `_share` outside a split (pump_arbiter.py:2000-2020: boosts, non-plan modes, no plan step) and `_disinfecting`'s space→both (pump_arbiter.py:1388-1390). Its next space write reads the same hot return and clamps to the ceiling by the same mechanism. A boost is excluded by I5, but disinfection and non-plan modes are not.
  - Fix: name this site in the sibling list, and either cover it (a duty-served signal the pump reports) or record it as a stated residual with its reason. The harness should classify it.
- R6 consistency (§6, MODE-LEGS row). The note grounds the order and the "one owner" rule on "MODE-LEGS' served-duty history". MODE-LEGS at 79719c386a adds no such history: its latch lives in `duty_switch._Record.order`, and it edits `_served`/`_share`. What already records duty transitions in the tree is:
  - `ArbiterState.last_duty`, which is the step duty and not the served one, set in `_observe` (pump_arbiter.py:1857);
  - `duty_switch.note_mode_write`, which hears landed mode writes but none on the gate transport.

  Fix: re-read MODE-LEGS at its tip, and say why `swap_at` cannot reuse either record, or reuse one. Then restate the ordering reason: it is the shared `_served`/`_arbitrate` lines, and the swap count that MODE-LEGS changes under the harness baseline.

## Decisions routed (not revise points)
- decision: owner. D's start risk can be measured only by a soak on the reporting install after merge. The off switch is a code argument, so a rollback is a patch release, since the design adds no option (config_flow.py is over the limit). Does the owner accept a post-merge soak gate with a release-time rollback?
- decision: orchestrator. Order: after MODE-LEGS is accepted, for the reasons in R6. MODE-LEGS is serialized after FLOWCAP and FROST-HOLD, so this group is transitively after FROST-HOLD as well, and §6's "their order is free" no longer holds.
- decision: orchestrator. The routing of the `other` class: ceiling writes with a cool return during the fault cluster. In the bundle they hold the ceiling for minutes rather than ramping, so they look like a different path, not a kick. A D16 lens on `_level_kw`/`_band_kw` (pump_arbiter.py:662-721), where an experiment step or a missing band keeps `heat_c`, is the likely owner.

## Notes for the fixer
- Carry: R11-OWNER-STEP-KICK (item held-plumbing). `_map_inputs` takes no `ArbiterState` today. `_flow_target`/`_space_target` reach it from `desired`, which has `coord`, and `_pass_record` has `held`. The note's data flow does not say how `swap_at` reaches it. Count those signature lines in the `module_excess_loc` net.
- Carry: R11-OWNER-STEP-KICK (item settle-vs-start-hold). "The settle ends when the loop's start hold ends, and the two never disagree" is not true. `FeedbackRun.start` resets on every stopped pass (pump_arbiter.py:1044-1047), so after a stop at the swap, the loop's hold runs past `swap_at + FEEDBACK_START_HOLD`. That is harmless, because the live inlet is cool by then, but correct the sentence.
- Carry: R11-OWNER-STEP-KICK (item learner-latch). Once the heated gate (`HEATED_MARGIN_K`) opens Tuya episodes, a learned `dhw_space` latch changes `both_step_duty`'s order and `planner_fields`' pricing. Report the latch state before and after in the body.
- Carry: R11-OWNER-STEP-KICK (item frost-entry). Entering a frost hold right after a dhw-served pass makes the served duty "space" (FROST-HOLD e91a4e30), which sets `swap_at`. The hold bypasses `_map_inputs`, so nothing is written differently, but add a test that pins it.
- Carry: R11-OWNER-STEP-KICK (item buffer-text). §3 "Buffer-tank plants: ... rarely active" holds only where the pump-loop return is unset. A buffer plant with a pump-loop return sensor is exactly the active case. Fix the sentence.
- Carry: R11-OWNER-STEP-KICK (item experiment). A system-identification step maps through `_map_inputs`, so a swap inside an experiment lowers its partial-level writes for the settle. State whether sysid excludes such windows.

Seat token count: not reported by the harness.
