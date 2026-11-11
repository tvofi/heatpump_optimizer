# Proposal triage, session s14, batch 200 (P626)

Sources:
- Roster `handoff/audit-r10-roster` at `b679c2850b`, where the groups owning `review_packet.py`,
  `merge_train.py`, `bugclasses.json`, `fix-review.md` and `governance.yml` were read.
- origin/main `60413046e3`.
- The root-cause seat's RCA for R10-RCA-PUSHER-CENSUS-ESCAPE, sections 3-6, and its scratch probe
  and job-step JSON files, re-run by this seat.

## P626: R10-RCA-PUSHER-CENSUS-ESCAPE countermeasure C1, the introduced-red line

Verdict: ACCEPT, as a new group R10-INTRODUCED-REDS-BARRIER (M, fixer opus, reviewer opus).
The orchestrator ruled under the owner's mandate (policy scope) that C1 is accepted in principle
as the class barrier. This ruling checks the numbers, sizes the work and places it.

Source: triage queue line 304, 2026-11-11T13:36:53Z, orchestrator s14: RCA RESULT, rule first.

The ruling under the mandate keeps the 2026-11-07 ruling (234ff52c75, "only a required check's
red owes a ## Red checks answer") for reds inherited from main. It restores the backstop only for
an `instrument-self-tests` step that is red at the PR head and not red at its base. Such a red is a
finding of the PR, and the reviewer blocks on it.

Spot-checks, by this seat:
- **The demo reproduces.** The RCA's probe on the step conclusions of job 130479299736 (#3425
  head c93903f075) against job 130415622883 (main cbd23f1c8b) prints `introduced: 4` and exits
  1. The 4 steps are the sweep template render and the three pr_args census steps.
- **The null pair reproduces.** Job 130415622883 (cbd23f1c8b) against job 130402966157 (main
  f24d107bd7) prints `introduced: 0` and exits 0. Both are red on the push-only drift step alone,
  which the probe excludes.
- **The window is right.** 234ff52c75 is committed 2026-11-07T19:15:02Z. #3425 merged
  2026-11-11T11:13Z, which is 3.67 days later. #3361 merged 2026-11-10T04:34:59Z (8652aa65ce),
  inside the window. The 3 instances are #3361 once and #3425 twice, with two independent causes
  (c966df8730 and c6c04f21b5). The seat did not re-derive the 135-merge scan. The scan reads 2 of
  about 118 steps, so 3 is a lower bound, as the RCA says.

Cost/benefit: the defect costs about 6 h per occurrence (main red plus seat-hours) at about 0.6
per 17 h release cycle, so about 3.5 h per cycle. C1 costs 2 job-step REST reads, about 1 s, per
packet. The defect reddens main, which meets the owner's bar without a percentage. C2 (a census
arm in prepr) is the RCA's recorded fallback, but it covers one step only and is not a class
barrier. The RCA refuses C3, C4 and C5, and this ruling agrees: C4 conflicts with decision 0013's
`HPO_JOB_GRADES: nothing` boundary, and C5 costs 431 s or more per prepr.

Placement: existing groups first. No live group owns this seam, which is the head-vs-base reading
of a non-required job's step reds:
- R10-HOTFIX-NONREQUIRED-REDS and -2 owned it last. Both are `done`, so neither can receive a carry.
- R10-GATE-DEFER-BARRIER (not started, M, 7 carries) owns `review_packet.py`, `merge_train.py`
  and `bugclasses.json`, but for a different class: the gate's at-once deferral red. It waits on
  R10-TICK-RESIDUE, which is `carries-open`. A carry would put a barrier against main-red behind
  those 7 carries and grow the group to L.
- R10-REVIEW-DISPATCH-RESIDUE (in progress) owns `review_packet.py` and `fix-review.md` for
  reviewer dispatch and return, which is a different seam.

So the work is a new group. Overlap is admitted with GATE-DEFER-BARRIER, REVIEW-DISPATCH-RESIDUE,
GH-READ-RESIDUE-P3, PROCESS-SLIM (#3451) and RESTORE-BASE-SKEW (#3463), because each is a
distinct seam.

The group's items:
1. `review_packet.py` and `merge_train.py classify` list each `instrument-self-tests` step that is
   red at the head and not at the base as INTRODUCED. The push-only drift step is excluded.
   - The base is the latest concluded run at the PR's merge base. If there is no base run, every
     head red counts as introduced.
   - An unreadable job fails closed.
   - A step skipped by scoping is not counted.
   - Self-test arms cover all four cases.
2. Correct the comment above `instrument-self-tests` in `governance.yml`. It still says
   `pr-contract` makes the body answer a red there.
3. Add a `bugclasses.json` key for the class, recorded as barriered by item 1.
4. Add a matching sentence in `fix-review.md`: an introduced red is a block. Add a matching sentence
   in `defect-root-cause.md`: such a red is a finding of the PR, and an inherited red stays unowed.
   Regenerate `.claude/rules` and `.cursor/rules` by `rules_sync.mjs`.
5. Land the RCA document as `R10-RCA-PUSHER-CENSUS-ESCAPE.md` under `dev/audit/rca/`.

The PR is policy (items 4 and 2), and it merges on the mandate approval.

Acceptance:
- (a) The built check reports the 4 INTRODUCED steps and a nonzero exit for #3425 head c93903f075
  against its base.
- (b) The null pair cbd23f1c8b vs f24d107bd7 reports 0 and passes.
- (c) The check passes on a fixed head. That is R10-HOTFIX-PUSHER-CENSUS's merge on main, or its PR
  head against that PR's base if it has not merged by the handoff.
- (d) A mutation that drops the base subtraction turns (b) red.
