Part 1 of 3 of R11-PRE-ACK-COMPLETION: builds carries 0-4 of the group's brief in `tools/audit/seat/orchestrator_tick.py` and its owed-family readers (carry 4 is built to carry 7's text, which supersedes it). The P14 acknowledgement-lifecycle work and carries 5-15 are later parts; none is answered here.

Carries built: Carry 0 is OUTSIDE-CHAIN-IDLE (`Tick.outside_chain_idle`); Carry 1 is the repair-discharges census; Carry 2 is the opener clause, OPENER ABSENT and held by ruling (`Tick.orphans`); Carry 3 is UNDISPATCHED (`Tick.undispatched`); Carry 4 is DESIGN-REVIEW OWED, built to carry 7's superseding text (`ledger.design_reviews_owed`).

## Head

b85164a43d5f9fa2c47df045257c73ca99df774c

(Round 2 repair of the Round 1 block `mutation-vacuous`: the code of 7caa9f561c is unchanged apart from tests in `orchestrator_tick.py --self-test` and `ledger.py --self-test`.)

## Mutation proof

Each mutant was applied to production lines, `python3 tools/audit/seat/orchestrator_tick.py --self-test` run, and the file restored:
- DESIGN-REVIEW OWED, dropping the dispatch-time clause (`if t in review_at and review_at[t] >= tip_at[t]` in `ledger.design_reviews_owed`): red "DESIGN-REVIEW OWED: null controls".
- DESIGN-REVIEW OWED, dropping the stage gate (`stage not in DESIGN_REVIEW_STAGES`): red, same arm.
- UNDISPATCHED, `SEATLESS_STAGES = UNBLOCKABLE_STAGES` (no stage widening): red "carries-open group ... prints the line" and "dispatch ref older than the gate opening is no seat".
- OUTSIDE-CHAIN-IDLE, stopping the walk after one edge (`if up and len(path) < 2`): 3 arms red, including the whole-path and null-control arms.
- OWED handoff opener state, removing the `held by ruling` replace: red; disabling the `OPENER ABSENT` branch: red.
- Census, dropping `UNDISPATCHED:` from `owed_unactioned.FAMILY`: red "every owed-family kind is armed or debt" and the key arm.
- A first draft of the seat-ref reader keyed topics on `ref.split("/", 2)[-1]`; the null-control arm (a dispatch ref newer than the gate) caught it before commit.

Round 2 (verdict/3635), driver `ev/mutant_driver.py` from that verdict, each mutant against the new tests, all KILLED:
- m6-dr-fetch-unreadable: red "a failed fetch of the design refs is UNREADABLE and owes no line".
- m25-dr-timeread-unreadable: crash `KeyError` in the self-test (nonzero); its assertion arm is "a failed commit-time read is UNREADABLE naming the sha", with null control "with both reads answering ... nothing is UNREADABLE".
- m24-dr-cp: red in both self-tests ("carries the CP mark"), null control: a group off the critical path prints none.
- m12-ud-cp: red "carries-open group ... prints the line" (now requires `UNDISPATCHED: CP R10-OI`), null control `UNDISPATCHED: R10-LATE`.
- m22-ledger-arm: the disposition arm now goes through `ledger.dispose`, which raises `Refused` without the arm; ledger self-test classifies `refs/heads/design/x`.
- m23-ud-wipseat: ls-remote in a new `SeatStub` answers only refs the argv patterns match; one fresh ref in each of the five SEAT_REFS families must silence the group; null control a `probe/` ref does not.
- m16-op-stuck3: `_opener_last` driven at n=1, 2, 3; no STUCK below three.

## Null control

At the base (`origin/main` 98847b99d7) none of the five lines exists: `git grep -n "UNDISPATCHED:\|OUTSIDE-CHAIN-IDLE\|DESIGN-REVIEW OWED\|OPENER ABSENT" 98847b99d7 -- tools/audit/seat` returns nothing, and the base self-test reports 319 checks, 0 failed. Each new arm carries its own null control: a verdict at the tip, a reviewer dispatched after the tip, a done group and a disposition at the tip's sha print no DESIGN-REVIEW OWED; a group held behind an unfinished `after` group, a seat ref newer than the gate opening and a non-carries-open group print no UNDISPATCHED; a path ending in a seat ref inside SEAT_WINDOW_MIN and a non-outside group print no OUTSIDE-CHAIN-IDLE; an all-clear bus prints no OPENER ABSENT with no state directory.

