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

`c221d2ac4eb579853953f00eefa75f8b8712b738` is the authored code head, pushed to `handoff/r10-cop-partload`.
It is six commits on `54437ac84` (the previous handoff tip), and its merge
base is origin/main `edd7e0e14`:

- `6d14230a8` merges origin/main `edd7e0e14` into `54437ac84`.
  `tests/structure_budgets.json` and `tests/closures.json` merged through the
  ledger driver; the claim file was re-cut in `e03722e94`.
- `e03722e94` repairs two things. `tests/features.py` did not parse at
  `54437ac84`: the merge `5599dcd19` placed main's #2261 heat-meter section
  after the part-load hot-water `R.check` and dropped that call's closing
  `)` (`SyntaxError: '(' was never closed`; prepr's `no-copies` step refused
  on it too). The `)` and its two blank lines are back, and that is the
  file's whole edit; `git diff origin/main...HEAD -- tests/features.py` is
  pure additions. `tests/golden/claimed_drift.txt` is main's file byte for
  byte plus this branch's one `config_flow` claim, `claims-for: 7.0.5` ==
  `VERSION`. The claimnotes driver refused the merge (both sides rewrote the
  list); main's R10-HOUSE-GRADE `coord_*` claims stay, because deleting them
  here would delete them from main while their drift is unstamped.
  `card_claimed_drift.txt` is byte-identical to main.
- `639ba901f` pays the production-call red in `tests/stress.py` with code
  (`## Red checks`): `thermal_model.heat_per_cop_kw(params, power)` is the
  draw's heat per unit of COP (the draw at derate 0, else draw times
  `partload_factor`), and `delivered_heat_kw` is `cop * heat_per_cop_kw(...)`.
  The part-load factor depends on the draw alone, so the batch twin takes it
  once for its power matrix and `extend_dhw_temps` once for its schedule,
  and each sub-step multiplies in its own COP. Before, those two loops called
  the helper once per interval and sub-step: 30432 and 5566 of the 38014
  `delivered_heat_kw` calls on `heavy_old/winter`. After, 0 and 0 of 2016
  (the 1920 scalar-step calls and the 96 hot-water trajectory calls are
  unchanged). Out-of-tree counter `$SCRATCH/probe/site_count.py`. The
  association is now `cop * (power * factor)` at every site, scalar and
  batch, so the twins stay bitwise; at derate 0 every product is still
  exactly `cop * power`.
- `ad2bf7fd6` pays the six class lines the hoist first cost
  (`class_excess_loc 17992 > 17986`): both loops build `heat_per_cop` from
  the `asarray` and read their shapes from it, and the batch's existing COP
  comment carries the note. `class_excess_loc 17986 <= 17986`.
- `c221d2ac4` closes the last firing scenario: at `f041578bd` the channel
  read `summer/1z/space/valve` 88705 against 84434 = 1.051x, because
  `delivered_heat_kw` now made a second call per scalar step. Both zone
  steps and the hot-water trajectory write `cop * heat_per_cop_kw(...)`, the
  product `delivered_heat_kw` returns, and `delivered_heat_kw` stays the
  optimizer ceiling's.
- `f041578bd` deletes `delivered_heat_kw`'s two pins (`GUARD_OFF 54581fbd`,
  `RETURN_DEL 8c667869`), which `ci_predict` reads as STALE PIN once their
  lines moved into `heat_per_cop_kw`.

Every comparison below is three-dot against `edd7e0e14`. Figures measured at
an earlier head say which. The mutation proof and the null control are
carried from `635e991a4`. The one later production change that touches the
priced law is `639ba901f`, which keeps `cop * power` exactly at derate 0, and
the two `_grad_parity` cells at derate 0.15 hold the twins bitwise.

## Unpinned sites

`ci_predict` names three sites `639ba901f` adds and nothing pins yet. Each is
disposed as pinned by `mutation-autofix`, which pins a killed added site:

