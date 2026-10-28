R10-COP-PARTLOAD: price the compressor's power in COP, off by default

`ThermalModel.compute_cop` priced a heat pump's efficiency from outdoor
temperature, humidity and flow or tank temperature only. Electrical power entered
every heat conversion as a plain multiplier, `heat = cop * power`, so the model
called a compressor equally efficient at its modulation floor and at its maximum
— where the heat-exchanger approach the power sets has grown. A plan therefore
priced heat it could not deliver at the power it chose.

`ThermalParameters.cop_partload_derate` (options flow
`heat_pump_cop_partload_derate`, default 0) is the share of COP lost at maximum
power against the floor, linear across the band.
`thermal_model.delivered_heat_kw` applies it at the seven priced forward
conversions — the scalar and batch space-heat steps, the full hot-water
trajectory, `extend_dhw_temps`, and the optimizer's buffer charge ceiling — so
the plan's cost and its heat both see the fall. At the default 0 the helper
returns `cop * power` unchanged, so no existing install's plan moves.

The root-cause analysis is `dev/audit/rca/R10-RCA-COP-PARTLOAD.md`: the defect's
measured size, its process state with the evidence, the cost test, and the
forward-carried inverse conversions.

## Head

`54437ac849f8cd9d73ef59fa3bd2faf8f0190a9d` is the authored code head, pushed to
`handoff/r10-cop-partload`. It is three commits on `635e991a4` (the previous
handoff tip, which merged `34cd75bf1` into `f4415303e`):

- `5599dcd19` merges origin/main `e8cb7e683` (the v7.0.5 stamp), now this
  branch's merge base. Five files conflicted and were resolved by hand:
  - `tests/golden/claimed_drift.txt`: the stamp emptied main's claim list at
    `claims-for: 7.0.5`, and the `claimnotes` driver refused the merge (both
    sides rewrote the list). This branch's only golden diff against
    `e8cb7e683` is `tests/golden/config_flow.json` (`git diff --stat
    e8cb7e683...HEAD -- tests/golden/`: that file and the claim file), so the
    result is main's file plus one `config_flow` claim for the part-load
    option's keys. The seven other claims the previous head carried excused
    other pull requests' diffs, which the stamp released. `card_claimed_drift.txt`
    is untouched (byte-identical to main).
  - `tests/features.py`: both sides appended a block at the same place
    (this branch's part-load checks, main's #2261 heat-meter checks); both kept.
  - `dev/audit/rounds/round3/D5/option_doc_coverage.py`: both sides added one
    option, so the header's counts are re-measured at the merge (203 fields,
    236 schema keys) and its history names both moves.
  - `dev/audit/rounds/round4/D6/claims.py`: this branch's Range row (92) beside
    main's module count (83, `heat_energy.py`); `claims.md` is the script's own
    regeneration at the merge, not a hand edit.
  - `tests/structure_budgets.json` and `tests/closures.json` merged through
    the ledger driver.
- `2f082ee3b` pays the structure budget instead of raising it (below).
- `54437ac84` routes the derate's validation through `const.finite_float`,
  which `tests/finite_boundary.py` refused (below).

Every comparison below is three-dot against `e8cb7e683`. Figures measured at an
earlier head say which.

## Mutation proof

`pl_mutants.py` applies each mutant to the real `tests/features.py` tree, runs
the suite, prints the failing check names, and restores every touched file with
`git checkout --` (`git status --short` empty afterwards).

- R1, the helper's factor removed (`return 1.0`): **7 of 4488 feature checks
  fail** — the factor's linear law, the pump's max-power heat, the scalar
  step's slab warm, the buffer's charge ceiling, the flat-price plan's
  max-power share, the hot-water schedule and the full trajectory. Each names
  a behaviour the term carries; none is collateral.
