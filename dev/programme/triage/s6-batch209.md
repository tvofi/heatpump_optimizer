# Proposal triage, session s14, batch 209 (P640)

Sources:
- Triage queue line 317, 2026-11-11T16:22:20Z, and `s14/sweep.md` lines 446 and 500-502 (the
  dispatch seat's FIRED lines).
- `git ls-remote origin 'refs/heads/handoff-wip/*' 'refs/heads/handoff-body/*'
  'refs/heads/handoff/*'`, read about 16:30Z.
- origin/main `tools/audit/seat/cloud_dispatch.py` :236, :321-330 and :363, and
  `tools/audit/seat/cloud_relay.sh` `carry_fold_arm` (:805).
- Roster `handoff/audit-r10-roster`: group R10-RELAY-NOBODY-STALL (triage
  s6-batch194.md#P617). Its stage is not-started, it has no carry yet, and its severity is medium.

## P640: a body-only body_push refusal is repaired in the same cloud seat

Verdict: ACCEPT part (a), as a carry on R10-RELAY-NOBODY-STALL. REJECT part (b), because that
group already owns it.

Source: triage queue line 317, PROPOSAL (orchestrator s14). Three cloud fixers ended at "body_push:
refused body kept at handoff-wip/<t>-body" with no handoff-body ref, each refused for a gap only in
the body, and each needed a continuation seat.

Instances:
- The body-only repair fires today (`grep -n 'body repair\|body-only repair' s14/sweep.md`):
  - :446, 15:50:30Z: r10-relay-arm-order #3465, block body-stale.
  - :500, 16:26:30Z: r10-hotfix-replay-class-cut, brief-carries: carry 1.
  - :501, 16:27:00Z: r10-relay-arm-order #3465, UNROUTED item ba6117cc.
  - :502, 16:27:30Z: r10-sav-valuation-residue #3442, brief-carries: carry 7-9.

  That is four sonnet continuation seats across three topics. Each kept body is on its remote ref
  (ls-remote: 4b172a6c2, dbbb07c98 and 42db754f1). Each fixer had already pushed its code head
  (bd93b5634, 9647bc111 and 611102f07), so the body was the only gap.
- Denominator: `grep -ciE 'FIRED.*fixer' s14/sweep.md` gives 82 fixer fires this session, so
  body-only repairs are 4 of 82 (4.9%). The proposal costs each at 30 to 60 min of
  critical-path wall-clock.
- What the fixer is told today (cloud_dispatch.py :321-330): only exit 4 (CARRY-LANDED) has an
  instruction, which is to push BLOCKED and stop. Every other body_push refusal kind has none, so
  the seat stops. Brief-carries and UNROUTED refusals name the body line to add, so a seat that
  holds the body can repair them itself. CARRY-LANDED needs a roster write, which a cloud seat
  may not make, so that kind stays a stop.
- Part (b) is already owned. Arm 1 of R10-RELAY-NOBODY-STALL (RELAY-NOBODY-OWED) owes any fire
  that moved a code ref but no handoff-body/<topic> within 3600 s. Arm 3 (REFUSAL-RECORD) has
  body_push write the refusal verbatim beside the kept body. Together they print the line the
  proposal asks for. A second arm keyed on handoff-wip/<t>-body would duplicate them in
  cloud_relay.sh, which three groups already edit.

The rule, run per instance:
- Part (a), measured on the proposal's measure (continuation seats per fixer handoff). The 4
  body-only repair seats go to 0, because each refusal named its fix in the seat that held the
  body. That is 4 of 82 fires today.
- The machinery bars do not apply: the group's severity is medium and it is a root-cause
  countermeasure group (proposal-triage.md "skip them").
- The group's arm 2 (STOP-TO-BLOCKED) already rewrites this exact prompt text, so the carry adds
  no second edit site.

Cost:
- Part (a): about two sentences in the fixer text cloud_dispatch.py renders, plus one assertion
  in the render self-test that arm 2 already adds. No new file, no new check, no CI time, no API
  calls.
- Part (b): a new relay arm, a self-test and a hot file, for a signal arms 1 and 3 already
  produce.

Binding:
- Part (a): a measured saving of four seats and 2 to 4 hours of critical path a day, at near-zero
  marginal cost inside an edit the group already makes.
- Part (b): duplicate machinery, rejected.

Destination: append-carry on R10-RELAY-NOBODY-STALL, with this text:

> BODY-REFUSAL-REPAIR (triage P640, extends arm 2). In the fixer text cloud_dispatch.py renders,
> a body_push.sh refusal of any kind other than CARRY-LANDED (exit 4) is repaired in the same
> seat. Examples are brief-carries ("carry N is not named in the body"), carry_audit UNROUTED and
> body-stale. The seat edits the body as the refusal line names and re-runs body_push.sh. It ends
> only when handoff-body/<topic> names its code tip, or when the refusal is CARRY-LANDED or one it
> cannot repair from the body. Only then does it push BLOCKED per arm 2. Demonstration: the
> render self-test asserts that the fixer text names the in-seat repair and keeps CARRY-LANDED as
> the stop. It fails on the base render and passes on the fix. Null control: a designer or
> reviewer render is unchanged. Instances: s14/sweep.md :446, :500-502 (four body-only
> continuation seats, 2026-11-11).

Bar re-check (2026-11-11, orchestrator's question; proposal-triage.md lines 9-19). A carry on an existing group is still added instrument work, so the same bar applies to it. No ratchet-budgets.md cap is touched: every change here is code under tools/ and moves no policy_budgets.json measure, so the 20% figure below is read on the proposal's own benefit measure.

Bar: severity medium (R10-RELAY-NOBODY-STALL's roster severity; the group is a root-cause countermeasure for R10-RCA-FIXER-NOBODY-STALL). Figure: 4 of 82 fixer launches, about 4.9%, under 20%. Accepted only as a severity-exempt repair: the fixer text has no branch for a non-CARRY-LANDED refusal, so the seat stalls, which is the stall the group counters. It is not accepted as over-20%; on the 20% bar alone it would be REJECTed.
