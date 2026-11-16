# `enumerate.py`

- `enumerate.py` — prints one audit universe, one item per line, so a finder
  reports `universe=N examined=n` against a command and not a recollection.
  Path: `tools/audit/enumerate.py`; its docstring lists every universe and
  the rule each is read by. When: a dimension brief names it as a step's
  universe (D0, D1, D2, D8, D9, D12, D15, D16, D17; `d3-sites` and
  `d14-classes` are ported for the briefs that will cite them). Two universes are registers a round's register pull request
  appends to: `dev/audit/config/identities.json` (D2) and
  `dev/audit/config/bundles.json` (D15). `--ledger TSV` joins a seat's
  ledger to any universe, each line beside its asserting test or `not run`
  (rows: item, test; `d12-cells`: cell, source, test), and refuses a row
  that names no item, an unlisted source or no test. Refusal: exit 2 on a missing
  source or an empty universe, never a pass. `--self-test` plants a fake
  repo per universe, deletes one item and empties the source: the null
  control.
