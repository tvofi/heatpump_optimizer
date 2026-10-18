Round 10, group `R10-PUMP-MODEL`, its third finding: what the model charges
for a hot-water tank. Part of #2232 and #2238. The group's primary
(D7-arch3-04 and D7-s3-8x-slotfloor) merged as #2365, so its code is now the
base: this PR's diff over `main` is the one finding and the four steps the
ruling on it returned. This body is re-cut at the new head; round history is
dropped.

**The ruling.** #201 comment 6240984157, under mandate 6175172275: accept the
fix. The two-law pricing is the defect; the `docs/how-it-works.md` sentence
described what #1530 left behind, not a recorded design decision. Its steps:
(1) the docs sentence, (2) repair `k1725_blas_kernel_gap.py` and re-derive the
`tests/optimality.py` ftol bound from a kernel matrix, (3) route
`coverage_floor_override` into the production-call floor and add the override
in `tests/stress_budgets.json` at CI's measured counts, (4) state each
re-planned stress scenario's solver work against baseline from CI's stress log.

**Pending**, each named so this body is not read as complete:
- **the ftol check** (step 2). CI's fast lane at `74f23814e` read production
  `60.96` and the both-sites 1e-2 arm `60.96` (0.00% gap); Accelerate reads
  +0.635% (below). Half the smallest gap is zero, so no bound separates. The
  orchestrator's ruling: race production against the ftol 1e-8 fixed point
  instead, decided from the kernel matrix's tight-arm numbers; if production
  equals that fixed point on every kernel point, retire the check with the
  per-kernel measurements as the recorded reason. The matrix comes from this
  branch's `kernel-points` job (below), run on the pull request's label.
- **CI's stress log at this head**: the two coverage figures and the step-4
  solver-work comparison are re-taken from it, not carried. The figures below
  are CI's at `74f23814e`, the counts the override was set from; the stress
  baseline is now `main`, which includes #2365.

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

