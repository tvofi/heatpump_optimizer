# Proposal triage, session s14, batch 204 (P634-P635)

Sources:
- Roster `handoff/audit-r10-roster`, read at its tip at 2026-11-11T14:33Z.
- origin/main `ceb3070ccb`.
- The fire ledger the beat's verdict-audit row reads: `fire_ledger` in the beat's
  `sweep-overlay.json`, which is `s9/seat-dispatch/ledger-standin.txt`. It has 1312 lines.
- The beat's `verdict-audit` job output, at 2026-11-11T14:45Z.
- The orchestrator's local `s9/sweep-runner/blind_spots.py`, which has no tree copy.

## P634: the fire-ledger line format hides fires from the stale-PR detectors

Verdict: ACCEPT narrowed, as a carry on R10-TICK-RESIDUE-P3, for the tracked
`tools/audit/seat/verdict_audit.py` (added to the group's files).
- Promoting the local RED-UNOWNED arm into a tracked instrument: DEFER.

Source: triage queue line 312, 2026-11-11T14:37:53Z, orchestrator s14, PROPOSAL blind_spots
fire-line format. The local fix was applied at 14:36Z.

Instances:
- The ledger's format changed. 71 of its last 300 lines lead with `FIRED <utc>`, and 229 lead
  with a bare stamp (`tail -300 | cut -c1-14`). The first `FIRED` line is line 274,
  2026-11-04T07:40:04Z.
- The local `blind_spots.fired_after` matched only a leading stamp. That raised 4 false
  RED-UNOWNED alarms in 30 min (#3444, #3430, #3469, #3452), each with a reviewer fired 60-75 min
  earlier. It is fixed locally.
- **The tracked twin has the same defect.**
  - `verdict_audit.recent_lines` (verdict_audit.py:29-37 at origin/main) keeps a ledger line only
    if `STAMP.match(l)`, which is anchored at column 0. So every `FIRED <utc>` line is dropped.
  - Its self-test's null control passes `"FIRED r10-x\n"` straight in as `recent` (:124) and
    never drives `recent_lines`. So nothing pins the reader.
  - Live effect, in the beat's verdict-audit output at 14:45Z: `UNHELD #3464 no verdict ever:
    owed a first reviewer`. Yet the ledger's line 1276 reads `FIRED 2026-11-11T12:48:59Z
    reviewer #3464 ...`, 2 h earlier and inside the 12 h window.
  - So 1 of the 6 UNHELD lines is false. Each false line costs an orchestrator turn, every
    1800 s beat until the fire ages out.

Classification:
- A reader defect in a tracked beat instrument that produces false owed work. Severity medium,
  the same as its host group's.
- The repair is a regex prefix plus a check that drives the reader, so the machinery bar does not
  apply.

Placement:
- No live group lists `verdict_audit.py`. Its last edits were 02ca1f20d8 and dba9e7d329, both
  beat folds.
- R10-TICK-RESIDUE-P3 is the not-started residue group that owns `beat_jobs.py`, whose
  verdict-audit row runs it. So it is a carry there, with `verdict_audit.py` added to its files.
- R10-SEAT-IDENTITY-P5 also lists `beat_jobs.py`, but its seam is the job table and the generation
  token.

The carry's acceptance:
- (i) `recent_lines` keeps a line led by a stamp, `FIRED <stamp>` or `- FIRED <stamp>`, and keys
  the age on that stamp.
- (ii) A self-test drives `recent_lines` → `audit` with a `FIRED`-prefixed fire for #N inside
  12 h. #N is held.
- (iii) Null control: the same line aged 13 h is not held. A line with no stamp is still
  ignored.
- (iv) Mutation: restoring the column-0 match makes (ii) red.

The RED-UNOWNED promotion is DEFERRED:
- UNHELD's `no verdict ever` arm covers a PR with no verdict ref. RED-UNOWNED adds the case of a
  red gate with a verdict at an older head and no fire in 3 h.
- No true positive of that extra case has been counted. The only figures are the 4 false ones
  above.
- What would change it: a count, over a day of the fixed local arm, of RED-UNOWNED lines that
  were true and that UNHELD did not print. If the count is non-zero, the arm goes into
  `verdict_audit.audit` as a carry on the same group.

Binding: false owed work from a tracked beat instrument. 1 of 6 UNHELD lines is false now.

Bar re-check (2026-11-11, orchestrator's question; proposal-triage.md lines 9-19). A carry on an existing group is still added instrument work, so the same bar applies to it. No ratchet-budgets.md cap is touched: every change here is code under tools/ and moves no policy_budgets.json measure, so the 20% figure below is read on the proposal's own benefit measure.

Bar: severity medium (R10-TICK-RESIDUE-P3's roster severity). Figure: 1 of 6 UNHELD lines false, about 17%, under 20%. Accepted as a severity-exempt defect repair (a reader that drops every `FIRED <utc>` line), not as over-20%.


## P635: P631 revisited, with the orphans' cwd

Verdict: DEFER stands, narrowed. The launcher is now identified, and the countermeasure, if
another instance comes, is one bound at that call site.

Source: the orchestrator's datum of 14:37:53Z (triage queue line 312, last sentence). Both
orphans' cwd (lsof) was a temporary copy-tree harness, `.../T/hr-sii7u88j/tree`.

Instances:
- The only tracked local launcher of `roster_lib.py --self-test` is
  `tools/audit/seat/r10_roster_ops_mutants.py`.
  - `target_self_test()` (:359-363) runs `subprocess.run([sys.executable, "-I", target,
    "--self-test"], cwd=ROOT)` with no `timeout=`.
  - The orphans' `python3 -I ... roster_lib.py --self-test` under the system 3.11 matches it when
    the driver itself was started with the system python.
  - A planted roster_lib mutant (L1-L8, :38) that loops would hang the child. If the harness that
    held the copy tree was then killed, the child would be orphaned under ppid 1, as observed.
- The `hr-` tree prefix is in no tracked file (`git grep` at origin/main), so the copy-tree
  harness itself is a seat's out-of-tree one.
- The cost is unchanged from P631: about 3.5% of an 8-core box for 4 h, once.

What would change it:
- A second instance. Then the countermeasure is `timeout=` in `target_self_test`, reporting a
  timed-out plant as `hang` (killed). That fixes the one call site, not every self-test.
- If the countermeasure is built, it goes as a carry on R10-TICK-RESIDUE-P3, the live roster-tool
  residue group. The groups listing `r10_roster_ops_mutants.py` (R10-ROSTER-OPS,
  R10-ROSTER-WRITE-SWEEP) are done.

Binding: one instance, under the bar on standing CPU.
