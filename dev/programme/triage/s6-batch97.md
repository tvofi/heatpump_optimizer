# Proposal triage, session s9, batch 97 (P352)

The rolling batch after batch 96, which was pushed first and left at its head. Facts were read at
origin/main `8fec54ee2`, at the round's roster branch `origin/handoff/audit-r10-roster`
(`b3558fc7c`), at `handoff/r10-replay-real-day` `73ef64912`, and at `handoff/r10-roster-schema`
(`784f8391b`, PR #3054, open).

## P352: re-home R10-REPLAY-REAL-DAY's live-bundle carries

Verdict: ACCEPT, as a re-home. Two of the four items move to R10-ROUND-PLAYBOOK as one carry, with
both source entries marked `moved`. One is a restatement of another and moves with it. One,
D15 lead L6, is answered by code already on main and is marked `dismissed`. No roster group is
added.

Source: orchestrator s9, by message, 2026-11-01. R10-REPLAY-REAL-DAY handed off at `73ef64912`.
The orchestrator's carries "4, 6, 8 and 9" are 1-based, which is the numbering the handoff body
uses. In `mark-carry`'s 0-based indices they are 3, 5, 7 and 8. The ops below select by `--match`,
so a shifted index cannot hit the wrong entry.

Instances:
- **The fixer left the four items undone, each for lack of a live bundle.** The handoff body on
  `handoff-body/r10-replay-real-day`, Carry list:
  - "Carry 4 and Carry 6 ... not done. They read a live diagnostics bundle's learner snapshots,
    which the replay export does not carry".
  - "Carry 8 (D15 L6 ...): not done; it needs a live bundle's self-test record".
  - "Carry 9 (R10-SCORES' `--bundle PATH` scale-drift harness ...): not done; it needs the
    owner's diagnostics bundle".
- **No open group reads a bundle.** A regex over the roster branch's groups for
  `diagnostics bundle|live bundle|--bundle` matches:
  - groups that are `done`: R10-PARAMS-OWNER, R10-SAV-COMFORT, R10-DIAG-REDACT and
    R10-STORE-RACES;
  - R10-COP-GATE (`carries-open`). Its bundle carries 2 and 3 are triage of the 2026-10-24
    bundle, and its leads L1 and L2 (carries 8 and 9) are verified by driving the code, not by
    reading a new bundle;
  - R10-REPLAY-REAL-DAY itself.

  No open group has a step that receives a bundle. D15's own brief takes the bundle as an input
  "named in your task" (`dev/governance/dimensions/D15.md`, Inputs), and only an audit round's
  D15 seat is given one.
- **Carry 6 restates carry 4.** Index 5 opens "**R10-REPLAY-REAL-DAY** carry 4 (D15 lead L9), in
  its brief on `origin/main`" and repeats index 3's ask and controls.
- **Carry 8 (L6) asks a question the code at main answers.** It asks whether a quiet
  change-reporting meter can age past the self-test's rule without an outage, and if it can, to
  key the age on the last report, not the last change:
  - The self-test's sensor block, `sensor_sanity` (`debugger.py` line 260), copies `problem_inputs`
    and `input_ages_minutes` from the coordinator's data (`_HEALTH`, line 88).
  - The coordinator fills those from the input health (`coordinator.py` lines 5118-5120).
  - That health takes its age from `InputReader._age_minutes` (`inputs.py` line 842), and so from
    `state_age` and `state_stamp` (line 219). `state_stamp` reads `last_reported` first, then
    `last_updated`, then `last_changed`.
  - That precedence has been on main since `a1bdb11c1` (#775, 2026-09-11; `git merge-base
    --is-ancestor` true). That is before the 2026-10-25 install that produced L6.
  - It is pinned by `tests/features.py`, check "D1-s5-01" (lines 2219-2255): the cell
    (reported 5 min, updated 480 min) reads age 5.0, which is L6's null control, and the cell
    (400, 400) stays aged.
  - So the rule already keys on the last report. A meter that writes no state for 238 min is
    silent to Home Assistant, and no field a bundle carries would tell that apart from an outage.
    L6 itself says "historical only".
- **Index 8 (the scale-drift harness) and indices 3 and 5 (`unhealthy_input`) need the owner's
  bundle.**
  - `dev/audit/harnesses/r10_scores_envelope.py` takes `--bundle PATH` (line 37) and prints the
    stored scale and the grade on both bases.
  - `snapshots.py` line 115 records `unhealthy_input` on each weekly snapshot.
  - The replay export carries neither (handoff body, above).

Cost:
- **Holding them on R10-REPLAY-REAL-DAY.**
  - #3054's `closing_stage` refuses `set-stage done` while a carry is unmarked. The group would
    then stay `carries-open` until the owner supplies a bundle.
  - The owner is away, and no round-10 seat is given a bundle. So that is an open roster group
    at round 10's closure, which the closure criterion forbids.
  - Its other carries are done or recorded at its handoff (body, carries 1, 2, 3, 5, 7, 10, 11).
- **Moving them.**
  - Four roster-queue ops: one `append-carry` and three `mark-carry`, plus one `dismissed` mark.
    That is no seat time beyond the roster seat's queue run.
  - R10-ROUND-PLAYBOOK goes from 17 carries to 18. It is the roster's home for round-11 items:
    its carries 1-6 and 8-9 are round-11 decision items, and stranded carries 9, 14, 45 and 52
    were folded into it on 2026-10-31.
  - The carry adds no file and no check. The group's brief already holds `dev/audit/README.md`
    to its `policy_lint --budgets` cap, and the carry restates that.
- **The L6 dismissal.** It costs nothing, and it spares a round-11 D15 seat a read whose answer
  the code already gives.
- No capped file is touched by this ruling. Its diff is this one markdown file.

Binding: no open round-10 group can read a live bundle, so a bundle-only carry left on a closing
group is a guaranteed strand. The existing group that carries round-11 items takes it. Choosing it
avoids a new group.

Carry (R10-ROUND-PLAYBOOK, `s7/carries/b97-P352.txt`):

> Round-11 D15 inputs, re-homed from R10-REPLAY-REAL-DAY (its 0-based carries 3, 5 and 8;
> handoff `73ef64912`). Both items read the owner's live diagnostics bundle, which no round-10
> seat holds, so they belong to round 11's D15 run. They are not part of this group's own README
> work. Where the playbook describes the audit-dimensions phase, it states that the round-11 D15
> seat's task names these reads:
>
> (1) D15 lead L9. Read `unhealthy_input` from each weekly learner snapshot (`snapshots.py`),
> name the input that marked each unhealthy snapshot, and say whether it was genuinely silent or
> whether outdoor's 180 min on-change limit flagged a quiet, healthy sensor. Change that limit only
> on that evidence. Controls: a week with every input reporting names none (null); a week with one
> input silent all day names that input.
>
> (2) The R10-SCORES scale drift. Run `dev/audit/harnesses/r10_scores_envelope.py --bundle PATH`
> on the owner's bundle, to measure the suspected 2.6x scale drift and the band on the owner's
> house.
>
> No figure is stated here that the bundle must supply. The README stays within its
> `policy_lint --budgets` cap.
>
> triage: dev/programme/triage/s6-batch97.md#P352

Roster ops (queued #held until this file and `mark-carry`, PR #3054, are both on origin/main;
the append runs before the marks):
1. `append-carry R10-ROUND-PLAYBOOK @.../s7/carries/b97-P352.txt`
2. `mark-carry R10-REPLAY-REAL-DAY --match 'From R10-HEAT-METER (#2261; D15 lead L9' moved R10-ROUND-PLAYBOOK`
3. `mark-carry R10-REPLAY-REAL-DAY --match 'carry 4 (D15 lead L9), in its brief' moved R10-ROUND-PLAYBOOK`
4. `mark-carry R10-REPLAY-REAL-DAY --match 'STRANDED CARRY 54' moved R10-ROUND-PLAYBOOK`
5. `mark-carry R10-REPLAY-REAL-DAY --match 'STRANDED CARRY 34' dismissed met on main: inputs.state_stamp reads last_reported first since a1bdb11c1 (#775), pinned by tests/features.py D1-s5-01 (triage s6-batch97.md#P352)`

Rule run on each instance:
- **Index 3**: needs a bundle. Moved, and covered by the carry's item (1).
- **Index 5**: a restatement of index 3. Moved with it.
- **Index 7**: met on main, as shown above. Dismissed.
- **Index 8**: needs a bundle. Moved, and covered by the carry's item (2).
- **Index 9** (`loop_cpu_ratio`) and the others: these are the group's own work and are not
  touched.