**The kernel-points job** (`.github/workflows/kernel-points.yml`, ruling
step 2, in the shape the orchestrator approved): outside the required set,
started only by `workflow_dispatch` or the `kernel-points` pull-request label,
never by a push. It runs `dev/audit/harnesses/k1725_blas_kernel_gap.py` under
`OPENBLAS_CORETYPE` unset (the runner's native kernel), Haswell, Sandybridge
and Nehalem, on the `fast` job's hash-pinned install, and writes each leg's
`environment:` and `RESULT` lines to its step summary. The file joins the two
closures that read every workflow, and `pr-contract-rerun.yml` watches it
(`tests/entities.py`'s D13-s1-03 check requires that follower to watch every
pull-request workflow but the contract). Both are `.github/workflows/`
changes, so tvofi approves them at merge.

**The card census** (`tests/card.mjs`). Main's R10-DEEPLINK-CENSUS check
presses the slot menu's `add`/`remove` by right-clicking the plan charts at
fixed pixels; which row renders depends on where the solver put the hot-water
runs, and with the re-priced tank none of the fixed pixels landed on a run.
The gesture now walks each chart in 20 px steps until both branches are
pressed.

**How this head was reached.** The PR branch (`74f23814e`) lacked the
seat's later work on `handoff/r10-pump-model-d2` (`2cf679716`: the kernel job,
the explicit production-call floor and its budget entry, the card census).
This head merges `origin/main` `211c8290e` into `74f23814e` (`79b90e1a1`),
then `2cf679716` (`72a9e232d`), then `origin/main` `c8cc75ea9`
(`e77b587d3`), so it fast-forwards both the PR branch and the handoff ref.
One conflict, `tests/entities.py`'s P2 owners table: this branch's
`cop_law_fork` entry kept, main's rewording of the `slot_floor_rule` comment
(#2365's review: `plan_step.plan_step_start` is the owner) taken. The other two
merges were clean (`tests/closures.json` through the ledger driver). The D2
delta's own lines survive the first merge unchanged: `git diff 03bffee33
f89848334` and `git diff 211c8290e 79b90e1a1` (less this PR's delivery row),
each reduced to its `+`/`-` lines, compare equal under `diff`, which printed
nothing; the two later merges add only the handoff ref's seven files and
main's tooling.

## Head

`e77b587d3243f6f25338591ce6f2253b7be0be11`, against the merge base
`c8cc75ea9` (`origin/main`, 2026-10-18 UTC). `thermal_model.py` at `c8cc75ea9`
is byte-identical to the primary head `03bffee33`'s (`git diff --quiet`,
rc 0), so `origin/main` is the "before" arm of every D2 figure. Every figure
below was taken at this head, the worktree or a `git archive` export of it,
unless it names CI's run at `74f23814e`.

## Mutation proof

Each mutant ran in its own `git archive e77b587d3` export; the worktree was
not mutated.

**D2-s2-01.** `thermal_model.py` put back to `c8cc75ea9`'s (the two-law
`compute_cop_dhw`, the only production difference: 16 lines).
`python3 tools/audit/seat/features_block.py "R10-PUMP-MODEL -- DHW lift, the
duty floor channel, the step-start fold"` prints `3 of 10 FEATURES BLOCK
FAILED`:

    FAIL D2-s2-01: the space-valve flag does not price the hot-water tank -- both
      plants charge one lift, over the whole outdoor/tank grid  [worst ratio
      1.4346 at outdoor=7.0 tank=65.0]
    FAIL D2-s2-01: the tank's price is _cop_law at the tank's own water
      temperature, humidity and all -- not a penalty of its own  [o=7 T=65
      direct 2.66 law 1.8541518628970441]
    FAIL D2-s2-01: a tank below the reference flow earns no lift and a hot one
      pays it (the one-sided rule _batch_cop states)  [below-ref boost 1.2000,
      65 C price 2.6600 vs base 3.5000]

The unmutated export (M0) prints `ALL 10 FEATURES BLOCK PASSED`. In the same
mutant `PYTHONPATH=tests/hastub python3 tests/entities.py` fails the P2 entry:

    FAIL P2 owners: cop_law_fork is decided only by its owner or a
      dispositioned site, its owner exists, no disposition is stale, the rule is
      live  [SEAM ['thermal_model.py:2204 in ThermalModel.compute_cop_dhw']
      OWNER-MISSING [] STALE-DISPOSITION [] DEAD-RULE False (hits=4)]

with the planted-sibling null-control check failing beside it (every plant now
also trips `cop_law_fork`). M0's and the mutant's `FAIL` lines, sorted and
compared with `diff`, differ in those two lines and in `a8:register_once`,
whose printed `extra` list is a set in another order; the rest are the
export's own (it is not a git checkout) and identical in both.

**Step 3, the override routing and the explicit production-call floor**
(`tests/stress.py` `coverage_floors`, `tests/stress_budgets.json`,
`tools/policy/budget_raise_gate.py`). Driven through two scratch drivers that
import the tree's `tests/stress.py`: `$SCRATCH/drv/floors_drive.py <tree>`
runs stress.py's three coverage-floor self-check predicates without the
sweep; `$SCRATCH/drv/table_floors.py <tree>` reads the tree's committed budget
table and holds its floors to CI's 18 of 54 and 6 of 20.
- M0: `check_override_reaches_both=ok check_sites_read_function=ok`,
  `literal=(40, 15, None) override=(30, 12, 'ruling')` over `pop=20 sweep=54`;
  `both=(18, 6, 'ruling') check_explicit_calls_floor=ok`; `work_floor=18
  calls_floor=6 work_check=ok calls_check=ok`.
- M3, the share in `coverage_floors` taken from the literal:
  `override=(30, 15, 'ruling')`, `check_override_reaches_both=FAIL`,
  `check_explicit_calls_floor=FAIL`.
- M4, the `_calls_floor` site put back to the literal expression:
  `check_sites_read_function=FAIL reads={'_floor': 'coverage_floors',
  '_calls_floor': None}`.
- M5, the explicit field dropped from `coverage_floors`:
  `both=(18, 7, 'ruling') check_explicit_calls_floor=FAIL`; `calls_floor=7
  calls_check=FAIL`, red at 6 of 20.
- M6, `calls_floor` dropped from the committed entry: `calls_floor=7
  calls_check=FAIL`.
- M7, the gate's `calls_floor` OVERRIDE rule deleted: `python3
  tools/policy/budget_raise_gate.py --self-test` fails `the production-call
  floor raised is routine` and `... withdrawn is routine`, `204 checks, 4
  failed` against M0's `204 checks, 2 failed` (both arms' other two are the
  export having no git repository; in the worktree the self-test reads `239
  checks, 0 failed`).

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
  bool, a blank citation, a float, a bare number) all read the literal, and
  the malformed production-call floors all read the share rule, each arm's
  own null.

## Figures

- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_dhw_lift_law_grid.py
  --root <tree>` (sha1 `7563d2e650a0ed96d546ba7dfd49c35c39aa9ed0`), 41 outdoor
  (-25..15 °C) x 51 tank (20..70 °C) at 1 K: before (`c8cc75ea9`)
  `dev_cells=1861` of `cells=2091`, `worst_ratio=1.4548` at (7.0, 70.0),
  `within_ratio=1.3522` (one direct install: tank 2.9400 against the space
  lift's 2.1742), `below_ref_boost=1.1200`; head `dev_cells=0`,
  `worst_ratio=1.0000`, `within_ratio=1.0000`, `below_ref_boost=1.0000`; head
  `--perturb` equal to the before arm in every value. The features block's own
  grid (6 outdoors x tanks 10, 35, 45, 55, 65 °C) reads its worst at 1.4346
  (7 °C / 65 °C) and a below-reference boost of 1.2000 at its 10 °C tank, the
  finding's figures; this census runs to 70 °C and from 20 °C, which is why it
  reads 1.4548 and 1.1200.
- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/k1725_blas_kernel_gap.py`,
  the head's copy run in each tree, Apple M1 / Accelerate, numpy 2.4.6,
  Python 3.14.7: before (`c8cc75ea9`) `stop_prod_cost=61.28`,
  `stop_both_1e2_cost=64.97`, `stop_check_gap_pct=+5.682`,
  `stop_tight_1e8_gap_pct=-2.760`; head `stop_prod_cost=60.58`,
  `stop_both_1e2_cost=60.96`, `stop_check_gap_pct=+0.635`,
  `stop_tight_1e8_gap_pct=-0.000` (production is its own ftol 1e-8 fixed
  point). `main`'s own copy of the harness is the pre-WeatherSeries one this
  branch repairs.
- `python3 dev/audit/rounds/round10/D14/sweep-P2/enumerate_p2.py`, each tree's
  own copy run in that tree: `F3_cop_law_fork=3` before (seams `compute_cop`,
  `compute_cop_dhw`, `_batch_cop`), `2` at the head (`compute_cop`,
  `_batch_cop`, the registered owners); `--perturb` at the head
  `perturb.F3_cop_law_fork before=2 after=3 moved=1`.
- Scope, `python3 tests/closure.py select --diff c8cc75ea9`: `MODE: SCOPED --
  28 script(s) run, 5 scoped out` over 20 changed files. Run here at this head:
  `PYTHONPATH=tests/hastub python3 tests/features.py` `ALL 4179 FEATURE CHECKS
  PASSED`; `tests/entities.py` `ALL 2348 ENTITY CHECKS PASSED`;
  `tests/doc_claims.py` `ALL 169 checks PASSED`; `tests/deployment_shape.py`
  `ALL DEPLOYMENT SHAPE CHECKS PASSED`; `node tests/card.mjs` (after
  `tests/plan_view.py`) `ALL CARD CHECKS PASSED`; `python3
  tools/policy/budget_raise_gate.py --self-test` `239 checks, 0 failed`;
  `python3 tests/env_drift.py --claims-only` `claims hygiene: origin/main ok`.
  The heavy scoped scripts (`stress.py`, `optimality.py`, `golden.py`,
  `backtest.py` and the rest of `scope.run`) are CI's.
- `python3 tools/pr/ci_predict.py --base c8cc75ea9`: `CI PREDICT: no closures or
  fast red predicted against c8cc75ea90a3 (a data-file read is not seen)` --
  it does not run the heavy scripts, so it cannot see the expected reds.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff c8cc75ea9`: `Architecture
  score: dS +0.0000 NULL`.

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
1. Narrow the fix so fewer scenarios re-plan (keep the linear law on direct
   plants): refused -- that law is the defect the ruling accepted fixing.
2. Split the pull request: no lower count -- all 36 hot-water scenarios
   re-plan on whichever half carries the law change.
3. Re-record the baseline: impossible -- the baseline is main's tree solved
   beside the run, not a recording a branch can move.
4. Judge re-planned scenarios by a per-scenario work statement instead of a
   floor: a larger change to `tests/stress.py`, and the ruling chose the
   override; the statement is step 4's, from CI's stress log at this head.
5. The share rule alone: floor 18 rounds to a calls floor of 7 against the
   measured 6, and the largest floor holding both, 16, is 2 below the measured
   work count -- so the override names the calls floor explicitly, the share
   rule staying the default.

No code payment exists: `tools/audit/archscore/` reads only
`custom_components/`, and the entry is a JSON file under `tests/`.
`python3 tools/audit/archscore/score.py --diff c8cc75ea9` at this head:
Architecture score: dS +0.0000 NULL

`tools/policy/budget_raise_gate.py` is code-owned (`.github/CODEOWNERS`
`@tvofi`), so its new rule is tvofi's to approve at merge, with the two
workflow files.

## Red checks

At the previous head `74f23814e`:
- **`fast (3.14)`** (check-run 117553042465) was red on exactly two
  scripts, both this fix's own blast radius:
  - **`tests/optimality.py`, `the production stop rule (ftol) buys a
    materially better plan`**: `ftol 1e-6 60.96 vs loosened 1e-2 both sites
    60.96 (-0.00% gap, bound 2.5%)`. Production's ftol is unchanged; the plan
    is better conditioned (production is now its own ftol 1e-8 fixed point),
    so the loosened arm no longer lands in a worse basin. Expected red again
    here; answered by the ruled re-derivation under **Pending** (the 1e-8
    race, or the check's retirement on the kernel matrix). Cheaper detector:
    none -- this block is the only place the stop rule is raced.
  - **`tests/stress.py`, the two coverage floors**: `only 18 of 54 scenarios
    are judged, against a floor of 40` (36 re-planned, 0 without a baseline
    solve) and `6 covered` of 20 families against 15, `2 of 112 STRESS CHECKS
    FAILED`: every scenario with hot water re-plans, because the price of hot
    water changed. That head had no override; this one carries it at exactly
    those counts (`## Raise justification`), so it is green here only if CI's
    counts at this head, against the new baseline, hold. Cheaper detector:
    none -- coverage is a property of a stress run.
- **`pr-contract`** was red on one error: `## Red checks` did not name
  `fast (3.14)`; the body named both failing scripts but not the context they
  run under. Cheaper detector: none -- `tools/pr/prepr.sh` lints a body before
  the CI conclusion it must match exists; this section now names it.

Expected at this head:
- **`budget-raise-gate`**, red by design on the override's two leaves
  (`floor`, and `calls_floor: None -> 6`, which the base's copy of the gate
  reads as a pinned value it cannot sign; the `calls_floor` OVERRIDE rule is
  this branch's and binds once on main). Answered by `## Raise
  justification`; red until the raise is approved at this head. Cheaper
  detector: none -- this gate is the detector.
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
- `dev/governance/roles/fixer.md: cost: a fixer dispatched to a PR head can miss later work on the topic's handoff ref (here 2cf679716 carried five D2 commits the PR branch did not: 04ea8dbb6, 26e097a12, b575020d4, f1878b10b, 7822a7423), so the brief should name both refs, and a seat compares them before merging main.`
