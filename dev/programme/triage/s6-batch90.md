# Proposal triage, session s8, batch 90 (P327, P328)

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

## P328: a cloud reviewer died in setup, and nothing flagged it for 5 h 15 min

Verdict: ACCEPT narrowed. Add one git-only arm to **R10-FLY-TICK-APPROVAL-OWED** (the
tick-verdict-level group P327 routes to). It flags a dispatched review at the PR's current head
that has no verdict after 90 minutes. The run-log read is REJECTED.
- **REJECTED: reading the RemoteTrigger run log.** P280 (`s6-batch60.md#P280`) rejected exactly
  this read. It is a call of the orchestrator's own session, and nothing in the tree reads a cloud
  run back: `cloud_dispatch.py` writes `cloud-sessions.tsv` and never reads a run. Liveness is
  judged from the work, not the session, and the work here is in git.
- **The arm.** In `verdict_levels` (`orchestrator_tick.py:653`), which already reads each open
  PR's verdict comments:
  - Condition: the bus dispatch record (`_dispatched`, `orchestrator_tick.py:712`) holds
    `(pr, head)` for the current head, and no approver verdict names that head.
  - It prints `REVIEW STALLED: #N <head8> <minutes>m`, flagged, when the
    reviewer dispatch ref's tip commit time is more than 90 minutes old. That ref is
    `dispatch/reviewer-rev-<N>`, `cloud_dispatch.py`'s `dispatch_ref`, re-pushed per dispatch.
  - The minutes come from the ref's commit time: one local `git for-each-ref` over the refs the
    tick already fetches, with no API call.
  - `REVIEW STALLED:` joins `owed_unactioned.py`'s family. Its action is to re-fire the reviewer
    with the same nonce at the same head, as the orchestrator did for #3027.
- **Why 90 minutes, measured by triage.** The sample is the older per-head refs,
  `dispatch/reviewer-<N>-<sha8>`, one per dispatch. The per-PR `rev` refs keep only their last
  dispatch. Of 231 of those refs with a later verdict commit on `verdict/<N>`, the dispatch-to-first-verdict latency is:

  | Statistic | Minutes |
  |---|---|
  | p50 | 17 |
  | p75 | 32 |
  | p90 | 56 |
  | p95 | 70 |
  | max | 959 |

  | Threshold | Dispatches over it |
  |---|---|
  | 45 min (the filing's) | 34 of 231 (15%) |
  | 60 min | 21 |
  | 90 min | 6 (2.6%) |
  | 120 min | 4 |

  - The filing's 45 minutes would flag one healthy review in seven.
  - At 90 minutes the line fires on the tail, where #3027's 315 minutes and the 959-minute
    outlier sit.
- **Controls.**
  - Failing row first: a dispatch record at the head, a dispatch ref 100 minutes old and no
    verdict prints `REVIEW STALLED`. Today it prints nothing.
  - Null: the same at 30 minutes prints nothing.
  - Null: a verdict at the head prints no stall, whatever its age.
  - Null: a dispatch at an older head after the head moved prints no stall. That case is
    REVIEW OWED's.
  - One mutant: drop the age test, and the 30-minute row fires.
- **Order inside the group.** P327's APPROVAL-OWED arm is the priority. This arm must not delay
  it: if the fixer has already handed off, it lands as a follow-up PR on the same group.

Source: the orchestrator s8's message of 2026-10-31 (slip).

Instances: #3027 (batch 82). Reviewer session fired 02:05Z, died in "Running setup script", found
by hand at 07:20Z: 315 minutes, during which #3027 and its roster op b82 were held. The probe's
tail holds 4 more dispatches over 120 minutes since the dispatch refs began.

Cost: S, about 15 lines in `verdict_levels` plus four fixture rows and one mutant, inside a group
already being dispatched. No API call and no new file.

Binding:
- A dead reviewer holds a PR and everything behind it until someone looks. Here that was 5 h
  15 min, and the tail shows it recurring.
- A git-only age test inside the tick's existing verdict pass costs an S arm.
- At 90 minutes it fires on 2.6% of reviews. That clearly beats hand discovery.

Carry text (for `roster_edit.py append-carry R10-FLY-TICK-APPROVAL-OWED`, citing
`triage: dev/programme/triage/s6-batch90.md#P328`): "P328: a second level arm, git-only. In
`verdict_levels`, a PR whose current head is in the bus dispatch record (`_dispatched`), with no
approver verdict naming that head, prints `REVIEW STALLED: #N <head8> <minutes>m` (flagged) when
its reviewer dispatch ref's tip (`dispatch/reviewer-rev-<N>`, `cloud_dispatch.py` `dispatch_ref`) is more than 90 minutes old.
- Read the age with a local `git for-each-ref` and no API call. Never read a cloud run log
  (P280).
- Add `REVIEW STALLED:` to `owed_unactioned.py`'s family. The action is to re-fire the reviewer
  with the same nonce at the same head.
- Basis: #3027's reviewer died in setup at 02:05Z and was found by hand at 07:20Z. Over 231
  dispatch refs, the latency to the first verdict is p50 17 min and p95 70 min, and 6 exceed
  90 min.
- Rows:
  - 100 min old, no verdict: prints the line.
  - Null: 30 min old prints nothing.
  - Null: a verdict at the head prints nothing.
  - Null: a dispatch at an older head prints nothing (REVIEW OWED's case).
  - One mutant drops the age test, and the 30-min row fires.
- P327's APPROVAL-OWED arm goes first. This arm may follow in a second PR on this group."
