Round 10, group `R10-PUMP-MODEL`, its third finding: what the model charges
for a hot-water tank. Part of #2238. This branch is cut from the group's
primary head `03bffee33` (`handoff/r10-pump-model`, D7-arch3-04 and
D7-s3-8x-slotfloor), so its own diff is the one finding and the four steps the
ruling on it returned.

**The ruling.** #201 comment 6240984157, under mandate 6175172275: accept the
fix. The two-law pricing is the defect; the `docs/how-it-works.md` sentence
described what #1530 left behind, not a recorded design decision. Its steps:
(1) the docs sentence, (2) repair `k1725_blas_kernel_gap.py` and re-derive the
`tests/optimality.py` ftol bound from a kernel matrix, (3) route
`coverage_floor_override` into the production-call floor and add the override
in `tests/stress_budgets.json` at CI's measured counts, (4) state each
re-planned stress scenario's solver work against baseline from CI's stress log.

**Pending**, each named so this body is not read as complete:
- **the ftol check** (step 2). CI's fast lane at `74f23814e` reads production
  `60.96` and the both-sites 1e-2 arm `60.96` (0.00% gap); Accelerate reads
  +0.635%. Half the smallest gap is zero, so no bound separates. The
  orchestrator's ruling: race production against the ftol 1e-8 fixed point
  instead, decided from the kernel matrix's tight-arm numbers; if production
  equals that fixed point on every kernel point, retire the check with the
  per-kernel measurements as the recorded reason. The matrix comes from this
  branch's new `kernel-points` job (below), run on the pull request's label.
- **CI's stress log at this head**: the two coverage figures and the step-4
  solver-work comparison are re-taken from it, not carried; the figures below
  are CI's at `74f23814e`, the counts the entry was set from.

**D2-s2-01** (#2238, low, class P2). `ThermalModel.compute_cop_dhw` took its law
from the space circuit's valve flag. With `cop_flow_carnot` the tank paid
`_cop_law`'s Carnot lift at its own water temperature; without it, a linear
0.008/K penalty floored at 0.5. The flag is a space-circuit fact -- whether a
passed flow temperature is the supply the machine runs at -- and has no reading
on how hard a hot-water tank is to heat. The tank now pays `_cop_law` at its own
water temperature on both plants: one law, one-sided, the ratio the buffer
pays. The alternative -- make both arms linear -- loses: the linear form is the
fitted %/K that hits the floor at storage temperatures where a real unit still
manages 1.5-2.0, and it is the arm that grants the below-reference boost
`_batch_cop`'s own comment refuses.

**How the branch was built.** The held branch `e1eca9bfa` carried all three
findings from `92accb2cf`. Its D2-only delta (`c4304bb1f..e1eca9bfa`) is merged
onto the primary head as a merge of that ref (`e438816e3`), so the ref
fast-forwards. Two repairs to that delta:
`tests/golden/claimed_drift.txt` keeps this delta's 41 claims, with both sides'
notes, and drops main's four inherited claim lines as the claimnotes driver
directs; and `tests/closures.json` had lost the slot-floor census inert read the
primary added after the held branch was cut -- a silent revert, restored to the
primary's bytes in `dfb12c47e`.

Since then: `329514767` merges the primary's reviewed head `a0c0f8665` (one
conflict, `tests/entities.py`'s P2 table: D2's `cop_law_fork` entry kept, the
primary's slot-floor comment taken; against `a0c0f8665` the merged tree
differs only in this finding's files), `da32f7ec9` merges `origin/main`
`994695e06` (delivery records only), `04ea8dbb6` adds the kernel job,
`26e097a12` adds it to the stale-contract follower's watched list,
`b575020d4` and `f1878b10b` are the explicit production-call floor and the
budget entry (`## Raise justification`), and `dcda811e4` merges `origin/main`
`c09d61dc9`. That merge had two conflicts, both sides kept:
`coordinator.py`'s `FORECAST_STEP` keeps the primary's one-owner width
(`plan_step.PLAN_STEP_MINUTES`) under main's comment naming
`drift.utc_step_starts`, and `tests/dst_checks.py` imports main's
`utc_step_starts` and no longer `_solve_anchor`, which the primary folded into
`plan_step.plan_step_start`.

`7822a7423` repairs a check that merge brought in. Main's R10-DEEPLINK-CENSUS
census in `tests/card.mjs` presses the slot menu's `add`/`remove` by
right-clicking the plan charts at x=300 and x=600; which row renders depends
on where the solver put the hot-water runs, and with this finding's re-priced
tank none of the four pixels lands on a run, so the merged head read
`unpressed remove` (`1 CARD CHECK(S) FAILED`) with the card unchanged. The
gesture now walks each chart in 20 px steps until both branches are pressed:
`ALL CARD CHECKS PASSED` here and on `c09d61dc9`'s tree; with the card's
`editable` test forced false the census still fails `unpressed remove`
(`4 CARD CHECK(S) FAILED`).

`e7e7db805` merges the primary's new head `3ca9f1943` (its resolution against
origin/main `42e6dedb2`: the same two conflicts this branch resolved in
`dcda811e4`, resolved the same way, plus main's `log_latch.py` counted beside
`plan_step.py` -- 79 modules, 97 package files) with no conflict, and
`2cf679716` merges origin/main `d79dd4952` (record files only).

