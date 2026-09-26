# Sweep: "selector minimum off its own step grid"

Round 9, D14 sweep, thread S7. Baseline `1936d5ca`. Finding: D4-s2-05
(verified, low). Not a ledger class (new).

## Enumerator

The finder's own `tools/audit/round9/D4/s2/step_grid.py` (already committed
on this branch) already is the widened enumerator D14.md step 3 asks for:
it renders every `NumberSelector` of both the config and options flows
(defaults arm, and the derived arm after the building questionnaire stores
computed values) through a real Chromium `<input type=number>` and reads
`validity.stepMismatch`. This sweep did not re-run it: its Node half
(`step_grid.mjs`) needs `playwright`, which is not installed in this cloud
seat's box and is a heavy Playwright-driven check, so per tvofi's
no-heavy-D3/D9-rerun rule (extended here on the same reasoning: expensive,
shared-box, browser-driven measurement) this sweep reuses the finder's own
recorded run rather than re-installing a browser stack for a class already
capped at N=1 by the brief.

`tools/audit/round9/D14/sweep/selector_min_off_step_grid/enumerate.py`
(this dir) is a lighter static cross-check attempted first: it regexes
`NumberSelectorConfig({...})` literal blocks for a hard-coded `min`/`step`.
It found 0, because every call in `config_flow.py` goes through a shared
`_number(minimum, maximum, step, ...)` helper (the finder's own
"Instrumented symbol" line) whose arguments come from named constants
(`RANGE_*`, `POSITIVE_PARAM_FLOOR`) resolved only at render time — exactly
why the finder needed a rendered-DOM check rather than a static one. Left
in place as a non-finding (0 static hits), not deleted, so a later sweep
does not repeat the same dead end.

## Positive control

Finder's own run (`REPORT.md` D4-s2-05, cited verbatim):

```
$ OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub python3 tools/audit/round9/D4/s2/step_grid.py
-> 8 defaults + 4 derived (count) = 12
```

e.g. `slab_thermal_mass` 5 with min 0.1 step 0.5 -> spinner gives 5.1, not
5.5; `upper_floor_heat_loss` 0.08 with min 0.001 step 0.01 -> 0.081.

## Null control

Finder's own: `off_grid_slider_fields=0` — the 42 slider-mode fields, whose
minimum sits on their own grid, report none. Confirms the detector does not
over-count fields that are already fine.

## Perturbation

Finder's own: `"step": step,` -> `"step": step if slider else "any"` (the
fix shape, applied in memory) takes both arms to 0.

## Baseline vs main

`custom_components/heatpump_optimizer/config_flow.py` is unchanged between
`1936d5ca` and `origin/main`. All 12 seams still exist on main.

## Disposition

12 box-mode `NumberSelector` fields (8 at their shipped defaults, 4 more
once the building questionnaire's derived values are stored) are
**instance** (one finding, one mechanism: `_number`'s min/step contract,
per COMMON.md's phenomenon-grouping rule). The 42 slider-mode fields are
**not applicable** (sliders render no `<input type=number>`, so
`stepMismatch` cannot apply to them — the finder's own null control).

## Count

N = 1 verified finding + 0 sweep-confirmed instances (the finder's own
enumerator was already the full widened enumeration; this sweep adds no
new seams, only re-confirms via citation) = **1**. **rca: false**, matching
the brief.

## Barrier proposal

None built (N < 3). The finder's own: `config_flow._number` sets
`"step": "any"` for box-mode fields, or move each `RANGE_*`/
`POSITIVE_PARAM_FLOOR` minimum onto its field's step grid — left for the
fixer.

## Gate seconds

Static cross-check: ~0.01s (0 hits, non-finding). Full rendered check (not
re-run): finder's own cost, not re-measured here.
