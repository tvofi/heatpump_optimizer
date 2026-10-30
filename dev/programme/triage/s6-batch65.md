# Proposal triage, session s7, batch 65 (P296)

The rolling batch (V182) after batch 64 (#2980, merge verdict at `3fbbb46f`, not yet merged).
Facts were read at origin/main `1148ee635`, on the round roster branch
`origin/handoff/audit-r10-roster`, and on the live bodies and comments of #2925 and #2962 (one
read each). P295 is the orchestrator's reserved number. This ruling keeps its number, P296.

## P296: a bad `Carry:` destination in an older verdict cannot be superseded

Verdict: ACCEPT option (a), narrowed, as one carry on R10-FLY-CARRY-DISPOSITION (the group that owns
`tools/audit/carry_audit.py`'s routing). Option (b) is REJECTED. Option (c) is REJECTED as the
class fix. For #2925 and #2962 now, see Binding. URGENT: two merge-verdicted PRs are parked on it,
and the orchestrator counts 4 carry parks this sweep.

Source: the orchestrator's message of 2026-10-30, P296.
- #2925 at `5682d74e`: review 6495961723, item `a3103224`, `Carry: R10-RCA-PREPR-HEAD-GRADERS`. That
  is an RCA record, not a roster group.
- #2962 at `9ce0179f`: review 6506038459, item `75f08830`, `Carry: #2959`. #2959 is merged and has
  no owner.
In both, a later marker routes the same item to a live group, and the train still parks the PR as
BAD-DEST.

Instances, reproduced. `carry_audit.audit(body, comments, load_dests())` was run on the live body
and comments of each PR, at `1148ee635`, with round roster `origin/handoff/audit-r10-roster`.
- **#2925.** Exactly one non-routed row: `a3103224 bad`, with the note
  "R10-RCA-PREPR-HEAD-GRADERS is not a group of the roster or of origin/handoff/audit-r10-roster".
  The same item's other destination, R10-FLY-CIPREDICT-RESTORING, is valid.
- **#2962.** Exactly one non-routed row: `75f08830 bad`, with the note "#2959 has no owner". Its
  other destination, R10-ORCH-REVIEW-PACKET, is valid.
- **The mechanism.** In `carry_audit.py`, `audit()` sets an item's destinations to its own markers
  plus every `(item <id>)` reference (`refs.get(r["id"])`, via `carry_refs`). It sets
  `status = "bad"` if any token fails `Dests.check`. Destinations only accumulate, so a valid
  re-route can never cure a bad token. The only cure today is editing the comment that holds the
  bad token.
- **Both PRs pass once the bad token is set aside.** Each has 0 non-routed rows when the
  orchestrator's patched comment is substituted (`comment-<id>.patched.md`). It is also 0 for each
  under a simulated rule that ignores a bad token on a row holding a valid destination.

Cost and benefit:
- **(a), narrowed: S.** About 15 lines in `carry_refs` / `audit`, plus self-test rows.
  `carry_audit.py` has no `policy_lint.mjs --budgets` row. It is a CODEOWNERS path, so the fix
  merges on tvofi's approving review, or under the mandate in force if the orchestrator rules it
  covers that review. Benefit: each instance stops costing a park plus a hand cure. That is 4 this
  sweep, per the orchestrator.
- **(b) REJECTED.** An approver-key edit of an App verdict comment makes it carry text its reviewer
  never wrote. The verdict ref `verdict/<pr>` is bus-signed and would then disagree with the
  comment. Decision 0011 gives verdict posting to the approver identity alone. A one-off use has
  the same defect, so it is rejected for the two PRs as well.
- **(c) REJECTED as the class fix.** Each instance costs a reviewer seat. "The newest verdict's
  items supersede" would silently drop an older verdict's findings that a newer reviewer did not
  restate, and that loses findings. It does not cure today's PRs either: the old comment still
  holds the bad token, and destinations accumulate across comments.

The carry:
1. **Grammar.** `Carry: <dest> (item <id>, supersedes <old>)`, in the body or in a verdict
   comment, retires `<old>` for item `<id>` only.
2. **It retires an invalid token only.** `<old>` is retired only if `Dests.check(<old>)` fails. A
   `supersedes` naming a valid destination is refused, naming the item, so it cannot hide a live
   routing.
3. **The item must still end valid.** It must keep at least one valid destination. A retired
   token prints as a NOTE (`<old> superseded by <dest> (item <id>)`) and is never silently
   dropped.
4. **No author test.** carry_audit cannot see who wrote a body line. Rule 2 removes the need for
   one: a line can only replace a destination that was already invalid with a valid one.
5. **Fixtures.** The #2925 pair (item `a3103224`, R10-RCA-PREPR-HEAD-GRADERS superseded by
   R10-FLY-CIPREDICT-RESTORING) and the #2962 pair (`75f08830`, #2959 superseded by
   R10-ORCH-REVIEW-PACKET) go from bad to routed.
6. **Null controls.**
   - The same body without `supersedes` stays bad, which is today's behaviour.
   - A `supersedes` naming a valid destination is refused.
   - A `supersedes` whose new destination is invalid stays bad.
   - A `supersedes` naming another item's id leaves this item bad.
7. **Mutation.**
   - Dropping the "old must be invalid" test lets the valid-supersede control pass.
   - Dropping the item-id scoping lets the other-item control pass.

Binding:
- **#2925 and #2962, now.** Do not wait for the carry. The replay above shows every finding item
  of both has a valid owner, and the single bad token on each is the stale one. Run the two
  through a train of their own without `--pre-flight`, under the orchestrator's ruling, as #2683
  was. Before adding them, check by hand what pre-flight would have checked: the merge verdict at
  the live head, the delivery row and the approval. Record each waiver in the ledger with the
  item id and the superseded token.
- **Each body, in the same pass.** Write the `supersedes` line for the item, so the body already
  carries the grammar this carry builds. Today it reads as one more `(item <id>)` route, which is
  harmless. That needs a body push only, with no new head and no re-review.
- **Dispatch.** The carry can be dispatched alone, ahead of R10-FLY-CARRY-DISPOSITION's larger
  carries. It touches the same function family as P293's carry (batch 64), so one S fixer can take
  both. The urgency is the coordinator's call: batch 65 holds this one ruling, and the carry
  cannot reach the roster until batch 65 is on main.
