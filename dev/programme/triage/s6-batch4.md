# Proposal triage, session s6, batch 4 (P54)

One proposal, S6-U of the s6 orchestrator's out-of-tree `proposals.md` (2026-10-24
~12:58Z), ruled as P54 from `dev/governance/roles/proposal-triage.md`. Numbering
continues after `s6-batch3.md` (P53). GitHub calls: 0.

A roster op citing an ACCEPT below resolves only once this file is on the
roster branch or origin/main (`roster_edit.py` reads the ruling from there).

## P54: the tick's owner-gated line counts groups a mandate already covers
Verdict: DEFER -> owned by R10-ORCH-ROSTER-SCHEMA (it owns `roster_lib.py` and the group schema); re-triage when `owner_gate` has a structured form
Source: s6 proposals.md item S6-U (tick.txt REPLAN line 172, "38 group(s) blocked on owner disposition").
Instances: 1 recurring line, on every tick board. The count is real: on
`origin/handoff/audit-r10-roster` `bbe44258e`, 38 groups with a non-empty
`owner_gate` and `resume.stage` other than `done` (a python3 filter over
`wave-r10-groups.json` at that ref). 35 name a 10-digit mandate id in the text
(19 `6175172275`, 9 `6319294694`, 7 `6329234399`); 3 name none
(R10-REPLAY-SCOPED, R10-MERGE-SUBJECT-HARDEN, R10-STRUCTURE-ALIAS). The
mechanism: `orchestrator_tick.py` lines 1804-1823 count every open group whose
`owner_gate` is truthy and set `flag=True`.
Cost: S -- about 15 lines in `orchestrator_tick.py` plus a self-test arm, as
the item says; but the classifier it needs is a parse of free text, which is
where the cost is not S (see Binding).
Binding: `owner_gate` is free prose, and the one group the item names as
needing the owner, R10-FLOW-MQ-PROBE, reads "owner decision after the probe;
the probe ruleset itself under 6175172275": it cites a mandate id and still
needs tvofi. A rule "a cited mandate in force means not owner-blocked" would
therefore silence exactly the item that is real, the null control the proposal
cannot pass (35 of 38 cite an id; the true owner items are among them). A rule
that parses the prose further (which words mean "covered") is a regex over
sentences like "the mandate 6175172275 covers it until 2026-10-28T18:14Z, after
which a fresh grant is needed", which is a lapse date, not a cover. The sound
form is a structured field (for example `owner_gate.covered_by`, set by the
roster op that records the grant), which is a roster-schema change owned by
`R10-ORCH-ROSTER-SCHEMA`, not a tick edit; the benefit today is one constant
line per tick that the orchestrator already reads past, and it is unmeasured
in time or tokens, so the bar ("clearly") is not met. What would change the
answer: a missed owner item traced to this line's constant noise, or the
schema group landing a structured gate.
