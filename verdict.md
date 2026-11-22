Design review: approve 09fecb1b69220acb7e22b8abe34cc297c165422c

Delta review of design/R11-OWNER-STEP-KICK, 238cf282f3..09fecb1b69 (rev 3), against C1 and the three carries of design-verdict a4aeeaf7de. Code was read at origin/main 3a98735a7e, and MODE-LEGS at its approved tip 0e59437a8f. Ruling applied: option (a) (orchestrator, 2026-11-22). `ArbiterState.served` is the only swap record, and MODE-LEGS' carry is corrected in its fixer brief.

## Prior points
- C1 resolved. The sibling list cites MODE-LEGS 0e59437a. §3 names `rec.leg` (set in `note_mode_write` on a mode-key change) as a landed-mode signal that this group does not read. That reason holds: a GCHV gate transport stays in Heat + DHW, so `rec.leg` never moves at a swap there. One owner of the swap moment is named, and §6 states the same. The MODE-LEGS overlap line and its `leg-history-owner` carry are the orchestrator's correction, in that group's fixer brief.
- t9-label resolved. T9 is the window boundary and T11 is the frost-hold entry. §3 and §6 point to the new labels.
- fault-gap resolved. T9 pins a gap of 4 min 59 s (a swap) and one of 5 min 0 s (no swap). This matches §3's strict "less than `SWAP_SETTLE` ago". §6 states the FAULT-HOLD case on both sides.
- payment-fallback resolved. `_gate_floor_c` is excluded from the fallback, with its readers named. `_or_hold` is the candidate. Its only reader is `_map_inputs` (pump_arbiter.py:994), as the note says.

## Notes for the fixer
- Carry: R11-OWNER-STEP-KICK (item or-hold-ledger). `_or_hold` has a killed-mutant entry keyed on its current path (tests/mutation_ledger/killed_by/pump_arbiter.py/_or_hold.RETURN_DEL.c0db090d.json). If the fallback payment moves it into `flow_anchor.py`, the ledger anchor moves with it. Re-key the entry, or let the mutation job re-kill it, rather than leaving an orphan.

Seat token count: not reported by the harness.