**The `kernel-points` job** (`.github/workflows/kernel-points.yml`, ruling
step 2, in the shape the orchestrator approved): outside the required set,
started only by `workflow_dispatch` or the `kernel-points` pull-request label,
never by a push. It runs `dev/audit/harnesses/k1725_blas_kernel_gap.py` under
`OPENBLAS_CORETYPE` unset (the runner's native kernel), Haswell, Sandybridge
and Nehalem, on the `fast` job's hash-pinned install, and writes each leg's
`environment:` and `RESULT` lines to its step summary. The file joins the two
closures that read every workflow (`tests/entities.py`,
`tests/harness_headers.py`), and `pr-contract-rerun.yml` now watches it:
`tests/entities.py`'s D13-s1-03 check requires that follower to watch every
pull-request workflow but the contract, and failed on `04ea8dbb6` until it
did. Both are `.github/workflows/` changes, so tvofi approves them at merge.

## Head

`2cf679716`, against the merge base `d79dd4952` (`origin/main`). This
finding's production file `thermal_model.py` is byte-identical to
`f89848334`, where the D2-s2-01 and step-3 mutants below were taken
(`git diff f89848334 2cf679716 -- custom_components/heatpump_optimizer/thermal_model.py`
is empty); `tests/stress.py` differs from it only by `b575020d4`, whose own
mutants were taken at `f1878b10b`; everything else that moved since is the
primary's reviewed head and main.
Before that merge the head was `f89848334`, against `6e5753a4a`. The "before"
arm of every D2 figure is the primary head `03bffee33`, where
`compute_cop_dhw` still has two laws; `thermal_model.py` there is
byte-identical to `6e5753a4a`'s. The k1725 head arm was taken at `2ccfcd3ed`:
`git diff --stat 2ccfcd3ed f89848334` names only
`dev/audit/harnesses/r10_dhw_lift_law_grid.py`, `tests/closures.json` and
`tests/stress.py`, none of which the harness imports.

## Mutation proof

Each mutant ran in its own `git archive f89848334` export; the worktree was not
mutated.

**D2-s2-01.** `thermal_model.py` put back to `03bffee33`'s (the two-law
`compute_cop_dhw`, the only production difference: 16 lines).
`python3 tools/audit/seat/features_block.py "R10-PUMP-MODEL -- DHW lift, the
duty floor channel, the step-start fold"` prints `3 of 7 FEATURES BLOCK FAILED`:

    FAIL D2-s2-01: the space-valve flag does not price the hot-water tank -- both
      plants charge one lift, over the whole outdoor/tank grid  [worst ratio
      1.4346 at outdoor=7.0 tank=65.0]
    FAIL D2-s2-01: the tank's price is _cop_law at the tank's own water
      temperature, humidity and all -- not a penalty of its own  [o=7 T=65
      direct 2.66 law 1.8541518628970441]
    FAIL D2-s2-01: a tank below the reference flow earns no lift and a hot one
      pays it (the one-sided rule _batch_cop states)  [below-ref boost 1.2000,
      65 C price 2.6600 vs base 3.5000]

