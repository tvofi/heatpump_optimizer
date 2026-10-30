R10-FLOW-DESIGN-STAGES part 2 (topic r10-flow-design-stages-p2): `tools/audit/seat/cloud_dispatch.py` renders a published stub that pins PROMPT.md by commit SHA (item A), and a group's dispatch briefs the seat with its `After:` groups and every roster carry (item B), with the carries the dispatch owes the fixer, reviewer and setup line (5, 6, 7, 9, 12, 13, 15, 17) and one mutant per design arm #2994 merged. Part 1 is already on main; this part closes no issue by itself (the group's issues stay open for the remaining items).

Alternatives considered: inlining the whole prompt in the trigger event (the pre-change behaviour, resent whole on every trigger update) lost to the stub; pinning the ref's tip instead of PROMPT.md's commit lost because a re-dispatch would move what a running seat reads. The stub is committed as PROMPT.md alone and PAYLOAD.json on top, since a commit cannot name its own SHA.

## Head

ee13ac5fc94b0ad1c813e58f5136772df4026657 (code head `handoff/r10-flow-design-stages-p2`: the original handoff 9256af6a0 plus a clean merge of origin/main cc930cdd1, taken 2026-10-30; the merge touches no file of this diff).

## Mutation proof

Each mutant is a one-occurrence replacement of a production predicate in `tools/audit/seat/cloud_dispatch.py`, applied alone, the self-test run, the file restored.
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_dispatch-1 .. cloud_dispatch-20`: 20 KILLED, survivors=0 (pin by tip, footer ban dropped, parent return dropped, pin check off, carries dropped, step ref, step-ref delete, pre-handoff merge, identity pin, CI waiter, setup check, model ruling x2, design bypass, approval read, moved-design approval, L/XL gate, absent design, design-reviewer pin, design topic).
- `python3 dev/audit/harnesses/r10_flow_dispatch_mutants.py`: M0 failed=0 (null control), 33 mutants, survived=0; six CRASHED (parent-drop, topic-to-id, head-ignored, roster-repo-ignored, fetch-skipped, pointer-off) are killed by a self-test that died before its summary, not survivors. `wait-line-dropped` is re-aimed at the reflowed setup line and killed (failed=1).

## Null control

The unmutated tree: `cloud_dispatch.py --self-test` prints `124 checks, 0 failed`, and the flow-dispatch harness's M0 prints `failed=0`. The inlined (unpublished) render is byte-identical to before the stub; the stub payload is under 1 KB at the real repository name.

## Figures

- `python3 tools/audit/seat/cloud_dispatch.py --self-test` : 124 checks, 0 failed at the head.
- `python3 tests/entities.py` : ALL ENTITY CHECKS PASSED.
- `python3 tests/structure.py` : STRUCTURE RATCHET PASSED.
- `bash tools/pr/prepr.sh` : exit 0, MODE: SCOPED, scope.run = tests/entities.py.
- `python3 dev/audit/harnesses/r10_flow_dispatch_mutants.py` : survived=0.
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_dispatch-1` : KILLED (see Mutation proof for the full list).

## Red checks

none

## Forward-carry

none beyond the group's remaining items, which stay in the roster's R10-FLOW-DESIGN-STAGES brief. Carry: R10-FLOW-DESIGN-STAGES

## Friction

none
