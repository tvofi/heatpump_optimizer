# Round 9, D0 (price optimality), finder seat D0-s3

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`. Box B3: a 4-CPU Linux container shared with other finder seats. `load1` ran at 4 to 8 for the whole session. Interpreter: `/home/claude/venv314/bin/python`, with `PYTHONPATH=tests/hastub`, BLAS pinned to one thread, `thread_factor` 1.000 on every run.

My cells cover steps D0.M5 (null control), D0.M6 (MPC masking) and D0.M7 (decomposition and terminal credit), over every file and every price profile. I measured nothing in M1 to M4. What I saw there is listed under leads.

**Result: no findings.** Every mechanism I measured either held or did not survive its own control. The numbers are below, so a later round can call these cells dry or pick up where this one stopped.

## Harnesses

Each harness is run from the export root with `PYTHONPATH=tests/hastub`. The exact command is in each file's header. Raw outputs from this session are in `out/`.

| harness | measures | hooks |
|---|---|---|
| `race.py` | Per-cell objective gap between production and a stronger search on the exact captured objective. Both arms are run through the full `optimize()`. Reports feasibility parity, step-0 difference and the flat-price null control. | `optimizer:_multi_start_minimize` (replaced by production's own call plus challengers), `optimizer:HeatPumpOptimizer.optimize` |
| `decomp.py` | Whether iterating the DHW/space split more than once changes the objective (arm `iter`), and whether dropping the `pinned` trigger does (arm `free`) | `optimizer:HeatPumpOptimizer._co_optimize`, `_build_dhw_requirements` |
| `mpc.py` | A closed receding-horizon loop, with the plant equal to the model and a re-plan every 30 minutes. The warm start is handed in exactly as `coordinator._warm_seeded` does it. Arms: prod, open (re-plan once a day), cold, shift, noterm, chal. Reports realized and settled objective, and the per-cycle effect of the warm-start seam. | `optimizer:_multi_start_minimize`, `HeatPumpOptimizer._terminal_cost`, `HeatPumpOptimizer._comfort_terms`, `_prev_shipped_plan` |
| `terminal.py` | Planned energy in hours 20 to 24 of the 24 h plan, divided by the 48 h plan's energy in the same hours. Also the end-state temperature gap between the two. | `optimizer:HeatPumpOptimizer._terminal_cost` (zeroed under `--perturb noterm`) |

## D0.M5: null control (deep)

`race.py` ran over every price profile (8) × every weather profile (5) × single-zone and two-zone × DHW off and on. That is 160 cells: 80 single-zone and 80 two-zone. The two-zone summary counts 76 cells, because 4 were set aside as infeasible (listed below).

The challenger adds production's own answer (a warm restart) and bang-bang seeds at 0 to 1.5 times the production energy. It runs L-BFGS-B at ftol 1e-12, maxiter 3000 and maxfun 60000 on the same jac path, and keeps whichever arm scores lower.

- **Single-zone** (`out/race_one.log`):
  - Mean gap over priced profiles: 0.512 %. Maximum: 16.20 % (`summer_negative|shoulder`, J 0.306 -> 0.256, on a bill of -1.62 SEK). With the single most favourable cell dropped: 0.285 %.
  - At flat prices: mean 0.136 %, maximum 0.678 %, and 4 of 10 cells above 0.1 %.
  - 24 priced cells gap by more than 0.1 %. In 19 of them the challenger spends more money than production, and the mean absolute gap is 0.062 objective units.
  - 15 of those 24 exceed the matched flat cell by more than 0.1 percentage points.
- **Two-zone** (`out/race_two.log`):
  - Mean gap over priced profiles: 0.153 %. Maximum: 3.28 % (`summer_negative|shoulder`). With the best cell dropped: 0.106 %.
  - At flat prices: mean 0.075 %, and 3 of 9 cells above 0.1 %.
  - 28 priced cells gap by more than 0.1 %, with a mean of 0.112 units and a maximum of 0.469. In 13 of them the challenger spends more money.
  - 4 cells were excluded because the challenger's plan runs colder than production's.
- **Reading.** The priced gaps are small in absolute terms, 0.06 to 0.11 SEK-equivalent per day on average. Mostly the challenger buys comfort pull with money rather than saving money, and a flat-price gap of the same order exists beside them.
- Where a real price basin exists, it is a seeding matter (M1/M2). The winning seeds are bang-bang at 0.35x, 0.5x and 0.75x, and a warm restart at tight ftol. That goes to leads, not findings.
- The summer gaps sit on bills of 2 SEK or less. The brief rules those out.

## D0.M6: MPC masking (deep on single-zone, open on two-zone)

- **Step-0 test, over the M5 grid.** Among cells gapped by more than 0.1 %, step 0 differs by more than 0.05 kW in 6 of 28 single-zone cells and 4 of 31 two-zone cells. Everywhere else the first action is identical, so the next re-plan decides again.
- **Closed loop.** `mpc.py` ran 4 days, single-zone, `winter_cold`, comparing the production 30-minute re-plan against a policy that re-plans once a day. Both arms use the same plant and the same inputs.
- **The day-1 ruler is biased.** The day-1 "realized objective" ruler, which evaluates the first cycle's own objective on the realized first day, shows production 3.38 % worse than its own open-loop plan on `winter_typical`. That figure is an artefact: the open arm is the minimiser of that very ruler. The flat control exposes it at 11.67 %.
- **The unbiased ruler.** Money, plus production's own terminal-cost settlement of the end state, plus production's `_comfort_terms` over the realized trajectory (`out/mpc4.log`). On that ruler the loop is:

  | cell | settled objective, loop vs daily |
  |---|---|
  | `winter_typical` | -2.42 % |
  | `winter_extreme` | -2.08 % |
  | `winter_moderate` | -2.42 % |
  | `winter_narrow` | +0.04 % |
  | `shoulder` | +0.35 % |
  | `flat` | +1.53 % |

  The loop is no worse at priced profiles and, in winter, better. It spends more money to hold the house about 0.6 to 1.0 K warmer, which the objective values. Comfort-floor violation is 0 in every arm.
- **The flat-price cell is open.** It is the one cell where the loop is worse: +5.75 SEK over 4 days, at almost the same comfort. It is a single cell, so it goes to `unfinished`, not findings.
- **Horizon perturbation.** At 48 h the day-1 ruler's excess drops from 3.38 % to 0.27 % (`out/mpc_h48.log`). That is consistent with the ruler bias being a horizon-end effect.
- **The warm-start seam.** `coordinator._warm_seeded` hands the previous plan in unshifted. Handing it shifted by the elapsed steps changed the shipped plan by:
  - `winter_typical`: mean -0.0026 % over 47 cycles, better in 4 and worse in 4.
  - `shoulder`: mean +0.034 % over 47 cycles, better in 11 and worse in 4.

  Both are noise (`out/mpc_seam.log`, run with `--arms prod,cold,shift --seam 1 --days 1`). The docstring's "the same problem one step later" is inaccurate, but it costs nothing measurable. That goes to leads.

## D0.M7: decomposition and terminal credit (deep on single-zone)

- **Iterating the DHW/space split** (`decomp.py --k 5`). This ran on 24 single-zone and 24 two-zone DHW cells across 8 prices x 3 weathers. It adopted 0 extra rounds, and the gap was 0.0000 % in every cell. The first round's re-plan is adopted in only 2 cells per topology (`summer_negative|winter_cold`, `shoulder|winter_cold`), and the next round then never triggers.
- **Dropping the `pinned` trigger** (`--arm free`, single-zone). The DHW planner returns the same schedule every time (`same`) or the re-plan is rejected. 0 rounds adopted, 0.0000 % gap. The decomposition is stable.
- **The terminal credit** (`terminal.py`). The docstring says it stops the plan dumping its last hours. That holds in direction:
  - In single-zone `winter_cold` cells the 24 h plan buys 0.50 to 0.86 times the 48 h plan's energy in hours 20 to 24.
  - With the credit zeroed (`--perturb noterm`) it buys 0.000 in every cell, and the end slab is 5.8 to 12.1 K colder.
  - In magnitude it errs both ways. In cold weather the plan under-buys (end slab 2.8 to 3.6 K below the 48 h plan). In shoulder weather it over-buys: DHW-on ratios are 5.7 to 7.9 against a near-zero 48 h tail, and the end slab sits +3.17 K above the 48 h plan.
  - The flat-price cells show the same pattern (0.53 and 0.61 in `winter_cold`). So this is valuation, not price arbitrage. The magnitude question belongs to D2 and goes to leads.

## Unfinished

- M6: the closed loop was not run on two-zone or DHW cells (a two-zone loop costs about 7 s x 48 solves x 4 days per arm on this loaded box). Nor was it run on weathers other than `winter_cold`. The flat-price over-spend (+1.53 % settled objective, +5.75 SEK over 4 days) needs the flat arm over at least 5 cells before it can be a finding.
- M7: the terminal-credit tail ratio was not run on two-zone cells, and the `free` decomposition arm was not run on two-zone.

## Exposure

I read `tools/audit/bugclasses.json` for the `class_guess` ids. It carries earlier-round finding ids as context, and I made no use of them. I read nothing under `tools/audit/round3` to `round8`, no `docs/`, and nothing on GitHub. I read `tests/optimality.py`, which cites earlier D0 ids in comments; that was context only.
