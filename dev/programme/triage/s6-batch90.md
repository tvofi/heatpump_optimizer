# Proposal triage, session s8, batch 90 (P327)

The rolling batch after batch 89 (handoff `triage-s8-batch89`). Facts were read at origin/main
`cabfaadc3` and on the roster branch.

## P327: merge verdicts at the head of BLOCKED/REVIEW_REQUIRED PRs never print MERGE-READY

Verdict: ACCEPT as already ruled. This is **P294** (`s6-batch64.md#P294`), whose fix is the whole
brief of **R10-FLY-TICK-APPROVAL-OWED** (`not-started`, S). Its `next_step` already reads
"dispatch a fixer (fly-in; ahead of other instrument fly-ins ...)". The group was never
dispatched, and today's six PRs are the same class recurring. One carry adds the instances, the
priority, and one clarification.
- **What P294 already specifies.** The filing's candidate is P294 under another name.
  - `prs()` asks for `reviewDecision`. Today it does not: the `--json` list at
    `orchestrator_tick.py:554` names `mergeStateStatus` and no review field.
  - `verdict_levels` (`orchestrator_tick.py:653`) adds `APPROVAL-OWED: #N <head8>`, flagged: a
    merge verdict at the head, `BLOCKED`, `REVIEW_REQUIRED`.
  - A catch-all `UNLEVELLED:` line handles a merge verdict at the head in any state no arm covers.
  - Both prefixes join `owed_unactioned.py`'s family.
  - The #2980 review's null rows are included: a pending or red required check prints neither
    line, and a one-pass `UNKNOWN` prints no `UNLEVELLED`.
- **Keep P294's name, `APPROVAL-OWED`, not `MERGE-READY`.** The two lines own different actions.
  `MERGE-READY` means the approval exists. `APPROVAL-OWED` means queue the PR for the train,
  which posts the approval itself (`app_approve.sh`, or the owner's approval under `--mandate`).
  The carry states that action in the line's docstring and in `owed_unactioned.py`'s family text,
  so the reader of the line knows to queue rather than wait.
- **REJECTED: the `(needs tvofi)` suffix on code-owned paths.**
  - It costs a per-PR files read each pass.
  - The train already stops a code-owned head without `--mandate` and names it
    ("code-owned (...) and no --mandate given: the owner's review").
- **Root cause.** As P294 recorded: the idle-PR class
  (`dev/audit/rca/R10-RCA-OWED-UNACTIONED.md`, process state (c)), with the catch-all as its
  barrier. The barrier was ruled 2026-10-30 and not built. P305's stranded-carry repair does not
  apply, because the group is live. The fault is dispatch order, which the carry's priority note
  addresses.

Source: the orchestrator s8's message of 2026-10-31 (slip, priority).

Instances, from the filing:
- #3022 (HOTFIX), verdict at the head from 05:09Z;
- #3029 from 03:04Z;
- #3030 from 03:47Z;
- #3031 from 04:20Z;
- #3033 from 04:42Z;
- #3034 from 07:08Z.

None was queued until the orchestrator read the verdicts by hand at 07:18Z, about 2 h for the
hotfix. P294's own instances were #2962, #2976 and #2977 (11 h, 5 h and 5 h). That is nine PRs
in two days.

Cost: as P294 sized it, S. The carry adds the instance rows to the fixture list and no new arm.

Binding:
- An unbuilt, already-ruled level line cost a hotfix about 2 hours and five record PRs between
  0.2 and 4 hours today.
- Building it costs an S fixer.
- Dispatching it now is clearly worth more than any instrument fly-in queued ahead of it.

Carry text (for `roster_edit.py append-carry R10-FLY-TICK-APPROVAL-OWED`, citing
`triage: dev/programme/triage/s6-batch90.md#P327`): "P327 (orchestrator s8, 2026-10-31,
priority) re-files this group's brief (P294) unbuilt.
- Six PRs had a merge verdict at their head and no level line: #3022 HOTFIX (from 05:09Z),
  #3029, #3030, #3031, #3033 and #3034. All were BLOCKED/REVIEW_REQUIRED because the train posts
  the approval itself. They waited for a hand read at 07:18Z.
- Priority: dispatch ahead of every other instrument fly-in. The brief is complete without this
  carry, so dispatch need not wait for it to land.
- Keep the name `APPROVAL-OWED`, and state its action in the `verdict_levels` docstring and in
  `owed_unactioned.py`'s family text: queue the PR for the train, which posts the approval.
- No code-owned suffix: the train already names a code-owned stop.
- Fixture: one row in the shape of #3022 (BLOCKED, REVIEW_REQUIRED, `gate` green, merge verdict
  at the head) prints `APPROVAL-OWED`, beside the existing MERGE-READY rows. Its null control is
  the same row with a required check red, which prints neither line."
