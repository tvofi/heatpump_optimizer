Design review: approve e91a4e30d7eb5d10b030db06a154457d315fe097

Delta review of design/R11-OWNER-FROST-HOLD, aefc8bc416..e91a4e30d7, checked against the revise points R1-R9 of design-verdict a330ce0ae8. Code was read at origin/main 3a98735a7e. Rulings applied: tvofi 2026-11-22, the three in the brief, plus "A stale reading should start a hold. I assume this fix will cover all installs with an on/off switch?", which the coordinator relayed.

## Prior points
- R1 resolved. `frost_hold.reading` takes the outdoor value from the `InputHealth` verdict and never from `state.outdoor_temperature`. `None` sets the latch, and only a reading at or above threshold + 1 K clears it. Test 4 covers the back-filled 5.0.
- R2 resolved. The install table covers every case. With duty mode off or observe, the switch stays on and nothing else is written, which matches pump_arbiter.py:1930-1960, where nothing outside control writes. The cost is stated in the note and in the release note.
- R3 resolved. An explicit `frost_hold` boolean, with off as a tested branch (test 6). The threshold selector is now -15..10.
- R4 resolved. There is no new duty string. Served becomes "space" and bypasses `_without_block`. `_mode_for(inp, "space")` gives Heating on Tuya, so `_lead_mode` leads with Heating, and test 11 pins that with a mutant. The block interplay is decided: the hold wins.
- R5 resolved. `_hold_floor_c` is the entity minimum, raised to `_setpoint_limits_c` where that sensor reads. The gate value is used only where the entity states no minimum, and `_gate_c` is not used.
- R6 resolved. A quiet off window is converted like any idle step, with a docs line and test 13. This is an orchestrator decision pending owner override, routed in the note.
- R7 resolved. The latch is in memory only, the restart case is stated, and it is updated with no `await` between read and write.
- R8 resolved. About three coordinator-class lines, paid by moving the eight-line "Not switching off" debug branch into `frost_hold`. `_tail_freeze` is a module function. archscore is run before and after.
- R9 resolved. Tests 1-19 each carry the opt-out null control, and the mutation sites follow the new shape.

## New in the delta, checked
- The no-sensor forecast fallback and the fail-closed freeze for an unmetered hold are consistent with the existing `learner_unmetered` chain at coordinator.py:3461. Both are orchestrator decisions pending owner override and are marked as such.
- Flow-cap sibling (design/R11-OWNER-FLOWCAP 5b697934d8): no shared write. The cap moves the space grid's high end, which is at least 30 °C, and the hold floor reads its low end.

## Notes for the fixer
- Carry: R11-OWNER-FROST-HOLD (item unmetered-freeze-text). On an install with no meter, every held interval freezes the learners, not only intervals with a run. The release note's "learning pauses for those runs" should say that unmetered installs pause for the whole hold.
- Carry: R11-OWNER-FROST-HOLD (item manual-off-rewritten). Below the threshold, the gate switches a power switch that reads off back on, including one a person turned off while the optimizer is active. A plan ON step does the same today. Say so in the docs/configuration.md bullet next to "A pump switched off is left alone", so that bullet is not read as covering the power switch.

Seat token count: not reported by the harness.
