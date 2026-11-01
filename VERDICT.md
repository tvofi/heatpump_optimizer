Fix review: merge 77524a704af85e3a402b95b8b8c66a25332a08a3

bus-nonce: de47dad1a03520ce1ee596bce5d31dce

Round 1. Measured at 77524a704af85e3a402b95b8b8c66a25332a08a3 from a detached worktree; head unchanged at post time.

## Findings

- The carry_audit sites `orphaned`, `sweep_ref` and `Dests.owns` are pinned in-tree only by carry_audit's own self-test, with no in-tree mutant harness; the body's CA1-CA4 plants live in an untracked scratch driver. I planted four of my own (owns always False, sweep_ref returning main, unreadable state read as closed, carry files ignored) and each failed the self-test, so they are pinned today, but the plants are not reproducible from the tree. Carry: dismissed: the self-test kills every plant I made, and the body states the disposition for prepr step 6d.
- `roster_sync.issue_reader` turns a failed `gh` issue read into Refuse for the whole pass, but only when the pass derives a done; a gh outage therefore halts reconciliation for that beat, which differs from `orphaned`'s unreadable-counts-as-open rule (which applies only to a None state). Carry: dismissed: refusing on an unreadable read is the reconciler's standing rule (B11) and the next beat retries.

## Evidence

- RESULT 8-issue table re-derived with carry_audit.load_dests(<ref>).owned: at origin/main #2248/#2249/#2257/#2942/#2998 unowned, #2492 owned by R10-SAV-ACTUATION, #2731 by R10-FLY-GH-READ-RETRY, #2674 by carry-2674.json (sweep catches 5 of 8). At the cited live ref 84571a150c06 all of them unowned except #2674: live ref catches 7 of 8, as the body says. The live tip has since moved (3f6dc470f) and differs, as expected.
- RESULT mutants: M25 rc=1 fails=4, M26 fails=1, M27 fails=4, M28 fails=3, H1 fails=2, H2 fails=1, all as in the body; files restored. My own four carry_audit plants fail 1-3 checks each.
- RESULT self-tests at head: carry_audit 214/0, roster_sync 83/0, roster_edit 135/0, r10_roster_ops_mutants 105/0.
- Null controls: the new fixtures hold twin checks (shared owner, closed issue, carry file, O-brief, twin groups closing together) that assert done is written; M28 turns those red, so a legitimate done transition is not refused when the issue is closed or has another owner.
- Figure not re-derived: the historic-parent replay (c47931afa, PR #2961). My attempt with `--roster-file` read the live ref instead and derived nothing, so I cannot confirm those two lines. The 2382-version / 264-transition class replay (scratch script, not in the tree) was not re-run either; both rest on the body's account. The fixture null controls and the table above stand independently.
- tests/structure.py: STRUCTURE RATCHET PASSED. Scoped gate: MODE: SCOPED -- 1 script(s) run, 32 scoped out. No VERSION, manifest, RELEASE_NOTES or golden/claim change in the three-dot diff; delivery row dev/programme/delivery/3092.md present. git merge-tree --write-tree origin/main head: rc 0, no conflict.
- CI: all 55 check runs at the head success or skipped, none red (## Red checks: none is correct); merge_train.py classify GREEN. Body carries all answered by carry_audit (5 routed, 0 unrouted).
- Process state (c) named, cost test with numbers, countermeasure and demonstration present per root-cause.md.
