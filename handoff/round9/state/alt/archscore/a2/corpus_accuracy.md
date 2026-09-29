# Historical calibration corpus for the architecture score (a2)

Baseline `origin/main` `7952d8f9`. 45 commits on main's history: **14 BAD, 24 GOOD, 7 NEUTRAL**.
Every label comes from a source that does not use a structure metric: a root-cause analysis, a
probe-confirmed screen verdict, an issue draft, a PR body or review, or an owner decision. The
quote and its path or PR are in `corpus.tsv` under `label_source`.

## Files

| file | what it is |
|---|---|
| `labels.tsv` | the hand labels: sha, PR, label, `circ`, class, description, quoted source |
| `measure_one.py` | measures one tree: the **current** `tests/structure.py` (copied from `7952d8f9` into `measurer/`) with `REPO_ROOT` re-pointed, plus the m1/m2/m3 enumerators rewritten as functions, plus `null_pkg_loc` (raw production LOC, a pure size proxy) |
| `measure_all.py` | for each label: first parent → `wt-before`, commit → `wt-after` (two detached worktrees, removed at the end), measure both, write `corpus.tsv`; per-commit JSON is cached in `results/` |
| `analyze.py` | `corpus.tsv` → `accuracy_tables.md` (the tables below are that file) |
| `corpus.tsv` | 45 rows. Columns: sha, parent, carried_by (first-parent main commit), date, pr, label, circ, class, description, label_source, measure_errors, seam fallback counts, then `d_<metric>` = after − before for all 25 structure rows, 12 enumerator counts and `null_pkg_loc` |

Reproduce: `python3 measure_all.py && python3 analyze.py` (about 4 minutes, 90 tree measurements).

## How it was measured, and whether that can be trusted

- **The current measurer on old trees.** `measure()` is the 7952d8f9 function unchanged. The only
  adaptation is the seam map. For a method the current `tests/seam_map.json` names, it uses the
  map's seam; for a historic name the map does not know, it uses the measurer's own seed rule,
  `regex_seam`. That is a function of the name, so both sides of one commit get the same
  assignment. The fallback counts are in the `seam_fallback_b/a` column (up to 38 methods on
  early trees). Coordinator-seam rows before about 2026-09-25 therefore use the name rule that
  #1539 retired.
- **No tree failed.** 0 of 90 measurements raised. `HeatPumpOptimizerCoordinator` exists at every
  commit back to April.
- **Validation against numbers quoted in PR bodies.** The deltas here reproduce the before and
  after figures those bodies quote, row for row:
  - #506: `cut_views` −9, `coordinator_loc` −141, `functions_cc_over_15` −1, `methods_over_150` −1;
  - #551: `coordinator_loc` −64, `methods_over_150` −1, `methods_over_200` −1;
  - #750: `coordinator_loc` −395, methods −12, attrs −13, multiassigned −10, edges −27,
    `cut_dhw` −22, `cut_learning` −29, `classes_over_300` +1;
  - #1751: edges −5, cross −3, `cut_grid` −1, `cut_learning` −1;
  - #1765: `coordinator_loc` −15, `cut_fetch` −11, `cut_grid` −11, multiassigned −1.
- **The enumerators.** These are the round-9 prototypes from `handoff/audit-r9-alt`
  `evidence/m{1,2,3}_*.py`, wrapped so that a missing function or golden gives `NA`:
  - m1: in-place writes into `_opt_config`/`_thermal_params`/`_current_state` on the solve path,
    in `coordinator.py`, and package-wide;
  - m2: top-level `coordinator.data` keys the platforms read, and keys absent from every golden;
    `NA` before the goldens existed;
  - m3: reads and writes of the coordinator's private members from other modules.

## Labels, and the circularity caveat

