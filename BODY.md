Triage batch 72 rules the orchestrator s8's message of 2026-10-30. `carry_audit.py` flagged item `08d5f26d` of the #2987 verdict (issue comment `6520504435`) as UNROUTED, and that parked #2987 in the train. The item is the reviewer's `## Evidence` line "- Red checks: none red in the check-runs API at this read ... They are not a block for a docs-only diff". It is the next rolling batch under V182, after batch 71 (#2991). It holds one ruling and one held roster op.

- **P306: ACCEPT narrowed, an amendment to P293's carry on R10-FLY-CARRY-DISPOSITION.** That fixer is not started and already edits this Evidence-arm predicate and its fixture table.
  - An Evidence item that opens `Red checks:` and states none is red is a check-state measurement, and its NONBLOCK words are not read. DEFERRED and LEAD still are, and an item naming a red check is unchanged.
  - REJECTED: "never count an Evidence bullet". P293 refused it already, and #2465's shape (a defect left in place, not blocking, under Evidence) stays a finding.
  - Already done: `RESULT` lines are freed by `TRAILER` (`carry_audit.py:103`).
  - Measured: 1 of the 40 newest `verdict/*` refs has this shape. Of the "four waivers", two (#2925 `a3103224`, #2962 `75f08830`) are BAD-DEST, P296's class, not this one.
  - Null controls carried: the #2465 row, a `Red checks:` line naming a check red, and an unrouted item under `## Findings`, all still findings.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`21bbfc66a5290b17feef7dc22b74a458f77d06eb`; the file is the whole diff against `1afdef887`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P306 as `ACCEPT`. `triage_refusal` passes the carry text, which cites `triage: dev/programme/triage/s6-batch72.md#P306`: it returns None.
- With `Verdict: ACCEPT narrowed` changed to `Verdict: REJECT narrowed`, the same carry is refused: `dev/programme/triage/s6-batch72.md#P306 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve: `the triage ruling dev/programme/triage/s6-batch72.md is not on the roster branch or origin/main`.

## Figures

- `gh api repos/tvofi/heatpump_optimizer/issues/2987/comments` (comment `6520504435`): `## Findings` at line 7, `## Evidence` at line 11, and the item at line 19.
- `git ls-remote origin 'refs/heads/verdict/*'`, the 40 newest, each `VERDICT.md` read with `git show`: 2 hold a `- Red checks:` line, and 1 (`verdict/2987`) pairs "none red" with a NONBLOCK word.
- `tools/audit/carry_audit.py` at main: `TRAILER` at line 103, `NOT_REQUIRED` at line 111, `NONBLOCK` at line 119.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
