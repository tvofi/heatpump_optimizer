# Proposal triage, session s8, batch 70 (P304)

The rolling batch (V182) after batch 69 (open, branch `fix/triage-s8-batch69`). Facts
were read at origin/main `b646e8306`, on the roster branch `origin/handoff/audit-r10-roster`, and in
the orchestrator's `s8/plan-opt/` scratch (its rosters `scratch-*.json` and its prototype
`replan_cp.py`).

## P304: the plan charges a critical-path group a slot that policy says it never waits for

Verdict: ACCEPT narrowed, in two parts, both on **R10-ORCH-ROSTER-SCHEMA** (`carries-open`). That
group already carries `tools/plan/replan.py`'s stage predicate (P131, `s6-batch26.md`: "make `replan.py` call
roster_lib's one closed-stage predicate").
- (a) New carry: `replan.py` schedules a ready critical-path group without a slot and without a
  seat, as `dev/governance/roles/orchestrator.md` section 5 dispatches it. `check_plan` exempts
  exactly those groups from the slot and seat counts and keeps every other refusal. The filing's
  prototype instead drops the in-flight checks wholesale. Its `main()` filters out every
  `check_plan` line containing `in flight`, `working` or `peak`, which would also stop refusing
  an over-cap non-critical schedule. That part is REJECTED.
- (b) The filing's "absorbed as closed" half is ACCEPT as already carried. R10-ORCH-ROSTER-SCHEMA
  holds it three times: the absorbed-edge closure (#2554), the consolidation-folds carry (replan
  schedules absorbed groups as phantom work), and P131's single predicate. No new text.

Source: `s7/triage-queue-s7.txt` line 17 (orchestrator s8, 2026-10-30T10:12:06Z, plan-opt seat,
measured).

Instances:
- **The policy.** `orchestrator.md` section 5 (lines 100-105 at main) says: "A ready
  critical-path group starts regardless of every cap". A group in the plan's `critical_path` whose
  `after` groups are done is dispatched at the WIP cap, a drain-first hold, a coordinator limit
  or the seat cap alike.
- **The model.** `replan.py` admits a ready group only `while ready and free_slot() is not None`
  (lines 473-480 at main). A tier-0 (critical-path) group sorts first, but it still waits for a
  free slot.
- **The size of the disagreement, re-measured here.** This seat ran main's `replan.py` and the
  orchestrator's `replan_cp.py` over the same four rosters, at `--start 2026-10-30T09:58:00Z`,
  with main's `tools/plan/durations.json`. Projected closure:

  | roster | main | CP exempt | shift |
  |---|---|---|---|
  | `scratch-base.json` | 2026-11-04T19:27Z | 2026-11-04T12:27Z | -7.0 h |
  | `scratch-comb.json` | 2026-11-03T23:21Z | 2026-11-03T19:24Z | -4.0 h |
  | `scratch-cp.json` | 2026-11-03T23:21Z | 2026-11-03T17:43Z | -5.6 h |
  | `scratch-x.json` | 2026-11-03T23:21Z | 2026-11-03T17:43Z | -5.6 h |

  All eight runs exited rc 0. The filing's -4.4 h (06:21Z to 01:57Z on 2026-11-02) came from its
  own run's inputs, and the saved `plan-cp.json` reads `2026-11-02T01:57:00Z`. The absolute dates
  here differ because the durations file differs. The direction and size agree: 4 to 7 h on
  every roster.
- **The prototype's diff against main** is 4 added lines at the scheduling site (each ready
  tier-0 group starts at `t` on a synthetic slot numbered past `slots`). It also changes
  `main()`'s `bad = check_plan(plan)` to drop every line containing `in flight`, `working` or
  `peak`.

Cost:
- (a) is about 10 lines in `replan.py`: the tier-0 start, plus a `check_plan` that leaves tier-0
  groups out of the slot and seat counts. Add two self-test rows.
- It adds no file, API call or standing CPU; `replan` runs once per sweep.
- `tools/plan/replan.py` is not a capped file.
- It goes into a group already open on the same file. It may be dispatched alone, ahead of that
  group's other carries.

Binding:
- The plan is the round's schedule model, and the record beat and the plan page re-render it
  every sweep. Today it contradicts a three-times-restated owner rule by 4 to 7 h of projected
  closure on every roster measured. It also orders non-critical work behind slots that critical
  work does not hold.
- About 10 lines for that is clearly positive.
- The narrowing keeps `check_plan` a refusal: the prototype's wholesale filter would print
  PLAN OK on a plan that puts seven non-critical groups in six slots.

Carry text (for `roster_edit.py append-carry R10-ORCH-ROSTER-SCHEMA`, citing
`triage: dev/programme/triage/s6-batch70.md#P304`): "From P304 (queue 2026-10-30T10:12Z, plan-opt
seat). May be dispatched alone, ahead of this group's other carries.
- `tools/plan/replan.py`'s scheduler starts a ready tier-0 (critical-path) group at the instant
  it is ready, without taking one of `slots` or `seats`. This matches `orchestrator.md`
  section 5: a ready critical-path group starts regardless of every cap.
- A tier-0 group never displaces a running group, and it is not counted in peak in-flight.
- `check_plan` leaves exactly the tier-0 groups out of the slot and seat counts. Every other
  refusal stays, including in-flight over `slots` for non-critical groups. Do NOT filter
  `check_plan`'s output by substring, as the plan-opt prototype did.
- Measured, main against CP-exempt over four rosters at 2026-10-30T09:58Z: projected closure
  moves -4.0 h to -7.0 h.
- Self-test rows:
  - With `slots=1`, a ready tier-0 group and a running tier-2 group run at once; today the
    tier-0 group waits.
  - Null: two tier-2 groups with `slots=1` still serialise, and a planted third non-critical
    group in flight is still refused by `check_plan`.
- One mutant: put tier-0 back on the slot path, and the first row fails."
