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

`f4415303e`

The branch's own production commits are `7ae824d78`, `503238983` and
`566d0cad6`. After them come the structure re-record, the golden fixture and its
claim, the D6 claim counts, the option-doc re-measure and `docs/configuration.md`,
the RCA, the typing local, two audit header blocks, the equivalence harness and
its INERT entry, one features check, the mutation ledger's rows, the delivery
row and the mutation proof's re-take; the merge commits carry origin/main's tree,
including the autofix bot's `ci: merge main`, which this head merged rather than
pushed past. The scoped gate, the figures, the mutation proof and the null
control below were all taken against this tree, whose merge base is `524c1896b`.
`custom_components` is byte-identical between `4f3c73020` and `524c1896b`
(`git diff 4f3c73020 524c1896b -- custom_components` is empty), so every base
arm measured at `4f3c73020` below is `524c1896b`'s tree too; the structure
ratchet and the architecture score were re-measured at this head.

## Mutation proof

Run against the real `tests/features.py` — 4 475 checks at this head — in a
detached worktree at `24bd25b9`, with every mutated file restored afterwards;
the failing lines are in `dev/audit/rca/R10-RCA-COP-PARTLOAD.md` §6.

**R1, the factor itself deleted** (`partload_factor` returns 1.0, so every site
prices the flat law the defect shipped): `7 of 4475 FEATURE CHECKS FAILED` —
the factor, the pump heat, the scalar step, the buffer ceiling, the flat-price
plan and both hot-water checks, and only those. The configured-derate check
passes, as it must: it drives `from_config`, not the factor.

**R2, five site-level mutants in one run**, each owning a different check, so a
failing name is attributable to one mutant — the ceiling priced `max_power *
cop` again, the two-zone scalar step left plain (the second of the two
identical step blocks, so the single-zone twin stays wired), both hot-water
conversions left plain, and the range predicate forced true: `6 of 4475
FEATURE CHECKS FAILED`, one group per mutant:

- `batched simulation is bitwise-identical: two-zone part-load derate` and
  `batched jac == scipy 2-point FD bit-for-bit on free variables: two-zone
  part-load derate` — the two-zone twin, through the batch and its gradient
- `a configured derate inside [0, 0.5] is taken; a negative, oversized,
  non-numeric or NaN one refuses to the 0 default` — the range predicate
- `the buffer's charge ceiling prices the pump's max-power output with the
  derate: a derated pump stops charging at a cooler tank in deep cold` — the
  ceiling
- `a hot-water schedule carries the derate too: ...` and `the full
  trajectory's hot-water track prices the same conversion as the step twin:
  ...` — the two hot-water conversions

R1 says the fix's line is load-bearing; R2 says every site is pinned by its own
check rather than by a neighbour's.

**R3, the upper comparison bound.** The configuration check now drives both
ends of the accepted range, `0.0` and `0.5`, so `0.0 <= derate < MAX` (which
answers the 0 default at `0.5`) is killed by it: the check that names the range
goes red. The other twin, `0.0 < derate <= MAX`, is equivalent and is why the
ledger carries a `survivor_triage` verdict for the anchor rather than a pin:
`dev/audit/harnesses/r10_cop_partload_equiv.py` drives 40 cells — both bounds,
+0.0 and −0.0, the non-finite floats, numeric strings, non-float types and numpy
scalars, direct and through `from_config` — and the lower twin differs on none
of them; its tie-only control differs on the seven cells that are 0.0 and
nowhere else, and the upper twin differs on the four cells that are 0.5, which
is the control that says the probe can see a difference.

## Unpinned sites

`ci_predict.py --base origin/main` predicted three lines — four sites — the
ones an earlier `ci: pin killed mutants` commit left undriven of the thirteen
this diff adds (its seven rows pin the other nine), and
`mutation_table.py --pin-killed --scripts tests/features.py --base origin/main`
drove them at `24bd25b9`:

