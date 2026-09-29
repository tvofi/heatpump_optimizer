# Metric soundness review: the 24 structure metrics, calibrated by perturbation

Baseline: `origin/main` 7952d8f9. Instrument: `tests/structure.py::measure()` imported from each worktree
(`measure.py`). There is no `--json` flag; `measure()["metrics"]` is the interface. Baseline values are
`out/base.json`; the ratchet passes at baseline (`out/base_ratchet.txt`).

## Method

- 30 perturbations, each a deterministic script under `perturb/` (`python3 perturb/X.py <worktree>`). Every
  anchor is asserted to match exactly once, so a script run on another tree fails instead of editing the wrong
  place. `run_one.sh X` resets `wt-p` to 7952d8f9, applies X, then checks three things: every changed
  file compiles, every package module imports under `tests/hastub`, and ruff `F` reports no finding the
  baseline did not already have. It then measures. All 30 import cleanly. Only B8 adds ruff findings, and
  it is meant to: 419 × F405 from a star import.
- Behaviour is preserved by construction, not by a run of the suite. G1, G3 and B7 move code verbatim.
  B3 is a pure tail extraction. N1b and N1c assert that the AST is identical. The rest are small hand edits.
- Grading (`build_matrix.py` → `matrix.tsv` long form, `matrix_wide.tsv` wide form):
  - NULL: the expected delta is 0.
  - GOOD: the expected delta is ≤ 0.
  - BAD: the expected delta is ≥ 0.
  - A *targeted* cell is the metric the move is about. It expects a strict move, and holding is **MISS**.
  - A move in the wrong direction is **WRONG**.
- `probes.py` / `probes.tsv` prototype the proposed fixes on the same trees. Those numbers are the evidence
  for the "modify" verdicts.

The nulls: **N1** renames a local (18 sites) and moves **0/24** metrics. That is the control that the harness
itself is stable. N1b, N1c, N2, N3 and N4 are nulls too, and each one moves something (see the defects below).

## Matrix (delta vs baseline; `!` = WRONG, `?` = MISS)

