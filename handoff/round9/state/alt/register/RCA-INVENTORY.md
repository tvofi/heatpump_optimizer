# RCA inventory: every root-cause analysis conducted, where it is recorded, and what is still owed

Measured 2026-09-28 at origin/main `3490cb16`.
- Rows: `rca_inventory.json` (conducted) and `rca_scheduled.json` (scheduled or owed).
- The register indexes every row under `_rca` in `bugclasses.v2.json`.
- Built by `a1-src/rca_inventory_build.py`.

**94 RCAs indexed:**
- 82 conducted before this investigation;
- 11 conducted by it (the bulk RCAs, below);
- 1 still running at the time of writing (N-name-sort, `RCA-BULK-4`).

## What this sweep changes in the record

- **The 14 round-9 class RCA documents are recoverable.** They were thought to exist only under `/mnt/project-files`, but they are in `handoff/audit-r9-plan` history at `763b0ba4`, under `handoff/round9/state/rca/<slug>/RCA.md`; the branch tip removed them. R9-EG-R0 lands them in-tree under `tools/audit/rca/`.
- **40 of the 82 were documented in neither the register nor an issue:**
  - 31 live only in PR bodies or in the tree;
  - 9 are lost (deleted #201 and issue comments; PRs #1089, #1092, #1107, #1118, #1120, #1122 and #1123 by the retired `tvofi-seat-author` return 404).
  - Their countermeasures landed. Rebuilding the lost records is refused (RCA-BULK-2 §3.4 (v)); the register indexes each with what survives.
- **Roster bookkeeping error:** `handoff/audit-r9-fixplan` commit `27049219` set `rca-done` on **R9-EG-B1**, not R9-EG-B0. Roster rev 2 corrects it.
- **Misfiled as owed:** #1662's draft says "RCA: owed", but RC2 (#1641) is that RCA.
- **Half-landed class barriers:**
  - On main: I3, P11, P5 and N-future-instant.
  - Partly on main: I5 (only its quoted-line pass).
  - Still prototype-only, owed by not-started groups: P1 (F1.6), P3 (F1.10), P2 and P6 (F1.11), P9 (F6.3), N-solve-recompute and cpu-gate-blind (F10.2), I1 (F10.3), I5's doc_claims (F10.4), I4 (F11.4).
- **The plan-of-record row for #1070** says "root-cause seat in flight". No seat ever ran, and its countermeasure had already landed (`97d9bdb3`, #1124). The next record PR corrects the row.

## Conducted by this investigation (`../rca/`)

| id | subject | verdict | placement |
|---|---|---|---|
| BULK-1-P7 | P7 naive datetime across DST | build: tracer config and straddle arms. F1.1's barrier catches 1 of 3 historical members | R9-F10.1c (new issue) |
| BULK-1-P10 | P10 CPU work outside the process worker | build: kernel calls outside the worker = 0. 2304 loop calls at main (`topology.py:_advisor_replay`, #1658) | carry into R9-F1.7 (#1658) |
| BULK-1-P8 | P8 currency and unit precedence | build: carry the feed currency from ingest, plus the EUR-feed check (11/11 wrong at main). Refuse #1657's resolver metric, which would lock the defect in | carry into R9-F1.8 (#1657); the owner rules on the displayed currency |
| BULK-1-P4 | P4 seeds and tolerance | refuse the barrier on numbers (#1293/#1294 owner refusals); the solve certificate is the detector | R9-F2.4 (#1664); owner records the refusal |
| BULK-2-I2 | I2 closure diverges from deps | build: a nightly strace comparison; refuse an over-scope barrier. 3 of 8 members reclassified | carry into R9-F10.3 (#1663) |
| BULK-2-N-structure-blind | dead production code, metric reads 0 | build: reachability liveness, a planted-shape self-check, and an unmeasured-shape count | carry into R9-F10.4 (#1661, #1686) |
| BULK-2-R-register | the register and RCA records decay | build: the `fold_ledger.py` fold, `--check`, and in-tree RCA docs; the policy parts go to the owner | R9-EG-R0, R9-EG-R1 (new issue) |
| BULK-3-1721 | governance red on main (trigger 2) | build: a governance step in `graders-head-copy` under `GITHUB_TOKEN` | R9-F11.7 (new issue) |
| BULK-3-1545 | the bare `ConfigEntry` claim | confirmed: #1590's check fails at the claim's SHA and passes at main; gap: `qs_py_typed_files` | carry into R9-F10.4 |
| BULK-3-1070 | corpus-cap headroom | band confirmed (#1124); per-file band refused until 3 per-file frictions in one window | plan-row correction in the record PR |
| BULK-3-v660-freeze | v6.6.0 options-flow freeze (trigger 1) | cause not established; instrument first (nightly-ha loop heartbeat, plus the owner's host profiler) | R9-F10.7 (new issue) |
| BULK-3-1041-rerun | the silent-zero cost test | refusal overturned: land `merge_shape_guard` in `agreement.mjs`; lint and helper refusals confirmed; the class barrier goes to the owner | carry into R9-F11.4 (#1650) |

## The inventory before this investigation (phase A2, verbatim below)

82 RCAs (2026-08-27 to 09-28): 45 done, 22 partial, 15 prototype-only; 20 scheduled or owed. Rows: `rca_inventory.json`, `rca_scheduled.json`.

- **done**: four parts; countermeasure on main or refusal recorded.
- **partial**: a part missing, or the record lost.
- **prototype-only**: four parts; countermeasure only on a branch or proposed.

## Done (45)

| group | RCAs (process state → countermeasure landing) |
|---|---|
| era 1, 09-06..11 | #546 pairs (a)→137b6d59; 0002 proxy (c)→1684e620; hassfest (a)→a6e95ff9; #690 record-status (c)→c9dfec77; #678 (c)→015fdbd8; stated-number (c)→44f914ac; #541 audience (c)→ae36eff1, body-figures (a)→e64d287f, gh-api-f (c)→1fd24876; refusals: #593 (a), dev-record quantity (c), #865 (c) |
| era 2, 09-15..17 | #1041 plan/D6 (c)→3aa1351d; delivery-row seam (c)→31384db6; #1087 (d)→c71c53cf (comment deleted; parts from the plan) |
| round 8, 09-23..25 | #1499 (c)→f8630d95; #1514 (c) and #1515 (a)→e2e8c3bf; #1525 (a)→14d7a276; #1577 (a); #1584 (c); #1596 (d); plus 13 written inside fixer PRs, no separate seat (#1553, #1559, #1560, #1561, #1563, #1569, #1572, #1576, #1581, #1590, #1602, #1558/#1516, #1567) |
| v6.6.12 | bug 5 (a)→8f7abb96; listener (c)→9b60705e; bugs 3/4 (d)→#1619 and #1625; bug 7 (a)→#1622 and #1626 |
| round 9 | RC1 (c)→b6234f2c; RC2 (d)/(a)/(c)→4f25b5e3; I3→87d780c7; P11→1ef6a805; P5→fab17619; N-future-instant→917f16c2 |

## Partial (22)

- **Record lost; countermeasure landed:**
  - ledger self-loop (#201 comment 5705776367, deleted);
  - gate lease (#1089);
  - scratch-collide (#1092);
  - #1094 and #1095 (their issue comments were deleted);
  - mutation baseline (#1120);
  - the vacuous-acceptance-arm refusal (5720829142, deleted);
  - #1565 mutation timeouts (its PR body could not be retrieved).

  PRs #1089, #1092, #1107, #1118, #1120, #1122, #1123 return 404 (all by `tvofi-seat-author`).
- **Process state missing or not lettered (a)–(d):** trap 13 (#531/#569/#591), #1566, #1595, #1728, coil-drain e6a26880.
- **Cost test missing:** scratchpad body swap, #1336 (#1371), #1485, #1589/#1604, #1638 regression, v6.6.12 bugs 1/6 and 2.
- **Cause only:** #70 (v5.1.1, before the doctrine) and #1249.

## Prototype-only (15): countermeasures on branches that never landed

| RCA | where the countermeasure sits | owed landing |
|---|---|---|
| P1 | `handoff/r9-rca-p1@0ade2456` (magnitude scrub, Arm 4) | F1.6 |
| P2 | `r9-rca-p2@3938c8ea` (owners_lint) | F1.11 |
| P6 | `r9-rca-p6@aa2026b7` (entities arms) | F1.11 |
| P3 | `r9-rca-p3@2ca057ae` | F1.10 |
| P9 | `r9-rca-p9@4f3b9d4f` (p9Grid, +572 lines) | F6.3 |
| I1 | `r9-rca-i1@8eda51a2` (per-site ratchet) | F10.3 |
| I4 | `r9-rca-i4@06bae072` (agreement.mjs) | F11.4 |
| I5 | `r9-rca-i5@c6ba6036`: the doc_claims arms have not landed; the quoted-line pass landed in #1715 | F10.4 |
| N-solve-recompute | `r9-rca-avoidable…@ab04e39b` (call channel): only an evidence copy landed, in #1734 | F10.2 |
| N-cpu-gate-blind | `r9-rca-cpu-gate-blind@8352c9e0` | F10.2 |
| RCA-1736 | the EG-B1 refactor, not built | EG-B1 |
| #1041 silent-zero | `merge_shape_guard.py` was built and never pushed; the instances were fixed (ed875dea) | none |
| #533 nightly unrun | a `pull_request` arm for nightly-ha; at 3490cb16 it still runs only on schedule and dispatch | none |
| #1372 D0 | a cost-aware finding format, proposed to the owner | none |
| check-does-not-bind | `assert_binds`/`safepost.sh`, local to one seat | none |

## Scheduled or owed (20 JSON rows; barrier landings grouped)

| subject | owner | status |
|---|---|---|
| #1747 Root cause section (EG-B8) | EG-B8 fixer | not-started |
| #1736 EG-B0 | root-cause seat | **done**; rosters still say `not-started` (27049219 set `rca-done` on EG-B1) |
| EG-B1 plus the bugclasses fold and the barrier-window policy | EG-B1 / tvofi | not-started |
| F11.5, which lands the approved RCA drafts A1–A9 | F11.5 | not-started |
| 8 class-barrier landings (F1.6, F1.10, F1.11, F6.3, F10.2, F10.3, F10.4, F11.4) | lane fixers | not-started |
| #1721 red on main, detector "owed to a root-cause seat" | unassigned | no RCA |
| #1545 (round 8, §6) | root-cause seat | no RCA; the issue has 0 comments |
| #1070 corpus-cap headroom, "in flight" since 09-17 | root-cause seat | no RCA |
| v6.6.0 options-flow freeze (5712963862) | defect seat | no RCA; #1107 "not shown to fix" it |
| #1041 cost-test re-run | root-cause seat | not done |
| P1 residue and P11 D6-s1-81 | tvofi | asked |
| a superseded-head red that recurs a 3rd time | root-cause seat | armed |
| P4, I2, P7, P8 cross-round recurrence | ledger owner | flagged only |

## Undocumented: neither the register nor an issue

`bugclasses.json` cites RCAs only for P5, N-future-instant, P11 (the v6.6.12 record) and N-restart (RC2). I3's entry does not cite its RCA.

40 of the 82 have neither a register citation nor an issue record:

- **PR body or tree only (31).** All round-8 RCAs, plus #593, #1577, #1584, #1596, #1589, RC1, #1728, #1638, #1372, #70 and #1249. Decision 0002, trap 13 and coil-drain live only in the tree.
- **Lost (9).** The deleted #201 and issue comments, and the PRs that return 404.

## Class RCAs the round-9 judge owed

All 14 judge `rca: true` classes have one: 13 at `audit-r9-plan@763b0ba4:handoff/round9/state/rca/<slug>/RCA.md` and N-restart via RC2. N-future-instant, `rca: true` only after the sweep, has one there too.

No RCA at all:

- P4: 14 historical instances.
- I2: 5 of 6 rounds.
- P7: 4 of 6 rounds; it was barriered without one.
- P8: N=2.
- The solve-scoped hub-write class went 3 rounds unrecognised until RCA-1736.