- `custom_components/heatpump_optimizer/thermal_model.py:1704 GUARD_OFF`
  (`heat_per_cop_kw`'s `if params.cop_partload_derate:`): it carries the
  derate, the guard R1 below removes, killed by 7 feature checks.
- `custom_components/heatpump_optimizer/thermal_model.py:1706 RETURN_DEL`
  (`return electrical_power`) and
  `custom_components/heatpump_optimizer/thermal_model.py:1716 RETURN_DEL`
  (`delivered_heat_kw`'s `return cop * heat_per_cop_kw(...)`): either
  dropped makes every conversion `cop * None`, so every `tests/features.py`
  plan check raises.

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
- At `ad2bf7fd6`: `CLAIMED config_flow: 2 leaves moved`, `NO UNCLAIMED DRIFT:
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
  `STRUCTURE RATCHET PASSED` once `--record` wrote 17992; main then recorded
  18044, so the +3 this branch adds is paid and no cap rises. At `ad2bf7fd6`
  the ledger driver's merge reads 17986 against main's 18038, and
  `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. Equivalence:
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

Lines naming `ad2bf7fd6` were re-run there on this arm64 host (the two
later commits are a ledger deletion and `c221d2ac4`, which spells three
sites' product `cop * heat_per_cop_kw(...)`, the value `delivered_heat_kw`
returned there); the golden,
optimality and mutation-proof readings were taken at `635e991a4` and are
carried (`## Head` says why).

- `budget-raise-gate / budget-raise-gate`: red at `fe964895e` on `class_excess_loc` 18067 -> 18070.
  Answered by paying it: at `ad2bf7fd6` no cap rises (`git diff
  edd7e0e14...HEAD -- tests/structure_budgets.json`: `class_excess_loc` 18038
  -> 17986, `recorded_at` only otherwise), and the gate's own diff read,
  `raises_between(merge-base, HEAD)`, returns `[]` (budget_raises=0);
  `python3 -I tools/policy/budget_raise_gate.py --check-body BODY.md --base
  origin/main --head HEAD` prints `the diff raises no cap, and the body has no
  raise section to judge`. Answer: no cheaper detector than the gate exists
  for a cap rise; `tests/structure.py` already names the growing row locally,
  which is how this pass found it.
- `tests / fast (3.14)`, `tests/finite_boundary.py` at `fe964895e`: `1 of 108 FINITE
  BOUNDARY CHECKS FAILED`, `stray=['thermal_model.py::_partload_derate']` (the
  derate read its config through a bare `float()`). Same at `2f082ee3b`;
  `ALL 108 FINITE BOUNDARY CHECKS PASSED` at `54437ac84` and at `ad2bf7fd6`.
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
- `tests/stress.py`, the production-call channel: **this branch's**, and paid
  in code, not passed by review. At `6d14230a8` (54437ac84 plus main) 13
  scenarios grew 1.051x to 1.064x past the 1.05 allowance on work their counts
  vouch at 1.000x (`heavy_old/winter` 1258913 against 1182874, 1.064x,
  thermal_model.py +76034; `winter/cycle` 2655470 against 2527295, 1.051x).
  The growth was `delivered_heat_kw`'s call per interval and sub-step in the
  batch twin and per step in `extend_dhw_temps`; `639ba901f` takes the
  draw's heat per unit COP once per schedule (`## Head`). At `ad2bf7fd6`:
  at `f041578bd` the full run judged 20 of 20 family members and one still
  fired, `summer/1z/space/valve` 88705 against 84434 = 1.051x;
  `c221d2ac4` removes the second call, and `stress.production_calls`, the
  channel's own meter run in process on this head and on the merge-base
  tree, reads `summer/1z/space/valve` 86593/84434 = 1.026x,
  `summer/1z/space` 81620/79661 = 1.025x, `light_new/shoulder`
  486204/482519 = 1.008x, `heavy_old/winter` 1187891/1182874 = 1.004x,
  `summer_negative/1z/dhw` 277773/275086 = 1.010x, all under 1.05. The
  baselines are the stress run's own to the call. Driver
  `$SCRATCH/probe/calls.py`. The full `tests/stress.py` was not re-run at
  `c221d2ac4`; CI's `tests / stress` run is the authority.
  Answer: no cheaper detector exists. A per-sub-step call costs nothing the
  CPU kernels' 3.0x factor sees, so only this exact count finds it, and it
  costs a stress run.
  `PYTHONPATH=tests/hastub python3 tests/stress.py`
- `tests/features.py`: did not parse at `54437ac84` (`SyntaxError: '(' was
  never closed`, the merge's dropped `)`, `## Head`); `ALL 4550 FEATURE CHECKS
  PASSED` at `ad2bf7fd6`, the two `_grad_parity` part-load cells at derate
  0.15 bitwise included. Answer: the cheaper detector is `python3 -c "import
  ast; ast.parse(...)"` on every merged test file, which prepr's `no-copies`
  step already runs and which refused; the earlier push did not stop on it.
  `PYTHONPATH=tests/hastub python3 tests/features.py`
- `tests/optimality.py`: 1 of 84, the `one|summer_negative|shoulder` claim. The
  file records that "the gate's platform is the one that counts, so this claim
  reads stale on arm64 only" (`tests/optimality.py`, the claim's note), and the
  32-hash null control shows the derate at 0 moves no plan. Not this branch's.
  `PYTHONPATH=tests/hastub python3 tests/optimality.py`
- `tests/harness_headers.py`: green. `ALL 112 HARNESS HEADER CHECKS PASSED` at
  `54437ac84`, which executes the two headers the merge re-measured.
  `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/harness_headers.py`
- `mutation` at `c221d2ac4`: red by construction on the 3 sites under
  `## Unpinned sites`; mutation-autofix pins killed sites after the push.
  The ten rows `d2e128d49` and `24bd25b92` added stand, less the two
  `delivered_heat_kw` pins `f041578bd` deletes as stale.
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
at `2f082ee3b` after it, at `54437ac84`, and at `ad2bf7fd6` against origin/main
`edd7e0e14`; all four print the same line).
