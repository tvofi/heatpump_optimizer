# D5 verify-0-1 — verifier 1 of 3, panel D5-0, audit round 4

- **verifier tree**: `/Users/timmalmstrom/.zcode/workspace/default/audit-r4-verify-D5-1`,
  detached HEAD `0855277` (`claude/13-dimension-audit-920935` head, "Merge remote-tracking
  branch 'origin/main' into claude/13-dimension-audit-920935")
- **baseline cited by finder**: `7dd68dd327fe3dbfb09f3bd0fe38910c58877697` (25 commits
  behind my HEAD). `git diff --stat 7dd68dd..HEAD -- docs/configuration.md
  custom_components/heatpump_optimizer/strings.json tests/README.md tests/stress.py
  tests/validate.py README.md docs/ecl110.md` is **empty**: every file either finding
  measures is byte-identical baseline-to-head, so no number can be baseline-only.
- **machine**: the shared audit box (Apple M1, 8 core, macOS 25.6); `load1` ran 3.2–7.6
  across my runs — irrelevant, every number below is a count over file bytes or one
  builder call, contention-immune by construction. No timing or memory number is cited.
- **interpreter**: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`,
  `PYTHONPATH=tests/hastub`, always from the worktree root. Installed nothing.
- **own harnesses**: `tools/audit/round4/D5/d5_own_D5-01.py`,
  `tools/audit/round4/D5/d5_own_D5-02.py` (both root-rule `Path(".").resolve()`, i.e.
  they measure the tree they are run from — run from this worktree).
- **stance**: refute-first. Both findings survived every attack I could mount; two
  defects in the findings' *stated perturbation prose* were found and are recorded
  below (they do not move the measured numbers).

---

## D5-01 — configuration reference: 15 of 200 shipped options labels named nowhere

### Finder harnesses re-run, exactly per headers

`options_placement.py` (also `--list`, `--selftest`), `d5_doc_structure.py` (+`--selftest`),
`reader_paths.py` (+`--selftest`), all from the worktree root:

```
options_placement.py          load1=3.32 thread_factor=1.0
RESULT sections_matched=21 sections_orphan=0 steps_undocumented=0
RESULT rows_total=139 rows_misplaced=4 fields_total=200
RESULT fields_undocumented=63 fields_elsewhere=35 fields_nowhere=28
RESULT labels_absent_distinct=15 labels_absent_occurrences=34 labels_checked=200
  --selftest: rows_misplaced=139 fields_undocumented=200   (control fires)

d5_doc_structure.py           load1=3.21
RESULT documents_walked=18 orphans=2 unreachable_reader_docs=0 level_skips=1
  --selftest: orphans=14                                      (control fires)

reader_paths.py               load1=3.21
RESULT tokens 101/201/35  deadends 0/0/0 total=0
  --selftest: deadends 3/3/3 total=9                          (control fires)
```

Every `options_placement.py` number matches `RESULTS.txt` at baseline exactly. Two
`d5_doc_structure.py` numbers moved vs the finder's export — `corpus` 14→17,
`reader_docs` 6→9, `level_skips` 0→1 — and I attacked whether that is baseline-only
tree drift: it is not. The finder ran in a preparation export that had **deleted**
`docs/audit-2026-08.md`, `docs/audit-2026-09.md`, `docs/backlog.md` (the harness
carries an `EXPORT_ABSENT` list for exactly these three); all three exist in git at
baseline `7dd68dd` and at my HEAD, so my full checkout sees 3 more reader docs and,
with them, one heading skip (`docs/backlog.md:30`, h1→h3). Export artefact, not tree
movement; none of the moved numbers is load-bearing for D5-01, which rests entirely on
`options_placement.py` over files that are identical baseline-to-head.

### My own harness, my own metric

`d5_own_D5-01.py`. Metric (deliberately different from the finder's): distinct
options-field labels from `strings.json options.step.*.data` whose text — one trailing
parenthetical stripped, case-folded, non-alphanumerics collapsed — occurs **nowhere**
in the folded concatenation of `README.md` **and every `docs/*.md` present** (globbed:
15 documents — the finder's haystack is a fixed list of 7 reader docs; mine is strictly
more generous, i.e. biased against the finding). My own table parser over
"Changing settings later" (exact folded title equality, no substring generosity).

```
RESULT own_corpus_docs=15 own_sections_matched=21 own_rows_total=139
RESULT own_fields_total=200 own_fields_no_row=65
RESULT absent_labels_distinct=15 absent_label_pages=34     load1=4.71 thread_factor=1.0
```

The 15-label set and the 20-page `after saving` are **identical** to the finder's,
label for label. The extra 8 documents I added to the haystack (audit register,
backlog, plan docs, HANDOVER) mention none of the 15. `own_fields_no_row=65` vs the
finder's `fields_undocumented=63`: definitional — I strip the trailing parenthetical
in the row-match arm too, which matches two fewer rows; the load-bearing arm is the
label-absence one, and it agrees exactly. Definitions written down for the judge:
finder = substring-in-fixed-7-docs; mine = substring-in-globbed-15-docs; same answer.

### Perturbations, executed on disk against the finder's own harness

1. **Forward (finder's stated perturbation)** — insert
   `| After saving | Return to the section menu | menu / close | Where the dialog goes after a save. |`
   after the last row of the "Comfort and temperatures" table:
   `labels_absent_distinct` **15→14**, `labels_absent_occurrences` **34→14**, exactly
   as the finding claims (also `fields_undocumented` 63→62, `fields_elsewhere`
   35→54: all 20 `after_save` fields become described, 1 in own section + 19
   elsewhere — internally consistent). Reverted.
2. **Reverse (finder's stated perturbation)** — delete the `Buffer tank size` row at
   `docs/configuration.md:375`: `labels_absent_distinct` **stays 15**,
   `labels_absent_occurrences` **stays 34**. The stated reverse perturbation is
   **wrong as worded**: the label survives at `:154` (setup walkthrough row) and
   `:412` (prose), so deleting one row cannot make it absent. What does move is
   `fields_undocumented` 63→64 and `fields_elsewhere` 35→36 — right direction, wrong
   named metric. My in-memory arm (`arm_drop_buffer_row_turns_absent=0`) agrees.
   The harness is nonetheless demonstrably live in both directions (arm 1 moves the
   labels arm; arm 2 moves the fields arm).

### Attacks

- **Ground truth by grep** (`grep -rli` over `README.md docs/*.md`): "Weekend day
  starts at", "Holiday day ends at", "Surcharge per kWh", "Temperature rise that
  counts as evidence", "After saving", "What the control entity expects" — zero hits
  each. The harness is not manufacturing absences.
- **Is "After saving" a field at all?** Worst case for the finding: if the navigation
  control is excluded, the count drops 15→14 distinct, 34→14 occurrences — still a
  finding; `docs/ecl110.md:86` ("All **eight** settings") counting settings
  *excluding* `after_save` while `heat_curve` ships 9 fields shows both readings
  coexist in the tree. Either way the finder's framing (name it, don't hide it) holds.
- **The 200 itself**: independently recomputed — 23 steps, 20 with data, no duplicate
  titles, sum of `data` over distinct step ids = **200**. The 21st matched section is
  the data-less `setup_overview` page; no section double-counts a step's fields.
- **Combined-row claims**: `docs/configuration.md:89` "Weekend daytime / night
  comfort" and `:331` "VAT multiplier / surcharge | 1.0 / 0 | 0–2" exist exactly as
  the finding describes (the range cell is VAT's, not the surcharge's).
- **The README promise exists**: `README.md:334-335` "Every field and its range is
  documented in [docs/configuration.md]" — the premise the metric falsifies.
- **"What that set-point entity expects" vs "What the control entity expects"**:
  both ship as distinct labels (`docs/configuration.md:337` documents only the
  former; the latter ships on the `building` page). Confirmed, not a fuzzy-match
  artefact — my harness's substring fold does not conflate them.
- **Mitigation claim**: re-checked per-step `step.<sid>.data_description.<field>`
  (my first probe looked at the wrong JSON level and I note that as my own error,
  corrected): all 15 fields carry a `data_description`. The finder's mitigation
  paragraph is accurate, and it caps severity at medium honestly.
- **Baseline-only?** No: all measured files identical at baseline and head.

### Vote

**verify**, severity **medium** (unchanged). Executed number:
`labels_absent_distinct=15` of `labels_checked=200` (`labels_absent_occurrences=34`),
reproduced by the finder's harness and by my own harness under a stricter,
more-generous corpus. One defect recorded for the judge: the finding's stated
*reverse* perturbation names the wrong RESULT lines (the labels arm cannot move while
`:154`/`:412` carry the label); the forward perturbation and its claimed 15→14 / 34→14
are exact.

---

## D5-02 — tests/README.md says 48 stress combinations; the sweep returns 51

### Finder harness re-run

```
test_doc_counts.py            load1=3.22 thread_factor=1.0
RESULT doc_stress_sweep=48  code_stress_sweep=51   -> MISMATCH
RESULT doc_stress_edges=17  code_stress_edges=17   -> matched
RESULT doc_validate_cases=22 code_validate_cases=22 -> matched
RESULT counts_checked=3 mismatches=1
```

Exact reproduction, including the two null controls in the same sentence/list.

### My own harness, my own metric

`d5_own_D5-02.py`. Metric: the integer preceding "combinations" on the
`tests/README.md` line annotating the stress.py command, extracted by my own regex
(`stress\.py[^\n]*#\s*(\d+)\s+combinations`), against `len(stress.sweep_combinations())`
executed directly, with an arithmetic decomposition re-derived from the loops in
`sweep_combinations()` itself: `len(SEASONS)*4 + 2*7 + len(BUILDINGS)*2 + 3`.

```
RESULT doc_sweep=48 code_sweep=51 code_sweep_decomposition=51 mismatches=1
RESULT control_edges_code=17 control_validate_code=22       load1=7.19 thread_factor=1.0
RESULT seasons=7 buildings=3
RESULT arm_add_season_delta=4 arm_add_building_delta=2 arm_doc_51_mismatches=0
```

51 = 7 seasons × 4 + 2 seasons × 7 non-empty feature flags + 3 buildings × 2 + 3
zero-range scenarios. The tree corroborates independently: `tools/audit/README.md`
records "The 51-combination sweep (`sweep_combinations()`; was 48 before #286/#287's
3 zero-range-bounds scenarios)", and `tests/stress.py`'s own comments document the
three added scenarios. `tests/README.md:356` is the only live doc still saying 48.

### Perturbations, executed on disk against the finder's own harness

1. **README 48→51**: `mismatches` **1→0**, `code_stress_sweep` unmoved at 51 — exactly
   as the finding claims. Reverted.
2. **Add one entry to `SEASONS`** (`"zzz_fabricated": ("flat", "winter_cold")`):
   `code_stress_sweep` **51→55** (+4), `mismatches` stays 1 with the gap widening
   (48 vs 55). The finding's stated magnitude — "must rise by `len(BUILDINGS)` = 3,
   to 54" — is **wrong**: a season feeds the 2×2 two_zone×dhw product (+4), not the
   buildings loop; `len(BUILDINGS)` entering the sentence at all is a copy error.
   Direction and the mismatches-stay-1 invariant hold; my in-memory arms agree
   (+4 season, +2 building). Recorded as a defect in the finding's perturbation
   prose; the measured 48-vs-51 is untouched by it.

### Attacks

- **Null controls**: 17 edge cases and 22 seasonal scenarios re-derived by my own AST
  walks — both agree with the doc. A harness that disagreed with documentation in
  general would have flagged these.
- **Is 51 the number the gate runs?** `sweep_combinations()` is a module-level
  function whose docstring says it exists precisely so harnesses "see exactly the
  list the gate runs"; I executed it. No dead-code objection available.
- **Scope**: `RELEASE_NOTES.md:6379` also says 48 — dated release history (48 was
  true at that release), append-only, not a live claim; it corroborates that the
  number was once right and went stale, which is the finding's class.
- **Baseline-only?** No: `tests/README.md` and `tests/stress.py` are byte-identical
  baseline-to-head.

### Vote

**verify**, severity **low** (unchanged). Executed number: `doc_stress_sweep=48` vs
`code_stress_sweep=51` (decomposition 51), `mismatches=1`. One defect recorded: the
stated SEASONS-perturbation arithmetic (+3/54) should read +4/55.

---

## Summary table

| id | finder number | my number | vote | severity | perturbation prose defects found |
|---|---|---|---|---|---|
| D5-01 | labels_absent_distinct=15 / occurrences=34 of 200 | 15 / 34 of 200 (own harness, 15-doc glob corpus) | verify | medium | reverse perturbation names the wrong RESULT lines (labels arm cannot move; fields arm does, 63→64) |
| D5-02 | doc 48 vs code 51, mismatches=1 | 48 vs 51, decomposition 51, mismatches=1 | verify | low | SEASONS perturbation magnitude mis-stated (+4 to 55, not +3 to 54) |

Both harnesses the finder shipped are live under perturbation in the direction that
carries each finding; the two prose defects above affect no measured number and no
vote.
