R10-MODE-BEFORE-SUPPLY-ON, part E of Bankaifan's note on pull request 3420 (alpha innotec LWDV 91-1/3, Luxtronik 2.1): thank you, Bankaifan, for the measurement this is built on. On their install the mode write followed the supply switch-on by several seconds, so the pump started in the last duty and was switched while starting. Cause at main: a pass writes nothing while the power switch reads off (`_pump_off`), and the cycle runs the pass before its switch write, so the mode reached the pump only on the next pass after the switch-on.

Fix, in `pump_arbiter.py`: `write_supply` is now the switch write behind the coordinator's gate (`_write_supply`, shared by the cycle and the step tick). On a switch-on with the switch still reading off, `_lead_mode` writes the mode the step owes through `_write` (the pass's own writer: record, persistence, learner report), then the switch. Only the mode: the set-points the pump reports while off are its own (`_pump_off`), and the first pass after the switch-on compares and writes them as at main. A failed mode write is logged by `_write` and holds the switch back by zero passes. `desired`'s mode row moves to `_mode_for`, so the pass and the lead share one rule; `_arbitrate`'s duty and served-duty expressions move to `_step_duty` and `_served` for the same reason.

Decision: while the switch reads off, the lead writes against the ownership record and compares no reading, because the arbiter compares nothing while off (module docstring, "While the configured power switch reads off, nothing is compared or written"). So a mode changed at the pump while the switch was off, with a record still matching the step, is re-sent by the first pass after the switch-on (`hold`), as at main.

Alternatives: a full arbiter pass before the switch-on would also write the set-points against readings the pump makes up while off, and `hold` would count those as misses; a coordinator-side call before `switch_supply` would add a logic line to the coordinator class, where `write_supply` replaces the existing call in place (`coordinator.py` diff: one line changed, zero added).

