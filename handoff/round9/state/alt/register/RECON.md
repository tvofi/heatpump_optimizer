# R1–R7 survivors vs rows_v2.tsv

Sources: the register (`5a2a62ff:docs/audit-2026-09.md`), the round-3 ledger, the round-4 judge verdicts, and all 648 issues. Round 5 has no register in any commit, so its issues are the only record.

| round | survivors | rows_v2 | invalid in rows_v2 | missing |
|---|---|---|---|---|
| R1 | 60 | 42 | 2 (D3-01 refuted; D8-02 double-counts M2 with D1-04) | 20 |
| R2 | 78 (75, plus judge-found #291, #310, #325) | 63 | 0 | 15 |
| R3 | 44 (D0-01/02 split, as rows_v2 does) | 35 | 0 (the D0 split may double-count) | 9 |
| R4 | 43 (42, plus OWNER-01) | 36 | 0 | 7 |
| R5 | 82 (47 from `1cc89e0`, 35 from `eaa2a06`) | 48 | 1 (#1293 refuted after filing) | 35 |
| R6 | 31 | 30 | 0 | 1 |
| R7 | 32 (31, plus fixer sweep #1487) | 31 | 0 | 1 |
| **total** | **370** | 285 | 3 | **88** |

Check: 285 − 3 + 88 = 370. For R1 the register says 59, because it counts D7-06 as killed; the dead-symbol half survives as #178.

## Why findings.tsv omitted them

classes.md says the gap is merged duplicate rows. That is false: none of the 88 is a merge. Its 321 headline is copied from the register, but its rows skip whole groups:
- **R1:** tail rows of each table, including D8-03 (#174) and seven D10 rows. No rule explains the choice.
- **R2:** the D10 rows marked fixed-since-baseline or corroborating, and D4-09..12. The judge-found issues were never in the register table.
- **R3:** the three D4 rows (panel votes only), R3-INSTRUMENT, D7-02, D6-03 and D10-01/03/04.
- **R4:** the four `-INST` rows (carried by RESUME.md, not the index), D4-03, D3-S4 (dropped as an equivalent mutant) and OWNER-01.
- **R5:** the source was #1293–#1340 only. The earlier `eaa2a06` run (#1207–#1241) has no prefix or label.
- **R6:** D0-01, with no reason given.
- **R7:** #1487, which is not in the register.

The zcode session's round-2 D10 run (#216–#218) only duplicates R2 D10-03, D10-09 and D10-12. It is in `excluded.tsv`.

## Added per class

| class | rows |
|---|---|
| I1 | 18 |
| _unclassified | 15 |
| I5 | 11 |
| I3 | 7 |
| P2 | 6 |
| I4, P9 | 5 each |
| P1, P4 | 3 each |
| N-name-sort, P5, P11, I2, P6, P3 | 2 each |
| N-structure-blind, P8, N-solve-recompute | 1 each |

The `_unclassified` rows are mostly HA quality-scale or typing conformance, following the A1 flags.

## Confidence

46 high, 30 med, 12 low. The low ones are:
- R2 D10-06, D10-07 and D10-11, re-reports of R1 findings fixed before the R2 baseline. I kept them because rows_v2 keeps R2 D10-01, the same kind of row.
- Weak class fits: R1 D4-08, D10-05, D10-09, D10-11; R2 D4-12; R3 D4-03; R4 D3-INST, D9-INST, OWNER-01.

Unresolvable: the `1cc89e0` numbering gaps (D0-02, D1-01..04, D9-01..04) and any unfiled `eaa2a06` findings. No verdict record exists for either.
