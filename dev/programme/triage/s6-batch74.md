# Proposal triage, session s8, batch 74 (P308)

The rolling batch (V182) after batch 73 (handoff `triage-s8-batch73`). Facts were read at
origin/main `cc930cdd1`, on the roster branch `origin/handoff/audit-r10-roster`, and in the
verdict comments named below. Each was fetched by id with
`gh api repos/tvofi/heatpump_optimizer/issues/<n>/comments` and re-judged with
`carry_audit.py pr <n>` at `cc930cdd1`.

## P308: carry_audit's `## Evidence` arm parks the train on reviewers' measurements

Verdict: ACCEPT narrowed. It replaces the word tuning of P293 (`s6-batch64.md#P293`) and P306
(`s6-batch72.md#P306`) with a structural rule. Host: **R10-FLY-RELAY-REVIEW-FF**
(`carries-open`), which now owns `tools/audit/carry_audit.py`'s disposition: R10-FLY-CARRY-DISPOSITION
is folded into it, P293 and P306 included ("carried whole").
- **The rule.** In a verdict's `## Evidence` section, an item is a finding only when it hands
  something on explicitly. That means it opens with a LEAD (`Out of scope:`, `Follow-up:`,
  `Residual:`, `Not fixed here:` ...; `carry_audit.py`'s `LEAD`), or it carries a `Carry:` marker,
  which is then judged as everywhere else.
- **What stops.** DEFERRED and NONBLOCK words anywhere else in an Evidence item are no longer
  read. That is the orchestrator's proposal, narrowed only to keep the explicit lead.
- `## Findings`, `## Friction`, `## Block` and every other heading are unchanged.
- **P293 and P306 are superseded on this arm.** Their `NOT_REQUIRED` shapes, code-span strip and
  `Red checks:` row are moot under the new rule. Their fixtures stay as rows that must now pass.
  P293's class-B "advisory" decline needs no change.

Source: the orchestrator s8's message of 2026-10-30. It reports a recurring class and four items
waived by name under the mandate.

Instances. Every one is an `## Evidence` item flagged `[evidence]` and UNROUTED, and every one is a
measurement:
- #3002, verdict comment `6528190135`, item `af269651`: "- No finder's harness is named. This is
  tooling item G of a residual brief, and the self-test is the instrument." The trigger is
  "residual" (`DEFERRED`).
- #3001, verdict comment `6527309416`:
  - Item `c4431278`: "- Disposition-stage count in the live roster: 11 at both the head and the
    base, under the body's own rule (DISPOSITION = deferred, refused, ...)". The trigger is
    "deferred" in a list of stage names (`NONBLOCK`).
  - Item `3de8ca1d`: "- Forward-carry: every residual in the body routes to a group (carry_audit:
    5 routed, 0 unrouted)". The trigger is "residual".
- #2987, verdict comment `6520504435`, item `08d5f26d`: "- Red checks: none red ... not a block"
  (P306).
- **Before today.** P293 counted 7 Evidence items flagged in 5 of the last 30 merge verdicts, none
  of them a finding.
- **Precision of the arm, measured.** Over P293's 30 verdicts and these four items, 12 Evidence
  flags, 0 findings. The two true shapes the arm was written for (#2441's nit and #2465's defect
  left in place) are its own fixture rows from the commit that introduced it, `1e2252261`
  (2026-10-21, "a verdict's ## Evidence is no finding unless it hands a defect on"). No later true
  catch is recorded.
- **Why word tuning does not converge.** The four new triggers are three different words ("residual"
  twice, "deferred" as a stage name, "not a block"), none of them covered by P293's or P306's
  shapes. P293 and P306 are both unbuilt. Each new reviewer phrasing has so far meant one more
  park, one more waiver and one more ruling. Four instances across three PRs in a day makes this
  an audit class under `defect-root-cause.md`, and the barrier has to remove the class, not add
  a fifth phrase.

Cost:
- About 5 lines in the Evidence branch (`carry_audit.py:205-207`): keep `LEAD.match(first)` and
  the `inherited` lead, and drop the `DEFERRED`/`NONBLOCK` clause there. Plus fixture changes and
  the parser-mutant harness sites it names (`dev/audit/harnesses/r10_carry_parser_mutants.py`).
- The binding cost is detection: #2441's and #2465's shapes (a nit or a defect left in place,
  called not blocking, under Evidence with no lead) stop being findings. Pay for that on the writer
  side, at no review-time cost: the fixture rows for those two shapes flip to "passes", each
  annotated that a defect handed on belongs under `## Findings` or opens with a lead.
- No new file, check or API call. `carry_audit.py` is not a capped file.

Binding:
- Twelve false parks against zero measured true catches since the arm landed. Each false park
  costs a train skip and a named mandate waiver, and the orchestrator has made four today. A rule
  that trades a fixture-only true shape for that is clearly positive.
- Keeping the explicit lead preserves the one way a reviewer hands a defect on from Evidence
  deliberately.
- REJECTED: keeping the word arm and tuning it again (the P293/P306 path). It has not converged.

Carry text (for `roster_edit.py append-carry R10-FLY-RELAY-REVIEW-FF`, citing
`triage: dev/programme/triage/s6-batch74.md#P308`): "P308 (orchestrator 2026-10-30, class barrier)
supersedes P293's and P306's Evidence-arm word tuning, folded here from R10-FLY-CARRY-DISPOSITION.
- In `tools/audit/carry_audit.py`'s `## Evidence` branch (lines 205-207 at cc930cdd1), an item is
  a finding only when it opens with `LEAD`, sits under a lead (`inherited`), or carries a `Carry:`
  marker (judged as elsewhere). `DEFERRED` and `NONBLOCK` words elsewhere in an Evidence item are
  not read.
- `## Findings`, `## Friction`, `## Block` and every other heading are unchanged.
- Fixtures:
  - The four field items pass: #3002 `af269651`, #3001 `c4431278` and `3de8ca1d`, #2987 `08d5f26d`
    (texts in the ruling). P293's five class-A and C items pass.
  - Null, still a finding: an Evidence item opening `Follow-up:`.
  - Null, still a finding: an unmarked item under `## Findings` is refused UNROUTED.
  - Null, still a finding: an Evidence item with `Carry: <live group>` routes, and one with
    `Carry: <done group>` is BAD-DEST.
  - The #2441 and #2465 rows flip to pass, each annotated that a defect handed on belongs under
    `## Findings` or opens with a lead.
- Update the mutant sites in `dev/audit/harnesses/r10_carry_parser_mutants.py`.
- One mutant: restore the DEFERRED/NONBLOCK clause, and the four field rows fail."