- R2, four mutants in one run — the optimizer's ceiling (`heat =
  p.max_electrical_power * cop`), the second of the two line-for-line
  identical scalar-step blocks, the hot-water schedule and the full
  trajectory, and the config validation (`if True:`): **6 of 4488 fail**, each
  at its own site and each failure owning it. The batched bitwise-identity and
  jacobian checks pin the two-zone step, the ceiling check pins the ceiling,
  the two hot-water checks pin their sites, and the validation check prints
  the accepted `-0.1` and `0.9`. R1 shows what depends on the term; R2 shows
  each of the four call shapes routes through the helper rather than around it.

  `PYTHONPATH=tests/hastub python3 $EXPORT/probe/pl_mutants.py R1`, then `R2`
  (sha1 `979ad48a4a60`)

## Null control

With the derate at its default, the branch's plans are the merge base's, not
merely close: the `d=0.0` plan hashes are identical 32 of 32 between `635e991a4`
and the merge base `34cd75bf1` — 16 grid cells of R10-SETPOINT-BOOST (two heat-loss
scales, two buffer volumes, DHW on and off, rounded and unrounded) on its spread
and flat price days — every hash printed by the same harness run at each tree
(the base worktree carries a copy of the harness and prints `term in tree False`;
`635e991a4` prints `term in tree True`), `failures 0` on both arms.

The feature's own checks carry the same control in miniature: at 1.5 kW — the
modulation floor, where the factor is 1 by construction — the derated and plain
arms agree exactly, so a check that would fire on any perturbation of the step
does not fire there.

## Figures

- `partload: grid 27 plants; ratio at p_max >= 0.808, at p_min >= 0.985` — the
  worst plant loses 19.2 % of its COP at maximum power.
  `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_cop_partload.py`
- `solves: central plant derate 0.112 term in tree True` — the central plant of
  that grid. Same command.
- `spread term vs none: cost per plant kWh change min -0.0598 max -0.0094 cells
  cheaper 16 dearer 0` — pricing the fall takes 0.94 % to 5.98 % off the cost
  per delivered kWh on price-spread days, on all 16 installs. Same command.
- `spread d=0.0: cells 16 heat short max 0.1093` and `spread d=0.112: cells 16
  heat short max 0.0822` — the plan delivers at most 8.2 % less heat than it
  promises instead of 10.9 %. Same command.
- `flat term vs none: cost per plant kWh change min -0.0754 max +0.0046 cells
  cheaper 10 dearer 4` — the flat-price day, where shaping buys no price: the
  term is not a one-way gain, which is why it ships off by default. Same
  command.
- `32 of 32` `d=0.0` plan hashes identical between the merge base and `635e991a4`
  — the null control above; the same command at each tree.
- At `54437ac84`: `CLAIMED config_flow: 2 leaves moved`, `NO UNCLAIMED DRIFT:
  56 scenario(s) checked against origin/main` and `NO STALE FIXTURE: 56
  committed fixture(s) still match what this tree computes` (rc 0): the one
  claim the resolved file carries excuses exactly this branch's diff.
  `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all`
- The feature block costs 1.89 s CPU, median of three, measured by
  `$EXPORT/probe/pl_block_cost.py` (sha1 `fc6e9af30290`) — what the eight checks
  and two parity cells cost the suite every run. Measured at `635e991a4`.
- `59 sites in the package where a COP meets a power or a heat` — the class's
  seam rule, so the fix is not a search for the one instance: 7 priced forward
  conversions route through `delivered_heat_kw`, 2 are the helper's own lines,
  28 call the COP law itself, and the other 22 are dispositioned one group at a
  time in `dev/audit/rca/R10-RCA-COP-PARTLOAD.md` §5, with the four inverse
  conversions carried forward below. The RCA §5 table was written at 60; the
  merge of #2745 removed one `marginal_cop` call in
  `optimizer._deferred_energy_cost`, and the 22 remaining groups map one for
  one.
  `$EXPORT/probe/cop_seams.py custom_components/heatpump_optimizer` (sha1
  `c628396caf3c`)

- The payment, `2f082ee3b`: `ThermalParameters._tabled_values` mapped each
  field to a (config key, default) pair of `const` suffixes, and all 41 table
  rows and all three boolean rows named the same suffix twice (an AST count of
  rows whose two names are equal: 41 of 41; the part-load row was already
  written `("HEAT_PUMP_COP_PARTLOAD_DERATE",) * 2`). The table now maps a field
  to its one suffix. `ThermalParameters` spans 995 lines at `5599dcd19` and 940
  at `2f082ee3b` (`ast` `end_lineno - lineno + 1`), and `python3
  tests/structure.py` reads `class_excess_loc 17992 (budget 18047, -55)`, then
  `STRUCTURE RATCHET PASSED` once `--record` wrote 17992; main records 18044,
  so the +3 this branch adds is paid and no cap rises. Equivalence:
  `asdict(ThermalParameters.from_config(cfg))` for an empty config, one setting
  all 219 `CONF_` string keys to 0.37, and the boolean rows read from `"x"`,
  compared byte for byte before and after the edit: identical. Null control:
  the same comparison with `min_electrical_power` planted on
  `HEAT_PUMP_MAX_POWER` differs. Out-of-tree driver
  `$SCRATCH/fc_equiv.py` (sha1 `613e177f1989`).
- The derate's reader, `54437ac84`: `_partload_derate` returns the same value
  before and after on `0, 0.0, 0.1, 0.5, -0.1, 0.9, 'x', None, NaN, inf, True,
  False, '0.2'`, and refuses `b'0.1'` (0.0, was 0.1), which `const.finite_float`
  refuses everywhere. The guard and both return lines are unchanged, so the two
  pinned sites (`_partload_derate GUARD_OFF 0035a9e4`, `RETURN_DEL 208f053a`)
  keep their anchors.

## Red checks

Lines naming `54437ac84` were re-run there on this arm64 host; the golden,
stress, optimality and mutation-proof readings were taken at `635e991a4` and
are carried: this pass's production edits are the table's shape and the
derate's reader, and both leave `from_config`'s output unchanged (`## Figures`).

