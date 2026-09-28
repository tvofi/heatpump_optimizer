# Bug-class register v2: rounds 1–9 enumerated, classified and folded

Built 2026-09-28 against origin/main `3490cb16`, and proposed as the replacement for `tools/audit/bugclasses.json`.
Every count below is derived by `build_v2.py` from `rows_v2.tsv`. `python3 build_v2.py --check` rebuilds everything
and exits 1 on any drift.

## Why

RCA-1736 showed that the register counts across rounds but never received a round-8 member. Its round-9 members
reached only the classes that got a barrier. The phase-A1 enumeration measured the rest:

- At main, 186 register rows sit in no class: 39 from R8, which was never classified, and 147 from R9.
- The R9 judge re-minted 20 of its 31 "new" classes for mechanisms the register already had.
- It split mechanisms below 3.
- P4, P7, P8, P10 and I2 recurred for rounds and never got an RCA.

## What changed from v1

**Scope:** 486 rows (R1 42, R2 63, R3 35, R4 36, R5 48, R6 30, R7 31, R8 39, R9 162).
- R1–7 are the 285 rows of the round-8 classification's `findings.tsv`, and every v1 member is kept.
- R8 is classified for the first time.
- R9 covers 145 judged findings plus the instances the fix plan counted beyond them.

**Counting rule:**
- An instance is a judged survivor, or an instance a sweep, RCA or fixer seat found beyond the judged site.
- Sweep seams that are the judged site itself are dropped.
- Incident- and screen-found members are listed under `non_round_instances` and not counted.
- The two RCA-seat-found counts differ from the sweep-only ones for P9 (12 vs 5) and N-solve-recompute (7 vs 5). `a1-src/derive.out` prints both.

**Reclassifications:** 40 rows, each recorded in its row's `move` column.
- 37 are the enumeration's flags: moves between classes, reasoned per row.
- 3 are RCA-seat moves from RCA-BULK-2: I2's D3-FLAKE is a timing flake, and R5-INST-01 and R7-INSTR-01 are hand-typed dimension lists, now I4.
- 7 rows fit no mechanism class and sit in `_unclassified` with their reason: coordinator size, HA quality-scale code conformance, recorder payload, and the flake.

**Class merges and re-maps:**
- 21 of the R9 judge's 31 new classes map onto existing ids; each R9 id is kept as an alias.
- Merges:
  - dead-member with structure-blind;
  - the three translation/icon classes with N-markdown into I5;
  - dup-entity, availability, late-try and menu into P2;
  - plausibility, min-gap and service-clamp into P1;
  - sign-floor, euler-coupled and clamp-range into P3;
  - N-loop-cpu into P10;
  - N-cpu-gate-blind into I1;
  - N-fit-integrator into P5.
- The reasons are in `reclassifications.md`.

**New ids (10):**
- N-solve-recompute, N-structure-blind, N-name-sort, N-shared-config (the RCA-1736 class), N-approval-rebuy, N-finally-return, N-step-grid, N-reap-lock and N-staleness each carry `nearest_existing` and `mechanism_difference`.
- N-silent-zero is the cross-cutting class from #1041, re-run by RCA-BULK-3. Its members count under their own classes and are listed in `members_elsewhere`.
- The `class_guess` enum in `finding.schema.json` moves in the same PR (`finding.schema.class_guess.json`), as `check-wave-script.mjs:730-737` requires.

**New fields:** `per_round`, `total`, `max_per_round`, `aliases`, `rca` (ids into `_rca`), `rca_planned` (roster groups), and `trigger` (per-round, cross-round, barriered, class RCA on record). v1's `rounds` and `instances` (as `R<n> <id>` strings) are kept, so every existing reader works unchanged.

**Top level:**
- `_rca` indexes all 94 RCAs: class, level, trigger, status, the parts missing, the countermeasure, where it landed, where the doc is, and its in-tree home.
- `_unclassified`.
- `_counting`.

**Class text the bulk RCAs changed:**
- P4: `status: detector`, with the solve certificate and the recorded refusal.
- P7: `barrier_gap`, two measured blind spots of F1.1's tracer.
- P8: a new `detector_idea`.
- P10: the mechanism widened to CPU work outside the process worker.
- I2 and N-structure-blind: new `detector_idea`s.
- N-shared-config: the m1 enumerator, plus the screen members.

## The classes