```
metric                           G1  G2   G3 G4a G4b  G5  B1 B1c  B2 B3a B3b  B3c B4a B4b B4c B5a B5b B5c B5d B5e  B6 B6b    B7  B8 N1 N1b  N1c  N2   N3  N4
attrbag_classes_over_30           0   0    0   0   0   0   0   0   0   0   0    0   0   0   0   0   0   0   0   0   0   0     0   0  0   0    0   0    0   0
classes_over_300                  0   0    0   0   0   0   0   0   0   0   0    0   0   0   0   0   0   0   0   0   0   0     0   0  0   0    0   0    0   0
const_modules_over_50             0   0    0   0   0   0   0   0   0   0   0    0   0   0   0   0   0   0   0   0   0   0     0 -1!  0   0    0   0    0 -1!
coordinator_attrs                 0   0   -3   0   0  -1   0   0   0   0   0    0 +0?  +1 +0?   0   0   0   0   0   0   0   +0?   0  0   0    0   0    0   0
coordinator_loc                 +4!  -1 -187   0 +4!  -6   0   0   0   0  +9   +9  +2  +2  +1  +5  +6  +4 +10   0   0   0 -188!   0  0   0    0 +5!    0   0
coordinator_methods             +1! +1!   -5   0 +1!   0   0   0   0   0  +3   +3   0   0   0  +1  +1  +1  +2   0   0   0   -5!   0  0   0    0   0    0   0
coordinator_multiassigned_attrs   0   0   -3   0   0  -1   0   0   0   0   0    0 +0?  +1 +0?   0   0   0   0   0   0   0   -1!   0  0   0    0   0    0   0
cross_seam_edges                  0  -1   -3 +0? +0?   0   0   0 +0?   0   0    0   0   0   0   0   0   0   0   0   0   0   -7!   0  0   0    0   0  -2!   0
cut_dhw                           0   0  +0? +0? +0?   0   0   0 +0?   0   0    0   0   0   0   0   0   0   0   0   0   0   +0?   0  0   0    0   0    0   0
cut_fetch                         0  -1  +0? +0? +0?   0   0   0 +0?   0   0    0   0   0   0   0   0   0   0   0   0   0   +0?   0  0   0    0   0    0   0
cut_grid                          0   0  +0? +0? +0?   0   0   0 +0?   0   0    0   0   0   0   0   0   0   0   0   0   0   -3!   0  0   0    0   0    0   0
cut_learning                      0  -2   -8 +0? +0? +1!   0   0 +0?   0   0    0   0   0   0   0   0   0   0   0   0   0  -13!   0  0   0    0   0 -21!   0
cut_views                         0   0   -6 +0? +0?   0   0   0 +0?   0   0    0   0   0   0   0   0   0   0   0   0   0   -8!   0  0   0    0   0    0   0
dead_methods                      0   0    0   0   0   0   0   0   0   0   0    0   0   0   0  +1 +0? +0?  +1   0   0   0     0   0  0   0    0   0    0   0
dead_top_level_symbols            0   0    0   0   0   0   0   0   0   0   0    0   0   0   0   0   0   0   0  +1   0   0     0 +42  0   0    0   0    0   0
duplication_blocks                0  -2    0   0   0   0 +0?  +2   0   0   0    0   0   0   0   0   0   0   0   0   0   0     0   0  0 -2!    0   0    0   0
functions_cc_over_15            +0?   0    0   0   0   0   0   0   0 +0? +0?  +0?   0   0   0   0   0   0   0   0   0   0     0   0  0   0    0   0    0   0
functions_cc_over_25            +0?   0    0   0   0   0   0   0   0 +0? +0?  +0?   0   0   0   0   0   0   0   0   0   0     0   0  0   0    0   0    0   0
internal_call_edges             +1! +1!   -9   0   0   0   0   0   0   0  +3   +3   0   0   0  +1  +1  +1  +2   0   0   0  -14!   0  0   0    0   0    0   0
local_imports                     0   0    0   0   0   0   0   0   0   0   0    0   0   0   0   0   0   0   0   0 +0?  +1     0   0  0   0    0   0    0   0
max_cc                          +0?   0    0   0   0   0   0   0   0 -1! +0? -14!   0   0   0   0   0   0   0   0   0   0     0   0  0   0    0   0    0   0
max_class_loc                   +4!  -1 -187   0 +4!  -6   0   0   0   0  +9   +9  +2  +2  +1  +5  +6  +4 +10   0   0   0 -188!   0  0   0    0 +5!    0   0
max_method_loc                  +0?   0    0   0   0   0   0   0   0 +0? +0?  +0?   0   0   0   0   0   0   0   0   0   0     0   0  0   0 +38! +4!    0   0
methods_over_150                +0?   0    0   0   0   0   0   0   0 +0? +0?  +0?   0   0   0   0   0   0   0   0   0   0     0   0  0   0    0   0    0   0
methods_over_200                +0?   0    0   0   0   0   0   0   0 -1! -1!  -2!   0   0   0   0   0   0   0   0   0   0     0   0  0   0    0   0    0   0
```

Perturbation key: see the docstring of each `perturb/*.py` file.

- **GOOD**
  - G1: extract a cohesive block from `_update_current_state`.
  - G2: dedupe the replay block of the two fabric learners.
  - G3: move the frequency cluster and its state into `FrequencyControl`.
  - G4a: `coord._x` becomes an existing public accessor (21 sites).
  - G4b: a new property replaces 4 sites.
  - G5: the order-coupled `_last_house_sample` pair becomes a frozen record passed as an argument.
- **BAD**
  - B1: clone a function into another module. B1c is the same clone in the same module.
  - B2: 5 new private reaches.
  - B3a, B3b, B3c: meaningless tail-call fragment chains.
  - B4a, B4b, B4c: a per-operation value written into shared state before an await.
  - B5a–B5e: dead code in 5 shapes.
  - B6: a module-level import cycle. B6b is the same cycle as a function-scope import.
  - B7: the G3 cluster as free functions `f(coord)`, with the state left behind.
  - B8: `from .const import *`.
- **NULL**
  - N1: rename a local.
  - N1b: re-wrap a signature (AST identical).
  - N1c: explode 12 calls one argument per line (AST identical).
  - N2: add docstrings.
  - N3: a relabel in `seam_map.json` only.
  - N4: `from . import const` plus `const.X`.

## Per-metric verdicts

