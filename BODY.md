Round 10, group `R10-PUMP-MODEL`, its third finding: what the model charges
for a hot-water tank. Part of #2232 and #2238. The group's primary merged as
#2365, so this PR's diff over `main` is the one finding and the four steps of
the ruling on it. Re-cut at this head; round history is dropped.

**The ruling.** #201 comment 6240984157, under mandate 6175172275: accept the
fix. Its steps: (1) the `docs/how-it-works.md` sentence, (2) repair
`k1725_blas_kernel_gap.py` and re-derive the `tests/optimality.py` ftol bound
(or re-select the cell/arm) from a kernel matrix, half the smallest gap, still
red when production ftol is loosened, (3) route `coverage_floor_override` into
the production-call floor and add the override at CI's measured counts, (4)
state each re-planned stress scenario's solver work against baseline from CI's
stress log, growth past the 3.0x work factor voiding the acceptance. All four
are done in this body; what only CI can add is named under **Pending**.

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

**Step 2, the ftol check, re-selected by measurement.** At the old cell
(winter_typical prices, winter_cold weather) the kernel matrix at this head
reads production 60.96 SEK and every loosened arm -- both sites 1e-3 and 1e-2,
the round-4 single-site 1e-3 and 1e-2 -- 60.96 too, on Haswell (this box's
native kernel), SkylakeX, Sandybridge and Nehalem, and CI's fast lane read the
same pair at `c3a25d2ae`: with one lift law, a loosened stop rule lands on
production's own plan there, so no bound on that cell can separate, whatever
its arm. Racing production against the ftol 1e-8 fixed point (the
orchestrator's alternative) does not separate either: on the old cell
production sits 0.81-1.58% short of it on the x86 kernels while a loosened
production reads the same 60.96, so a loosening moves nothing such a race reads.
The check is not retired: `dev/audit/harnesses/r10_ftol_cell_search.py` (new)
raced production against the three loosened arms on 36 cells (two-zone and
single-zone x six winter/shoulder price profiles x three weathers, DHW on, the
check's house, state and date) under the four kernels. Two-zone /
winter_moderate / winter_cold is the one two-zone cell where every loosened arm
is costlier than production on every kernel, bit-identically across them: prod
80.2228, both sites 1e-3 81.5990 (+1.687%), single-site 1e-3 81.5410
(+1.617%), both sites 1e-2 83.0998 (+3.462%). The check now races the
both-sites 1e-3 arm there with a bound of half its smallest gap, 0.84%. Keying
on the wider 1e-2 arm was refused: a production loosened 1000x lands 1.80-1.88%
under it, above any bound half of 3.462 could hold, so only the 10000x class
would go red. `k1725_blas_kernel_gap.py` follows the check to the new cell and
arm, so the kernel-points job measures what the gate runs; on that cell
production is also its own ftol 1e-8 fixed point (objective 106.4690 both) on
all four kernels.

**The kernel-points job** (`.github/workflows/kernel-points.yml`): outside the
required set, started by `workflow_dispatch`, the `kernel-points` label, and --
new here -- a push to a pull request that carries the label. It runs
`k1725_blas_kernel_gap.py` under the runner's native kernel, Haswell,
Sandybridge and Nehalem on the `fast` job's hash-pinned install and writes each
leg's `environment:` and `RESULT` lines to its step summary. It had never run on
this branch because the label went on at 17:35:28Z, when the head was
`74f23814e`, which did not carry the file: a `labeled` event runs the workflow
at the head of that moment, and nothing re-fires it. The `synchronize` arm
makes the label a standing request, so the push carrying this head runs the
matrix. The file is in the two closures that read every workflow, and
`pr-contract-rerun.yml` watches it (`tests/entities.py`'s D13-s1-03 check).

**Step 3, the coverage override.** `tests/stress_budgets.json` carries
`coverage_floor_override` at `floor: 18`, `calls_floor: 6`, and
`coverage_floors` feeds both coverage checks. This head fixes the review's
soundness defect: a `calls_floor` was accepted anywhere below the literal's
share (15), so withdrawing a `calls_floor: 10` dropped the floor to the share
of 18 (7) while `budget_raise_gate.py` reads a withdrawal as routine. It must
now sit below the share of the override's own work floor, so the share rule is
always the stricter state and the gate's reading is true.

**The card census** (`tests/card.mjs`). Main's R10-DEEPLINK-CENSUS check
presses the slot menu's `add`/`remove` by right-clicking the plan charts at
fixed pixels; with the re-priced tank none of the fixed pixels landed on a
hot-water run. The gesture walks each chart in 20 px steps until both branches
are pressed.

**Pending**, each named so this body is not read as complete:
- **CI's kernel points.** The CI runner's native kernel (an AMD EPYC 9V45 at
  `c3a25d2ae`) is reached only by the `fast` job's own run of the check and by
  the kernel-points matrix, both on the push of this head. A native gap under
  +1.68% would re-derive the bound; one under +0.84% is the check red.
- **Accelerate** is not re-measured on the new cell: this seat is a Linux
  container. The ruling names Accelerate in the matrix; its point on this cell
  is owed by a Mac seat.

## Head

`8100b5e559b8734825a013192170eb5ebf4342ce`, which merges `origin/main` `106af95a3` (2026-10-18 UTC;
R10-CI-CONCURRENCY, touching no file in the solver, the thermal model or
`tests/stress.py`) into the PR head `c3a25d2ae` (`875c4b415`, clean, the
ledger driver on `tests/closures.json`) and adds five commits: the ftol cell
and arm (`e4f5a41e2`), the `calls_floor` bound (`18b5c0c14`), the
kernel-points trigger (`42d78852d`), the docstring nit kept line-neutral and
the new harness's citation fixed (`ce3d3bc6d`), and the harness's canonical
root walk (`8100b5e55`). Merge base `106af95a3`; 22 files over it. Every figure
below was taken at this head, its worktree or an export of it (`git archive`,
or `git ls-files` for the ftol mutants, taken at `e4f5a41e2`'s tree, whose
`tests/optimality.py` and `optimizer.py` equal this head's), unless it names
CI's run at `c3a25d2ae`.

## Mutation proof

**The ftol check** (`tests/optimality.py`, challenger 7). Each mutant is an
export of the tracked tree with `optimizer.py`'s production ftol edited;
`PYTHONPATH=tests/hastub python3 tests/optimality.py` in each:
- M0, unmutated: `stop-prod 80.22`, `stop-rule 81.60`, `ALL 84 OPTIMALITY
  CHECKS PASSED`.
- MA, all three `"ftol": 1e-6` options dicts at 1e-3: `FAIL the production stop
  rule (ftol) buys a materially better plan [ftol 1e-6 81.60 vs loosened 1e-3
  both sites 81.60 (0.00% gap, bound 0.84%)]`, 2 of 84 failed (the other is the
  iteration-budget challenger).
- MB, the multi-start refinement's options dict alone at 1e-3 (the round-4
  single-site class): `FAIL ... [ftol 1e-6 81.54 vs loosened 1e-3 both sites
  81.60 (0.07% gap, bound 0.84%)]`, 2 of 84 failed.
- MC, all three at 1e-2: `FAIL ... [ftol 1e-6 83.10 vs loosened 1e-3 both sites
  81.60 (-1.84% gap, bound 0.84%)]`, 4 of 84 failed.

**The `calls_floor` bound** (`tests/stress.py` `coverage_floors`). A scratch
driver that execs the tree's `coverage_floors` alone, with
`{"floor": 18, "cites": "r"}` plus `calls_floor` 6 / 7 / 10 / 14 / absent over
20 families and 54 scenarios: at `c3a25d2ae` `(18, 6)`, `(18, 7)`, `(18, 10)`,
`(18, 14)`, `(18, 7)` -- 10 and 14 held although withdrawing them reads 7; at
this head `(18, 6)`, `(18, 7)`, `(18, 7)`, `(18, 7)`, `(18, 7)`. The stress
self-check `coverage floors: an override naming both floors is held to both,
and a malformed production-call floor is the share rule` now also feeds
`share(18)` and `share(18) + 3` (10); against the previous predicate the 10
returns `(18, 10, 'ruling')`, not the share, and the check fails.

**D2-s2-01.** `thermal_model.py` put back to `origin/main`'s (the two-law
`compute_cop_dhw`; 17 lines each way against this head, the docstring line
included) in a `git archive` export of this head. `python3
tools/audit/seat/features_block.py "R10-PUMP-MODEL -- DHW lift, the duty floor
channel, the step-start fold"` prints `3 of 10 FEATURES BLOCK FAILED`:

    FAIL D2-s2-01: the space-valve flag does not price the hot-water tank -- both
      plants charge one lift, over the whole outdoor/tank grid  [worst ratio
      1.4346 at outdoor=7.0 tank=65.0]
    FAIL D2-s2-01: the tank's price is _cop_law at the tank's own water
      temperature, humidity and all -- not a penalty of its own  [o=7 T=65
      direct 2.66 law 1.8541518628970441]
    FAIL D2-s2-01: a tank below the reference flow earns no lift and a hot one
      pays it (the one-sided rule _batch_cop states)  [below-ref boost 1.2000,
      65 C price 2.6600 vs base 3.5000]

The unmutated export prints `ALL 10 FEATURES BLOCK PASSED`.

## Null control

- **The ftol cell is not a kernel accident**: the four kernels read the new
  cell's four arm costs identically to the fourth decimal, and k1725's
  `stop_repeat_identical=1` holds on each (two solves in one process
  bit-identical). The old cell's flat reading is the null the re-selection
  rests on: at the same head and kernels it reads every loosened arm at
  production's 60.96, so the search's positive gaps are the cell's and not the
  harness's.
- **The 1e-3 arm is not inert**: MA reads the arm and a both-sites-1e-3
  production at the same 81.60, the construction by which the check goes red.
- **The grid census** (`r10_dhw_lift_law_grid.py`): at a 35 °C tank, where both
  laws must agree, `null_max_diff=0.000e+00` at both ends; its `--perturb` arm
  reinstates the retired linear law in-process and reproduces the before arm
  to the digit at this head.
- **The P2 class census** returns to 3 under its own `--perturb` at this head.
- **The ftol search's own null**: `r10_ftol_cell_search.py --perturb` loosens
  production itself to the both-sites 1e-2 rule; on the new cell it reads
  `gap_both_1e2=+0.000` (prod 83.0998 = arm), the construction the check
  turns on.

## Figures

- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/k1725_blas_kernel_gap.py`
  (sha1 `571a7ca097c264ae8578f452ae70485549770000` at this head), under
  `OPENBLAS_CORETYPE` unset (this box's native kernel reports Haswell),
  SkylakeX, Sandybridge and Nehalem, Intel Xeon @ 2.10GHz, numpy 2.4.6, Python
  3.14.7. At the old cell (the head's tree before `e4f5a41e2` moved it):
  `stop_prod_cost=60.96` and every `stop_loose_*` / `stop_both_*` cost 60.96 on
  all four (gaps +0.000 / -0.002), `stop_tight_1e8_cost` 60.02 (Haswell), 60.45
  (SkylakeX), 60.47 (Sandybridge, Nehalem). At this head's cell, on each of the
  four: `stop_prod_cost=80.22`, `stop_both_1e3_cost=81.60`,
  `stop_loose_1e3_cost=81.54`, `stop_both_1e2_cost=83.10`,
  `stop_tight_1e8_cost=80.22` (objective 106.4690, production's own),
  `stop_check_gap_pct=+1.687`, `stop_repeat_identical=1`.
- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_ftol_cell_search.py`
  (sha1 `2e10028927aef86e4f086642b5468614a58d0d86`), 36 cells, the same four
  kernels: a cell qualifies when its `min_gap` (the least of the three loosened
  arms' gaps) is positive on every kernel, its smallest across kernels shown.
  Three cells do: two-zone winter_moderate/winter_cold (`+1.617`, every
  kernel's four costs equal to the fourth decimal), single-zone
  winter_narrow/shoulder (`+0.339`) and single-zone winter_typical/winter_mild
  (`+0.001`). The old cell reads `-0.002`. The check is two-zone (single-zone
  is insensitive to ftol on its cell, the comment's record), and the one
  two-zone cell is also the widest, so it is the cell.
- `PYTHONPATH=tests/hastub python3 tests/optimality.py` at this head:
  `stop-prod : cost 80.22`, `stop-rule: cost 81.60`, `ALL 84 OPTIMALITY CHECKS
  PASSED` (the scoped gate run below).
- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_dhw_lift_law_grid.py
  --root <tree>` (sha1 `7563d2e650a0ed96d546ba7dfd49c35c39aa9ed0`), 41 outdoor
  (-25..15 °C) x 51 tank (20..70 °C): before (`origin/main` `106af95a3`)
  `dev_cells=1861` of `cells=2091`, `worst_ratio=1.4548` at (7.0, 70.0),
  `within_ratio=1.3522` (tank 2.9400 against the space lift's 2.1742),
  `below_ref_boost=1.1200`; head `dev_cells=0`, `worst_ratio=1.0000`,
  `within_ratio=1.0000`, `below_ref_boost=1.0000`; head `--perturb` equal to the
  before arm in every value.
- `python3 dev/audit/rounds/round10/D14/sweep-P2/enumerate_p2.py`, each tree's
  own copy: `F3_cop_law_fork=3` before (seams `compute_cop`, `compute_cop_dhw`,
  `_batch_cop`), `2` at the head (`compute_cop`, `_batch_cop`, the registered
  owners); `--perturb` at the head `perturb.F3_cop_law_fork before=2 after=3
  moved=1`.
- Scope, `python3 tests/closure.py select --diff 106af95a3`: `MODE: SCOPED --
  28 script(s) run, 5 scoped out`. `env -u BASH_ENV GATE_SCOPE=auto
  GOLDEN_MODE=drift GOLDEN_REF=106af95a3 ./tests/run.sh` at `42d78852d`: 26 of
  the scoped and run-always scripts green, among them `optimality.py`
  `ALL 84`, `features.py` `ALL 4179`, `entities.py` `ALL 2348`, `golden` via
  `env_drift.py --all` ok, `card.mjs` and `card_drift.mjs` ok, `backtest.py`
  `ALL 25`. Red were `structure.py` (`class_excess_loc` +1, the two-line
  docstring, paid in `ce3d3bc6d`), `layout.py` (the new harness citing the
  retired `tools/audit/README.md`, fixed in `ce3d3bc6d`), `harness_headers.py`
  and `stress.py` (0 s each: `HPO_GATE_LOCK_LABEL` set to a label never taken,
  `flock-wrap refused ... holds no lease`). Re-run directly at the following
  heads: `stress.py` `ALL 113 STRESS CHECKS PASSED` at `ce3d3bc6d` (below);
  at this head `harness_headers.py` `ALL 109 HARNESS HEADER CHECKS PASSED`
  (after `8100b5e55`, which fixed its `every inlined walk matches the
  canonical helper` refusal), `layout.py` rc 0 with `GUARD: 0 refusal(s)`,
  `structure.py` `STRUCTURE RATCHET PASSED`, `entities.py` `ALL 2348 ENTITY
  CHECKS PASSED`, `features.py` `ALL 4179 FEATURE CHECKS PASSED`,
  `doc_claims.py` `ALL 169 checks PASSED`.
- `python3 tools/policy/budget_raise_gate.py --self-test`: `239 checks, 0
  failed`. `python3 tests/env_drift.py --claims-only 106af95a3`: `claims
  hygiene: ... ok`. `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `python3 tools/pr/ci_predict.py --base 106af95a3`: `CI PREDICT: no closures or
  fast red predicted against 106af95a33f8 (a data-file read is not seen)`.
- `python3 tools/audit/archscore/score.py --diff 106af95a3`: `Architecture
  score: dS +0.0000 NULL`.

## Raise justification

`tests/stress_budgets.json` gains `coverage_floor_override` at `floor: 18`,
`calls_floor: 6`: CI's measured counts -- 18 of 54 scenarios judged by the
solver-work check (literal floor 40) and 6 of 20 families by the
production-call check (literal floor 15), at `74f23814e` and again at
`c3a25d2ae` against `c8cc75ea9`. Every hot-water scenario re-plans because the
tank's price changed, so it drops out of both comparisons. Sanctioned by
ruling #201 comment 6240984157 step 3 under mandate 6175172275; the
orchestrator ruled the explicit floors at the measured values and refused a
floor of 16 under the share rule as unearned headroom.

Payments tried:
1. Narrow the fix so fewer scenarios re-plan (keep the linear law on direct
   plants): refused -- that law is the defect the ruling accepted fixing.
2. Split the pull request: no lower count -- all 36 hot-water scenarios
   re-plan on whichever half carries the law change.
3. Re-record the baseline: impossible -- the baseline is main's tree solved
   beside the run, not a recording a branch can move.
4. Judge re-planned scenarios by a per-scenario work statement instead of a
   floor: a larger change to `tests/stress.py`, and the ruling chose the
   override; the statement is step 4's, below.
5. The share rule alone: floor 18 rounds to a calls floor of 7 against the
   measured 6, and the largest floor holding both, 16, is 2 below the measured
   work count -- so the override names the calls floor explicitly, now bounded
   by the share of its own work floor.

No code payment exists: `tools/audit/archscore/` reads only
`custom_components/`, and the entry is a JSON file under `tests/`.
`python3 tools/audit/archscore/score.py --diff 106af95a3` at this head:
Architecture score: dS +0.0000 NULL

`tools/policy/budget_raise_gate.py` is code-owned (`.github/CODEOWNERS`
`@tvofi`), so its rule is tvofi's to approve at merge, with the two workflow
files.

**Step 4, each re-planned scenario's solver work against baseline**, from CI's
`fast (3.14)` stress log at `c3a25d2ae` (job 117743791052): `solver work: 18
of 54 scenarios judged against the baseline captured beside this run, at
1.80x; 36 re-planned by this branch, 0 new here, 0 dropped`. The rule: for each
`re-planned by this branch` line, evaluations here over evaluations at the
baseline. Largest 1.370 (winter_mild/1z/dhw), under the 3.0x factor the ruling
names and under the gate's own 1.80x; 10 grew, 17 shrank, 9 equal. Had any
scenario grown past 3.0x, its ratio would print above 3.000 here. Every line:

    flat/1z/dhw: 592 vs 452 = 1.310x
    flat/2z/dhw: 734 vs 878 = 0.836x
    heavy_old/shoulder: 894 vs 798 = 1.120x
    heavy_old/winter: 528 vs 580 = 0.910x
    light_new/shoulder: 236 vs 280 = 0.843x
    light_new/winter: 594 vs 504 = 1.179x
    shoulder/1z/dhw: 620 vs 554 = 1.119x
    shoulder/2z/dhw: 696 vs 752 = 0.926x
    shoulder/cycle: 1080 vs 1384 = 0.780x
    shoulder/pv: 1252 vs 1198 = 1.045x
    shoulder/pv+cycle: 1678 vs 1956 = 0.858x
    shoulder/tariff: 1334 vs 1372 = 0.972x
    shoulder/tariff+cycle: 1180 vs 3462 = 0.341x
    shoulder/tariff+pv: 1006 vs 2224 = 0.452x
    shoulder/tariff+pv+cycle: 1760 vs 2914 = 0.604x
    summer/1z/dhw: 56 vs 56 = 1.000x
    summer/1z/dhw/fuse-cap: 56 vs 56 = 1.000x
    summer/2z/dhw: 24 vs 24 = 1.000x
    summer/2z/dhw/pin-off: 24 vs 24 = 1.000x
    summer_negative/1z/dhw: 56 vs 56 = 1.000x
    summer_negative/2z/dhw: 24 vs 24 = 1.000x
    typical_slab/shoulder: 1122 vs 962 = 1.166x
    typical_slab/winter: 54 vs 54 = 1.000x
    winter/1z/dhw: 52 vs 52 = 1.000x
    winter/2z/dhw: 946 vs 728 = 1.299x
    winter/cycle: 1114 vs 1402 = 0.795x
    winter/pv: 946 vs 728 = 1.299x
    winter/pv+cycle: 1114 vs 1402 = 0.795x
    winter/tariff: 884 vs 942 = 0.938x
    winter/tariff+cycle: 704 vs 998 = 0.705x
    winter/tariff+pv: 884 vs 942 = 0.938x
    winter/tariff+pv+cycle: 704 vs 998 = 0.705x
    winter_extreme/1z/dhw: 50 vs 50 = 1.000x
    winter_extreme/2z/dhw: 1092 vs 980 = 1.114x
    winter_mild/1z/dhw: 852 vs 622 = 1.370x
    winter_mild/2z/dhw: 904 vs 940 = 0.962x

`production calls: 6 of 20 family members judged against c8cc75ea9`;
re-planned: heavy_old/winter, light_new/shoulder, summer/1z/dhw/fuse-cap,
summer/2z/dhw, summer/2z/dhw/pin-off, summer_negative/1z/dhw,
typical_slab/winter, winter/cycle, winter/pv, winter/pv+cycle, winter/tariff,
winter/tariff+cycle, winter/tariff+pv, winter/tariff+pv+cycle; new: none.
Re-taken here, `PYTHONPATH=tests/hastub GOLDEN_REF=106af95a3 python3
tests/stress.py` at `ce3d3bc6d` (no file `stress.py` reads changed after it):
`solver work: 18 of 54 ... 36 re-planned by this branch, 0 new here, 0
dropped`, `production calls: 6 of 20 family members judged against
106af95a3`, the same 36 scenarios, largest ratio 1.282 (light_new/winter), `ALL
113 STRESS CHECKS PASSED`. The counts equal the override's floors exactly,
zero headroom.

## Red checks

At the previous head `c3a25d2ae`:
- **`fast (3.14)`** (job 117743791052) was red on one check, `tests/optimality.py`'s
  `the production stop rule (ftol) buys a materially better plan` (`ftol 1e-6
  60.96 vs loosened 1e-2 both sites 60.96 (-0.00% gap, bound 2.5%)`, 1 of 84).
  This fix's own blast radius: the one lift law made every loosening land on
  production's plan at that cell. Answered by step 2 above (the cell and arm
  re-selected, mutation-proven). Cheaper detector: none -- this block is the
  only place the stop rule is raced, and the kernel harness measuring it ran on
  no head between.
- **`budget-raise-gate`**, red by design on the override's two leaves
  (`floor`, `calls_floor: None -> 6`); expected red again here, until the raise
  is approved at this head. Answered by `## Raise justification`. Cheaper
  detector: none -- this gate is the detector.

At `74f23814e` (earlier in this branch): `fast (3.14)` red on the same ftol
check and on `tests/stress.py`'s two coverage floors (the override then
absent), and `pr-contract` red on `## Red checks` not naming `fast (3.14)`;
both answered there and green since. Cheaper detector for the contract one:
none -- `tools/pr/prepr.sh` lints a body before the CI conclusion it must name
exists.

`golden.py` / `env_drift.py` drift is claimed (`tests/golden/claimed_drift.txt`);
a red there naming an unclaimed fixture is a new finding.

## Forward-carry

`none` -- the cell and arm re-selection is this check's own, recorded in its comment block with the instrument that made it; no later stage's technique, figure or option moves.

## Unpinned sites

`prepr.sh` step 6d lists what the diff adds. The one production site this
finding adds is `compute_cop_dhw`'s return, pinned by
`tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.compute_cop_dhw.RETURN_DEL.a4eaefe8.json`;
`ThermalModel.compute_cop_dhw GUARD_OFF ca964a78` retires with the
`cop_flow_carnot` guard it pinned. This head's other production change is a
docstring line. The ledger's verdict at this head is CI's mutation check.

## Friction

- `dev/governance/rules/claim-files.md: contradiction: a fixture whose baseline_cost moves cannot be claimed while it carries a may-drift entry, and a may-drift entry cannot excuse a judged-key move, so the held branch suspended twelve owner-sanctioned may-drift entries for the release -- the R8-P3 wood_coil precedent, recorded nowhere as the rule.`
- `dev/governance/roles/fixer.md: cost: a label-triggered workflow added by a branch never runs for a label applied before the file reached the head (#2368: labelled at 74f23814e, workflow arrived at c3a25d2ae, zero runs), and nothing in the seat's brief or the job says the label must go on after; fixed for kernel-points by its synchronize arm.`
- `.claude/rules/gate-scoping.md: unclear: exporting HPO_GATE_LOCK_LABEL for a run.sh run without first taking that label fails every leased script at 0s with no reason line in the gate log (harness_headers.py and stress.py here); the rule says run.sh "under HPO_GATE_LOCK_LABEL renews itself" without saying the label must already hold the lease.`
