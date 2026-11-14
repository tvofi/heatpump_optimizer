# Proposal triage, session s14, batch 195 (P619)

Sources:
- origin/main `ee64358be7`. Every line number below is at that commit.
- `handoff/audit-r10-roster` at `f65729f2da` (measured) and `329c996e8e` (re-run).

## P619: CARRY-EXACT-MATCH

Verdict: ACCEPT narrowed, as a new group R10-ROSTER-CARRY-EXACT-MATCH (S, instrument, severity
low, sonnet fixer and reviewer). Only the exact-equality preference in `_carry_index` is built.
The alternative of filtering marked carries out of the hits is rejected.

Source: triage queue line 297, 2026-11-11T12:42:27Z, the s14 roster-repair seat: `mark-carry
--match` refuses as ambiguous when the match equals one carry exactly and is also a substring of
another (R10-TRAIN-RESIDUE carries 11 and 12 inside the dismissed duplicates 7 and 8), and the
queue refuses index keys, so the queue path cannot mark such a carry; worked around by a direct
index write.

Instances:
- **The mechanism, read in code.** `_carry_index` (`tools/audit/seat/roster_edit.py:550`) collects
  every carry containing the match (`:557`) and refuses two or more hits (`:562`). Both
  `op_drop_carry` (`:540`) and `op_mark_carry` (`:575`) call it. `replay_unsafe`
  (`tools/audit/seat/roster_queue.py:186`) refuses `mark-carry` and `drop-carry` without `--match`
  in a queue, by design (R10-RCA-ROSTER-DRAIN-REPLAY: 18 carries dropped). So a pending carry whose
  whole text sits inside a sibling cannot be named through the queue by any match text: every
  substring of it is also a substring of the sibling.
- **The proposer's instance, verified.** At `f65729f2da`, R10-TRAIN-RESIDUE carries 7 and 8 are
  marked `dismissed` ("duplicate of carry 11/12 kept bare; P548 roster_sync re-append") and each
  contains the bare text of carry 11 or 12. Carry 11 is marked implemented by the hand writes
  `f65729f2da` and `f6032a663e` (2026-11-11T12:43Z and 12:45Z); carry 12 is still pending.
- **Exposure on the live roster.** The harness `s14-18/sim619.py` (seat scratch; run from
  `tools/audit/seat` with the roster JSON) asks, for every pending carry, whether `--match <its full
  text>` resolves to that carry. At `f65729f2da`: 778 pending carries; 35 sit inside a sibling, in
  15 groups. 25 of the 35 are inside a marked sibling (the re-append shape) and 10 inside a pending
  one.

  | rule | null (743 not in a pair) | in-pair (35) | wrong entry |
  |---|---|---|---|
  | current substring rule | 743 | 0 | 0 |
  | exact-equality preference | 743 | 35 | 0 |
  | unmarked-only filter | 743 | 25 | 0 |

  At `329c996e8e` (before carry 11 was marked) the same harness reads 743 null and 36 in-pair, 0
  resolved under the current rule.
- **Null control.** All 743 pending carries that sit inside no sibling resolve identically under
  all three rules, and no rule resolves any carry to a wrong entry. No two carries are byte-identical,
  so the exact rule never meets a tie on today's roster.
- **The bar.** For the class this repairs, the queue path's right-first-time goes from 0 of 35 to
  35 of 35. Over all 778 pending carries it goes from 743 (95.5%) to 778 (100%). The proposal's
  value is the first figure, and it is a repair of non-production machinery at severity low, so
  the machinery rule's bar is met by the measured gain on the ops it touches. The second figure is
  why it is ruled S and low, not medium.
- **Frequency, measured honestly.** A search of the local drain and seat logs for the
  "is ambiguous in" refusal finds no retained line: the drain overwrites its job file per pass. The
  one recorded instance is the proposer's. The exposure is structural, though: the roster_sync
  re-append writes this shape every time it keeps a bare carry beside its dismissed duplicate, and 13
  of the 35 sit in one group (R10-ROUND-PLAYBOOK-FINAL).
- **Why not the unmarked filter.** It resolves 25 of the 35, misses the 10 pending-inside-pending
  pairs, and changes which entry an existing substring names. The exact rule changes nothing that
  resolves today.

Cost:
- About 4 lines in `_carry_index` and one self-test with its null arm, in
  `tools/audit/seat/roster_edit.py` (3,055 lines). That file has no row in
  `tests/structure_budgets.json` or any other `*_budgets.json`.
- One S sonnet fixer and a sonnet review, about one session each. No new file, check or CI lane.

Binding: the benefit is the removal of the one case that forces a hand index write past the
queue's replay guard, at 0 of 35 to 35 of 35 on that class with a flat null. The binding cost is
the S group itself, which is why it carries severity low and no design step.
