Design review: revise c52e37824a6c1b4e503295583c242e1dee977e53 harness

Design round 2. Reviewed `design.md` at c52e3782 from a detached worktree. The base was judged against c668197a, and the predecessor against #3299 head e066a630.

The note reads 85ba6cda. Between 85ba6cda and e066a630 the following files are byte-identical: off_restore.py, heat_curve.py, `__init__.py` and entry_config.py (`git diff --stat 85ba6cda e066a630` on those paths prints nothing). The only production changes are main merges: coordinator.py ±3 lines, const.py and config_flow.py. So the note's off_restore, heat_curve and `__init__` citations hold at e066a630.

## Revise point

1. harness. `design.md`:118 (I4) and `design.md`:207-208 (null control) contradict `design.md`:46-58 (C1) and `design.md`:200 (the arm "entity cleared with A armed → A restored").

   C1 replaces `armed[key]: float | None` (off_restore.py:88) with `{"entity_id", "value"}` for every key, and keeps the legacy reader only for records already stored. So a fresh kind-`offset` arm persists `{"heat_curve": {"entity_id": …, "value": 0.0}}`, where #3299 persists `{"heat_curve": null}`.

   C1 also reverses #3299's "a consumer no longer configured is disarmed unwritten" (off_restore.py:153-154, :163-165) for every key. For kind `offset`, a crash, then the entity cleared, then a restart now writes 0 to A instead of disarming. That is the same move the note justifies for `persistent` in Alternative C (`design.md`:158-160).

   Yet I4 promises "with kind `offset` or no entity, no behaviour, payload, golden or record shape moves". The null control asserts "the stored record is byte-identical to #3299's for kind `offset`". As written, the null control fails on the design's own C1. A fixer must either break C1 or break the null control, and the fix review would judge against a control that cannot pass.

   Fix wanted: choose one and state it.
   - (a) C1's entity record and rule R bind only `neutral=None` consumers. A neutral consumer keeps `float | None` and #3299's disarm-on-unconfigured rule, so I4 and the null control stand. The arbiter, also `neutral=None`, still gets C1.
   - (b) C1 binds every key, as I5 (`design.md`:119) reads. Then restate I4 and the null control: kind `offset`'s writes, MQTT payloads and goldens stay unchanged. Its record entry becomes `{entity_id, value: 0}`. Its cleared-entity crash path now restores 0 to the recorded entity, for Alternative C's reason. And add that arm to §Evidence plan for kind `offset`.

   Either choice is a few lines in §Shape C1, I4 and §Evidence plan. Nothing else in the note needs to move.

## Round 1 (ae96e235): answered

- Point 1: the baseline lives only in off_restore's armed record (C1). The consumer state is C3's `state` section of the same Store. There is no second Store.
- Point 2: there is no heat_curve remove call. `async_forget` logs and writes nothing (C4), with the reason given.
- Point 3: the entity is persisted, rule R is stated, and the A→B arm is in §Evidence plan (`design.md`:198-199).
- Point 4: `baseline.py` is dropped. classify stays beside the write state it reads.

The predecessor is built on, not ignored. The note names what its fixer re-checks once #3299 merges: ghcp-03 (`Restorer`, `async_arm`, `async_restore`, `async_forget`, `restored`, `state_for`) and ghcp-r3 (the line citations).

## Routed, not revise

- decision: orchestrator. Which of this group and R10-ARBITER-OFF-RESTORE lands C1 and C2 first (`design.md`:240-242).
- decision: orchestrator. The arbiter brief's "while Home Assistant is not stopping" against the hook's restore on stop (`design.md`:246-248).
- decision: owner. ghc-d02, the MQTT displace 0 on off and unload (`design.md`:249-250).

## Checked and sound

- Seam (step 1): one owner per concern, checked at e066a630.
  - off_restore owns the record, arm, restore, MODE_OFF and remove.
  - heat_curve registers on the existing key `heat_curve` with the existing writer `write_setpoint` (heat_curve.py:95-114), so one per-key writer serves both kinds.
  - `__init__.py`:424-427 restores on unload with `effective_config`, and :438 calls `async_forget`. Neither is touched.
- Shape (step 2): every moved behaviour traces to the owner rulings, PR 3284's P1-P7 and O1-O5, carries a2b5f107, 67895f89 and 73eb63bd, or review round 1.
- Sibling sites (step 3): the arbiter's Store and off rule (pump_arbiter.py) are dispositioned to R10-ARBITER-OFF-RESTORE. No other off-restore consumer exists at e066a630.
- Evidence plan (step 4), apart from point 1: the failing test is red at #3299 for the stated reason (an unknown kind falls back to offset, entry_config.py:222-224, then `range_excludes_zero`, heat_curve.py:227). No golden or claim file moves.
- Siblings in flight (step 5): `design/R10-HEAT-METER` does not name off_restore.py or heat_curve.py.
- Cost (step 6): no coordinator line is added, and about 40 lines go to off_restore. This fits size L.
- O5 defaults are restated with their sources and tags (`design.md`:134-149).

## Notes for the fixer (carried)

- `inputs.write_setpoint` (inputs.py:597-616) returns False without raising for a domain with no set-point service, and `async_restore` (off_restore.py:166-176) counts only a raise as failure. C1's "A restored only on success" before arming B must treat a False return as a failure. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-r5)
- The publish flow reads `armed.value` (`design.md`:86-87), but C1-C4 name no read accessor of the armed entry. Add one beside C2 in off_restore, its one owner. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-r6)
- The legacy reader resolves "the configured entity" (`design.md`:56-58), but `_armed_record` (off_restore.py:100-113) has no config. Resolve the legacy entry lazily at arm or restore, against the config passed in. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-r7)
- At e066a630 the coordinator citations are one line later than the note's 85ba6cda figures:
  - `async_set_mode` at 6484, with `async_mode_change` at 6491;
  - `async_shutdown` at 6555;
  - `heat_curve.publish` at 7670.

  Re-anchor them at the merged head. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-r8)
- C3's `restored` callback bumps `count` for the restore. Key that count to the day of the restore write, not the day of the displace, so I2 holds across midnight. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-r9)

Seat token count: not reported by the harness.