- **BAD (14).** Each is an introducing commit named by an RCA or a probe-confirmed verdict whose
  cause is the commit's own shape:
  - 9 N-shared-config: a live shared object carrying a second, per-operation meaning. Sources are
    RCA-1736, the #1736 shape screen (`VERDICTS.md` S1/S2/H1–H4/C1/C2) and issues #1752/#1753.
  - 2 duplicated fact: P2 (`a1bdb11c`) and P3 (`3e5aba6a`).
  - 1 reach-through plus duplicated rule: the arbiter, #1739 and R9-P2.
  - 1 untyped-payload contract: P6/#1737.
  - 1 implicit two-place family definition: N-name-sort, RCA-BULK-4.
- **GOOD (24).** Accepted structural changes whose PR, RCA or review argues the structural gain.
  **10 are `circ=yes`:** #193 decomposition stages whose acceptance was argued in these same
  metrics (titles such as "cut_dhw 194 -> 103"). They agree with the metrics by construction and
  are shown separately as `GOOD-nc`, the 14 non-circular ones.
- **NEUTRAL (7).** Reported but not scored:
  - moved but kept the pattern: `e4bc3756`/#492, and the #1563 envelope repair;
  - reader-only fix: #437;
  - canonical resolver of the wrong fact: currency, `9a0d4c5e`;
  - disputed mechanism: economy widening, `c5fcfb17`;
  - scaffolding only: #497;
  - commit contradicts the finding's framing: `7d47e80e`.

## Scoring

GOOD expects delta ≤ 0 and BAD expects delta ≥ 0. Each case falls into one of three outcomes:

- **right**: the metric moved strictly the expected way;
- **flat**: 0;
- **wrong**: it moved the other way.

`ok%` is (right + flat) / n, the brief's measure. **It is dominated by flat**, which is why the
table also gives `moved%` and `sep = (right − wrong) / n`. A metric that never moves scores 100 %
ok and sep 0.

BAD-small is the six BAD commits whose production diff is at most 300 lines. On these a size row
cannot fire on feature growth alone.

GOOD n=24 (non-circular 14), BAD n=14, NEUTRAL n=7

BAD-small (production diff <= 300 lines) n=6: 8827452e, ca711b56, 07bdc557, a1bdb11c, 546b4924, aa2677ba