Sibling sites, every path that writes the power switch. Rule: `git grep -n -E "switch_supply\(|write_supply\(|wiring\.write\(|_write_supply\b" -- 'custom_components/heatpump_optimizer/*.py'` plus the switch slot's readers (`git grep -n heat_pump_switch_entity -- 'custom_components/heatpump_optimizer/*.py'`):

| Path that turns the supply on | Site | Disposition |
|---|---|---|
| cycle's plan write | `_apply_action` to `_write_supply` to `write_supply` | covered (check "a cycle that switches the supply on writes the step's mode first") |
| step tick at a boundary | `supply_tick` to `wiring.write`, which is `_write_supply` | covered (check "a step tick that switches the supply on ...") |
| early cut-off | `early_cutoff.py` `switch_supply(..., False)` | not affected: writes off only |
| a switch-on the gate holds (cut-off `MIN_OFF`) | `_write_supply`, `allow_on` before `write_supply` | covered: no mode written either (check "a cycle switch-on an early cut-off holds writes no mode") |
| supply-hold retry of R10-OUTSIDE-SUPPLY-MIN-RUN-PAUSE (Carry 0) | not on main; at its head 701a18e2 the hold sits inside `_write_supply` before the switch call and the retry re-enters `_write_supply` from `supply_tick` | covered once both land, if the switch call stays `pump_arbiter.write_supply` behind its hold; carried below |
| unload `release` | writes no switch | not affected |
| circulation pumps `_async_set_pump` | space and hot-water circulation entities, not the power switch | not affected |
| a person or automation switching the pump on | not a write of this integration | not affected: the first pass after it writes the mode, as at main |

Learner (part A, merged in #3461): the lead's write reaches `duty_switch.note_mode_write` with `supply_on` False, which `SwitchContext.void_cause` returns as `supply_off`, so `mode_write` opens no episode.

## Head

84fe94c780e04d5c0f39434550ef71268b1be19b, on origin/main 005eed2573da9e946fa4838de147401d0ff36cc1.

## Mutation proof

Block: `python3 tools/audit/seat/features_block.py --emit-prelude P "# #3420 part E (Bankaifan)" "# The pump_duty record's held slots are declared"`, then the same block with `--prelude 'exec(open("P").read())'`; each mutant is one textual edit of `pump_arbiter.py`, restored after (`cmp` against the saved copy).

- M1, the lead call deleted from `write_supply`: FAIL "a cycle that switches the supply on writes the step's mode first, then the switch", "a step tick that switches the supply on writes the step's mode first, then the switch", "the mode written ahead of a switch-on is reported with the supply off, opening no learner episode", "null control: the same context with the supply on is not voided by the supply", "a mode write that fails ahead of a switch-on holds nothing: the switch follows in the same write", "null control: the same heating step with no cut on record writes the mode, then the switch", "null control: write_supply with the switch off and the optimizer on writes the mode first".
- M2, `not on or` dropped from `_lead_mode`'s guard: FAIL "a cycle switch-on an early cut-off holds writes no mode ahead of the switch it holds back".
- M3, `or not _pump_off(inp, held)` dropped: FAIL "write_supply with the switch already on, the optimizer off or the entry released writes the switch alone".
- M4, the duty-mode guard dropped: FAIL "null control, duty mode observe: the service calls and their order are today's".
- M5, `inp.mode == MODE_OFF` to `False`: FAIL "write_supply with the switch already on, the optimizer off or the entry released writes the switch alone".
- M6, `inp.entry_released` to `False`: FAIL, the same check.
- M7, `_disinfecting` dropped from `_mode_for`: FAIL "the mode written ahead of a switch-on for a heating step under a held disinfection is Heating + DHW".
- M8, `await _load(coord)` deleted from `_lead_mode`: FAIL "a lead write loads the persisted record before it writes".

The diff's mutants that the block above lets survive (`prepr.sh`'s `MUTANT_CMD` set to that block) are the refactored `desired` rows and `_arbitrate`'s write, which the arbiter's existing checks own. Each was driven by hand in its own detached worktree at 84fe94c7 through the full `tests/features.py` and `tests/block_duty.py` (`PYTHONPATH=tests/hastub`):

- `desired` `duty = _disinfecting(inp, duty)` deleted: features FAIL "a disinfection cycle held on turns a space-only step into Heating + DHW, with no hot-water gate"; block_duty FAIL "the space-only gate stays a gate on a booked step, but a held cycle turns it into Heating + DHW".
- `desired` space-gate `return` deleted: features FAIL "with no heating-only mode (GCHV Modbus) the hot-water set-point is the gate, at the entity's minimum"; block_duty FAIL as above.
- `desired` indoor-gate `return` deleted, and its `5.0` swapped to `10.0`: features FAIL "an indoor space set-point is gated at 5 °C (or the entity's minimum) with no DHW-only mode".
- `_mode_for` idle `return None` deleted: features FAIL "a block on both channels serves idle: the mode select is not written".
- `_arbitrate` `await _command(...)` deleted: features FAIL "a hot-water-only step writes DHW only, the configured hot-water set-point and the space gate".

Failing test first: the block at the merge base's production files (`git stash push custom_components`) raises `AttributeError: module 'heatpump_optimizer.pump_arbiter' has no attribute '_lead_mode'`.

## Null control

Each null control is the same run through the real coordinator with `_lead_mode` replaced by a no-op, which is the order at main. On an install with no mode entity, on duty mode observe, and on a pass that changes the mode with the supply already on, the ordered select and switch calls are identical with and without the lead, for both the cycle and the step tick (checks "null control, no mode entity / duty mode observe / supply already on: the service calls and their order are today's"). Where the lead owes the mode, the no-op run switches on with no mode before it ("null control: without the lead the same cycle and tick switch on with no mode before it"). No golden under `tests/golden/` moves; neither claim file is touched.

## Figures

<!-- figure-block: scope-line mb=005eed2573da9e946fa4838de147401d0ff36cc1 head=84fe94c780e04d5c0f39434550ef71268b1be19b -->
~~~text
MODE: SCOPED -- 22 script(s) run, 11 scoped out.
~~~
<!-- /figure-block -->
- Feature block: `python3 tools/audit/seat/features_block.py --prelude 'exec(open("P").read())' "# #3420 part E (Bankaifan)" "# The pump_duty record's held slots are declared"` at the head: every check passes; at the merge base's production files it raises (above).
- Architecture score: `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` reads NULL at the head. At a3ac0f8e it read WORSENS on `coord_footprint`; paid in 2b540f7f by folding the switch-on check into `_lead_mode` and the disinfection rule into `_mode_for`, so `write_supply` and the lead's duty line are delegations.
- Structure: `python3 tests/structure.py` passes the ratchet at the head.
- Ledger: `python3 tests/mutation_table.py --pin-killed --base origin/main` pinned every site the diff adds, none left unpinned.
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift bash tests/run.sh` at 2b540f7f: every script the mode line selects passed, the golden lane in drift mode included; 84fe94c7 adds only checks to `tests/features.py` and pins under `tests/mutation_ledger/`, and the block holding the new checks passes at 84fe94c7.

## Unpinned sites

The diff adds no unpinned ledger site. The nine survivors `prepr.sh` reports for its `MUTANT_CMD` (the new block alone) at 84fe94c7, each with the check outside that block that kills it, measured above or by the ledger:

- `pump_arbiter.py:1217` STMT_DEL (`desired`, `duty = _disinfecting(inp, duty)`): killed by `tests/features.py` and `tests/block_duty.py`, measured above.
- `pump_arbiter.py:1222` GUARD_OFF: pinned, killed by `tests/block_duty.py` (`desired.GUARD_OFF` under `tests/mutation_ledger/killed_by/pump_arbiter.py/`).
- `pump_arbiter.py:1223` RETURN_DEL: killed by `tests/features.py` and `tests/block_duty.py`, measured above.
- `pump_arbiter.py:1224` GUARD_OFF: pinned, killed by `tests/features.py`.
- `pump_arbiter.py:1225` RETURN_DEL and CONST_SWAP (`5.0` to `10.0`): killed by `tests/features.py`, measured above.
- `pump_arbiter.py:1245` GUARD_OFF: pinned, killed by `tests/features.py` (`_mode_for.GUARD_OFF`).
- `pump_arbiter.py:1246` RETURN_DEL: killed by `tests/features.py`, measured above.
- `pump_arbiter.py:1757` CALL_DEL (`_arbitrate`'s `_command`): killed by `tests/features.py`, measured above.

Ledger: the ten `killed_by` pins on `desired`'s old mode rows named lines the refactor moved into `_mode_for`, `_disinfecting` and the gate rows; they are deleted by hand, and `python3 tests/mutation_table.py --pin-killed --base origin/main` at 84fe94c7's tree pinned every site the diff adds (`PIN KILLED: 14 pinned, 0 left unpinned`), under `tests/mutation_ledger/killed_by/pump_arbiter.py/`.

## Red checks

none

## Forward-carry

- Carry 0 (the brief's forward-carry from feature triage f4, outside pull request 3456), answered: the retried write is its own row in the sibling table above, covered behind the gate, and this group merges first by the order the train picks, so the second to merge re-reads the other's paths. R10-OUTSIDE-SUPPLY-MIN-RUN-PAUSE: its hold must stay inside `_write_supply` ahead of the switch call, and that call must be `pump_arbiter.write_supply(self, switch_entity, value)` after both land, so a held switch-on writes no mode and a retried one that lands writes the mode first; control: this PR's check "a cycle switch-on an early cut-off holds writes no mode ahead of the switch it holds back" with its null, re-run with the hold engaged. Re-read both groups' paths at main. Lands in `dev/programme/rosters/wave-r10-groups.json` (its group's brief, on `handoff/audit-r10-roster`, by the relay). Carry: R10-OUTSIDE-SUPPLY-MIN-RUN-PAUSE

## Friction

none