- `budget-raise-gate / budget-raise-gate`: red at `fe964895e` on `class_excess_loc` 18067 -> 18070.
  Answered by paying it: at `54437ac84` no cap rises (`git diff
  e8cb7e683...HEAD -- tests/structure_budgets.json`: `class_excess_loc` 18044
  -> 17992, `recorded_at` only otherwise), and `python3 -I
  tools/policy/budget_raise_gate.py --base e8cb7e683 --head 54437ac84 --pr
  2872` prints `RESULT budget_raises=0 count` and `PASS: no budget raise; no
  owner review is owed`. Answer: no cheaper detector than
  the gate exists for a cap rise; `tests/structure.py` already names the
  growing row locally, which is how this pass found it.
- `tests / fast (3.14)`, `tests/finite_boundary.py` at `fe964895e`: `1 of 108 FINITE
  BOUNDARY CHECKS FAILED`, `stray=['thermal_model.py::_partload_derate']` (the
  derate read its config through a bare `float()`). Same at `2f082ee3b`;
  `ALL 108 FINITE BOUNDARY CHECKS PASSED` at `54437ac84`.
  `PYTHONPATH=tests/hastub python3 tests/finite_boundary.py`. Answer: the
  cheaper detector exists and is that script, which a local run of the scoped
  gate reaches in 7 minutes; it was not run before the earlier push.
- `tests / typing` at `fe964895e` (`no-any-return` +1): repaired by `eeb7430a6`
  before this pass; `ALL 9 typing-ruler checks PASSED` at `54437ac84`
  (`HPO_TYPING_PYTHON=<venv-ha python> python3 tests/typing_ruler.py`).
- `tests / mutation` and `tests / mutation-autofix` at `fe964895e` (4 added
  unpinned sites): disposed by `24bd25b92` and `d2e128d49`, see the
  `mutation` line below.
- `pr-contract` and `gate` at `fe964895e`: the body then named an older head;
  this body names the head it is pushed with.
