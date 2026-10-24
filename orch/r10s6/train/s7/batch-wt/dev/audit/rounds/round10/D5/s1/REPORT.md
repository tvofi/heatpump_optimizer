# D5-s1 — reader paths (D5.M1) over README.md and docs/**

Baseline 17f1c55fad1b. Seat cells: D5.M1 over README.md, docs/*.md.

## Method
Walked the three M1 readers (HACS install to first plan; feature configuration
for two-tank storage / ECL110 / capacity tariff; developer running the tests)
and turned each "go here, click this" instruction into an executable check
against what the production UI renders: manifest.json `name` (Add-integration
picker) and strings.json config/options `menu_options` (menu buttons). Internal
link targets and anchors were checked for every relative link.

## Findings
**D5-s1-01 (low, hygiene)** — docs name UI labels the UI does not show.
Harness `dev/audit/rounds/round10/D5/s1/ui_labels.py`: mismatches=5.
- docs/configuration.md:23 — "Add integration → Heat Pump Optimizer"; the
  picker shows manifest name "Heat Pump Cost Optimizer" (README.md:281 and
  docs/setup.md:48 have it right, so the docs contradict each other on the
  first step of reader path 1). "Heat Pump Optimizer" is the entry's default
  *title* (config_flow.py:1281), correct at configuration.md:241 only.
- README.md:356, docs/configuration.md:43, :164, docs/setup.md:70 — menu
  button "Enter thermal values directly (expert)"; strings.json
  config.step.building.menu_options.thermal is "Enter thermal values directly".
Perturbation: in memory append " (expert)" to that menu option -> 1.

## Non-findings
- Relative links: every file and anchor in README.md + docs/*.md resolves
  except docs/how-it-works.md -> ../dev/archive/backlog.md, removed by the
  finder wall (export artefact, not a defect).
- Settings-table first columns in configuration.md/setup.md/ecl110.md: 69 of
  313 not verbatim in strings.json; spot-checked 21 by difflib, all are the UI
  label minus a unit or "(optional)" suffix, or a merged pair — readable.
- Developer path: README.md:980 and architecture.md:299 both route to
  tests/README.md, which exists.

## Unfinished
- M1 feature paths checked only at label level; the dead-end/forward-reference
  narrative walk per paragraph was not exhaustively recorded.

## Exposure
Read README.md and docs/*.md (required by D5). Code comments cite earlier
finding ids; RELEASE_NOTES.md version claims not checked.
