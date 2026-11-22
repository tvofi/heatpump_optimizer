# R11-OWNER-STEP-KICK: the space set-point's step-start kick to the ceiling (design note, rev 3)

Rev 2 answered `Design review: revise 6deece87f2c53f27bb3dd60938e7adc705ad8f94 harness` (verdict 824b0d4a: R1–R6 and six carries). Rev 3 answers `Design review: revise 238cf282f37e4baf1a99c8cf474201700dffc702 consistency` (verdict a4aeeaf7: C1, plus the carries t9-label, payment-fallback and fault-gap), under the orchestrator's ruling for option (a).

Base: `origin/main` 3a98735a7ecc59e7ecc095a0429cdf6251d956ec. There is no predecessor handoff. Sibling notes, read at their tips:
- `design/R11-OWNER-FLOWCAP` fa8cd134
- `design/R11-OWNER-FROST-HOLD` e91a4e30
- `design/R11-OWNER-FAULT-HOLD` 6244553e
- `design/R11-OWNER-MODE-LEGS` 0e59437a (approved, verdict a45b5af9)

Evidence: the owner's live report, read against a private diagnostics bundle that stays local. **No finder harness: owner report.** Every number below is either invented or a code constant.

## 1. Why the kick exists

The code has no deliberate kick. Nothing writes the ceiling because a step started. Three rules combine to produce it:

1. **The top of the map.** `pump_arbiter.FLOW_HEAT_C` (55 °C, option `flow_heat_c`) tops the level map. It was added in 34339ad4e0 after a production report of 2026-09-26: written as the pricing curve, the set-point held 25 °C and underheated the house. The reason given there is "so the pump's own water thermostat never cuts a planned heating step short".
2. **The bottom of the map.** The floor is `thermal_model.modulation_floor_flow_c`, the inlet plus a lift. It was added in 25c3bd7b40 (R10-SETPOINT-POWER, 2026-10-19). `start_flow_min_lift_k` keeps that lift at or above the pump's start hysteresis, "its controller starts only once the target sits that far above the water". This is the code's only start-forcing rule, and it acts on the floor, not on 55.
3. **The inlet.** The inlet is the first fresh rung of `pump_arbiter.FLOW_INLET_KEYS`, and the pump-loop return comes first.

After a hot-water leg the pump-loop return reads the tank coil's water, so `inlet + lift` lands at or above the ceiling. `flow_setpoint_for_level` then writes `heat_c`, and `_bounded`'s `lo=min(floor, heat)` pins it there. Each minute's write then follows the cooling probe down. That is the 1–4 min ramp the owner sees.

Pinning tests:
- The R10-SETPOINT-POWER cells (`_sp_write`) and the R10-SETPOINT-BOOST cells (`_bst_write`) in `tests/features.py`.
- None of them pins the post-swap transient.

The rule is documented in `docs/configuration.md`, "Pump duty control".

**Start risk, restated (R4).** Rev 1 assumed that a target above the hot water keeps the heating request on across the swap. The design review read the reporting install's bundle, and it does not bear that out. Under today's ceiling write, most swaps that run at the swap still stop the compressor within `duty_switch.STOP_WINDOW_S` and restart about a minute later. So the kick does not keep the compressor on there, and stop-at-swap is near-saturated before any change.

The risk option D adds is a **longer restart after that stop**, or an extra missed start. The reason is that the controller restarts against a lower target while its supply probe is still warm. The same reading gives weak evidence the other way: at today's restarts the code had already written below the supply probe, and the compressor restarted anyway.

The return-target case is different. A target below a just-heated return stops the compressor there (`docs/design/2026-11-10-duty-switch-restart-learning/design.md`), so that unit is excluded (I4).

## 2. Options and their risks

