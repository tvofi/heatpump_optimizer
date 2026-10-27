# Proposal triage, session s7, batch 39 (P207-P210)

Four proposals, relayed by the orchestrator on 2026-10-27 in its funding order (P207, P208,
P209, P210). None is yet in `proposals.md`, whose newest entry is V123. Facts read at
origin/main `67178dc6a`; this seat's own samples at 17:10Z and 53 s later.

## P207: a verdict publishes before anything checks its findings name a destination (V127)

Verdict: ACCEPT -> a carry of **R10-FLY-CARRY-DISPOSITION** (`resume.stage` `not-started`;
the only group whose `files` name both files the change touches,
`tools/audit/seat/bus.sh` and `tools/audit/carry_audit.py`).

Source: orch s7 relay P1, 2026-10-27; not yet in `proposals.md`.

Instances: the class is a published verdict whose finding bullets name no `Carry:`, and the
refusal exists on the train side only.
- (1) Two approving verdicts (#2876, #2881) were published, confirmed and posted, then parked
  by the train at `PRE-FLIGHT: 0 of 1 admitted` / `TRAIN_RC=1` for non-blocking bullets with no
  destination. Cost per slip: a routing-only re-issue seat (opus, ~6 min wall), two fresh
  dispatches, two fresh confirms, a #201 comment, about 50 minutes of merge-cycle latency. The
  orchestrator's measurement; it is not re-derived here -- `grep -rh 'PRE-FLIGHT'` over the
  session's train directory prints nothing and the only `TRAIN_RC=1` lines there end
  2026-10-26T05:15:57Z.
- (2) The class has an earlier recorded instance: `grep -n 'PRE-FLIGHT' merge-report.txt` in the
  session state prints
  `2026-10-24T10:06:03Z parked #2683 train 20261024-100534: PRE-FLIGHT carry_audit: 4 finding item(s) with no valid Carry (first: review 6379079217 item 57e267d2 unrouted)`.
- (3) The check already reads exactly this text, and only at admission:
  `tools/audit/seat/queue_pre_flight.py:176-205` (`findings_gate`) reads the body and every
  `Fix review:` verdict comment (`carry_audit.finding_rows(body, comments)`), audits them
  (`carry_audit.audit(body, comments, dests)` at 199) and refuses naming the count and the first
  item.
  `bus.sh`'s `push_verdict()` (lines 200-228) names no carry check at all:
  `git grep -n 'carry_audit' origin/main -- tools/audit/seat/bus.sh` prints nothing.

Cost: one carry-audit run per published verdict, before `append_commit` (bus.sh:228). Measured
over three runs: `carry_audit check --body` on a body with no finding rows prints its summary in
0.64/0.62/0.60 s real (`/usr/bin/time -p python3 -I tools/audit/carry_audit.py --roster-ref
origin/main check --body <body>`); a verdict with findings adds the roster read, measured at
0.63/0.65/0.65 s real (`load_dests('.', 'origin/main')`, 208 groups) and 1.13 s real on the
audit roster ref the check actually reads (`origin/handoff/audit-r10-roster`, 211 groups). So
about 1-2 s per verdict, as estimated, and no new rule: carry_audit's own `audit` decides, as decision 0012 requires.

Binding: the refusal must be carry_audit's own -- same parser, no second reading; it must run
before `append_commit` so `review/<pr>` does not move on a refusal (the precedent is the
host-path guard in `append_commit`, pinned by bus.sh:1209-1221 where `review/7` does not move); a verdict with no finding rows passes without reading the
roster (queue_pre_flight:192's own short-circuit, `finding_rows(...)[0]` empty); and the line
must name the count and the first item, so the reviewer reads in the refusal what the train
would otherwise have said.

## P208: the body's `## Head` is checked last, after the expensive steps (V128)

Verdict: ACCEPT -> a carry of **R10-RCA-BODY-LINT** (the group that owns `tools/pr/prepr.sh`,
`tools/audit/seat/body_push.sh` and `tools/policy/policy_lint.mjs`; `resume.stage` `done`, so the
roster op reopens it first, the route P196 took).

Source: orch s7 relay P4, 2026-10-27; not yet in `proposals.md`.

Instances: both are bodies whose `## Head` named the head they were written at, not the head the
prepr ran on, because `update_pr.sh`/`open_pr.sh` merge `main` before pushing.
- (1) R10-FLOW-BOARD's body re-take had to be redone: it named `c35a4e313` and the checkout was
  at `4c62b9804` after the merge. Recovered in minutes because it was caught before the prepr.
  Both shas are the board's own `handoff/r10-flow-board` update lines at 16:0xZ and 16:5xZ.
- (2) R10-BUFFER-STORE did not recover, and the log is local. A 40-minute scoped prepr took the
  heavy slot and then refused:
  `grep -n 'REFUSE' ~/.local/state/hpo/pr/r10-buffer-store/p1.log` prints 78:
  "`## Head` does not name 8d0a1c3, which is the head this ran on. Evidence measured at another
  head describes another tree." -- and 86: `app_push: REFUSE: the body did not pass
  tools/pr/prepr.sh, so NOTHING was minted, pushed or posted`. This seat measured the same run
  live at 37 minutes (pid 19711, `open_pr.sh` -> `app_push.sh`, at "pinned graders"), so the
  duration is not only the relay's.
- Correction to the relay's order, measured: the log puts `REFUSE pr-body` at line 78 *before*
  `ok figures` / `ok carry` / `ok unpinned sites` at 82-85. The body check is step 7's first
  arm; the waste is everything before step 7 -- 1b's heavy slot and the scoped gate at steps
  2-6f -- not the body sub-checks.

Cost: reorder, not new code. The early arm calls the same lint (`## Head` needs only the body
and `git rev-parse HEAD`; it needs no diff, unlike the `## Approval` arm keyed on the path
list), so the cost is one extra invocation of an existing check before step 1b, and the step-7
call stays. Risk, as the relay states: a body that fails `## Head` today fails in the first
minute instead of the last -- which is the point.

Binding: no second parser (decision 0012) -- the early arm is the same check, and the step-7
call remains, because a head can move *during* the run (update_pr merges `main` before pushing);
the early refusal must print the same line the late one does; the check must run before step
1b's slot is taken, or the expensive part it exists to avoid is still spent; and the null
control is a matching body running every step exactly as today.

## P209: the claim driver refuses a merge it can safely union (V129)

Verdict: ACCEPT -> a carry of **R10-996-RUNNER-CLAIMS** (`resume.stage` `carries-open`;
`files` `tests/env_drift.py` and `tests/golden/claimed_drift.txt`).

Source: orch s7 relay P2, 2026-10-27; not yet in `proposals.md`.

Instances: a merge where both sides added claims and neither deleted one, refused as if the
claim lists conflicted.
- (1) #2876 was SKIPPED by the train on one unmerged file: the orchestrator's counts are base
  750, ours 770 (+4 `coord_*`), theirs 752 (+2 R10-SAV-COMFORT), no line deleted on either
  side. Cost: an opus fixer seat and a full re-review round. The counts are the orchestrator's
  and are not re-derived here; the ruling rests on the shape -- additions on both sides,
  deletions on neither.
- (2) The code carries its own recurrence: `tests/entities.py:22387` records "five branches and
  ten conflicts in the session that built this, and the hand resolution was identical every
  time", and `merge_claim_file`'s docstring says "every branch that merges main after another
  one merged conflicts there".
- (3) Measured correction to the relay's cost line: the test it proposes to add already exists,
  in the shape the change stops refusing. `tests/entities.py:22449-22456` pins
  `merge_claim_file(_CM_BASE, _CM_OURS_CLAIM, _CM_THEIRS_CLAIM) is None`, and those constants
  are a base with no claims, ours adding `everything_on`, theirs adding
  `valve_storage_small_tank` -- disjoint additions, not a deletion. So the change rewrites that
  pinned expectation (and the docstring's "Measured; `tests/entities.py` pins it") and adds the
  deletion shape as the refusing one, rather than only adding a test.

Cost: one comparison arm in `merge_claim_file` (the three maps are already parsed at
`tests/env_drift.py:1790-1792`), one deterministic order for the union (the file is rebuilt and
its byte-exact round trip is pinned), the test rewrite above, the docstring, and one sentence of
`dev/governance/rules/claim-files.md` -- "refuses ... when both sides rewrote the bare claim
list" -- which stops being true in the disjoint shape. That sentence changes what a seat must
do (it no longer hand-resolves this case), so the pull request carries a policy edit and needs
the owner's approving review before it merges.

Binding: union only when `ours >= base`, `theirs >= base` and the additions are disjoint; the
deletion shape keeps refusing, and its measured reason still holds (a union would reinstate a
claim a side deleted, unseen by the inherited-claims guard); the union's order must be
deterministic and preserve the stamp, header and `may-drift` lines the existing tests pin
(`tests/entities.py:22423-22445`); the retained refusal keeps the reason that still applies;
and the policy sentence moves in the same pull request, never after it.

## P210: the field-coverage step has no bound, so a blocked run reads as a long one (V130)

Verdict: DEFER -> what would change the answer is one healthy run to completion (wall and CPU)
plus what the zero-CPU instances wait on. The item is `tools/pr/prepr.sh`, `R10-PREPR-CAP`'s
file (`resume.stage` `done`, no carry; a carry there needs the reopen route).

Source: orch s7 relay P3, 2026-10-27; not yet in `proposals.md`.

Instances:
- (1) Three `field_coverage.mjs` instances alive and blocked, sampled twice 53 s apart:
  `ps -p 64440,66073,85913 -o etime,time` printed 09:15/09:11/08:46 at 0:00.81/0:00.76/0:00.76,
  then 10:08/10:04/09:39 at 0:00.83/0:00.79/0:00.78 -- about 0.02 s of CPU in 53 s. Their
  parents are `bash tools/pr/prepr.sh` (79792), a claims review harness (85801) and a
  `prepr.sh` under a worktree (87624).
- (2) One isolated run on main used 52.47 s user + 15.74 s system and was still going at
  `timeout 120` (rc 124). So the script also has a slow-but-working mode, and a bound cannot be
  read from that run. The orchestrator's measurement.
- (3) The step holds a heavy slot: three of four held, with a fourth job queued behind them.
  The orchestrator's measurement.
- (4) There is no bound and no recording to base one on. `tools/pr/prepr.sh:3246` (step 3f3;
  3f4 opens at 3253) runs `heavy_run /tmp/prepr-fc.$$ node .../field_coverage.mjs`, and
  `heavy_run()` (defined at 605) only TERMs the group when the parent dies -- it has no
  wall-clock arm. `git show origin/main:tests/closures.json | grep -n
  '"tools/policy/field_coverage.mjs":'` finds no `recorded` entry; line 1642 is the path inside
  a closure's file list, not a duration.

Cost: unknown, and that is the DEFER. The wrapper is a few lines in `prepr.sh` plus one
self-test arm, but the bound's *value* is the risky part: a bound below a healthy run's wall
time fails a legitimate push on the serial push lane, so choosing one now trades a rare hang
for false reds at an unmeasured rate.

Binding: the bound must sit above the healthy runtime's observed upper end, and the failure
must name the step and the bound (a bare `timeout` exit reads as a test failure); if the
blocked mode proves idle rather than slow, a CPU-idle watchdog is the cheaper mechanism,
because it cannot fire on a working run. What would change the answer: (a) one uninterrupted
healthy run with wall and CPU time; (b) what the zero-CPU instances wait on (open fd or
syscall); (c) whether the three live instances ever finish. With (a) and (b) measured, the arm
becomes costable and ACCEPT-able; today its cost cannot be stated.
