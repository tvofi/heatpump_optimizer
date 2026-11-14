# Proposal triage, session s14, batch 242

Source: orchestrator order of 2026-11-12: the owner's study-review ruling Q1 (batch 218 P666) has no
implementing group on the plan. Ruling recorded by triage s14-64.

## P732: Q1 (ci-ratchet advisory on a push to main) to round 11, with its red trigger

Verdict: ACCEPT
Basis: batch 218 P666 (owner ruling tvofi 2026-11-11, "I agree with all the recommendations.":
`tests / ci-ratchet` becomes advisory on a push to main, built as a hotfix on its next red, else in
round 11). P666 carried it as CI-RATCHET-ADVISORY-ON-PUSH on R10-HOTFIX-GATE-REDISPATCH-LOOP
(0-based carry 0). That group's pull request #3473 merged on 2026-11-12T04:50:33Z without it:
tools/ci/gate.py:68 on origin/main still lists ci-ratchet in PUSH_ONLY. It is that group's one open
carry, so the group sits carries-open with nothing in flight. Closure test (P718): not needed by
the critical path or closeout, and P666 itself names round 11 unless main reddens. Destination: the
round-11 opening list on R10-ROUND-PLAYBOOK-FINAL with the trigger kept (built as a round-10 hotfix
only if `tests / ci-ratchet` reddens a push to main before closure). The carry is marked moved
R10-ROUND-PLAYBOOK-FINAL, so R10-HOTFIX-GATE-REDISPATCH-LOOP discharges. Severity medium. Figure
against 20%: not applicable (owner ruling).
