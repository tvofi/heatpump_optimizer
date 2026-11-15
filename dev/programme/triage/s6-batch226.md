# Proposal triage, session s14, batch 226

Source: triage queue line 318 (PRODUCT-RULING, #3452 body items 7052beca and 9ac8c410), answered
by the fable probe result handoff-body/r10-product-ruling-dhw-hard-max at d507c499a85c, and the
orchestrator's decision under the mandate (2026-11-12), ruled as P681. Line numbers are at
origin/main 2cfa3d7d69. Roster read at handoff/audit-r10-roster 923e8cf196.

## P681: dhw_hard_max_temp product rulings for R10-OUTSIDE-DISINFECTION-SETPOINT

Verdict: ACCEPT both rulings as the probe states them: "Ruling: (1) round-down (2) respect-and-surface".

Orchestrator decision, verbatim: ACCEPT both rulings as the probe states them — (1) a no-cycle
hot-water write never exceeds the charge limit (round down on the entity's step; the user-safety
ground is the scald risk of a silent, permanent round-up); (2) respect the ceiling and surface it,
as the probe's section (2) specifies. Outside-derived work: it is built in round 10, as part 2 of
R10-OUTSIDE-DISINFECTION-SETPOINT, never deferred.

Destination and severity: (1) is a carry on R10-OUTSIDE-DISINFECTION-SETPOINT (severity high,
stage in-progress, PR #3452 open), shipped as part 2 in its own pull request after #3452 merges.
(2) is already the brief of R10-DISINFECTION-STEP-NOTICE (M, high, after the parent), with
9ac8c410 moved there; nothing further is queued for it.

Figure against 20%: the bar does not apply; this is an outside-derived product ruling under the
mandate. Basis: 104 of 780 no-cycle census rows write above the charge limit `dhw_max_temp` at
main and at the group's head; null control 455 on-step rows, 0 over. The ceiling is the charge
limit, not `dhw_hard_max_temp`, which counts 64 of the 104 with the cycle enabled.