- `custom_components/heatpump_optimizer/thermal_model.py:1724 CMP_BOUND*2`:
  `if 0.0 <= derate <= MAX_HEAT_PUMP_COP_PARTLOAD_DERATE:`. The anchor carries
  two rewrites and the ledger keys an anchor once, so neither could take a
  `killed_by` row: the lower one, `0.0 < derate ...`, lives (equivalent,
  measured below), and the upper one, `0.0 <= derate < MAX`, is killed by
  `tests/features.py` but shares the anchor with it — the drive's own line says
  `killed by tests/features.py, but its anchor also covers a site no run
  killed`. `survivor_triage/.../_partload_derate.CMP_BOUND.0035a9e4.json`
  records the equivalent verdict and its measurement: 40 cells, 0 differing,
  direct and through `from_config`, 7 ties, the tie-only control differing on
  all 7 and nowhere else, `--identity` all zero, and the upper twin differing
  on the four 0.5 cells. The configured-derate check is what kills the upper
  twin; it now drives both ends of the accepted range.
- `custom_components/heatpump_optimizer/thermal_model.py:1737 CMP_BOUND`:
  `if band <= 0.0:` — pinned; the mutant `if band < 0.0:` divides 0.0 by 0.0 on
  a fixed-speed plant instead of returning 1.0, and took `tests/features.py`
  from `rc=0 failed=0` to `rc=1 failed=1`.
- `custom_components/heatpump_optimizer/thermal_model.py:1752 GUARD_OFF`:
  `if params.cop_partload_derate:` — pinned; the guard off took
  `tests/features.py` from `rc=0 failed=0` to `rc=1 failed=7`.

The drive closes with `PIN KILLED: 2 pinned, 2 left unpinned (2 survived, 0
not started for the budget, 0 exclusive tails cut, 0 timed out, 0 skipped)`,
and with the three rows committed every site the diff adds carries a
disposition: `ci_predict.py --base origin/main` prints `CI PREDICT: no
closures, fast, wave-script or instrument red predicted against 524c1896b694`.

## Null control

With the derate at its default, the branch's plans are the merge base's, not
merely close: 32 of 32 plan hashes identical, over 16 synthetic installs of
R10-SETPOINT-BOOST at a spread and a flat price day and five pricing
configurations, each hash taken from `simulate_trajectory_with_dhw` and printed
by the same harness run against a detached worktree at `4f3c73020`
(`term in tree False`) and against this head (`term in tree True`). The arm was
taken at `4f3c73020` before main advanced; `custom_components` is byte-identical
between it and the merge base `524c1896b`, so the same arm on the merge base is
the same tree. Both arms print `failures 0` and the same three score summaries.

The feature's own checks carry the same control in miniature: at 1.5 kW — the
modulation floor, where the factor is 1 by construction — the derated and plain
arms agree exactly, so a check that would fire on any perturbation of the step
does not fire there.

## Figures

- `partload: grid 27 plants; ratio at p_max >= 0.808, at p_min >= 0.985` — the
  worst plant loses 19.2 % of its COP at maximum power.
  `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_cop_partload.py`
- `solves: central plant derate 0.112` — the central plant of that grid.
  Same command.
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
- `32 of 32 plan hashes identical` between `4f3c73020` — the component-identical
  ancestor of the merge base `524c1896b` — and this head at `d=0` — the null
  control above; each arm's `d=0.0 plan <sha1>` lines compared as a set. Same
  command, run in a detached worktree at the base and at the head.
- `equiv: cells 40, differs 0, config_differs 0, ties 7, control_differs 7,
  control_untied 0, positive_differs 4` — the lower bound's rewrite is
  equivalent on the probed domain and the upper one is not.
  `PYTHONPATH=tests/hastub:. python3 dev/audit/harnesses/r10_cop_partload_equiv.py`
- The feature block costs 1.94 s CPU per `tests/features.py` run, median of
  three, measured by `$EXPORT/probe/pl_block_cost.py` (sha1 `fc6e9af30290`) —
  what the eight checks and two parity cells cost the suite every run.
- `60 sites in the package where a COP meets a power or a heat` — the class's
  seam rule, so the fix is not a search for the one instance: 7 priced forward
  conversions route through `delivered_heat_kw`, 2 are the helper's own lines,
  29 call the COP law itself, and the other 22 are dispositioned one group at a
  time in `dev/audit/rca/R10-RCA-COP-PARTLOAD.md` §5, with the four inverse
  conversions carried forward below.
  `$EXPORT/probe/cop_seams.py custom_components/heatpump_optimizer` (sha1
  `c628396caf3c`)

## Red checks

