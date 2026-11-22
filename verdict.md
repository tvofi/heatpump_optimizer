Design review: revise 238cf282f37e4baf1a99c8cf474201700dffc702 consistency

Delta review of design/R11-OWNER-STEP-KICK, 6deece87f2..238cf282f3 (rev 2), against points R1-R6 and the six carries of design-verdict 824b0d4a8a. Code was read at origin/main 3a98735a7e. Sibling designs were read at:
- design/R11-OWNER-MODE-LEGS 0e59437a8f (approved, verdict a45b5af9af)
- design/R11-OWNER-FAULT-HOLD 6244553e45
- design/R11-OWNER-FROST-HOLD e91a4e30d7
- design/R11-OWNER-FLOWCAP fa8cd13408

Rulings applied, relayed by the orchestrator on 2026-11-22:
- the order is FLOWCAP, FROST-HOLD, FAULT-HOLD, MODE-LEGS, STEP-KICK;
- restart latency is the primary start-risk metric;
- the `other` class goes to D16;
- the owner accepts a post-merge soak, with rollback by patch release;
- the faults were E5.

## Prior points
- R1 resolved. Leg R's perturbations act where the classifier reads, at the first write of a classified start, and each moves its count by exactly N.
- R2 resolved. Both H2 measures now have a perturbation: a 120 s delay, and a deleted restart. The spread is the range of the per-day medians, over at least 3 days, and the space→space null is dropped. The minimum is 20 running-at-swap events.
- R3 resolved. Leg R recomputes each swap pass through the real pure functions. It has a fidelity gate (at least 90 % within one entity step) and an `unreplayable` count. Leg S is marked as the post-merge soak the owner accepted.
- R4 resolved. §1 and the option-A row are restated. Restart latency is primary, and the tolerance is max(60 s, the before day spread), where 60 s is the write cadence.
- R5 resolved. The residual is stated with its reason: no slot reports the diverter, and a bare hot-inlet trigger fails T3. The harness counts `both-internal`, and T10 pins it.
- R6 **open**: see C1.

## Carries
All six are taken in the note:
- held-plumbing: `Settle` is passed through `settle=` with default `None`, and its lines are in the net.
- settle-vs-start-hold: corrected in §3.
- learner-latch: kept as a carry.
- frost-entry: T9.
- buffer-text: in the generalisation table.
- experiment: I6, with a null in T6.

## Revise point
- C1 consistency (§3 "The swap record", §6 MODE-LEGS row, and the sibling list at the head, which cites MODE-LEGS 79719c38). Rev 2 says "MODE-LEGS at 79719c38 adds no served-duty history". The approved MODE-LEGS (0e59437a8f, §1b) adds `duty_switch._Record.leg = (mode, since, previous)`, set in `note_mode_write`. Its overlap section states "R11-OWNER-STEP-KICK. Its `swap_at` reads the served-duty history that `rec.leg` holds; it lands after this group and reuses that field". Its fixer carry is "Shape it so STEP-KICK's `swap_at` reads it". This note instead adds `ArbiterState.served`. As written, the two fixers get opposite instructions, and on a mode transport the DHW→Heating transition would have two records.
  - The note's own reason still holds against `rec.leg`. `rec.leg` moves only on a landed mode-key change. A GCHV gate transport stays in Heat + DHW (FROST-HOLD e91a4e30's install table), so it never moves there, and that install needs the served-duty record.
  - Fix: re-read MODE-LEGS at 0e59437a8f and name one owner for the swap moment. Either:
    - (a) keep `ArbiterState.served` as the only swap record. State why `rec.leg`, which is a landed mode, is a different signal that this group does not read. Route the correction of MODE-LEGS' STEP-KICK overlap line and its `leg-history-owner` carry to the orchestrator.
    - (b) read `rec.leg` on mode transports and `ArbiterState.served` only where no mode key changes. Say why two sources do not disagree at a swap.
  - Update the sibling list to the approved tip. Everything else in rev 2 can stand.

## Notes for the fixer
- Carry: R11-OWNER-STEP-KICK (item t9-label). The test table has two rows labelled T9 (the fault-gap recency case and the frost-hold entry). Number them apart, so a mutation report names one test.
- Carry: R11-OWNER-STEP-KICK (item payment-fallback). The fallback payment moves `_gate_floor_c` into `flow_anchor.py`. FLOWCAP, FROST-HOLD and `_flow_target`'s callers all read it, and by then those groups have landed on it. Prefer a move that only the floor anchor reads, and judge it with archscore before and after.
- Carry: R11-OWNER-STEP-KICK (item fault-gap). Under FAULT-HOLD 6244553e, a fault cleared within the settle span still counts as a swap on the first free pass, because the dhw serve is recent. That is physically right, since the return can still be hot, but T9 should pin both sides of the span.

Seat token count: not reported by the harness.