| metric | GOOD right/flat/wrong | GOOD ok% | GOOD-nc right/flat/wrong | BAD right/flat/wrong | BAD ok% | BAD-small right/flat/wrong | moved% (G+B) | sep |
|---|---|---|---|---|---|---|---|---|
| classes_over_300 | 0/22/2 | 92 | 0/14/0 | 1/13/0 | 100 | 0/6/0 | 8 | -0.03 |
| attrbag_classes_over_30 | 0/24/0 | 100 | 0/14/0 | 1/13/0 | 100 | 1/5/0 | 3 | +0.03 |
| methods_over_200 | 3/21/0 | 100 | 3/11/0 | 2/12/0 | 100 | 0/6/0 | 13 | +0.13 |
| methods_over_150 | 5/19/0 | 100 | 4/10/0 | 5/9/0 | 100 | 0/6/0 | 26 | +0.26 |
| max_class_loc | 12/12/0 | 100 | 6/8/0 | 10/3/1 | 93 | 2/3/1 | 61 | +0.55 |
| max_method_loc | 3/21/0 | 100 | 1/13/0 | 6/8/0 | 100 | 2/4/0 | 24 | +0.24 |
| max_cc | 1/23/0 | 100 | 0/14/0 | 4/10/0 | 100 | 1/5/0 | 13 | +0.13 |
| coordinator_loc | 12/12/0 | 100 | 6/8/0 | 10/3/1 | 93 | 2/3/1 | 61 | +0.55 |
| coordinator_methods | 4/20/0 | 100 | 1/13/0 | 9/5/0 | 100 | 2/4/0 | 34 | +0.34 |
| coordinator_attrs | 3/21/0 | 100 | 0/14/0 | 8/5/1 | 93 | 2/4/0 | 32 | +0.26 |
| coordinator_multiassigned_attrs | 3/21/0 | 100 | 1/13/0 | 8/6/0 | 100 | 2/4/0 | 29 | +0.29 |
| duplication_blocks | 0/24/0 | 100 | 0/14/0 | 0/14/0 | 100 | 0/6/0 | 0 | +0.00 |
| functions_cc_over_25 | 1/23/0 | 100 | 1/13/0 | 3/11/0 | 100 | 0/6/0 | 11 | +0.11 |
| functions_cc_over_15 | 4/20/0 | 100 | 2/12/0 | 7/7/0 | 100 | 0/6/0 | 29 | +0.29 |
| const_modules_over_50 | 0/24/0 | 100 | 0/14/0 | 1/13/0 | 100 | 0/6/0 | 3 | +0.03 |
| local_imports | 1/23/0 | 100 | 1/13/0 | 0/14/0 | 100 | 0/6/0 | 3 | +0.03 |
| dead_top_level_symbols | 0/24/0 | 100 | 0/14/0 | 5/8/1 | 93 | 0/6/0 | 16 | +0.11 |
| dead_methods | 0/23/1 | 96 | 0/13/1 | 1/11/2 | 86 | 0/6/0 | 11 | -0.05 |
| internal_call_edges | 6/18/0 | 100 | 2/12/0 | 7/7/0 | 100 | 1/5/0 | 34 | +0.34 |
| cross_seam_edges | 5/19/0 | 100 | 2/12/0 | 7/7/0 | 100 | 1/5/0 | 32 | +0.32 |
| cut_dhw | 3/21/0 | 100 | 0/14/0 | 4/10/0 | 100 | 1/5/0 | 18 | +0.18 |
| cut_learning | 5/19/0 | 100 | 2/12/0 | 2/12/0 | 100 | 0/6/0 | 18 | +0.18 |
| cut_fetch | 1/23/0 | 100 | 1/13/0 | 5/9/0 | 100 | 0/6/0 | 16 | +0.16 |
| cut_grid | 4/20/0 | 100 | 3/11/0 | 6/8/0 | 100 | 1/5/0 | 26 | +0.26 |
| cut_views | 1/23/0 | 100 | 0/14/0 | 7/7/0 | 100 | 2/4/0 | 21 | +0.21 |
| m1_solve_sites | 0/24/0 | 100 | 0/14/0 | 4/10/0 | 100 | 0/6/0 | 11 | +0.11 |
| m1_solve_fields | 0/24/0 | 100 | 0/14/0 | 4/10/0 | 100 | 0/6/0 | 11 | +0.11 |
| m1_coord_sites | 1/22/1 | 96 | 0/13/1 | 6/8/0 | 100 | 1/5/0 | 21 | +0.16 |
| m1_coord_fields | 1/23/0 | 100 | 0/14/0 | 6/8/0 | 100 | 1/5/0 | 18 | +0.18 |
| m1_pkg_sites | 1/22/1 | 96 | 0/13/1 | 6/8/0 | 100 | 1/5/0 | 21 | +0.16 |
| m2_keys_read | 0/24/0 | 100 | 0/14/0 | 8/6/0 | 100 | 2/4/0 | 21 | +0.21 |
| m2_read_sites | 0/24/0 | 100 | 0/14/0 | 8/4/2 | 86 | 2/3/1 | 26 | +0.16 |
| m2_unproduced | 0/24/0 | 100 | 0/14/0 | 2/9/0 | 100 | 1/4/0 | 6 | +0.06 |
| m3_reaches | 1/23/0 | 100 | 1/13/0 | 4/10/0 | 100 | 1/5/0 | 13 | +0.13 |
| m3_members | 0/24/0 | 100 | 0/14/0 | 3/11/0 | 100 | 1/5/0 | 8 | +0.08 |
| m3_files | 0/23/1 | 96 | 0/13/1 | 3/11/0 | 100 | 1/5/0 | 11 | +0.05 |
| m3_writes | 0/23/1 | 96 | 0/13/1 | 1/13/0 | 100 | 1/5/0 | 5 | +0.00 |
| null_pkg_loc | 2/1/21 | 12 | 2/0/12 | 14/0/0 | 100 | 6/0/0 | 97 | -0.13 |

