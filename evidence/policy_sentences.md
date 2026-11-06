## Policy text changed (for the coordinator to surface to tvofi)

The full diff is ev/policy.diff, and the list below is ev/policy_sentences.md. In summary:
- CLAUDE.md:
  - the delivery-status row now reads "the record is the pull-request list and one #201 line per merge ... no per-PR row";
  - finding-propagation's "before the producing pull request merges" becomes "landed at the latest at the producing pull request's merge";
  - the `proposal-triage.md` row is removed;
  - fix-review's row loses "a head that moved under the review is a blocked verdict" and gains "blocks on code, tests and harness, paperwork is a note; a verdict carries while the PR's own diff is unchanged";
  - "the fix reviewer returns `blocked` on one the body left unanswered" becomes "an unanswered one is a reviewer's note resolved at merge (card C5)".
- fix-review.md:
  - adds "Block only on code, tests and harness (card C5) ... one on `custom_components/` blocks. `bus.sh post` refuses `merge` at a red (C8)";
  - `carry-missing` and `root-cause-*` become `Note:` lines;
  - removes the "posted only once the head's workflows all concluded ... (tvofi, 2026-10-08)" sentence;
  - the delivery-status exemption is removed;
  - step 12's carry is extended to "any later head whose own diff is unchanged (card C4)", and head-moved now applies only when the own diff moved.
- fixer.md: "Your PR does not merge until any finding that changes how a later stage must work is in that stage's own brief" becomes "Put any finding ... in that stage's own brief".
- orchestrator.md:
  - section 5: a proposal is "ruled directly, by the owner or by you ... no standing triage seat (card C6)";
  - section 9: the record is the postmerge #201 line and roster `resume`, with no per-PR row;
  - "bar its delivery row" is removed.
- standing-dispatch.md: the delivery-row check is removed, and "(cards C4, C8 refuse there)" is added.
- standing-roster.md: the proposal-triage citation becomes "An op naming a triage or proposal number cites its ruling".
- D11.md item 5: "goes to `proposal-triage.md`" becomes "goes to the orchestrator".
- defect-root-cause.md:
  - the enforcement block becomes a C5 note and a C8 no-merge-at-red;
  - `governance / delivery-status` is dropped from the main-graded pair;
  - "or a row it did not add" and "or drain the overdue rows" are removed.
- delivery-status-tracking.md: rewritten around #201 and the PR list. "same session or an immediate record PR" becomes "at that merge"; the status-word and record-autofix bullets are removed; a stale body becomes a note; and it adds "An owner's ask in a verdict or a body goes into the roster at the merge".
- finding-propagation.md: "before the PR that produced it merges" becomes "by the producing PR's merge (card C5)".
- policy_budgets.json: the two proposal-triage.md keys (36, 489) are removed.
- proposal-triage.md: deleted.

The body says `content approved by tvofi in chat 2026-11-05`.

