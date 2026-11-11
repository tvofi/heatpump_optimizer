# R10-TICK-RESIDUE-P3 design note: 24 carries cut into 11 parallel parts by owning seam

- **Base:** 0e28afd38b353ca8e66269d9ae4be8614fcf5cfb, which is origin/main when this note is written. Every line cited is at it. No predecessor (`after` is empty), so there is no handoff head to read.
- **Roster:** origin/handoff/audit-r10-roster 5dd572c649 (re-read before the push; the carries are unchanged from 085216ba9d). The group is size L with carries 0-23, byte-equal to the dispatch brief's snapshot (compared by script, all 24).
- **Sources read:** each carry's text; dev/audit/rca/R10-RCA-TICK-BLIND.md section 4 (countermeasures 1, 2, 4, 5, 7, 8, 9 are carries 0, 6, 1, 2, 3, 5, 4); the diff of #3471 at bdf48d98a9; #3425's merge ee64358be7.
- **No finder harness** for any carry: each is a triage ruling or an RCA countermeasure. The evidence is the measured instance each carry names; §5 names the fixture that replays it.
- **Three findings the orchestrator rules on before dispatch** (§6): carry 22 item (1) contradicts what #3425 merged and #3471 extends; carries 14 and 23 are one predicate; carries 12 and 13 are roster data with no production diff.

## 1. Owning seams

tests/seam_map.json names no file under tools/audit/seat, and tests/structure_budgets.json measures none, so `fixer.md` step 17's rule decides: the module that computes a fact owns it, and a module that prints it only calls.

| part | carries | owner (edited) | callers (hunk only) | size |
|---|---|---|---|---|
| T1 design review owed | 23, 14 | tools/audit/seat/ledger.py, beside `design_builds` (:621) | orchestrator_tick.py `design_builds` (:1676), owed_unactioned.py `FAMILY` and `key_of` | M |
| T2 dispatch gaps | 7, 1 | ledger.py (two pure predicates) | orchestrator_tick.py `plan` (:1595) | M |
| T3 red reasons | 16, 0 | orchestrator_tick.py `red_brief` (:1880) and `one_pr` (:1206) | reads merge_train.py `job_log` (:648), unedited | M |
| T4 owed handoffs | 6, 22 item (2) | orchestrator_tick.py `orphans` (:2411) | owed_unactioned.py is read by the pin, unedited | M |
| T5 record idempotence | 3, 5 | tools/audit/seat/record_beat.py (one reader of the record issue) | orchestrator_tick.py `unrecorded` (:2129) and the HANDOVER line (:2097); postmerge.py unedited | M |
| T6 repair barrier | 4 | orchestrator_tick.py `self_test` (:2742) | none | M |
| R1 relay skips | 11, 2 | tools/audit/seat/cloud_relay.sh `handoff_arm` (:572) and `probe_arm` (:330) | orchestrator_tick.py ranks the level lines | M |
| L1 tick loop | 18, 21 | tools/audit/seat/tick_loop.sh | none | M |
| B1 beat table | 19, 20, 8 | tools/audit/seat/beat_jobs.py, beatd.jobs.json, beat_jobs_selftest.py | none; beatd.py unedited | M |
| B2 CP watch | 15 | beat_jobs.py (a new row in `RUN`, :631) | calls T1's and T2's ledger predicates | M |
| X1 roster tools | 9, 17 | roster_edit.py self-test; roster_sync.py `carry_plan` (:508) | none | S + S |
| X2 plan page | 10 | roster_lib.py `one_line_brief` (:656) for (1); plan_page.py for (2), (3) | plan_table.py:126 gets (1) unedited | S |

No carry needs two owners. Carry 15 comes closest: its group arms are the predicates T1 and T2 land in ledger.py, and B2 owns only the row, the graces and the four PR arms.

## 2. Shape

**One ref snapshot, pure predicates (T1, T2, B2).** Today `designs_owed` (:1632) and `design_builds` (:1683) each run their own ls-remote. T1 widens the second, as carry 23 rules, with the design-reviewer dispatch refs; T2 adds one ls-remote of dispatch, handoff, handoff-wip, handoff-body and fix heads, cached on the `Tick` instance for the pass. The predicates take dicts and return lines, as `design_builds` does, so the tick and the beat row share them and the self-test needs no git.

```
ls-remote (git only) --> {ref: sha} --> ledger predicates (pure) --> lines
   one fetch of design + dispatch tips for commit times          |-> Tick.line(flag=True)
   a failed read is Tick.unreadable, never an empty dict         |-> B2 row: CP-OWED past grace
```

