# Proposal triage, session s14, batch 153 (P564)

This batch rules `s7/triage-queue-s7.txt` line 247, which arrived after batch 152. The bar and the
denominators are batch 141's.

Sources: origin/main `63bcdcaad8` (line numbers); the round roster branch
`handoff/audit-r10-roster`; PR 3377 (head `fix/audit-r10-roster-pr` at `6d347c73a5`) and its body,
read with `gh pr view 3377 --json body`.

## P564: S14-ROSTER-LANDING-MOVING-TARGET

Verdict: ACCEPT narrowed (the first remedy). It repairs an observed wrong behaviour: the review
packet can never pass the round's roster landing PR while the programme runs. The second remedy, a
drain hold, is rejected.

Source: queue line 247 (2026-11-11T01:49:51Z, the dispatch seat, PR 3377).

Instances:
- **The refusal.** `review_packet.handoff_not_applied` (line 348) refuses a PR on `fix/<t>` or
  `fix/<t>-pr` unless the current tip of `handoff/<t>` is an ancestor of the head (line 355). The
  refusal is added at line 562. For PR 3377, `<t>` is `audit-r10-roster`, the round roster branch.
- **How fast the tip moves.** The commit times on `handoff/audit-r10-roster` since 00:00Z: 97
  commits, a median gap of 43 s, a p90 gap of 110 s, and 0 of 96 gaps longer than 600 s. Command:
  `git log --since=2026-11-11T00:00Z --format=%ct origin/handoff/audit-r10-roster`, then the gaps.
  - The branch is 961 commits ahead of main (`git rev-list --count
    origin/main..origin/handoff/audit-r10-roster`).
  - `update_pr` takes about 10 min (the source's figure), so the tip has always moved by
    dispatch.
  - A false premise would have looked like quiet windows longer than 600 s. There were none.
- **The head is a correct snapshot.** PR 3377's head contains `7696a3ba07`, which its body names as
  "the tip of `handoff/audit-r10-roster` at the snapshot". That sha is an ancestor of the current
  tip, now 9 commits ahead. Command: `git merge-base --is-ancestor` both ways, and `git rev-list
  --count`.
  - The body already states that "the branch keeps moving and a later landing takes the rest".
- **The cost.** The landing was owed for 57 sweeps (the source's figure). PR 3377 has been open
  since 2026-11-09T16:52Z.
- **No other consumer.** Only `review_packet.py` applies the ancestry rule.
  `merge_train.py:1833` is the verdict-carry check.

Cost: in `handoff_not_applied`, for the round's roster topic only (the branch `roster_lib.round_ref`
names), a head that does not contain the tip is accepted when two conditions hold:
- the head contains the snapshot sha that the body names as its code head;
- that sha is an ancestor of the current tip.

It prints an advisory: `roster snapshot <sha>, N commits behind handoff/<t>; a later landing takes
the rest`. Every other topic keeps today's rule.
- Self-test:
  - the 3377 shape (head contains the named snapshot, tip 9 commits ahead) renders with the
    advisory;
  - a roster landing whose named snapshot is not an ancestor of the tip, or is not in the head, is
    refused;
  - the null control: a fixer branch whose head lacks its handoff tip is refused as today (#2887's
    shape);
  - a mutant that drops the round-topic scope fails the null control.
- `review_packet.py` has no row in `tests/structure_budgets.json`.

Binding: the drain hold is rejected.
- It would stop every roster op, about 53 an hour at today's rate, for the update, the review and
  the dispatch.
- Seats that wait on a carry landing would wait with it.
- And the hold would have to outlive a seat that can die.

The snapshot rule costs one scoped branch in an existing check. One carry goes to
R10-REVIEW-DISPATCH-RESIDUE, which holds `review_packet.py`; it is `not-started`, so there is no
PART 2 prefix. Carry file: `b153-P564.txt`.
