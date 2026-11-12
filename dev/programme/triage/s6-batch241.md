# Proposal triage, session s14, batch 241

Source: orchestrator order of 2026-11-12 (added to batch 240's queue ops): discharge the idle
R10-HOTFIX-RESTORE-BASE-SKEW as batch 238 P717 did R10-HOTFIX-REPLAY-CLASS-CUT, applying the
closure rule (batch 239 P718) to any carry not built. Ruling recorded by triage s14-64.

## P731: R10-HOTFIX-RESTORE-BASE-SKEW: four unbuilt carries to round 11, group discharges

Verdict: ACCEPT
Basis: the group is carries-open with no open pull request, handoff or fired fixer; its pull
request #3463 merged 2026-11-12 at 5cc6f6f2ef (mergedAt 2026-11-11T19:30:54Z), and the RCA's #3438
merged at ae5b6f535b. Its four carries are two seams, each recorded twice (the RCA body items
e41acc16 and 530feedf, and their bare copies, 0-based 2 and 3): the mutation-pins payload-base
refusal at tests.yml `mutation-pins`, and the census arm's per-run cost. Neither is built on
origin/main: no `_rbs_defects` exists anywhere under tests/, tools/ or .github/. Built: 0. Not
built: 4. Closure test (P718): self-fed, not in flight, not needed by the critical path or
closeout: round 11. Destination: the round-11 item on R10-ROUND-PLAYBOOK-FINAL; each carry marked
moved R10-ROUND-PLAYBOOK-FINAL (copies 2 and 3 by their exact text, which the items 0 and 1
contain), so the group discharges. Severity medium. Figure against 20%: not applicable.
