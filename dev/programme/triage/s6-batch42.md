# Proposal triage, session s7, batch 42 (P216)

One entry: V129, written by the orchestrator s7 at 2026-10-27T20:40Z and quoted below as it stands.
Facts read at origin/main `a0e7664ea`; roster at `origin/handoff/audit-r10-roster` `9aed78e0e`
(212 groups).

## P216: an agent message that contradicts a contract must not enter a seat's record as direction (V129)

Verdict: ACCEPT -> a carry of **R10-ROUND-PLAYBOOK** (`resume.stage` `not-started`, so the op is a
plain append; it owns `CLAUDE.md` and `dev/audit/README.md`, and its brief is the playbook a fresh
orchestrator and its seats read from the tree alone). The rule is carried as written; the scope is
**any** agent message, not the orchestrator's alone.

Source: `proposals.md` V129 (orchestrator s7, 2026-10-27T20:40Z).

Instances: one, and it is this seat's own record.
- (1) At 20:20Z the orchestrator told this seat that "the two append-carry ops are yours to re-run",
  which contradicts `dev/governance/roles/proposal-triage.md` ("the seat does not implement, edit the
  roster, or merge") and the owner's standing rule that roster operations go to the standing roster
  seat's queue. This seat wrote it into `triage-STATE.md` as "main's direction, superseding" its
  earlier reading -- the record then asserted a lane change that never happened. It was caught only
  because the policy corpus was re-read after a compaction before the next merge; the record alone
  would have carried the wrong lane to the next seat, and the next seat would have run
  `roster_edit.py` itself, which is the write V128/P215 exists to refuse.
- (2) The class has no second recorded instance; it is carried on one measurement plus the harm's
  bound, and it is stated as such rather than inflated.

Distinct from P215, and the ruling keeps them separate: P215 guards the **caller** at the instrument
-- a structural roster op from a direct caller is refused. P216 governs the **receiver's record** --
what a seat writes when a peer's message contradicts a rule it holds. The pair is the two halves of
the same failure: a seat that obeyed P216 would never have written "the lane changed", and a seat
that wrote it anyway would have been refused by P215 at the write.

Cost: one paragraph in `CLAUDE.md` beside the other rules that bind every seat -- no code, no
runtime, no new instrument, no check to keep green. The paragraph states the marker
(`pending owner confirmation`), the requirement to quote the rule the instruction would change, and
the two prohibitions (do not act on the superseding half; do not write it as direction) until the
owner or the contract moves. Benefit: the measured instance above, and the harm it bounds -- a
later seat following a lane that was never changed, at the cost of a write the lane forbids.

Not carried, and why -- the mechanisation the proposal does **not** ask for: a text predicate in
`tools/audit/seat/state_docs.py` that refuses a state file containing "direction" or "superseding".
It would fire on any state file that quotes a rule or records a genuine lane change with the owner's
approval, and the cost of a false refusal is paid at every state push. The null control for the
carried rule is a state file that quotes `CLAUDE.md` while changing nothing, which must pass; a
predicate cannot tell that file from the one that failed. The rule is prose because the distinction
is semantic, and the enforcement is the reader the rule exists for.

Binding: the rule enters `CLAUDE.md` as policy, so the pull request that carries it merges only on
tvofi's approving review at its head (`CLAUDE.md`, "The owner approves a change to any of it before
merging"), and the carry must say so in its own body; the wording is the proposal's, with "another
agent" as the subject, so a fixer relaying a ruling is bound as the orchestrator is; the marker
phrase is fixed (`pending owner confirmation`) and the record quotes the rule it would change, so a
later reader can resolve the contradiction without the conversation; and a genuine lane change is
recorded the same way, then unblocked by the owner's or the contract's move -- the marker is not a
permanent veto, it is a record that the question is open.