At the head the block prints `ALL 7 FEATURES BLOCK PASSED`. In the same
mutant `PYTHONPATH=tests/hastub python3 tests/entities.py` fails the P2 entry:

    FAIL P2 owners: cop_law_fork is decided only by its owner or a
      dispositioned site, its owner exists, no disposition is stale, the rule is
      live  [SEAM ['thermal_model.py:2204 in ThermalModel.compute_cop_dhw']
      OWNER-MISSING [] STALE-DISPOSITION [] DEAD-RULE False (hits=4)]

with the planted-sibling null-control check failing beside it (every plant now
also trips `cop_law_fork`); the unmutated export (M0) fails neither line.

**Step 3, the override routing** (`tests/stress.py`, `coverage_floors`). The
two self-checks it adds were driven through
`$SCRATCH/drv/floors_drive.py <tree>`, a scratch driver that imports
`tests/stress.py` and runs the same two predicates without the sweep:
- head: `check_override_reaches_both=ok check_sites_read_function=ok`,
  `literal=(40, 15, None) override=(30, 12, 'ruling')` over 20 families of 54;
- M3, the calls floor computed from the literal inside `coverage_floors`:
  `override=(30, 15, 'ruling')`, `check_override_reaches_both=FAIL`;
- M4, the `_calls_floor` site put back to the literal expression:
  `check_sites_read_function=FAIL reads={'_floor': 'coverage_floors',
  '_calls_floor': None}`.

**The explicit production-call floor** (`b575020d4`, `tests/stress.py`
`coverage_floors`, and `tools/policy/budget_raise_gate.py`). Test first: the
self-check `coverage floors: an override naming both floors is held to both,
and a malformed production-call floor is the share rule` was written against
`26e097a12`'s `coverage_floors` and driven through
`$SCRATCH/drv/floors_drive.py <tree>`: `both=(18, 7, 'ruling')`,
`check_explicit_calls_floor=FAIL`; after the change `both=(18, 6, 'ruling')`,
`ok`. Each mutant below ran in its own `git archive f1878b10b` export, judged
by the same driver and by `$SCRATCH/drv/table_floors.py <tree>`, which reads
the tree's committed budget table and holds its floors to CI's 18 of 54 and
6 of 20:
- M0 (unmutated): `check_explicit_calls_floor=ok`; `work_floor=18
  calls_floor=6 work_check=ok calls_check=ok`.
- M5, the explicit field dropped from `coverage_floors` (the override reads
  the share rule): `check_explicit_calls_floor=FAIL`; `calls_floor=7
  calls_check=FAIL` -- red at 6 of 20.
- M6, `calls_floor` dropped from the committed entry: `calls_floor=7
  calls_check=FAIL`.