### BAD cases: which metrics rose (structure metrics | enumerators), and which fell

| sha | class | structure metrics up | structure metrics down | enumerators up | pkg LOC delta |
|---|---|---|---|---|---|
| 8827452e | N-shared-config | attrbag_classes_over_30, max_class_loc, max_method_loc, max_cc, coordinator_loc, coordinator_methods, coordinator_attrs, coordinator_multiassigned_attrs, internal_call_edges, cross_seam_edges, cut_dhw, cut_views | - | m1_coord_sites, m1_coord_fields, m1_pkg_sites, m2_keys_read, m2_read_sites | 255 |
| 5f6ada5e | N-shared-config | methods_over_200, methods_over_150, max_class_loc, coordinator_loc, coordinator_methods, coordinator_attrs, coordinator_multiassigned_attrs, functions_cc_over_25, functions_cc_over_15, dead_top_level_symbols, internal_call_edges, cross_seam_edges, cut_learning, cut_fetch, cut_grid, cut_views | dead_methods | m1_solve_sites, m1_solve_fields, m1_coord_sites, m1_coord_fields, m1_pkg_sites, m2_keys_read, m2_read_sites | 1665 |
| c27a6d32 | N-shared-config | methods_over_150, max_class_loc, max_method_loc, max_cc, coordinator_loc, coordinator_methods, functions_cc_over_15, internal_call_edges, cross_seam_edges, cut_dhw, cut_learning, cut_fetch, cut_grid | coordinator_attrs, dead_top_level_symbols, dead_methods | m1_solve_sites, m1_solve_fields, m1_coord_sites, m1_coord_fields, m1_pkg_sites, m3_reaches, m3_files | 506 |
| f2d7a502 | N-shared-config | max_class_loc, coordinator_loc, coordinator_methods, coordinator_attrs, coordinator_multiassigned_attrs, functions_cc_over_15, dead_top_level_symbols, internal_call_edges, cross_seam_edges, cut_dhw, cut_grid, cut_views | - | m1_solve_sites, m1_solve_fields, m1_coord_sites, m1_coord_fields, m1_pkg_sites, m2_keys_read, m2_read_sites | 942 |
| 9ac2d02c | N-shared-config | methods_over_150, max_class_loc, coordinator_loc, coordinator_methods, coordinator_attrs, coordinator_multiassigned_attrs, functions_cc_over_25, functions_cc_over_15, dead_top_level_symbols, dead_methods, internal_call_edges, cross_seam_edges, cut_dhw, cut_fetch, cut_grid | - | m1_solve_sites, m1_solve_fields, m1_coord_sites, m1_coord_fields, m1_pkg_sites, m2_keys_read, m2_read_sites | 1260 |
| 2e0d3d96 | N-shared-config | methods_over_150, max_class_loc, max_method_loc, coordinator_loc, coordinator_methods, coordinator_attrs, coordinator_multiassigned_attrs, functions_cc_over_15, dead_top_level_symbols, internal_call_edges, cross_seam_edges, cut_fetch, cut_grid, cut_views | - | m2_keys_read, m2_read_sites | 1355 |
| 364d9b41 | N-shared-config | methods_over_200, methods_over_150, max_class_loc, max_method_loc, max_cc, coordinator_loc, coordinator_methods, coordinator_attrs, coordinator_multiassigned_attrs, functions_cc_over_25, functions_cc_over_15, internal_call_edges, cross_seam_edges, cut_views | - | m2_keys_read, m2_read_sites, m2_unproduced | 942 |
| ca711b56 | N-name-sort | max_method_loc | - | none | 66 |
| 07bdc557 | N-shared-config | **none (blind)** | max_class_loc, coordinator_loc | m3_reaches, m3_members, m3_files, m3_writes | 257 |
| a1bdb11c | P2 | **none (blind)** | - | none | 27 |
| 546b4924 | N-shared-config | **none (blind)** | - | none | 41 |
| 3b320405 | P2+reach | max_class_loc, coordinator_loc | - | m3_reaches, m3_members, m3_files | 505 |
| 3e5aba6a | P3 | classes_over_300, max_class_loc, max_method_loc, max_cc, coordinator_loc, coordinator_methods, coordinator_attrs, coordinator_multiassigned_attrs, functions_cc_over_15, const_modules_over_50, dead_top_level_symbols, cut_fetch, cut_views | - | m1_coord_sites, m1_coord_fields, m1_pkg_sites, m2_keys_read, m2_read_sites, m3_reaches, m3_members | 1024 |
| aa2677ba | P6 | max_class_loc, coordinator_loc, coordinator_methods, coordinator_attrs, coordinator_multiassigned_attrs, cut_grid, cut_views | - | m2_keys_read, m2_read_sites, m2_unproduced | 88 |

