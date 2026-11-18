# Proposal triage, session s8, batch 72 (P306)

The rolling batch (V182) after batch 71 (#2991, in the train). Facts were read at origin/main
`1afdef887`, in the verdict comment on #2987 (issue comment `6520504435`), in the 40 newest
`verdict/*` refs on origin, and in the orchestrator's `seat-ledger.md`.

## P306: carry_audit reads a reviewer's "Red checks: none red" evidence line as a finding

Verdict: ACCEPT narrowed. This is one more shape in the class P293 ruled (`s6-batch64.md#P293`): the
`## Evidence` arm over-fires on a reviewer's measurement. P293 is a carry on
**R10-FLY-CARRY-DISPOSITION** (`not-started`), released to the roster today and not yet built. That
fixer edits the same predicate with a fixture table, so this ruling is one amendment carry there.
- **Narrowed.** An `## Evidence` item that opens `Red checks:` and states that none is red is a
  check-state measurement, and its NONBLOCK words are not read. DEFERRED and LEAD still are.
- **REJECTED: "never count a `## Evidence` bullet".** P293 already refused it. A defect left in
  place, called not blocking, under `## Evidence` is a finding (#2465's shape), and that row stays
  a null control.
- **Already done: "or a RESULT line".** `carry_audit.py`'s `TRAILER` (line 103 at main) already
  frees `RESULT` lines wherever they sit.

Source: the orchestrator s8's message of 2026-10-30, after the merge seat's waiver audit
(`seat-ledger.md:2552`: "#2987 fa662285 only UNROUTED 08d5f26d (## Evidence)").

Instances:
- **This one.** The #2987 verdict (issue comment `6520504435`) has `## Findings` at line 7 and
  `## Evidence` at line 11. Its line 19 reads "- Red checks: none red in the check-runs API at
  this read. ... were still in_progress ... They are not a block for a docs-only diff, but the
  merge train reads them." The NONBLOCK word is "not a block" (`NONBLOCK`, `carry_audit.py:119`).
  It qualifies checks that are in flight, not a defect. `NOT_REQUIRED` (line 111) frees only "not
  a required context/check ... does not block", and P293's carry, not yet built, widens it to "not one of the
  required contexts" and "not this pull request's ... and does not block" in an item naming a red
  check. Neither covers "none red ... not a block".
- **How often, measured.** Of the 40 newest `verdict/*` refs on origin, each holding a
  `VERDICT.md`, 2 carry a `- Red checks:` evidence line. One of those pairs "none red" with a
  NONBLOCK word: `verdict/2987`. So the shape is rare (1 in 40) and new, since P293's 30-verdict
  table had none.
- **The "fourth waiver this round" is not four of this class.** The same ledger line shows #2925's
  only item is BAD-DEST `a3103224`, and #2962's is BAD-DEST `75f08830`. Both are P296's class
  (`s6-batch65.md`), not the Evidence arm. This class has one waiver, #2987's.

Cost:
- About 3 lines in `carry_audit.py`'s Evidence arm (a `Red checks:` lead, a "none red" or "no red"
  test, and NONBLOCK not read in that item), plus three fixture rows. They go in the arm and
  fixture table P293's fixer is already building.
- No new file, check, API call or review round. `carry_audit.py` is not capped.

Binding:
- Benefit: one train park and one waiver so far. The `Red checks:` line is the body template's own
  label, which reviewers echo under Evidence while CI is in flight, so the shape recurs whenever a
  docs-only head is reviewed before its heavy lanes finish.
- Against a near-zero marginal cost inside a fixer already editing this predicate, the trade is
  clearly positive.
- As a stand-alone group it would be marginal and rejected. That is why it rides P293.
- The two other waivers are BAD-DEST and stay with P296's carry.

Carry text (for `roster_edit.py append-carry R10-FLY-CARRY-DISPOSITION`, citing
`triage: dev/programme/triage/s6-batch72.md#P306`): "Amends P293's Evidence-arm carry (P306,
orchestrator 2026-10-30).
- In `tools/audit/carry_audit.py`'s `## Evidence` arm, an item that opens `Red checks:` and states
  none is red (`none red`, `no red`, or `none` right after the colon) is a check-state measurement.
  NONBLOCK is not read in it. DEFERRED and LEAD still are, and an item naming a check as red is
  unchanged.
- Observed: #2987 verdict comment 6520504435, item 08d5f26d, "- Red checks: none red in the
  check-runs API at this read. ... They are not a block for a docs-only diff". It was flagged
  UNROUTED and parked #2987 in the train. 1 of the 40 newest verdict refs has this shape.
- Fixture rows:
  - That item clears.
  - Null, still a finding: "- Red checks: `gate` red, a pre-existing defect, not blocking" (a check
    named red).
  - Null, still a finding: P293's #2465-shape row (a defect left in place, not blocking, under
    Evidence).
  - Null, still a finding: an unrouted item under `## Findings`, refused as UNROUTED.
- One mutant: drop the `Red checks:` lead test, and the #2987 row is flagged again."