- M7, the gate's `calls_floor` OVERRIDE rule deleted: `python3
  tools/policy/budget_raise_gate.py --self-test` fails `the production-call
  floor raised is routine` and `... withdrawn is routine`, 4 failed against
  M0's 2 (both arms' other two are the export having no git repository; in
  the worktree the self-test reads `239 checks, 0 failed`).

## Null control

- **The grid census** (`r10_dhw_lift_law_grid.py`): at a 35 °C tank, the
  reference flow where both laws must agree, `null_max_diff=0.000e+00` at both
  ends; its `--perturb` arm reinstates the retired linear law in-process and
  reproduces the before arm to the digit at the head, so the head's zeros are
  the fix and not a grid on which the laws coincide.
- **The flag is not inert.** The block's fourth D2 check reads the flag pricing
  the SPACE buffer's lift, green in the mutant and at the head.
- **k1725** carries `stop_repeat_identical=1` at both ends (two solves in one
  process are bit-identical, so the kernel and the tree are the only movers).
- **The P2 class census** returns to 3 under its own `--perturb` at the head.
- **The coverage-floor checks**: the malformed overrides (above the literal, a
  bool, a blank citation, a float, a bare number) all read the literal, the
  arm's own null.

## Figures

- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_dhw_lift_law_grid.py
  --root <tree>`, 41 outdoor (-25..15 °C) x 51 tank (20..70 °C) at 1 K: before
  (`03bffee33`) `dev_cells=1861` of `cells=2091`, `worst_ratio=1.4548` at
  (7.0, 70.0), `within_ratio=1.3522` (one direct install: tank 2.9400 against
  the space lift's 2.1742 at 7 °C / 55 °C water), `below_ref_boost=1.1200`;
  head `dev_cells=0`, `worst_ratio=1.0000`, `within_ratio=1.0000`,
  `below_ref_boost=1.0000`; head `--perturb` equal to the before arm in every
  value. The features block's own grid (6 outdoors x tanks 10, 35, 45, 55,
  65 °C) reads its worst at 1.4346 (7 °C / 65 °C) and a below-reference boost
  of 1.2000 at its 10 °C tank, the finding's figures; this census runs to
  70 °C and from 20 °C, which is why it reads 1.4548 and 1.1200.
- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/k1725_blas_kernel_gap.py`,
  Apple M1 / Accelerate, numpy 2.4.6, Python 3.14.7: before (`03bffee33`)
  `stop_prod_cost=61.28`, `stop_both_1e2_cost=64.97`,
  `stop_check_gap_pct=+5.682`, `stop_tight_1e8_gap_pct=-2.760`; head
  (`2ccfcd3ed`) `stop_prod_cost=60.58`, `stop_both_1e2_cost=60.96`,
  `stop_check_gap_pct=+0.635`, `stop_tight_1e8_gap_pct=-0.000` (production is
  its own ftol 1e-8 fixed point), and every loosened arm at +0.635 to +0.637.
  At the merge base the same harness raised TypeError (the pre-WeatherSeries
  `simulate_trajectory` call this branch repairs).
- `python3 dev/audit/rounds/round10/D14/sweep-P2/enumerate_p2.py`, run inside
  each tree: `F3_cop_law_fork=3` before (seams `compute_cop`,
  `compute_cop_dhw`, `_batch_cop`), `2` at the head (`compute_cop`,
  `_batch_cop`, the registered owners); `--perturb` at the head `before=2
  after=3 moved=1`.
- Scope, `python3 tests/closure.py select --diff c09d61dc9`: `MODE: SCOPED -- 28
  script(s) run, 5 scoped out` over 42 changed files. Run here at `dcda811e4`:
  `PYTHONPATH=tests/hastub python3 tests/features.py` `ALL 4170 FEATURE CHECKS PASSED`;
  `tests/entities.py` `ALL 2348 ENTITY CHECKS PASSED` (at `04ea8dbb6` it read
  `1 of 2348 ENTITY CHECKS FAILED`, the follower check above); `tests/doc_claims.py` `ALL 169 checks
  PASSED` (the two regenerated `docs/img/model/` figures fresh); `block_duty`,
  `deployment_shape`, `guard_pins`, `manual_plan`, `solar_alignment`,
  `wood_advisor`, `plan_view`, `debug_collect`, `config_flow_steps`,
  `typing_ruler`, `structure` and `node tests/md_tables.mjs` each exit 0;
  `node tests/card.mjs` at `7822a7423` `ALL CARD CHECKS PASSED`;
  `python3 tests/env_drift.py --claims-only` `claims hygiene: origin/main ok`.
  The heavy scoped scripts (`stress.py`, `optimality.py`, `golden.py`,
  `backtest.py` and the rest of `scope.run`) are CI's.
- At `2cf679716`, cheap checks only (the heavy lanes are CI's under tvofi's
  heavy-to-CI rule): `python3 tests/closure.py select --diff d79dd4952`
  `MODE: SCOPED -- 28 script(s) run, 5 scoped out` over 43 changed files;
  `STRUCTURE RATCHET PASSED`; `tests/doc_claims.py` `ALL 169 checks PASSED`;
  `tests/deployment_shape.py` `ALL DEPLOYMENT SHAPE CHECKS PASSED`;
  `node tests/card.mjs` `ALL CARD CHECKS PASSED`; `python3
  tools/policy/budget_raise_gate.py --self-test` `239 checks, 0 failed`; the
  floors drivers `check_explicit_calls_floor=ok`, `work_floor=18
  calls_floor=6`; `claims hygiene: origin/main ok`. `features.py` and
  `entities.py` above are `dcda811e4`'s; the primary's resolution re-ran both
  at `3ca9f1943` (`ALL 4171 FEATURE CHECKS PASSED`, `ALL 2347 ENTITY CHECKS
  PASSED`), and CI's run at this head is the figure.
- `python3 tools/pr/ci_predict.py --base d79dd4952`: `CI PREDICT: no closures or
  fast red predicted against d79dd49529d7 (a data-file read is not seen)` --
  it does not run the heavy scripts, so it cannot see the two expected reds.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff d79dd4952 HEAD` at
  `2cf679716`: `dS +0.0000 NULL` (`--diff c09d61dc9 HEAD` at `dcda811e4`: the same); `--diff a0c0f8665` (the primary) at
  `04ea8dbb6`: `dS +0.0000 NULL`.

