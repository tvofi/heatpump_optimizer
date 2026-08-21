# Tests

These are plain scripts, not a pytest suite, so they can be run against a real
Home Assistant environment without extra tooling. They need `numpy` and
`scipy`; `validate.py` and `edge.py` do not need Home Assistant itself.

```bash
python tests/validate.py     # 19 seasonal scenarios, asserts invariants
python tests/edge.py         # degenerate inputs and boundary conditions
python tests/optimality.py   # checks the solver against cheaper challengers
python tests/plan_view.py    # plan sensor payloads, also writes /tmp/plandata.json
node   tests/card.mjs        # renders the dashboard card against that payload
```

`profiles.py` holds Nord Pool SE3 price curves and Swedish weather profiles for
winter, summer and shoulder season, used by all three.

- **validate.py** runs single-zone and two-zone houses through winter, summer
  and shoulder conditions, with and without hot water, and checks solver
  status, power bounds, per-step comfort bounds, savings range, hot water
  availability during demand windows, and how much energy lands in the most
  expensive quarter of the day. It prints `NO ISSUES` when everything holds.
- **edge.py** covers single-step and 48 hour horizons, flat/zero/negative
  prices, -25 °C and storm conditions, starting outside the comfort band, an
  overdue legionella cycle, a 1500 L tank, and a collapsed comfort range.
- **optimality.py** is a sanity check on solution quality rather than a pass/fail
  test. It compares the optimizer against a greedy cheapest-hours schedule and
  against random perturbations, and reports whether either beats it while
  still respecting comfort.

- **plan_view.py** runs a winter scenario and builds the payloads the two plan
  sensors publish, checking that the slot summaries reconcile with the raw
  step schedule. It writes the result to `/tmp/plandata.json`.
- **card.mjs** loads the Lovelace card in Node against a minimal DOM stub and
  the payload written by `plan_view.py`, so the card is exercised against real
  optimizer output rather than a fixture. It checks that the SVG renders, that
  all six series appear in the legend, and that toggling a series changes the
  chart and persists. Run `plan_view.py` first.
