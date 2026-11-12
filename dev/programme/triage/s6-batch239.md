# Proposal triage, session s14, batch 239

Source: owner rulings (tvofi, 2026-11-12 about 07:50Z, 08:00Z and 08:10Z), recorded, not weighed
(P718, P719). Ruling recorded by triage s14-64.

Owner rulings, verbatim:
- ~07:50Z: "The "may not move the programme closure later" ruling should also apply to groups that
  are self-fed from the ongoing round 10"
- ~08:00Z: "Good. It should also apply to any new such self fed groups"
- ~08:10Z: "The contributur cycle mechanism should be built in full, asap"

## P718: the closure rule extends to self-fed groups, existing and new

Verdict: ACCEPT
Basis: the 07:50Z and 08:00Z rulings above, extending batch 238 P715 (outside work) to work round
10 feeds itself: residue parts, HOTFIX groups not fixing a red main, FLY and SEAT groups, and
instruments grown by triage ACCEPTs, both those already on the roster and any appended from now on.
Rule for the rest of round 10: such a group stays in round 10 only if the critical path or closeout
needs it, or it is small and finishes without moving the programme closure (plan-live finish at or
before about 2026-11-14T12:00Z); otherwise it is planned for round 11. Standing rule for this seat:
every ACCEPT that would append a group or a carry gets that closure test at ruling time, and the
entry says which; a round-11 outcome is recorded the P709 way (append-carry on
R10-ROUND-PLAYBOOK-FINAL citing the ACCEPT, and a new group at stage deferred). Existing groups:
the stage changes are the orchestrator's to order, from the self-fed table measured by s14-63; this
entry queues no roster op. Exempt: R10-OUTSIDE-CONTRIBUTOR-CYCLE (P719). Closure and R10-CATALOG-PR
by 2026-11-15 still outrank all non-critical work (P716). Severity high (closure date). Figure
against 20%: not applicable (owner ruling).

## P719: R10-OUTSIDE-CONTRIBUTOR-CYCLE is round 10, in full, top priority above the cap

Verdict: ACCEPT
Basis: the 08:10Z ruling above. The group (appended by P714, source outside) is round 10 by owner
order: its design and every build part run in round 10, no part deferred, exempt from P715 and
P718; it is dispatched at top priority above the open-PR cap. This supersedes the earlier note that
the build's round is decided at design approval. Plan check, one read of origin/main: replan.py
dispatch_tier returns TIER_TOP for roster_lib.is_outside (source "outside", set at 4721), and
roster_lib.dispatch_rank returns RANK_TOP for it, so the tier needs nothing more. The plan's own
cap exemption (scheduler pick with cap_exempt) keys on the computed critical path only; this group
has no after-edges and is not on it, so the plan models it as a top-tier peer of the critical path
inside the slot count, not above it. No roster field expresses "above the cap"; the cap that binds
dispatch is the orchestrator's open-PR cap, so above-the-cap is the orchestrator's dispatch act,
and no roster op is queued. The group's L size plus design is unmovable slot load in the date
analysis. Severity high (owner order). Figure against 20%: not applicable (owner ruling).