## Raise justification

`tests/stress_budgets.json` gains `coverage_floor_override` at `floor: 18`,
`calls_floor: 6` (`f1878b10b`): CI's measured counts at `74f23814e` exactly
-- 18 of 54 scenarios judged by the solver-work check (literal floor 40) and
6 of 20 families by the production-call check (literal floor 15). Every
hot-water scenario re-plans because the tank's price changed, so it drops out
of both comparisons. Sanctioned by ruling #201 comment 6240984157 step 3
under mandate 6175172275; the orchestrator ruled the explicit floors at the
measured values and refused a floor of 16 under the share rule as unearned
headroom.

Payments tried:
1. Narrow the fix so fewer scenarios re-plan (keep the linear law on valve
   plants): refused -- that law is the defect the ruling accepted fixing.
2. Split the pull request: no lower count -- all 36 hot-water scenarios
   re-plan on whichever half carries the law change.
3. Re-record the baseline: impossible -- the baseline is main's tree solved
   beside the run, not a recording a branch can move.
4. Judge re-planned scenarios by a per-scenario work statement instead of a
   floor: a larger change to `tests/stress.py`, and the ruling chose the
   override; the statement is given anyway (CI at `74f23814e`: 36 re-planned
   scenarios from 0.34x, `shoulder/tariff+cycle` 1180 vs 3462 evaluations, to
   1.37x, `winter_mild/1z/dhw` 852 vs 622, none over the 3.0x factor).
5. The share rule alone: floor 18 rounds to a calls floor of 7 against the
   measured 6, and the largest floor holding both, 16, is 2 below the measured
   work count -- so the override names the calls floor explicitly
   (`b575020d4`), the share rule staying the default for every other entry and
   for main.

No code payment exists: `tools/audit/archscore/` reads only
`custom_components/`, and the entry is a JSON file under `tests/`.
`python3 tools/audit/archscore/score.py --diff <merge base> <head>`, against
the merge base `994695e06`, before the entry (`26e097a12`) and after it
(`f1878b10b`), each:
Architecture score: dS +0.0000 NULL

