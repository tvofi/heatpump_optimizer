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

`e0b5805a07e761ec56648b4320322f81496eb574` is the authored code head, pushed to `handoff/r10-cop-partload`. It is
five commits on the PR head `ea4630ace` (round 1's code head `c221d2ac4`
merged with origin/main `0b8f8b585`, plus the bot's `ci: pin killed
mutants`), so the round-1 pins are in its ancestry.

## Round 2 delta

The round-1 review blocked at `ea4630ace`:
`_partload_derate` took any derate in [0, 0.5] whatever the band, and above
band/(band + p_max) `delivered_heat_kw` falls with power. Heat is
`cop * P * (1 - d * (P - p_min) / band)`. Its slope at p_max is
`cop * (1 - d * (band + p_max) / band)`, the least anywhere on the band, so
heat rises across the band exactly while d < band/(band + p_max).

- `7c1f1e5f5`, failing first. Two `tests/features.py` checks on a 4-5 kW
  band, where the limit is 1/6, with derate-0 and default-band null
  controls. At this commit the part-load block reads `2 of 10 PART-LOAD
  BLOCK FAILED`: 0.19 and the limit itself were kept on both construction
  paths, and the options page had no refusal.
- `773af6e7b`, the fix.
  - `thermal_model.partload_derate_limit(p_min, p_max)` is band/(band +
    p_max). It is infinite for an empty band, where the factor is 1 and a
    derate prices nothing.
  - `_partload_derate(value, params)` refuses a derate that is not strictly
    below the limit to the 0 default. This is the reader's existing refusal,
    applied to one more bound. It refuses rather than clamps because a clamp
    would price a derate nobody configured, and a derate at the limit is a
    pump whose heat stops rising at max power. 0 is the term off: the plan
    is the one priced before the term existed.
  - `ThermalParameters.clamp`, which every construction path runs, applies
    the reader. A direct construction is now bounded too, and the
    `from_config` call is gone, so the class's line count is unchanged.
  - The options page refuses the derate on its own field
    (`config_flow._partload_errors`, error `partload_derate_above_limit`,
    en and sv). It judges against the stored band when the page posts only
    the derate.
  - The option's description and `docs/configuration.md` name the bound:
    0.44 for a 1-5 kW pump, 0.17 for a 4-5 kW one. The selector stays 0-0.5,
    because the bound depends on the two power fields and a static selector
    cannot carry it.
  - The existing range check's 0.5 cell now reads 0 through `from_config`
    on the default 1-5 kW band, which is past 4/9. The reader alone still
    keeps 0.5 and refuses the next float up, so the cap stays pinned.
- `0910e0955` corrects `r10_cop_partload_equiv.py`'s header. Its control
  lines read 15 and 8, not 7 and 0, both at `ea4630ace` and here. Since
  `54437ac84` routed the reader through `const.finite_float`, the eight
  refused cells reach the rewritten line as 0.0. The equivalence counts are
  unchanged: `equiv_differs=0`, `equiv_config_differs=0`, positive 4.
  `--identity` reads 0 on every line but the 7 ties.
- `1617eaa73`: the docs row.
- `e0b5805a0` adds a cell for each new site's mutant: the exact limit and
  the float below it on the page, a fixed-speed 3-3 kW band keeping its
  derate, and a -2..-1 kW band reading no limit. It also drops the page's
  redundant `derate > 0.0 and`: the limit is positive or infinite, so that
  conjunct was an equivalent mutant.

Measured on this arm64 host at `e0b5805a0` unless named, with the 1-minute
load average at 76 to 110 (triage P251: the part-load block alone, no full
`features.py` and no mutation table):

- The part-load block, `tests/features.py` from its R10-COP-PARTLOAD marker
  to the #2261 one under the header: `ALL 10 PART-LOAD BLOCK PASSED`, and
  `2 of 10` failing at `7c1f1e5f5`. The runner is
  `$SCRATCH/probe/pl_block.py`. `features_block.py` cannot run this block:
  it needs `_PvOpt` and `_WS` from earlier in the file.
- The reviewer's `monotone_probe.py` at `773af6e7b`: every band and derate
  row reads `monotone`, including 4-5 kW at 0.19, 3-5 kW at 0.3 and 1-5 kW
  at 0.5 (each refused to 0, so heat is `cop * P`). Null: `d=0` is bitwise
  `cop*P`. Parity at 0.15: scalar against vector bitwise, n 20000.
- Mutation proof of the round's eight added sites
  (`$SCRATCH/probe/r2_mutants.py`, each applied to an archived copy of the
  tree, then the block run). Every mutant is killed:
  - the limit's `GUARD_OFF`: 1 of 10 checks fail
  - `band < 0.0`: 1 of 10 fail
  - `band + p_max < 0.0`: `ZeroDivisionError`
  - the limit's `RETURN_DEL`: `TypeError`
  - the reader's `<` written `<=`: 1 of 10 fail
  - the page's `GUARD_OFF`, `>` and `RETURN_DEL`: 1 of 10 fail each

  The null control is the unmutated tree, which passes 10 of 10.
- `r10_cop_partload.py` reproduces the body's figures: grid 27 plants with
  the ratio at p_max >= 0.808; spread term against none min -0.0598, max
  -0.0094, cheaper 16, dearer 0; flat min -0.0754, max +0.0046, cheaper 10,
  dearer 4; `failures 0`. Every plant's derate sits below its band's limit.
- `tests/env_drift.py --all` at `773af6e7b`: `CLAIMED config_flow: 2 leaves
  moved`, `NO UNCLAIMED DRIFT: 56`, `NO STALE FIXTURE: 56`, rc 0. The claim
  file is untouched this round.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. No
  `*_budgets.json` is touched.
- `tests/finite_boundary.py` at `773af6e7b`: `ALL 108 FINITE BOUNDARY CHECKS
  PASSED`. The new reads go through `const.finite_float`.
- `ci_predict --base origin/main`: no closures, fast, wave-script or
  instrument red. It reports 7 unpinned sites, listed below.
- Not re-run this round, because of the load and because the round adds no
  per-step work: full `tests/features.py`, `tests/stress.py` and the
  mutation table. Round 1's CI readings at `ea4630ace` (stress 113 of 113,
  mutation table passed) are the last full ones.

Round 1, carried.

Every comparison below is three-dot against `edd7e0e14`. Figures measured at
an earlier head say which. The mutation proof and the null control are
carried from `635e991a4`. The one later production change that touches the
priced law is `639ba901f`, which keeps `cop * power` exactly at derate 0, and
the two `_grad_parity` cells at derate 0.15 hold the twins bitwise.

## Unpinned sites

The bot's `ci: pin killed mutants` pinned round 1's three sites. Round 2 adds
seven, each killed by the part-load block (`## Round 2 delta`, mutation
proof). Disposition for each: pinned by `mutation-autofix`.

