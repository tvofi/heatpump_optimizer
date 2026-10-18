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

**Pending CI**, each named so this body is not read as complete:
- **the ftol bound** (step 2): the Accelerate point is measured below; the
  CI-runner and OpenBLAS kernel points come from CI, and the bound is half the
  smallest gap, shown still red when production ftol is loosened;
- **the `coverage_floor_override` value** (step 3): set at CI's measured
  covered counts, with `## Raise justification`, reported to the orchestrator
  before it is pushed;
- **the step-4 solver-work comparison**: per re-planned scenario, from CI's
  stress log, against the 3.0x work factor.

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

## Head

`f89848334`, against the merge base `6e5753a4a` (`origin/main`). The "before"
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
- Scope, `python3 tests/closure.py select --diff 6e5753a4a`: `MODE: SCOPED -- 28
  script(s) run, 5 scoped out` over 22 changed files. Run here:
  `PYTHONPATH=tests/hastub python3 tests/features.py` `ALL 4162 FEATURE CHECKS PASSED`;
  `tests/entities.py` `ALL 2348 ENTITY CHECKS PASSED`; `tests/doc_claims.py` `ALL 169 checks
  PASSED` (the two regenerated `docs/img/model/` figures fresh);
  `python3 tests/env_drift.py --claims-only` `claims hygiene: origin/main ok`.
  The heavy scoped scripts (`stress.py`, `optimality.py`, `golden.py`,
  `backtest.py` and the rest of `scope.run`) are CI's.
- `python3 tools/pr/ci_predict.py --base 6e5753a4a`: `CI PREDICT: no closures or
  fast red predicted against 6e5753a4aca8`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff 6e5753a4a`: `Architecture
  score: dS +0.0000 NULL`; `--diff 03bffee33`: `dS +0.0000 NULL`.

## Red checks

Expected on this head, both the fix's own blast radius, both pending CI:
- **`optimality.py`, `the production stop rule (ftol) buys a materially better
  plan`**: at the head the loosened arm lands 0.635% above production on
  Accelerate, under the 2.5% bound. Production's ftol is unchanged; the plan is
  better conditioned (it is now its own ftol 1e-8 fixed point), so the bound
  no longer separates. Step 2 re-derives it from the kernel matrix. Cheaper
  detector: none -- this block is the only place the stop rule is raced.
- **`stress.py`, the solver-work and production-call coverage floors**: every
  scenario with hot water re-plans, because the price of hot water changed.
  Step 3's override, at CI's counts, is the answer the ruling sanctions.
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