- **T1.** A function beside `design_builds` returning the line carry 23 item (1) spells, under its clauses (a)-(d); `FAMILY` gains the prefix and `key_of` a branch keyed on the design ref plus tip sha. Carry 14 asks for the same predicate with a shorter line; carry 23 is the later ruling (batch 164 against 141) and its line wins.
- **T2.** (7a) a carries-open or not-started group whose after-groups are all done or carries-open, with no dispatch, handoff or PR ref, prints the UNDISPATCHED line, CP-marked as `designs_owed` marks; `UNBLOCKABLE_STAGES` (:215) is not widened, because :1644 and :1646 reuse it for DESIGN OWED and would then owe designs for carries-open groups. (7b) parses `start after #N` from carry text. (1) walks `after` transitively from each open group `roster_lib.is_outside` is true for, and prints the idle path when its deepest open group has no seat ref inside `SEAT_WINDOW_MIN` (:129), first in its section.
- **T3.** `red_brief` falls back to `job_log` through the existing `_module` loader only when the check-run output is empty; escapes stripped before ERR_LINE. `one_pr`'s NOT REVIEWABLE (:1261) reads the same cached log per job id and classifies with the deferral text tools/ci/gate.py owns, imported as :1255 already imports that module, never a second regex. One API read of gate-sweep.yml's workflow state per pass prints the disabled line when it is not `active`.
- **T4.** Each OWED handoff line carries the opener's last result read from the open-driver state directory; a missing directory while handoffs are owed prints OPENER ABSENT once; a topic the opener skips by ruling prints held by ruling, not the opener repair. Carry 22 item (2)'s pin drives `orphans` with one ref over the cap and feeds every flagged line through `FAMILY` and `key_of`.
- **T5.** record_beat.py gains one function: the record issue's comments since a given time, matched for a sha40 locally. `record` (:123) calls it and posts nothing on a hit, `--retry` included. `unrecorded` calls it once per pass in place of one search per merge (ten calls become one paged read; the `type:comment` qualifier returns 0 for any sha, RCA lines 175-177). The carry's "issue 201" is stale: record_beat.py posts to its `RECORD_ISSUE`, and its self-test (:219) pins that it is not #201; read the constant. The line at :2097 stops naming `state_docs.py --push`, which cannot write the handover's updated-for line (RCA lines 189-194).
- **T6.** A table in `self_test`, one row per flagged line kind (the enumerator: `grep -c "flag=True" tools/audit/seat/orchestrator_tick.py`): the fake repair that removes the line, and the fake in which the repair cannot run and the line says so. A completeness check refuses a flagged kind with no row.
- **R1.** Carry 11: the arm has four silent skips of an open PR (:601 no handoff-body ref, :603 tip object absent, :607 body already applied, :608 first-pass seed) and one with no level (:680 busy). The fix is not a print per skip. After the loop, one sweep over open PRs and handoff refs writes `level_line` with a new handoff-behind kind for every PR whose head does not contain its handoff tip and for which this pass wrote no level, so a future skip cannot be silent either. Carry 2: `probe_arm` (:346-376) appends the reason class (carry_audit, already relayed, no ev names the head) to the level it already writes; the tick ranks critical-path PRs first.
- **L1.** Carry 18 adds two arms to `fresh_check` (:90) before the branch refusal at :105, and a second-consecutive-stale counter that appends the board line. Carry 21 replaces the single `sleep "$every"` (:84) with a loop that calls `relay_reap` (:119) and, once the gap has passed, `relay_start` (:128) under the same lock.
- **B1.** Carry 19: `roster_drain` (:339) appends one line per refusal through `event` (:274), whose dedupe is by line, so the line carries the occurrence key; refused keys go to a second memory beside the done one (:351). Carry 20: line 3 of beatd.jobs.json becomes 900 and the table check sits beside the roster-drain pin (beat_jobs_selftest.py:404-406). Carry 8: one row, one API read of ci.yml's runs, flagging an attempt of 20 or more; no reader of a run's attempt exists at the base.
- **B2.** Row cp-owed. Set: `roster_lib.is_outside` groups plus `roster_lib.critical_path_read`'s (:856, no caller under tools/audit/seat today), and their open PRs. Graces as carry 15 lists them, in one table at the top of the row.
- **X1.** Carry 9: the arm sits beside the P409 arm (roster_edit.py:2943); the mutant row goes in tools/audit/seat/r10_roster_ops_mutants.py. Carry 17: `carry_plan`'s exact-text skip (:543) widens to the 8-hex item id or the normalised text; mutant in r10_roster_sync_mutants.py.
- **X2.** (1) `one_line_brief` strips markdown heading and list markers before it cuts the first sentence. (2), (3): the page counts both figures from the rows it renders; plan_page.py:657 reads the open-groups figure from the plan file's summary today, which tools/plan/replan.py:1493 computes over a different set.

