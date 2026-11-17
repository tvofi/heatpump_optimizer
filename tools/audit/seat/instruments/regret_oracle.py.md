# `regret_oracle.py`

- `regret_oracle.py` — reads decision 0018's `regret` term. Path:
  `tools/audit/regret_oracle.py`; its docstring states every rule. When: a
  D0 seat's step 8 (`grid`, per cell of `enumerate.py d0-grid`, default the
  price x weather plane at `PLANE_LEVELS`), a D15 seat's step 9 (`installs
  --bundle LABEL=PATH`, per line of `enumerate.py d15-installs`), and at a
  round's close for the objective record. The universes are `enumerate.py`'s,
  imported, never enumerated again. `grid` runs the integration's loop
  (`tests/rolling.py` `run_rolling`'s shape) per cell on a plant whose heat
  loss is `--plant-error` times the model's, and prints `C_real`, `C_model`,
  `C_same` (the least cost among the executed plan, the same loop given the
  plant's parameters, and `tests/optimality.py`'s greedy and perturbed
  challengers, each held to the executed plan's bound violation on the plant,
  the open-loop ones also to the heat it left stored; the row names the
  winner), `C_fore`, regret, floor and model gap, then each mean with two
  standard errors. Regret is a lower bound, never negative. `installs` prints
  `C_real` from the bundle's energy store beside the metered power times the
  price, `C_model` from the accuracy store's day-ahead promises, and the gap;
  `C_same` per install-day is NO-READ, its reason derived from
  `replay_doc.py`. Each gap is `undecided` while `thresholds.band_model_gap`
  is null. Cost: one closed loop per cell (two with a plant error), a
  simulated day each; `--jobs` runs cells in parallel. Refusal: exit 2 on a
  missing or empty universe, an unreadable bundle or an unknown `--cells`
  item. `--self-test` runs each regret control of the design at
  `design/R11-PRE-PRODUCT-READS` section 6 on the live tree; CI runs it in
  `tests.yml`'s `arch-instrument` job, the one that installs the pinned
  solver stack.
