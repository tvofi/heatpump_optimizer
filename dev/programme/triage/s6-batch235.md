# Proposal triage, session s14, batch 235

Source: the owner's answer to batch 234's P708, put to tvofi by the orchestrator. Carry indices are
0-based on group R10-STANDING-CONTRACTS-P2 at the roster's current head; the quoted carry texts are
taken from the roster by jq, unparaphrased. Ruling recorded by triage s14-43.

## P709: plan the merge-seat and dispatch-seat retirement for round 11 (owner ruling on P708)

Verdict: ACCEPT
Scope: R10-STANDING-CONTRACTS-P2 carries 9, 12, 13 and 14, dismissed for round 10 by P708.
Owner ruling (tvofi, in person, 2026-11-12 about 06:55Z), verbatim: "Plan them for round 11".
Supersedes in P708: the refusal for round 10 stands (the merge and dispatch seats stay standing
seats for this round), but it is no longer a bare refusal. P708's reason is to be read as
"planned for round 11 by owner ruling 2026-11-12, see P709", and the work enters round 11's
opening plan as one intake entry covering the four carries below.
Evidence: the measured load from P708, since session s14 began (2026-11-11T01:02Z): 48 merges to
main and 46 reviewer fires in the session. tools/audit/seat/beatd.jobs.json has no merge, train or
reviewer-dispatch row.
Destination and severity: one carry on R10-ROUND-PLAYBOOK-FINAL (not-started), normal. That group
writes the "Round 11's opening plan carries" list in dev/audit/README.md, and it already holds the
earlier owner round-11 intake ruling (batch 218 P668, R11-INTAKE-SCORECARD-PARAGRAPHS), so this
uses the same destination and form. Figure against 20%: not argued here; the owner ordered the
planning, and round 11's P3 sizes it against the bar. Size: L, design first under decision 0014
(designer and design review before a fixer).
Precondition, common to all four, stated by the carries themselves: the replacement beat job is
live and has run one real cycle beside the seat (for the merge seat, one real pitch built and
merged by the job with the merge seat watching and agreeing) before the seat is stopped; the work
moves to a daemon or beat job, never into the orchestrator's turns.

Carry 9 (merge seat into a pitch job; owner-ordered), its original text:

> tvofi 2026-10-24 card 1 (owner accepted; CARDS.json (prestudy-mech, r10s6 scratch, not in the tree)): when this group lands, the standing merge seat retires: the queue builder and the train run as a daemon or beat job (train.sh and merge_train.py), their per-pitch outcome goes to the digest, and no pitch is assembled in the orchestrator's turn. Edit dev/governance/roles/standing-merge.md in this group or in R10-ORCH-BEATD's contract edit, whichever merges later, not both. Binding constraint (owner, tvofi 2026-10-24, verbatim): 'make sure the retirement of the standing seats dont cause you to run things inline'. A seat's work moves to a daemon or beat job, never into the orchestrator's turns, and the seat stays until its replacement job is live and verified. Acceptance: one real pitch is built and merged by the job, with the merge seat watching and agreeing; only then is the seat stopped.

Carry 12 (dispatch half of standing-dispatch.md into a beat job; owner-ordered), its original text:

> Orchestrator ruling 2026-10-24 (tvofi card 1): the dispatch half of standing-dispatch.md (open_pr and update_pr, bus dispatch, pool briefs and verdict confirm) becomes a beat job owned by this group's registry. It never moves into the orchestrator's turns. The standing dispatch seat stays until that job has run beside it for one full cycle.

Carry 13 (the dispatch beat job owned by the registry), its original text:

> From R10-ORCH-DISPATCH-REG (handoff de66f00b): **The dispatch half of standing-dispatch.md becomes a beat job owned by this registry.** Not built here: the beat and its job table are R10-ORCH-BEATD's (concern B), which is after this group. What it needs from here exists: one writer (`bus.sh dispatch`), a registry with time and model, a reopen on a failed publish. The standing dispatch seat stays until the job has run beside it for one full cycle.

Carry 14 (the dispatch beat job and its control), its original text:

> **R10-ORCH-BEATD: carry [5], the dispatch beat job.** It calls `bus.sh dispatch` (or `dispatch_group`), never a second writer of the registry or of the `reviewer-fire` close; the standing dispatch seat stays until the job has run beside it for one full cycle. Control: one beat pass over a handoff with no live dispatch leaves one registry line and one `close reviewer-fire` in `events.tsv`, and a second pass adds neither. Carry: R10-ORCH-BEATD

Control: the four carries keep their P708 marks; the round-11 intake entry is the one live record
of the work, and the R10-ROUND-PLAYBOOK-FINAL fixer writes it into the README's round-11 list.
Re-mark: roster_edit.py mark-carry refuses a carry that is already marked and has no re-mark op,
so the four marks keep P708's reason text; this entry is their supersession of record.
