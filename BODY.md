Lands the last open arms of the roster-library routing invariants: a tick-level invariant line, an `append-carry` refusal of mark-shaped text, and the pin for the surviving M9 mutant. Carries 1-4 were already delivered by #3250.

Repair round: answers the fix-review block at `88690628b6feb50266cdcdb175b2a9c293db472a` (`roster_invariants` UNREADABLE guards survived their mutants T6 and T8). Two commits are added over the reviewed code head `e3d39d0d5c55eca3aa442765f6ef69f7d7ad51b6`. `58f2f02b611cea5841dccdb5f2b484624878983e` adds five tick self-test rows, "REPLAN routing invariants: an unreadable tool is never clean", and plants U1-U6 in `tools/audit/seat/r10_roster_ops_mutants.py`. `cddc8988f869131af4d9ea703ebc1bd1247d6963` makes that harness read an indented `  FAIL` line, which is how `orchestrator_tick.py` prints one; before this, every tick plant read as a survivor (`fails=0`, crash tail). No production line changed.

## Head

`0cfccb706dc42b2e9230c1053b2277e2345c895f` merges origin/main `daf8b349fd30cc60786eeca333a426b693aa4c5f` (tip at 2026-11-08T21:06Z) into `70f3b76c1a92b015a5f9b5dbf16f86a4ac3cd59a`, which itself merges origin/main `51cd5ec8a42abde3c223f22e9f4a0d5f35f8844a` into `cddc8988f869131af4d9ea703ebc1bd1247d6963`. Both merges were clean, and the second brings only `dev/programme/delivery/3346.md` and `tests/card_browser.mjs`, neither of which this diff reads. Every figure below was re-measured at `0cfccb706dc42b2e9230c1053b2277e2345c895f`, and `tools/pr/prepr.sh` was re-run there.

Carry 1: the fold; its four arms are carries 2-5 below.
Carry 2: covered by 87c2852eb (#3250); proving rows in roster_lib's self-test: "absorbed is closed: not open, and an after-edge on it clears", "an absorbed group is not in the open set or the dependency depth".
Carry 3: covered by 87c2852eb; carry_audit row "an absorbed destination is refused naming absorbed_into" (one set, `roster_lib.CARRY_CLOSED`).
Carry 4: covered by 87c2852eb; `roster_lib.gate_kind`, tick rows "REPLAN owner gates: only a decision not yet taken flags".
Carry 5: covered by 87c2852eb; plan_table, resume_doc and handover_prompt print one REFUSED line and exit 2 on a missing ref.
Carry 6: the detection is in the tool (`carry_audit.py roster --open-issues`, ISSUE-STRANDED) and is now run by the tick (below); which live group re-lists or closes the friction key's issue is a roster disposition by the orchestrator, not code, and waits on that ruling.
Carry 7: that issue is listed by R10-FRICTION-RECORDS (in-progress), so it is not unowned at this base.
Carry 8: same detection and the same waiting disposition as carry 6, for the sibling issues; they are held by live groups at this base.
Carry 9: (a) and (e) delivered here; (b) was already delivered (`roster_lib.closing_stage` rewrites only `done`); (c) and (d) delivered here.

## Fix review block answered

- T6 (`if rc not in (0, 1) or not summary:` -> `if False:`) and T8 (`except OSError` -> `except ZeroDivisionError: return`) survived at `88690628`. Each is now planted in-tree as U1 and U5, alongside U2 (the rc arm alone), U3 (the summary arm alone), U4 (the OSError branch silent) and U6 (a non-JSON `gh issue list` still passing `--open-issues`). Every one is killed at this head (see the mutation proof). The verdict's suggested non-JSON row is U6's row. Carry: built-here

## Mutation proof

- `python3 -I tools/audit/seat/r10_roster_ops_mutants.py U1 U2 U3 U4 U5 U6` at this head: `RESULT mutant=U1 rc=1 fails=3`, U2-U6 `rc=1 fails=1` each, `plants: 6, without a FAIL line: none`. The failing checks are "REPLAN routing invariants: an unreadable tool is never clean": "exit 2 with no summary (a REFUSED roster ref) is one UNREADABLE line" (U1), "exit 2 with a summary is still UNREADABLE (the rc arm alone)" (U1, U2), "exit 0 with no summary is UNREADABLE (the summary arm alone)" (U1, U3), "an OSError from the tool is one UNREADABLE line naming it" (U4, U5), "a non-JSON issue list drops --open-issues and still runs the roster call" (U6).
- U5 reproduces the reviewer's T8. The row's `ri_tick` catches an escaped OSError, so the mutant prints a FAIL line instead of crashing the self-test.
- From the previous round, still standing: removing the tick's `roster_invariants` call fails "REPLAN routing invariants at tick level". `r10_roster_ops_mutants.py W18` fails "append-carry refuses text ending in a mark-shaped suffix". `r10_roster_sync_mutants.py M9_carry_dedupe_dropped` fails "an item the destination holds verbatim is skipped silently".

## Null control

- I ran the same plants (`U1`-`U6`) at the previous code head `e3d39d0d5c55eca3aa442765f6ef69f7d7ad51b6`, with only this round's harness copied in. Every plant printed `rc=0 fails=0`, which means all survived and the block reproduces. So the new rows are what kill them.
- The harness's own self-test row "an indented FAIL line is read; an ok line naming FAIL is not" is the parser's null: an `ok` line that contains the word FAIL is not counted.
- A clean roster (`CARRY-ROSTER ... 0 stranded`) flags nothing (row "null: a clean roster flags nothing from the invariant").

## Figures

- `PYTHONPATH=tests/hastub python3 tools/audit/seat/orchestrator_tick.py --self-test`: 0 failed. The check count rose by the five new rows over the reviewed head's.
- `python3 -I tools/audit/seat/r10_roster_ops_mutants.py --self-test`: 0 failed. This includes anchor-once, changes-text and parses rows for each of U1-U6.
- `python3 tools/audit/seat/roster_edit.py --self-test`: 0 failed. `python3 tools/audit/seat/roster_sync.py --self-test`: 0 failed.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED`, and `scope.run` names `tests/entities.py`. `PYTHONPATH=tests/hastub python3 tests/entities.py`: ALL ENTITY CHECKS PASSED, rc 0 (the previous round's 3 workflow-probe failures do not reproduce in this container).

## Unpinned sites

`roster_invariants` is a `tools/` site outside the mutation-autofix lane. Its guards are pinned by the in-tree harness `tools/audit/seat/r10_roster_ops_mutants.py`, plants U1-U6. The call, the open-issues argument and the null are pinned by the tick self-test rows named above.

## Red checks

none

## Forward-carry

none

## Friction

none