The red contexts `pr-contract` lists across this branch's ancestry, and what
each is now. Every one of them is named here verbatim — `tests / fast (3.14)`,
`tests / typing`, `tests / mutation`, `budget-raise-gate / budget-raise-gate`,
`tests / mutation-autofix`, `governance / instrument-self-tests`,
`tests / closures`, `tests / closures-autofix` — and `gate` and
`pr-contract / pr-contract` besides:

- `tests / fast (3.14)`: **this branch's**, and the one red that needs the
  owner. `tests/stress.py`'s production-call channel reports 13 scenarios growing
  1.050x to 1.063x past the 1.05 allowance on work their counts vouch at
  1.000x, and the merge base does not fire it. The growth is
  `delivered_heat_kw`'s one call per heat conversion, which is the point of the
  change: the alternative is `cop * power` written at nine sites with the
  factor beside it, the divergence the fix exists to remove. The CPU kernels
  stay inside their 3.0x factor, so this channel is the only one that sees a
  call. The channel's own rule is that a legitimate firing passes for one pull
  request, never by a raise, on the owner's approving review naming the merge
  and the measured growth. Answer: no cheaper detector exists. Inlining the
  law at the call sites is the only way to remove the call, and it is the defect
  this change removes; a call census that discounted one named helper would be
  an allowlist, and the next legitimate helper would need its own exception.
- `tests / typing`: this branch's own, and fixed at `eeb7430a6`. The census the
  job uploads (`typing-census`) reported one error, `no-any-return` in
  `optimizer.py`: `delivered_heat_kw` is typed `Any` because its batch callers
  pass rows, so the buffer ceiling's nested `net()` — declared `-> float` —
  returned `Any`, and the census refuses a `float` declaration that leaks one.
  The local is now declared `float` (`heat: float = delivered_heat_kw(...)`),
  which is what that site is: `marginal_cop` takes scalar arguments there and
  the subtraction is scalar. The census at this head, under the pinned pair
  mypy 2.3.1 / homeassistant-stubs 2026.9.3, prints `ALL 9 typing-ruler checks
  PASSED` and `errors did not grow`. Answer: no cheaper detector. The ruler's
  source half runs in `fast` and is clean at this head; the error is a
  cross-module inference — it needs the stubs' types for `marginal_cop` and the
  optimizer's own attribute surface — which is exactly what the census lane is,
  one run per pull request.
