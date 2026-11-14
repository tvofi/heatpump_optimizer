# Appendix E: the switch, not approved (R11-PRE-PARALLEL-PIPELINE)

The owner ruled "Day 1 plus shadow" on 2026-11-14. Moving main by promotion
from an integration branch is a decision he takes on the shadow's result.
This file holds what that design must contain if he takes it, as amended by
the design review; nothing in it is built by day 1 or by the shadow.

## Shape, as amended

- **Landing.** A pull request stays based on main. When GitHub's own read of it
  against main's rules is satisfied (`reviewDecision`, `mergeStateStatus`, the
  required set at the reviewed head) the train merges the reviewed sha onto
  the integration tip locally, with the merge drivers, under GitHub's merge
  subject grammar. The head is never moved.
- **Proof.** One push-judged proof of the tip at a time (day 1's proof input).
  A transient red is re-run once. A real red is searched over prefixes: every
  landing is a first-parent commit, so each prefix exists. The search runs on
  cloud seats where `SEATS.md`'s agreement measurement allows, else one FULL
  proof at a time. The green prefix is promoted after its own proof; the
  culprit is evicted and the branch rebuilt behind it.
- **Promotion.** Under the main-writer hold. It re-runs the WHOLE admission
  read for every landed entry (review state, required set, head equal to the
  landed sha), not the head comparison alone (R10), then moves main by the D1
  arm chosen.
- **I1, as it holds (R6).** Main moves by promotion to a proved sha, or by a
  writer that exists today: `stamp.py`, the ledger App's push, a direct hotfix
  merge under `merge_pr.sh`. Each of the latter forces a rebuild of the branch
  on the new main and restarts the proof. Record and dependabot pull requests
  land like any other change.
- **Priority.** A hotfix or outside pull request lands first in the next
  range; it does not cancel a proof in flight. Worst case to main: the rest of
  that proof plus one proof wall. The within-the-hour path is the direct merge.
- **A head that conflicts with an unpromoted landing (R10)** waits for that
  landing's promotion, then meets the conflict on main, where its fixer sees
  it. No one merges the integration tip into a head.
- **Successors (R4).** An `after` successor branches from its predecessor's
  REVIEWED head, never from the integration tip. Three possible starts, each
  with its figure in `COST.md`: at landing (S-i), after a seat's green gate at
  that landing (S-ig), at promotion (S-im). Starting on an unproved landing
  goes beyond every public design in `STUDY.md`; the shadow measures the red
  rate that prices it.
- **State.** The branch on origin is the state of record: each first-parent
  landing names its pull request and sha. The local state file is a cache; a
  host restart between landing and promotion rebuilds it from the branch (a4).
- **`remerge_main.sh` and `app_push.sh --recarry`** have no caller once
  landing runs the drivers; they retire with the switch (b1).

## D1: how main is moved. Three arms.

| | (a) the deploy key, ruleset as it is | (b) a promotion pull request merged by GitHub | (c) fast-forward with the ruleset split |
|---|---|---|---|
| ruleset change | none | none | `main-protect-checks` becomes two rulesets: the pull-request rule, bypassed by the promoting credential; the required-status rule, with no bypass for it |
| what GitHub still refuses at the push | nothing | everything, as today | a sha with no green `gate` |
| what only the instrument checks | pull-request association, review, code-owner review, the required set | nothing | pull-request association, review, code-owner review |
| main's first-parent line | one merge commit a change, as today | one merge commit a batch: the 14 files that enumerate "Merge pull request #" there see promotions, not changes | as (a) |
| promoted sha against proved sha | equal | differs | equal |
| owner reviews | as today, on each code-owned change | also on every promotion carrying a code-owned path (95 of the 215 changes touch one, the reviewer's count) | as today |
| `stamp.py` | unchanged | unchanged | the deploy-key actor carries no id, so two keys cannot be told apart: either the stamp first proves its commit on a ref (one proof wall a stamp, 11 a week in the window, and the 2 stamp reds of the 24 go) or promotion uses an App credential and the stamp keeps the key's bypass on both rulesets |
| probe owed | U2, U3, U4, U5 | U4 | U7 below, with U3, U4, U5 |

U7: on a throwaway branch under a split throwaway ruleset, a fast-forward
push by a credential that bypasses the pull-request rule and not the status
rule is refused for a sha with no green `gate` and admitted for one with it.
GitHub documents this for branch protection ("pushed directly to the
protected branch" after required checks pass) and documents that rules of
several rulesets on one branch are aggregated; it does not state it for a
ruleset. If U7 fails, (c) is (a).

If U5 fails (the review read does not reflect the code-owner rule), (a) and
(c) are cancelled: the instrument recomputing ownership would grade itself.
If U4 reads something other than the landing commit, the seven readers of the
merge commit derive it from main's first-parent line by subject, as
`stamp.py`'s notes rule does.

Under any arm the audit step on main's push run re-derives, from the
first-parent range a promotion added, that each commit is the landing of one
pull request GitHub reports approved; it is exempt from any push-run skip.

## The push-run skip

Not part of the switch's first build. `REVISE-1.md`'s R8 table lists six
push-only producers (two caches, the proof consumer, ci-ratchet, record,
delivery-status-publish) a skip would drop at every promoted sha; a skip must
keep each. Probe U6 and a change to `CLAUDE.md` rule 1 come first.

## Notes carried from the verdict

- A landing's message is a closing surface only on main; each rebuild
  re-pushes it and GitHub adds a cross-reference to the issues it names (f3).
- A head pushed between promotion's read and its push leaves the pull request
  open with its content on main: a self-test arm (f4).
- `prelude.py`'s proof ref and tests.yml's proof consumer are an existing
  proof notion; the proof input extends it, on the workflow side too (f6).
- A landing made before a stamp meets the new `claims-for` at the rebuild;
  eleven stamps a week make this the common case, not an edge (a4).
