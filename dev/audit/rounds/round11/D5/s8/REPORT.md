# D5-s8 — round 11, dimension D5 (code comments in tests/{a,b,c,d,g}* and tools/policy/**)

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`, box B12 (light seat). Cells: 44 files, as
`tools/audit/check_scopes.py --seat D5-s8` prints them (`cells.txt`), steps M1-M4.

## Method

- Enumerators: `enum_steps.py --step M1|M2|M3|M4` (the brief's `text_ledger.py outline` / `units`
  over the cells). M1, M2 and M3 print 0 lines: every cell is code (.py/.mjs/.js/.sh), and `outline`
  prints no row for a non-document. M4 prints 3628 units.
- M4: `m4_ledger.py` rows every unit (`ledger_m4.tsv`). Per unit it extracts each repo path,
  bare file name, `path:symbol`, `path:line`, and backticked or called identifier, and resolves it
  against `git ls-tree`/`git grep -w` at the ref, with comments stripped from the code corpus (C2).
  It also measures the longest sentence after splitting at blank, list, usage and indented lines
  (C5). The 81 unresolved units it first printed were read one by one. 56 of their references are
  adjudicated in its `ADJ` table: fixtures, examples, generated artefact names, history sentences
  and citations pinned to a SHA or branch. That leaves 25 stale units.
  `text_ledger.py check --plant` gives units=3628 rows=3628 stale=25 true=1114
  unverifiable=2489 unrowed=0 orphan=0 malformed=0 plant_refused=1 (`check_m4.out`).
- Redispatch C7: `numbers_adjacent.py` checks each number a comment cites against the numeric
  constant the comment sits on. It finds 28 pairs and 8 candidates. All 8 were read and none
  contradicts its constant.
- Walking to the stale rows exposed an instrument defect, `ledger_lines.py` (D5-s8-07).

## Findings

| id | file | number | perturbation |
|---|---|---|---|
| D5-s8-01 | tools/policy/policy_lint.mjs | 12 stale units (usage lines `node .claude/workflows/policy_lint.mjs`: Cannot find module; corpus_excluded.json path contradicts `CORPUS_EXCLUDED_DATA`) | respell one path: 11 |
| D5-s8-02 | tools/policy/friction_issues.mjs | 1 unit, 3 usage lines on a missing path (node exit 1; tracked path --self-test exit 0) | respell: 0 |
| D5-s8-03 | tests/closure.py | 5 stale units (coverage_tree.sh x2, governance_cost.py loader path, docs/delivery, carry-1922.json) | respell one: 4 |
| D5-s8-04 | tests/doc_claims.py | 3 units citing untracked design notes / CONDENSED.md | drop one: 2 |
| D5-s8-05 | tests/card.mjs | 4 units citing untracked card_shapes.mjs / DESIGN.md | drop one: 3 |
| D5-s8-06 | all cells | 657 units (870 sentences) over 40 words; longest 524 (deployment_shape.py docstring); leave-one-out 44 files, 0..150, 507 without policy_lint.mjs | drop one: 656 |
| D5-s8-07 | tools/audit/text_ledger.py:scan_c_like | 1175 of 1899 JS comment units carry a wrong `line` | one-line fix: 0; Python null 0/1200 |

Each finding is in `findings/<id>.json`, and its stale rows are in `m4_stale_rows.txt`.
D5-s8-01 to D5-s8-05 follow D6 step 3: one finding per file holding a stale row. D5-s8-06 is one
phenomenon across the cells (COMMON.md, group by phenomenon). D5-s8-07 is an instrument defect met
by this step (dev/audit/README.md), so it is a finding of D5. The file sits in D5-s6's cells, so a
lead goes there as well.

## Non-findings

- 0 unresolved identifiers across 2906 references. The planted control caught both planted
  identifiers.
- 0 number-vs-constant contradictions over 28 pairs.
- Python line numbers: 0 of 1200 mislocated.
- `agreement_py.py`'s `tools/seat/` comment is true of its code. The code itself is a lead.

## Not finished

- M4: C1 behavioural truth was not executed for 2489 units (verdict `unverifiable`: they name no
  path or symbol), nor beyond resolvability for the 1114 `true` rows. C3 (restatement) and C4
  (history over half) were not measured. `deployment_shape.py`'s 524-word census history is an
  obvious C4 case for the next pass.
- M3 C6: the docstrings' mechanism paragraphs were not traced against their code paths.
- Redispatch items outside these cells, sent as leads: C2 (D5-s1), C3 (D5-s2), and C7's www and
  README/docs parts (D5-s4, D5-s2).

## Harnesses

`m4_ledger.py`, `ledger_lines.py`, `numbers_adjacent.py` and `enum_steps.py`. Each header carries
its command, expected value and perturbation. Every number here is a count, so none is
provisional.

## Exposure

No `docs/` file was read. The comments cite earlier ids (R9-*, R10-*, D11-s1-03, #issues) as
context. The ref's file listing printed round-10 evidence file names; their contents were not
opened.