| metric | definition (structure.py) | proxies | verdict | evidence |
|---|---|---|---|---|
| attrbag_classes_over_30 | classes with more than 30 distinct `self.X` store targets | god-state classes | **retire** (redundant) | Reads 1, and that class is the coordinator (the harness asserts it). 0/30 cells move. Every move it could see is already in coordinator_attrs. |
| classes_over_300 | classes whose span is more than 300 lines | god classes | **retire** | 0/30 cells move. Size only. Known #1738c: it scores an extraction as a regression. max_class_loc carries the same information with a gradient. |
| const_modules_over_50 | modules whose `from .const import` names total more than 50 | fan-in on the constants hub | **retire** from the architecture score (a lint concern). If kept, **modify**: count distinct const symbols a module *loads* (resolved via `bound_references`, `const.X` included) and refuse `import *` | **WRONG on two moves.** N4 (null) gives −1: the same 264 names, spelled `const.X`. B8 (bad) gives −1: a star import is rewarded. |
| coordinator_attrs | distinct `self.X` stores in the coordinator class | the breadth of the god object's state | **keep + modify** | Right sign on G3 −3, G5 −1, B4b +1. MISS on B4a and B4c: writes into a shared container, and writes by a module-level `f(coord)`, are invisible. Fix: count `coord.X` stores from any function in the package, and count stores *through* an attribute (`self.X[k]=`, `self.X.y=`, `self.X.append`) as writes to X. |
| coordinator_multiassigned_attrs | attrs stored by more than one coordinator method | shared mutable state, temporal coupling | **keep + modify** (the fix above, plus count write *sites* outside `_init_*`) | Right sign on G3 −3, G5 −1, B4b +1. **WRONG on B7 (−1)**: `_freq_last_write`'s writer left the class, so a hidden write reads as a decoupling. MISS on B4a and B4c. The prototype `coord_writers_multi` (writers in and out of the class) gives B7 0, G3 −2, G5 −1, B4b +1. |
| coordinator_loc | the coordinator's span | the size of the god class | **merge into max_class_loc** (identical in 30/30 columns) and **modify** as for that metric | See max_class_loc. |
| coordinator_methods | functions in the coordinator's class body, properties included | the number of responsibilities | **retire** → replace with a *coordinator footprint* | **WRONG 4 times.** G1 +1, G2 +1 and G4b +1 punish an extraction, a dedupe and a public accessor. B7 −5 rewards a move that decouples nothing. The tree already games it: `_fold_flow_lift`'s docstring (coordinator.py:801) says "a method here would cost `coordinator_methods`", so it was written as a free function over `coord`. The prototype `coord_footprint` counts logical statements in the class **plus** in every function whose first parameter is the coordinator. It gives G3 −65, B7 0, N1c/N2 0 and G1/G2 +1 (one call statement). |
| cross_seam_edges | `self.m()` calls inside the coordinator whose endpoints are in different seam-map buckets | coupling between the planned seams | **merge** with the cut_* rows into one `seam_cut_total`, then **modify** (below) | Right sign on G2 −1, G3 −3. **WRONG on B7 −7**, which beats G3's −3. **WRONG on N3 −2**, a one-line label edit with no code change. MISS on B2, G4a, G4b: out-of-class edges do not exist to it. |
| cut_dhw / cut_fetch / cut_grid / cut_learning / cut_views | per seam: cross-seam `self` attr refs plus method refs | the price of extracting that seam | **merge** into `seam_cut_total`, and **modify**: (1) treat functions `f(coord, …)` in any module as members of their seam, so their `coord.X` refs are charged; (2) compute against the ratchet base's `seam_map.json`, so a relabel in the same diff cannot lower the number, and send relabels through `--record` with a reason | **B7 beats G3** on cut_learning (−13 vs −8), cut_views (−8 vs −6) and cut_grid (−3 vs 0). N3 relabels one method and gets cut_learning **−21**; 100 of the 1,120 possible single relabels lower the table (`out/search_relabel.txt`). G5 +1 on cut_learning: the orchestrator reading a learning-owned record is priced as coupling. cut_dhw and cut_fetch moved in 1/30 cells. |
| dead_methods | class-body functions whose NAME is referenced nowhere; properties and HA conventions excluded | dead code | **keep as a quality ratchet, not in the architecture score**; **modify** to resolve by receiver (`self.m` and `coord.m` against the owning class, as `bound_references` does for top-level symbols) and to include properties | B5a +1 OK. B5b property 0 (known). B5c 0: the name `summary` is used on another class. B5d +1 for a two-method dead island (should be +2). These are documented limitations, now measured. |
| dead_top_level_symbols | top-level symbols no resolved load reaches | dead code | **keep as quality, not architecture**; **modify**: resolve `from m import *` | B5e +1 OK. **B8 +42: false positives.** 42 const symbols that the coordinator uses through a star import are reported dead. |
| duplication_blocks | rows of at least 10 identical normalized *lines* shared by two functions **of the same module** | copy-paste logic | **keep + modify**: statement-level AST windows (string literals blanked), package-wide, counting clone *pairs*, not rows; recalibrate the window as #369 did | B1 cross-module clone: 0 (known #1738a). B1c the same clone in one module: +2. **N1b −2 on a reformat whose AST is identical.** 8 of the 14 baseline rows are parameter lists or keyword-argument lists (tariff `peak_cost`/`peak_cost_smooth`, thermal_model `simulate_step`/`_simulate_step_two_zone`, the kwargs blocks of `objective_batch` and `simulate_trajectory*`). The prototype `dup_pairs` (window of 2 statements, at least 30 nodes) gives G2 −1, B1 +1, B1c +1 and N1b 0. Two caveats: N4 gives +1, because `const.X` adds AST nodes and pushes one window over the threshold (normalize `mod.X` to `X` before counting); and the baseline is 107 pairs, with precision not yet measured. |
| functions_cc_over_15 / functions_cc_over_25 | functions with CC over 15 / 25, nested defs included | local complexity | **retire from the architecture score** (function-level quality). If kept, add a `params_over_10` guard | MISS in 4/4 targeted cells (G1, B3a, B3b, B3c). A threshold count did not move under any split of this tree. |
| internal_call_edges | `self.m()` occurrences inside the coordinator | intra-class coupling? | **retire** | No monotone relation to quality. **G1 +1 and G2 +1 punish an extraction and a dedupe; B7 −14 rewards the god-helper module.** It survives as the denominator of the retired `cross_seam_fraction`. |
| local_imports | function-scope Import/ImportFrom statements | hidden or cyclic dependencies | **retire** → replace with `import_cycle_modules` | B6, a real module-level cycle (the package's first), reads **0**. B6b, the same cycle as a local import, reads +1. 4 of the 7 baseline rows are stdlib `import time` in optimizer.py. The prototype `import_cycle_modules` (modules in a non-trivial SCC, local imports included; baseline 0) gives B6 +2 and B6b +2, and 0 for every other move. |
| max_cc | the largest CC in the tree | the worst local complexity | **retire from the architecture score**. As a quality metric, keep it only paired with `params_over_10` | **B3a −1 and B3c −14 (48 → 34)** come from meaningless tail-call chains. G1, the real extraction, gives 0. B3c's fragments take up to 32 parameters. `params_over_10` goes 28 → 34 on B3c and stays at 28 on G1. |
| max_class_loc | the largest class span in lines | the size of the god class | **keep (as the only size row) + modify**: logical statements, excluding docstrings and comments, and charge `f(coord)` free functions to the class (= `coord_footprint`) | **WRONG 4 times.** G1 +4 and G4b +4 punish good moves, N2 +5 is a docstring, and B7 −188 rewards the god-helper module, one line more than G3's −187. |
| max_method_loc | the largest function span, 0 below 150 | the worst function size | **retire from the architecture score**. As a quality metric, **modify** to logical statements | N1c **+38** from an AST-identical reformat. N2 +4 from a docstring. MISS on G1, B3a, B3b and B3c. The prototype `logical_max_fn` gives N1c 0 and N2 0. |
| methods_over_150 / methods_over_200 | functions over 150 / 200 lines | function size | **retire from the architecture score** | methods_over_200 is **WRONG on B3a −1, B3b −1, B3c −2** (pass-through chains). methods_over_150 is MISS in 4/4. Both are span-based, so they move on nulls just as max_method_loc does. |

### The four non-structure ratchets

- `coverage_budgets.json` — **not architecture.** Test adequacy (the percent of the package covered) is a
  quality constraint on the test suite. It says nothing about module boundaries.
- `typing_budgets.json` — **not architecture.** Counts of type-checker errors measure annotation hygiene.
  A god class can type-check clean.
- `mutation_budgets.json` — **not architecture.** Test *strength* (surviving mutants and unpinned sites) is a
  quality constraint on the tests.
- `stress_budgets.json` — **not architecture.** Runtime and RSS ratios per scenario measure performance, and
  a structural refactor should leave them flat.

## Verified metric defects that are NOT #1738 a/b/c or dead properties

1. **Ranking inversion: a move that does not decouple outscores one that does (extends #1738b).**
   #1738b says an out-of-class reach "moves nothing". Here the out-of-class move is *rewarded more* than the
   decoupled one.
   - G3 and B7 move the same five methods.
   - B7 beats G3 on 6 keys: cross_seam_edges −7 vs −3, cut_learning −13 vs −8, cut_views −8 vs −6,
     cut_grid −3 vs 0, internal_call_edges −14 vs −9, coordinator_loc/max_class_loc −188 vs −187.
   - G3 wins on only 2 keys: coordinator_attrs −3 vs 0, and multiassigned −3 vs −1.
   - B7 adds 37 private reaches (`private_reach` 110 → 147). G3 adds 0.
   - Null: N1 gives 0.
2. **Writes from outside the class disappear from the attr census.**
   - B7: multiassigned −1, because `_freq_last_write`'s second writer left the class.
   - B4c: 0, where B4b, the same attribute written in-class, gives +1 on both attrs and multiassigned.
   - Null: N1 gives 0.
3. **In-place mutation of a long-lived shared object is invisible.** B4a writes two per-solve keys into
   `self._current_action` before an executor await. Every row reads 0 except the +2 span.
4. **duplication_blocks depends on formatting and mostly measures argument lists.**
   - N1b is an AST-identical re-wrap of one signature, and it reads −2.
   - 8 of the 14 baseline rows are parameter lists or keyword-argument lists.
5. **The span metrics move on nulls.**
   - N1c, an AST-identical reformat, gives max_method_loc +38.
   - N2, a docstring, gives max_method_loc +4, and coordinator_loc/max_class_loc +5.
6. **const_modules_over_50 measures how an import is spelled.**
   - N4, a null: −1.
   - B8, a star import that makes the code worse: −1.
7. **A seam-map edit alone lowers the cut table.**
   - N3 changes one label with no code change: cut_learning −21, cross_seam_edges −2.
   - 100 of the 1,120 single relabels lower `sum(cut) + cross`.
8. **Meaningless pass-through chains are rewarded.**
   - B3c: max_cc 48 → 34 and methods_over_200 −2. Its fragments take up to 32 parameters, while G1 (a real
     extraction) gets 0 on these rows.
   - B3a: max_cc −1 and methods_over_200 −1.
   - The docstring's `sum_cc` refusal anticipates decomposition. It has no guard against splits that
     decompose nothing.
9. **Good local refactors are penalised.**
   - G1 (Extract Method): coordinator_methods +1, internal_call_edges +1, loc +4.
   - G2 (dedupe): methods +1, edges +1.
   - G4b (a new public accessor, which is counted as a method): methods +1, loc +4.
   - G5 (a frozen record passed from the orchestrator): cut_learning +1.
10. **dead_top_level_symbols cannot resolve `import *`.** B8 reports 42 live const symbols as dead.
11. **No metric sees import cycles.** B6 creates the package's first module-level cycle and every row stays
    at 0. local_imports prices only the local-import spelling of it (B6b +1).
12. **Documented limitations, now measured.**
    - dead_methods is blind to name collisions: B5c gives 0.
    - It counts only the root of a dead island: B5d gives +1 for 2 dead methods.

## Artifacts

- `perturb/*.py`: 30 perturbation scripts and shared helpers (`_lib.py`, `_freq_common.py`,
  `_b1_common.py`), plus `search_relabel.py`.
- `run_one.sh`: reset, apply, compile/import/ruff checks, measure.
- `build_matrix.py`, `matrix.tsv`, `matrix_wide.tsv`.
- `probes.py`, `run_probes.sh`, `probes.tsv`: prototypes of the proposed replacements.
- `out/`: per-perturbation metrics JSON, diffs and ruff deltas.
