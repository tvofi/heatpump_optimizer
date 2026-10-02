R9-F10.4 precursor: the brief_lint 931dffe `coordinator_loc` pin holds only while `coordinator_loc` is a budget key.

Part of #1738; Part of #201

Before: `brief_lint.mjs` requires an error for the 931dffe fixture's literal `coordinator_loc 10394 <= 10394`. The metric rule resolves that word against `tests/structure_budgets.json`, so the error fires only while `coordinator_loc` is a budget key. R9-F10.4 (#1838) retires the key (#1738, decision R3-2 merges it into `max_class_loc`). CI runs the base's linter (decision 0013), so on #1838 the base linter reports `FIXTURE VACUOUS: [W1-G8] metric: coordinator_loc`, and `briefs` cannot go green from inside that PR.

After: the pin carries `whileBudgetKey: 'coordinator_loc'` and is required only while that key exists. On main it still exists, so main's required count stays 10 and nothing changes here. Once #1838 merges, the count drops to 9. `methods 255` and `attrs 176` keep the literal-metric rule pinned either way.

How: `assertAcceptanceFixture` filters the required list to the pins whose `whileBudgetKey` is absent or present in `budgets()`, checks the missing ones against that list, and prints its length.

## Head

b69961d780511b29af6e8d454c4ff829ec340783

## Mutation proof

- With the literal-metric rule switched off (`const metric = null && resolveMetricName(m[1])`), the fixture check on main's tree fails: all three W1-G8 pins (`coordinator_loc`, `methods 255`, `attrs 176`) are reported missing, and the run exits 1. The `whileBudgetKey` filter therefore cannot hide a broken rule while the key exists.
- Without the filter, run over R9-F10.4's tree (which retires the key), the linter exits 1 with `FIXTURE VACUOUS ... [W1-G8] metric: coordinator_loc`. That is the failure this change removes.

## Null control

On main's tree, the unmodified linter exits 0 with `FIXTURE ok: 15 error(s) pin the 931dffe acceptance (10 required)`. This head prints the same line, also with exit 0.

## Figures

- 931dffe pins (10 required at this head): `node .claude/workflows/brief_lint.mjs`

## Red checks

none

## Forward-carry

none

## Friction

- `gate-scoping: cost`: CI pins `.claude/workflows/*.mjs` to the base (decision 0013), so a linter change that a retiring PR needs has to land first, as its own PR. #1838 found this only from its red `briefs` run.

_Requested by **tvofi**_
