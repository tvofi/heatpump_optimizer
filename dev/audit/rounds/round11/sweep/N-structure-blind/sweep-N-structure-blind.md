# Class sweep, round 11: N-structure-blind

Baseline: `origin/handoff/audit-r11-register` at 28b864af. Ledger status: `barriered` (tests/structure.py
on the PR gate, the archscore rows of tests/ci_budgets.json on ci-ratchet). The judged findings
(D7-s1-01..04, D7-s3-05) are all shapes that pass that barrier; this sweep finds three more.

**Property.** Every structural ratchet row moves when the property it gates grows, whatever the code's
spelling.

## Enumerator

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep/blind_rows.py`

The seam universe is every row of `tests/structure_budgets.json` (18), plus the properties the findings
showed no row holds. Each probe plants the gated property twice into a temporary copy of the package:

- **canonical**, in the shape the row keys on: the row must move, so the row is live and the plant is real;
- **respelled**, the same property in another spelling.

A row is `BLIND` when the canonical plant moves it and the respelled one moves neither it nor any of the
25 `archscore.*` rows in `tests/ci_budgets.json`, which are measured under every plant as the second reader.
Each plant is live: an `assert` loads it, so the dead-code rows do not move because of the plant itself.
The no-row properties are re-run with the finder's own census arms (`D7/s1/m1_ratchet_census.py`,
`D7/s3/m6_inner.py`).

- **Positive control** (`positive_control.txt`): every judged finding is re-found.
  - D7-s1-01 `const-respell`: the row goes 3 → 2 while any-spelling stays at 4.
  - D7-s1-02 `clone-same-fn`: the row stays at 8 while in_function goes 6 → 7. Null: `clone-two-fns` goes 8 → 9.
  - D7-s1-03 `unused-import`: 14 → 15, with 0 rows off budget.
  - D7-s1-04 `module-growth`: unpriced 2981 → 4404, with every row flat. Null: `class-growth` moves
    class_excess_loc.
  - D7-s3-05 `m6_inner --perturb`: planted_delta = 1.
- **Null control** (`run--null.txt`): `--null` plants a comment on both arms and every delta is 0.
- **Perturbation**: each canonical plant is the one-def re-introduction.
  - P3 max_cc 44 → 51.
  - P4 dead_top_level_symbols 1 → 3.
  - P5 import_cycle_modules 0 → 2.

`run_baseline.txt` has all seven probes. Its P3 line predates the fix that makes the module-level plant's
globals read: the archscore rows that moved there moved because those globals were unread, not because of
the branches. `run_P3_fixed.txt` is the P3 reading.

## Dispositions

### instance (8; 3 beyond the findings)

| seam | finding | probe |
|---|---|---|
| `structure.measure` const_fanout (`const_modules_over_50`) | D7-s1-01 | m1 `--perturb const-respell` |
| `structure.duplicate_clones` / `archscore counters.gapped_clones` | D7-s1-02 | m1 `--perturb clone-same-fn` |
| no unused-package-import row | D7-s1-03 | m1 `--perturb unused-import` |
| `class_excess_loc`, no module-span row | D7-s1-04 | m1 `--perturb module-growth` |
| no dead-state row (params, locals, attributes, fields) | D7-s3-05 | `m6_inner.py --perturb` |
| **`cyclomatic_complexity` over `all_functions`** (max_cc, functions_cc_over_15/25) | beyond | P3. 50 branches in a def move all three rows. The same 50 branches at module level move nothing in structure or archscore. In the tree, store.py's module-level `DOMAINS` table (store.py:328) carries ~30 decision points that no row prices (m1: module_level_cc_max 33). |
| **`bound_references`/`is_dead_symbol`** (dead_top_level_symbols) | beyond | P4. Two unreferenced defs move it 1 → 3. Two defs that only call each other move nothing: liveness here is any Name load, not reachability from production roots (dead_members is reachability, for methods only). |
| **import graph of `import_cycle_modules`** (relative `ImportFrom` only) | beyond | P5. `from . import ledger` in const.py moves it 0 → 2. The same import spelled absolute, a real load-time cycle, moves nothing. `importlib.import_module`, used in the tree at `__init__.py:90` and `optimizer.py:1465`, is unseen too. |

### guarded

- `coordinator_private_reach`: a literal `getattr` is counted. A computed-name `getattr` (P1) moves
  `archscore.computed_attr_access` 27 → 28.
- `coordinator_attrs`, `coordinator_multiassigned_attrs`: a literal `setattr` is counted. `vars(x)[k] =` and
  `x.__dict__[k] =` (P2) move `archscore.reflective_writes` 10 → 12.
- `max_method_loc`, `methods_over_150/200`: `all_functions` walks nested defs, so P6's nested 250-line def
  moves both rows.
- `dead_methods`: reachability with the counting-rule self-check (#1686, #1738). The untyped shared-name
  shape (P7) moves `name_kept_members` 38 → 40.
- `seam_cut_total`: priced by `CoordinatorRoles` over the declared seam map; m1 `seam-relabel` moves it.

### not applicable

- `name_kept_members`: it is the printed count of the shape `dead_methods` cannot measure, the guard itself.
- `max_class_loc`: a max over class spans. Lines moved to another class are a split, which
  `class_excess_loc` prices per class; lines moved out of any class are D7-s1-04's seam.

## Barrier (proposed)

Each of the three blind shapes has a cheap in-tree fix in `tests/structure.py`, recorded at today's value so
the row only falls:

- **Module-level complexity**: score each module's top-level statements as one unit through
  `cyclomatic_complexity`.
- **Dead top-level symbols**: compute liveness by reachability from the production roots `dead_members`
  already uses, extended to top-level defs.
- **Import cycles**: add level-0 `ImportFrom`/`Import` of the package's own dotted name and literal
  `importlib.import_module` targets to the import graph.

The counting-rule self-check should also plant one example per shape. Cost: no new pass, since all three
reuse trees `measure()` already builds.
