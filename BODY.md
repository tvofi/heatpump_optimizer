Triage batch 71 rules the orchestrator's queue line 18 (2026-10-30T12:34:42Z, slip class): `roster_edit.py set-stage <G> done` after a merge closed groups that still own carries and open wired issues, so owed work dropped out of replan and dispatch. It is the next rolling batch under V182, after batch 70 (#2987). It holds one ruling and one held roster op.

- **P305: ACCEPT as already carried, narrowed.** R10-ORCH-ROSTER-SCHEMA has held this class's barrier since 2026-10-24: #2733's routing invariants and their undelivered remainder (`mark-carry`, a STRANDED report, and `roster_sync` writing `carries-open` instead of `done`). None of it is built: `mark-carry` is absent from `tools` at main.
  - One amendment carried: `set-stage done` applies the same `carries-open` downgrade through one predicate shared with `roster_sync`. The remainder is asked to dispatch alone, first.
  - The filing's set-stage refusal with `--force-done` is REJECTED. #2733's design rules out a set-stage refusal, and without `mark-carry` a refusal cannot tell a delivered carry from a pending one, so `--force-done` would become routine.
  - Five groups in round 10: R10-UX-HEALTH (4 open issues), R10-COP-PARTLOAD (#2501) and R10-ORCH-BEATD (#2505) read `done` now. R10-TRAIN-OVERLAP-GRADE and R10-COP-GATE were repaired by hand to `carries-open`, and TRAIN-OVERLAP-GRADE has six set-stage commits since 2026-10-28.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`4794c840bc78844d07e9824123dfc46aa3697595`; the file is the whole diff against `507a9ec26`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P305 as `ACCEPT`. `triage_refusal` passes the carry text, which cites `triage: dev/programme/triage/s6-batch71.md#P305`: it returns None.
- With `Verdict: ACCEPT` changed to `Verdict: REJECT`, the same carry is refused: `dev/programme/triage/s6-batch71.md#P305 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve: `the triage ruling dev/programme/triage/s6-batch71.md is not on the roster branch or origin/main`.

## Figures

- `gh issue view <n> -R tvofi/heatpump_optimizer --json state` gives OPEN for 2263, 2499, 2809, 2815, 2501, 2262 and 2505, and CLOSED for 2253, 2260 and 2725.
- `git log origin/handoff/audit-r10-roster` lists set-stage commits `c3a7bfd9a` (R10-UX-HEALTH), `d920e6bec` (R10-COP-GATE) and `968e9c423` (R10-TRAIN-OVERLAP-GRADE), all on 2026-10-30, plus six for R10-TRAIN-OVERLAP-GRADE since 2026-10-28.
- `git grep -ci mark-carry origin/main -- tools` prints nothing.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
