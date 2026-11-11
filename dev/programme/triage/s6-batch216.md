# Proposal triage, session s14, batch 216

Sources: the orchestrator's message to the triage seat (s14, 2026-11-11, after the #3481 CARRY-MISSING
roster ops), ruled as P656. Line numbers are at origin/main 61afd4f2db. Roster read at
handoff/audit-r10-roster 028ebe9c5d.

## P656: an item id must survive its own landed annotation

Verdict: REJECT as duplicate of s6-batch183.md#P605 (CARRY-LANDED-OWN-TOPIC, R10-CARRY-AUDIT-P5 carry 4, accepted, not built); both proposed fixes REJECTed in favour of it.

Source: orchestrator message, 2026-11-11, instance #3481.

The proposal's cause is half right. The three body items of #3481 did get new ids (c7424eb8,
ccc86b13 and 70e463f9 became b4048305, 128b800e and c33b6f10) once each item gained a
`Carry N: landed at f4c4044aaa ... (items <id>)` suffix. carry_audit.py:290 hashes the whole item
text. But a changed id is already provided for. landed() (carry_audit.py:620-660) also counts an
item as landed when its group's carries hold the SOURCE, `#<pr>` or the handoff topic (P310: "an
id re-minted by a reword still lands by its source"). The relay's carry-fold arm landed carries 2,
3 and 4 as `From r10-advisor-steady-start, body item ...`, which is the topic.

The refusal comes from the caller. tools/audit/seat/bus.sh:236-237 runs `carry_audit.py landed
--body ... --pr "#$1"` with no `--topic`, so the topic-sourced carries never match.

Measured on #3481's live body (head branch fix/r10-advisor-steady-start), roster at origin/main:
- `landed --pr '#3481'`: `CARRY-LANDED: 3 missing` (the bus's refusal).
- `landed --pr '#3481' --topic r10-advisor-steady-start`: `CARRY-LANDED: 0 missing`.

This also answers the open s14-26 question of why `carry_audit landed` printed "0 missing". That
run passed `--topic`; the bus does not.

Prior instances: 66 distinct CARRY-MISSING lines across 19 refused dispatches in tick-loop.log,
cloud-relay.daemon.log, s13/dispatch-seat/mint3299.out and the s14 dispatch seat files. For each
item, the group's current carries show how it was later satisfied:
- 11 items (3 PRs) were already held by a topic-sourced carry before the refusal: #3481 (3 items),
  #3227 (5, R10-BODY-CONTRACT) and #3220 (3, R10-SAV-COMFORT). Each refusal was false, and the
  hand-landed `From #N` / `From PR N` copy duplicated a carry. That is 11 duplicate carries;
  R10-BODY-CONTRACT carries 10, 16 and 26 are one example.
- 15 items were landed afterwards from `#N`. Those refusals were true.
- 26 were never landed by text (R10-REVIEW-DISPATCH-RESIDUE 22 and others, re-routed or
  dismissed).
- #3448 (P605's own instance: 23 own-group lines) is the same missing `--topic`.
So 4 of 19 refused dispatches (21%) were false refusals from the missing `--topic`. That is over
20% on dispatch right-first-time.

Why the proposed fixes are not taken:
- (i) Hashing the text before the landed suffix covers only this one annotation shape. A reword
  still re-mints the id, which is the case P310's source rule was built for.
- (ii) Moving the landed note out of the item changes the body template (policy-adjacent), and it
  too leaves the reword case open.
Passing the topic is the one change that makes the existing source rule work for both.

Binding: duplicate. P605's carry (R10-CARRY-AUDIT-P5 idx 4) is the fix, exactly as written: read
.head.ref, map it with topic_grammar.py pr-topic, and pass --topic. To the orchestrator: the
measure above (4 of 19 refused dispatches, 11 duplicate carries, one L-group first review held
tonight) supports dispatching R10-CARRY-AUDIT-P5 (medium, not started) ahead of other medium
instrument groups. Until it is built, a CARRY-MISSING refusal should first be re-run with
`--topic <pr topic>`. If that run reports 0 missing, the refusal is false. Then deliver the
dispatch past it by the orchestrator's ruling, and append no copy.
