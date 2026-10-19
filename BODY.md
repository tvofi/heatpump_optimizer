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

`e85ef9fe6f5080dd12cf12da4800e69ea14ab080` is the code head. It is two merges of origin/main onto the previous handoff head `2260b8b9058bc02f0673accb30dca76e94765b29`, which is also the authored code head of the last review:
- origin/main `fa424fd91a042f4a66ae53238c3db6d70d9d4ff1` (#2408) and then `dd27e7c1b4c6ca250f8be5b33c4e8443d6d1f0b6` (#2411, R10-SAV-BASELINE). The second conflicted in `tests/golden/claimed_drift.txt` only; see **The claims file**.
- origin/main `0dac0bf8731a36ca10805fcd3fd5c196b77cb8fc` (#2399). Clean.

`git merge-base --is-ancestor 0dac0bf87 HEAD` holds. origin/main has since moved to record-only merges; this body claims nothing about a later main. The PR head the orchestrator last saw, `86258e159d6e18b41aa0edafc79c6b8921d5c4dc`, was the orchestrator's earlier merge of `07a09406a`.

What the earlier review measured is unchanged where it matters: `git diff --stat 2260b8b90 HEAD -- custom_components/heatpump_optimizer/thermal_model.py` prints nothing, so D2's production change and its three features checks stand. `git diff e4f5a41e2 HEAD -- custom_components/heatpump_optimizer/optimizer.py | grep -c ftol` prints `0`, so the ftol mutants MA to MC (below) are on lines this head did not touch. `tests/stress.py`, `tests/optimality.py`'s ftol check and the three harnesses of this PR are unchanged by the merges. The merges brought #2411's optimizer, ledger and coordinator changes (the thermostat reference), which the gate below ran against.

Figures marked "head" were taken on 2026-10-19 between 03:50Z and 05:30Z, `GOLDEN_REF=0dac0bf87`. The harness figures of the previous heads (`8100b5e55`, `ce3d3bc6d`) are cited with the head they were taken at.

## The claims file

`tests/golden/claimed_drift.txt` conflicted with R10-SAV-BASELINE's own claims (#2411 claims 51 fixtures and suspended the same may-drift entries this branch suspends). The repo's driver (`python3 tests/env_drift.py --merge-claim-file`, routed by `.gitattributes`) refuses it by design: a claim "is written for exactly one diff", and a union would "reinstate a claim one side deleted". Resolved by hand as that refusal's message says, with the driver's own pieces: the notes (comments) are the three-way union of both sides (`_union_comments`), the claim list is this branch's (41 fixtures), and `merge_claim_defect(...)` returns `None`, so no may-drift line of either side was lost.
- No entry lost from this branch: `diff <(sort -u ours) <(sort -u result) | grep -c '^<'` prints `0`.
- No comment of main's lost: the same diff against main's file, filtered to comment lines, prints `0`. What main's file has and the result lacks is 54 unique claim lines (its 51 claims plus pre-existing duplicates), each a claim for R10-SAV-BASELINE's or older diffs.
- Why those claims are not carried, measured: the union of both claim lists (this branch's 41 plus 15 main-only names; 53 distinct fixtures) fails `python3 tests/env_drift.py --all` with `CLAIMED AND MAY-DRIFT: ... valve_storage, valve_storage_smart_write, valve_upper_direct_slab, winter_two_zone_no_dhw, wood_coil, wood_two_tank, wood_two_tank_smart_write as both`, rc=1. Those names do not drift against main (`ok ... is byte-identical to origin/main here`), so main's claims on them would also be stale. The resolved file prints `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 0dac0bf87` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes` (rc=0); `python3 tests/env_drift.py --claims-only` prints `claims hygiene: ... ok`.
- Main's claims are not owed here: they describe #2411's diff, which is in main now and so no longer drifts against this PR's base. They expire at the next stamp.

## Mutation proof

**The ftol check** (`tests/optimality.py`, challenger 7). MA to MC were taken at `e4f5a41e2`'s tree; the ftol lines they edit are unchanged at the head (Head), and M0's two readings are re-read at the head: `stop-prod : cost   80.22`, `stop-rule: cost   81.60` in the gate log. Each mutant is an
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
  `_batch_cop`), `2` at this head (`compute_cop`, `_batch_cop`, the registered
  owners); `--perturb` at this head `perturb.F3_cop_law_fork before=2 after=3
  moved=1`.
- Scope, `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` at the head: `MODE: SCOPED -- 28 script(s) run, 5 scoped out`. `env -u BASH_ENV GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=0dac0bf87 PYTHONPATH=tests/hastub ./tests/run.sh` at the head, 28 scripts, 26 green: `features.py` `ALL 4202`, `entities.py` `ALL 2350`, `env_drift.py --all` `NO UNCLAIMED DRIFT: 56 ... NO STALE FIXTURE: 56`, `card.mjs` `ALL CARD CHECKS PASSED`, `backtest.py` `ALL 25`, `structure.py` `STRUCTURE RATCHET PASSED`, `harness_headers.py` `ALL 109`, `doc_claims.py` `ALL 169`, `debug_collect.py` `ALL 122`, `closure.py selftest` `ALL 124`, `boost_drift_replay.py` `ALL 46`, `finite_boundary.py` `ALL 106`, `arch_score_head.py` `ALL 18`, `deployment_shape.py` ok, `guard_pins.py` `ALL 50`. The two red ones are named under **Red checks, local platform**.
- `python3 tools/policy/budget_raise_gate.py --self-test`: `239 checks, 0 failed`. `python3 tests/env_drift.py --claims-only` against origin/main: `claims hygiene: ... ok`. `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `python3 tools/pr/ci_predict.py --base fa424fd91`: `CI PREDICT: no closures or fast red predicted against fa424fd91a04 (a data-file read is not seen)` (at the first of the two merges; the second adds main's #2399).
- `python3 tools/audit/archscore/score.py --diff dd27e7c1b4c6ca250f8be5b33c4e8443d6d1f0b6`: `Architecture score: dS +0.0000 NULL`. Measured against a stale local `origin/main` (before #2411 was fetched) it read `dS -0.0006 WORSENS (coord_footprint 2498->2499)`: that was main moving under the diff, not this PR; not a figure.
- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_dhw_lift_law_grid.py --root .` at the head: `cells=2091`, `dev_cells=0`, `worst_ratio=1.0000`, `within_ratio=1.0000`, `below_ref_boost=1.0000`, `null_max_diff=0.000e+00`; `enumerate_p2.py` at the head: `F3_cop_law_fork=2`. `k1725_blas_kernel_gap.py` and `r10_ftol_cell_search.py` are not re-run here: they are heavy, `thermal_model.py` and the ftol lines are unchanged (Head), and the kernel-points job measures them in CI.

## Raise justification

**Re-measured at head `e85ef9fe6`** (`GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=0dac0bf87 ./tests/run.sh`, `tests/stress.py` lines): `solver work: 18 of 54 scenarios judged against the baseline captured beside this run, at 1.80x; 36 re-planned by this branch, 0 new here, 0 dropped` and `production calls: 6 of 20 family members judged against 0dac0bf87`. Both counts equal the override's two leaves, `floor: 18` and `calls_floor: 6`, so both raises are still needed and neither is dropped. `python3 tools/policy/budget_raise_gate.py --base fa424fd91 --head HEAD --pr 2368` (at the head before the last merge) prints the same two RAISE lines, `coverage_floor_override.floor: override added at 18` and `coverage_floor_override.calls_floor: override added at 6`, and `REFUSED: no decisive review by tvofi`: the raise is the owner's.

**Null control.** The floors without the override, from `coverage_floors` exec'd out of `tests/stress.py` with `{}`: `(40, 15)`. With the committed table: `(18, 6)`. So with the measured 18 and 6 judged, a table without the entry fails both coverage checks, and the entry is what the head needs, not headroom; the largest single floor that holds both measured counts is 16, 2 below the measured work count.

**Why neither raise can be paid by optimisation.** A floor here counts how many scenarios the solver-work (and production-call) check can compare against the baseline. The 36 scenarios that drop out are exactly the ones whose plan this finding changes: the tank is priced by a different law, so the head's solve and the baseline's are different problems, and the check judges only a scenario that "re-plans" nothing. Making the solver faster, or the code smaller, changes the evaluations each side spends, never whether the plans differ, so it cannot move a scenario back into the judged set. The only payment that would is to keep the old two-law `compute_cop_dhw`, which is the defect the ruling accepted fixing (payment 1 below). Both raises are therefore unpayable by optimisation, and the rest of this section lists the payments tried.

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
`python3 tools/audit/archscore/score.py --diff dd27e7c1b` at this head:
Architecture score: dS +0.0000 NULL

`tools/policy/budget_raise_gate.py` is code-owned (`.github/CODEOWNERS`
`@tvofi`), so its rule is tvofi's to approve at merge, with the two workflow
files.

**Step 4, each re-planned scenario's solver work against baseline**, from this seat's gate run at the head (`tests/stress.py` under `GOLDEN_REF=0dac0bf87`, log lines `re-planned by this branch: <scenario> (objective ...; E evaluations vs B)`). The rule: for each such line, evaluations here over evaluations at the baseline. 36 scenarios; largest 1.641 (winter/pv, 1080 vs 658), under the 3.0x factor the ruling names; 13 grew, 15 shrank, 8 equal. Had any grown past 3.0x its ratio would print above 3.000 here. The 36 are the same 36 names CI judged at `c3a25d2ae` (job 117743791052: largest 1.370, winter_mild/1z/dhw); the evaluation counts differ because the baseline now includes #2411's thermostat reference, and the 3.0x bound holds at both. Every line:

    flat/1z/dhw: 628 vs 558 = 1.125x
    flat/2z/dhw: 662 vs 726 = 0.912x
    heavy_old/shoulder: 1096 vs 952 = 1.151x
    heavy_old/winter: 656 vs 606 = 1.083x
    light_new/shoulder: 240 vs 264 = 0.909x
    light_new/winter: 540 vs 598 = 0.903x
    shoulder/1z/dhw: 500 vs 548 = 0.912x
    shoulder/2z/dhw: 724 vs 790 = 0.916x
    shoulder/cycle: 1032 vs 1318 = 0.783x
    shoulder/pv: 1462 vs 1286 = 1.137x
    shoulder/pv+cycle: 1642 vs 1968 = 0.834x
    shoulder/tariff: 822 vs 1302 = 0.631x
    shoulder/tariff+cycle: 1206 vs 3302 = 0.365x
    shoulder/tariff+pv: 1110 vs 2062 = 0.538x
    shoulder/tariff+pv+cycle: 1670 vs 3384 = 0.493x
    summer/1z/dhw: 56 vs 56 = 1.000x
    summer/1z/dhw/fuse-cap: 56 vs 56 = 1.000x
    summer/2z/dhw: 24 vs 24 = 1.000x
    summer/2z/dhw/pin-off: 24 vs 24 = 1.000x
    summer_negative/1z/dhw: 56 vs 56 = 1.000x
    summer_negative/2z/dhw: 24 vs 24 = 1.000x
    typical_slab/shoulder: 894 vs 866 = 1.032x
    typical_slab/winter: 56 vs 52 = 1.077x
    winter/1z/dhw: 52 vs 52 = 1.000x
    winter/2z/dhw: 1080 vs 658 = 1.641x
    winter/cycle: 1188 vs 1192 = 0.997x
    winter/pv: 1080 vs 658 = 1.641x
    winter/pv+cycle: 1188 vs 1192 = 0.997x
    winter/tariff: 1084 vs 770 = 1.408x
    winter/tariff+cycle: 810 vs 878 = 0.923x
    winter/tariff+pv: 1084 vs 770 = 1.408x
    winter/tariff+pv+cycle: 810 vs 878 = 0.923x
    winter_extreme/1z/dhw: 50 vs 50 = 1.000x
    winter_extreme/2z/dhw: 1050 vs 928 = 1.131x
    winter_mild/1z/dhw: 856 vs 582 = 1.471x
    winter_mild/2z/dhw: 1084 vs 784 = 1.383x

`production calls: 6 of 20 family members judged against 0dac0bf87`; re-planned: heavy_old/winter, light_new/shoulder, summer/1z/dhw/fuse-cap, summer/2z/dhw, summer/2z/dhw/pin-off, summer_negative/1z/dhw, typical_slab/winter, winter/cycle, winter/pv, winter/pv+cycle, winter/tariff, winter/tariff+cycle, winter/tariff+pv, winter/tariff+pv+cycle; new: none. The counts equal the override's floors exactly, zero headroom.

## Red checks

Read from the check-runs API on the PR head `86258e159d6e18b41aa0edafc79c6b8921d5c4dc` (`failure_logs.sh 2368`): four checks were red there.
- **`wave-script`** (job 117830542873). Inherited from main, not this diff: the agreement lane's `merge-subject-pr` was `divergent=2` on main's merges `Merge pull request #2401 (R10-ARCHSCORE-COVERAGE p5)` and `Merge pull request #2379 (R10-SENSOR-PAYLOAD)`, which `policy_lint.mjs`'s `resolvePrFromCommit` read as null. Cleared by main's #2423 and #2424, both in this head. At the head, `python3 -I tools/policy/agreement_py.py --out J; node tools/policy/agreement.mjs --py-json J` reads `divergent=0`. The detector is the agreement lane; no cheaper one exists.
- **`delivery-status`** (job 117830543161; not a required context): `DELIVERY STATUS OVERDUE`, main's row backlog while main was red. This diff adds its own row `2368.md` only. Cleared by main's later record merges; `python -I -S tests/delivery_status.py --check` at the head reads `DELIVERY STATUS OK`.
- **`pr-contract`** (job 117830697142): `check `wave-script` is red and `## Red checks` does not name it`. The cause was the body; this section names it, with `delivery-status` and `budget-raise-gate`. `policy_lint.mjs --pr-body` over this body reads 0 errors.
- **`budget-raise-gate`** (job 117830532680): `RAISE tests/stress_budgets.json: coverage_floor_override.calls_floor ... .floor ...` and `REFUSED: no decisive review by tvofi (id 70032254) on this pull request`. Red by design until the owner approves the raise; answered by `## Raise justification` (re-measured at the head, payments tried, unpayable by optimisation). Cheaper detector: none, the gate is the detector. This head is not yet approved, and nothing here claims it.

History on this branch, answered earlier: `fast (3.14)` at `c3a25d2ae` (the ftol check at the old cell; answered by step 2, mutation-proven) and at `74f23814e` (the ftol check and the coverage floors, the override then absent), and `pr-contract` at `74f23814e` (`## Red checks` not naming `fast (3.14)`); all green since. The detector for the contract one: none, `tools/pr/prepr.sh` lints a body before the CI conclusion it must name exists.

**Red checks, local platform (the merged head on this Mac).** Two scripts of the scoped gate were red on this arm64 seat: `tests/optimality.py` (`1 of 84`) and `tests/stress.py` (`1 of 113`). Neither is this branch's. A control, `tests/optimality.py` and `tests/stress.py` run in a detached worktree of origin/main `913ce1ff5` (record-only merges over `0dac0bf87`), reads the same two:
- `FAIL one|summer_negative|shoulder: a recorded claim still has a gap (not stale)  [claimed but gap 0.0000% is at or below the bar -- the claim closed and should be removed]`. `tests/optimality.py`'s own comment on `_CERT_CLAIMS` says it: "this claim reads stale on arm64 only", CI's linux fast lane still measuring the ladder at +10.55 %.
- `FAIL shoulder: cheaper than holding the setpoint  [4.67 vs 3.96]`, the same two numbers on main and on this head.
The control's other seven stress failures are the control's own (`origin/main IS this commit`: no baseline can be captured against itself) and are not read. Both of the scripts are heavy and belong to CI under tvofi's rule; main's `fast (3.14)` is `success` at `0dac0bf87` and at `8cc1abc3a` (check-runs API). CI at this PR's head is the orchestrator's carry and is not claimed here.

`golden.py` / `env_drift.py` drift is claimed (`tests/golden/claimed_drift.txt`, see **The claims file**); a red there naming an unclaimed fixture is a new finding.

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

