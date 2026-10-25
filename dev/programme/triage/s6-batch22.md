# Proposal triage, session s6, batch 22 (P101-)

Rulings from the s6 `proposals.md`, collected 4 or 5 to a pull request under
tvofi's batching rule of 2026-10-24 (one PR per ruling only when it unblocks
critical-path work). Numbering continues after `s6-batch21.md` (P97-P100,
#2790, unmerged at this base).

## P101: set-stage done does not check open PRs' Carry: lines that name the group (S6-V35)
Verdict: ACCEPT (barrier) -> R10-FLOW-POSTMERGE. `tools/audit/seat/roster_edit.py set-stage <group> done` refuses, and writes nothing, while any open pull request body carries a `Carry:` marker naming that group, and prints the pull requests to re-point. Every other stage is unchanged.
- REJECTED: running the whole `carry_audit.py` over every open body. Only the destinations matter here, and `carry_audit.carry_dests` already reads them.
- REJECTED: leaving it to the memory rule (`done-before-reroute`). It is a manual step of the post-merge beat, and it has been skipped four times.
Source: s6 `proposals.md` `## V35`.
Instances: 4 blocks on 3 pull requests, as the orchestrator's memory and V35 record them; I did not open the PRs.
- #2404 at r5, r7 and r8, 2026-10-19: three review blocks, each a carry aimed at a group already set done.
- #2762, 2026-10-25: body item c8bac42d carries to R10-POLICY-FIXER-MD after that group was set done, so `carry_audit` reports BAD-DEST at train preflight and the merge is parked.
This is past the third instance of one class, so a barrier is owed, not a note.
Measured on main:
- `op_set_stage` sets `resume.stage` and checks nothing about the group's other readers (`roster_edit.py`, line 153).
- `carry_audit.carry_dests(text)` returns every destination token of a body's `Carry:` markers, and needs no network. The only network read is the list of open pull request bodies.
- Main's roster lags the roster branch, so `pr-contract` stays green on the stale destination and only the reviewer or the train preflight catches it (memory `done-before-reroute`, recorded 2026-10-19).
Cost:
- About 25 lines in `roster_edit.py`: when the stage is `done`, one bulk read of the open pull requests' bodies (`gh pr list --state open --json number,body`, a single call and not one per pull request), `carry_dests` over each, and a refusal naming the numbers.
- `set-stage done` runs about once per merged group, so the call count is about one per merge.
- Fail closed, the repository's usual rule: if the listing cannot be read, the stage is not set, and the refusal says so.
- A self-test with a stub listing: a body carrying to the group refuses; the null control, a body carrying to another group, sets the stage; a body with no `Carry:` also sets it.
- The cost of not doing it: a parked merge (#2762 is at train preflight now) and a fixer round to re-point the carry, once per hit.
Binding: four instances of one class, a cause that sits in one function, and a fix of about 25 lines and one API call per merge, against a manual step that has failed four times.
What would change the answer: a legitimate `done` while a carry still names the group (a deliberate dismissal in the same step). That would want an explicit `--allow-open-carry <reason>` flag; it would not change the refusal.
Carry text (for `roster_edit.py append-carry R10-FLOW-POSTMERGE`, citing `triage: dev/programme/triage/s6-batch22.md#P101`): "In tools/audit/seat/roster_edit.py `op_set_stage`, when the stage is `done`, list the open pull requests' bodies with one `gh pr list --state open --json number,body` call, take `carry_audit.carry_dests` of each body, and refuse without writing when any destination equals the group, printing the pull request numbers to re-point; if the listing cannot be read, refuse too. Every other stage is unchanged. Self-test with a stub listing: a body carrying to the group refuses; the null control, a body carrying to another group, sets `done`; a body with no Carry: sets it. Mutation proof: dropping the destination comparison fails the refusal case. Basis: carries to a group already set done produced BAD-DEST blocks on #2404 (r5, r7, r8, 2026-10-19) and #2762 (2026-10-25, parked at train preflight)."