- `tests/golden.py` (`GOLDEN_MODE=strict`): `55 of 56 GOLDEN SCENARIOS CHANGED`
  at `635e991a4`, and the unmodified merge base `34cd75bf1` prints the same 55
  names, compared as sets. The fixtures are the canonical environment's values;
  this host's solver reaches other optima. The one scenario this branch changes,
  `config_flow`, is `ok`. Not this branch's.
  `GOLDEN_MODE=strict PYTHONPATH=tests/hastub python3 tests/golden.py`
- `tests/stress.py`, `shoulder: cheaper than holding the setpoint [4.67 vs
  3.96]`: the branch's only production change is the derate at its 0 default,
  where the null control shows the plans byte-identical, so this comparison is
  the merge base's. Not this branch's.
- `tests/stress.py`, the production-call channel: **this branch's**, and the one
  red that needs the owner. 13 scenarios grow 1.051x to 1.064x past the 1.05
  allowance on work their counts vouch at 1.000x, and the merge base does not
  fire it. The growth is `delivered_heat_kw`'s one call per heat conversion,
  which is the point of the change: the alternative is `cop * power` written at
  seven sites, the divergence the fix exists to remove. The CPU kernels stay
  inside their 3.0x factor, so this channel is the only one that sees a call.
  The channel's own rule is that a legitimate firing passes for one pull
  request, never by a raise, on the owner's approving review naming the merge
  and the measured growth. Answer: no cheaper detector exists. A pin's claim is
  "some check in the suite fails when this operator is applied", which only
  running the suite against the mutant establishes; a coverage delta prices both
  at zero and detects neither.
  `PYTHONPATH=tests/hastub python3 tests/stress.py`
- `tests/optimality.py`: 1 of 84, the `one|summer_negative|shoulder` claim. The
  file records that "the gate's platform is the one that counts, so this claim
  reads stale on arm64 only" (`tests/optimality.py`, the claim's note), and the
  32-hash null control shows the derate at 0 moves no plan. Not this branch's.
  `PYTHONPATH=tests/hastub python3 tests/optimality.py`
- `tests/harness_headers.py`: green. `ALL 112 HARNESS HEADER CHECKS PASSED` at
  `54437ac84`, which executes the two headers the merge re-measured.
  `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/harness_headers.py`
- `mutation`: no site this diff adds is unpinned at `54437ac84`. The branch's
  later commits `d2e128d49` and `24bd25b92` add ten ledger rows, one per site
  the diff adds, and `ci_predict` prints no ADDED UNPINNED line. Green.
  `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`

## Forward-carry

- The inverse conversions still close the loop with `heat / cop`:
  `dhw_planner._plan_dhw_min_cost`, `_clamp_dhw_to_capacity`,
  `optimizer._compute_baseline_power` and `coordinator._dhw_setpoint_sweep`.
  With a derate the forward relation is quadratic in power, so the closed form
  understates the electrical power needed to deliver a given heat by up to the
  derate; the exact form is the positive root on the band, and at the default 0
  the current ones are exact. Every setpoint a plan holds is still met because
  the ceiling and the step share the helper, so this is a cost-accounting
  inaccuracy, not a control error.

  Carry: R10-COP-PARTLOAD
- D2's item 2 says which quantities the COP step sweeps, and power is not among
  them, so eight rounds of that step passed a law with no power term (the RCA's
  §2). The countermeasure is one sentence in the brief: derive the priced
  formula's inputs from the device's own control surface and mark each a
  modelled term, a documented constant or out of scope. It is policy
  (`dev/governance/dimensions/D2.md`) and the owner approves it; this seat did
  not edit it.

  Carry: R10-COP-PARTLOAD

## Friction

none

## Architecture score

Architecture score: dS +0.0000 NULL (`python3 tools/audit/archscore/score.py
--diff origin/main`, origin/main `e8cb7e683`, at `5599dcd19` before the payment,
at `2f082ee3b` after it, and at `54437ac84`; all three print the same line).
