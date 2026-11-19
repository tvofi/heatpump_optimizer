# Class sweep: N-leaf-imports-solver (round 11, PLAN phase D)

Tree: `handoff/audit-r11-register` at `28b864af6d`. Finding in the class: D7-s1-06 (verified, low).

## Enumerator

`python3 dev/audit/rounds/round11/D14/leaf_imports_solver.py [root] [--probe MODULE]`

It lists every package module that reaches, through package imports, a layer above
its own: pure (0) < solver/scipy (1) < glue/Home Assistant (2). The import graph and
the layers come from `tools/audit/archscore/metrics/layering.py`, so the seam count
equals archscore's `layer_violations`. Each seam prints its shortest carrying path.
`--probe M` exits 1 while `M` is still a seam.

The ledger's mechanism names the solver leg (a leaf reaching scipy). That leg has
**0 seams** at this tree: no module rises 0 -> 1. All 13 seams climb to Home Assistant,
which is the reach D7-s1-06 measured. The enumerator covers both legs.

## Controls

| control | arm | reading |
|---|---|---|
| positive | tree as is | 13 seams. All 7 modules that D7-s1-06's accuracy/currency move frees are re-found |
| positive (move) | HA import cut from `accuracy.py` and `currency.py` | 13 -> 6, the verifier's figure. Cutting accuracy alone gives 7, currency alone gives 12 |
| null | clean fixture: pure <- solver <- glue, downward edges only | 0 |
| perturbation | add one line `from .glue import solve` to the fixture's pure module | 0 -> 3 |
| perturbation (real tree) | add one line `from .store import Store` to `drift.py` | 13 -> 39 seams |

## Disposition: 13 seams

Judged sites (the 7 that D7-s1-06's move frees; `beyond_finding: false`):
comfort_learning, external_heat, power_guard and tariff via `accuracy`; topology and
optimizer (1 -> 2) via `tariff > accuracy`; grid_fee via `currency`.

Instances beyond the finding (6, `beyond_finding: true`), each with the probe
`leaf_imports_solver.py . --probe <module>` that fails on it:

| module | carried by |
|---|---|
| disinfection | `inputs` |
| price_model | `inputs` |
| quiet_windows | `inputs` |
| setpoint_check | `inputs` |
| snapshots | `store` |
| sysid | `accuracy`, plus a second path that still holds after both cuts |

No seam is guarded. The only check that reads the metric is
`tests/ci_budgets.json` `archscore.layer_violations: 22`. That one-sided cap sits
9 above the count, so a new seam passes it. The class is **not barriered**.

Not applicable: none. Every module in layer 0 or 1 that does not appear above
already respects the layering.

## Proposed barrier

Pin `layer_violations` in the structural ratchet at its measured count (13, or 6
after the D7-s1-06 move) instead of the 22 CI cap. Then any re-introduction fails
the gate. The enumerator runs in about 1 s.
