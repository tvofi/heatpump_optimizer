# Proposal triage, session s9, batch 93 (P333, P334)

The rolling batch after batch 92. Facts were read at origin/main `7539d1675` and at the round's
roster branch, `origin/handoff/audit-r10-roster`.

## P333: the tick prints DESIGN OWED for a group whose approved design rides another topic

Verdict: REJECT as filed. The proposed mechanism does not resolve the instance, and the instance has
two causes that cost an operation each and need no code. No roster op from this ruling.
- **What was proposed.** `designs_owed` in `tools/audit/seat/orchestrator_tick.py` (lines
  1236-1265 at `7539d1675`) would match a design ref through `roster_lib.group_for_branch`, as the
  design-verdict arm does (line 1319), instead of by `design/<group id lowercased>` (line 1248).
- **It does not match this instance.** `group_for_branch` (`roster_lib.py` lines 452-473) tries
  two matches:
  - an exact `resume.branch` match. R10-AUDIT-COVERAGE-ENDGAME's `resume.branch` is null, so
    `branch_of` gives `handoff/r10-audit-coverage-endgame`.
  - the branch's last segment, normalized, against each group id, and only on equality, "never a
    prefix". `r10-audit-coverage` is not equal to `r10-audit-coverage-endgame`.

  So `group_for_branch(roster, "design/r10-audit-coverage")` returns None. The tick would still
  print `DESIGN OWED: CP R10-AUDIT-COVERAGE-ENDGAME`.

  Widening the match to a prefix is what that function's docstring forbids: `fix/r9-fr-1` must not
  answer for `R9-FR-10`.
- **The two causes are records, not code.**
  - **The design ref is named off-contract.** `designer.md` step 8 puts the note "at
    `design/<group>`". Of the 12 `design/*` refs on origin, exactly one names no roster group:
    `design/r10-audit-coverage` (ae3d86dc0), with `design-verdict/r10-audit-coverage` 5b77e98dd.
    The tick follows the contract. The ref does not.
  - **The roster stage is stale.** The group's `resume.stage` is `not-started`, while its
    `next_step` reads "fixer dispatched (s9, local opus)". `designs_owed` skips any group past
    `UNBLOCKABLE_STAGES + ("design",)` (line 1256, `UNBLOCKABLE_STAGES = (None, "", "not-started")`
    at line 208). With the stage recorded as `fixing`, the line stops whatever the design ref is
    named.
- **Remedy (orchestrator and roster ops, not a carry).** Queue
  `set-stage R10-AUDIT-COVERAGE-ENDGAME fixing`. That ends the false CP line on the next tick, and
  it is owed anyway, because a dispatched fixer at `not-started` misstates the plan. Optionally,
  push `design/r10-audit-coverage-endgame` and `design-verdict/r10-audit-coverage-endgame` at the
  same SHAs, so the design is found by contract. A rename of a ref the fixer's brief already cites
  is not needed.
- **Re-open trigger.** Re-open if a second off-contract design topic appears. That is, a design
  ref under `design/` that names no group, at two or more in a round. The fix then belongs at the
  writer: `bus.sh`'s design push, or the designer's brief, refusing a topic that is not a group id.
  It does not belong in a widened reader.

Source: the orchestrator s9's triage-queue line of 2026-10-31T17:15:00Z (slip, false owed line).

Instances:
- One. `git ls-remote origin 'refs/heads/design/*'` gives 12 refs. A comparison with the roster
  branch's group ids, lowercased, leaves `r10-audit-coverage` as the only one off-name.

Cost of the filed change: a few lines plus a self-test case, which would buy nothing for this
instance. The remedy costs one queue line.

Binding: a code change that leaves its own instance unfixed adds surface for nothing. One roster op
that is already owed removes the line.

## P334: roster_edit.py append-group refuses an @path while append-carry requires one

Verdict: ACCEPT, as one carry on R10-ORCH-ROSTER-SCHEMA. That group owns `roster_edit.py`'s op
grammar and holds P300's comment-strip carry. It is `done` at `67178dc6a`, so the op that appends
the carry must be preceded by `set-stage R10-ORCH-ROSTER-SCHEMA carries-open`. The `edit-brief` half
is already built.
- **The asymmetry, at `7539d1675`.**
  - `op_append_group` (line 237) passes its argument straight to
    `Path(json_file).read_text`. A leading `@` is read as part of the path:
    `append-group: unreadable JSON: [Errno 2] No such file or directory: '@/...'`.
  - `edit-brief` already reads `@file`. `op_edit_brief` (line 272) calls `_text` (line 429),
    which strips the `@`. The help on line 74 says so.
  - `append-carry` treats a bare path as literal text. That is the reverse trap: a stored path, not
    the file's contents, which `roster_queue.py` line 149 reads back only for `@`.
  - So one queue line shape, `<op> <group> @file`, works for two ops and refuses for the third.
- **Instances.** The roster seats' reports hold 9 append-group refusals on an `@` path, from
  `grep "No such file or directory: '@"` over `s7/roster-s8-report.txt` and `roster-report.txt`.
  The paths named are:
  - R10-CATALOG-PR, R10-FLY-BUS-BASH32, R10-FLY-CANCEL-SWEEP, R10-FLY-SEAT-ALIVE-ID,
    R10-FLY-TICK-APPROVAL-OWED and R10-MARKETPLACE;
  - R10-FLY-RELAY-DELIVERED-GUARD, once;
  - R10-FLY-STANDING-CONTRACTS, twice.

  `roster-queue-s7.txt` lines 397-399 record s8 re-queueing three of them bare, and line 706
  records s9 doing the same. Each refusal cost a group append until someone read the report and
  re-queued it. Today that was hours for two groups.
- **Measured over two sessions:** 9 refusals, which is past the audit-class threshold of three.

Source: the orchestrator s9's triage-queue line of 2026-10-31T17:15:00Z (slip, two refusals today).

Instances: as above. The figure comes from a `grep` of the two roster report files.

Cost:
- About 3 lines in `op_append_group`: strip one leading `@` before the read. Plus a self-test pair
  next to the existing `append-group rc` and `round-trip` rows (lines 1065-1071).
- `roster_edit.py` has no `policy_lint.mjs --budgets` row; the `--budgets` output at `7539d1675`
  names it 0 times.
- No policy changes. The help line for `append-group` names `<json-file | @json-file>`.

Binding: 9 refusals in two sessions, each a lost group append, against three lines that make one
queue grammar true for all three file-reading ops.

The carry:
1. **Strip the `@`.** In `tools/audit/seat/roster_edit.py`'s `op_append_group`, strip one leading
   `@` from `json_file` before `Path(...).read_text`.
2. **State the grammar.** Change the usage line and the ops help (lines 7 and 72) to
   `append-group <json-file | @json-file>`, and say that `append-carry` and `edit-brief` read
   `@file` too.
3. **Fixtures.**
   - `append-group @<newg>` returns rc 0, and the round-trip matches the bare-path row.
   - Null: the bare path still reads unchanged.
   - Null: `@<missing>` is still refused, `unreadable JSON`, rc 2.
4. **One mutant.** Drop the strip, and the `@` row returns rc 2.
5. **Out of scope.** `edit-brief` already reads `@file` through `_text` (line 273), and
   `append-carry`'s bare-text behaviour is its documented form. Neither changes.
