Triage batch 74 rules the orchestrator s8's class report of 2026-10-30: `carry_audit.py` reads reviewers' `## Evidence` measurements as unrouted findings and parks train entries. It has done so for four items on three pull requests today, each waived by name under the mandate. It is the next rolling batch under V182, after batch 73. It holds one ruling and one held roster op.

- **P308: ACCEPT narrowed, a carry on R10-FLY-RELAY-REVIEW-FF.** That group owns `carry_audit`'s disposition since R10-FLY-CARRY-DISPOSITION was folded into it with P293 and P306.
  - Structural rule: an `## Evidence` item is a finding only when it opens with a LEAD, sits under a lead, or carries a `Carry:` marker. DEFERRED and NONBLOCK words elsewhere in it are not read.
  - Findings, Friction, Block and every other heading are unchanged. This supersedes P293's and P306's word tuning on that arm.
  - Instances, re-judged at `cc930cdd1` with `carry_audit.py pr <n>`: #3002 `af269651` ("residual"), #3001 `c4431278` ("deferred" as a stage name) and `3de8ca1d` ("residual"), and #2987 `08d5f26d` ("not a block").
  - Precision measured over P293's 30 verdicts plus these items: 12 flags, 0 findings.
  - The binding cost, stated: #2441's and #2465's fixture shapes (a defect left in place, not blocking, under Evidence with no lead) stop being findings. Those rows flip to pass, annotated that a defect handed on goes under `## Findings` or opens with a lead.
  - Null controls carried: an unmarked `## Findings` item still refuses; an Evidence `Follow-up:` lead is still a finding; an Evidence `Carry:` is still judged for its destination.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`3214f52a7f8f2e1bf3b39cc13fc8bb33c397be43`; the file is the whole diff against `cc930cdd1`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P308 as `ACCEPT`. `triage_refusal` passes the carry text, which cites `triage: dev/programme/triage/s6-batch74.md#P308`: it returns None.
- With `Verdict: ACCEPT narrowed` changed to `Verdict: REJECT narrowed`, the same carry is refused: `dev/programme/triage/s6-batch74.md#P308 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it as not on the roster branch or origin/main.
- The carry appended to the live roster, run through `node tools/policy/brief_lint.mjs` at `cc930cdd1`, gives `TOTAL: 0 error(s)`.

## Figures

- `python3 -I tools/audit/carry_audit.py pr 3002` gives `UNROUTED #3002 review 6528190135 item af269651 (## Evidence) [evidence]`.
- `python3 -I tools/audit/carry_audit.py pr 3001` gives `UNROUTED ... item c4431278 (## Evidence) [evidence]` and `... item 3de8ca1d (## Evidence) [evidence]`.
- `git log -S'EVIDENCE_HEADING' origin/main -- tools/audit/carry_audit.py` names `1e2252261` (2026-10-21) as the arm's origin. Its #2441 and #2465 rows are in the fixture table.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