Design choices: (1) a design-tip disposition is recordable because `ledger.ARMS` gains `refs/heads/design/` with the derived kind `design-review` (a disposition needed a ref the ledger classifies); (2) the group-level UNDISPATCHED line covers `carries-open` groups (a) and any open group whose pending carry reads `start after #N` with #N merged (b), and leaves a not-started group to the existing UNBLOCKED line rather than printing two flagged lines for it; (3) the opener's state is read from `<state dir>/open-driver/` (`open-driver.log`, `fails.json`) and never written; (4) carry 2's "counted, never silently capped" and the held-last ordering already stood at the base (`CAP_ORPHANS` line counts its held refs), so only the opener clause, OPENER ABSENT and the `held by ruling` wording were added; (5) carry 1's barrier is a census over `owed_unactioned.FAMILY`, the one list of lines an operator is told to repair, with each kind ARMED or named DEBT. A source scan of every `flag=True` site was rejected: 19 sites have a dynamic prefix, so a new kind would hide in that bucket.

## Figures

- `python3 tools/audit/seat/orchestrator_tick.py --self-test`: 365 checks, 0 failed at b85164a43d5f9fa2c47df045257c73ca99df774c (base: 319 checks, 0 failed).
- `python3 tools/audit/seat/owed_unactioned.py --self-test`: 60 checks, 0 failed; `python3 tools/audit/seat/ledger.py --self-test`: 108 checks, 0 failed; `python3 tools/audit/seat/beat_jobs.py --self-test` (the real entry; `beat_jobs_selftest.py` runs nothing).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, no metric moved (none of the changed files is measured).
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: MODE: SCOPED, scripts `tests/doc_claims.py` and `tests/entities.py`; doc_claims 410 checks passed.
- Seams enumerated for carry 1: `python3 -c "import re,sys; sys.path.insert(0,'tools/audit/seat'); import owed_unactioned as o; print(re.match(r'\^-> \((.*)\)$', o.FAMILY.pattern).group(1).split('|'))"` lists 13 kinds; 4 are armed here (OWED, DESIGN-REVIEW OWED:, UNDISPATCHED:, DESIGN-BUILD:), 9 are DEBT (REVIEW OWED:, RECORD-OWED:, DISPATCH:, OWNER FLAG:, MERGE-READY:, BLOCKED-UNFIXED:, APPROVAL-OWED:, UNLEVELLED:, REVIEW STALLED:). The census fails on a kind in neither set.
- The finder's harness is a recorded case, not a script: DESIGN-REVIEW OWED's measured replay (three groups at 2026-11-11T05:06Z) needs the live remote refs of that instant, which this container cannot reproduce; the self-test's revise-verdict, old-dispatch and newer-tip fixture is its stand-in.

Carries not built in this part (parts 2 and 3 build them, none is answered here): Carry 5, Carry 6, Carry 8, Carry 9, Carry 10, Carry 11, Carry 12, Carry 13, Carry 14, Carry 15, Carry 16, Carry 17.

## Red checks

none

## Forward-carry

- dev/programme/rosters/wave-r10-groups.json (group R11-PRE-ACK-COMPLETION, parts 2 and 3): the 9 DEBT kinds of carry 1's census need their own repair-discharges arms. Carry: R11-PRE-ACK-COMPLETION
- dev/programme/rosters/wave-r10-groups.json (group R11-PRE-ACK-COMPLETION, parts 2 and 3): `UNDISPATCHED` does not print for a not-started group (UNBLOCKED already does); whether UNBLOCKED should read the seat refs is the same seam as carry 3 (a) and is left to a later part. Carry: R11-PRE-ACK-COMPLETION

- OUTSIDE-CHAIN-IDLE and the flagged OPENER ABSENT line are not in `owed_unactioned.FAMILY`, so the census and `owed_unactioned.py` do not see them (verdict follow-up). Carry: R11-PRE-ACK-COMPLETION

## Friction

none
