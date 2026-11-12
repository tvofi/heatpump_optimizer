# Proposal triage, session s14, batch 237

Source: two outside items the orchestrator put first (outside requests go before internal ones).
Carry indices are 0-based at roster f13e2f9eb0. Ruling recorded by triage s14-44.

## P712: outside comment on #3398 (combi store field data, docs-only suggestion)

Verdict: ACCEPT
Source: contributor comment 6783357148 on #3398 (R10-COMBI-TANK PR B, merged), 2026-11-11T00:36Z,
by the reporter of #3225. Field data from a 600 l single-shell combi store with no middle probe
(863 five-minute samples, 8-11 Nov): top-bottom difference median 24.8 K, at least 20 K in 91% of
samples; a top-only probe overstates stored heat by about 9 kWh. The ask is docs only, no feature:
for a tall store without a middle well, say the buffer temperature entity can be a template
sensor averaging a top and a bottom probe.
Checked on origin/main: docs/how-it-works.md covers a stratified top probe only for the wood
tank; no doc gives the combi or buffer user the averaging advice.
Destination and severity: one carry on R10-USER-DOCS-VERIFY (not-started; it owns
docs/configuration.md and docs/setup.md), and #3398 wired to that group so the outside intake
has an owner. Normal. Figure against 20%: not applicable (docs request, measured by the
contributor). The reply to the contributor is the orchestrator's.

## P713: one owner for R10-OUTSIDE-DISINFECTION-SETPOINT carry 0 (7052beca)

Verdict: ACCEPT
Carry 0 (#3452 body item 7052beca): the no-cycle write rounds an off-step everyday set-point to
the nearest step and can exceed dhw_hard_max_temp, 104 of 780 census rows. Carry 2 of the same
group is its part 2, ruled by s6-batch226 P681: round down, so a no-cycle hot-water write never
exceeds the charge limit, in pump_arbiter.py and setpoint_check.py, which that group owns.
R10-DISINFECTION-STEP-NOTICE took carry 1 (9ac8c410), the disinfection-cycle credit shortfall
in legionella.py; it does not touch the everyday write and does not own carry 0.
Ruling: the group's own part 2 owns it. Carry 0 is marked dismissed as superseded by carry 2,
which states the build; the work stays open through carry 2, so the group keeps one open carry
for this defect and one owner.
