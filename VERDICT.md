Fix review: blocked 4a276b6ac22e5543acf0351ba32464b3ee081e36 claim-false: P216's heading and the authored commit subject cite V136, which proposals.md does not contain (the entry is V129); the PR body's mutation proof cites `ruling_verdict` at 456 and `triage_refusal` at 464, which are 455 and 466.
bus-nonce: 90602aa3a83e9d593d64b3f3bc454260

## Blocking: false citations

- **`V136` is not a proposal.** `proposals.md` holds 121 entries and ends at V131; `grep -c V136` = 0. The entry's heading reads `## P216: ... (V136)` while its own `Source:` line reads `V129`, and the authored commit subject reads `rule V129 as P216/V136`. A later reader resolving the ruling against its stated source finds nothing. Correct the heading to `(V129)`; the authored commit `1c6731b` is not on main and can carry the same correction.
  Carry: dismissed: corrected in this record pull request before merge; the ruling's content routes to R10-ROUND-PLAYBOOK unchanged.
- **The PR body's mutation proof cites the wrong lines.** It says `ruling_verdict` at 456 and `triage_refusal` at 464. At the head, `ruling_verdict` is at `tools/audit/seat/roster_edit.py:455` and `triage_refusal` at `:466`; line 456 is the first docstring line and 464 is blank. `roster_edit.py` is absent from the diff, so base and head agree. Re-derive the two line numbers.
  Carry: dismissed: corrected in this record pull request before merge.

## Verified (non-blocking)

- **Triage gate moves on every arm.** Reviewer-built harness on `roster_edit.triage_refusal` (`ev/triage_gate_harness.py`, output `ev/triage_gate.out`): the committed P216 reads ACCEPT; the ACCEPT citation resolves; DEFER, REJECT, a renamed heading, an absent entry, a missing batch, and an uncited proposal are all refused; a plain carry lands. `RESULT PASS` x9, 0 FAIL.
  Carry: dismissed: verified, no action.
- **Destination holds.** At `origin/handoff/audit-r10-roster` `9aed78e0e` (212 groups), `R10-ROUND-PLAYBOOK` exists with `resume.stage: not-started`, files `CLAUDE.md` and `dev/audit/README.md`, 7 carries. `R10-BRIEFS-FOLD` is done, carries 20, and also lists `CLAUDE.md`; `R10-RCA-ORCH-CONTINUITY` lists `sweep_template.md`, not `CLAUDE.md`. The destination and the pre-emption in the body are accurate.
  Carry: R10-ROUND-PLAYBOOK
- **Scope and narrowing hold.** V129's title says "orchestrator message", but its Candidate says "another agent", so the ruling's "any agent message" is the proposal's own subject. The declined predicate's argument holds: the carried rule's own text contains "direction" and "superseding", so a state file quoting it would trip the substring test, and the named null control cannot pass.
  Carry: R10-ROUND-PLAYBOOK
- **Instance corroborated.** `triage-STATE.md:13` records the correction: "this seat QUEUES the two append-carry ops and runs nothing", against main's "the ops are yours to re-run". P215 (batch 41 at `handoff/triage-s6-batch41` `adf011c8f`) includes `append-carry` in its structural set, so "would have been refused at the write" holds; note P215 resolves on that branch, not origin/main.
  Carry: dismissed: verified, no action.
- **Record discipline.** `git diff --name-status origin/main...HEAD` is exactly `dev/programme/triage/s6-batch42.md` and the one-line `**open**` row; `git merge-tree --write-tree origin/main HEAD` exits 0; `carry_audit.py check --body` reads 0 unrouted; the roles contract is unchanged since the merge base; no concluded red check at the head (several checks still in progress).
  Carry: dismissed: verified, no action.

## Notes

- The ruling's quote of the role contract is a paraphrase in quotation marks: `proposal-triage.md` reads "**You do not** implement, edit the roster or merge", not "the seat does not implement, edit the roster, or merge". Quote it exactly when the rule lands.
  Carry: R10-ROUND-PLAYBOOK
- The header says V129 is "quoted below as it stands"; the entry paraphrases it rather than quoting it.
  Carry: R10-ROUND-PLAYBOOK

## Evidence

- `ev/head.txt`, `ev/citations.txt`, `ev/checks.txt`, `ev/triage_gate_harness.py`, `ev/triage_gate.out`.
- RESULT symbol/id: V129 resolves at `proposals.md:653`; V136 resolves nowhere (0 of 121 entries). RESULT lines: `ruling_verdict` 455 vs body 456; `triage_refusal` 466 vs body 464.
- RESULT figures: 212 groups at `9aed78e0e`; PLAYBOOK 7 carries, `not-started`; BRIEFS-FOLD 20 carries, done.
- RESULT gate: 9 of 9 arms move. RESULT records: merge-tree clean, carry-audit 0 unrouted, two-file diff.
