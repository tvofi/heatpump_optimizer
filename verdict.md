Design review: approve fa8cd134080b291c9388474991517a58de9e6e75

Round 2, delta only (later rounds review the delta): `git diff 5b697934d8..fa8cd13408 -- design.md`, at base origin/main 3a98735a7e, which the note now names. The clamp handoff `handoff/r11-owner-flowcap` is on origin at 13290409848b, as the note says. All five round-1 points and all six round-1 carries are resolved.

## Round-1 points

1. Seam conflict: resolved. A "Seam ownership and order" section records the orchestrator's ruling. This group lands first and owns the `write_setpoint` clamp. R11-SEAM-actuation-writes consumes the clamp, keeps its own sibling sites (the frequency `np.clip` and the `setpoint_check` DHW Fix), and carries a `Carry: R11-SEAM-actuation-writes` line. The base SHA and the handoff SHA are both named.
2. Manual limit below the entity's minimum: resolved by precedence rule 5. The entity's minimum, rounded up onto its step, wins and is logged, so the arbiter's record equals what the clamp sends. It is tested: option 35 with minimum 40 gives 40; minimum 41 on a 5-degree step gives 45; `_edited` is false; and there is a null control.
3. Sites not named: resolved. A separate `_space_grid` accessor replaces the change to the shared `_grid`, so `_flow_command` keeps the advertised grid. It has a `draw_range` test and a null control (a capped write is neither `takes_ceiling` nor `_overdrawn`). `_adopt` and `_arm_space` are each disposed with a reason. The indoor-unit paths are excluded at runtime, where `_space_grid` returns the advertised grid when `_flow_unit` is false, and a test pins that.
4. Ratchet: resolved. The limit logic moves to a new pure module `flow_limit.py`, which is under `MODULE_LOC_LIMIT`. The `pump_arbiter.py` net change must be zero or below, measured by `tests/structure.py`. The design names the next move and judges it by archscore. `config_flow.py` is paid by a measured move, and the budget-raise route under mandate 6893738184 is named with `## Raise justification`, settled before push.
5. Install-specific data: resolved. The Problem section is generic, and the test numbers (70/52/48/40) are synthetic.

The routed sensor-versus-option decision is ruled: with both present, the lower wins (orchestrator ruling 2, relayed to the owner). The strings and tests follow it.

The round-1 carries, items 1 to 6, are all folded into the design: the `stored_value_out_of_range` path, the `_ABSENT_IS_NOT_DEFAULT` measured class, the one gate rule with its `log_held` line, the crossed sensor pair falling back to the option, the `_arm_space` disposition, and the five named mutation sites.

## Notes for the fixer

- design.md "The effective high limit", rules 1-5 "applied in this order": the gate rule (4) and the crossed-pair rule (3) come after the lower-of-two step (2). Read literally, a sensor below the gate would win the lower and then be dropped, which leaves no limit instead of the option. The design's own test says "dropped ... with the option then in force". So apply rules 3 and 4 to each source before step 2, and keep that test as the pin. Carry: R11-OWNER-FLOWCAP (item 7)
- Gate-rule boundary: today `_feedback_bounds` keeps a limit equal to `lowest` (`v >= lowest`, `pump_arbiter.py:1105`). The design says a limit "at or below" the gate plus one step is dropped, and its test drops "the gate plus one step". Keep the existing `>=` boundary, so a limit exactly at `lowest` is kept, unless the PR body states why the boundary moves. Pin the equality case. Carry: R11-OWNER-FLOWCAP (item 8)
- `flow_limit.py` is a new tracked file. Classify it into a measured closure in `tests/closures.json` (it is product code that `pump_arbiter` reaches), or `tests/entities.py` fails with "these force the FULL suite when touched". Check the D7 seam rows and the `seam_cut_total` cost of the new import edge in the same structure run. Carry: R11-OWNER-FLOWCAP (item 9)
