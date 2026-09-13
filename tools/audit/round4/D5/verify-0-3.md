# D5 verification — verifier 3 of 3 (panel D5-0, round 4)

- **Worktree**: `/Users/timmalmstrom/.zcode/workspace/default/audit-r4-verify-D5-3`,
  detached at `0855277` ("Merge remote-tracking branch 'origin/main' into
  claude/13-dimension-audit-920935").
- **Baseline the finder measured**: `7dd68dd`. `git diff 7dd68dd..0855277` over
  `docs/configuration.md`, `custom_components/heatpump_optimizer/strings.json`,
  `translations/*`, `README.md`, `tests/README.md`, `tests/stress.py`,
  `tests/validate.py` is **empty** — no number in either finding is
  baseline-only; everything below was executed at the branch head.
- **Stance**: refute-first, per `tools/audit/briefs/verifier.md`. Other
  verifiers' output and the register's verdict columns were not read.
- **Own harness**: `tools/audit/round4/D5/verify3_own.py` (written by me; root
  rule `Path(".")` — run from this worktree's root only). It takes the shipped
  field set from the **production options-flow registry**, not from
  `strings.json`, and searches a doc corpus of its own construction.
- All numbers below are counts over file bytes or one import —
  contention-immune by construction. `load1` at my runs: 2.96–4.32 (quoted,
  not gated); the finder's was 7.67. Identical numbers at both loads.
  `thread_factor=1.0`, `swapins=0` on every run.

---

## D5-01 — configuration reference omits 15 of 200 shipped options fields

**Vote: verify (severity medium, as filed).**

### Finder's harness re-run

`PYTHONPATH=tests/hastub python3 tools/audit/round4/D5/options_placement.py`
at `0855277`: every RESULT identical to `RESULTS.txt` —
`sections_matched=21`, `rows_total=139`, `rows_misplaced=4`,
`fields_total=200`, `fields_undocumented=63`, `fields_elsewhere=35`,
`fields_nowhere=28`, **`labels_absent_distinct=15`,
`labels_absent_occurrences=34`**, `labels_checked=200`.
`--selftest` (rotate step→section map) moves `rows_misplaced` 4 → 139 as
documented.

### My own number (independent metric and code path)

`verify3_own.py` does not read `strings.json` as the definition of "shipped".
It imports `heatpump_optimizer.config_flow` and rebuilds the field set from
`_OPTION_FIELDS` (every static row, union over `when` predicates), the one
`_DYNAMIC` row expanded through `_questionnaire_fields()`, and the
`after_save` field `_options_schema` appends to every saving page:

```
RESULT v3_registry_steps=20      RESULT v3_registry_fields=200
RESULT v3_strings_steps_with_data=20   RESULT v3_strings_fields=200
RESULT v3_phantom_keys=0         RESULT v3_untranslated_keys=0
RESULT v3_labels_absent_distinct_reader=15
RESULT v3_labels_absent_occurrences_reader=34
RESULT v3_labels_absent_distinct_fulldocs=15
RESULT v3_labels_absent_occurrences_fulldocs=34
```

The 15 labels are, name for name, the finder's 15. My metric differs from the
finder's in two ways that both cut against the finding, and it survives both:

1. **The shipped set is the production registry, not the translations file.**
   Key-for-key parity in both directions (0 phantom keys that no flow renders,
   0 renderable keys missing from strings). `translations/en.json` and
   `translations/sv.json` (what HA actually loads) also carry exactly 200
   options data fields. There is no inflation in the 200.
2. **The haystack is every `docs/*.md` (15 documents), not the finder's
   7 reader docs.** The count does not move: 15/34 either way. Even the
   linter's own plan documents do not name these fields.

The README promise was confirmed present verbatim: "Every field and its range
is documented in [docs/configuration.…]" (`README.md`).

### Attacks, in contract order

- **Contention**: counts over bytes; identical results at `load1` 2.96 and at
  the finder's 7.67. Nothing timing-based to attack.
- **Wrong gate mode**: not a gate/mutant claim; N/A.
- **Grid artefact**: no grid; N/A.
- **Null control**: the labels arm's null control is the 185 of 200 labels
  that DO occur, plus two executed perturbations (below) that move the number
  in both directions. The sections/rows arm has its own `--selftest`
  (4 → 139). Controls present and passing.
- **Reachability in real Home Assistant vs a stub**: this was the strongest
  available attack — "strings.json lists keys the flow never renders, so the
  200 is phantom". It fails to refute: the production `_OPTION_FIELDS`
  registry plus `CONF_AFTER_SAVE` plus the questionnaire expansion is exactly
  the strings.json set, and `translations/{en,sv}.json` agree at 200. The
  fields are what the real options flow renders; no stub is involved anywhere
  in the measurement.
- **Severity earned by consequence**: medium stands. The README's explicit
  "Every field and its range" promise is false for 15 distinct labels; of
  them, 5 are covered in substance by combined rows (see correction below),
  and 10 have no field documentation anywhere — the four weekend/holiday
  schedule hours, the four external-heat detection fields (whose *mechanism*
  is prose-documented at `docs/how-it-works.md:818-833`, but with no unit,
  range, default or page anywhere), `After saving` on all 20 saving pages, and
  `What the control entity expects`, for which the doc offers the
  confusingly similar `What that set-point entity expects` — a *different
  field on a different page* (`space_setpoint_unit` vs
  `mixing_valve_write_target_kind`). Mitigation is real (every field carries a
  `data_description`; selector bounds render in the UI), which caps it at
  medium rather than high.

**Perturbations executed** (against a temp copy of the doc corpus via
`D5_DOCS_DIR`, worktree untouched):

- Forward, as filed: add `| After saving | Return to the section menu | menu /
  close | ... |` to the "Comfort and temperatures" table →
  `labels_absent_distinct` 15 → 14 and `labels_absent_occurrences` 34 → 14.
  Exactly the finder's prediction.
- Reverse, as filed: delete the `Buffer tank size` row(s) → **no movement**
  (finder's stated reverse perturbation is defective: a prose mention at
  `docs/configuration.md:411` keeps the substring alive). Deleting the prose
  mention too does move it: 14 → 15 distinct, 14 → 15 occurrences. Direction
  verified; the stated perturbation was incomplete.

**Corrections to the finder's triage (none move the headline number):**

- "Surcharge per kWh ... covered by the combined row whose Default/Range cells
  state VAT's range, not the surcharge's" is **wrong**: the registry gives both
  `CONF_PRICE_VAT` and `CONF_PRICE_SURCHARGE` the widget
  `_number(0.0, 2.0, 0.01)` with defaults `1.0` / `0.0`, so the doc row
  `| VAT multiplier / surcharge | 1.0 / 0 | 0–2 |` is accurate for both
  fields. Five of the 15 are covered in substance, not "four plus one with the
  wrong range". This works *against* the finding's severity, and it survives.
- The prose says "the three external-heat detection fields"; there are four
  (the table correctly lists four).
- The reverse perturbation defect noted above.

---

## D5-02 — tests/README.md states 48 stress combinations; the sweep is 51

**Vote: verify (severity low, as filed).**

### Finder's harness re-run

`PYTHONPATH=tests/hastub python3 tools/audit/round4/D5/test_doc_counts.py` at
`0855277`: `doc_stress_sweep=48`, `code_stress_sweep=51`, `mismatches=1`;
null controls agree exactly (`doc/code_stress_edges=17/17` — same sentence —
and `doc/code_validate_cases=22/22` — same list). Identical to `RESULTS.txt`'s
record for the D5-02 numbers (the finder's consolidated file does not repeat
these lines, but the report's numbers reproduce to the digit).

### My own number

`verify3_own.py` arm B re-extracts the annotations with my own regexes, calls
`len(stress.sweep_combinations())` itself, and counts `edges` and `run(...)`
with its own AST walk: `doc=48` vs `code=51`, `mismatches=1`, controls
`17/17`, `22/22`. Independently re-derived arithmetic:
7 seasons × (2 zoning × 2 dhw) = 28, + 14 feature combinations
(2 seasons × 8 − 2 skipped), + 3 buildings × 2 seasons = 48, + 3 zero-range
scenarios = **51**.

### History (is 48 stale, or never-true?)

`git log -S 'Zero-range bounds' -- tests/stress.py` lands on `2ab9b84`
("The stress gate can see a 2x regression, samples the zero-range bound, ..."
= #339, 2026-09-03). At `2ab9b84^`: SEASONS=7, BUILDINGS=3, no zero-range
block → implied sweep 48; at `2ab9b84`: 48+3 = 51. `git show
2ab9b84:tests/README.md` already said "48 combinations" at its line 229. So
the annotation was true until 2026-09-03 and stale ever since — through every
merge to the branch head. `tools/audit/README.md` in the same tree already
records the change ("was 48 before #286/#287's 3 zero-range-bounds
scenarios"); the tree knows, the developer doc does not. The in-code comment
at `tests/stress.py` ("Zero-range bounds (#286/#287)... three scenarios")
agrees.

### Attacks, in contract order

- **Contention**: counts; immune (identical at load1 2.96 and 4.32).
- **Wrong gate mode / grid artefact**: N/A.
- **Null control**: strong — two counts in the *same sentence/list* agree
  (17, 22), so the harness is not a general disagree-with-documents machine.
- **Reachability**: `sweep_combinations()` is a module-level function the
  gate itself runs (its docstring says so); importing it under
  `PYTHONPATH=tests/hastub` executes no solve. Real artefact, no stub.
- **Severity**: low is right — one stale word in a developer README
  annotation, correct number recorded in-tree elsewhere; hygiene class.

**Perturbations executed** (in-place, `git checkout --` restored after each;
worktree clean):

- Edit the annotation 48 → 51: `mismatches` 1 → 0, `code_stress_sweep`
  unmoved at 51. As filed.
- Add one entry to `SEASONS`: `code_stress_sweep` 51 → **55**, not the 54 the
  finder predicted. The finder's stated mechanism ("must rise by
  `len(BUILDINGS)` = 3") is wrong — a new season enters the
  `itertools.product(SEASONS, (False, True), (False, True))` loop and adds
  2 × 2 = 4 combinations; `len(BUILDINGS)` is irrelevant to that loop. The
  direction (rise, mismatch persists) holds; the magnitude and mechanism in
  the report are incorrect. Core claim (48 ≠ 51) unaffected.

---

## Defects found in the instruments (recorded, none changes a verdict)

1. `options_placement.py`'s stated reverse perturbation is masked by the
   prose mention at `docs/configuration.md:411` (executed: no movement until
   the prose is also removed).
2. The D5-02 report's SEASONS perturbation arithmetic is wrong (+4, not +3;
   executed: 51 → 55).
3. The D5-01 consequence table mis-states the surcharge row's Range cell as
   VAT-only; both fields share `0.0–2.0` (executed against
   `config_flow.py:1369-1370`).

My own harness had one bookkeeping bug on its first run (a code-only
diagnostic counted as a doc mismatch); fixed before any number was recorded
here.