### GOOD cases: which structure metrics fell / rose

| sha | pr | circ | structure metrics down | structure metrics UP | enumerators down | pkg LOC delta |
|---|---|---|---|---|---|---|
| ca937daa | #340 | no | methods_over_200, methods_over_150, max_method_loc, functions_cc_over_25, functions_cc_over_15 | - | none | 43 |
| 4a7bdb69 | #358 | yes | max_method_loc | - | none | 96 |
| 4b6e0765 | #360 | no | methods_over_200, methods_over_150, local_imports | - | none | 17 |
| 67e1cf33 | #500 | yes | coordinator_attrs | - | none | 19 |
| d979110c | #502 | yes | max_class_loc, coordinator_loc, coordinator_methods, internal_call_edges | - | none | 2 |
| 5a4e6ff9 | #506 | yes | methods_over_150, max_class_loc, coordinator_loc, functions_cc_over_15, cut_views | - | none | 70 |
| 8281f544 | #529 | yes | max_class_loc, coordinator_loc, cut_dhw, cut_learning | - | none | 8 |
| d04ed89f | #537 | yes | max_class_loc, coordinator_loc, internal_call_edges, cross_seam_edges, cut_grid | - | none | 6 |
| 0f9eb71a | #551 | no | methods_over_200, methods_over_150, max_class_loc, coordinator_loc | - | none | -7 |
| 52d38d95 | #555 | yes | cut_learning | - | none | 0 |
| 8bc4c661 | #557 | yes | max_method_loc, max_cc | - | none | 21 |
| 0323c5b8 | #597 | no | methods_over_150 | - | none | -743 |
| 69781076 | #750 | yes | max_class_loc, coordinator_loc, coordinator_methods, coordinator_attrs, coordinator_multiassigned_attrs, functions_cc_over_15, internal_call_edges, cross_seam_edges, cut_dhw, cut_learning | classes_over_300 | m1_coord_sites, m1_coord_fields, m1_pkg_sites | 107 |
| ec263d82 | #771 | yes | max_class_loc, coordinator_loc, coordinator_methods, coordinator_attrs, coordinator_multiassigned_attrs, internal_call_edges, cross_seam_edges, cut_dhw | classes_over_300 | none | 80 |
| 137b6d59 | #548 | no | functions_cc_over_15 | - | none | 12 |
| 33cedffa | #1359 (fixes #1299) | no | max_class_loc, coordinator_loc | - | none | 16 |
| 043ed159 | #1605 (fixes #1520/#1530) | no | **none (blind)** | - | none | 83 |
| 56cb0027 | #1559 (fixes #1513) | no | max_class_loc, coordinator_loc | - | none | 122 |
| 2a451021 | #1576 (fixes #1526) | no | max_class_loc, coordinator_loc | - | none | 10 |
| 3e9f1878 | #1704 | no | **none (blind)** | dead_methods | none | 117 |
| ff30236d | #1694 | no | **none (blind)** | - | none | 16 |
| 3bae92d9 | #1731 | no | max_class_loc, coordinator_loc, coordinator_methods, internal_call_edges, cross_seam_edges, cut_learning, cut_grid | - | none | 80 |
| c2a0448d | #1751 | no | internal_call_edges, cross_seam_edges, cut_learning, cut_grid | - | none | 52 |
| 5395394d | #1765 | no | max_class_loc, coordinator_loc, coordinator_multiassigned_attrs, cut_fetch, cut_grid | - | m3_reaches | 29 |