- `custom_components/heatpump_optimizer/thermal_model.py:1681 GUARD_OFF`, the limit's empty-band guard: 1 of 10 fail
- `custom_components/heatpump_optimizer/thermal_model.py:1681 CMP_BOUND*2`: `band < 0.0` fails 1 of 10, and `band + p_max < 0.0` raises `ZeroDivisionError`
- `custom_components/heatpump_optimizer/thermal_model.py:1683 RETURN_DEL`: raises `TypeError`
- `custom_components/heatpump_optimizer/thermal_model.py:1699 CMP_BOUND`, the reader's `<`: 1 of 10 fail
- `custom_components/heatpump_optimizer/config_flow.py:906 GUARD_OFF`: 1 of 10 fail
- `custom_components/heatpump_optimizer/config_flow.py:906 CMP_BOUND`: 1 of 10 fail
- `custom_components/heatpump_optimizer/config_flow.py:908 RETURN_DEL`: 1 of 10 fail

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
  3.96]`: on this arm64 host only. CI reads it ok at `ea4630ace` and at the
  merge base, so it is the host, not the branch.
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
  `$SCRATCH/probe/calls.py`. CI's `tests / stress` at `ea4630ace`: `ALL
  113 STRESS CHECKS PASSED`, the production-call channel included (the
  round-1 review's reading).
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
- `mutation` at `e0b5805a0`: red by construction on the 7 sites under
  `## Unpinned sites`; mutation-autofix pins killed sites after the push.
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
