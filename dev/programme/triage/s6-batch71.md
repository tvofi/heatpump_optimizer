# Proposal triage, session s8, batch 71 (P305)

The rolling batch (V182) after batch 70 (#2987, in the train). Facts were read at origin/main
`507a9ec26`, on the roster branch `origin/handoff/audit-r10-roster`, in its `git log`, and from
`gh issue view` for each wired issue.

## P305: `set-stage done` closes groups that still own carries and open issues

Verdict: ACCEPT as already carried, narrowed. **R10-ORCH-ROSTER-SCHEMA** (`carries-open`) has held
this class's barrier since 2026-10-24: #2733's routing invariants and their "undelivered
remainder" carry. Neither is built.
- The remainder is a `mark-carry` op, a `carry_audit.py roster` arm that reports STRANDED carries,
  and `roster_sync.py` emitting `carries-open` instead of `done` while carries are pending.
- One amendment, carried here. The `carries-open` rule also binds `roster_edit.py set-stage
  done`, the writer every instance below went through, with one predicate shared with
  `roster_sync`.
- The filing's form, a set-stage refusal with `--force-done`, is REJECTED. #2733's verified design
  rules it out in so many words: "roster_sync sets the existing `carries-open` stage instead of
  `done` when pending carries remain; no set-stage refusal". Without the `mark-carry` op the
  refusal has no "delivered" marker to read, so it would refuse every group with any carry, and
  `--force-done` would become the routine path.
- Downgrading `done` to `carries-open` keeps the fact (the code merged) and keeps the group in the
  plan, which is what the filing wants, without a refusal.

Source: `s7/triage-queue-s7.txt` line 18 (orchestrator s8, 2026-10-30T12:34:42Z, slip class,
4 instances today).

Instances, on the roster branch at this batch's read. The stage is from the roster JSON, and
issue state is from `gh issue view <n> --json state`.
- R10-UX-HEALTH: `done`, 20 carries. Of issues 2253, 2260, 2263, 2499, 2809 and 2815, four are
  OPEN (2263, 2499, 2809, 2815). Its last set-stage commit is `c3a7bfd9a` (2026-10-30T12:38Z).
- R10-COP-PARTLOAD: `done`, 4 carries, #2501 OPEN.
- R10-ORCH-BEATD: `done`, 37 carries, #2505 OPEN. This is P299's instance (`s6-batch68.md`): P46,
  P63 and P97 were stranded, and two were re-routed by hand.
- R10-TRAIN-OVERLAP-GRADE and R10-COP-GATE now read `carries-open` (20 and 19 carries). The
  orchestrator repaired them by hand: `968e9c423` and `d920e6bec` today. R10-TRAIN-OVERLAP-GRADE
  has six `set-stage` commits since 2026-10-28 (`git log origin/handoff/audit-r10-roster | grep
  'set-stage R10-TRAIN-OVERLAP-GRADE'`), so the stage was flipped and repaired repeatedly.
- **Count.** Five groups in round 10 closed over live carries (the four filed plus BEATD), so this
  is an audit class. Its barrier is the unbuilt remainder.
- **The barrier is not in the tree.** `git grep -ci mark-carry origin/main -- tools` prints
  nothing. `roster_sync.py` mentions `carries-open` only as a stage it leaves alone (lines 27 and
  96 at main), never as one it sets.

Cost:
- No new group. The remainder is already sized S inside R10-ORCH-ROSTER-SCHEMA, by #2733's
  verifier.
- The amendment is about 5 lines: `op_set_stage` (`roster_edit.py:153`) calls the same pending-
  carries predicate as `roster_sync` and writes `carries-open` with a printed reason. Add two
  self-test rows.
- It adds no API call or standing CPU. Neither file is capped.
- Ask: dispatch the remainder alone, ahead of this group's other carries. Every day it stays
  unbuilt costs a hand repair per merge of a carry-bearing group (six on one group since
  2026-10-28).

Binding:
- Owed work dropped silently out of the plan and dispatch on five groups, and the hand repair
  recurs.
- The fix exists as a design the owner requested and a verifier sized. What is missing is the
  dispatch, plus the one writer the design left out.
- A refusal would contradict that design. Until `mark-carry` exists it could not tell a delivered
  carry from a pending one.

Carry text (for `roster_edit.py append-carry R10-ORCH-ROSTER-SCHEMA`, citing
`triage: dev/programme/triage/s6-batch71.md#P305`): "Amends the #2733 remainder (P305, queue
2026-10-30T12:34Z). Dispatch the remainder alone, ahead of this group's other carries.
- `roster_edit.py set-stage <G> done` (`op_set_stage`, line 153 at 507a9ec26) applies the same
  rule as `roster_sync`, through one predicate the two share. When the group holds a pending
  carry (not `mark-carry`ed implemented, moved or dismissed, and not legacy at the cut-over), the
  stage written is `carries-open`, and it prints `set-stage <G>: done -> carries-open (<n> pending
  carries)`, rc 0.
- An open wired issue is reported in that same line, not refused.
- Do NOT add a refusal or a `--force-done` flag. #2733's design rules out a set-stage refusal, and
  the downgrade keeps the group in replan and dispatch.
- Observed 2026-10-30: R10-UX-HEALTH (20 carries, 4 open issues), R10-COP-PARTLOAD (4, #2501),
  R10-ORCH-BEATD (37, #2505) sit `done`. R10-TRAIN-OVERLAP-GRADE and R10-COP-GATE were set `done`
  and repaired by hand to `carries-open` (`968e9c423`, `d920e6bec`). TRAIN-OVERLAP-GRADE has six
  set-stage commits since 2026-10-28.
- Self-test rows:
  - A fixture group with one pending post-cut-over carry, given `set-stage done`, is written
    `carries-open`.
  - Null: a group whose carries are all marked, or legacy, is written `done`.
- One mutant: bypass the shared predicate in `op_set_stage`, and the first row fails."

To the orchestrator, not carried: R10-UX-HEALTH, R10-COP-PARTLOAD and R10-ORCH-BEATD read `done`
over open issues and carries now. Set each to `carries-open` (or re-home their carries) until the
remainder lands.
