# Proposal triage, session s8, batch 87 (P324)

The rolling batch after batch 86 (#3033). Facts were read at origin/main `4822c8f9b`.

## P324: a mandated budget-raise approval goes stale on automatic merges; accept an ancestor approval

Verdict: REJECT. This covers both the proposal as filed and its narrowed train-side variant
(below), on cost/benefit. No roster op.
- **What was proposed.** `budget-raise-gate` and the train's raise check accept tvofi's approval on
  an ancestor head when `review_carry.py` prints CARRY and the raised values are byte-identical.
  That edits decision 0013's "APPROVED on the head SHA" wording.
- **Why the gate change is rejected.**
  - **It weakens an owner guarantee to save a re-post.** The gate exists so that only the owner, or
    an agent under a mandate in force, can approve a raise. Today an approval at the head is a
    single fact the gate reads from the API. The proposal would replace it with a judgement that
    the commits between are harmless.
  - **That judgement would run on code the PR can edit.** `review_carry.py` and
    `app_approve.sh --carry` live in `tools/audit/seat/` and `tools/pr/`. The gate's job restores
    only its own program from the base and runs it under `python3 -I` (0013). Moving the carry
    judgement into the required check means pinning a second program and its git history in that
    job, or trusting the head's copy.
  - **The at-head rule already costs nothing when the train moves the head.** The train re-posts
    the approval at the new head itself: `_carry_owner_approval` in
    `tools/audit/seat/merge_train.py`, behind `--approval-carry`. That flag is on by default
    (`train.sh` line 87, "on already"). It re-reads the mandate at the merge and refuses a delta
    that names a branch-own file. The approval stays "at the head", so 0013 needs no edit.
- **What #3006 actually hit.** It was a narrower gap than the proposal names. The carry accepts h0
  only among heads that this invocation's recarries moved through:
  `chain = [c for c in item.get("carried_chain") ...]`, with
  `no("this run's recarry did not move the head")` on an empty chain (`merge_train.py`
  lines 1653-1655).
  - #3006's approval sat on `958b4af8`. The first move, `ci: merge main` to `76d96ac7`, was not
    the train's. So the train's recarry to `9033a595` had a chain of `[76d96ac7]` only, which does
    not hold the approved commit.
  - The train therefore refused with the gate's own reason, "tvofi's approval is on 958b4af8,
    not this head".
- **Narrowed variant, also REJECTED on cost/benefit.** The narrowed fix would also accept an h0
  outside the chain when `app_approve.sh --carry <h0> <h>` prints CARRY (automatic main merges
  only), keeping every other condition.
  - **Benefit, measured, is small.** Raise-bearing merges since 2026-10-17: 7 of 51 merges that
    touched a `*_budgets.json` (`raises_between(<merge>^1, <merge>)`, budget_raise_gate's own
    reading). The orchestration logs hold one earlier "approval is on ..., not this head" refusal
    (#2368, round-10 session 3), plus #3006's two. That is about 3 refusals in two weeks, at about
    5 orchestrator minutes each.
  - **Cost is a fixer and review cycle**, an S change in `merge_train.py` with its fixtures and a
    mutant. It also widens a condition the owner set on 2026-10-12 ("the recarry of THIS
    invocation moved the head"), so it needs the owner's review or a mandate in force.
  - **Little payback left.** Round 10 closes 2026-11-01, so almost no payback lands this round.
  - **This is a marginal trade.**
- **Re-open trigger.** Re-open the narrowed variant, not the gate change, in a later round if the
  train logs a carry refusal "this run's recarry did not move the head" on a raise PR at three or
  more PRs in one round, which is the audit-class threshold. Its fixture is #3006's chain:
  - `958b4af8`, then `ci: merge main` `76d96ac7`, then the train's recarry `9033a595` carries.
  - Null, refused: a hand-resolved conflict between h0 and h.
  - Null, refused: a non-merge commit in h0..h.
  - One mutant: drop the CARRY test, and the conflict row lands.

Source: the orchestrator s8's message of 2026-10-31 (slip, #3006).

Instances:
- #3006 (2026-10-31): two re-approvals in one hour, heads 958b4af8, then 76d96ac7, then 9033a595.
- #2368 (round 10, session 3 train log): "approval is on ..., not this head".

Cost: as above. The filed form is a pinned-gate change plus a decision-0013 edit. The narrowed form
is S in `merge_train.py` and widens an owner condition.

Binding:
- The rule that a raise approval sits at the head is cheap where the train moves the head, because
  the train already re-posts it.
- The residue is about 5 minutes for each raise PR that a non-train merge moves, measured at about
  3 in two weeks.
- That does not clearly pay for weakening the owner's gate or widening the owner's carry
  condition at the end of the round.