| option | risk / why it loses |
|---|---|
| A. Keep | **Start risk:** none added. **Cost:** on the reporting install the kick does not prevent the swap stop, so it buys little. It keeps asking for maximum lift against space-loop water. Its effect on the P3 trips is unproven, not refuted. |
| B. Start at supply + k K and ramp up | At the swap the supply probe reads the hot-water leg's water, so supply + k is above the ceiling and the kick returns. Ramping after the settle needs D's detection plus a ramp state machine and one write per minute. Each write is a cloud round trip on the Tuya fork (`ECHO_GRACE_S`). |
| C. Cap the first-minute lift | A cap needs a reference. The return and the supply are both hot, so a cap against either caps nothing. A fixed time cap is install-specific and misses minutes 2–4. |
| **D. Skip the kick only right after a hot-water→space swap (recommended)** | **What it does:** for the settle window it anchors the floor on the space loop's own water. **Risk:** restart latency after the swap stop, which the post-merge soak measures. **Off switch:** settle span 0, which reverts to option A. |

## 3. Recommendation: D, the swap-settle inlet anchor

**Owning seam.** The seam is `pump_arbiter.py`, through `_map_inputs`. It is the one place the floor is mapped, both for the write and for the pass record. A new pure module, `custom_components/heatpump_optimizer/flow_anchor.py` (no `homeassistant` import), owns the anchor rule. The coordinator, `ArbiterInputs` and `const.py` are unchanged.

