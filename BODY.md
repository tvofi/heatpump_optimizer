Triage batch 93 rules three of the orchestrator s9's triage-queue slips of 2026-10-31 (17:15Z twice, 18:30Z). This is the next rolling batch after batch 92, with three rulings, one held carry and one released stage correction.

- **P333: REJECT as filed.** The tick prints a false `DESIGN OWED: CP` for R10-AUDIT-COVERAGE-ENDGAME.
  - The proposed `group_for_branch` match would not resolve it. `group_for_branch(roster, "design/r10-audit-coverage")` returns None: the group's `resume.branch` is null, and the tail matches only on equality, never a prefix (`roster_lib.py` 452-473).
  - The causes are records:
    - the design ref is off-contract. `designer.md` step 8 says `design/<group>`, and 1 of 12 `design/*` refs names no group;
    - the stage is `not-started`, although the design is approved. The fixer is waiting on R10-FLY-MUTANT-RESTORE and R10-996-RUNNER-CLAIMS, not dispatched.
  - Remedy: the orchestrator's queued `set-stage R10-AUDIT-COVERAGE-ENDGAME queued`, plus a `next_step` correction. That op supersedes anything this ruling might name; `designs_owed` skips `queued`. Optionally, alias refs at the same SHAs.
  - Re-open at a second off-contract design topic, with the fix at the writer.
- **P334: ACCEPT**, as one carry on R10-ORCH-ROSTER-SCHEMA (its `set-stage ... carries-open` is released now, under P335).
  - `op_append_group` reads `@file` as a literal path, so 9 append-group refusals sit in the s8/s9 roster reports.
  - `append-carry` and `edit-brief` already read `@file`; `edit-brief` does it through `_text`.
  - The carry: strip one leading `@`, and fix the help line. Null rows: a bare path is unchanged, and a missing `@` file is still refused.

- **P335: ACCEPT as already ruled (P305).** The merge seat queued `done` for R10-WOOD-NOTIFY over a carry that had already landed.
  - The barrier is the #2733 remainder plus P305's amendment on R10-ORCH-ROSTER-SCHEMA: one predicate shared by both writers. It is now built on `handoff/r10-roster-schema` `6aea809f6` (PR "R10-ORCH-ROSTER-SCHEMA (part 2)" opening), not yet on main.
  - That group was itself closed over those carries today. `roster_sync` `52aea59b1` (15:53Z) rewrote `in-progress` to `done`.
  - `set-stage R10-ORCH-ROSTER-SCHEMA carries-open` (queue line 719) is released now, as a stage correction.
  - Nothing further is owed for P335. The merge seat's interim read of the roster carries is in its brief (orchestrator s9).
  - REJECTED: the merge-seat check as filed. It guards one of the two writers, has no delivered marker to read, and would edit `standing-merge.md`, which is near its cap (36 of 37 lines).

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`b8fe7646e3409e914f52654538d23cdb5d44df77`; the file is the whole diff against `7539d1675`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P333 as `REJECT`, and P334 and P335 as `ACCEPT`.
- `triage_refusal` passes P334's carry, which cites `triage: dev/programme/triage/s6-batch93.md#P334`, and returns None.
- With P334's verdict changed to `REJECT`, the carry is refused: `dev/programme/triage/s6-batch93.md#P334 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it as not on the roster branch or on origin/main.
- P333 and P335 carry no op of their own. P335's stage correction is a `set-stage`, which no triage gate reads.

## Figures

- `orchestrator_tick.py` at `7539d1675`:
  - `designs_owed` at lines 1236-1265;
  - the `design/<id lowercased>` set at line 1248;
  - the stage skip at line 1256;
  - `UNBLOCKABLE_STAGES` at line 208.
- `roster_edit.py` at `7539d1675`:
  - `op_append_group` at line 237;
  - `op_edit_brief` at line 272;
  - `_text` at line 429.
- `roster_sync` `52aea59b1` set R10-ORCH-ROSTER-SCHEMA to `done` (from `in-progress` at `a396c2a83`). `git grep -ci mark-carry origin/main -- tools` prints nothing.
- `git ls-remote origin 'refs/heads/design/*'`: 12 refs. 11 name a roster group, and `r10-audit-coverage` does not.
- `node tools/policy/policy_lint.mjs --budgets` names neither `roster_edit.py` nor `orchestrator_tick.py`.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
