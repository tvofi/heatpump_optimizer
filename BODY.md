Triage batch 97 rules one re-home that the orchestrator s9 sent by message on 2026-11-01. R10-REPLAY-REAL-DAY handed off at `73ef64912` with four carries undone, because each one needs the owner's live diagnostics bundle and the replay export carries none of them. This is the rolling batch after batch 96, which was pushed first and left at its head.

- **P352: ACCEPT, as a re-home.**
  - Carries 3 and 8 (0-based) move to R10-ROUND-PLAYBOOK as one new carry, the round-11 D15 inputs. Carry 3 is lead L9's `unhealthy_input` read. Carry 8 is the R10-SCORES `--bundle` scale-drift run. Both source entries are marked `moved`.
  - Carry 5 restates carry 3, so it moves with it.
  - Carry 7 (D15 lead L6) is marked `dismissed`, because main already answers it. The self-test's input ages come from `inputs.state_stamp`, which has read `last_reported` first since `a1bdb11c1` (#775). `tests/features.py` check D1-s5-01 pins that (cells (5, 480) and (400, 400)).
  - No open round-10 group reads a bundle. R10-ROUND-PLAYBOOK is the roster's existing home for round-11 items. Holding the carries on R10-REPLAY-REAL-DAY would keep that group open past round 10's closure.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`8603d4637d21049f5f028e02dbc82e88a903640e`; the file is the whole diff against `8fec54ee2`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`. The gate was run with that tool and `roster_lib.py` at PR #3054's head, `361be3cd6`, which adds `mark-carry`, against the roster at `b3558fc7c`.
- On the committed file, `ruling_verdict` reads P352 as `ACCEPT`.
- `op_append_carry` accepts the carry on R10-ROUND-PLAYBOOK. All four `op_mark_carry` calls apply. `carry_mark` then reads `moved` at indices 3, 5 and 8 and `dismissed` at index 7, and leaves the other indices unmarked.
- `triage_refusal` over every added text returns None.
- With P352's verdict changed to `REJECT`, the ops are refused: `dev/programme/triage/s6-batch97.md#P352 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it: `the triage ruling dev/programme/triage/s6-batch97.md is not on the roster branch or origin/main`.
- `brief_lint.mjs` reports the same error lines on the roster before and after the five ops (an empty diff).

## Figures

- `handoff/r10-replay-real-day` = `73ef64912`. Its handoff body's carry list marks carries 4, 6, 8 and 9 (1-based) as "not done" for want of a live bundle.
- `git merge-base --is-ancestor a1bdb11c1 origin/main`: true. `a1bdb11c1` is dated 2026-09-11.
- R10-ROUND-PLAYBOOK has 17 carries on the roster branch at `b3558fc7c`.
- No capped file is touched.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