`tools/policy/budget_raise_gate.py` is code-owned (`.github/CODEOWNERS`
`@tvofi`), so its new rule is tvofi's to approve at merge, with the two
workflow files.

## Red checks

**`fast (3.14)`** is red at `74f23814e` on exactly two scripts, both this
fix's own blast radius, and the same two are expected on this head:
- **`optimality.py`, `the production stop rule (ftol) buys a materially better
  plan`**: at the head the loosened arm lands 0.635% above production on
  Accelerate, under the 2.5% bound. Production's ftol is unchanged; the plan is
  better conditioned (it is now its own ftol 1e-8 fixed point), so the bound
  no longer separates; on CI's own kernel the gap is 0.00% (`60.96` both).
  Answered by the ruled re-derivation under **Pending** (the 1e-8 race, or the
  check's retirement on the kernel matrix). Cheaper detector: none -- this
  block is the only place the stop rule is raced.
- **`stress.py`, the solver-work and production-call coverage floors**: every
  scenario with hot water re-plans, because the price of hot water changed:
  CI judged 18 of 54 (floor 40) and 6 of 20 families (floor 15), `2 of 112
  STRESS CHECKS FAILED`. Answered by the override entry at exactly those
  counts (`## Raise justification`); green here only if CI's counts at this
  head hold. Cheaper detector: none -- coverage is a property of a stress run.
- **`budget-raise-gate`** is red at this head by design: 2 budget raises in
  `tests/stress_budgets.json` -- the override added at `floor: 18`, and
  `coverage_floor_override.calls_floor: None -> 6`, which the base's copy of
  `tools/policy/budget_raise_gate.py` reads as a pinned value it cannot sign
  (the `calls_floor` OVERRIDE rule is this branch's, `b575020d4`, and binds
  only once it is on main; under either copy the leaf is a raise). Answered
  by `## Raise justification`; it stays red until the raise is approved at
  this head. Cheaper detector: none -- this gate is the detector, and
  `tools/pr/prepr.sh` already ran it here.
- **`pr-contract`** was red at `74f23814e` on one error: `## Red checks` did
  not name `fast (3.14)`. The body named both failing scripts as expected
  reds but not the context they run under. Cheaper detector: none --
  `tools/pr/prepr.sh` lints a body before the CI conclusion it would have to
  match exists; naming the context of an expected red is the body's own duty,
  and this section now does.
- `golden.py` / `env_drift.py` drift is claimed (41 fixtures in
  `tests/golden/claimed_drift.txt`); a red there that names an unclaimed
  fixture is a new finding.

## Forward-carry

`none` -- nothing here narrows a later stage's technique, invalidates a figure it rests on, or removes an option it expected: the ftol bound and the coverage override are this branch's own re-derivations under its ruling.

## Unpinned sites

`prepr.sh` step 6d lists what the diff adds. The one production site this
finding adds is `compute_cop_dhw`'s return, pinned by
`tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.compute_cop_dhw.RETURN_DEL.a4eaefe8.json`,
which `python3 tests/mutation_table.py --pin-killed` wrote on the held branch
and this merge carries; `ThermalModel.compute_cop_dhw GUARD_OFF ca964a78`
retires with the `cop_flow_carnot` guard it pinned. The ledger's verdict at
this head is CI's mutation check.

## Friction

- `dev/governance/rules/claim-files.md: contradiction: a fixture whose baseline_cost moves cannot be claimed while it carries a may-drift entry, and a may-drift entry cannot excuse a judged-key move, so the held branch suspended twelve owner-sanctioned may-drift entries for the release -- the R8-P3 wood_coil precedent, recorded nowhere as the rule.`
- `dev/governance/roles/fixer.md: cost: a held branch cut from an older base carries stale copies of files its sibling branch has since changed; its delta re-applied onto the sibling's head reverts those lines with no conflict (tests/closures.json here), so a re-applied delta is diffed against the sibling head line by line before it is committed.`
