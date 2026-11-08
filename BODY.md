The 1-based "Carry N" numbers here are the packet's (roster array index N-1). The waste-study ruling (cards 3 and 7) is Carry 18 in that numbering ("Carry 17" in the orchestrator's 0-based wording): `bus.sh dispatch` reads a required-context RED as a repair owed to the fixer, not a refusal a retry loop re-tries. A WAIT head still dispatches and only RED holds. Part 2 also carries the two earlier `review_packet.py` commits already on this branch (head-note asks `policy_lint --pr-body --head`; the packet refuses a figure_lint red and a moved head).

Ruling cited: orchestrator ruling (mandate 6715477401, 2026-11-08): "a PENDING (queued or in-progress) required context does NOT hold a dispatch; WAIT dispatches, only RED holds." That supersedes the brief's pending ruling. Carry 7 (the 0-based "6"; hold on a pending required context) is therefore closed as superseded by this ruling and not built. Card 7's WAIT-dispatches arm is already the code (`0|3) ;;`) and is pinned by the existing "classify WAIT dispatches" self-test arm; I changed nothing there.

Pending a ruling, not built here: Carries 1, 5, 9, 12 and 13 (0-based 0, 4, 8, 11, 12) (BLOCKED.md of 07:31Z listed them as waiting on an owner or orchestrator ruling). Carry 7 vs 18 (0-based 6 vs 17): resolved as above.

## Head

092a333d577dbc28e390e8e0979d67b63d9cd9c7

## Mutation proof

Mutant: `exit 5` changed to `exit 1` in the RED arm of `bus.sh dispatch`. `bash tools/audit/seat/bus.sh --self-test` then fails "a head whose required context concluded failure (classify RED) is not dispatched, owes its fixer a repair (rc 5, REPAIR-OWED, no REFUSE), and nothing is recorded". Restored, the arm passes. Failing-first was done in one step: the arm asserts rc 5, the `REPAIR-OWED` prefix and no `REFUSE`, which the old `die` (rc 1, `bus: REFUSE:`) could not satisfy.

## Null control

The same self-test keeps the null arms: classify GREEN mints and records, WAIT (rc 3) dispatches, APPROVAL-OWED dispatches, unreadable (rc 2) still refuses with `REFUSE`. A head whose only red is non-required classifies GREEN (classify reads the required set through merge_train.py), so it dispatches; non-required reds never bounce. Environment control: `tests/entities.py` at origin/main in this container fails the same three checks as BLOCKED.md named (coverage job reuse, release ZIP root, Pages tag probe), so they are environment and not this diff's.

## Figures

- `bash tools/audit/seat/bus.sh --self-test`: 159 checks, 1 failed at this head. The one failure ("an ordinary append with no intervening fetch is the same commit object as before") reproduces at origin/main; named, not fixed here.
- `PREPR_SKIP_CLOSURES=1 MUTANT_CMD="bash tools/audit/seat/bus.sh --self-test" bash tools/pr/prepr.sh`: rc=0 at this head. Origin/main had not been merged; per the owner ruling of 2026-11-07 I handed off at the first clean head.
- `tests/entities.py` at origin/main: `python3 tests/entities.py > /tmp/ent_main.log; echo rc` gave rc=1 with the three environment checks above among its FAIL lines.
- Diff-mutant step: it printed "BASELINE FAILS: the command fails on the unedited tree; no mutant was run", because the bus self-test baseline carries the one pre-existing failure above. Survivor count 0 (none run); mutant wall time not applicable.

## Unpinned sites

The changed `bus.sh` lines are pinned by the manual mutation above (the `exit 5` predicate). The automated diff-mutant run could not baseline, for the reason in Figures.

## Carry dispositions

- Carry 1: pending a ruling, not built (re-key, held-verdict relay).
- Carry 2: delivered at main by an earlier PR, no re-fix (survey of afc1586a4).
- Carry 3: delivered at main, no re-fix.
- Carry 4: delivered at main, no re-fix.
- Carry 5: pending a ruling, not built.
- Carry 6: delivered at main, no re-fix.
- Carry 7: closed as superseded by the orchestrator ruling cited above; not built.
- Carry 8: delivered at main, no re-fix.
- Carry 9: pending a ruling, not built.
- Carry 10: delivered at main, no re-fix.
- Carry 11: delivered at main, no re-fix.
- Carry 12: pending a ruling, not built.
- Carry 13: pending a ruling, not built.
- Carry 14: delivered at main, no re-fix.
- Carry 15: delivered at main, no re-fix.
- Carry 16: delivered at main, no re-fix.
- Carry 17: built on this branch (review_packet.py head-note asks policy_lint --pr-body --head, P405).
- Carry 18: built here, cards 3 and 7 (REPAIR-OWED on RED; WAIT dispatches).

## Red checks

none

## Forward-carry

none

## Friction

none