**The swap record (R6).** I checked which existing records could detect the swap; neither can:
- `ArbiterState.last_duty` is the **step** duty. `_observe` sets it before `_served` runs, so a both step's DHW→Heating leg change never shows in it.
- `duty_switch.note_mode_write` hears only landed mode writes. The GCHV gate transport swaps duties without one.
- MODE-LEGS at 0e59437a adds `duty_switch._Record.leg = (mode, since, previous)`, set in `note_mode_write` whenever the mode key changes. That is a different signal: the **landed mode**, not the **served duty**. On a GCHV gate transport the mode stays Heat + DHW (FROST-HOLD e91a4e30's install table), so `rec.leg` never moves at a swap there.

**One owner (orchestrator ruling, option (a)):** `ArbiterState.served: tuple[str | None, datetime] | None` is the only swap record. `_arbitrate` writes it right after `served = _served(...)`, on passes that reach `_command`. **STEP-KICK does not read `rec.leg`**, so on a mode transport there are not two records of one swap that could disagree. `rec.leg` stays MODE-LEGS' own, for its entry check. The orchestrator corrects MODE-LEGS' STEP-KICK overlap line and its `leg-history-owner` carry in that group's fixer brief.

**A swap** is a pass that serves `space` or `both` when `held.served` holds `dhw` from **less than `SWAP_SETTLE` ago**. Because the previous serve must be that recent, a gap such as FAULT-HOLD's suspension, a switch-off or a restart (the field is not persisted) never fires a swap late. A swap sets `held.swap_at`, and `held.served` is then overwritten.

**Shape.**
- **The anchor rule.** `flow_anchor.settled_inlet_c(live_c, space_c, next_rung_c, swap_at, now, settle) -> float | None`.
  - Outside `[swap_at, swap_at + settle)` it returns `live_c`.
  - Inside the window it returns `min(live_c, x)`. `x` is the first of: `space_c` (the inlet remembered from the last space-served pass outside a settle with the compressor running, if younger than `LEASE_MINUTES`); `next_rung_c` (the first fresh rung other than the pump-loop return); or `None`. `None` falls to `FLOW_HOLD_C` through `_or_hold`.
  - `settle` is `FEEDBACK_START_HOLD`, passed in by the caller.
  - `FLOW_INLET_KEYS` and `RETURN_SKIPPED_RUNG` move into this module with their comment. `pump_arbiter.py` re-exports them in one line.
- **Plumbing (carry held-plumbing).**
  - `desired` already calls `state_for(coord)`. It builds `flow_anchor.Settle(swap_at, space_inlet)`, a frozen value, once.
  - That value is passed as the keyword `settle=` through `_space_target` → `_flow_target` → `_map_inputs`.
  - `_pass_record` builds the same value from `held`.
  - The keyword defaults to `None`, which means no settle. So every other caller, the test helpers included, is unchanged.
- **Data flow.** `_arbitrate` → `_served` → (new: note `served`, `swap_at`, `space_inlet`) → `desired` → `_space_target` → `_flow_target` → `_map_inputs` → `settled_inlet_c` → `modulation_floor_flow_c` → `flow_setpoint_for_level`.
- **Settle and the loop's start hold (carry settle-vs-start-hold).** The two do not always end together. `FeedbackRun.start` resets on every stopped pass, so after a stop at the swap, the loop's hold outlasts `swap_at + settle`. This is harmless: by then the live inlet is cool, and `min()` returns it.

**Invariants.**
- **I1.** A write is never higher than today's, because the anchor is `min(live, …)`.
- **I2.** Outside the settle window, every write is byte-identical to today's.
- **I3.** The gate-plus-step floor holds.
- **I4.** No change on a return-unit or indoor-unit set-point.
- **I5.** A level at the band top, or a boost, still writes the ceiling.
- **I6 (carry experiment).** No settle while `_experiment_kw(inp)` is not `None`, so a sysid step keeps its commanded level map. Sysid has no swap exclusion of its own, so the rule stands aside rather than altering the fit's input.

**Generalisation.**

| install | behaviour |
|---|---|
| Tuya fork (select transport, flow target, pump-loop return) | Applies. |
| GCHV/Rotenso Modbus (gate transport) | Applies: the swap is a served-duty change with no mode write, and the record keys on the served duty. |
| Return target (Luxtronik smart-home interface) | Excluded (I4). |
| No inlet sensor | No-op. |
| Buffer plant with no pump-loop return | The buffer rung is space-side water, so the rule is rarely active. |
| Buffer plant **with** a pump-loop return | Exactly the active case. `next_rung_c` (the buffer) is the fallback anchor (carry buffer-text). |

There is no new option, because `config_flow.py` is over `MODULE_LOC_LIMIT`. A rollback is therefore a patch release. **Decided** (owner ruling 2026-11-22, relayed by the orchestrator): the owner accepts a post-merge soak on the reporting install, with rollback by patch release if starts worsen.

**Sibling sites.** The first two commands below list the inlet sites and the served-duty sites. The third adds the frost hold, which lives on its own sibling ref:
- `grep -n "_flow_inlet_c(" custom_components/heatpump_optimizer/pump_arbiter.py`
- `grep -n "_disinfecting\|Heating + DHW leaves" custom_components/heatpump_optimizer/pump_arbiter.py`
- the frost hold, on FROST-HOLD e91a4e30 (not on base)

Inlet sites:
- `_map_inputs`: changed.
- `_full_draw_c`: return unit only, so out of scope (I4).
- `_feedback`: stays live. During the settle the loop is in its start hold.
- `_pass_record`: its inlet column stays a live measurement. Its `floor_c` goes through `_map_inputs`, so `draw_range` agrees with the write.
- The duty-switch context `inlet_c=`: stays live, because its heated gate measures the real return.

**Residual, stated (R5): `both` served throughout.** These passes have no served change to key on:
- `_share` returning Heating + DHW outside a split: a boost, a non-plan mode, no plan step, or a disinfection hold.
- `_disinfecting` turning space into both.

On these passes the pump's own two thermostats swap internally. Its next space write can read the same hot return and clamp to the ceiling.

This group does not cover them, because no configured slot reports the pump's diverter state. The Tuya fork and the GCHV package expose none, and using a hot inlet alone as the trigger would also fire on a genuinely hot buffer (T3). Boosts are excluded anyway (I5). The harness counts this class, `both-internal`, so a later group can size it.

**FROST-HOLD entry (carry frost-entry).** Entering a frost hold right after a dhw-served pass serves `space`, so it sets `swap_at`. The hold row bypasses `_map_inputs`, so no write changes. T11 pins this.

## 4. Harness

The harness is `dev/audit/harnesses/r11_owner_step_kick.py <bundle.json>`. It prints counts only, and the bundle is never committed.

**Definitions.**
- **Swap pass:** a mode write to Heating, or a space write rising off the gate, within 90 s of a step boundary, following a hot-water leg.
- **Kick classes**, by that start's first space write:
  - `hot-inlet`: at least the ceiling minus 0.5 K, with the pump-loop return within the lift of the ceiling.
  - `other`: at least the ceiling minus 0.5 K, with a cool return. Counted only, and routed to D16 by the orchestrator.
  - `both-internal`: the mode was Heating + DHW throughout.
  - `none`: everything else.

**Leg R, replay (pre-merge, R3).** For each swap pass, the harness recomputes the write from the bundle's own series.
- The inputs are the inlet rungs, the lift, the ceiling, and the step's planned level and band. The level and band come from the plan or cycle rows. A pass without them is counted `unreplayable`.
- It runs through the real pure functions, once without and once with `settled_inlet_c`: `modulation_floor_flow_c` → `flow_setpoint_for_level`.
- **Fidelity check:** the "before" recompute must equal the recorded write within one entity step on at least 90 % of replayable passes, or the leg is void.
- **Pass:** zero `hot-inlet` in "after"; I1 on every pass; I2 on every pass outside the window; at least 10 replayable swaps.
- **Perturbation (R1):**
  - Raise the recorded first write of N `none` starts to the ceiling, with the return set within the lift: `hot-inlet` must rise by exactly N.
  - Lower N `hot-inlet` first writes: the count must fall by N.

**Leg S, soak (post-merge; accepted by the owner 2026-11-22).** The same classifier runs on a bundle taken after the deploy.
- **H2, primary (R4):** restart latency. This is the time from the swap stop to the first meter reading at or above `_ran_kw`, for swaps running at the swap.
- **H2, secondary:** missed starts (no start before the step ends) and stop-at-swap within `STOP_WINDOW_S`.
- **Spread (R2):** the before window is split by day. The spread is the range of the per-day medians, which needs at least 3 days. The space→space null is dropped for H2.
- **Minimum:** at least 20 running-at-swap events before and after, collected over as many days as that takes.
- **Pass:**
  - after median restart latency ≤ before median + max(60 s, before day spread), where 60 s is the arbiter's write cadence, the finest change it can resolve;
  - missed starts ≤ before;
  - stop-at-swap within the before day spread.
  - On failure: patch release with settle 0.
- **H2 perturbations (R2):**
  - Delay the first `_ran_kw` reading after N swaps by 120 s: the median must move.
  - Delete the restart on N swaps: missed starts must rise by N.
- **H1, secondary evidence only, gates nothing:** fault onsets within 5 min after each start, by class. The owner identifies the faults as outdoor-unit E5 trips after Heating→DHW switches, so H1 also counts onsets within 5 min after each Heating→DHW switch.
  - Null 1: the same windows shifted +7.5 min.
  - Null 2: space starts with no hot-water leg in the 15 min before.

## 5. Tests and structure payment

**Tests**, all in `tests/features.py`, with invented readings: return 54 °C after the leg, remembered space inlet 29 °C, band 1.5–5.5 kW, buffer 31 °C.

| test | case | expected |
|---|---|---|
| T1 (failing first) | a swap pass at mid-band | below the ceiling, equal to the map from 29 + lift. Main writes the ceiling. |
| T2 (null) | the previous serve was `space` | same as main |
| T3 (null) | a hot inlet with no swap | still clamps to the ceiling |
| T4 | after the settle, or with the live inlet at or below the anchor | the live value |
| T5 | no remembered inlet | the buffer rung; with none, `FLOW_HOLD_C` |
| T6 (null) | return unit, indoor unit, an experiment step (I6) | unchanged |
| T7 | band top, boost | the ceiling (I5) |
| T8 | gate transport, served swap with no mode write | the rule triggers |
| T9 | both sides of the window (carry fault-gap): a dhw serve 4 min 59 s before a space serve (for example a FAULT-HOLD that clears inside the settle span) is a swap; one 5 min 0 s before (a longer fault gap) is not | swap, then no swap |
| T11 | frost-hold entry after dhw | `swap_at` set, no write changes |
| T10 | `both` served throughout | unchanged (the residual, pinned) |

**Mutation targets:** the settle comparison, the `min`, the served-duty predicate, the recency guard, the max-age guard, the I4 and I6 exclusions.

**Payment.**
- `module_excess_loc` has no headroom, and `pump_arbiter.py` is over `MODULE_LOC_LIMIT`.
- The move of `FLOW_INLET_KEYS` and `RETURN_SKIPPED_RUNG` with their comment, plus any `CONF_*` imports left unused, has to cover everything this group adds to `pump_arbiter.py`. That is the fields, the swap note, the space-inlet record, the `Settle` build, and the `settle=` keyword lines.
- The fixer measures the net with `python3 tests/structure.py` at its merge base, and it must be zero or below. They also run `tools/audit/archscore/` before and after.
- If the net comes out above zero, prefer a move that only the floor anchor reads, judged by archscore before and after. Do **not** move `_gate_floor_c`: FLOWCAP (its flow-limit gate rule), FROST-HOLD (the hold's floor) and every `_flow_target` caller read it, and by then those groups have landed on it. Moving it would reach into three groups' code for a one-group payment (carry payment-fallback). `_or_hold` alone, which only `_map_inputs` reads, is the candidate.
- The new module and the harness must be classified, in a closure or on `tests/closure.py`'s INERT list. Never run a full `derive_closures.sh` off Linux.

## 6. Hot files, order, overlap

Hot files: `pump_arbiter.py`, `tests/features.py`, `flow_anchor.py`, `tests/closures.json`.

**Order (orchestrator ruling):** FLOWCAP lands first, then FROST-HOLD, then FAULT-HOLD, then MODE-LEGS, then STEP-KICK. This group rebases onto all of them.

- **FLOWCAP** owns the top (`heat_c`, `flow_limit.py`), and this group owns the floor anchor. They compose. Its fallback payment moves `_flow_command`/`_full_draw_c`, not the inlet keys.
- **FROST-HOLD** adds `ArbiterState` fields and a frost read in `_arbitrate`. Its entry sets `swap_at` with no effect on the write (T11).
- **FAULT-HOLD** returns from `_arbitrate` before `_command` while faulted, so no `served` note is made then. A fault that clears inside the settle span still counts as a swap on the first free pass. That is physically right, because the return can still be hot. A longer one does not count (T9 pins both sides).
- **MODE-LEGS** (0e59437a) changes `_served`/`_share` and the swap count, and it adds `rec.leg`, which this group does not read (§3). The `served` note sits on the same `_arbitrate` lines. The harness's "before" baseline is taken on MODE-LEGS' merged code, because fewer swaps means fewer kicks.

## Notes for the fixer

- `_map_inputs` takes no state today. Count the `settle=` lines in the net. Carry: R11-OWNER-STEP-KICK (held-plumbing)
- Once the kick stops masking them, the heated gate (`HEATED_MARGIN_K`) opens Tuya episodes. A latched `dhw_space` would change `both_step_duty`'s order and `planner_fields`' pricing. Report the latch state before and after in the body. Carry: R11-OWNER-STEP-KICK (learner-latch)
- The `other` class (the ceiling held with a cool return, around faults) is counted, not fixed. Carry: dismissed: the orchestrator routes it to D16 (`_level_kw`/`_band_kw`).