### Composite: the ratchet's own decision rule (any of the 25 rows up => FAIL)

- BAD cases the ratchet would FAIL: 11/14
- GOOD cases the ratchet would PASS with a recorded gain: 19/24; FAIL: 3/24; no row moved: 2

### Size confound: sign agreement of each structure metric with raw package LOC (pkg LOC != 0 and metric moved)

| metric | agrees with LOC sign | disagrees |
|---|---|---|
| classes_over_300 | 3 | 0 |
| attrbag_classes_over_30 | 1 | 0 |
| methods_over_200 | 3 | 2 |
| methods_over_150 | 7 | 3 |
| max_class_loc | 11 | 12 |
| max_method_loc | 6 | 3 |
| max_cc | 4 | 1 |
| coordinator_loc | 11 | 12 |
| coordinator_methods | 9 | 4 |
| coordinator_attrs | 8 | 4 |
| coordinator_multiassigned_attrs | 8 | 3 |
| functions_cc_over_25 | 3 | 1 |
| functions_cc_over_15 | 7 | 4 |
| const_modules_over_50 | 1 | 0 |
| local_imports | 0 | 1 |
| dead_top_level_symbols | 5 | 1 |
| dead_methods | 2 | 2 |
| internal_call_edges | 7 | 6 |
| cross_seam_edges | 7 | 5 |
| cut_dhw | 4 | 3 |
| cut_learning | 2 | 4 |
| cut_fetch | 5 | 1 |
| cut_grid | 6 | 4 |
| cut_views | 7 | 1 |
| m1_solve_sites | 4 | 0 |
| m1_solve_fields | 4 | 0 |
| m1_coord_sites | 7 | 1 |
| m1_coord_fields | 6 | 1 |
| m1_pkg_sites | 7 | 1 |
| m2_keys_read | 8 | 0 |
| m2_read_sites | 8 | 2 |
| m2_unproduced | 2 | 0 |
| m3_reaches | 4 | 1 |
| m3_members | 3 | 0 |
| m3_files | 4 | 0 |
| m3_writes | 2 | 0 |

## What the corpus says