**Invariants kept.** A failed read is UNREADABLE, never empty. No tick part adds an API call except T3's one workflow read; T5 removes nine. No new tracked file, so `tests/entities.py` asks for no classification.

## 3. Alternatives

- **One pull request for all 24.** Lost on state ownership: eight files with five different self-tests, and one blocked verdict on any carry holds the other 23. The split was made to get exactly this off the critical path.
- **Predicates inside orchestrator_tick.py (T1, T2).** Lost on call count: B2 would import the 5290-line tick and its `Tick` state to ask one question, or re-implement it. ledger.py already holds `design_builds` in the pure form.
- **cp-owed as a tick level (carry 15 allows either).** Lost on budget: carry 21 measures a tick pass at about 290 API calls with about 240 an hour of headroom, and four PR arms add reads to every pass; a row keeps its own interval.
- **A print at each silent skip (R1).** Lost on coupling: five sites today, and the next skip added is silent again. The post-loop sweep states the invariant once.
- **Widening `UNBLOCKABLE_STAGES` (T2).** Lost because :1644 and :1646 share the tuple; see §2.

## 4. Sibling sites

- `git grep -n "ls-remote" -- tools/audit/seat/orchestrator_tick.py`: the fixer of T2 lists each and folds into the snapshot only those that read the same ref families; the rest stay.
- `git grep -n "one_line_brief(" -- tools`: two callers, plan_page.py:277 and plan_table.py:126. Both take X2 (1).
- `git grep -n "state_docs.py --push" -- tools/audit/seat/orchestrator_tick.py`: :2097 is carry 3's line. :2157 names it for the record beat, which state_docs can discharge; it stays.
- `grep -n "continue" tools/audit/seat/cloud_relay.sh` inside :572-713: R1's sweep covers every one; the fixer names in the body which predicate skipped #3358.
- `git grep -n "class_wait_s" -- tools/audit/seat`: the table and beatd.py's default (:129), which carry 20 leaves.

## 5. Evidence, by file

| part | failing test first | null control | mutants |
|---|---|---|---|
| T1 | orchestrator_tick.py self-test beside the DESIGN-BUILD arm (:5116): revise verdict at an older sha, newer tip, older dispatch gives one line that keys | verdict at the tip; dispatch newer than the tip; a done group | drop the dispatch-time clause; drop the stage gate |
| T2 | the OUTSIDE-INTAKE shape; the 19:11Z chain of RCA lines 287-293 | a live dispatch ref; every path ending in a live seat | drop the stage widening; stop the walk at depth one |
| T3 | null check-run output, a log with escapes and one error line; #3291's deferral with its decider green | a check-run with its own output makes no log read; a real red still reads back to its fixer | the fallback; the decider-green test |
| T4 | no open-driver directory with handoffs owed; cap plus one stranded refs | exactly the cap stranded | drop the absent line; re-break the cap line's key |
| T5 | a fixture pinning the query, not a chosen count; a second `record` for one sha posts nothing | a sha the issue does not carry still posts | drop the check in `record`; restore `type:comment` |
| T6 | a flagged kind with no row is refused | the shipped table is green | delete one row |
| R1 | #3358 at 88f4d521 against handoff 62542627 gives an update or an OWED line | a head containing its handoff gives neither | drop the sweep |
| L1 | carry 18's four cases and carry 21's stub case, in the script's own self-test (:179) | one stale pass; a relay still in flight at the gap | a `mut:` tag per arm, as the file does |
| B1 | a refused op's events line survives an applied pass; a table at 60 is refused; the #3287 window fires | an applied op; a run at attempt 1 | rows in `MUTANTS` (beat_jobs_selftest.py:932) |
| B2 | each arm fires at grace 0 | every step inside its grace prints nothing | one per arm |
| X1 | two ops in one run with the fetch in `_on_origin` (:945) failing; queue-then-sync appends once | green with the update-ref; a distinct item still appends | delete :1215; drop the skip |
| X2 | the 2026-11-10T01:14Z plan file: each figure equals its rows | a page with no such group is byte-unchanged | dev/audit/harnesses/r10_plan_page_mutants.py |

No golden fixture moves; neither claim file is touched. Carry 23's acceptance replay (three lines at the 05:06Z ref state, none at 05:20Z) goes in T1's body as a measurement, since those refs have moved.

## 6. Hot files, serial position, rulings owed