| class | kind | total | max/round | per round | status | RCAs on record | barrier owed by |
|---|---|---|---|---|---|---|---|
| P1 | production | 30 | 16 | R1:2 R2:2 R3:1 R4:2 R5:3 R6:2 R8:2 R9:16 | open | R9-P1, RCA-R8-P1 | R9-F1.6 |
| P2 | production | 60 | 27 | R1:5 R2:7 R3:2 R4:2 R5:4 R6:2 R7:4 R8:7 R9:27 | open | R9-P2, RCA-1499, RCA-R8-P2 | R9-F1.11 |
| P3 | production | 22 | 6 | R2:4 R4:4 R5:2 R6:4 R7:1 R8:1 R9:6 | open | R9-P3, RCA-R8-P3, RCA-coil-drain | R9-F1.10 |
| P4 | production | 16 | 3 | R1:2 R2:3 R3:2 R4:2 R5:3 R6:1 R7:1 R8:1 R9:1 | detector | BULK-1-P4 | R9-F2.4 |
| P5 | production | 21 | 6 | R1:2 R2:2 R3:3 R4:2 R5:3 R6:1 R7:1 R8:1 R9:6 | barriered | R9-P5, RCA-1525, RCA-R8-P5-1523 | — |
| P6 | production | 21 | 5 | R1:5 R2:5 R3:2 R4:1 R6:1 R7:2 R8:1 R9:4 | open | R9-P6, RCA-R8-P6-1526 | R9-F1.11 |
| P7 | production | 4 | 1 | R2:1 R3:1 R5:1 R9:1 | barriered | BULK-1-P7 | R9-F10.1c |
| P8 | production | 7 | 2 | R1:1 R4:2 R7:1 R8:1 R9:2 | open | BULK-1-P8, RCA-R8-P8-1513 | R9-F1.8 |
| P9 | production | 32 | 12 | R1:4 R2:8 R4:1 R5:3 R6:1 R7:2 R8:1 R9:12 | open | R9-P9, RCA-R8-P9-1522 | R9-F6.3 |
| P10 | production | 7 | 2 | R1:1 R2:1 R3:1 R5:1 R6:1 R9:2 | open | BULK-1-P10, BULK-3-v660-freeze, PRE-70-v511-freeze | R9-F1.7, R9-F10.7 |
| I1 | instrument | 65 | 14 | R1:8 R2:11 R3:6 R4:4 R5:9 R6:6 R7:2 R8:5 R9:14 | open | R9-I1, R9-N-cpu-gate-blind, RCA-1336-d9-memory-arm, RCA-1485-ledger-line-shift, RCA-1595-nan-ratchets, RCA-R8-I1a-kill-rule, RCA-vacuous-acceptance-arm | R9-F10.2, R9-F10.3 |
| I2 | instrument | 5 | 2 | R2:1 R5:2 R8:1 R9:1 | open | BULK-2-I2 | R9-F10.3 |
| I3 | instrument | 31 | 7 | R2:1 R3:4 R4:6 R5:2 R6:2 R7:3 R8:6 R9:7 | barriered | R9-I3, R9-RC1-pinned-local, RCA-1514, RCA-1515, RCA-1567-unpinned-installs, RCA-1589-policy-docs-red, RCA-R8-I3-1516 | — |
| I4 | instrument | 21 | 8 | R4:1 R5:4 R6:3 R7:8 R8:1 R9:4 | open | R9-I4 | R9-F11.4 |
| I5 | instrument | 82 | 25 | R1:7 R2:12 R3:9 R4:7 R5:8 R6:5 R7:3 R8:6 R9:25 | open | BULK-3-1545, R9-I5, RCA-1546, RCA-R8-I5b | R9-F10.4 |
| N-future-instant | production | 9 | 8 | R3:1 R9:8 | barriered | R9-N-future-instant | — |
| P11 | production | 6 | 6 | R9:6 | barriered | BULK-3-1721, R9-P11, V6612-bug1-6-ownership, V6612-bug2-lease, V6612-bug3-4-echo, V6612-bug5-switch, V6612-bug7-card-history, V6612-listener-callback | R9-F11.7 |
| N-restart | production | 3 | 2 | R3:1 R9:2 | barriered | PRE-1249-picker-revert, R9-1638-clobbered-store, R9-RC2-bug5-reboot | — |
| N-solve-recompute | production | 13 | 7 | R1:1 R2:1 R4:1 R5:1 R7:1 R8:1 R9:7 | open | R9-N-solve-recompute | R9-F10.2 |
| N-structure-blind | instrument | 9 | 4 | R2:1 R6:1 R7:1 R8:2 R9:4 | open | BULK-2-N-structure-blind | R9-F10.4 |
| N-name-sort | production | 6 | 2 | R2:1 R3:1 R4:1 R5:2 R9:1 | open | — | — |
| N-shared-config | production | 4 | 2 | R2:1 R8:2 R9:1 | open | R9-RCA-1736, RCA-R8-P12-1517-1529 | R9-EG-B9, R9-EG-B10, R9-EG-B1 |
| N-approval-rebuy | instrument | 1 | 1 | R9:1 | open | — | — |
| N-finally-return | instrument | 1 | 1 | R9:1 | open | — | — |
| N-step-grid | production | 1 | 1 | R9:1 | open | — | — |
| N-reap-lock | production | 1 | 1 | R9:1 | open | — | — |
| N-staleness | production | 1 | 1 | R9:1 | open | — | — |
| N-silent-zero | instrument | 0 | 0 |  | open | BULK-3-1041-rerun, RCA-1041-silent-zero | R9-F11.4 |