1. **The ratchet's own decision rule (any row up ⇒ FAIL) catches 11 of 14 BAD, but it catches
   growth, not the defect.**
   - Eight of the eleven are feature commits of 505–1,665 production lines: v2.8.0 wiring,
     v3.8.0, v4.0.0 T2/T3/T6, the manual plan, the arbiter and the April two-zone model. A ninth,
     `8827452e`, is a 255-line feature. Every size-shaped row rises on them. The project's own rule answers a feature's rise with an
     owner-confirmed budget raise, so none of these FAILs would have stopped the defect.
   - On the defect-sized commits the structure rows are blind or move the wrong way:
     - `07bdc557` (the #1752 boost leak, severity high): no row up, `coordinator_loc` −6;
     - `a1bdb11c` (second stamp chain): nothing moves;
     - `546b4924` (streak shared across entries): nothing moves;
     - `ca711b56` (N-name-sort): only an incidental `max_method_loc` +6.
2. **Blind classes. No structure row responds to the labelled shape itself:**
   - **N-shared-config**, 9 cases: rows rise on the 7 introductions that arrived inside a
     feature (`8827452e`, `5f6ada5e`, `c27a6d32`, `f2d7a502`, `9ac2d02c`, `2e0d3d96`,
     `364d9b41`). Nothing rises on the 2 defect-sized ones: the `_current_action` in-place
     overlay (`07bdc557`) and the `hass.data` streak (`546b4924`).
   - **P2/P3 duplication**: `duplication_blocks` moved on 0 of 38 scored commits. It is blind to
     both introductions (a stamp chain and a one-expression copy are under the 10-line window)
     and to every dedup GOOD (#551, #597, F1.3, F1.5, F2.1, the COP law).
   - **N-name-sort**: translations, so outside every metric.
   - **Reach-through**: the arbiter adds 23 private reaches and structure sees `coordinator_loc`
     +2, which reproduces M3's claim on history.
   - **Untyped payload**: only `coordinator_*` rows, through the new keys' producer lines.
3. **The enumerators are the only instruments that respond to the shapes on small diffs.**
   - **m3** fires on both reach-through BADs: `07bdc557` +6 with 1 write, arbiter +23.
   - **m2_unproduced** fires on `aa2677ba` (+2) and `364d9b41` (+1).
   - **m1** fires on the hub-writing N-shared-config introductions: `5f6ada5e`, `c27a6d32`,
     `f2d7a502`, `9ac2d02c`, and `8827452e` at coordinator scope. It is blind to non-hub shared
     objects (`_current_action`, the what-if cache, module globals).
   - **m1 has a move blind spot.** An extraction that renames the hub (`self._params` in
     `dhw_learning.py`, `setattr` over a field list in `away.py`) reads as an improvement:
     - W5-G9 moved 4 writes out, and m1 falls by 4;
     - `e4bc3756` moved 12 writes out, and m1 falls by 12;
     - but VERDICTS H4 says the defect "moved to `dhw_learning.py` by 69781076", and RCA-1736
       says #492 left the writer untouched.

     m3 prices #492's move at +7 reaches.
4. **GOOD side.**
   - 19 of 24 pass with a recorded gain. Among the 14 non-circular ones, 11 show a gain and 3 are
     blind: one COP law, one stamp owner, one power-fraction helper. Centralising a fact outside
     the coordinator moves no row.
   - **Wrong-way readings:**
     - `classes_over_300` +1 on both real seam moves (W5-G9, W5-G10), the M7 shape: extraction
       creates a class over 300 lines;
     - `dead_methods` +1 on the F4.1 stamp owner, where the old copy became dead.
   - Most non-circular gains are `coordinator_loc` lines paid, not the fact being centralised.
5. **The size confound is real but not trivial.**
   - Raw package LOC rises on 14 of 14 BAD and on 21 of 24 GOOD (sep −0.13), so size alone does
     not separate the labels.
   - `coordinator_loc` and `max_class_loc` separate best (sep +0.55) because GOOD is mostly
     coordinator-shrinking stages and BAD mostly coordinator-growing features. That is a
     property of how the labelled commits were chosen, not evidence that the metric sees the
     defect shape.
6. **Implication for a score.**
   - A score built from the 25 rows would reward the decomposition programme (true by
     construction) and would penalise features.
   - It would **not** detect any of the labelled defect shapes on a defect-sized diff.
   - Only m1 (extended to non-hub shared objects and to renamed hubs), m3 and m2_unproduced
     carry shape signal, and each covers one class.
   - Duplication would need a cross-module, sub-10-line (or expression-level) detector before it
     can see P2/P3.

## Not measured

- No runtime behaviour: every delta is static.
- The GOOD/BAD sets are small (14 BAD, 14 non-circular GOOD). An ok% difference of one case is
  7 points.
- The seam rows on pre-#1539 trees use the name-rule fallback.
- `m2_unproduced` depends on the goldens present in each tree.
