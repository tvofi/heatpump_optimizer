# D5-s7: round 11, dimension D5, cells tests/f*

Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B12. Cells (`check_scopes.py --seat D5-s7`):
`tests/features.py`, `tests/finite_boundary.py`, `tests/frontend.py`; steps M1 to M4.

## Method

- Enumerators: `bash dev/audit/rounds/round11/D5/s7/enumerators.sh M1|M2|M3|M4`, which wrap
  `tools/audit/text_ledger.py` over the seat's cells. M1 = 0, M2 = 0, M3 = 0 (the cells hold no
  Markdown or HTML document), M4 = 4030 units (3863 + 143 + 24; 3402 comment blocks, 628 docstrings).
- M4: `m4_comments.py` rows every unit in `ledger.tsv` with an executed battery:
  - C2: every backticked or snake/Camel-case name and every path the unit uses as code is looked up
    among the code tokens of the live tracked tree. Comments and docstrings are excluded, so a
    comment never vouches for itself. Each miss is triaged in `triage.tsv`: a Home Assistant or
    library name, a formula term, an example or a harness cell resolves; the rest fail.
  - C5: the unit is split into paragraphs at rules, list items and per-line trailing comments,
    then into sentences with `text_ledger.sentences`. A sentence over 40 words fails.
  - C1 numbers (carry C7): each cited decimal or unit-bearing number is matched to a code literal
    within 40 lines above to 120 lines below, allowing x60, x3600, x4, x1000, x100, x24, x0.25
    and x96 conversions. An unmatched number makes the row `unverifiable`.
  - C1 traced: the docstring at features.py:6856 states a count. `c1_sleep_count.py` measured it by
    counting `time.sleep(0.002)` calls per caller over the 50 golden solves.
- Null control: `text_ledger.py check --plant` returns units=4030 rows=4030 unrowed=0 orphan=0
  malformed=0 plant_refused=1 (`check_plant.out`). `--perturb plant` raises c2_fail by 1.

## Findings

| id | file | false rows | what |
|---|---|---|---|
| D5-s7-01 | tests/features.py | 454 | C1 (1): "the eight between-run sleep(0.002) calls" (features.py:6856). The measured count is 3 to 34 per solve; 2 of 50 solves read 8. C2 (3): `tools/audit/w5-partition/partition.py` (57049) moved to tools/coverage/ in 3b0a39216b; `_feedback_sent` (86177) was never defined; `PlantRig` (54592) is in no tracked file. C5 (450): longest sentence 177 words (54710). |
| D5-s7-02 | tests/finite_boundary.py | 14 | C5 only; longest sentence 94 words (1018) |
| D5-s7-03 | tests/frontend.py | 3 | C5 only (lines 1, 43, 226); longest sentence 52 words |

Perturbations, all in memory:

- `--perturb fix-path` (the one-line comment edit at 57049): c2_fail goes from 3 to 2.
- `c2-define`: c2_fail goes to 0.
- `c5-split`: total false rows go from 471 to 4.
- `c1_sleep_count.py --perturb` (one more start per call): between-run calls per solve go from
  3..34 to 4..41, and the number of solves reading eight goes from 2 to 0.

All findings are severity low, class hygiene, class_guess `new`.

## Non-findings

- C2 holds for finite_boundary.py and frontend.py: 0 failures over 125 references.
- In features.py, 2109 references leave 3 failures after the triage.
- 908 of 1164 cited numbers match a nearby code literal.
- The source has 3 `sleep(0.002)` sites, called from `_lbfgsb_restart`, `_multi_start_minimize`
  and `_optimize_with_dhw`.

## Not finished

- 82 units remain `unverifiable`, listed in REPORT.json's not_reached. Their only open item is a
  cited number with no code literal nearby.
- 71 false-row units carry such numbers too (see detail.tsv, `C1n`).
- C3 (restatement) and C4 (history over half) were not judged per unit.

## Round-10 carries

- C1: M3 has a denominator, 0.
- C4 and C5: examined; the universes are empty for these code cells.
- C6: the 628 docstrings are rowed in M4.
- C7: examined in these cells. The www/*.js and README/docs parts are leads to D5-s4 and D5-s2.
- C2 and C3: not reached here; they are in docs/ cells, with leads to D5-s1 and D5-s2.

## Exposure

Test comments cite earlier finding ids (R6-D9-01, D12-s2-02 and others) and round harness names.
These were read as context only. No docs/ and no GitHub were read.

## Harnesses

- `m4_comments.py`
- `c1_sleep_count.py`
- `enumerators.sh`
- `triage.tsv`

Outputs: `ledger.tsv`, `detail.tsv`, `m4_comments.out`, `check_plant.out`, `perturb_*.out`,
`c1_sleep_count*.out`.