- **Parallel now, files disjoint:** L1, B1, X1 (its two halves also disjoint), X2, R1 and one tick part. R1's ranking hunk is its only tick line.
- **Tick train.** T1-T5 edit different methods of orchestrator_tick.py and add self-test arms beside their own level, so they build in parallel and merge in train order; each re-runs `--self-test` after its rebase. **T6 is last**: its completeness check would turn main red for any part merged after it without a row. T4 starts after #3471 merges, because #3471 rewrites the cap line that `orphans` prints.
- **B2 after T1 and T2**, whose predicates it calls. B1 and B2 share beat_jobs.py with R10-SEAT-IDENTITY-P5 (admitted overlap, train order). T3 only reads merge_train.py, which R10-GATE-DEFER-BARRIER and R10-GH-READ-RESIDUE-P3 edit.
- **Files to add to the group's list** (set-files): ledger.py, cloud_relay.sh, plan_page.py, roster_lib.py, beat_jobs_selftest.py, the two roster mutant harnesses. dev/programme/HANDOVER.md can leave it: carry 3 edits the tick's line, not the handover.
- **Ruling 1, carry 22 item (1).** It says the writer drops the OWED prefix and rejects a reader-side skip of the literal. The base has that skip: `CAP_NOTICE` (owed_unactioned.py:57, commit c966df873 in #3425), and #3471 widens it and pins the cap line as starting with OWED. The measured defect (the owed check UNREADABLE, rc 2) is therefore gone at the base. This note builds item (2) only, which holds under either wording. Building item (1) as written means deleting `CAP_NOTICE` and #3471's pin in T4; that is the orchestrator's choice between two rulings (batch 161 against batch 181), not a fixer's.
- **Ruling 2, carries 12 and 13.** Neither has a production diff. Carry 12 is four `append-carry` ops; its group is stage done (7 carries at the roster tip), and R10-GATE-DEFER-BARRIER owns the gate-deferral readers. Carry 13's code half is at the base (roster_queue.py:194 refuses the index forms); what is left is prose. Both are standing-roster work, not a fixer part.

## 7. Carries

- Carry: R10-TICK-RESIDUE-P3 (item 1): carries 23 and 14 are part T1; carry 14 is discharged by carry 23's line.
- Carry: R10-TICK-RESIDUE-P3 (item 2): carries 7 and 1 are T2; 16 and 0 are T3; 6 and 22 item (2) are T4; 3 and 5 are T5; 4 is T6.
- Carry: R10-TICK-RESIDUE-P3 (item 3): carries 11 and 2 are R1; 18 and 21 are L1; 19, 20 and 8 are B1; 15 is B2; 9 and 17 are X1; 10 is X2.
- Carry: R10-TICK-RESIDUE-P3 (item 4): carry 22 item (1) waits on §6 ruling 1 and is built by no part until it is given.
- Carry: R10-GATE-DEFER-BARRIER (item 5): carry 12's four restored carries land there by roster op, if §6 ruling 2 agrees.
- Carry: dismissed: code half already at base (item 6): carry 13's queue refusal is roster_queue.py:194; its prose half is the orchestrator's.

## Notes for the fixer

- Carry: R10-TICK-RESIDUE-P3 (item 7): T5, read `RECORD_ISSUE` from record_beat.py; do not write 201. Page the comments read by a since time taken from the oldest scanned merge, or the read grows with the issue.
- Carry: R10-TICK-RESIDUE-P3 (item 8): T3, cache `job_log` by job id for the pass; `one_pr` and `red_brief` can ask for the same job. The null control counts log reads, so the cache is observable.
- Carry: R10-TICK-RESIDUE-P3 (item 9): T4, re-read `orphans` at #3471's merge before writing; its held count already separates some triage refs, and held by ruling must not count them twice.
- Carry: R10-TICK-RESIDUE-P3 (item 10): R1, the ancestor test needs the PR heads as local objects. Fetch them with git in one call; make no API read per PR.
- Carry: R10-TICK-RESIDUE-P3 (item 11): B1, `event` drops a line already in the file, so two refusals of the same op text need the occurrence key in the line, or the second is silent.
- Carry: R10-TICK-RESIDUE-P3 (item 12): B1, after carry 20 merges the local jobs override and its launch flag retire at the next beat restart; say so in the body for the orchestrator.
- Carry: R10-TICK-RESIDUE-P3 (item 13): X1, if no arm can go red without roster_edit.py:1215, carry 9 says the line is dead and is removed; report which.
- Carry: R10-TICK-RESIDUE-P3 (item 14): X2 (3), this note did not establish which set replan.py's open figure counts; measure it against the ledger rows before choosing the page's count.
- Carry: R10-TICK-RESIDUE-P3 (item 15): T2 (7b), this note did not read how many carries hold `start after #N`; enumerate them at the roster tip and name the count's command in the body.
