Design review: approve 726e84d230580e58eb696e17bf2fbf8f44efde2c

Design note design/R11-OWNER-COOLING-AUTORETURN at 726e84d230, revision 2. Round 2: this review covers the delta 41979366f8..726e84d230 and whether the prior finding is resolved (prior verdict 7a9783a29c). A full re-review was not needed. Code read at base origin/main 49cb3207a9, at #3864 0f9fc88ff3 (which contains a90d7bc9da) and at #3872 d6a54399a6. #3872's blocking verdict (verdict/3872 c61cfa41bf) was also read.

## Prior findings

- R1 resolved. The return's conditions at design.md:63-70 now end with `fault_hold.consult(entry, inp)` False. That is the accessor `pump_arbiter.apply` calls at #3872 (pump_arbiter.py:1858) and `fault_hold.gate` calls (fault_hold.py:131). Its imports (fault_hold.py:36-39: `issues`, `const`, `entry_config`, `inputs`) give `supply_hold` no cycle. E4 at design.md:148-153 gains the fault case with its null control (a fresh off) and the clear. The fault consult is a mutation target at design.md:157. The pump-actuation-writer axis is enumerated by FAULT-HOLD's own grep (design.md:129-135), and the return's row under the hold is "none". The composition with the `_write_supply` chain is stated for both of FAULT-HOLD's forms, the inline gate (#3872 coordinator.py:7784) and the `write_gated` fallback (design.md:85-98). Under a latched fault, the cooling check returns `None` and `fault_hold.gate` passes a non-False value unchanged (fault_hold.py:131). So nothing is written. `supply_tick` keeps retrying on `cooling_asked` (#3864 pump_arbiter.py:2149), and the return is due at the first tick after the clear. That matches the note.
- Routed decision (serial position) answered: design.md:172-180 records the chain FLOWCAP, FROST-HOLD, FAULT-HOLD, this group, MODE-LEGS, STEP-KICK. It branches after #3864 and #3872 merge and counts no other group's structure payment.

## Dependency on #3872's repair (fault_hold.py:115/150)

The design calls `consult`, and the surviving mutants are on line 115, the body of `consult`: its `released=` and `off=` arguments. Line 150 is `diagnostics_view`'s `since`, which the design does not read. The return checks Off and `entry_released` itself, before the consult (design.md:64-67). So deleting or changing those two keyword arguments would not change what the return decides. If the repair renames or inlines `consult`, carry N4 (design.md:200-202) binds the fixer to "whatever `fault_hold.gate` calls". The repair report (fix-3872-repair.md) adds checks and deletes no site. No dependency blocks.

## Notes (non-blocking)

- At #3872, the `_write_supply` statement (coordinator.py:7784-7785) is already two physical lines, and `pump_arbiter.supply_write` is #3864's `supply_hold.supply_write` before the rebase. Adding `self.entry` and `await` must not add a third line under `class_excess_loc`'s zero headroom. If it would, the fixer passes `entry` by another route already in the expression (for example inside `inp`) rather than wrapping. N3's re-measure catches this either way.
- E4's fault fixture must back-date the fault entity's `last_changed` by 11 minutes. The latch seeds `since` from it (fault_hold.py:86-88), not from the test's clock alone.
