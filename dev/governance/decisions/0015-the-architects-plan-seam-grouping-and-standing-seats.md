# 0015 — The architect's plan, seam grouping, proposal triage and the standing seats

Status: recorded 2026-10-22 from the repository owner's rulings of 2026-10-21
(the architect/planner seat, adopted from the Lean flow study's pre-study,
`dev/programme/flow-study/architect-planner/STUDY.md` at commit
`30c57744ad8aab329d0054880fc9a3154262f204` on branch
`claude/dazzling-gauss-7l3u2b`) and of 2026-10-22 (proposal triage; the four
standing seats and their liveness check; critical-path groups exempt from every
cap). Lands as roster group R10-FLOW-ARCH-PLANNER, under the mandate in force
with scope all (#201 comment 6329234399).

## Context

Today's P3 is the orchestrator hand-editing `audit-verify`'s draft roster,
grouped by bug class under 0012's move 5 (revoked with the rest of 0012 by
0014, so nothing in force stated the grouping rule). The study measured, on
round 10's roster, file-order edges (one change merely touching another's
file) costing 12-13 h of the round before a mid-round re-chain removed them,
at a critical depth of 11 against 8; and the archscore history since the
score's introduction reading dS +74.6 yet **inadmissible**, four metrics having
regressed unseen. Its section 4 defines a target that cannot be met by gaming;
its section 6 the round-11 template.

## Decision

1. **P3 is the architect's plan** from round 11: `architect-planner.md` writes
   it, `plan-review.md` attacks it, the owner approves it. The orchestrator's
   P4 executes the approved plan and records each deviation against it
   (`orchestrator.md` section 2b).
2. **Move 5, amended**: findings are grouped **by owning seam**, the
   `bugclasses.json` class id kept as a tag. A class that spans seams is split
   into one group per seam, and the class's sweep becomes one of the plan's
   fitness functions. `audit-verify`'s class-grouped draft roster stays its
   output, as the architect's input, never dispatched as is.
3. **The programme-level architecture target**: a round's end-to-end
   `score.py --diff` at dS >= +22.7 (a 30% weighted fall over the 17 scored
   metrics at frozen weights: log2(1/0.7) x 44.18), admissible, read with the
   counters on, attributed per planned move, spread over at least three
   classes with no metric above 40%, and checked against holdouts the score
   does not contain. It binds the architect's plan, never a single seat; the
   conditions are `architect-planner.md`'s, and `tools/audit/archscore/ABOUT.md`
   reconciles it with "a review trigger, never a target a seat is rewarded for
   moving".
4. **Proposal triage** (tvofi, 2026-10-22): every process, tooling or
   instrument proposal passes `proposal-triage.md`'s cost/benefit gate before
   any implementation; rulings land under `dev/programme/triage/`, and
   `roster_edit.py` refuses proposal-sourced roster text citing no ACCEPT.
5. **Four standing seats** (tvofi, 2026-10-22): tick, merge,
   dispatch/relay/verdict and roster, each a tracked contract, kept alive by
   the sweep's standing-seat liveness step and `tools/audit/seat/pulse.py`.
6. **Critical-path groups start regardless of every cap** (tvofi, 2026-10-22,
   restated: "remember critical path groups starts regardless off the caps
   when ready"): WIP, drain-first, coordinator K/2 and seat cap alike, and go
   first in every queue (`orchestrator.md` section 5). Measured that day:
   R10-SCORES held ready behind the drain cap moved the projected closure from
   Wed 28 Oct 23:00Z to Fri 30 Oct 03:11Z.
7. **The round-11 template** in the plan of record: P1 <= 10 h, P2 <= 10 h,
   **P3 <= 8 h** (was 4: architect plan, plan review, owner approval),
   **P4 <= 56 h** (was 60, the 4 h returned by seam-first edges), P5 <= 6 h,
   buffer 10 h.

## Why the triage record is its own directory

A Delivery-status row is written per pull request at its merge; a ruling
precedes any pull request, and a REJECT or DEFER never yields one. A batch
file per triage pass under `dev/programme/triage/` is where a later seat and
`roster_edit.py` read it; it holds rulings, not state, so it is no second
handover.

## Consequences

- The study's limits stand: the move-effort estimate rests on three prototype
  reports, the -12 h on one roster, and the score's calibration bar was not
  met (ABOUT.md). Section 4's conditions are therefore not optional.
- R10-FLOW-AUDIT-PLAN lands the `audit-plan` workflow, the move ledger and the
  holdout check; until then the architect seat runs by hand on these
  contracts.
- The corpus-cap raise the seven contracts need is argued in the landing
  pull request's `## Raise justification`.
- `dev/governance/` is `@tvofi`'s in `.github/CODEOWNERS`: this record and the
  contracts merge on the owner's approving review, or under a mandate in force
  with scope all.
