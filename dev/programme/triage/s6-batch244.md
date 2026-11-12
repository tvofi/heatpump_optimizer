# Proposal triage, session s14, batch 244

Source: orchestrator order of 2026-11-12 on the owner's ruling of about 08:20Z and analyst s14-68's
study reconciliation (s14-68/study-reconciliation.md, section 4), whose what-ifs were each measured
as not moving the programme closure. Ruling recorded by triage s14-67.

## P734: study decisions that were dropped are built in round 10 when they do not move closure

Verdict: ACCEPT
Basis: owner ruling (tvofi 2026-11-12 about 08:20Z, verbatim "I want it now if it does not move
closure. That applies for any other study decisions that might have been dropped"), given on the
study's instrument/production grading split. It supersedes P732 (Q1, ci-ratchet advisory on a push,
to round 11) and P733 (R11-PROTECTION-CENSUS to round 11): neither one's queued roster op landed
(both were pulled before the drain reached them), so the Q1 carry on
R10-HOTFIX-GATE-REDISPATCH-LOOP stays unmarked and no carry cites P732 or P733. The closure test
(P718) still applies to each item: the analyst measured every what-if below at no move.
Destination: P735-P738. Severity medium. Figure against 20%: not applicable (owner ruling).

## P735: R10-GATE-PUSH-RATCHET (Q1 with B2)

Verdict: ACCEPT
Basis: P734; study review Q1 (batch 218 P666) and the review plan's B2. New group, size S, sonnet
fixer and opus reviewer. Q1: the `ci-ratchet` job in .github/workflows/tests.yml stops failing the
push gate; tools/ci/gate.py drops ci-ratchet from its push-only set, with its self-test, the
tools/release/stamp.py docstring and any pin in tests/entities.py. B2: on a push, gate.py prints one
report-only machinery summary line; no exit code changes. tools/ci/gate.py is shared with
R10-GATE-DEFER-BARRIER (critical path) on a different seam: this group merges before the barrier's
next handoff, or the barrier merges main. tests.yml and stamp.py are code-owned. The P666 carry
CI-RATCHET-ADVISORY-ON-PUSH on R10-HOTFIX-GATE-REDISPATCH-LOOP is marked moved to this group, which
discharges the hotfix group; BUILD-ON-NEXT-RED no longer applies. Closure: measured, no move.
Severity medium. Figure against 20%: not applicable (owner ruling).

## P736: R10-MACH-SCORECARD (the P668 scorecard as a beat row)

Verdict: ACCEPT
Basis: P734; study review Q3 (batch 218 P668), "scorecard recorded daily from now". P668 carried
the landing on R10-TICK-RESIDUE-P3 (carry SCORECARD-LANDS-AS-BEAT-ROW), which is deferred, so the
daily scorecard was dropped. New group, size S, sonnet fixer and opus reviewer, holding that
carry's text; the carry there is marked moved to this group. R10-TICK-RESIDUE-P3 stays deferred.
Its files (beat_jobs.py, beatd.jobs.json) are not barrier files. Closure: measured, no move.
Severity medium. Figure against 20%: not applicable (a measurement; owner ruling).

## P737: R10-PROTECTION-CENSUS (read-only study)

Verdict: ACCEPT
Basis: P734; the review plan's R11-PROTECTION-CENSUS, brought into round 10. New group, size S,
read-only study, sonnet and opus by the roster rule. One row per red check per production head of
round 10, classed real catch, grader skew or infrastructure, with a count of product reds caused by
a grader's version. Its result feeds B1, a product-only required set: no B1 group is created now.
If the census supports it, B1 is ordered for round 10 under P734; B1's known risk is that
line-citation reds move to main's push gate. Closure: measured, no move. Severity medium. Figure
against 20%: not applicable (a measurement).

## P738: A1 and A2 stay in round 10

Verdict: ACCEPT
Basis: P734; the review plan's A1 (MAIN-CANCEL-BOUNDED, R10-CI-PRIORITY-PAUSE carry 7, P658) and
A2 (TRAIN-WAIT-CAP-OUTAGE, R10-TRAIN-RESIDUE-P2 carry 20, P659) were queued as moved to round 11
under the w4m closure trim (batch 240). Neither mark landed: both lines were pulled from the
queue, so both carries stay unmarked on their groups for round 10. The analyst measured both at no
closure move. Severity medium. Figure against 20%: not applicable (owner ruling).