- `tests / mutation`: this branch's own. The command is
  `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`;
  at the run before this head it exited 0 and printed three
  `PREDICT tests / mutation ADDED UNPINNED` lines (four sites) and
  `CI PREDICT: 3 unpinned site(s) the diff adds -- a warning; the body owes each
  a line under ## Unpinned sites`. The red itself refused with
  `3908 unpinned site(s) against 3904, 4 of them added by this diff`; the four
  are the three lines above, and each now carries a disposition measured at
  `24bd25b9` (`killed_by` for the three killed rewrites, the `survivor_triage`
  equivalent verdict for the surviving twin, which is the same code at this
  head). At this head the same command prints only
  `CI PREDICT: no closures, fast, wave-script or instrument red predicted
  against 524c1896b694`. Answer: no cheaper detector exists. A pin's claim is
  "some check in the suite fails when this operator is applied", which only
  running the suite against the mutant establishes; this tree's own measurement
  records 22 checks that executed the line they were named for and pinned
  nothing and 25 production guards deletable with no check failing
  (`tests/mutation_table.py`'s header), and a coverage delta prices both at zero
  and detects neither. The pins' standing cost is one disposition row per site,
  keyed on the line's content anchor rather than its number, each driven by the
  single script whose recorded closure reaches the file. R1 and R2 above already
  show each site is killed by a named check, so the pins record kills that exist
  rather than buy new work.
- `budget-raise-gate / budget-raise-gate`: red until the owner approves
  `tests/structure_budgets.json`'s `class_excess_loc` 18067 -> 18070 at this
  head (the raise; the justification is below). Answer: no cheaper detector
  exists for this rise. A check that could tell an irreducible config surface
  from verbose growth would have to price each new line against a
  counterfactual shape, which no static read can do; the alternative — an
  allowlist of blessed lines — is the drift machine the RCA's §3 refused at a
  53-entry standing cost, and the per-PR owner judgement this gate already makes
  is the cheap end of that trade.
- `pr-contract / pr-contract`: the run before this head refused because the
  body it read did not name `budget-raise-gate / budget-raise-gate`,
  `tests / fast (3.14)` and `tests / typing` under `## Red checks`. This body
  names every context the job lists, and the four answers above are the ones
  the root-cause rule asks for.
- `tests / mutation-autofix`: red at `fe964895e`, the autofix bot's `ci: merge
  main`, with `shards merged: skip-measure-failed` and
  `AUTOFIX: skip-measure-failed -- THE REPAIR DID NOT HAPPEN`: the lane that
  pins surviving mutants declined because the mutation lane it repairs produced
  no pin shards, so it is the mirror of `tests / mutation` above, not a separate
  finding. Its answer is that lane's — the four sites now carry dispositions and
  `ci_predict` predicts no mutation red at this head — and the lane skips itself
  when there is nothing to repair (`skipped` at main's tip `524c1896b`).
- `governance / instrument-self-tests`, `tests / closures` and
  `tests / closures-autofix`: all three are red at `2f15a24c`, an intermediate
  commit of R10-FLOW-AUDIT-PLAN that this ancestry carries because the autofix
  bot merged main (`fe964895e`, whose second parent `6f4434608` is
  `Merge pull request #2869`). None is this branch's. The instrument self-test
  failed on GitHub's own API — `code-scanning/analyses page 1: HTTP 422`,
  `KeyError: 'sort'`, `analysis 11 (actions): HTTP 404` — not on a check of this
  diff; the two closures lanes failed on that group's own instrument opening a
  file its `INERT` entry still listed (`INERT READS UNDER-APPROXIMATED`), which
  that group's next commit `fd36e08a1` fixed. All three are green or skipped at
  this branch's remote head `fe964895e` and at main's tip `524c1896b`, and the
  commits this branch adds touch neither the alert-listing instrument nor
  `tests/closure.py`. Answer: not this branch's; nothing here made them red and
  nothing here can answer for them.
- `gate`: red only as the aggregate of the checks above; it runs the same
  scripts. The pre-pr run at `f4415303e` printed `clean no refusal` with
  `MODE: SCOPED -- 30 script(s) run, 3 scoped out`, and its ancestry-reds step
  answered `ok   the body answers every red this branch pushed`; its one warning
  is the push order, which the push after this body is.

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

Architecture score: dS +0.0000 NULL — computed, not absent. The vector measured
at the merge base `524c1896b` and on the production tree this head carries
gives `S(524c1896b) = -108.482248`, `S(head) = -108.482248`, dS `+0.0000`, and no
metric differs between the two vectors at all:
`tools/audit/archscore/score.py --diff 524c1896b f4415303e` prints
`Architecture score: dS +0.0000 NULL`. The two absolute scores are
`archscore.vector.measure` on each ref's tree, summed with
`archscore.score.weights()`, and the vector reads
`custom_components/heatpump_optimizer` alone, so the commits after the
production tree — the typing local, the ledger rows, the equivalence harness,
one features check and the delivery row — cannot move it, and neither can the
merge. The typing commit declares a local `float` and changes no expression. The
one structure-budget rise is explained below; the ratchet was re-run at this head
and prints `class_excess_loc 18070 <= 18070`, `STRUCTURE RATCHET PASSED`.

## Raise justification

`tests/structure_budgets.json` rises `class_excess_loc` 18067 -> 18070, and the
three lines are irreducible — the `cop_partload_derate` field on
`ThermalParameters`, its row in `_tabled_values`, and its validation call in
`from_config`. The parameter cannot exist without all three, and moving a
dataclass field out of its class trades the metric for a worse one.

Payments tried: the naive shape — the two pricing helpers as
`ThermalParameters` members, the options row at the three-line shape its
neighbours use, the ceiling's single-use `p_max` local kept — reads
`class_excess_loc 18099` at this head (18070 as shipped), so it pays nothing and
costs 29 lines; measured on that tree against `4f3c73020`, `Architecture score:
dS +0.0000 NULL`, and judgement finds it worse, a config dataclass carrying the
pricing math. Inlining the law at the seven call sites instead of a helper was
rejected: those lines fall inside `ThermalModel`'s own class span and it writes
`cop * power * partload_factor(...)` at nine sites, the divergence this change
removes.

Architecture score: dS +0.0000 NULL
