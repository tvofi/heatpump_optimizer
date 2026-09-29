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
