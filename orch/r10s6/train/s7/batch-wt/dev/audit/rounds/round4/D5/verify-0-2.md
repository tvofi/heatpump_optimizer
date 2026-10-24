# D5 verifier 2 of 3 — round 4, panel D5-0

- **tree**: `audit-r4-verify-D5-2`, detached at `0855277` (branch head
  `claude/13-dimension-audit-920935`). Baseline-to-head diff touches **none**
  of the files either finding reads (`docs/configuration.md`,
  `custom_components/heatpump_optimizer/strings.json`, `tests/README.md`,
  `tests/stress.py`, `tests/validate.py`, `README.md` all byte-identical to
  `7dd68dd`); only `docs/HANDOVER.md` and audit/plan/delivery docs moved, and
  `HANDOVER.md` is in neither harness's corpus. **No number is baseline-only.**
- **interpreter**: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`,
  `PYTHONPATH=tests/hastub`, always from the worktree root. Both harnesses use
  `ROOT = Path(".")`, so they measure the tree they are run from — I ran them
  from this worktree only.
- **contention**: every number below is a count over file bytes or one builder
  call. `thread_factor=1.0` throughout; `load1` ran 3.14–6.48 during my runs
  (box currently at 8.15/5.71/4.14 with other agents). No wall/CPU/RSS number
  is cited anywhere, so nothing is provisional.
- **my harness**: `tools/audit/round4/D5/verify-0-2-harness.py` (header per the
  contract; leaves both perturbed files restored byte-identical, verified by
  `git status` after every run).

## D5-01 — 15 of 200 shipped options labels occur in no reader document

### Re-run of the finder's harness

`PYTHONPATH=tests/hastub python3 tools/audit/round4/D5/options_placement.py`,
`load1=3.14`, `thread_factor=1.0`:

```
labels_absent_distinct=15  labels_absent_occurrences=34  labels_checked=200
fields_total=200  fields_undocumented=63  fields_elsewhere=35  fields_nowhere=28
```

Exact match to the finder on every line. `--selftest` fires for the placement
metrics (rows_misplaced 4 -> 139, fields_undocumented 63 -> 200) but **leaves
the labels arm untouched** (still 15/34), so that arm's control has to come
from the doc-edit perturbations below.

### My own harness, my own metric

Metric: distinct options-field labels from `strings.json` whose name does not
occur in the corpus, under three normalisations I wrote myself
(paren-stripped substring — finder-comparable; unstripped substring —
stricter; contiguous word-token match — independent of folding), each against
two corpora: the finder's six reader docs, and **every `*.md` at the repo root
and in `docs/`** (20 files: HANDOVER, plan-2026-09, audit-2026-09,
delivery-status adjacent docs, SECURITY, RELEASE_NOTES, DISCLAIMER, NOTICE
included).

```
my_fields_total=200                      my_absent_parenstrip_reader=15
my_corpus_generous_files=20              my_absent_parenstrip_generous=14
my_absent_unstripped_reader=47           my_absent_tokens_reader=15
my_absent_tokens_generous=14             my_absent_occurrences_reader=34
```

My 15 and 34 reproduce the finder's numbers from independently written code.

### Attacks, in contract order

1. **Contention** — counts over bytes; immune. Nothing timing-based to attack.
2. **Wrong gate mode** — not a gate claim; N/A.
3. **Grid/corpus artefact** — the analogue here is corpus selection, and it
   fails to break the finding: widening the corpus from 6 reader docs to all
   20 markdown files in the repository moves the count 15 -> 14. The single
   label cleared is `After saving`, which occurs **only** in
   `RELEASE_NOTES.md:2673` ("...the 'After saving' selector at the bottom") —
   release history, not a reader-facing reference, and incidental prose even
   there. 14 of 15 labels occur in **no markdown file in the repository at
   all**. The stricter unstripped normalisation raises the count to 47, so the
   finder's paren-strip is the generous direction, as their header claims.
4. **Null/positive control** — I ran the finding's stated perturbations on
   temp-edited copies (restored byte-identical afterwards):
   - **Perturbation A passes exactly**: adding the `| After saving | ... |`
     row to the Comfort table drives `labels_absent_distinct` 15 -> 14 and
     `labels_absent_occurrences` 34 -> 14 (one doc mention clears all 20
     page-occurrences of that label, since the haystack is doc-wide text).
   - **Perturbation B as literally stated FAILS**: deleting the
     `Buffer tank size` table row (one row, then both rows) leaves the number
     at 15/34 both times, because the label also survives in prose at
     `docs/configuration.md:412`. **Corrected perturbation B passes**: with all
     three occurrences neutralised (two rows + the prose), the number rises
     15 -> 16 and 34 -> 35. The metric is live and moves in the stated
     direction; the finding's *wording* of perturbation B ("delete the row")
     is imprecise. Recorded as a wording defect, not a metric defect.
5. **Reachability in real Home Assistant vs the stub** — no stub involved:
   `strings.json` `options.step.*.data` labels are exactly what HA renders in
   the options flow, and `after_save` is a genuine select
   (`config_flow.py:981`, choices menu/close) shipped on 20 of 23 steps (23
   steps = 21 field pages + 2 menus; 200 data fields — my own count). The
   user-visible surface the finding measures is the real one.
6. **Severity earned by consequence** — spot-checked the consequence table and
   it holds:
   - `heat_curve` ships **9** fields (`After saving` among them) while
     `docs/ecl110.md:86` says "All **eight** settings live on the options
     page".
   - The building step ships `external_heat_detection_enabled`,
     `external_heat_entity`, `external_heat_min_rise`,
     `external_heat_decay_minutes`; the wood-furnace section
     (`docs/configuration.md:378-388`) documents the tank sensors and fuel
     prices but none of the four detection controls — "evidence", "stove",
     "flue" occur nowhere in reader docs in a configuration sense.
   - `mixing_valve_write_target_kind` = "What the control entity expects"
     (strings.json:546) is a different field from the documented
     `space_setpoint_unit` = "What that set-point entity expects"
     (strings.json:402; doc row at configuration.md:337). Confusingly similar
     names, genuinely different fields.
   - The weekday pair "Day starts at"/"Day ends at" is documented
     (configuration.md:87-88); the **weekend and holiday variants** (8 shipped
     fields on `comfort`, my own enumeration) are covered only by the combined
     "Weekend daytime / night comfort" row (:89) for two of them and by
     nothing for the four hour fields.
   - The combined row "VAT multiplier / surcharge | 1.0 / 0 | 0–2" (:331)
     exists as described.
   - The promise the finding leans on is real and explicit:
     `docs/configuration.md:3` ("Every field the integration asks for...") and
     `README.md:334` ("Every field and its range is documented in
     docs/configuration.md").

   Mitigation is also real (`data_description` on every field; selector bounds
   render as slider limits) and the finder states it themselves. A broken
   "every field" promise in the designated reference, with 10 fields absent in
   substance on documented reader paths (two-tank detection, weekend/holiday
   schedule), with an in-form workaround — medium (hygiene) is the defensible
   ceiling and it is what was claimed. Not high (no wrong behaviour, in-UI
   help exists); low would understate a reference doc failing its one stated
   job for 7.5 % of its fields.

### Verdict D5-01

**verify**, severity **medium** (as claimed). My number 15 distinct / 34
occurrences / 200 checked, reader-doc corpus; 14/200 against every markdown
file in the repo; 47/200 under the strictest normalisation. One imprecision
noted: perturbation B must say "remove every occurrence", not "delete the
row".

## D5-02 — tests/README.md:356 says 48 combinations; the sweep returns 51

### Re-run of the finder's harness

`PYTHONPATH=tests/hastub python3 tools/audit/round4/D5/test_doc_counts.py`,
`load1=3.14`, `thread_factor=1.0`:

```
doc_stress_sweep=48  code_stress_sweep=51  -> MISMATCH (mismatches=1)
doc_stress_edges=17  code_stress_edges=17  -> agree
doc_validate_cases=22  code_validate_cases=22 -> agree
```

Exact match. The null control is strong: two other counts in the same
sentence/list agree, so the harness is not a blanket disagreer.

### My own harness, my own metric

Metric: my own regex for the `stress.py` annotation against
`len(sweep_combinations())`, plus a key-signature decomposition of the returned
list to prove 51 is computed and not a constant:

```
my_doc_sweep=48   my_code_sweep=51   my_sweep_mismatch=1
my_sweep_base=28        # 7 SEASONS x 2 zones x 2 dhw
my_sweep_feature=14     # 2 seasons x 7 on-combos of (tariff, pv, cycling)
my_sweep_archetype=6    # 3 BUILDINGS x 2 seasons
my_sweep_zero_range=3   # the #286/#287 scenarios
28+14+6+3 = 51
```

### Attacks, in contract order

1. **Contention** — counts and one builder call; immune.
2. **Wrong gate mode** — the symbol is the real gate path, not a stub or a
   vestige: `tests/stress.py:1938` (`main`) runs
   `combinations = sweep_combinations()` and `tests/run.sh:455` runs
   `tests/stress.py`; `:1250` re-iterates the same function for the budget
   check. The function's own docstring says it exists precisely so harnesses
   re-derive the gate's list.
3. **Grid artefact** — none; the decomposition above shows the 51 is structural.
4. **Null control** — present and passing (17/17, 22/22, re-derived by my own
   AST-free count of `validate.py` via my harness's independent path).
5. **Real vs stub** — no HA surface involved; developer doc vs test code.
6. **Severity** — one stale word in a developer README; the tree's own
   `tools/audit/README.md:81` already records the change ("was 48 before
   #286/#287's 3 zero-range-bounds scenarios"). The zero-range block landed in
   `2ab9b84` (2026-09-03, #339 implementing #286/#287; absent at its parent,
   present in it — verified by `git show` on both sides), and
   `tests/README.md` was last touched 2026-09-11 (#850) without fixing the
   number. **Low (hygiene) is exactly earned.**

   Perturbation check: the finding says adding one `SEASONS` entry must raise
   `code_stress_sweep` "by `len(BUILDINGS)` = 3, to 54". **Executed: it rises
   by 4, to 55** (a season adds 2x2 to the base grid; the archetype loop uses
   the literal `("winter", "shoulder")`, not `SEASONS`). Direction correct,
   `mismatches` stays 1 as claimed, `doc_stress_sweep` unmoved; the stated
   arithmetic is wrong. The reverse perturbation passes exactly: editing the
   README 48 -> 51 drives `mismatches` to 0 without moving `code_stress_sweep`
   (executed, restored).

### Verdict D5-02

**verify**, severity **low** (as claimed). My numbers: doc 48, code 51
(28+14+6+3), mismatch 1. One imprecision noted: the SEASONS perturbation is
+4/to 55, not +3/to 54.

## Files

- report: `tools/audit/round4/D5/verify-0-2.md` (this file, uncommitted)
- my harness: `tools/audit/round4/D5/verify-0-2-harness.py` (uncommitted)
- finder's harnesses re-run unmodified: `options_placement.py`,
  `test_doc_counts.py`