## Trigger evaluation (`trigger.out`)

```
class                total maxR  per-round cross-round barriered  class-RCA  owed-and-missing
P1                      30   16  True      True        False      True       
P2                      60   27  True      True        False      True       
P3                      22    6  True      True        False      True       
P4                      16    3  True      True        False      True       
P5                      21    6  True      True        True       True       
P6                      21    5  True      True        False      True       
P7                       4    1  False     False       True       True       
P8                       7    2  False     True        False      True       
P9                      32   12  True      True        False      True       
P10                      7    2  False     True        False      True       
I1                      65   14  True      True        False      True       
I2                       5    2  False     True        False      True       
I3                      31    7  True      True        True       True       
I4                      21    8  True      True        False      True       
I5                      82   25  True      True        False      True       
N-future-instant         9    8  True      True        True       True       
P11                      6    6  True      True        True       True       
N-restart                3    2  False     False       True       True       
N-solve-recompute       13    7  True      True        False      True       
N-structure-blind        9    4  True      True        False      True       
N-name-sort              6    2  False     True        False      False      OWED
N-shared-config          4    2  False     True        False      True       
N-approval-rebuy         1    1  False     False       False      False      
N-finally-return         1    1  False     False       False      False      
N-step-grid              1    1  False     False       False      False      
N-reap-lock              1    1  False     False       False      False      
N-staleness              1    1  False     False       False      False      
N-silent-zero            0    0  False     False       False      True       
owed and missing a class RCA: ['N-name-sort']
unclassified rows: 7; RCAs indexed: 94
```

- The per-round arm is the rule in force.
- The cross-round arm is the proposed clause: ≥3 over any 3 consecutive rounds, or ≥5 total while open. It is owner-gated in R9-EG-R1.
- Every class that fires under either arm now has a class-level RCA on record, **except N-name-sort**. Its RCA (RCA-BULK-4) was conducted in this pass and is indexed on landing.

## Owner review before R9-EG-R0 merges

1. **The 40 moves** (`rows_v2.tsv`, `move` column) and the low-confidence placements (the `confidence` column), which are:
   - R8 D2-s2-01 → P3;
   - N-euler-coupled and N-clamp-range → P3;
   - N-min-gap and N-service-clamp → P1;
   - N-step-grid, N-reap-lock and N-staleness as new ids;
   - P9-f61a..c, whose seams no document names.
2. **P1's mechanism text** ("persisted-store boundary") no longer fits its members, which cross live-input, feed and service boundaries. Either widen it (the `mechanism_note` proposes wording) or mint an input-boundary class and move about 8 rows.
3. **P2 (60) and I5 (82) are catch-alls.** Their detector ideas miss most of their members. Split them along what a detector can check, in a later round.
4. **Whether RCA-seat-found instances count.** The rule says "sweep-confirmed"; v1 and the fix plan also count RCA-found ones. v2 counts them.

## Landing (R9-EG-R0) and the mechanism (R9-EG-R1)

- **R0 is a data PR, with no policy and no budget.** It replaces `tools/audit/bugclasses.json` with `bugclasses.v2.json`, moves the enum, and adds `tools/audit/rca/` (INERT, outside `POLICY_GLOBS`) with the 14 round-9 class RCAs from `763b0ba4`, RCA-1736 and RCA-BULK-1..4.
- **R1 is the permanent fold**, specified in RCA-BULK-2 §3.4 and on the R0/R1 issue. It adds `tools/audit/fold_ledger.py`, run by `audit-verify.js`, and its `--check`. The policy clauses go to tvofi.
