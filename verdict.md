Design review: revise e2d81a61c0f668c0a382575fd1212cb7206d4900 architecture-unsound

Design round 1. I reviewed the note at e2d81a61 from a detached worktree. I judged it against base 4b5d771b, origin/main 2a3c0564, and the predecessor's #3299 head d7d4c511 (refs/pull/3299/head, the same as handoff/r10-generic-heat-curve 070cff63 in heat_curve.py and off_restore.py). The note was written before #3299 had a head, so it reads heat_curve.py as a module still to be created. At #3299 head, that module and a separate restore owner, off_restore.py, both exist. The note's seam does not match them.

## Revise points

1. architecture-unsound. In design.md §Owning seam and §Shape "The record" (lines 18-40), heat_curve.py gets a second per-entry QuarantiningStore holding a baseline and a restore. At #3299 head, off_restore.py already owns all of this:
   - the per-entry store `{DOMAIN}_{entry_id}_off_restore` (off_restore.py:96-97);
   - the baseline capture before the first write (`async_arm`, `Restorer.neutral=None` with `baseline_of`, :51-67 and :123-146);
   - the MODE_OFF and unload restore (`async_restore` :149, `async_mode_change` :184);
   - the remove-entry path (`async_forget` :197, called from `__init__.py`:434-438).

   The note's record therefore makes a second owner of the persisted baseline. That breaks the group brief ("no second owner of unload, remove or MODE_OFF") and carries 73eb63bd ("register a consumer and arm before the first write, never a second owner") and 67895f89 ("the baseline is persisted per entry by `async_arm`").

   Fix wanted: re-cut the record so that kind `persistent` registers an off_restore consumer with `neutral=None` and keeps its baseline in off_restore's armed record. Only the consumer-private write state (written/previous, day, count, dwell) belongs in heat_curve.py, persisted there or as an extension of the consumer entry in off_restore's record. Then name the off_restore API changes the shape needs, each with its one owner:
   - edit adoption (P6) needs a re-baseline call, because `async_arm` keeps the first baseline forever (:135);
   - the write-ahead "previous" needs a home.

2. architecture-unsound. In design.md "Restore hook" and the flow's `remove entry` line (lines 57-60 and 51), the note adds `heat_curve.async_remove`, which restores from a dirty record at `async_remove_entry`. #3299 has already settled this site: `async_forget` deletes the record and writes nothing (off_restore.py:197, "The unload before it restored what it could"). A restore at remove would be a second owner of the remove path.

   Fix wanted: keep remove as off_restore's alone. If a dirty-record retry at remove is wanted, specify it as a change to `async_forget`, with its reason. Do not add a call in heat_curve.py.

3. class-open. The entity-keying follow-up binds this group: fix review 1 of #3299, VERDICT.md:18, roster carry a2b5f107. The note does not answer it.
   - At #3299 head, `_Held.armed` maps consumer key → baseline with no entity id (off_restore.py:88).
   - `async_restore` writes to the entity that `factory(config)` names now (:160-167).
   - So if a write is armed on entity A, then a crash or restart happens, then an options change to B, the restore writes A's baseline into B and leaves A displaced. If the entity is cleared instead, the consumer is disarmed and A stays displaced.

   The note's record holds `entity_id` (line 36), but no line says which entity the restore writes, or what classify does when the recorded entity differs from the configured one.

   Fix wanted: persist the armed entity id beside the baseline in off_restore's record. State the rule: restore to the recorded entity, or disarm with an INFO when it no longer matches. Add the arm "armed on A, options to B, restart → A restored (or disarmed, logged), B untouched" to §Evidence plan. R10-ARBITER-OFF-RESTORE needs the same rule (VERDICT.md:19), so the off_restore change belongs to whichever group lands first, `decision: orchestrator`.

4. architecture-unsound. §Shared baseline (lines 69-76) proposes a new `baseline.py`. With point 1, the shared baseline is off_restore's armed record, and the arbiter is its second consumer. A pure `classify` helper is sound only where off_restore does not already hold the logic.

   Fix wanted: re-derive whether `baseline.py` is still needed once the record lives in off_restore. If it is, its single owner is off_restore (the classify belongs beside the record it reads), not a third module. The note's D7 argument against sharing the Store (alternative D) is already moot at #3299 head: the Store is shared, per entry and keyed by consumer.

## Dependency on #3299 still moving

#3299's fix review 1 verdict (eb61f80c) is `blocked`. The repair of its block 1 added the `restored(entry, value)` callback (070cff63) that this group's write record would use. No second fix-review verdict exists yet. Points 1-4 depend on off_restore.py's shape at #3299 head: `Restorer`, `async_arm`, `async_restore`, `async_forget` and `restored`. The re-cut should be read against #3299's merged diff (carry ghcp-03 already says so).

## Routed, not revise

- decision: orchestrator. The off rule on a Home Assistant stop now differs between siblings. This note drops P3's stop exception, which matches #3299: `__init__.py` unload says "a Home Assistant stop included". R10-ARBITER-OFF-RESTORE's roster brief still says "on unload (while Home Assistant is not stopping)". One hook should carry one rule, so the arbiter brief should be re-read against the 2026-11-07 ruling.
- decision: orchestrator. The serial order for the off_restore entity-id change (point 3) and for `baseline.py`, between this group and R10-ARBITER-OFF-RESTORE.

## Checked and sound

- The shape follows the owner's ruling and the request in #3284. P1-P7 and O1-O5 are answered as far as the record goes.
- The reserve rule bounds restores inside the budget.
- I4 (kind `offset` unchanged) and no golden moving are the right null control and goldens. No claim file is touched.
- Cost fits size L, and no coordinator line is added.
- Sibling grep (step 3): the off guards and other writers' MODE_OFF sites are dispositioned correctly. No missed heat-curve writer was found at main or at #3299 head.
- Step 5: no other open design/* ref claims heat_curve.py or off_restore.py.

## Notes for the fixer (carried)

- At #3299 head, an unknown kind falls back to offset (entry_config.py:223-224), so the failing test is red because `range_excludes_zero` refuses 5..35 as "not an offset", not because the kind is refused. The test stays red, but its stated reason should be corrected. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-r1)
- #3299 already has an in-memory write cap W4 (`write_cap_per_day`, heat_curve.py:274, `HeatCurveState.writes`). Kind persistent's persisted budget must replace W4 for that kind, not stack on it. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-r2)
- Stale citations to refresh at the predecessor's merged head:
  - coordinator.py:6509/6579, now 6566/6636 at main and 6483/6554 at #3299;
  - inputs.py:596, now 597;
  - `__init__.py`:429, now 434 at #3299;
  - `__init__.py`:372-398, now 373-399;
  - entry_config.py:284, now 289 at #3299.

  Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-r3)

Seat token count: not reported by the harness.
