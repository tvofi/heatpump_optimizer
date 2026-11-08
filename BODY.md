Lands the last open arms of the roster-library routing invariants: a tick-level invariant line, an `append-carry` refusal of mark-shaped text, and the pin for the surviving M9 mutant. Carries 1-4 were already delivered by #3250.

## Head

e3d39d0d5c55eca3aa442765f6ef69f7d7ad51b6 (cut from origin/main 73365699a; main unmoved at handoff of this body, no second prepr run).

Carry 1: the fold; its four arms are carries 2-5 below.
Carry 2: covered by 87c2852eb (#3250); proving rows in roster_lib's self-test: "absorbed is closed: not open, and an after-edge on it clears", "an absorbed group is not in the open set or the dependency depth".
Carry 3: covered by 87c2852eb; carry_audit row "an absorbed destination is refused naming absorbed_into" (one set, `roster_lib.CARRY_CLOSED`).
Carry 4: covered by 87c2852eb; `roster_lib.gate_kind`, tick rows "REPLAN owner gates: only a decision not yet taken flags".
Carry 5: covered by 87c2852eb; plan_table, resume_doc and handover_prompt print one REFUSED line and exit 2 on a missing ref.
Carry 6: the detection is in the tool (`carry_audit.py roster --open-issues`, ISSUE-STRANDED) and is now run by the tick (below); which live group re-lists or closes the friction key's issue is a roster disposition by the orchestrator, not code, and waits on that ruling.
Carry 7: that issue is listed by R10-FRICTION-RECORDS (in-progress), so it is not unowned at this base.
Carry 8: same detection and the same waiting disposition as carry 6, for the sibling issues; they are held by live groups at this base.
Carry 9: (a) and (e) delivered here; (b) was already delivered (`roster_lib.closing_stage` rewrites only `done`); (c) and (d) delivered here.

## Mutation proof

- Tick line: `roster_invariants` call removed -> `orchestrator_tick.py --self-test` fails "REPLAN routing invariants at tick level".
- `r10_roster_ops_mutants.py W18` (append-carry refusal dropped) -> roster_edit self-test FAIL "append-carry refuses text ending in a mark-shaped suffix".
- `r10_roster_sync_mutants.py M9_carry_dedupe_dropped` -> FAIL "an item the destination holds verbatim is skipped silently" (at main the same mutant ended rc=0, fails=0).

## Null control

A clean roster (`CARRY-ROSTER ... 0 stranded`) flags nothing (row "null: a clean roster flags nothing from the invariant"). At main, `python3 tools/audit/seat/r10_roster_sync_mutants.py M9_carry_dedupe_dropped` printed `RESULT ... rc=0 fails=0`, i.e. survived.

## Figures

- `python3 tools/audit/carry_audit.py roster` at the merge base reports one stranded carry (R10-FLY-GANTT-DRIFT, absorbed); data, left to the orchestrator's roster op, not edited here.
- `PYTHONPATH=tests/hastub python3 tools/audit/seat/orchestrator_tick.py --self-test`: 0 failed.
- `python3 tools/audit/seat/roster_sync.py --self-test`: 0 failed. `python3 tools/audit/seat/roster_edit.py --self-test`: 0 failed.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Mutant run: MUTANT_CMD unset (report-only step skipped); the three named mutants above were run by hand, 0 survivors.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` (counts the ENTITY CHECKS FAILED line; null: the baseline checkout prints the same line): 3 fail in this container and 3 of 2665 at the baseline checkout (workflow-probe checks, not touched by this diff); left to CI.

## Unpinned sites

`roster_invariants` is a `tools/` site outside the mutation-autofix lane; pinned by the tick self-test rows above (the call, the open-issues argument, the null).

## Red checks

prepr.sh step `closures` REFUSES in this container: `tests/entities.py` exits 1 on 3 workflow-probe checks (coverage-cache key, release ZIP build, Pages probe), which the baseline checkout also fails (same ENTITY CHECKS FAILED line); the diff touches no workflow file. Left to CI. No other prepr step refuses at this head.

## Forward-carry

none

## Friction

none
