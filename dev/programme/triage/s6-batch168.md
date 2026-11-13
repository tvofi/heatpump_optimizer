# Proposal triage, session s14, batch 168 (P582, P583)

This batch rules two orchestrator requests made 2026-11-11 under mandate 6715477401 (scope
all): where R10-GENERIC-HEAT-CURVE-PERSISTENT's open carry 6 goes, and why the plan sized that
group as it did. The bar and the denominators are batch 141's.

Sources:
- origin/main `a7628041dc`. Every line number below is at that commit.
- The roster at `origin/handoff/audit-r10-roster` `de1cf3d732`.
- PR 3402's merged body, read once with `gh pr view 3402 --json body`. The merge commit is
  `45adb0c3b425dc44e72fd9ce4ef51f480b5a3af6`; the head is `c12789515e`.
- `tools/plan/durations.json`, `tools/plan/replan.py` and `tools/plan/size_durations.py` at
  `a7628041dc`.

## P582: GHCP-CARRY6-MQTT-OFF-HOME

Verdict: ACCEPT, as a new group R10-ECL110-MQTT-OFF-NEUTRAL: size S, `after`
R10-ARBITER-OFF-RESTORE. It is not a carry on R10-ARBITER-OFF-RESTORE.

Source: the orchestrator's owner ruling under the mandate. When the optimizer is turned off or
unloaded, no actuator arm may leave the pump displaced, MQTT included; "byte-identical" was
W7's scope limit, not a product decision. The ruling asks for a measurement first. The carry is
PERSISTENT's carry 6 (ghc-d02, body item 711d4be1). PR 3402 left it untouched (`## Roster
carries`: "Carry 6 (ghc-d02): untouched").

Instances, as static reads at `a7628041dc`:
- **The MQTT arm.** `heat_curve.publish` (`heat_curve.py:237-262`) publishes the MQTT topics
  through `publish_ecl110_topics` on every call. `mode_off` gates only the entity arm (`:260`).
- **No publish on MODE_OFF.** `coordinator.async_publish_current_action` returns before
  publishing when `self._mode == MODE_OFF` (`coordinator.py:7683-7687`, "off writes nothing").
  The only other caller, `_async_peak_guard_transition`, returns on MODE_OFF the same way
  (`:8827`).
  - Statically, then, the last displace published before off stays the last command on the
    topic.
  - Retain is a user option, `DEFAULT_ECL110_RETAIN = False` (`const.py:1543`). With retain on,
    the broker keeps that last displace for any later subscriber. With it off, the controller
    bridge keeps whatever it last received.
- **The null control** the brief must measure against: the entity arm (non-MQTT), which
  `off_restore` restores to its baseline on MODE_OFF and unload since #3299 and 3402
  (`heat_curve.py:151` registers the consumer).
- **Existing groups first.**
  - The only live groups naming `mqtt` or `ecl110` with `coordinator.py` or `climate.py` in
    their files: R10-GENERIC-HEAT-CURVE-PERSISTENT itself. It is carries-open, with a merged PR.
  - R10-ARBITER-OFF-RESTORE (in progress; PR 3404 frozen mid conflict-repair) owns the restore
    of the pump arbiter's set-point, a different seam. It shares `coordinator.py`,
    `__init__.py` and `tests/features.py`.
  - A carry there would re-open a frozen PR, or its part 2, for a seam it does not own. A new
    group ordered after it avoids both.

Cost:
- About 15 production lines, an off and unload publish of displace 0 on the MQTT topics.
  The coordinator's MODE_OFF transition and the `off_restore` unload path are its two call
  sites.
- About 40 test lines: a failing test first, with a mutation proof on each path. A test that
  the null-control entity arm is unchanged.
- A docs line in `docs/ecl110.md`.
- No capped file; no row for these files in `tests/structure_budgets.json` at `a7628041dc`.
- If the measurement shows the topic already neutral, the cost is one measurement and a
  dismissal.

Binding:
- **ACCEPT, new group R10-ECL110-MQTT-OFF-NEUTRAL.** S, production, `after`
  R10-ARBITER-OFF-RESTORE, because the two share three files. Its brief:
  1. **First, measure.** On the MQTT ECL110 arm, find what value stands on the topic after
     MODE_OFF and after unload, retained or last published, with retain on and off. Measure the
     entity arm restored by 3402 as the null control.
  2. **If a non-zero displace stands,** publish displace 0 on both paths. Pin it with a failing
     test first and a mutation proof per path.
  3. **If the topic is already neutral,** record the command and its output, and mark the carry
     dismissed with that evidence.
  4. **Also,** re-read #3299's merged diff (`20d96598c9` is on main) and re-check design carries
     ghcp-03 and ghcp-r3's citations at origin/main. 3402's `## Design carries` re-checked
     them only at `e066a630`, "to be re-checked at the merged base".
- PERSISTENT's carry 6 is dropped once the new group's entry is read back. That is the
  orchestrator's instruction (c).

## P583: PLAN-HELD-SIZE-NONE-MEASURED

Verdict: REJECT a repair of `held_rows` / `prs_of_groups`: there is no mis-map, and a
re-measure changes this group's figure by 0 min. DEFER the held-group part granularity, on the
terms below.

Source: the orchestrator's request (d). The plan's duration basis read "8 carries, none measured
as answered", while `cited_carries()` over the merged 3402 body returns 7 answered.

Instances:
- **Where the words come from.** `replan.held_open` (`replan.py:489-498`) prints "none measured
  as answered" when `durations.json`'s `held_open_carries` has no record for the group.
- **The measure is stale, not mis-mapped.**
  - `durations.json` has `sizes_measured_at` 2026-11-01T07:38:26Z. Its last change on main is
    `857586f29f`, 2026-11-06.
  - `size_durations.py` runs by hand only. CI runs its `--self-test` (`governance.yml`), not the
    measurement.
  - PR 3402 merged 2026-11-10T14:26:57Z, after the record.
  - Of the 8 groups now carries-open, **0** have a record. All 27 recorded groups are no longer
    carries-open.
  - `prs_of_groups` (`size_durations.py:197-213`) maps 3402 to the group through the roster's
    `resume.commit`, which is the merge commit `45adb0c3b4`. Nothing is mis-mapped.
- **What the stale measure cost here: 0 min.**
  - `durations.json` holds `carries_per_part` 11 and `carry_part_hours` 19.8. A held group is
    sized as `ceil(open / 11)` parts x 19.8 h (`replan.py:530-534`).
  - 8 open gives 1 part, 1188 min. 1 open (carry 6 alone, the measured truth) gives 1 part,
    **the same 1188 min**.
  - The 1188 min at the head of the binding chain came from one owner-decision carry left
    open with the group carries-open. Re-homing that carry (P582) and the `set-stage done`
    release it; a re-measure would not have.
- **The granularity.** All 7 carries-open groups with any open carry are planned at exactly
  1188 min, whatever their 1-8 open carries. One part of 11 carries costs the same as one carry.

Cost:
- A repair to the mapping: none is owed.
- A scheduled re-measure: one GraphQL fetch of every PR since `SINCE` per run. That is an API
  cost, against a 0 min change on this instance.

Binding:
- **REJECT the mapping repair.** There is no mis-map, and the re-measure moves this instance by
  0 min. The binding cost is a change to `tools/plan/` that buys nothing here.
- **DEFER the part granularity** (one carry planned as a whole 19.8 h part). It changes on a
  measured carry-part duration by open-carry count, from the merged part PRs. The owning group
  is whichever live group holds `tools/plan/replan.py`. If the measure shows a single carry well
  under a part, `held_open` should size by carries, not whole parts.
