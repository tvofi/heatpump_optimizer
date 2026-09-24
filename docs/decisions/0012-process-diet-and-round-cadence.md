# 0012 — Process diet: a moratorium on new process, a rotation cadence, and D14's stop rule

Status: recorded 2026-09-24 from the round-8 convergence design and the
owner's inputs in the round-8 audit thread, including the end date confirmed
2026-09-24. Source: the design handed over 2026-09-23
(`/private/tmp/audit-7/r8prog/design-rotation-and-D14.md`, sections A, B and
D) and Tim's inputs recorded there. This record is item F6 of that design's
section F.

## Context

The round-8 design proposed five moves of a convergence strategy. The owner
adopted **moves 1 (rotating seat focus), 2 (real-day replay), 4 (process
diet) and 5 (fix by class)**. **Move 3 (feature freeze) was not adopted.**
Nothing before this record put the process-diet move, the audit-round
cadence it depends on, or D14's stop rule into the tree; each existed only in
the design document and the thread.

Two of the design's other items landed first and are cited here rather than
restated: `#1507` (F1, round-driver repairs to `prepare_baseline.sh` and
`finding.schema.json`) and `#1505` (F2, `audit-verify.js` moved to one
verifier per dimension with one common judge, and `verifier.md`'s panel-size
sentence). F3+F4 (rotation and the D14 dimension) are in flight as `#1510`;
F5 (the real-day replay export and sanitiser, move 2) is in flight as
`#1508`.

## Decision

### Adopted moves

- **Move 1 — rotating seat focus.** Per-dimension method steps get ids
  (`D<k>.M<n>`), tracked in a coverage ledger (`tools/audit/rotation.json`)
  that carries each round's seat assignment, depth and yield, and drives the
  next round's dispatch. Panel shape changes with it: one verifier per
  dimension, carrying both halves of `verifier.md`, and one common judge over
  every finding — landed in `#1505`.
- **Move 2 — real-day replay.** A nightly lane (`tests/replay.py`) replays a
  sanitised day of Tim's own Home Assistant recorder data through the real
  coordinator, checking invariants a synthetic matrix does not exercise
  (`#1499`'s shape: state/attribute disagreement). Gated nightly, not
  per-PR, until its runtime is measured. In flight as `#1508`.
- **Move 4 — process diet.** This record and the cadence and moratorium
  below.
- **Move 5 — fix by class.** Open audit issues are grouped and fixed by
  `bugclasses.json` class id, one PR per class, ordered by live
  high/critical instances first, then by classes with an existing detector
  (promotions), then the rest.

### Not adopted

**Move 3, feature freeze, was not adopted.** No moratorium on production
feature work follows from this record; only the process moratorium below
does.

### The process moratorium

**Until 2026-10-31** (the end date the owner confirmed on 2026-09-24), no new
policy file, lint class, or `.claude/rules/*` rule is added. The only
exceptions are what a landed D14 barrier requires to enforce a class it
closes, or what a critical/high `D11` finding requires. `policy_budgets.json`
caps may move down under this moratorium; they may not move up under it
(the design's own exception language governs whichever of the two triggers
above applies).

### Audit-round cadence

Per the design's section A.5 seat table: **`D11` and `D13` run every third
round; `D5` and `D6` alternate rounds.** The other dimensions' seat counts
are as the design states them and are not restated here — this record fixes
only the cadence for the four rounds that do not run every round, since that
cadence is what the moratorium and the stop rule below both depend on.

### One enforcement point

**Where a D14 barrier replaces a prose rule, the prose rule is deleted in the
same pull request.** The detector is the rule; a class with both a barrier
and a surviving prose restatement of it is not a smaller footprint, it is
two places for the same fact to drift apart, which is the failure this whole
move exists to stop.

### What stays

Unchanged by this record, named because the process diet is a subtraction and
each of these was weighed and kept: the identity model of decision 0011
(App-authored PRs, App-approved non-code-owned paths, `tvofi` verdicts —
`hpo-approver` verdicts since 0013), the
fix-review adversarial verdict, the scoped gate (`GATE_SCOPE=auto` against
measured closures, forced `full` on a push to `main`), and the golden-fixture
claim protocol (`claimed_drift.txt` / `card_claimed_drift.txt`). These guard
the product and cost little per merge; the diet targets new process, not
these.

### D14's stop rule

D14 (the recurring-bug-class dimension) does not stop at zero findings —
rounds 6-8 sit flat at roughly 15-20 production findings, so a zero-findings
stop would never trigger. Instead: **the round's D14 finds no `open` class
with a new instance, and the nightly replay (move 2) shows no new invariant
break, for two consecutive rounds, and there are 0 high/critical production
findings.** All three conditions, held across two consecutive rounds, are
required together; any one failing resets the count.

## Consequences

- A seat proposing a new policy file, lint class, or `.claude/rules/*` rule
  before 2026-10-31 must show which exception applies (a landed D14 barrier's
  requirement, or a critical/high D11 finding) or stop and ask, per this
  repository's fix-verify-file order and the owner-approval rule this same
  `docs/decisions/` directory is under.
- A pull request that lands a D14 barrier and leaves the prose rule it
  replaces in place is incomplete under this record, not merely untidy —
  the same PR deletes the prose.
- The cadence table is read alongside the design's full seat-count table
  (`/private/tmp/audit-7/r8prog/design-rotation-and-D14.md`, section A.5) for
  the dimensions this record does not restate; this record is the durable
  copy of only the two facts (D11/D13 thirds, D5/D6 alternation) that the
  moratorium and stop rule depend on.
- `docs/decisions/` is `@tvofi`'s in `.github/CODEOWNERS`; this record is
  policy and needs the owner's approving review before it merges.

## Approval

Awaiting the owner's approving review.
